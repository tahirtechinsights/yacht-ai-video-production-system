# Production Policy & Governance Framework

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `governance\production-policy.md`  
**Version:** 1.0.0

---

## 1. Purpose

This policy establishes the operational rules, authority boundaries, and non-negotiable protections governing all AI-assisted yacht video productions within `E:\Yacht-AI-Video-Production`.

---

## 2. Human Approval Authority

1. **Supreme Decision Authority:** A designated Human Production Authority (Executive Producer / Creative Director / Project Owner) retains sole authority over:
   - Production initialization and brief approval.
   - Lifecycle state transitions (`DRAFT` through `DELIVERED`).
   - Vessel identity verification on enhanced images and generated videos.
   - Candidate acceptance or rejection.
   - Final release and delivery authorization.
2. **Role of Automation & AI Agents (Antigravity):**
   - Antigravity and helper scripts are authorized to perform repository scaffolding, documentation maintenance, manifest updates, technical validation checks (e.g., resolution, frame rate, codec inspection), and workflow orchestration when explicitly instructed.
   - Automated systems **must never** self-approve creative assets, advance a production lifecycle gate autonomously, fabricate QA results, or overwrite approved files.

---

## 3. Original Asset Preservation

1. **Immutability Rule:** All client-supplied or reference yacht photographs, spec sheets, and videos ingested into `productions\<PRODUCTION-ID>\references\` are strictly **read-only and immutable**.
2. **Prohibited Operations on References:**
   - In-place cropping, colour grading, retouching, or re-encoding of files in `references\`.
   - Renaming or deleting registered reference files without a formal manifest revision approved by the Human Production Authority.
3. **Working Copies:** All image preparation, aspect-ratio framing, cleanup, or upscaling must read from `references\` and write new derivative files into `productions\<PRODUCTION-ID>\assets\` with new unique Asset IDs linked to the parent Reference ID.

---

## 4. Yacht Identity Protection

1. **Zero-Hallucination Mandate:** The subject yacht's physical architecture is invariant. AI image enhancement and image-to-video generation must preserve:
   - Exact hull lines, sheer line, bow profile, and transom geometry.
   - Superstructure deck tiers, radar arch / hardtop geometry, and mast configurations.
   - Window shapes, mullions, glazing tint, and portlight counts/positions.
   - Exterior paint colours, boot-top stripes, teak decking patterns, and materiality.
   - Deck furniture arrangements, railings, cleats, and safety equipment.
   - Interior architectural layout, joinery woods, stone surfaces, and lighting fixtures.
2. **Mandatory Rejection:** Any generated image or video candidate that alters, morphs, adds, or removes structural vessel features must be rejected regardless of aesthetic appeal (see [standards/yacht-identity.md](../standards/yacht-identity.md)).

---

## 5. Prompt and Generation Traceability

1. **No Unlogged Generations:** Every candidate image or video generated for a production must be accompanied by a complete metadata record in `productions\<PRODUCTION-ID>\prompts\` and registered in `productions\<PRODUCTION-ID>\assets\asset-manifest.json`.
2. **Required Traceability Fields:**
   - Unique Candidate ID and Target Shot ID.
   - Source/Parent Asset ID (exact keyframe image used for I2V).
   - Prompt Version ID, including full positive prompt, preservation constraints, and negative constraints.
   - External AI platform/model name, model version, seed (if exposed), motion strength / CFG / camera control settings, and timestamp.

---

## 6. Candidate Acceptance and Rejection

1. **Explicit Status Classification:** Every generated asset or video take is assigned one of the following statuses in the Asset Manifest:
   - `PENDING_REVIEW`: Newly ingested candidate awaiting technical and visual inspection.
   - `APPROVED`: Passed technical checks and approved by Human Production Authority for timeline assembly.
   - `REJECTED`: Failed technical, identity, or motion criteria (reason must be logged).
   - `SUPERSEDED`: Previously approved candidate replaced by a superior approved candidate.
2. **Distinguishability & Non-Destructive Handling:**
   - Rejected candidates must remain clearly distinguishable from approved candidates via manifest status and filename/subfolder conventions (or explicit rejection logs) so they can never be accidentally pulled into an edit timeline.
   - Approved media must never be silently overwritten by subsequent generations; new generations receive new incremented Candidate IDs.

---

## 7. Production Lifecycle Transitions

1. **Strict Sequential Progression:** Productions move through nine defined states (`DRAFT` -> `REFERENCES_REGISTERED` -> `SHOTS_PLANNED` -> `IMAGES_APPROVED` -> `VIDEO_CANDIDATES_READY` -> `EDIT_READY` -> `QA_PASSED` -> `FINAL_APPROVED` -> `DELIVERED`).
2. **No Implicit Advancement:** The mere presence of files in a directory (`references\`, `generations\`, `deliverables\`, etc.) **does not** advance the production state. Every transition requires verifying entry/exit criteria in [governance/approval-gates.md](approval-gates.md) and updating `CURRENT-STATE.md` and the production brief upon human sign-off.
3. **Rollback Protocol:** If a downstream stage uncovers a defect (e.g., QA detects hull morphing in Shot 2), the production state must be explicitly rolled back to the appropriate upstream state (`VIDEO_CANDIDATES_READY` or `IMAGES_APPROVED`) and documented in `CURRENT-STATE.md`.

---

## 8. Release Authorization

1. **Pre-Release Requirements:** A final video deliverable in `productions\<PRODUCTION-ID>\deliverables\` may only be authorized for release when:
   - A completed QA report in `productions\<PRODUCTION-ID>\qa\` demonstrates `PASS` across all technical and visual realism criteria ([standards/quality-assurance.md](../standards/quality-assurance.md)).
   - The final export is fully traceable in the asset manifest to its approved timeline, approved shot candidates, approved keyframes, and immutable reference assets.
   - The Human Production Authority grants explicit `FINAL_APPROVED` sign-off.
