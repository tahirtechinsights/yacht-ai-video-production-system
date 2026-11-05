# Managed Media Intake & Asset Manifest System (`YVP-SYS-002`)

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `pipeline\intake\README.md`  
**Version:** `1.0.0`

---

## 1. Managed Intake Architecture

The Managed Media Intake system ingests external yacht reference images and videos into isolated production workspaces through a deterministic, non-destructive nine-stage pipeline:

```text
[External Source File]
        │
        ▼
[1. Pre-Intake File Inspection]    (Existence, regular file, symlink/junction rejection, non-zero size)
        │
        ▼
[2. File Type Validation]          (Extension & MIME classification: image vs. video)
        │
        ▼
[3. SHA-256 Calculation]           (Streamed 64KB chunked hash of external source)
        │
        ▼
[4. Duplicate Content Detection]   (Checks production manifest by SHA-256; skips second copy if already registered)
        │
        ▼
[5. Temporary Managed Copy]        (Copies source to .<ASSET_ID>.<UUID>.part without modifying source)
        │
        ▼
[6. Copy Integrity Verification]   (Verifies copied_sha256 == source_sha256 and byte size equality)
        │
        ▼
[7. Finalize Managed Copy]         (Atomically renames verified temp copy to REF-<NNN>.<ext>)
        │
        ▼
[8. Technical Metadata Extraction] (Pillow for images; FFprobe or Python stdlib ISO-BMFF fallback for videos)
        │
        ▼
[9. Atomic Manifest Registration]  (Validates record & atomically replaces assets/asset-manifest.json)
        │
        ▼
[Intake Summary Report]
```

- **External Source Protection:** The external source file is opened strictly in read-only mode and is never modified, moved, or deleted.
- **Managed Copy Immutability:** Once finalized under `productions/<PROD-ID>/references/{images|videos}/`, managed reference copies are marked `immutable_locked: true` and are never overwritten, resized, recompressed, or converted.

---

## 2. Media Storage Conventions

Within each production workspace (`productions/<PRODUCTION-ID>/`), managed reference files are segregated by media type:

```text
productions/<PRODUCTION-ID>/
├── assets/
│   └── asset-manifest.json
└── references/
    ├── images/
    │   ├── .gitkeep
    │   ├── REF-001.jpg
    │   └── REF-002.png
    └── videos/
        ├── .gitkeep
        └── REF-003.mp4
```

- **Controlled Naming Convention:** Managed files are named `<ASSET_ID><normalized_lowercase_extension>` (e.g., `REF-001.jpg`, `REF-002.png`, `REF-003.mp4`).
- **Original Metadata Preservation:** The original filename (`original_filename`), original extension (`file_extension`), full source path (`original_source_path`), SHA-256 (`sha256`), and UTC timestamp (`intake_timestamp` / `ingested_at_utc`) are preserved in `assets/asset-manifest.json`.
- **Git Exclusion:** All binary media files inside `references/images/` and `references/videos/` are excluded from Git via `.gitignore`, while `.gitkeep` and `assets/asset-manifest.json` remain eligible for Git tracking.

---

## 3. Supported Formats

| Media Type | Supported Extensions | MIME Types |
|---|---|---|
| **Image (`image`)** | `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`, `.webp`, `.bmp` | `image/jpeg`, `image/png`, `image/tiff`, `image/webp`, `image/bmp` |
| **Video (`video`)** | `.mp4`, `.mov`, `.m4v`, `.mkv`, `.avi`, `.webm`, `.mxf` | `video/mp4`, `video/quicktime`, `video/x-m4v`, `video/x-matroska`, `video/x-msvideo`, `video/webm`, `application/mxf` |

Files with unsupported extensions or `0`-byte size are deterministically rejected prior to copying.

---

## 4. Asset ID Allocation & Duplicate Handling

1. **ID Format:** Follows the authoritative governance convention `REF-<NNN>` (`REF-001`, `REF-002`, `REF-003`, automatically expanding digits for `>= 1000`). The validator accepts `^REF-\d{3,6}$` (`REF-001` through `REF-999999`).
2. **No Identifier Reuse:** The allocator inspects both `manifest["source_references"]` and all existing filenames inside `references/images/` and `references/videos/`, assigning `max_existing_index + 1`.
3. **SHA-256 Duplicate Detection:**
   - Before copying, the source file's SHA-256 digest is compared against all registered `source_references` in the target production's manifest.
   - If an identical SHA-256 already exists in the same production, the intake operation returns `DUPLICATE_SKIPPED`, reports the existing `asset_id` and `managed_relative_path`, and does **not** create a duplicate managed copy.
   - Identical files ingested into **different** productions (e.g., `TEST-PROD-A` vs. `TEST-PROD-B`) remain completely isolated per production workspace.

---

## 5. Manifest Schema Usage

Each production's manifest lives at `productions/<PRODUCTION-ID>/assets/asset-manifest.json` and adheres to `TPL-ASSET-MANIFEST` (`v1.1.0`).

Key fields recorded per entry in `source_references[]`:
- `production_id`: Production identifier (e.g., `YACHT-001`)
- `reference_id` & `asset_id`: Assigned reference ID (e.g., `REF-001`)
- `media_type` & `asset_type`: `"image"` or `"video"`
- `original_filename` & `original_source_path`: Original file provenance
- `relative_path`: Production-relative path (`references/images/REF-001.jpg`)
- `managed_relative_path`: Repository-relative path (`productions/YACHT-001/references/images/REF-001.jpg`)
- `sha256` & `file_size`: Verified cryptographic hash and byte count
- `mime_type` & `file_extension`: Media classification
- `ingested_at_utc` & `intake_timestamp`: ISO-8601 UTC registration time
- `technical_metadata`: Extracted technical parameters
- `validation_status`: Technical validation status (`PASS`, `WARNING`, `FAIL`, `NOT_TESTED`)
- `approval_status`: Human approval status (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED`)
- `provenance`: Checksum verification and immutability record

> **Governance Separation Rule:** Technical validation (`validation_status`) is strictly separated from creative/identity sign-off (`approval_status`). Newly registered assets always receive `"approval_status": "PENDING_REVIEW"` regardless of whether `validation_status` is `PASS` or `WARNING`.

---

## 6. Technical Metadata Extraction

### Images (`extract_image_metadata`)
Uses **Pillow (`PIL`)** to extract:
- `width` and `height` (pixels)
- `format` (`PNG`, `JPEG`, `TIFF`, `WEBP`, `BMP`)
- `colour_mode` (`RGB`, `RGBA`, `L`, `CMYK`)
- `colour_profile` (Embedded ICC profile description, EXIF ColorSpace tag, or `"untagged"`)
- `orientation` (EXIF Orientation code and label if present, else `null`)
- `file_size` (bytes)
- `aspect_ratio` (Simplified ratio string, e.g., `"16:9"`)

### Videos (`extract_video_metadata`)
- **Primary Extractor (`ffprobe`):** When `ffprobe` is available on `PATH`, extracts `width`, `height`, `container_format`, `video_codec`, `frame_rate`, `duration`, `aspect_ratio`, `audio_stream_present`, and `file_size`.
- **Fallback Extractor (`python_stdlib_isobmff`):** When `ffprobe` is not installed on the system, the extractor explicitly logs `"missing_dependencies": ["ffprobe"]` in the metadata warnings and uses a pure-Python standard-library ISO-BMFF (`MP4`/`MOV`) binary atom parser (`ftyp`, `mvhd`, `tkhd`, `mdhd`, `hdlr`, `stsd`, `stts`) to extract real stream headers without fabricating values.

---

## 7. Deterministic Validation Rules

The validation engine (`pipeline/intake/validator.py`) executes 11 deterministic checks:

| Check Name | Failure Condition (`FAIL`) | Warning Condition (`WARNING`) |
|---|---|---|
| `valid_production_id` | Invalid ID syntax or manifest mismatch | — |
| `manifest_consistency` | Missing required schema fields or invalid status enum | — |
| `duplicate_detection` | Duplicate `asset_id` or `sha256` within same manifest | — |
| `path_containment` | Path escapes `productions/<ID>/references/` or uses symlink/junction | — |
| `file_existence` | Managed file missing on disk | — |
| `supported_extension` | Extension not in supported image/video sets | — |
| `file_readability` | Managed file cannot be opened for reading | — |
| `nonzero_file_size` | File size is `0` bytes or mismatches manifest `file_size` | — |
| `sha256_integrity` | Disk SHA-256 differs from manifest `sha256` | — |
| `managed_copy_checksum_equality` | `source_sha256 != managed_sha256` | — |
| `source_quality_advisory` | Corrupt/unreadable media stream | Resolution `< 1920x1080`, aspect ratio `!= 16:9`, image long edge `< 1280px`, or optional `ffprobe` missing |

---

## 8. Command-Line Interface (CLI) Usage

Run commands from the repository root (`E:\Yacht-AI-Video-Production`):

```powershell
# 1. Intake one or more external reference files into YACHT-001
python -m pipeline.intake.cli intake --production YACHT-001 --zone exterior "C:\path\to\yacht_photo.jpg"

# 2. Validate all registered assets and manifest integrity for YACHT-001
python -m pipeline.intake.cli validate --production YACHT-001

# 3. List registered reference assets in YACHT-001
python -m pipeline.intake.cli list --production YACHT-001

# 4. Inspect full JSON metadata & provenance for a specific asset ID
python -m pipeline.intake.cli inspect --production YACHT-001 REF-001

# 5. Generate an intake, validation, and dependency summary report
python -m pipeline.intake.cli report --production YACHT-001

# 6. Run standalone tools wrappers
python tools/validation/validate_manifest.py --production YACHT-001
python tools/media-processing/media_inspector.py --check-deps
```

Add `--json` to `intake`, `validate`, `list`, or `report` for machine-readable JSON output.

---

## 9. Error Handling, Recovery & Future Productions

- **Failed-Copy Recovery:** Files are copied to a hidden `.part` file (`references/{images|videos}/.<ASSET_ID>.<UUID>.part`) and verified via SHA-256 before being moved to their final `REF-<NNN>.<ext>` name. Any I/O error or checksum mismatch automatically deletes the `.part` file in a `finally` block and aborts before touching `asset-manifest.json`.
- **Atomic Manifest Updates:** Updates to `asset-manifest.json` are written to `.asset-manifest.<UUID>.tmp`, flushed to disk with `os.fsync()`, and swapped atomically via `os.replace()`.
- **Initializing Future Productions:** Pass `--init-production` with a new production ID (e.g., `python -m pipeline.intake.cli intake --production YACHT-002 --init-production <file>`) or call `ensure_production_workspace("YACHT-002", create_if_missing=True)` to scaffold an isolated workspace and manifest without code changes.
