# Image-to-Video (I2V) Prompt Engineering Guide

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `prompts\image-to-video\image-to-video-guide.md`  
**Version:** 1.0.0

---

## 1. Purpose

This document provides the modular, provider-agnostic prompt engineering patterns for driving Image-to-Video (I2V) generation from approved keyframes (`IMG-S<SS>-v<VV>`).

All I2V prompts strictly separate:
1. **Preservation Constraints** (Source-Image Fidelity & Yacht Identity Lock)
2. **Creative Direction** (Cinematic Composition, Camera Motion, & Natural Environmental Movement)
3. **Negative Constraints** (Referenced from `..\negative-constraints\negative-constraints-library.md`)
4. **Technical Generation Settings & Parameter Records**

---

## 2. Core Prompt Modules

### Module 1: Source-Image Fidelity & Yacht Identity Constraints (Mandatory Prefix/Anchor)
Include this preservation intent in every I2V prompt record:
```text
Strict first-frame fidelity to the input reference photograph. The yacht's hull geometry, sheer line, superstructure decks, window mullions, railings, radar arch, paint colour, teak deck layout, and architectural materials remain completely rigid, invariant, and locked throughout the clip.
```

### Module 2: Cinematic Composition & Camera Motion Archetypes

Select **one** primary, low-amplitude camera motion vector per shot. Avoid combining multi-axis compound camera moves (e.g., simultaneous orbit + zoom + tilt), which frequently induce parallax hallucination on yacht structures.

| Shot Archetype | Recommended Camera Motion | Reusable Camera Motion Prompt Phrase |
|---|---|---|
| **Exterior (`S01` - 4s)** | Slow gyro-stabilized lateral tracking OR gentle dolly push-in | `Slow, ultra-smooth gyro-stabilized aerial cinema camera tracking gently parallel to the yacht, maintaining a perfectly level horizon and constant framing distance.` |
| **Deck (`S02` - 3s)** | Smooth linear slider glide OR slow forward dolly | `Subtle, poised motorized slider movement gliding slowly forward along the deck axis, tripod-grade stability, locked perspective lines, no lens distortion.` |
| **Interior (`S03` - 3s)** | Slow architectural dolly push-in OR subtle lateral slide | `Very slow, stabilized architectural cinema dolly push-in through the salon interior, perfectly level horizontal and vertical lines, smooth constant velocity.` |

### Module 3: Natural Environmental Movement

Keep environmental motion subtle, physically grounded, and appropriate to the shot context:

- **Exterior Marine Environment:**
  ```text
  Natural, calm ocean surface with gentle, physically accurate ripples and subtle sunlight specular reflections shimmering softly on the water and hull. Real-time marine water physics, calm ambient sea breeze.
  ```
- **Deck Environment:**
  ```text
  Gentle, realistic water ripples visible beyond the bulwarks and soft natural daylight reflections shifting subtly across polished stainless steel and glass surfaces. Furniture and deck hardware remain completely stationary.
  ```
- **Interior Environment:**
  ```text
  Soft, natural sunlit water caustics and gentle ambient light reflections entering calmly through the yacht windows. Interior walls, cabinetry, furniture, and lighting fixtures remain completely static and rigid.
  ```

---

## 3. Complete Assembled Shot Templates (`YACHT-001` Provisional Archetypes)

### 3.1 Shot 01 — Exterior (`4.0s` Provisional)
- **Preservation Constraints:**
  `Maintain exact yacht identity, hull profile, window alignment, superstructure tiers, railings, and exterior livery from the source keyframe with zero geometric deformation.`
- **Creative Direction (Composition, Camera & Environment):**
  `Premium photorealistic marine cinematography. Slow, ultra-smooth gyro-stabilized camera movement gently pushing in toward the yacht on a perfectly level horizon. Calm, natural sea ripples and soft sunlight reflections moving realistically across the water surface around the hull.`
- **Negative Constraints Module:** `NEG-GLOBAL-01` + `NEG-EXT-01` (see [`..\negative-constraints\negative-constraints-library.md`](../negative-constraints/negative-constraints-library.md)).

### 3.2 Shot 02 — Deck (`3.0s` Provisional)
- **Preservation Constraints:**
  `Preserve exact teak deck planking, seating geometry, table layout, stainless steel railings, and superstructure architecture from the input keyframe without morphing.`
- **Creative Direction (Composition, Camera & Environment):**
  `Premium photorealistic luxury yacht cinematography. Smooth, slow cinema slider movement gliding gently across the deck space. Subtle, natural ocean movement visible in the background and soft daylight reflections on glass and polished metal fittings.`
- **Negative Constraints Module:** `NEG-GLOBAL-01` + `NEG-DECK-01`.

### 3.3 Shot 03 — Interior (`3.0s` Provisional)
- **Preservation Constraints:**
  `Preserve exact interior cabin/salon architecture, wood joinery grain, stone surfaces, furniture geometry, window frames, and ceiling light fixtures from the source keyframe.`
- **Creative Direction (Composition, Camera & Environment):**
  `Premium photorealistic architectural interior cinematography. Very slow, poised dolly push-in with locked vertical lines, accompanied by subtle, natural daylight and gentle water reflection shimmer visible through the exterior windows.`
- **Negative Constraints Module:** `NEG-GLOBAL-01` + `NEG-INT-01`.

---

## 4. Model-Specific Parameter Record Specification

Every I2V prompt executed for a production must log its technical generation settings in `productions\<PROD-ID>\prompts\PRM-S<SS>-v<VV>.md` using the following provider-neutral schema:

| Parameter Field | Required Documentation |
|---|---|
| **Prompt Record ID** | `PRM-S<SS>-v<VV>` (e.g., `PRM-S01-v01`) |
| **Target Shot ID** | `S01` / `S02` / `S03` |
| **Source Keyframe Asset ID** | `IMG-S<SS>-v<VV>` |
| **External Provider / Model** | `<Provider Name, Model Family, & Exact Version>` |
| **Generation Mode** | `Image-to-Video (First-Frame Anchored)` |
| **Native Output Resolution** | e.g., `1920 × 1080` (`16:9`) |
| **Native Output Frame Rate** | e.g., `24 fps` |
| **Requested Clip Duration** | e.g., `4.0s` or `5.0s` (with clean trim target `4.0s` / `3.0s`) |
| **Motion Amplitude / Scale** | Low / Conservative (e.g., `2–4` on a `1–10` scale, or equivalent motion bucket) |
| **Camera Control Parameters** | Pan / Tilt / Zoom / Dolly numeric values if supported by model |
| **Guidance / CFG / Fidelity Scale** | High source adherence setting |
| **Random Seed** | Exact integer seed used for each candidate (`CAND-S<SS>-<NNN>`) |

---

## 5. Prompt Version History Tracking

Every shot prompt file must include a cumulative version history table linking prompt iterations to generated candidates and their QA outcomes:

| Prompt Version | Date | Candidate IDs Generated | Parameter / Wording Adjustment | Outcome (`APPROVED` / `REJECTED` + Reason) |
|---|---|---|---|---|
| `v01` | `YYYY-MM-DD` | `CAND-S01-001` | Baseline low-motion exterior tracking prompt | `<Record actual result during execution>` |
