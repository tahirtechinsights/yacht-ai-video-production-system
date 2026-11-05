# Image Technical Standards

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `standards\image-standards.md`  
**Version:** 1.0.0

---

## 1. Purpose

This standard defines the technical and visual requirements for source reference images (`references\`) and prepared/enhanced keyframe images (`assets\`) used as inputs to Image-to-Video (I2V) generation.

To maintain clarity across productions, requirements are explicitly separated into **Hard Technical Requirements**, **Creative Preferences**, and **Provisional Defaults**.

---

## 2. Prepared Keyframe Images (`assets\`) — Hard Technical Requirements

All prepared images submitted for `IMAGES_APPROVED` sign-off must satisfy every requirement below:

| Parameter | Hard Technical Requirement | Verification Method |
|---|---|---|
| **File Format** | Lossless PNG (`.png`) or uncompressed/lossless TIFF (`.tif`, `.tiff`) preferred; high-quality JPEG (`.jpg`, quality >= 95) permitted only if no lossless master exists | File extension & header check |
| **Bit Depth** | Minimum 8-bit per channel (24-bit RGB); 16-bit per channel supported for grading/preparation | Media metadata inspection |
| **Colour Space & Profile** | `sRGB` (IEC 61966-2-1) or `Rec.709` matching target video pipeline; embedded ICC profile must match pixel data | Metadata & visual colour check |
| **Target Resolution (`YACHT-001`)** | Minimum `1920 × 1080` pixels (`2560 × 1440` or `3840 × 2160` 16:9 masters permitted if downscaled cleanly) | Pixel dimension check |
| **Aspect Ratio (`YACHT-001`)** | Exact `16:9` (`1.7778:1`) with square pixels (`PAR 1:1`) | Width / Height ratio check |
| **Geometric Integrity** | Zero stretching, non-uniform scaling, perspective warping, or AI-induced structural hallucination | Side-by-side overlay/blink comparison against parent `REF-<NNN>` |
| **Artifact Floor** | No visible compression macroblocking, aliasing, halos, watermarks, text overlays, or framing borders | 100% zoom visual inspection |
| **Provenance Linkage** | Logged in `assets\asset-manifest.json` with valid parent `REF-<NNN>` ID and enhancement prompt ID (if enhanced) | Manifest audit |

---

## 3. Source Reference Images (`references\`) — Intake Requirements

1. **Immutability:** Source reference images are ingested exactly as supplied (`JPG`, `PNG`, `TIFF`, `RAW`, `WebP`) without re-compression.
2. **Minimum Usable Quality:** References selected as primary parents for keyframe preparation must have sufficient effective resolution and sharpness to clearly resolve hull lines, window mullions, railings, and surface materials without guesswork.
3. **Rejection of Unusable References:** Heavily motion-blurred, severely under/over-exposed, or low-resolution thumbnail images (< `1280` px on long edge) must not be used as primary I2V keyframes unless explicitly waived by the Human Production Authority.

---

## 4. Creative Preferences (Non-Blocking Guidelines)

The following attributes represent preferred aesthetic direction for luxury yacht imagery unless overridden by the production brief:

- **Lighting Conditions:** Natural golden hour, clean daylight, or balanced twilight illumination that highlights hull curvature and water reflections without blown-out specular highlights.
- **Horizon & Framing:** Perfectly level horizon line (`0.0°` roll); generous breathing room around the bow, stern, and masthead to accommodate subtle I2V camera motion without clipping the vessel.
- **Colour Rendition:** Neutral whites on superstructure gelcoat/paint, natural teak warmth, and authentic marine water hues (avoiding oversaturated cyan/teal filters).
- **Clean Decks:** Uncluttered deck surfaces free of distracting maintenance gear, fenders deployed while underway, or stray personal items (unless present in reference and required to remain untouched).

---

## 5. Provisional Defaults (`YACHT-001` Pilot)

Unless modified after reference intake analysis during `YVP-SYS-002`:

- **Keyframe Count:** 3 prepared keyframe images (`IMG-S01-v01` Exterior, `IMG-S02-v01` Deck, `IMG-S03-v01` Interior).
- **Standard Delivery Resolution:** `1920 × 1080` (`16:9`, `sRGB`, `.png`).
- **Enhancement Policy:** Prefer minimal deterministic framing/upscaling over generative diffusion wherever source resolution permits, to maximize vessel identity preservation.
