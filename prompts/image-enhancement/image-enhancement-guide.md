# Image Enhancement & Keyframe Preparation Prompt Guide

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `prompts\image-enhancement\image-enhancement-guide.md`  
**Version:** 1.0.0

---

## 1. Purpose & Core Rule

Image enhancement prepares a registered reference image (`REF-<NNN>`) into an approved `16:9` keyframe (`IMG-S<SS>-v<VV>`) meeting [standards/image-standards.md](../../standards/image-standards.md).

> **GOLDEN RULE OF IMAGE ENHANCEMENT:**  
> Prefer deterministic optical processing (lossless crop, aspect framing, exposure balance) or ultra-low-denoise fidelity upscaling (`denoise <= 0.15`) over generative re-synthesis. Never allow an image enhancer to alter the yacht's hull lines, window layouts, railings, or materials.

---

## 2. Separation of Prompt Layers

When an AI upscaler, detail restorer, or environmental edge-extender (outpainter for `16:9` aspect framing) is used, structure the prompt record into the following separated blocks:

### Layer A: Source-Image Fidelity & Yacht Identity Constraints
```text
Strict fidelity to source reference photograph. Preserve exact yacht naval architecture, hull geometry, sheer line, superstructure proportions, window count and mullion geometry, stainless steel railings, radar arch, paint colour, teak deck planking, and interior joinery without modification or hallucination. Zero structural drift.
```

### Layer B: Image Enhancement & Cinematic Composition Direction
- **For Super-Resolution / Detail Restoration:**
  ```text
  High-resolution optical photograph restoration, crisp architectural edges, clean marine surface textures, natural daylight specular reflections on water and gelcoat, balanced dynamic range, zero compression artifacts, 35mm full-frame prime lens optical clarity.
  ```
- **For 16:9 Environmental Canvas Extension (Outpainting Sky/Water Margin Only):**
  ```text
  Seamless horizontal extension of surrounding natural marine environment and sky only. Match exact horizon line level, sea state ripple scale, water colour, and ambient lighting direction of the original frame. Do not extend, alter, or touch the yacht structure itself.
  ```

### Layer C: Negative Constraints (Enhancement)
Refer to [`..\negative-constraints\negative-constraints-library.md`](../negative-constraints/negative-constraints-library.md) (`NEG-ENH-01`):
```text
altered hull geometry, modified windows, extra deck tiers, warped railings, bent mullions, changed paint colour, artificial CGI look, plastic textures, oversharpening halos, painterly brushstrokes, text watermarks, asymmetrical distortion.
```

### Layer D: Technical Generation Settings & Parameter Record Template

Record the exact provider-neutral settings in `productions\<PROD-ID>\prompts\PRM-ENH-S<SS>-v<VV>.md`:

| Parameter Field | Description / Example Value |
|---|---|
| **Prompt Record ID** | `PRM-ENH-S01-v01` |
| **Source Reference ID** | `REF-001` |
| **Output Asset ID** | `IMG-S01-v01` |
| **Operation Type** | `Deterministic Crop` / `Fidelity Upscale` / `Margin Outpaint` |
| **External Tool / Model** | `<Provider / Model Name & Version>` |
| **Target Resolution** | `1920 × 1080` (`16:9`, `PAR 1:1`, `sRGB`) |
| **Denoise / Creativity Strength** | `<= 0.10 – 0.15` (Strict structure lock) |
| **Structure / Control Lock** | `Enabled` (Canny / Depth / Tile Control if applicable) |
| **Seed** | `<Numeric Seed or N/A>` |

---

## 3. Prompt Version History Format

Every enhancement prompt log must maintain a version history table:

| Version | Date | Author | Changes Made | Identity Check Result |
|---|---|---|---|---|
| `v01` | `YYYY-MM-DD` | `<Operator>` | Initial enhancement configuration | `NOT TESTED` / `PASS` / `FAIL` |
