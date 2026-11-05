# Video Encoding, Motion & Delivery Standards

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `standards\video-standards.md`  
**Version:** 1.0.0

---

## 1. Purpose

This standard defines the video encoding specifications, temporal consistency rules, camera movement constraints, and visual realism criteria for generated video candidates (`generations\`) and final master deliverables (`deliverables\`).

Requirements are divided into **Hard Technical Requirements**, **Motion & Visual Realism Criteria**, **Creative Preferences**, and **Provisional Defaults**.

---

## 2. Final Deliverable (`deliverables\`) — Hard Technical Requirements

For pilot production **`YACHT-001`** (and as the baseline for standard HD productions unless overridden in the production brief), the final exported master must satisfy:

| Parameter | Hard Technical Requirement (`YACHT-001`) | Verification Method |
|---|---|---|
| **Container Format** | `MP4` (`.mp4`, MPEG-4 Part 14) with `moov` atom at front (`faststart`) | FFprobe container check |
| **Video Codec** | `H.264` / AVC (`libx264`, High Profile, Level 4.1 or 4.2) | FFprobe codec stream check |
| **Pixel Format / Chroma** | `yuv420p` (8-bit, 4:2:0) for universal playback compatibility | FFprobe `pix_fmt` check |
| **Colour Space** | `Rec.709` (`bt709` primaries, transfer, and matrix) | FFprobe colour metadata check |
| **Resolution** | `1920 × 1080` pixels | FFprobe width/height check |
| **Aspect Ratio** | `16:9` (`DAR 16:9`, `SAR 1:1` square pixels) | FFprobe aspect ratio check |
| **Frame Rate** | `24 fps` exact constant frame rate (`24/1` CFR) | FFprobe `r_frame_rate` / `avg_frame_rate` |
| **Total Duration** | `10.0 seconds` (`240 frames` exact at `24 fps`) | FFprobe duration & frame count check |
| **Audio Stream** | **None** (zero audio tracks present in container; silent stream not permitted when "None" is specified) | FFprobe audio stream count == `0` |
| **Titles, Burn-ins & Labels** | **None** (no text overlays, watermarks, timecodes, or lower thirds) | Full-duration visual review |
| **Encoding Quality** | Constant Rate Factor `CRF 16–18` or target bitrate `>= 20 Mbps` (visually lossless without macroblocking on water surfaces) | Bitrate & visual inspection |

---

## 3. Raw Video Candidates (`generations\`) — Technical Requirements

1. **Resolution & Aspect Ratio:** Candidates must be generated at `16:9` aspect ratio. If an external AI generator outputs a native resolution other than `1920 × 1080` (e.g., `1280 × 720` or `3840 × 2160`), the native resolution must be logged in `asset-manifest.json` and cleanly upscaled/downscaled during conform without aspect distortion.
2. **Frame Rate Conform:** Candidates generated at non-24fps native rates (e.g., `25 fps` or `30 fps`) must be conformed to `24 fps` CFR cleanly without frame-blending ghosts or cadence stutter.
3. **Duration Margin:** Each shot candidate must contain sufficient clean usable frames to cover its target cut duration (e.g., `>= 4.0s` (`96 frames`) for Shot 1; `>= 3.0s` (`72 frames`) for Shots 2 and 3).

---

## 4. Camera Movement & Visual Realism Criteria (Hard Pass/Fail)

Every approved video candidate and final cut must satisfy these physical and temporal realism constraints:

1. **Stabilized, Physically Plausible Camera Motion:**
   - Camera movements must emulate real stabilized marine cinema hardware (e.g., gyro-stabilized aerial gimbal, smooth dolly/slider on deck, or locked tripod).
   - **Prohibited:** Unnatural acceleration/deceleration snaps, floating/drunken horizon roll, Z-axis zoom warping, or impossible camera trajectories through solid structures.
2. **Temporal Stability (Zero Flicker / Zero Boil):**
   - Hull paint, teak planking seams, window mullions, railings, and interior textures must remain temporally locked across all frames.
   - **Prohibited:** High-frequency luminance/chrominance flicker, texture crawling ("boiling"), or periodic pulsing at keyframes.
3. **Realistic Marine Water & Wake Physics:**
   - Ocean swells, ripples, hull lap, and wake foam must move at natural real-time speeds consistent with gravity and vessel state (at anchor vs. underway).
   - **Prohibited:** Backwards-flowing waves, gelatinous/viscous water surfaces, static frozen water alongside moving wakes, or spontaneous splash eruptions.
4. **Consistent Reflections & Lighting:**
   - Specular sunlight reflections on water and hull/glass surfaces must track consistently with camera angle and wave geometry.
   - **Prohibited:** Detached shadow movement, sudden global illumination shifts across a single shot, or impossible reflections.

---

## 5. Creative Preferences (Non-Blocking Guidelines)

- **Pacing & Energy:** Slow, deliberate, poised camera motion (`5%–15%` motion intensity) almost always reads as more luxurious and photorealistic than rapid camera sweeps.
- **Cut Transitions:** Clean straight cuts (`hard cuts`) between shots are preferred over cross-dissolves or flashy transitions unless specified in the production brief.
- **Shot Progression:** Establish scale first (Exterior full/three-quarter profile), transition to lifestyle/architecture space (Deck), and conclude with intimate luxury detail (Interior salon/cabin).

---

## 6. Provisional Defaults (`YACHT-001` Pilot)

Per the `YACHT-001` specification, the following shot plan is **provisional** until reference intake analysis is completed:

| Shot ID | Category | Provisional Duration | Frame Count (`@ 24 fps`) | Provisional Camera Direction |
|---|---|---|---|---|
| **Shot 01 (`S01`)** | Exterior | `4.0 seconds` | `96 frames` | Slow, gyro-stabilized tracking or gentle push-in showcasing full yacht profile on calm water |
| **Shot 02 (`S02`)** | Deck | `3.0 seconds` | `72 frames` | Smooth linear slider motion across aft/main deck or sundeck seating with subtle water movement beyond |
| **Shot 03 (`S03`)** | Interior | `3.0 seconds` | `72 frames` | Slow, poised dolly push-in or subtle lateral glide inside main salon/cabin with natural window light |
| **Total** | **3 Shots** | **`10.0 seconds`** | **`240 frames`** | **Silent (`No Audio`), `1920×1080`, `H.264 MP4`** |
