"""Managed Media Intake Workflow & Atomic Manifest Manager (YVP-SYS-002).

Implements the Managed Intake Architecture:
External Source -> File Inspection -> File Type Validation -> SHA-256 Calculation
-> Duplicate Check -> Managed Copy (Temp) -> Copy Integrity Verification
-> Finalize Managed Copy -> Technical Metadata Extraction -> Manifest Registration
-> Intake Report.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .metadata import (
    check_dependencies,
    extract_image_metadata,
    extract_video_metadata,
)
from .validator import (
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WARNING,
    check_path_containment,
    compute_sha256,
    validate_production_id,
    validate_production_manifest,
    validate_registered_asset,
    validate_source_file_pre_intake,
)


class IntakeError(Exception):
    """Raised when a safety, governance, or containment violation prevents operation."""


def get_default_repo_root() -> Path:
    """Resolve the repository root directory from this module's location."""
    return Path(__file__).resolve().parents[2]


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_default_manifest(production_id: str) -> Dict[str, Any]:
    """Build an initialized canonical v1.1.0 asset manifest dictionary."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "template_id": "TPL-ASSET-MANIFEST",
        "template_version": "1.1.0",
        "purpose": (
            "Track immutable source references, prepared keyframe assets, generation metadata, "
            "video candidates, approval statuses, and final deliverable lineage for a single "
            "yacht video production."
        ),
        "production_id": production_id,
        "lifecycle_state": "DRAFT",
        "last_updated_utc": utc_now_iso(),
        "storage_policy": {
            "mode": "colocated_workspace",
            "intake_model": "MANAGED",
            "media_root": ".",
            "git_tracks_binaries": false_bool(),
            "managed_subdirectories": {
                "image": "references/images",
                "video": "references/videos",
            },
        },
        "source_references": [],
        "prepared_assets": [],
        "video_candidates": [],
        "deliverables": [],
    }


def false_bool() -> bool:
    return False


def ensure_production_workspace(
    production_id: str, repo_root: Optional[Path] = None, create_if_missing: bool = False
) -> Dict[str, Path]:
    """Validate production workspace paths and ensure managed reference subdirectories exist."""
    root = (repo_root or get_default_repo_root()).resolve()
    if not validate_production_id(production_id):
        raise IntakeError(
            f"Invalid production ID '{production_id}'. Expected alphanumeric pattern like 'YACHT-001'."
        )

    prod_dir = root / "productions" / production_id
    ok_containment, msg = check_path_containment(prod_dir, root / "productions")
    if not ok_containment:
        raise IntakeError(msg)

    if not prod_dir.exists():
        if not create_if_missing:
            raise IntakeError(
                f"Production workspace 'productions/{production_id}' does not exist. "
                "Pass --init-production to initialize a new production workspace."
            )
        for sub in [
            "brief",
            "references",
            "references/images",
            "references/videos",
            "assets",
            "prompts",
            "generations",
            "editing",
            "qa",
            "deliverables",
        ]:
            d = prod_dir / sub
            d.mkdir(parents=True, exist_ok=True)
            keep = d / ".gitkeep"
            if not keep.exists():
                keep.write_text("", encoding="utf-8")

    refs_dir = prod_dir / "references"
    images_dir = refs_dir / "images"
    videos_dir = refs_dir / "videos"
    assets_dir = prod_dir / "assets"
    manifest_path = assets_dir / "asset-manifest.json"

    for d in [refs_dir, images_dir, videos_dir, assets_dir]:
        ok_d, msg_d = check_path_containment(d, prod_dir)
        if not ok_d:
            raise IntakeError(msg_d)
        d.mkdir(parents=True, exist_ok=True)

    if not manifest_path.exists():
        default_manifest = create_default_manifest(production_id)
        save_manifest_atomic(default_manifest, manifest_path, root)

    return {
        "repo_root": root,
        "prod_dir": prod_dir,
        "refs_dir": refs_dir,
        "images_dir": images_dir,
        "videos_dir": videos_dir,
        "assets_dir": assets_dir,
        "manifest_path": manifest_path,
    }


def load_manifest(production_id: str, repo_root: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate JSON structure of a production's asset-manifest.json."""
    root = (repo_root or get_default_repo_root()).resolve()
    if not validate_production_id(production_id):
        raise IntakeError(f"Invalid production ID '{production_id}'.")

    manifest_path = root / "productions" / production_id / "assets" / "asset-manifest.json"
    ok_containment, msg = check_path_containment(manifest_path, root)
    if not ok_containment:
        raise IntakeError(msg)

    if not manifest_path.exists():
        raise IntakeError(f"Manifest not found for production '{production_id}' at {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        raise IntakeError(
            f"Corrupted or unreadable manifest at {manifest_path}: {exc}. "
            "Recovery guidance: Restore from last known good backup or re-initialize if empty."
        ) from exc

    if not isinstance(data, dict) or data.get("production_id") != production_id:
        raise IntakeError(
            f"Manifest production_id mismatch in {manifest_path}: "
            f"expected '{production_id}', found '{data.get('production_id') if isinstance(data, dict) else None}'."
        )
    if "source_references" not in data or not isinstance(data["source_references"], list):
        raise IntakeError(f"Manifest missing valid 'source_references' array in {manifest_path}.")

    return data


def save_manifest_atomic(manifest: Dict[str, Any], manifest_path: Path, repo_root: Path) -> None:
    """Atomically write updated manifest JSON via temp file + fsync + os.replace."""
    ok_containment, msg = check_path_containment(manifest_path, repo_root)
    if not ok_containment:
        raise IntakeError(msg)

    manifest["last_updated_utc"] = utc_now_iso()
    temp_path = manifest_path.parent / f".asset-manifest.{uuid.uuid4().hex}.tmp"
    try:
        serialized = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(serialized)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, manifest_path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def allocate_next_asset_id(manifest: Dict[str, Any], refs_dir: Path) -> str:
    """Allocate the next sequential REF-NNN identifier without reusing any manifest or disk ID."""
    max_num = 0
    id_pattern = re.compile(r"^REF-(\d+)$", re.IGNORECASE)

    for rec in manifest.get("source_references", []):
        for key in ("asset_id", "reference_id"):
            val = str(rec.get(key, ""))
            m = id_pattern.match(val)
            if m:
                max_num = max(max_num, int(m.group(1)))

    # Also scan managed directories to ensure zero collision with any file on disk
    for sub in ("images", "videos"):
        sub_dir = refs_dir / sub
        if sub_dir.exists():
            for p in sub_dir.iterdir():
                m = id_pattern.match(p.stem)
                if m:
                    max_num = max(max_num, int(m.group(1)))

    next_num = max_num + 1
    return f"REF-{next_num:03d}"


def intake_single_file(
    source_file: Path,
    production_id: str = "YACHT-001",
    repo_root: Optional[Path] = None,
    vessel_zone: str = "unspecified",
    notes: str = "",
    init_production: bool = False,
    _simulate_copy_failure: bool = False,
) -> Dict[str, Any]:
    """Execute the complete managed intake workflow for a single external source file."""
    root = (repo_root or get_default_repo_root()).resolve()
    paths = ensure_production_workspace(production_id, root, create_if_missing=init_production)
    manifest = load_manifest(production_id, root)

    # Step 1 & 2: File Inspection & File Type Validation
    pre_check = validate_source_file_pre_intake(source_file)
    if pre_check["overall_status"] != STATUS_PASS:
        return {
            "intake_status": "REJECTED",
            "production_id": production_id,
            "source_path": str(source_file),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": pre_check["errors"],
            "warnings": pre_check["warnings"],
        }

    resolved_source = source_file.resolve()
    media_type: str = pre_check["media_type"]
    ext: str = pre_check["file_extension"]
    mime_type: str = pre_check["mime_type"]
    source_size: int = pre_check["file_size"]

    # Prevent intaking a file that is already inside the managed references directory of this production
    if resolved_source.is_relative_to(paths["refs_dir"].resolve()):
        return {
            "intake_status": "REJECTED",
            "production_id": production_id,
            "source_path": str(source_file),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": [
                f"Source file '{resolved_source}' is already inside the managed references directory."
            ],
            "warnings": [],
        }

    # Step 3: SHA-256 Calculation on Source
    source_sha256 = compute_sha256(resolved_source)

    # Step 4: Duplicate Content Detection by SHA-256 within same production
    for existing in manifest.get("source_references", []):
        if existing.get("sha256") == source_sha256:
            existing_id = existing.get("asset_id") or existing.get("reference_id")
            return {
                "intake_status": "DUPLICATE_SKIPPED",
                "production_id": production_id,
                "source_path": str(resolved_source),
                "asset_id": existing_id,
                "existing_managed_path": existing.get("managed_relative_path"),
                "sha256": source_sha256,
                "validation_status": existing.get("validation_status", STATUS_PASS),
                "errors": [],
                "warnings": [
                    f"Duplicate content detected (SHA-256: {source_sha256}). "
                    f"Already registered in {production_id} as '{existing_id}'. "
                    "Skipped creating a second managed copy."
                ],
            }

    # Allocate unique Asset ID
    asset_id = allocate_next_asset_id(manifest, paths["refs_dir"])
    target_dir = paths["images_dir"] if media_type == "image" else paths["videos_dir"]
    managed_filename = f"{asset_id}{ext}"
    final_dest = target_dir / managed_filename

    ok_dest, msg_dest = check_path_containment(final_dest, paths["refs_dir"])
    if not ok_dest:
        return {
            "intake_status": "FAILED",
            "production_id": production_id,
            "source_path": str(resolved_source),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": [msg_dest],
            "warnings": [],
        }

    # Never overwrite an existing managed asset
    if final_dest.exists():
        return {
            "intake_status": "FAILED",
            "production_id": production_id,
            "source_path": str(resolved_source),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": [f"Refusing to overwrite existing managed file: {final_dest}"],
            "warnings": [],
        }

    # Step 5 & 6: Managed Copy to Temporary File + Copy Integrity Verification
    temp_dest = target_dir / f".{asset_id}.{uuid.uuid4().hex}.part"
    try:
        shutil.copy2(resolved_source, temp_dest)
        if _simulate_copy_failure:
            # Deterministic hook for testing failed-copy recovery (Section 14 Test #11)
            with open(temp_dest, "ab") as corrupt_f:
                corrupt_f.write(b"CORRUPT")

        copied_size = temp_dest.stat().st_size
        copied_sha256 = compute_sha256(temp_dest)

        if copied_size != source_size or copied_sha256 != source_sha256:
            raise IntakeError(
                f"Copy integrity verification failed for '{resolved_source}': "
                f"source_sha256={source_sha256} ({source_size}B) != "
                f"copied_sha256={copied_sha256} ({copied_size}B). "
                "Recovery: Temporary copy removed; manifest was not modified."
            )

        # Finalize managed copy only after integrity verification succeeds
        if final_dest.exists():
            raise IntakeError(f"Target managed path appeared during copy: {final_dest}")
        os.replace(temp_dest, final_dest)

    except Exception as exc:
        if temp_dest.exists():
            try:
                temp_dest.unlink()
            except OSError:
                pass
        return {
            "intake_status": "FAILED",
            "production_id": production_id,
            "source_path": str(resolved_source),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": [str(exc)],
            "warnings": [],
        }
    finally:
        if temp_dest.exists():
            try:
                temp_dest.unlink()
            except OSError:
                pass

    # Step 7: Technical Metadata Extraction
    if media_type == "image":
        tech_meta = extract_image_metadata(final_dest)
        fmt_summary = tech_meta.get("format") or ext.lstrip(".").upper()
    else:
        tech_meta = extract_video_metadata(final_dest)
        fmt_summary = tech_meta.get("container_format") or ext.lstrip(".").upper()

    w = tech_meta.get("width")
    h = tech_meta.get("height")
    res_summary = f"{w}x{h}" if (w and h) else "unknown"

    timestamp = utc_now_iso()
    prod_rel_path = final_dest.relative_to(paths["prod_dir"]).as_posix()
    repo_rel_path = final_dest.relative_to(root).as_posix()

    record: Dict[str, Any] = {
        "production_id": production_id,
        "reference_id": asset_id,
        "asset_id": asset_id,
        "media_type": media_type,
        "asset_type": media_type,
        "original_filename": resolved_source.name,
        "original_source_path": str(resolved_source),
        "relative_path": prod_rel_path,
        "managed_relative_path": repo_rel_path,
        "sha256": source_sha256,
        "file_size": source_size,
        "mime_type": mime_type,
        "file_extension": ext,
        "format": fmt_summary,
        "resolution": res_summary,
        "ingested_at_utc": timestamp,
        "intake_timestamp": timestamp,
        "immutable_locked": True,
        "technical_metadata": tech_meta,
        "validation_status": "NOT_TESTED",
        "validation_summary": {},
        "approval_status": "PENDING_REVIEW",
        "provenance": {
            "intake_model": "MANAGED",
            "original_source_path": str(resolved_source),
            "source_sha256": source_sha256,
            "managed_sha256": copied_sha256,
            "checksum_verified": True,
            "ingested_at_utc": timestamp,
            "immutable_after_registration": True,
        },
        "vessel_zone": vessel_zone,
        "notes": notes,
    }

    # Validate the newly constructed asset record deterministically
    val_result = validate_registered_asset(record, manifest, root)
    record["validation_status"] = val_result["validation_status"]
    record["validation_summary"] = {
        "checks": val_result["checks"],
        "warnings": val_result["warnings"],
        "errors": val_result["errors"],
    }

    # If deterministic validation failed unexpectedly, roll back the managed file and abort manifest update
    if val_result["validation_status"] == STATUS_FAIL:
        try:
            final_dest.unlink()
        except OSError:
            pass
        return {
            "intake_status": "FAILED",
            "production_id": production_id,
            "source_path": str(resolved_source),
            "asset_id": None,
            "validation_status": STATUS_FAIL,
            "errors": val_result["errors"],
            "warnings": val_result["warnings"],
        }

    # Step 8: Atomic Manifest Registration
    manifest["source_references"].append(record)
    save_manifest_atomic(manifest, paths["manifest_path"], root)

    return {
        "intake_status": "REGISTERED",
        "production_id": production_id,
        "asset_id": asset_id,
        "asset_type": media_type,
        "original_filename": resolved_source.name,
        "source_path": str(resolved_source),
        "managed_relative_path": repo_rel_path,
        "sha256": source_sha256,
        "file_size": source_size,
        "validation_status": record["validation_status"],
        "approval_status": record["approval_status"],
        "technical_metadata": tech_meta,
        "warnings": val_result["warnings"],
        "errors": val_result["errors"],
    }


def intake_files(
    source_files: List[Path],
    production_id: str = "YACHT-001",
    repo_root: Optional[Path] = None,
    vessel_zone: str = "unspecified",
    notes: str = "",
    init_production: bool = False,
) -> Dict[str, Any]:
    """Register one or more external media files and return an Intake Summary Report."""
    results: List[Dict[str, Any]] = []
    for src in source_files:
        res = intake_single_file(
            source_file=Path(src),
            production_id=production_id,
            repo_root=repo_root,
            vessel_zone=vessel_zone,
            notes=notes,
            init_production=init_production,
        )
        results.append(res)

    return {
        "production_id": production_id,
        "timestamp_utc": utc_now_iso(),
        "total_processed": len(results),
        "registered_count": sum(1 for r in results if r["intake_status"] == "REGISTERED"),
        "duplicate_count": sum(1 for r in results if r["intake_status"] == "DUPLICATE_SKIPPED"),
        "rejected_or_failed_count": sum(
            1 for r in results if r["intake_status"] in {"REJECTED", "FAILED"}
        ),
        "results": results,
    }


def list_assets(production_id: str = "YACHT-001", repo_root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return summary list of registered reference assets for a production."""
    manifest = load_manifest(production_id, repo_root)
    return manifest.get("source_references", [])


def inspect_asset(
    production_id: str, asset_id: str, repo_root: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieve full manifest and technical metadata entry for a specific asset ID."""
    manifest = load_manifest(production_id, repo_root)
    for rec in manifest.get("source_references", []):
        if rec.get("asset_id") == asset_id or rec.get("reference_id") == asset_id:
            return rec
    return None


def generate_intake_report(
    production_id: str = "YACHT-001", repo_root: Optional[Path] = None
) -> Dict[str, Any]:
    """Generate a comprehensive intake, metadata, dependency, and validation report for a production."""
    root = (repo_root or get_default_repo_root()).resolve()
    manifest = load_manifest(production_id, root)
    val_report = validate_production_manifest(production_id, root)
    deps = check_dependencies()

    refs = manifest.get("source_references", [])
    images = [r for r in refs if r.get("media_type") == "image"]
    videos = [r for r in refs if r.get("media_type") == "video"]

    return {
        "report_generated_utc": utc_now_iso(),
        "production_id": production_id,
        "lifecycle_state": manifest.get("lifecycle_state", "DRAFT"),
        "manifest_path": val_report.get("manifest_path"),
        "dependencies": deps,
        "asset_counts": {
            "total_references": len(refs),
            "images": len(images),
            "videos": len(videos),
            "pending_review": sum(1 for r in refs if r.get("approval_status") == "PENDING_REVIEW"),
            "approved": sum(1 for r in refs if r.get("approval_status") == "APPROVED"),
            "rejected": sum(1 for r in refs if r.get("approval_status") == "REJECTED"),
        },
        "validation_overview": {
            "overall_status": val_report["overall_status"],
            "pass_count": val_report["pass_count"],
            "warning_count": val_report["warning_count"],
            "fail_count": val_report["fail_count"],
        },
        "assets": [
            {
                "asset_id": r.get("asset_id"),
                "asset_type": r.get("asset_type"),
                "original_filename": r.get("original_filename"),
                "managed_relative_path": r.get("managed_relative_path"),
                "resolution": r.get("resolution"),
                "file_size": r.get("file_size"),
                "sha256": r.get("sha256"),
                "validation_status": r.get("validation_status"),
                "approval_status": r.get("approval_status"),
            }
            for r in refs
        ],
    }
