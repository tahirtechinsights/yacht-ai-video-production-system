# Quality Assurance (QA) Standard & Acceptance Criteria

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `standards\quality-assurance.md`  
**Version:** 1.0.0

---

## 1. Purpose

This document establishes the mandatory Quality Assurance (QA) inspection framework for evaluating prepared images (`IMAGES_APPROVED` gate), generated video candidates (`VIDEO_CANDIDATES_READY` gate), and assembled master exports (`QA_PASSED` gate).

A production may only advance to `QA_PASSED` when **every Hard Acceptance Criterion** is verified as `PASS` and recorded in `productions\<PRODUCTION-ID>\qa\qa-report.md`.

---

## 2. QA Rating Definitions

Every inspection item in a QA Report must be recorded using one of three explicit states:

- **`PASS`**: The asset or master sequence has been inspected and meets the exact specification with supporting evidence (tool output or frame-by-frame review).
- **`FAIL`**: The asset or master sequence violates one or more hard requirements. Any single `FAIL` blocks gate advancement until remediated.
- **`NOT TESTED`**: The check has not yet been executed. **Rule:** Never report an unexecuted validation as `PASS`. A production cannot pass QA while any required check remains `NOT TESTED`.

---

## 3. Hard Technical Acceptance Criteria (Master Deliverable)

Verified via automated media inspection (`FFprobe` / PowerShell validation tools) against the production brief:

| Check ID | Inspection Item | `YACHT-001` Pass Requirement | Rejection Condition (`FAIL`) |
|---|---|---|---|
| **TECH-01** | File Container | `.mp4` (`MPEG-4 Part 14`) | Any other container (`.mov`, `.mkv`, `.avi`, `.webm`) |
| **TECH-02** | Video Codec | `H.264` (`avc1` / `libx264`) | `H.265/HEVC`, `ProRes`, `VP9`, `AV1`, or corrupt bitstream |
| **TECH-03** | Resolution | Exact `1920 × 1080` | Any deviation in pixel width or height |
| **TECH-04** | Aspect Ratio | Exact `16:9` (`SAR 1:1`, `DAR 16:9`) | Letterboxing bars baked into frame, pillar-boxing, or non-square pixels |
| **TECH-05** | Frame Rate | Exact `24.00 fps` (`24/1` CFR) | Variable Frame Rate (VFR), `23.976`, `25`, `29.97`, `30`, or `60 fps` |
| **TECH-06** | Total Duration | Exact `10.00 seconds` (`240 frames`) | Frame count != `240` frames (`±0` frames tolerance on final master) |
| **TECH-07** | Shot Split Timing | Matches approved `brief\shot-list.md` (provisional `4s + 3s + 3s`) | Unapproved shot timing deviation or missing shot |
| **TECH-08** | Audio Stream | Zero audio tracks (`0` audio streams) | Presence of any audio stream (even if silent/muted) |
| **TECH-09** | Titles & Overlays | Zero titles, labels, watermarks, or burn-ins | Any visible text, AI platform watermark, or graphic overlay |
| **TECH-10** | Provenance Lineage | Complete trace in `assets\asset-manifest.json` | Missing parent candidate ID, keyframe ID, prompt ID, or reference ID |

---

## 4. Hard Visual & Identity Acceptance Criteria (Frame-by-Frame Review)

Verified via full-screen real-time playback (`24 fps`) **and** frame-by-frame scrubbing across every frame (`001` to `240`):

| Check ID | Inspection Domain | Pass Requirement (`PASS`) | Mandatory Rejection Triggers (`FAIL`) |
|---|---|---|---|
| **VIS-01** | **Yacht Structural Identity** | Hull, superstructure, deck tiers, radar arch, and silhouette match `REF-<NNN>` 100% | Hull stretching, bow deformation, added/missing decks, altered silhouette |
| **VIS-02** | **Windows & Glazing** | Window counts, shapes, mullions, and tint remain rigid and identical to reference | Bending mullions, multiplying/vanishing portlights, morphing windscreen frames |
| **VIS-03** | **Livery, Colour & Materials** | Paint colour, boot-top stripe, teak seams, and interior joinery/stone remain true to reference | Hue shifts across shot, disappearing stripes, teak planks swimming/crawling |
| **VIS-04** | **Fine Hardware & Railings** | Stainless stanchions, handrails, cleats, antennas, and furniture stay solid | Melting railings, ghostly vanishing stanchions, wobbling rigid structures |
| **VIS-05** | **Camera Motion Realism** | Smooth, stabilized, single-vector cinematic movement consistent with real gimbal/slider hardware | Jerky velocity spikes, horizon roll/tilt drift, warping zoom, floating wobble |
| **VIS-06** | **Temporal Stability** | Clean temporal coherence from first frame to last frame of each cut | Luminance flicker, keyframe pulsing, high-frequency texture boiling, edge halo shimmer |
| **VIS-07** | **Water & Environmental Physics** | Natural wave propagation, realistic hull water lap, physically plausible wake/reflections | Backwards waves, frozen/gelatinous water, spontaneous splash artifacts, sliding reflections |
| **VIS-08** | **Cut Transitions & Boundaries** | Clean first and last frames on every shot cut; no dead/frozen start frames or tail decay | AI morphing decay in final 0.5s of a shot, duplicate freeze-frames at cut points |

---

## 5. Creative Preferences & Advisory Checks (Non-Blocking)

Reviewers may log advisory notes on the following aesthetic criteria without triggering an automatic technical `FAIL`, provided the Human Production Authority approves the creative look:

- **ADVISORY-01 (Exposure & Contrast Consistency):** Shot-to-shot brightness and colour warmth flow cohesively across Exterior -> Deck -> Interior cuts.
- **ADVISORY-02 (Pacing Harmony):** Camera movement speed feels matched across the three cuts so no cut feels abruptly faster or slower than adjacent cuts.
- **ADVISORY-03 (Compositional Balance):** Key architectural focal points remain comfortably within the Rule-of-Thirds / title-safe zones throughout the move.

---

## 6. Defect Handling & Rejection Workflow

When any candidate or master fails a `TECH-*` or `VIS-*` check:
1. Mark the specific check `FAIL` in `qa\qa-report.md` (or candidate review log) with the exact frame range (e.g., `Frames 068–096: Starboard bow rail morphing`).
2. Mark the offending candidate `REJECTED` in `assets\asset-manifest.json`.
3. Determine root cause:
   - **Encoding/Conform Defect (`TECH-*`):** Re-export from `editing\` with corrected FFmpeg/NLE settings.
   - **Tail-Frame Decay (`VIS-08`):** Trim the candidate to its clean frame window if sufficient duration remains, or select/generate an alternate candidate.
   - **Identity or Motion Defect (`VIS-01` to `VIS-07`):** Adjust prompt constraints/motion amplitude in `prompts\` and select or generate a new candidate (`CAND-S<SS>-<NNN+1>`).
