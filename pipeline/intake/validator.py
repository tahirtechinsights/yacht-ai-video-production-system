"""Deterministic Validation Engine for Managed Media Intake & Manifests (YVP-SYS-002).

Implements deterministic checks distinguishing PASS, FAIL, WARNING, and NOT_TESTED:
1. File existence
2. Supported extension
3. File readability
4. Nonzero file size
5. SHA-256 integrity
6. Managed copy checksum equality
7. Duplicate detection
8. Manifest consistency
9. Valid production ID
10. Asset path containment within the authorized repository & symlink/junction rejection
11. Source-quality advisory checks (resolution, aspect ratio, metadata extractor status)
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .metadata import (
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    classify_extension,
)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_WARNING = "WARNING"
STATUS_NOT_TESTED = "NOT_TESTED"

VALID_APPROVAL_STATUSES = {"PENDING_REVIEW", "APPROVED", "REJECTED", "SUPERSEDED"}
VALID_VALIDATION_STATUSES = {STATUS_PASS, STATUS_FAIL, STATUS_WARNING, STATUS_NOT_TESTED}

PRODUCTION_ID_REGEX = re.compile(r"^[A-Z0-9]+-[A-Z0-9_-]+$")
ASSET_ID_REGEX = re.compile(r"^REF-\d{3,6}$")

REQUIRED_SOURCE_REFERENCE_FIELDS = {
    "production_id",
    "reference_id",
    "asset_id",
    "media_type",
    "asset_type",
    "original_filename",
    "original_source_path",
    "relative_path",
    "managed_relative_path",
    "sha256",
    "file_size",
    "mime_type",
    "file_extension",
    "ingested_at_utc",
    "intake_timestamp",
    "immutable_locked",
    "technical_metadata",
    "validation_status",
    "approval_status",
    "provenance",
}


def compute_sha256(file_path: Path, chunk_size: int = 65536) -> str:
    """Calculate lowercase hex SHA-256 digest of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def is_unsafe_symlink_or_reparse(path: Path) -> bool:
    """Detect symbolic links, NTFS junctions, or reparse points on Windows and POSIX."""
    try:
        if path.is_symlink():
            return True
        if hasattr(path, "is_junction") and path.is_junction():  # Python 3.12+
            return True
        st = os.lstat(path)
        file_attrs = getattr(st, "st_file_attributes", 0)
        if file_attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
            return True
    except OSError:
        return False
    return False


def has_reparse_in_chain(target_path: Path, stop_at: Optional[Path] = None) -> bool:
    """Check if target_path or any of its existing ancestors (up to stop_at) is a symlink or junction."""
    curr = target_path
    stop_resolved = stop_at.resolve() if stop_at and stop_at.exists() else None
    visited = set()
    while curr not in visited:
        visited.add(curr)
        if curr.exists() or curr.is_symlink():
            if is_unsafe_symlink_or_reparse(curr):
                return True
        if stop_resolved is not None:
            try:
                if curr.exists() and curr.resolve() == stop_resolved:
                    break
            except OSError:
                pass
        if curr.parent == curr:
            break
        curr = curr.parent
    return False


def validate_production_id(production_id: str) -> bool:
    """Verify production ID format and ensure no path traversal tokens exist."""
    if not production_id or not isinstance(production_id, str):
        return False
    if ".." in production_id or "/" in production_id or "\\" in production_id or ":" in production_id:
        return False
    return bool(PRODUCTION_ID_REGEX.match(production_id))


def check_path_containment(target_path: Path, allowed_root: Path) -> Tuple[bool, str]:
    """Verify that target_path resolves strictly inside allowed_root without symlink/junction traversal."""
    try:
        resolved_root = allowed_root.resolve()
        # Check raw path components for '..' before resolving
        if ".." in target_path.parts:
            return False, f"Path contains prohibited '..' traversal token: {target_path}"
        if has_reparse_in_chain(target_path, stop_at=resolved_root):
            return False, f"Unsafe symbolic link or NTFS junction detected in path chain: {target_path}"
        resolved_target = target_path.resolve()
        if not resolved_target.is_relative_to(resolved_root):
            return False, f"Resolved path '{resolved_target}' escapes authorized root '{resolved_root}'"
        return True, "Path strictly contained within authorized directory"
    except Exception as exc:
        return False, f"Path containment verification error: {exc}"


def evaluate_source_quality_warnings(
    media_type: str, technical_metadata: Dict[str, Any]
) -> Tuple[str, List[str], List[str]]:
    """Evaluate technical metadata against standards, recording non-fatal source issues as WARNING."""
    warnings: List[str] = []
    errors: List[str] = []

    if not technical_metadata:
        return STATUS_NOT_TESTED, ["Technical metadata missing"], []

    ext_status = technical_metadata.get("extraction_status", STATUS_NOT_TESTED)
    for w in technical_metadata.get("warnings", []):
        warnings.append(w)

    if ext_status in {"FAILED", "FAILED_MISSING_DEPENDENCY", "FAILED_NO_FFPROBE"}:
        missing_deps = technical_metadata.get("missing_dependencies", [])
        if missing_deps:
            warnings.append(
                f"Metadata extraction incomplete due to unavailable optional dependency: {', '.join(missing_deps)}"
            )
        else:
            for err in technical_metadata.get("errors", []):
                errors.append(err)
            return STATUS_FAIL, warnings, errors

    width = technical_metadata.get("width")
    height = technical_metadata.get("height")
    aspect_ratio = technical_metadata.get("aspect_ratio")

    if width is not None and height is not None:
        long_edge = max(int(width), int(height))
        if int(width) < 1920 or int(height) < 1080:
            warnings.append(
                f"Source resolution ({width}x{height}) is below final target delivery resolution (1920x1080); "
                "image enhancement/upscaling may be required prior to IMAGES_APPROVED gate."
            )
        if media_type == "image" and long_edge < 1280:
            warnings.append(
                f"Source image long edge ({long_edge}px) is below recommended minimum usable reference quality "
                "(1280px per standards/image-standards.md Section 3.3)."
            )
    else:
        warnings.append("Pixel dimensions (width/height) could not be verified.")

    if aspect_ratio is not None and aspect_ratio != "16:9":
        warnings.append(
            f"Source aspect ratio ({aspect_ratio}) differs from target delivery aspect ratio (16:9); "
            "framing/crop preparation will be required."
        )

    if warnings:
        return STATUS_WARNING, warnings, errors
    return STATUS_PASS, warnings, errors


def validate_source_file_pre_intake(source_path: Path) -> Dict[str, Any]:
    """Run pre-intake validation checks on an external source file before copying."""
    checks: Dict[str, str] = {}
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Symlink / Reparse check on external source
    if has_reparse_in_chain(source_path):
        checks["symlink_or_junction_safety"] = STATUS_FAIL
        errors.append(f"Rejected unsafe symbolic link or junction in source path: {source_path}")
        return {"overall_status": STATUS_FAIL, "checks": checks, "warnings": warnings, "errors": errors}
    checks["symlink_or_junction_safety"] = STATUS_PASS

    # 2. File existence & regular file check
    if not source_path.exists() or not source_path.is_file():
        checks["file_existence"] = STATUS_FAIL
        errors.append(f"Source file does not exist or is not a regular file: {source_path}")
        return {"overall_status": STATUS_FAIL, "checks": checks, "warnings": warnings, "errors": errors}
    checks["file_existence"] = STATUS_PASS

    # 3. Supported extension check
    media_type, ext, mime_type = classify_extension(source_path)
    if media_type is None:
        checks["supported_extension"] = STATUS_FAIL
        supported_list = sorted(list(SUPPORTED_IMAGE_EXTENSIONS.keys()) + list(SUPPORTED_VIDEO_EXTENSIONS.keys()))
        errors.append(
            f"Unsupported file extension '{ext}'. Supported extensions: {', '.join(supported_list)}"
        )
        return {"overall_status": STATUS_FAIL, "checks": checks, "warnings": warnings, "errors": errors}
    checks["supported_extension"] = STATUS_PASS

    # 4. File readability check
    try:
        with open(source_path, "rb") as f:
            f.read(16)
        checks["file_readability"] = STATUS_PASS
    except Exception as exc:
        checks["file_readability"] = STATUS_FAIL
        errors.append(f"Source file is not readable: {exc}")
        return {"overall_status": STATUS_FAIL, "checks": checks, "warnings": warnings, "errors": errors}

    # 5. Non-zero file size check
    file_size = source_path.stat().st_size
    if file_size <= 0:
        checks["nonzero_file_size"] = STATUS_FAIL
        errors.append(f"Source file is empty (0 bytes): {source_path}")
        return {"overall_status": STATUS_FAIL, "checks": checks, "warnings": warnings, "errors": errors}
    checks["nonzero_file_size"] = STATUS_PASS

    return {
        "overall_status": STATUS_PASS,
        "media_type": media_type,
        "file_extension": ext,
        "mime_type": mime_type,
        "file_size": file_size,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }


def validate_registered_asset(
    record: Dict[str, Any],
    manifest: Dict[str, Any],
    repo_root: Path,
    seen_ids: Optional[set] = None,
    seen_hashes: Optional[set] = None,
) -> Dict[str, Any]:
    """Deterministically validate a single registered asset record against filesystem and governance."""
    checks: Dict[str, str] = {}
    warnings: List[str] = []
    errors: List[str] = []

    prod_id = manifest.get("production_id", "")
    rec_prod_id = record.get("production_id", prod_id)
    asset_id = record.get("asset_id") or record.get("reference_id") or "<UNKNOWN>"

    # 1. Valid production ID
    if validate_production_id(prod_id) and rec_prod_id == prod_id:
        checks["valid_production_id"] = STATUS_PASS
    else:
        checks["valid_production_id"] = STATUS_FAIL
        errors.append(f"Invalid or mismatched production_id: manifest='{prod_id}', record='{rec_prod_id}'")

    # 2. Manifest consistency (required fields, ID format, approval status separation)
    missing_fields = [k for k in REQUIRED_SOURCE_REFERENCE_FIELDS if k not in record]
    ref_id = record.get("reference_id", "")
    ast_id = record.get("asset_id", "")
    approval_status = record.get("approval_status", "")

    if (
        not missing_fields
        and ref_id == ast_id
        and ASSET_ID_REGEX.match(str(ast_id))
        and approval_status in VALID_APPROVAL_STATUSES
    ):
        checks["manifest_consistency"] = STATUS_PASS
    else:
        checks["manifest_consistency"] = STATUS_FAIL
        if missing_fields:
            errors.append(f"Missing required manifest fields: {', '.join(sorted(missing_fields))}")
        if ref_id != ast_id or not ASSET_ID_REGEX.match(str(ast_id)):
            errors.append(f"Invalid or inconsistent asset_id/reference_id: '{ast_id}' / '{ref_id}'")
        if approval_status not in VALID_APPROVAL_STATUSES:
            errors.append(f"Invalid approval_status '{approval_status}'")

    # 3. Duplicate detection (within manifest)
    sha256_expected = record.get("sha256", "")
    dup_error = False
    if seen_ids is not None:
        if asset_id in seen_ids:
            dup_error = True
            errors.append(f"Duplicate asset_id detected in manifest: {asset_id}")
        seen_ids.add(asset_id)
    if seen_hashes is not None and sha256_expected:
        if sha256_expected in seen_hashes:
            dup_error = True
            errors.append(f"Duplicate SHA-256 checksum detected in manifest: {sha256_expected}")
        seen_hashes.add(sha256_expected)
    checks["duplicate_detection"] = STATUS_FAIL if dup_error else STATUS_PASS

    # 4. Path containment within authorized repository & production references directory
    managed_rel_str = record.get("managed_relative_path", "")
    prod_rel_str = record.get("relative_path", "")
    authorized_refs_root = repo_root / "productions" / prod_id / "references"

    if not managed_rel_str:
        checks["path_containment"] = STATUS_FAIL
        errors.append("Missing 'managed_relative_path' in asset record")
        managed_abs = repo_root / "__invalid__"
    else:
        # Reject absolute paths disguised as relative paths
        raw_rel = Path(managed_rel_str)
        raw_prod_rel = Path(prod_rel_str) if prod_rel_str else Path()
        if raw_rel.is_absolute() or ".." in raw_rel.parts or ".." in raw_prod_rel.parts:
            checks["path_containment"] = STATUS_FAIL
            errors.append(f"Path traversal or absolute path violation in manifest: '{managed_rel_str}'")
            managed_abs = repo_root / managed_rel_str
        else:
            managed_abs = repo_root / raw_rel
            ok_repo, msg_repo = check_path_containment(managed_abs, repo_root)
            ok_refs, msg_refs = check_path_containment(managed_abs, authorized_refs_root)
            if ok_repo and ok_refs:
                checks["path_containment"] = STATUS_PASS
            else:
                checks["path_containment"] = STATUS_FAIL
                errors.append(msg_refs if not ok_refs else msg_repo)

    # Stop filesystem access if path_containment failed
    if checks["path_containment"] != STATUS_PASS:
        for skipped in [
            "file_existence",
            "supported_extension",
            "file_readability",
            "nonzero_file_size",
            "sha256_integrity",
            "managed_copy_checksum_equality",
            "source_quality_advisory",
        ]:
            checks[skipped] = STATUS_FAIL
        return {
            "asset_id": asset_id,
            "validation_status": STATUS_FAIL,
            "checks": checks,
            "warnings": warnings,
            "errors": errors,
        }

    # 5. File existence
    if managed_abs.exists() and managed_abs.is_file() and not is_unsafe_symlink_or_reparse(managed_abs):
        checks["file_existence"] = STATUS_PASS
    else:
        checks["file_existence"] = STATUS_FAIL
        errors.append(f"Managed file missing or unsafe at: {managed_rel_str}")
        for skipped in [
            "supported_extension",
            "file_readability",
            "nonzero_file_size",
            "sha256_integrity",
            "managed_copy_checksum_equality",
            "source_quality_advisory",
        ]:
            checks[skipped] = STATUS_FAIL
        return {
            "asset_id": asset_id,
            "validation_status": STATUS_FAIL,
            "checks": checks,
            "warnings": warnings,
            "errors": errors,
        }

    # 6. Supported extension
    media_type, ext, _ = classify_extension(managed_abs)
    if media_type is not None and ext == record.get("file_extension", "").lower():
        checks["supported_extension"] = STATUS_PASS
    else:
        checks["supported_extension"] = STATUS_FAIL
        errors.append(f"Unsupported or mismatched extension on managed file: '{ext}'")

    # 7. File readability
    try:
        with open(managed_abs, "rb") as f:
            f.read(16)
        checks["file_readability"] = STATUS_PASS
    except Exception as exc:
        checks["file_readability"] = STATUS_FAIL
        errors.append(f"Managed file unreadable: {exc}")

    # 8. Non-zero file size
    actual_size = managed_abs.stat().st_size
    expected_size = record.get("file_size", -1)
    if actual_size > 0 and actual_size == expected_size:
        checks["nonzero_file_size"] = STATUS_PASS
    else:
        checks["nonzero_file_size"] = STATUS_FAIL
        errors.append(f"Invalid or mismatched file size: actual={actual_size}, manifest={expected_size}")

    # 9. SHA-256 integrity
    actual_sha256 = compute_sha256(managed_abs)
    if actual_sha256 == sha256_expected and len(actual_sha256) == 64:
        checks["sha256_integrity"] = STATUS_PASS
    else:
        checks["sha256_integrity"] = STATUS_FAIL
        errors.append(
            f"SHA-256 mismatch on managed file: actual={actual_sha256}, manifest={sha256_expected}"
        )

    # 10. Managed copy checksum equality (Provenance verification)
    prov = record.get("provenance") or {}
    source_sha = prov.get("source_sha256")
    managed_sha = prov.get("managed_sha256")
    if (
        source_sha
        and managed_sha
        and source_sha == managed_sha == actual_sha256
        and prov.get("checksum_verified") is True
    ):
        checks["managed_copy_checksum_equality"] = STATUS_PASS
    else:
        checks["managed_copy_checksum_equality"] = STATUS_FAIL
        errors.append("Provenance source_sha256 and managed_sha256 equality check failed.")

    # 11. Technical metadata & source quality advisory
    tech_meta = record.get("technical_metadata") or {}
    q_status, q_warnings, q_errors = evaluate_source_quality_warnings(
        record.get("media_type", media_type or "image"), tech_meta
    )
    checks["source_quality_advisory"] = q_status
    warnings.extend(q_warnings)
    errors.extend(q_errors)

    # Overall status calculation
    if any(v == STATUS_FAIL for v in checks.values()) or errors:
        overall = STATUS_FAIL
    elif any(v == STATUS_WARNING for v in checks.values()) or warnings:
        overall = STATUS_WARNING
    else:
        overall = STATUS_PASS

    return {
        "asset_id": asset_id,
        "validation_status": overall,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }


def validate_production_manifest(production_id: str, repo_root: Path) -> Dict[str, Any]:
    """Validate an entire production manifest and all registered source_references."""
    if not validate_production_id(production_id):
        return {
            "production_id": production_id,
            "overall_status": STATUS_FAIL,
            "manifest_path": None,
            "asset_results": [],
            "errors": [f"Invalid production ID format: '{production_id}'"],
            "warnings": [],
        }

    prod_dir = repo_root / "productions" / production_id
    manifest_path = prod_dir / "assets" / "asset-manifest.json"
    ok_containment, msg_containment = check_path_containment(manifest_path, repo_root)
    if not ok_containment:
        return {
            "production_id": production_id,
            "overall_status": STATUS_FAIL,
            "manifest_path": str(manifest_path),
            "asset_results": [],
            "errors": [msg_containment],
            "warnings": [],
        }

    if not manifest_path.exists():
        return {
            "production_id": production_id,
            "overall_status": STATUS_FAIL,
            "manifest_path": str(manifest_path),
            "asset_results": [],
            "errors": [f"Manifest file does not exist: {manifest_path}"],
            "warnings": [],
        }

    try:
        import json

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as exc:
        return {
            "production_id": production_id,
            "overall_status": STATUS_FAIL,
            "manifest_path": str(manifest_path),
            "asset_results": [],
            "errors": [f"Failed to parse manifest JSON: {exc}"],
            "warnings": [],
        }

    errors: List[str] = []
    warnings: List[str] = []

    if manifest.get("production_id") != production_id:
        errors.append(
            f"Manifest top-level production_id ('{manifest.get('production_id')}') "
            f"does not match requested production ('{production_id}')."
        )

    source_refs = manifest.get("source_references")
    if not isinstance(source_refs, list):
        errors.append("Manifest 'source_references' must be a list.")
        source_refs = []

    seen_ids: set = set()
    seen_hashes: set = set()
    asset_results: List[Dict[str, Any]] = []

    for rec in source_refs:
        res = validate_registered_asset(
            rec, manifest, repo_root, seen_ids=seen_ids, seen_hashes=seen_hashes
        )
        asset_results.append(res)

    if errors or any(r["validation_status"] == STATUS_FAIL for r in asset_results):
        overall = STATUS_FAIL
    elif warnings or any(r["validation_status"] == STATUS_WARNING for r in asset_results):
        overall = STATUS_WARNING
    else:
        overall = STATUS_PASS

    return {
        "production_id": production_id,
        "overall_status": overall,
        "manifest_path": str(manifest_path.relative_to(repo_root).as_posix()),
        "total_assets": len(asset_results),
        "pass_count": sum(1 for r in asset_results if r["validation_status"] == STATUS_PASS),
        "warning_count": sum(1 for r in asset_results if r["validation_status"] == STATUS_WARNING),
        "fail_count": sum(1 for r in asset_results if r["validation_status"] == STATUS_FAIL),
        "asset_results": asset_results,
        "errors": errors,
        "warnings": warnings,
    }
