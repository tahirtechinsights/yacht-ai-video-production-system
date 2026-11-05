# Asset Manifest Template & Schema Guide

**Template ID:** `TPL-ASSET-MANIFEST`  
**Template Version:** `1.1.0`  
**Companion File:** [`asset-manifest-template.json`](asset-manifest-template.json)  
**Purpose:** Document the required fields, status enumerations, managed intake extensions, and provenance lineage rules for `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.

---

## 1. Overview

Every production workspace maintains a single authoritative `asset-manifest.json` inside `productions\<PRODUCTION-ID>\assets\`. Because heavy binary media files are excluded from Git via `.gitignore`, the Asset Manifest serves as the version-controlled ledger of record for all media assets, prompts, candidates, and deliverables.

---

## 2. Required Top-Level Sections

1. **Header & Storage Policy:**
   - `template_id` (`TPL-ASSET-MANIFEST`) & `template_version` (`1.1.0`)
   - `production_id` (e.g., `YACHT-001`)
   - `lifecycle_state` (Current state from `DRAFT` through `DELIVERED`)
   - `storage_policy` (Defines local media storage root, `intake_model: "MANAGED"`, `managed_subdirectories` (`references/images` and `references/videos`), and confirms binaries are excluded from Git)
2. **`source_references[]` (Managed Reference Intake Contract):**
   - Registers immutable client/vessel reference files copied into `productions/<PRODUCTION-ID>/references/{images|videos}/`.
   - Required fields mapped across `v1.0.0` and `v1.1.0` conventions:
     - `production_id`: Production identifier (e.g., `YACHT-001`)
     - `reference_id` / `asset_id`: Unique reference identifier (`REF-001`, `REF-002`, ...)
     - `media_type` / `asset_type`: `"image"` or `"video"`
     - `original_filename`: Original source filename (e.g., `hull_starboard.jpg`)
     - `original_source_path`: Full path to the external source file at intake time
     - `relative_path`: Production-relative path (e.g., `references/images/REF-001.jpg`)
     - `managed_relative_path`: Repository-relative path (e.g., `productions/YACHT-001/references/images/REF-001.jpg`)
     - `sha256`: 64-character lowercase hex SHA-256 digest
     - `file_size`: File size in bytes
     - `mime_type`: Detected MIME type (e.g., `image/jpeg`, `video/mp4`)
     - `file_extension`: Normalized lowercase extension (e.g., `.jpg`, `.mp4`)
     - `format` & `resolution`: High-level format and `WxH` resolution summary
     - `ingested_at_utc` / `intake_timestamp`: ISO-8601 UTC timestamp
     - `immutable_locked`: `true`
     - `technical_metadata`: Extracted image or video technical metadata object
     - `validation_status`: Technical validation status (`PASS`, `WARNING`, `FAIL`, `NOT_TESTED`)
     - `validation_summary`: Detailed per-check validation outcomes, warnings, and errors
     - `approval_status`: Human creative/identity approval status (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED`) — strictly separate from `validation_status`
     - `provenance`: Structured provenance record (`intake_model`, `original_source_path`, `source_sha256`, `managed_sha256`, `checksum_verified`, `ingested_at_utc`, `immutable_after_registration`)
     - `vessel_zone` & `notes`: Optional descriptive annotations
3. **`prepared_assets[]`:**
   - Tracks keyframe images in `assets\` prepared from `source_references`.
4. **`video_candidates[]`:**
   - Tracks every generated I2V candidate take in `generations\`.
5. **`deliverables[]`:**
   - Tracks final assembled master exports in `deliverables\` and their complete upstream `source_lineage`.

---

## 3. Separation of Technical Validation vs. Human Approval Status

| Field | Allowed Values | Authority & Meaning |
|---|---|---|
| **`validation_status`** | `PASS`, `WARNING`, `FAIL`, `NOT_TESTED` | Automated deterministic check result. `WARNING` indicates non-fatal source quality advisories (e.g., resolution below `1920x1080` or optional `ffprobe` unavailable). |
| **`approval_status`** | `PENDING_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED` | Human Production Authority sign-off. A technically valid file (`PASS` or `WARNING`) always starts as `PENDING_REVIEW` and never auto-approves. |
