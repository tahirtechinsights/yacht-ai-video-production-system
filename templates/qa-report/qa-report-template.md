# Technical & Visual QA Report Template

**Template ID:** `TPL-QA-REPORT`  
**Template Version:** `1.0.0`  
**Purpose:** Record formal technical verification (`TECH-*`) and frame-by-frame visual/identity inspection (`VIS-*`) results for a production's release candidate export prior to `QA_PASSED` gate approval. Copy to `productions\<PRODUCTION-ID>\qa\qa-report.md`.

---

## 1. QA Inspection Header

| Field | Value |
|---|---|
| **QA Report ID** | `<e.g., QA-v01>` |
| **Production ID** | `<e.g., YACHT-001>` |
| **Evaluated Deliverable / Export** | `<e.g., deliverables\YACHT-001_DELIV-v01_1080p24.mp4>` |
| **Inspection Date** | `<YYYY-MM-DD>` |
| **Technical QA Reviewer** | `<Name / Role>` |
| **Human Production Authority** | `<Name / Role>` |
| **Overall QA Status** | `NOT TESTED` (`PASS` / `FAIL` / `NOT TESTED`) |

> **Governance Rule:** Do not report unexecuted validations as `PASS`. All checks remain `NOT TESTED` until verified with supporting evidence.

---

## 2. Hard Technical Verification (`TECH-01` to `TECH-10`)

| Check ID | Parameter | Target Requirement (`YACHT-001` Baseline) | Observed Value / Evidence | Status (`PASS` / `FAIL` / `NOT TESTED`) |
|---|---|---|---|---|
| `TECH-01` | File Container | `MP4` (`.mp4`) | — | `NOT TESTED` |
| `TECH-02` | Video Codec | `H.264` (`avc1`) | — | `NOT TESTED` |
| `TECH-03` | Resolution | `1920 × 1080` | — | `NOT TESTED` |
| `TECH-04` | Aspect Ratio | `16:9` (`SAR 1:1`, `DAR 16:9`) | — | `NOT TESTED` |
| `TECH-05` | Frame Rate | `24 fps` CFR (`24/1`) | — | `NOT TESTED` |
| `TECH-06` | Total Duration | `10.0s` (`240 frames`) | — | `NOT TESTED` |
| `TECH-07` | Shot Split Timing | Matches approved shot list (`4s + 3s + 3s` provisional) | — | `NOT TESTED` |
| `TECH-08` | Audio Stream | `None` (`0` audio streams) | — | `NOT TESTED` |
| `TECH-09` | Titles & Labels | `None` (zero overlays/watermarks) | — | `NOT TESTED` |
| `TECH-10` | Manifest Lineage | Complete trace in `assets\asset-manifest.json` | — | `NOT TESTED` |

---

## 3. Hard Visual & Yacht Identity Inspection (`VIS-01` to `VIS-08`)

| Check ID | Inspection Criterion | Shot `S01` | Shot `S02` | Shot `S03` | Overall Status (`PASS` / `FAIL` / `NOT TESTED`) | Defect / Frame Notes |
|---|---|---|---|---|---|---|
| `VIS-01` | Hull & Superstructure Identity | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-02` | Window & Mullion Rigidity | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-03` | Livery, Colour & Materials | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-04` | Fine Hardware & Railings | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-05` | Stabilized Camera Motion | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-06` | Temporal Stability (Zero Flicker) | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-07` | Natural Water & Reflection Physics | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |
| `VIS-08` | Clean Cut Transitions & Tail Frames | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | `NOT TESTED` | — |

---

## 4. Advisory / Creative Observations

- **Exposure & Colour Continuity (`ADVISORY-01`):** `<Not evaluated>`
- **Camera Pacing Harmony (`ADVISORY-02`):** `<Not evaluated>`
- **Compositional Balance (`ADVISORY-03`):** `<Not evaluated>`

---

## 5. Sign-Off & Gate Decision

- **Gate Decision (`EDIT_READY` -> `QA_PASSED`):** `PENDING`
- **Remediation Required (if `FAIL`):** `<None / List required re-generations or re-exports>`
- **Approved By:** `<Signature / Name>`
- **Date:** `<YYYY-MM-DD>`
