"""Technical Metadata Extraction for Managed Media Intake (YVP-SYS-002).

Extracts deterministic technical metadata for source images and reference videos:
- Images: Uses Pillow (PIL) when available (with stdlib header fallback) to extract
  width, height, format, colour_mode, colour_profile, orientation, file_size, and aspect_ratio.
- Videos: Uses FFprobe when available on PATH; when FFprobe is unavailable, explicitly reports
  the missing dependency (`ffprobe`) and uses a non-fabricating Python standard-library
  ISO-BMFF (MP4/MOV) binary atom inspector to extract real container headers where present.
"""

from __future__ import annotations

import json
import math
import mimetypes
import os
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}

SUPPORTED_VIDEO_EXTENSIONS = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/x-m4v",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".webm": "video/webm",
    ".mxf": "application/mxf",
}

EXIF_ORIENTATION_LABELS = {
    1: "Horizontal (normal)",
    2: "Mirror horizontal",
    3: "Rotate 180",
    4: "Mirror vertical",
    5: "Mirror horizontal and rotate 270 CW",
    6: "Rotate 90 CW",
    7: "Mirror horizontal and rotate 90 CW",
    8: "Rotate 270 CW",
}

CODEC_FOURCC_MAP = {
    "avc1": "H.264",
    "avc3": "H.264",
    "hvc1": "HEVC",
    "hev1": "HEVC",
    "mp4v": "MPEG-4 Part 2",
    "vp09": "VP9",
    "av01": "AV1",
    "apch": "Apple ProRes 422 HQ",
    "apcn": "Apple ProRes 422",
    "apcs": "Apple ProRes 422 LT",
    "apco": "Apple ProRes 422 Proxy",
    "ap4h": "Apple ProRes 4444",
}


def compute_aspect_ratio(width: Optional[int], height: Optional[int]) -> Optional[str]:
    """Compute canonical integer aspect ratio string (e.g. '16:9') from pixel dimensions."""
    if not width or not height or width <= 0 or height <= 0:
        return None
    divisor = math.gcd(int(width), int(height))
    rw = int(width) // divisor
    rh = int(height) // divisor
    # Handle common near-16:9 standard video sizes if needed, otherwise exact simplified ratio
    return f"{rw}:{rh}"


def classify_extension(file_path: Path) -> Tuple[Optional[str], str, Optional[str]]:
    """Return (media_type, lowercase_ext, mime_type) for a file path."""
    ext = file_path.suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        return "image", ext, SUPPORTED_IMAGE_EXTENSIONS[ext]
    if ext in SUPPORTED_VIDEO_EXTENSIONS:
        return "video", ext, SUPPORTED_VIDEO_EXTENSIONS[ext]
    guessed_mime, _ = mimetypes.guess_type(str(file_path))
    return None, ext, guessed_mime


def check_dependencies() -> Dict[str, Any]:
    """Check availability of local metadata extraction dependencies without installing anything."""
    pillow_available = False
    pillow_version: Optional[str] = None
    try:
        import PIL  # type: ignore

        pillow_available = True
        pillow_version = getattr(PIL, "__version__", "unknown")
    except ImportError:
        pillow_available = False

    ffprobe_path = shutil.which("ffprobe")
    return {
        "pillow": {
            "available": pillow_available,
            "version": pillow_version,
        },
        "ffprobe": {
            "available": ffprobe_path is not None,
            "executable_path": ffprobe_path,
        },
    }


def _extract_icc_profile_description(icc_bytes: bytes) -> str:
    """Attempt to read ICC profile description via PIL.ImageCms or fallback indicator."""
    try:
        import io
        from PIL import ImageCms  # type: ignore

        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
        desc = ImageCms.getProfileDescription(profile)
        if desc and desc.strip():
            return desc.strip()
    except Exception:
        pass
    return f"embedded_icc_profile ({len(icc_bytes)} bytes)"


def extract_image_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract technical metadata from an image file using Pillow (or report missing dependency)."""
    file_size = file_path.stat().st_size
    warnings: List[str] = []
    errors: List[str] = []
    missing_dependencies: List[str] = []

    try:
        from PIL import Image  # type: ignore
    except ImportError:
        missing_dependencies.append("Pillow")
        errors.append("Required image inspection library 'Pillow' (PIL) is not installed.")
        return {
            "width": None,
            "height": None,
            "format": None,
            "colour_mode": None,
            "colour_profile": None,
            "orientation": None,
            "file_size": file_size,
            "aspect_ratio": None,
            "extractor": "unavailable",
            "extraction_status": "FAILED_MISSING_DEPENDENCY",
            "missing_dependencies": missing_dependencies,
            "warnings": warnings,
            "errors": errors,
        }

    try:
        with Image.open(file_path) as img:
            width, height = img.size
            img_format = img.format
            colour_mode = img.mode

            # Extract colour profile information
            colour_profile: Optional[str] = None
            icc_bytes = img.info.get("icc_profile")
            if icc_bytes:
                colour_profile = _extract_icc_profile_description(icc_bytes)
            elif "srgb" in {k.lower() for k in img.info.keys()}:
                colour_profile = "sRGB"

            # Extract EXIF orientation & colour space if present
            orientation_info: Optional[Dict[str, Any]] = None
            try:
                exif = img.getexif()
                if exif:
                    # 0x0112 = Orientation
                    raw_orientation = exif.get(0x0112)
                    if raw_orientation is not None:
                        orientation_info = {
                            "code": int(raw_orientation),
                            "label": EXIF_ORIENTATION_LABELS.get(int(raw_orientation), "Unknown"),
                        }
                    # 0xA001 = ColorSpace (1 = sRGB, 65535 = Uncalibrated)
                    if colour_profile is None:
                        cs_tag = exif.get(0xA001)
                        if cs_tag == 1:
                            colour_profile = "sRGB (EXIF)"
                        elif cs_tag == 65535:
                            colour_profile = "Uncalibrated (EXIF)"
            except Exception as exif_exc:
                warnings.append(f"EXIF inspection warning: {exif_exc}")

            if colour_profile is None:
                colour_profile = "untagged"

            aspect_ratio = compute_aspect_ratio(width, height)

            return {
                "width": width,
                "height": height,
                "format": img_format,
                "colour_mode": colour_mode,
                "colour_profile": colour_profile,
                "orientation": orientation_info,
                "file_size": file_size,
                "aspect_ratio": aspect_ratio,
                "extractor": "Pillow",
                "extraction_status": "SUCCESS",
                "missing_dependencies": missing_dependencies,
                "warnings": warnings,
                "errors": errors,
            }
    except Exception as exc:
        errors.append(f"Image metadata extraction failed: {exc}")
        return {
            "width": None,
            "height": None,
            "format": None,
            "colour_mode": None,
            "colour_profile": None,
            "orientation": None,
            "file_size": file_size,
            "aspect_ratio": None,
            "extractor": "Pillow",
            "extraction_status": "FAILED",
            "missing_dependencies": missing_dependencies,
            "warnings": warnings,
            "errors": errors,
        }


# =============================================================================
# Pure-Python Standard Library ISO-BMFF (MP4 / MOV) Header Inspector
# Used when FFprobe is unavailable so real binary metadata is extracted
# without fabricating values or installing unauthorized packages.
# =============================================================================

def _iter_mp4_boxes(data: bytes, start: int = 0, end: Optional[int] = None):
    """Iterate (box_type, payload_start, box_end) across an ISO-BMFF byte slice."""
    if end is None:
        end = len(data)
    offset = start
    while offset + 8 <= end:
        size, box_type_bytes = struct.unpack(">I4s", data[offset : offset + 8])
        box_type = box_type_bytes.decode("latin1", errors="replace")
        header_size = 8
        if size == 1:
            if offset + 16 > end:
                break
            size = struct.unpack(">Q", data[offset + 8 : offset + 16])[0]
            header_size = 16
        elif size == 0:
            size = end - offset
        if size < header_size or offset + size > end:
            break
        yield box_type, offset + header_size, offset + size
        offset += size


def _parse_isobmff_metadata(file_path: Path) -> Dict[str, Any]:
    """Parse real container/stream metadata from MP4/MOV/M4V files using Python stdlib."""
    result: Dict[str, Any] = {
        "width": None,
        "height": None,
        "container_format": None,
        "video_codec": None,
        "frame_rate": None,
        "duration": None,
        "aspect_ratio": None,
        "audio_stream_present": None,
    }

    file_size = file_path.stat().st_size
    # Read up to 16 MB for header parsing (sufficient for standard MP4/MOV moov atoms)
    max_read = min(file_size, 16 * 1024 * 1024)
    with open(file_path, "rb") as f:
        data = f.read(max_read)

    if len(data) < 8:
        return result

    found_moov = False
    has_audio_track = False
    has_video_track = False

    for box_type, payload_start, box_end in _iter_mp4_boxes(data, 0, len(data)):
        if box_type == "ftyp" and (box_end - payload_start) >= 4:
            major_brand = data[payload_start : payload_start + 4].decode("latin1", errors="replace").strip()
            ext = file_path.suffix.lower()
            if major_brand == "qt" or ext == ".mov":
                result["container_format"] = "MOV"
            else:
                result["container_format"] = "MP4"

        elif box_type == "moov":
            found_moov = True
            for m_type, m_start, m_end in _iter_mp4_boxes(data, payload_start, box_end):
                if m_type == "mvhd" and (m_end - m_start) >= 20:
                    version = data[m_start]
                    if version == 0 and (m_end - m_start) >= 20:
                        timescale, duration_units = struct.unpack(">II", data[m_start + 12 : m_start + 20])
                        if timescale > 0:
                            result["duration"] = round(duration_units / timescale, 4)
                    elif version == 1 and (m_end - m_start) >= 32:
                        timescale, duration_units = struct.unpack(">IQ", data[m_start + 20 : m_start + 32])
                        if timescale > 0:
                            result["duration"] = round(duration_units / timescale, 4)

                elif m_type == "trak":
                    track_handler: Optional[str] = None
                    tkhd_w: Optional[int] = None
                    tkhd_h: Optional[int] = None
                    mdhd_timescale: Optional[int] = None
                    mdhd_duration: Optional[int] = None
                    stsd_codec: Optional[str] = None
                    stsd_w: Optional[int] = None
                    stsd_h: Optional[int] = None
                    total_samples: int = 0
                    total_sample_delta: int = 0

                    for t_type, t_start, t_end in _iter_mp4_boxes(data, m_start, m_end):
                        if t_type == "tkhd":
                            version = data[t_start]
                            # Width and height are 16.16 fixed-point at the end of tkhd
                            wh_offset = t_start + (88 if version == 1 else 76)
                            if wh_offset + 8 <= t_end:
                                w_fixed, h_fixed = struct.unpack(">II", data[wh_offset : wh_offset + 8])
                                if (w_fixed >> 16) > 0 and (h_fixed >> 16) > 0:
                                    tkhd_w = w_fixed >> 16
                                    tkhd_h = h_fixed >> 16

                        elif t_type == "mdia":
                            for md_type, md_start, md_end in _iter_mp4_boxes(data, t_start, t_end):
                                if md_type == "mdhd":
                                    version = data[md_start]
                                    if version == 0 and (md_end - md_start) >= 20:
                                        mdhd_timescale, mdhd_duration = struct.unpack(
                                            ">II", data[md_start + 12 : md_start + 20]
                                        )
                                    elif version == 1 and (md_end - md_start) >= 32:
                                        mdhd_timescale, mdhd_duration = struct.unpack(
                                            ">IQ", data[md_start + 20 : md_start + 32]
                                        )
                                elif md_type == "hdlr" and (md_end - md_start) >= 12:
                                    track_handler = data[md_start + 8 : md_start + 12].decode(
                                        "latin1", errors="replace"
                                    )
                                elif md_type == "minf":
                                    for mi_type, mi_start, mi_end in _iter_mp4_boxes(data, md_start, md_end):
                                        if mi_type == "stbl":
                                            for st_type, st_start, st_end in _iter_mp4_boxes(data, mi_start, mi_end):
                                                if st_type == "stsd" and (st_end - st_start) >= 16:
                                                    entry_size, fourcc_bytes = struct.unpack(
                                                        ">I4s", data[st_start + 8 : st_start + 16]
                                                    )
                                                    fourcc = fourcc_bytes.decode("latin1", errors="replace").strip()
                                                    stsd_codec = CODEC_FOURCC_MAP.get(fourcc, fourcc)
                                                    # Visual sample entry width/height at entry_start + 32..36
                                                    if st_start + 8 + 36 <= st_end:
                                                        vw, vh = struct.unpack(
                                                            ">HH", data[st_start + 8 + 32 : st_start + 8 + 36]
                                                        )
                                                        if vw > 0 and vh > 0:
                                                            stsd_w, stsd_h = vw, vh
                                                elif st_type == "stts" and (st_end - st_start) >= 8:
                                                    entry_count = struct.unpack(">I", data[st_start + 4 : st_start + 8])[0]
                                                    pos = st_start + 8
                                                    for _ in range(entry_count):
                                                        if pos + 8 > st_end:
                                                            break
                                                        s_count, s_delta = struct.unpack(">II", data[pos : pos + 8])
                                                        total_samples += s_count
                                                        total_sample_delta += s_count * s_delta
                                                        pos += 8

                    if track_handler == "soun":
                        has_audio_track = True
                    elif track_handler == "vide":
                        has_video_track = True
                        result["width"] = stsd_w or tkhd_w
                        result["height"] = stsd_h or tkhd_h
                        result["video_codec"] = stsd_codec
                        if mdhd_timescale and mdhd_timescale > 0:
                            if total_samples > 0 and total_sample_delta > 0:
                                fps = (total_samples * mdhd_timescale) / total_sample_delta
                                result["frame_rate"] = round(fps, 3)
                            elif mdhd_duration and mdhd_duration > 0 and result["duration"] is None:
                                result["duration"] = round(mdhd_duration / mdhd_timescale, 4)

    if found_moov and has_video_track:
        result["audio_stream_present"] = has_audio_track
    result["aspect_ratio"] = compute_aspect_ratio(result["width"], result["height"])
    return result


def extract_video_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract technical metadata from a video file using FFprobe or stdlib ISO-BMFF fallback."""
    file_size = file_path.stat().st_size
    warnings: List[str] = []
    errors: List[str] = []
    missing_dependencies: List[str] = []

    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        try:
            cmd = [
                ffprobe_bin,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(file_path),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            probe_data = json.loads(proc.stdout)
            streams = probe_data.get("streams", [])
            fmt_info = probe_data.get("format", {})

            video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

            width = int(video_stream["width"]) if video_stream and "width" in video_stream else None
            height = int(video_stream["height"]) if video_stream and "height" in video_stream else None
            codec_name = video_stream.get("codec_name") if video_stream else None
            if codec_name == "h264":
                codec_name = "H.264"
            elif codec_name == "hevc":
                codec_name = "HEVC"

            fps: Optional[float] = None
            if video_stream and video_stream.get("avg_frame_rate"):
                num_den = video_stream["avg_frame_rate"].split("/")
                if len(num_den) == 2 and float(num_den[1]) > 0:
                    fps = round(float(num_den[0]) / float(num_den[1]), 3)

            duration_str = (video_stream or {}).get("duration") or fmt_info.get("duration")
            duration = round(float(duration_str), 4) if duration_str is not None else None

            ext = file_path.suffix.lower().lstrip(".").upper()
            return {
                "width": width,
                "height": height,
                "container_format": ext or fmt_info.get("format_name"),
                "video_codec": codec_name,
                "frame_rate": fps,
                "duration": duration,
                "aspect_ratio": compute_aspect_ratio(width, height),
                "audio_stream_present": len(audio_streams) > 0,
                "file_size": file_size,
                "extractor": "ffprobe",
                "extraction_status": "SUCCESS",
                "missing_dependencies": missing_dependencies,
                "warnings": warnings,
                "errors": errors,
            }
        except Exception as exc:
            errors.append(f"FFprobe execution failed: {exc}")

    # FFprobe is unavailable — record missing dependency explicitly and attempt stdlib ISO-BMFF inspection
    missing_dependencies.append("ffprobe")
    warnings.append(
        "Optional video utility 'ffprobe' is not installed or not on PATH. "
        "Used Python standard-library ISO-BMFF parser; install FFmpeg/FFprobe when authorized for full stream probing."
    )

    ext = file_path.suffix.lower()
    if ext in {".mp4", ".mov", ".m4v"}:
        try:
            parsed = _parse_isobmff_metadata(file_path)
            core_keys = [
                "width",
                "height",
                "container_format",
                "video_codec",
                "frame_rate",
                "duration",
                "aspect_ratio",
                "audio_stream_present",
            ]
            extracted_count = sum(1 for k in core_keys if parsed.get(k) is not None)
            if extracted_count == len(core_keys):
                status = "SUCCESS_STDLIB_FALLBACK"
            elif extracted_count > 0:
                status = "PARTIAL_NO_FFPROBE"
                missing_fields = [k for k in core_keys if parsed.get(k) is None]
                warnings.append(f"Fields requiring ffprobe could not be extracted: {', '.join(missing_fields)}")
            else:
                status = "FAILED_NO_FFPROBE"
                errors.append("Could not parse ISO-BMFF moov/trak headers and ffprobe is unavailable.")

            return {
                **parsed,
                "file_size": file_size,
                "extractor": "python_stdlib_isobmff",
                "extraction_status": status,
                "missing_dependencies": missing_dependencies,
                "warnings": warnings,
                "errors": errors,
            }
        except Exception as exc:
            errors.append(f"Stdlib ISO-BMFF parsing error: {exc}")

    else:
        errors.append(
            f"Video container '{ext}' requires 'ffprobe' for stream metadata extraction, and 'ffprobe' is unavailable."
        )

    return {
        "width": None,
        "height": None,
        "container_format": ext.lstrip(".").upper() if ext else None,
        "video_codec": None,
        "frame_rate": None,
        "duration": None,
        "aspect_ratio": None,
        "audio_stream_present": None,
        "file_size": file_size,
        "extractor": "unavailable (ffprobe missing)",
        "extraction_status": "FAILED_MISSING_DEPENDENCY",
        "missing_dependencies": missing_dependencies,
        "warnings": warnings,
        "errors": errors,
    }
