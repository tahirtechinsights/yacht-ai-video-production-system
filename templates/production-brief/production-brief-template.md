# Production Brief Template

**Template ID:** `TPL-PRODUCTION-BRIEF`  
**Template Version:** `1.0.0`  
**Purpose:** Define the authoritative scope, technical delivery targets, vessel identity constraints, and lifecycle status for a single yacht video production. Copy to `productions\<PRODUCTION-ID>\brief\production-brief.md`.

---

## 1. Production Identification

| Field | Value |
|---|---|
| **Production ID** | `<e.g., YACHT-001>` |
| **Vessel Name / Designation** | `<TBD upon reference intake>` |
| **Current Lifecycle State** | `DRAFT` |
| **Created Date** | `<YYYY-MM-DD>` |
| **Human Production Authority** | `<Name / Role>` |

---

## 2. Hard Technical Delivery Specifications

| Parameter | Requirement |
|---|---|
| **Total Duration** | `<e.g., 10 seconds>` |
| **Audio Policy** | `<e.g., None (0 audio streams)>` |
| **Aspect Ratio** | `<e.g., 16:9>` |
| **Target Resolution** | `<e.g., 1920 × 1080>` |
| **Frame Rate** | `<e.g., 24 fps (CFR)>` |
| **Final Container** | `<e.g., MP4>` |
| **Video Codec** | `<e.g., H.264>` |
| **Titles and Labels** | `<e.g., None>` |

---

## 3. Creative & Visual Direction

| Parameter | Requirement |
|---|---|
| **Visual Style** | `<e.g., Premium cinematic realism>` |
| **Provisional Shot Plan** | `<e.g., Exterior, deck, interior>` |
| **Provisional Shot Durations** | `<e.g., 4s + 3s + 3s>` |
| **Shot Plan Status** | `PROVISIONAL` (Subject to reference intake analysis) |

---

## 4. Vessel Identity & Realism Mandate

- **Identity Preservation:** Preserve exact yacht identity, hull geometry, colour/livery, deck layout, superstructure architecture, windows/mullions, materials, and key features from registered reference assets (`references\REF-*`).
- **Prohibited Artifacts:** Avoid artificial motion, temporal flicker, structural morphing, geometry distortion, inconsistent reflections, and unrealistic water movement.

---

## 5. Lifecycle Gate Sign-Off Log

| Lifecycle State | Status (`PENDING` / `APPROVED`) | Evidence Reference | Approved By | Date |
|---|---|---|---|---|
| `1. DRAFT` | `PENDING` | `brief\production-brief.md` | — | — |
| `2. REFERENCES_REGISTERED` | `PENDING` | `assets\asset-manifest.json` | — | — |
| `3. SHOTS_PLANNED` | `PENDING` | `brief\shot-list.md` | — | — |
| `4. IMAGES_APPROVED` | `PENDING` | `assets\asset-manifest.json` | — | — |
| `5. VIDEO_CANDIDATES_READY` | `PENDING` | `assets\asset-manifest.json` | — | — |
| `6. EDIT_READY` | `PENDING` | `editing\` | — | — |
| `7. QA_PASSED` | `PENDING` | `qa\qa-report.md` | — | — |
| `8. FINAL_APPROVED` | `PENDING` | `deliverables\` | — | — |
| `9. DELIVERED` | `PENDING` | `CURRENT-STATE.md` | — | — |
