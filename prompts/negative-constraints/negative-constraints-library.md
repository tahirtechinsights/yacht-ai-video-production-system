# Negative Constraints Library

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `prompts\negative-constraints\negative-constraints-library.md`  
**Version:** 1.0.0

---

## 1. Purpose

This library provides standardized, reusable negative constraint modules for external AI image enhancement and Image-to-Video (I2V) models.

For models that expose a dedicated `Negative Prompt` field, copy the applicable modules directly into that field. For models that accept only a single unified prompt, append the negative constraints as explicit `Avoid:` / `Do not include:` clauses at the end of the prompt.

---

## 2. Core Negative Constraint Modules

### `NEG-GLOBAL-01`: Universal Yacht Identity & Temporal Stability (Mandatory on All Shots)
```text
morphing, geometry distortion, warping hull, bending lines, melting railings, shifting window mullions, disappearing features, structural hallucination, temporal flicker, luminance pulsing, texture boiling, jitter, camera shake, horizon roll, fisheye distortion, lens warping, artificial motion, fast chaotic motion, CGI cartoon look, oversaturated colours, text, titles, labels, subtitles, watermarks, logos, timestamps, frame borders, blurry, low resolution, compression macroblocking
```

### `NEG-EXT-01`: Exterior & Marine Water Physics Constraints
```text
unrealistic water movement, backwards waves, frozen water, gelatinous sea, sudden violent splashes, impossible wake, detached water reflections, hull stretching, telescopic bow deformation, extra deck tiers, duplicated radar domes, mutating antennas, floating objects in water, people appearing out of nowhere
```

### `NEG-DECK-01`: Deck & Exterior Architecture Constraints
```text
swimming teak planks, shifting deck seams, warping handrails, melting stainless steel stanchions, deforming cushions, moving tables, sliding chairs, inconsistent glass reflections, phantom people walking, unnatural cloth flapping
```

### `NEG-INT-01`: Interior Architecture & Cabin Constraints
```text
bending walls, shifting cabinetry, crawling wood grain, morphing marble veins, flickering ceiling lights, changing colour temperature, moving furniture, warping door frames, impossible window views, floating decor items
```

### `NEG-ENH-01`: Image Enhancement & Keyframe Preparation Constraints
```text
altered vessel identity, modified window shapes, changed hull paint colour, redrawn superstructure, invented deck equipment, plastic skin/surface smoothing, oversharpening halos, ringing artifacts, painterly brushwork, AI text gibberish
```

---

## 3. Usage in Production Prompt Logs

When documenting a shot prompt in `productions\<PROD-ID>\prompts\PRM-S<SS>-v<VV>.md`:
1. Reference the module IDs applied (e.g., `NEG-GLOBAL-01 + NEG-EXT-01`).
2. Record the exact verbatim string passed to the external generator so any future re-run is 100% reproducible.
3. If a rejected candidate exhibits a specific defect (e.g., `CAND-S01-001` showed subtle radar arch shimmer), add a targeted negative term in `PRM-S01-v02` and document the addition in the Prompt Version History table.
