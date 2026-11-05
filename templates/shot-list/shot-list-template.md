# Shot List & Cinematic Plan Template

**Template ID:** `TPL-SHOT-LIST`  
**Template Version:** `1.0.0`  
**Purpose:** Define the shot-by-shot structure, duration allocation, source reference mapping, camera motion direction, and vessel preservation constraints for a yacht video production. Copy to `productions\<PRODUCTION-ID>\brief\shot-list.md`.

---

## 1. Shot Plan Metadata

| Field | Value |
|---|---|
| **Production ID** | `<e.g., YACHT-001>` |
| **Plan Status** | `PROVISIONAL` / `APPROVED` |
| **Target Total Duration** | `<e.g., 10.0 seconds (240 frames @ 24 fps)>` |
| **Transition Style** | `<e.g., Straight cuts (0-frame handles overlapped)>` |
| **Approved By** | `<Human Production Authority>` |
| **Date** | `<YYYY-MM-DD>` |

---

## 2. Shot Sequence Summary Table

| Shot ID | Zone / Category | Duration (s) | Frame Count (`@24fps`) | Source Reference ID | Approved Keyframe ID | Prompt Record ID | Winning Candidate ID |
|---|---|---|---|---|---|---|---|
| `S01` | `<e.g., Exterior>` | `<e.g., 4.0s>` | `<e.g., 96>` | `<REF-NNN>` | `<IMG-S01-vNN>` | `<PRM-S01-vNN>` | `<CAND-S01-NNN>` |
| `S02` | `<e.g., Deck>` | `<e.g., 3.0s>` | `<e.g., 72>` | `<REF-NNN>` | `<IMG-S02-vNN>` | `<PRM-S02-vNN>` | `<CAND-S02-NNN>` |
| `S03` | `<e.g., Interior>` | `<e.g., 3.0s>` | `<e.g., 72>` | `<REF-NNN>` | `<IMG-S03-vNN>` | `<PRM-S03-vNN>` | `<CAND-S03-NNN>` |
| **TOTAL** | — | **`<10.0s>`** | **`<240>`** | — | — | — | — |

---

## 3. Detailed Shot Specifications

### Shot `S01` — `<Category, e.g., Exterior>`
- **Duration / Frames:** `<e.g., 4.0s / 96 frames @ 24 fps>`
- **Assigned Source Reference (`REF-ID`):** `<TBD after reference intake>`
- **Approved Keyframe (`IMG-ID`):** `<TBD>`
- **Framing & Composition:** `<Describe framing, horizon placement, subject scale>`
- **Camera Movement:** `<Describe single-axis stabilized camera move and low motion amplitude>`
- **Environmental Motion:** `<Describe natural water ripple, reflection, or lighting behaviour>`
- **Vessel Identity Invariants to Protect:** `<List critical hull, window, arch, railing, or livery features visible in this angle>`

---

### Shot `S02` — `<Category, e.g., Deck>`
- **Duration / Frames:** `<e.g., 3.0s / 72 frames @ 24 fps>`
- **Assigned Source Reference (`REF-ID`):** `<TBD after reference intake>`
- **Approved Keyframe (`IMG-ID`):** `<TBD>`
- **Framing & Composition:** `<Describe deck perspective and architectural focal point>`
- **Camera Movement:** `<Describe smooth slider/dolly movement>`
- **Environmental Motion:** `<Describe background water or daylight reflection behaviour>`
- **Vessel Identity Invariants to Protect:** `<List teak planking, seating, railings, and superstructure features>`

---

### Shot `S03` — `<Category, e.g., Interior>`
- **Duration / Frames:** `<e.g., 3.0s / 72 frames @ 24 fps>`
- **Assigned Source Reference (`REF-ID`):** `<TBD after reference intake>`
- **Approved Keyframe (`IMG-ID`):** `<TBD>`
- **Framing & Composition:** `<Describe cabin/salon perspective and lighting>`
- **Camera Movement:** `<Describe slow architectural dolly movement>`
- **Environmental Motion:** `<Describe natural window light / subtle water reflection caustics>`
- **Vessel Identity Invariants to Protect:** `<List joinery wood grain, stone surfaces, furniture, window mullions, and light fixtures>`
