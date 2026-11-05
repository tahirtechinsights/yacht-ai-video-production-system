# Production Lifecycle & Approval Gates

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `governance\approval-gates.md`  
**Version:** 1.0.0

---

## 1. Lifecycle Governance Rule

Every yacht video production is governed by a nine-state deterministic lifecycle.

> **CRITICAL RULE:** Do not automatically advance a production state based solely on file existence. Advancing from one state to the next requires meeting all Exit Criteria, recording the Required Evidence in the repository, and receiving explicit sign-off from the designated Approval Authority.

---

## 2. State Definitions & Transition Criteria

### State 1: `DRAFT`
- **Purpose:** Initialize the production workspace, establish technical delivery specifications, and define provisional creative targets.
- **Entry Criteria:**
  - Human authorization to create a new production workspace (`productions\<PRODUCTION-ID>\`).
- **Exit Criteria (to transition to `REFERENCES_REGISTERED`):**
  - Production workspace directory tree is created.
  - Production brief (`brief\production-brief.md`) is populated with target resolution, frame rate, aspect ratio, duration, audio policy, and provisional shot structure.
  - Asset manifest (`assets\asset-manifest.json`) is initialized.
- **Required Evidence:**
  - Populated `productions\<PRODUCTION-ID>\brief\production-brief.md`.
  - Initialized `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.
- **Approval Authority:** Human Production Authority.

---

### State 2: `REFERENCES_REGISTERED`
- **Purpose:** Ingest, catalog, and lock original yacht reference photographs, videos, and layout specs.
- **Entry Criteria:**
  - Production is in `DRAFT` state with an approved production brief.
  - Original yacht reference files are placed in `productions\<PRODUCTION-ID>\references\`.
- **Exit Criteria (to transition to `SHOTS_PLANNED`):**
  - Every reference asset is assigned a unique Reference ID (`REF-001`, etc.) and logged in `assets\asset-manifest.json` with relative path, resolution/format metadata, and SHA-256 hash or file size/timestamp provenance.
  - Reference coverage is analyzed against exterior, deck, and interior requirements.
  - Vessel identity baseline notes (hull colour, deck configuration, glazing, key architectural features) are documented.
- **Required Evidence:**
  - Immutable reference files present in `productions\<PRODUCTION-ID>\references\`.
  - Complete `source_references` entries in `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.
- **Approval Authority:** Human Production Authority.

---

### State 3: `SHOTS_PLANNED`
- **Purpose:** Finalize the shot list, shot durations, camera movements, and reference-to-shot mappings based on verified reference coverage.
- **Entry Criteria:**
  - Production is in `REFERENCES_REGISTERED` state.
- **Exit Criteria (to transition to `IMAGES_APPROVED`):**
  - Provisional shot plan is updated to an authoritative shot list (`brief\shot-list.md`).
  - Each shot specifies exact duration (summing to total target duration, e.g., `4s + 3s + 3s = 10s` for `YACHT-001`), assigned Reference ID, framing, camera motion profile, and environmental motion notes.
- **Required Evidence:**
  - Completed `productions\<PRODUCTION-ID>\brief\shot-list.md`.
- **Approval Authority:** Human Production Authority.

---

### State 4: `IMAGES_APPROVED`
- **Purpose:** Prepare, enhance, crop/frame, and approve the exact keyframe start images that will drive Image-to-Video (I2V) generation.
- **Entry Criteria:**
  - Production is in `SHOTS_PLANNED` state.
- **Exit Criteria (to transition to `VIDEO_CANDIDATES_READY`):**
  - For each planned shot, a prepared keyframe image is placed in `productions\<PRODUCTION-ID>\assets\` meeting all hard technical requirements in [standards/image-standards.md](../standards/image-standards.md) (e.g., `16:9` aspect ratio, minimum `1920x1080`, sRGB/Rec.709, zero distortion).
  - If AI image enhancement was applied, prompt and parameter metadata are logged in `prompts\` and vessel identity preservation is verified against the parent reference ([standards/yacht-identity.md](../standards/yacht-identity.md)).
  - Prepared keyframe assets are marked `APPROVED` in `assets\asset-manifest.json`.
- **Required Evidence:**
  - Prepared image files in `productions\<PRODUCTION-ID>\assets\`.
  - Enhancement prompt records (if any) in `productions\<PRODUCTION-ID>\prompts\`.
  - Manifest status `APPROVED` for each shot's primary keyframe image.
- **Approval Authority:** Human Production Authority.

---

### State 5: `VIDEO_CANDIDATES_READY`
- **Purpose:** Generate I2V video candidates from approved keyframe images, log all generation parameters, and select winning candidates per shot.
- **Entry Criteria:**
  - Production is in `IMAGES_APPROVED` state.
- **Exit Criteria (to transition to `EDIT_READY`):**
  - Video candidates are generated externally using structured prompts from `productions\<PRODUCTION-ID>\prompts\` and saved in `productions\<PRODUCTION-ID>\generations\`.
  - Every candidate has a unique Candidate ID (`CAND-S01-001`, etc.), parent keyframe Asset ID, prompt version ID, model parameters, and review status recorded in `assets\asset-manifest.json`.
  - At least one candidate per shot passes pre-edit visual and vessel-identity screening and is marked `APPROVED` in the manifest, while rejected candidates are marked `REJECTED` with documented reasons.
- **Required Evidence:**
  - Prompt version logs in `productions\<PRODUCTION-ID>\prompts\`.
  - Video candidate files in `productions\<PRODUCTION-ID>\generations\`.
  - Updated `video_candidates` table in `productions\<PRODUCTION-ID>\assets\asset-manifest.json` showing one `APPROVED` candidate per shot.
- **Approval Authority:** Human Production Authority.

---

### State 6: `EDIT_READY`
- **Purpose:** Assemble the approved shot candidates into the master sequence matching exact timing, frame rate, and silent/audio rules.
- **Entry Criteria:**
  - Production is in `VIDEO_CANDIDATES_READY` state with an `APPROVED` video candidate for every shot in the shot list.
- **Exit Criteria (to transition to `QA_PASSED`):**
  - Approved shot candidates are conformed and edited into a continuous master sequence matching the production brief (e.g., `10.0s` exact duration, `24 fps`, `1920x1080`, `H.264 MP4`, no audio stream, no titles/labels).
  - Edit decision metadata or timeline notes are saved in `productions\<PRODUCTION-ID>\editing\`.
  - Candidate master export is generated for QA inspection.
- **Required Evidence:**
  - Edit project/conform record in `productions\<PRODUCTION-ID>\editing\`.
  - Release-candidate export logged in `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.
- **Approval Authority:** Human Production Authority.

---

### State 7: `QA_PASSED`
- **Purpose:** Execute technical and visual quality assurance on the assembled master sequence.
- **Entry Criteria:**
  - Production is in `EDIT_READY` state with a candidate master export available for inspection.
- **Exit Criteria (to transition to `FINAL_APPROVED`):**
  - Technical inspection verifies exact container, codec, resolution, aspect ratio, frame rate, frame count/duration, colour space, and audio absence ([standards/video-standards.md](../standards/video-standards.md)).
  - Visual realism and identity inspection verifies zero vessel morphing, zero flicker, natural water physics, consistent reflections, and clean shot cuts ([standards/quality-assurance.md](../standards/quality-assurance.md)).
  - Formal QA Report (`qa\qa-report.md`) is completed with overall status `PASS`.
- **Required Evidence:**
  - Signed-off `productions\<PRODUCTION-ID>\qa\qa-report.md` with technical inspection output and visual checklist results.
- **Approval Authority:** Technical QA Reviewer & Human Production Authority.

---

### State 8: `FINAL_APPROVED`
- **Purpose:** Grant executive release authorization for the QA-verified master video.
- **Entry Criteria:**
  - Production is in `QA_PASSED` state with zero unresolved QA defects.
- **Exit Criteria (to transition to `DELIVERED`):**
  - Human Production Authority reviews the final master video alongside `qa\qa-report.md` and `assets\asset-manifest.json`.
  - Final deliverable is promoted to `productions\<PRODUCTION-ID>\deliverables\` and marked `APPROVED` in the manifest with full end-to-end lineage recorded.
- **Required Evidence:**
  - Final master file in `productions\<PRODUCTION-ID>\deliverables\`.
  - Final approval entry recorded in `brief\production-brief.md`, `qa\qa-report.md`, and `CURRENT-STATE.md`.
- **Approval Authority:** Human Production Authority.

---

### State 9: `DELIVERED`
- **Purpose:** Conclude and archive the production in a clean, reproducible state.
- **Entry Criteria:**
  - Production is in `FINAL_APPROVED` state.
- **Exit Criteria (Terminal State):**
  - Final deliverable package and manifest lineage are verified intact.
  - `CURRENT-STATE.md` records the production as `DELIVERED` and closes active production tasks.
- **Required Evidence:**
  - Complete manifest lineage in `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.
  - Updated `CURRENT-STATE.md`.
- **Approval Authority:** Human Production Authority.

---

## 3. Gate Summary Matrix

| Transition | From State | To State | Key Required Evidence | Authority |
|---|---|---|---|---|
| **G1** | `DRAFT` | `REFERENCES_REGISTERED` | `references\*` + `asset-manifest.json` reference entries | Human Authority |
| **G2** | `REFERENCES_REGISTERED` | `SHOTS_PLANNED` | `brief\shot-list.md` mapped to Reference IDs | Human Authority |
| **G3** | `SHOTS_PLANNED` | `IMAGES_APPROVED` | Prepared keyframes in `assets\*` marked `APPROVED` | Human Authority |
| **G4** | `IMAGES_APPROVED` | `VIDEO_CANDIDATES_READY` | Prompt logs + `generations\*` + 1 `APPROVED` candidate/shot | Human Authority |
| **G5** | `VIDEO_CANDIDATES_READY` | `EDIT_READY` | Timeline/conform record in `editing\` + candidate export | Human Authority |
| **G6** | `EDIT_READY` | `QA_PASSED` | `qa\qa-report.md` with all Technical & Visual checks `PASS` | QA + Human Authority |
| **G7** | `QA_PASSED` | `FINAL_APPROVED` | Master in `deliverables\` + Executive sign-off | Human Authority |
| **G8** | `FINAL_APPROVED` | `DELIVERED` | Final manifest audit + `CURRENT-STATE.md` closure | Human Authority |
