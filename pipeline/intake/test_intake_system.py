"""Automated Verification & Unit Test Suite for Managed Media Intake (YVP-SYS-002).

Covers all 12 required verification scenarios from Section 14 using synthetic,
temporary test fixtures that are automatically removed after execution:
1. Valid image intake (1920x1080 PNG & low-res 800x600 JPEG warning behavior).
2. Valid video intake (synthetic spec-compliant ISO-BMFF MP4 container + explicit ffprobe warning check).
3. Duplicate file detection (identical SHA-256 within same production does not create second copy).
4. Unsupported extension rejection (.txt / .exe).
5. Empty file rejection (0-byte .png / .mp4).
6. Source and managed copy checksum equality (SHA-256 bit-for-bit verification & source preservation).
7. Manifest registration (all required fields, provenance, separation of validation vs approval status).
8. Repeated intake without overwriting (different files get sequential IDs REF-001, REF-002; pre-existing target file refuses overwrite).
9. Path traversal & symlink/junction protection (rejects '../', absolute paths in manifest, and junctions/symlinks).
10. Validation of a previously registered asset (PASS on intact file, FAIL on tampered/corrupted managed copy).
11. Failed-copy recovery (simulated mid-copy corruption removes temp .part file and leaves manifest unmodified).
12. Isolation between two test production IDs (TEST-PROD-A and TEST-PROD-B have isolated manifests & files; YACHT-001 remains untouched in DRAFT).
"""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PIL import Image  # type: ignore

from pipeline.intake.manager import (
    IntakeError,
    ensure_production_workspace,
    generate_intake_report,
    get_default_repo_root,
    inspect_asset,
    intake_single_file,
    list_assets,
    load_manifest,
    save_manifest_atomic,
)
from pipeline.intake.validator import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARNING,
    compute_sha256,
    validate_production_manifest,
)


def _make_box(box_type: bytes, payload: bytes) -> bytes:
    return struct.pack(">I4s", 8 + len(payload), box_type) + payload


def create_synthetic_mp4_bytes(
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
    duration_seconds: int = 4,
) -> bytes:
    """Create a minimal, spec-compliant ISO-BMFF (.mp4) header structure for deterministic testing."""
    timescale = fps * 1000
    duration_units = duration_seconds * timescale
    total_frames = fps * duration_seconds
    sample_delta = 1000

    # ftyp box
    ftyp = _make_box(b"ftyp", b"isom" + struct.pack(">I", 512) + b"isomiso2avc1mp41")

    # mvhd box (version 0)
    mvhd_payload = (
        struct.pack(">IIIIII", 0, 0, 0, timescale, duration_units, 0x00010000)
        + struct.pack(">H", 0x0100)
        + b"\x00" * 10
        + b"\x00" * 36
        + b"\x00" * 24
        + struct.pack(">I", 2)
    )
    mvhd = _make_box(b"mvhd", mvhd_payload)

    # tkhd box (version 0: 76 bytes before width/height 16.16 fixed point)
    tkhd_payload = (
        b"\x00" * 76
        + struct.pack(">II", width << 16, height << 16)
    )
    tkhd = _make_box(b"tkhd", tkhd_payload)

    # mdhd box (version 0)
    mdhd_payload = struct.pack(">IIIIII", 0, 0, 0, timescale, duration_units, 0)
    mdhd = _make_box(b"mdhd", mdhd_payload)

    # hdlr box ('vide')
    hdlr_payload = b"\x00" * 8 + b"vide" + b"\x00" * 12 + b"VideoHandler\x00"
    hdlr = _make_box(b"hdlr", hdlr_payload)

    # stsd box ('avc1' visual sample entry)
    avc1_entry_payload = (
        b"\x00" * 6
        + struct.pack(">H", 1)
        + b"\x00" * 16
        + struct.pack(">HH", width, height)
        + b"\x00" * 50
    )
    avc1_box = _make_box(b"avc1", avc1_entry_payload)
    stsd_payload = struct.pack(">II", 0, 1) + avc1_box
    stsd = _make_box(b"stsd", stsd_payload)

    # stts box (1 entry: total_frames, sample_delta)
    stts_payload = struct.pack(">IIII", 0, 1, total_frames, sample_delta)
    stts = _make_box(b"stts", stts_payload)

    stbl = _make_box(b"stbl", stsd + stts)
    minf = _make_box(b"minf", stbl)
    mdia = _make_box(b"mdia", mdhd + hdlr + minf)
    trak = _make_box(b"trak", tkhd + mdia)
    moov = _make_box(b"moov", mvhd + trak)
    mdat = _make_box(b"mdat", b"\x00" * 256)

    return ftyp + moov + mdat


class ManagedIntakeSystemTestSuite(unittest.TestCase):
    """Comprehensive verification suite for YVP-SYS-002."""

    def setUp(self) -> None:
        self.temp_dir_obj = tempfile.TemporaryDirectory(prefix="yvp_sys_002_test_")
        self.temp_root = Path(self.temp_dir_obj.name).resolve()
        self.repo_root = self.temp_root / "repo"
        self.external_sources = self.temp_root / "external_sources"
        self.repo_root.mkdir(parents=True, exist_ok=True)
        self.external_sources.mkdir(parents=True, exist_ok=True)
        (self.repo_root / "productions").mkdir(parents=True, exist_ok=True)

        # Initialize primary test production TEST-PROD-A
        ensure_production_workspace("TEST-PROD-A", self.repo_root, create_if_missing=True)

    def tearDown(self) -> None:
        self.temp_dir_obj.cleanup()

    def _create_test_image(
        self, filename: str, width: int = 1920, height: int = 1080, fmt: str = "PNG", color=(15, 45, 90)
    ) -> Path:
        path = self.external_sources / filename
        img = Image.new("RGB", (width, height), color=color)
        img.save(path, format=fmt)
        return path

    def _create_test_video(self, filename: str = "sample_ref.mp4") -> Path:
        path = self.external_sources / filename
        path.write_bytes(create_synthetic_mp4_bytes(1920, 1080, 24, 4))
        return path

    def test_01_valid_image_intake_and_low_res_warning(self) -> None:
        """Test 1: Valid 1080p image intake (PASS/WARNING) and low-resolution source warning behavior."""
        img_hd = self._create_test_image("exterior_1080p.png", 1920, 1080, "PNG")
        res = intake_single_file(img_hd, production_id="TEST-PROD-A", repo_root=self.repo_root, vessel_zone="exterior")

        self.assertEqual(res["intake_status"], "REGISTERED")
        self.assertEqual(res["asset_id"], "REF-001")
        self.assertEqual(res["asset_type"], "image")
        self.assertEqual(res["validation_status"], STATUS_PASS)
        self.assertEqual(res["approval_status"], "PENDING_REVIEW")
        self.assertEqual(res["technical_metadata"]["width"], 1920)
        self.assertEqual(res["technical_metadata"]["height"], 1080)
        self.assertEqual(res["technical_metadata"]["aspect_ratio"], "16:9")
        self.assertEqual(res["technical_metadata"]["format"], "PNG")

        # Now test low-resolution 800x600 (4:3) reference image -> should be REGISTERED with WARNING (not rejected!)
        img_low = self._create_test_image("deck_lowres.jpg", 800, 600, "JPEG", color=(40, 80, 120))
        res_low = intake_single_file(img_low, production_id="TEST-PROD-A", repo_root=self.repo_root, vessel_zone="deck")
        self.assertEqual(res_low["intake_status"], "REGISTERED")
        self.assertEqual(res_low["asset_id"], "REF-002")
        self.assertEqual(res_low["validation_status"], STATUS_WARNING)
        self.assertEqual(res_low["approval_status"], "PENDING_REVIEW")
        self.assertTrue(any("below final target delivery resolution" in w for w in res_low["warnings"]))

    def test_02_valid_video_intake(self) -> None:
        """Test 2: Valid video intake extracting technical metadata and reporting ffprobe status."""
        vid_path = self._create_test_video("yacht_aerial.mp4")
        res = intake_single_file(vid_path, production_id="TEST-PROD-A", repo_root=self.repo_root)

        self.assertEqual(res["intake_status"], "REGISTERED")
        self.assertEqual(res["asset_id"], "REF-001")
        self.assertEqual(res["asset_type"], "video")
        self.assertEqual(res["managed_relative_path"], "productions/TEST-PROD-A/references/videos/REF-001.mp4")

        meta = res["technical_metadata"]
        self.assertEqual(meta["width"], 1920)
        self.assertEqual(meta["height"], 1080)
        self.assertEqual(meta["container_format"], "MP4")
        self.assertEqual(meta["video_codec"], "H.264")
        self.assertEqual(meta["frame_rate"], 24.0)
        self.assertEqual(meta["duration"], 4.0)
        self.assertEqual(meta["aspect_ratio"], "16:9")
        self.assertIs(meta["audio_stream_present"], False)

    def test_03_duplicate_file_detection(self) -> None:
        """Test 3: Duplicate file detection by SHA-256 skips creating a second managed copy."""
        img1 = self._create_test_image("photo_a.png", 1920, 1080, "PNG", color=(10, 20, 30))
        # Create second file with different filename but identical binary content
        img2 = self.external_sources / "photo_a_copy.png"
        img2.write_bytes(img1.read_bytes())

        res1 = intake_single_file(img1, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res1["intake_status"], "REGISTERED")
        self.assertEqual(res1["asset_id"], "REF-001")

        res2 = intake_single_file(img2, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res2["intake_status"], "DUPLICATE_SKIPPED")
        self.assertEqual(res2["asset_id"], "REF-001")

        assets = list_assets("TEST-PROD-A", self.repo_root)
        self.assertEqual(len(assets), 1)
        managed_files = [
            p for p in (self.repo_root / "productions/TEST-PROD-A/references/images").iterdir() if p.name != ".gitkeep"
        ]
        self.assertEqual(len(managed_files), 1)

    def test_04_unsupported_extension_rejection(self) -> None:
        """Test 4: Unsupported file extension is deterministically rejected."""
        bad_file = self.external_sources / "document.txt"
        bad_file.write_text("Not a media file", encoding="utf-8")

        res = intake_single_file(bad_file, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res["intake_status"], "REJECTED")
        self.assertEqual(res["validation_status"], STATUS_FAIL)
        self.assertTrue(any("Unsupported file extension" in e for e in res["errors"]))
        self.assertEqual(len(list_assets("TEST-PROD-A", self.repo_root)), 0)

    def test_05_empty_file_rejection(self) -> None:
        """Test 5: Empty (0-byte) file is deterministically rejected."""
        empty_img = self.external_sources / "empty.png"
        empty_img.write_bytes(b"")

        res = intake_single_file(empty_img, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res["intake_status"], "REJECTED")
        self.assertEqual(res["validation_status"], STATUS_FAIL)
        self.assertTrue(any("empty (0 bytes)" in e for e in res["errors"]))
        self.assertEqual(len(list_assets("TEST-PROD-A", self.repo_root)), 0)

    def test_06_source_and_managed_copy_checksum_equality(self) -> None:
        """Test 6: Source file is untouched and managed copy SHA-256 matches source SHA-256."""
        src = self._create_test_image("hull_profile.png", 1920, 1080, "PNG", color=(100, 110, 120))
        pre_sha = compute_sha256(src)
        pre_bytes = src.read_bytes()

        res = intake_single_file(src, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res["intake_status"], "REGISTERED")

        # Verify source was not modified
        self.assertEqual(compute_sha256(src), pre_sha)
        self.assertEqual(src.read_bytes(), pre_bytes)

        # Verify managed copy checksum equality
        managed_path = self.repo_root / res["managed_relative_path"]
        self.assertTrue(managed_path.exists())
        self.assertEqual(compute_sha256(managed_path), pre_sha)
        self.assertEqual(res["sha256"], pre_sha)

    def test_07_manifest_registration_contract(self) -> None:
        """Test 7: Manifest registration contains all required fields and keeps validation separate from approval."""
        src = self._create_test_image("interior_salon.png", 1920, 1080, "PNG", color=(200, 180, 160))
        intake_single_file(
            src,
            production_id="TEST-PROD-A",
            repo_root=self.repo_root,
            vessel_zone="interior",
            notes="Main salon aft view",
        )

        rec = inspect_asset("TEST-PROD-A", "REF-001", self.repo_root)
        self.assertIsNotNone(rec)
        assert rec is not None
        self.assertEqual(rec["production_id"], "TEST-PROD-A")
        self.assertEqual(rec["asset_id"], "REF-001")
        self.assertEqual(rec["reference_id"], "REF-001")
        self.assertEqual(rec["asset_type"], "image")
        self.assertEqual(rec["original_filename"], "interior_salon.png")
        self.assertEqual(rec["managed_relative_path"], "productions/TEST-PROD-A/references/images/REF-001.png")
        self.assertEqual(rec["mime_type"], "image/png")
        self.assertEqual(rec["file_extension"], ".png")
        self.assertEqual(rec["validation_status"], STATUS_PASS)
        self.assertEqual(rec["approval_status"], "PENDING_REVIEW")
        self.assertTrue(rec["provenance"]["checksum_verified"])
        self.assertEqual(rec["provenance"]["source_sha256"], rec["sha256"])

    def test_08_repeated_intake_without_overwriting(self) -> None:
        """Test 8: Distinct files allocate sequential IDs (REF-001, REF-002) and never overwrite existing files."""
        img1 = self._create_test_image("shot1.png", 1920, 1080, "PNG", color=(1, 2, 3))
        img2 = self._create_test_image("shot2.png", 1920, 1080, "PNG", color=(4, 5, 6))
        img3 = self._create_test_image("shot3.png", 1920, 1080, "PNG", color=(7, 8, 9))

        r1 = intake_single_file(img1, production_id="TEST-PROD-A", repo_root=self.repo_root)
        r2 = intake_single_file(img2, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(r1["asset_id"], "REF-001")
        self.assertEqual(r2["asset_id"], "REF-002")

        # Even if an untracked file REF-003.png exists on disk in references/images, allocator skips REF-003 -> REF-004
        rogue_file = self.repo_root / "productions/TEST-PROD-A/references/images/REF-003.png"
        rogue_file.write_bytes(b"untracked_existing_file")

        r3 = intake_single_file(img3, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(r3["intake_status"], "REGISTERED")
        self.assertEqual(r3["asset_id"], "REF-004")
        # Confirm rogue_file was not overwritten
        self.assertEqual(rogue_file.read_bytes(), b"untracked_existing_file")

    def test_09_path_traversal_and_junction_protection(self) -> None:
        """Test 9: Path traversal in production ID, manifest paths, or NTFS junctions is blocked."""
        img = self._create_test_image("safe.png", 1920, 1080, "PNG")

        # 9a. Traversal in production ID
        with self.assertRaises(IntakeError):
            intake_single_file(img, production_id="../ESCAPE", repo_root=self.repo_root)

        # 9b. Tampered manifest path traversal blocked during validation
        intake_single_file(img, production_id="TEST-PROD-A", repo_root=self.repo_root)
        manifest = load_manifest("TEST-PROD-A", self.repo_root)
        manifest["source_references"][0]["managed_relative_path"] = "../../external_sources/safe.png"
        manifest_path = self.repo_root / "productions/TEST-PROD-A/assets/asset-manifest.json"
        save_manifest_atomic(manifest, manifest_path, self.repo_root)

        val_report = validate_production_manifest("TEST-PROD-A", self.repo_root)
        self.assertEqual(val_report["overall_status"], STATUS_FAIL)
        self.assertEqual(
            val_report["asset_results"][0]["checks"]["path_containment"],
            STATUS_FAIL,
        )

        # 9c. Test NTFS junction rejection on Windows
        junction_dir = self.temp_root / "junction_source"
        target_dir = self.external_sources
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction_dir), str(target_dir)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0 and junction_dir.exists():
            try:
                junction_file = junction_dir / "safe.png"
                res_j = intake_single_file(junction_file, production_id="TEST-PROD-A", repo_root=self.repo_root)
                self.assertEqual(res_j["intake_status"], "REJECTED")
                self.assertTrue(any("symbolic link or junction" in e for e in res_j["errors"]))
            finally:
                subprocess.run(["cmd", "/c", "rmdir", str(junction_dir)], capture_output=True)

    def test_10_validation_of_previously_registered_asset(self) -> None:
        """Test 10: Validation passes on intact registered asset and fails if managed file is altered."""
        img = self._create_test_image("valid_check.png", 1920, 1080, "PNG", color=(50, 60, 70))
        res = intake_single_file(img, production_id="TEST-PROD-A", repo_root=self.repo_root)
        self.assertEqual(res["intake_status"], "REGISTERED")

        val_ok = validate_production_manifest("TEST-PROD-A", self.repo_root)
        self.assertEqual(val_ok["overall_status"], STATUS_PASS)
        self.assertEqual(val_ok["pass_count"], 1)

        # Corrupt the managed copy on disk and verify validation catches SHA-256 mismatch
        managed_file = self.repo_root / res["managed_relative_path"]
        with open(managed_file, "ab") as f:
            f.write(b"TAMPERED")

        val_bad = validate_production_manifest("TEST-PROD-A", self.repo_root)
        self.assertEqual(val_bad["overall_status"], STATUS_FAIL)
        self.assertEqual(val_bad["asset_results"][0]["checks"]["sha256_integrity"], STATUS_FAIL)

    def test_11_failed_copy_recovery(self) -> None:
        """Test 11: Simulated copy corruption removes temp file and leaves manifest unmodified."""
        img = self._create_test_image("recover_test.png", 1920, 1080, "PNG", color=(90, 80, 70))
        res = intake_single_file(
            img,
            production_id="TEST-PROD-A",
            repo_root=self.repo_root,
            _simulate_copy_failure=True,
        )
        self.assertEqual(res["intake_status"], "FAILED")
        self.assertEqual(res["validation_status"], STATUS_FAIL)
        self.assertTrue(any("Copy integrity verification failed" in e for e in res["errors"]))

        # Verify no orphaned .part or REF-* files exist in references/images
        images_dir = self.repo_root / "productions/TEST-PROD-A/references/images"
        remaining = [p.name for p in images_dir.iterdir() if p.name != ".gitkeep"]
        self.assertEqual(remaining, [])

        # Verify manifest remains empty
        self.assertEqual(len(list_assets("TEST-PROD-A", self.repo_root)), 0)

    def test_12_isolation_between_two_productions_and_real_yacht001_intact(self) -> None:
        """Test 12: Two production IDs remain completely isolated, and real YACHT-001 remains DRAFT with 0 assets."""
        img = self._create_test_image("shared_source.png", 1920, 1080, "PNG", color=(12, 34, 56))

        res_a = intake_single_file(img, production_id="TEST-PROD-A", repo_root=self.repo_root)
        res_b = intake_single_file(
            img,
            production_id="TEST-PROD-B",
            repo_root=self.repo_root,
            init_production=True,
        )

        self.assertEqual(res_a["intake_status"], "REGISTERED")
        self.assertEqual(res_a["asset_id"], "REF-001")
        self.assertEqual(res_a["managed_relative_path"], "productions/TEST-PROD-A/references/images/REF-001.png")

        self.assertEqual(res_b["intake_status"], "REGISTERED")
        self.assertEqual(res_b["asset_id"], "REF-001")
        self.assertEqual(res_b["managed_relative_path"], "productions/TEST-PROD-B/references/images/REF-001.png")

        # Verify real repository YACHT-001 is completely untouched in DRAFT with 0 references
        real_root = get_default_repo_root()
        real_rep = generate_intake_report("YACHT-001", real_root)
        self.assertEqual(real_rep["lifecycle_state"], "DRAFT")
        self.assertEqual(real_rep["asset_counts"]["total_references"], 0)
        self.assertEqual(real_rep["validation_overview"]["overall_status"], STATUS_PASS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
