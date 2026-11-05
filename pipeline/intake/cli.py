"""Command-Line Interface for Managed Media Intake & Asset Manifest System (YVP-SYS-002).

Supported Commands:
  intake    Register one or more external source media files into a production workspace.
  validate  Run deterministic validation checks across a production manifest and managed files.
  list      List registered source reference assets for a production.
  inspect   Display full metadata and provenance for a specific registered asset ID.
  report    Generate a comprehensive intake, dependency, and validation summary report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

# Allow running directly as `python pipeline/intake/cli.py` or as `python -m pipeline.intake.cli`
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pipeline.intake.manager import (  # type: ignore
        IntakeError,
        generate_intake_report,
        get_default_repo_root,
        inspect_asset,
        intake_files,
        list_assets,
    )
    from pipeline.intake.validator import (  # type: ignore
        STATUS_FAIL,
        validate_production_manifest,
    )
else:
    from .manager import (
        IntakeError,
        generate_intake_report,
        get_default_repo_root,
        inspect_asset,
        intake_files,
        list_assets,
    )
    from .validator import STATUS_FAIL, validate_production_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yvp-intake",
        description="Yacht AI Video Production System — Managed Media Intake & Asset Manifest CLI",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Optional override for repository root path (defaults to E:\\Yacht-AI-Video-Production).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. intake
    p_intake = subparsers.add_parser("intake", help="Register one or more external source media files.")
    p_intake.add_argument(
        "--production",
        "-p",
        default="YACHT-001",
        help="Target Production ID (default: YACHT-001).",
    )
    p_intake.add_argument(
        "--zone",
        default="unspecified",
        choices=["exterior", "deck", "interior", "unspecified"],
        help="Optional yacht zone tag for registered reference(s).",
    )
    p_intake.add_argument("--notes", default="", help="Optional intake notes.")
    p_intake.add_argument(
        "--init-production",
        action="store_true",
        help="Initialize the production workspace directory structure if it does not yet exist.",
    )
    p_intake.add_argument("--json", action="store_true", help="Output result as formatted JSON.")
    p_intake.add_argument("files", nargs="+", type=Path, help="One or more source media file paths.")

    # 2. validate
    p_validate = subparsers.add_parser("validate", help="Validate registered assets in a production.")
    p_validate.add_argument(
        "--production",
        "-p",
        default="YACHT-001",
        help="Target Production ID (default: YACHT-001).",
    )
    p_validate.add_argument("--json", action="store_true", help="Output result as formatted JSON.")

    # 3. list
    p_list = subparsers.add_parser("list", help="List registered assets for a production.")
    p_list.add_argument(
        "--production",
        "-p",
        default="YACHT-001",
        help="Target Production ID (default: YACHT-001).",
    )
    p_list.add_argument("--json", action="store_true", help="Output result as formatted JSON.")

    # 4. inspect
    p_inspect = subparsers.add_parser("inspect", help="Display full metadata for a specific asset ID.")
    p_inspect.add_argument(
        "--production",
        "-p",
        default="YACHT-001",
        help="Target Production ID (default: YACHT-001).",
    )
    p_inspect.add_argument("asset_id", help="Asset ID to inspect (e.g. REF-001).")

    # 5. report
    p_report = subparsers.add_parser("report", help="Produce an intake & validation summary report.")
    p_report.add_argument(
        "--production",
        "-p",
        default="YACHT-001",
        help="Target Production ID (default: YACHT-001).",
    )
    p_report.add_argument("--json", action="store_true", help="Output report as formatted JSON.")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = (args.repo_root or get_default_repo_root()).resolve()

    try:
        if args.command == "intake":
            summary = intake_files(
                source_files=args.files,
                production_id=args.production,
                repo_root=repo_root,
                vessel_zone=args.zone,
                notes=args.notes,
                init_production=args.init_production,
            )
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print(f"=== Intake Summary ({summary['production_id']}) ===")
                print(
                    f"Processed: {summary['total_processed']} | "
                    f"Registered: {summary['registered_count']} | "
                    f"Duplicates Skipped: {summary['duplicate_count']} | "
                    f"Rejected/Failed: {summary['rejected_or_failed_count']}"
                )
                for res in summary["results"]:
                    status = res["intake_status"]
                    aid = res.get("asset_id") or "-"
                    src = res.get("source_path")
                    val = res.get("validation_status")
                    print(f"  [{status}] Asset={aid} Validation={val} Source={src}")
                    for w in res.get("warnings", []):
                        print(f"    WARNING: {w}")
                    for err in res.get("errors", []):
                        print(f"    ERROR:   {err}")
            return 1 if summary["rejected_or_failed_count"] > 0 else 0

        elif args.command == "validate":
            report = validate_production_manifest(args.production, repo_root)
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"=== Validation Report ({report['production_id']}) ===")
                print(f"Overall Status: {report['overall_status']}")
                print(
                    f"Total Assets: {report.get('total_assets', 0)} | "
                    f"PASS: {report.get('pass_count', 0)} | "
                    f"WARNING: {report.get('warning_count', 0)} | "
                    f"FAIL: {report.get('fail_count', 0)}"
                )
                for err in report.get("errors", []):
                    print(f"  MANIFEST ERROR: {err}")
                for ar in report.get("asset_results", []):
                    print(f"  - {ar['asset_id']}: {ar['validation_status']}")
                    for w in ar.get("warnings", []):
                        print(f"      WARNING: {w}")
                    for e in ar.get("errors", []):
                        print(f"      ERROR:   {e}")
            return 1 if report["overall_status"] == STATUS_FAIL else 0

        elif args.command == "list":
            assets = list_assets(args.production, repo_root)
            if args.json:
                print(json.dumps(assets, indent=2))
            else:
                print(f"=== Registered Reference Assets ({args.production}) [{len(assets)} total] ===")
                if not assets:
                    print("  (No reference assets registered)")
                for a in assets:
                    print(
                        f"  {a.get('asset_id')} | {a.get('asset_type'):5s} | "
                        f"{a.get('resolution'):10s} | Val={a.get('validation_status')} | "
                        f"App={a.get('approval_status')} | {a.get('managed_relative_path')} "
                        f"(orig: {a.get('original_filename')})"
                    )
            return 0

        elif args.command == "inspect":
            rec = inspect_asset(args.production, args.asset_id, repo_root)
            if rec is None:
                print(
                    f"ERROR: Asset '{args.asset_id}' not found in production '{args.production}'.",
                    file=sys.stderr,
                )
                return 1
            print(json.dumps(rec, indent=2))
            return 0

        elif args.command == "report":
            rep = generate_intake_report(args.production, repo_root)
            if args.json:
                print(json.dumps(rep, indent=2))
            else:
                print(f"=== Production Intake & Manifest Report ({rep['production_id']}) ===")
                print(f"Lifecycle State: {rep['lifecycle_state']}")
                print(f"Manifest Path:   {rep['manifest_path']}")
                counts = rep["asset_counts"]
                print(
                    f"Assets:          {counts['total_references']} total "
                    f"({counts['images']} images, {counts['videos']} videos)"
                )
                print(
                    f"Approval Status: {counts['pending_review']} PENDING_REVIEW, "
                    f"{counts['approved']} APPROVED, {counts['rejected']} REJECTED"
                )
                val = rep["validation_overview"]
                print(
                    f"Validation:      {val['overall_status']} "
                    f"(PASS={val['pass_count']}, WARNING={val['warning_count']}, FAIL={val['fail_count']})"
                )
                deps = rep["dependencies"]
                pil_str = (
                    f"AVAILABLE (v{deps['pillow']['version']})"
                    if deps["pillow"]["available"]
                    else "MISSING"
                )
                ffp_str = (
                    f"AVAILABLE ({deps['ffprobe']['executable_path']})"
                    if deps["ffprobe"]["available"]
                    else "UNAVAILABLE (using Python stdlib ISO-BMFF fallback)"
                )
                print(f"Dependencies:    Pillow={pil_str} | FFprobe={ffp_str}")
            return 0

    except IntakeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
