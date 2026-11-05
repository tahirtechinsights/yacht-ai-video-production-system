"""Standalone Media Metadata Inspector Utility (YVP-SYS-002).

Extracts and prints technical metadata for an image or video file using
pipeline.intake.metadata without modifying the file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pipeline.intake.metadata import (  # noqa: E402
    check_dependencies,
    classify_extension,
    extract_image_metadata,
    extract_video_metadata,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect technical metadata of an image or video file.")
    parser.add_argument("file", nargs="?", type=Path, help="Path to image or video file to inspect.")
    parser.add_argument("--check-deps", action="store_true", help="Print local dependency status.")
    args = parser.parse_args()

    if args.check_deps:
        print(json.dumps(check_dependencies(), indent=2))
        return 0

    if args.file is None:
        parser.error("Provide a file path or --check-deps.")

    if not args.file.exists() or not args.file.is_file():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        return 1

    media_type, ext, mime_type = classify_extension(args.file)
    if media_type == "image":
        meta = extract_image_metadata(args.file)
    elif media_type == "video":
        meta = extract_video_metadata(args.file)
    else:
        print(f"ERROR: Unsupported media extension '{ext}'", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "file": str(args.file),
                "media_type": media_type,
                "extension": ext,
                "mime_type": mime_type,
                "technical_metadata": meta,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
