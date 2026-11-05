# START HERE — Operational Onboarding & Production Guide

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Version:** 1.0.0

---

## 1. Welcome & Onboarding

This guide provides the operational entry point for working inside the **Yacht AI Video Production System**. Every production in this repository follows strict governance, asset traceability, and technical quality assurance rules to guarantee photorealistic, identity-faithful yacht videos.

Before executing any task:
1. Read [CURRENT-STATE.md](CURRENT-STATE.md) to confirm the active phase, authorized task ID, and any blockers.
2. Review [governance/production-policy.md](governance/production-policy.md) and [governance/approval-gates.md](governance/approval-gates.md).
3. Never advance a production state or begin media generation without explicit human authorization.

---

## 2. Production Lifecycle Overview

Every production progresses sequentially through nine strictly gated states. File existence alone never advances a state; each transition requires documented evidence and human sign-off:

```text
[1. DRAFT]
    │
    ▼
[2. REFERENCES_REGISTERED]
    │
    ▼
[3. SHOTS_PLANNED]
    │
    ▼
[4. IMAGES_APPROVED]
    │
    ▼
[5. VIDEO_CANDIDATES_READY]
    │
    ▼
[6. EDIT_READY]
    │
    ▼
[7. QA_PASSED]
    │
    ▼
[8. FINAL_APPROVED]
    │
    ▼
[9. DELIVERED]
```

Full entry criteria, exit criteria, required evidence, and approval authorities are specified in [governance/approval-gates.md](governance/approval-gates.md).

---

## 3. Directory Usage Guide

| Directory | Purpose & Operational Rules |
|---|---|
| `governance\` | Authoritative policies for human approval gates, lifecycle state transitions, and asset provenance. Modify only under governance tasks. |
| `standards\` | Technical specifications for images, video encoding, vessel identity preservation, and QA pass/fail rules. |
| `prompts\` | Reusable, provider-agnostic prompt engineering patterns, structural templates, and negative constraint libraries. |
| `pipeline\` | Stage-by-stage standard operating procedures (SOPs) for intake, image preparation, video generation, editing, and delivery. |
| `tools\` | PowerShell and CLI scripts for manifest validation, directory verification, and media inspection (`validation\`, `media-processing\`). |
| `templates\` | Clean master templates (`production-brief\`, `shot-list\`, `asset-manifest\`, `qa-report\`). Copy these into a production workspace; do not populate production data inside `templates\`. |
| `productions\<ID>\` | Isolated workspace for a specific production (e.g., `productions\YACHT-001\`). All reference files, manifests, prompts, candidates, edits, QA reports, and deliverables for that production live here. |

### Inside a Production Workspace (`productions\<PRODUCTION-ID>\`)
- `brief\`: Holds the instantiated production brief and shot list.
- `references\`: Read-only storage for managed, immutable client/vessel reference images (`references\images\`) and videos (`references\videos\`) registered via `python -m pipeline.intake.cli` ([pipeline/intake/README.md](pipeline/intake/README.md)).
- `assets\`: Holds `asset-manifest.json` and prepared/enhanced keyframe images approved for video generation.
- `prompts\`: Holds exact prompt versions, negative constraints, and model parameter logs used for each shot.
- `generations\`: Stores generated video candidates organized by shot and unique candidate ID (`CAND-S01-001`, etc.), separating approved and rejected takes via manifest status.
- `editing\`: Holds NLE timelines, edit decision lists, and assembly metadata.
- `qa\`: Holds completed QA inspection reports against [standards/quality-assurance.md](standards/quality-assurance.md).
- `deliverables\`: Stores final approved master video exports and delivery manifests.

---

## 4. Core Governance Requirements

1. **Human Approval Authority:** All lifecycle state transitions, creative selections, identity verifications, and final releases require explicit human approval.
2. **Original Asset Immutability:** Files placed in `productions\<ID>\references\` must never be modified, overwritten, cropped in place, or deleted.
3. **Vessel Identity Protection:** Hull geometry, superstructure lines, window proportions, paint/livery, deck layout, and interior furnishings must strictly match the reference vessel ([standards/yacht-identity.md](standards/yacht-identity.md)).
4. **Traceability:** Every generated image or video candidate must record its parent asset ID, prompt version ID, generation parameters, and approval status in the production's asset manifest ([governance/asset-provenance.md](governance/asset-provenance.md)).
5. **Git Hygiene:** Track documentation, manifests, prompts, and lightweight scripts in Git. Exclude heavy binary media files (`.mp4`, `.mov`, `.png`, `.tif`, etc.) as configured in [.gitignore](.gitignore).

---

## 5. Starting a Future Production

To initialize a new production (e.g., `YACHT-002`):

1. **Create the Production Directory Tree & Manifest:**
   Run `python -m pipeline.intake.cli intake --production YACHT-002 --init-production <source_file>` (or create `productions\YACHT-002\` with the standard subdirectories including `references\images\` and `references\videos\`).
2. **Instantiate Templates:**
   - Copy `templates\production-brief\production-brief-template.md` to `productions\YACHT-002\brief\production-brief.md`.
   - Copy `templates\shot-list\shot-list-template.md` to `productions\YACHT-002\brief\shot-list.md`.
   - Copy `templates\asset-manifest\asset-manifest-template.json` to `productions\YACHT-002\assets\asset-manifest.json` (automatically initialized if `--init-production` is used).
   - Copy `templates\qa-report\qa-report-template.md` to `productions\YACHT-002\qa\qa-report.md`.
3. **Set Initial State:**
   Record the new production in `DRAFT` state inside the production brief and [CURRENT-STATE.md](CURRENT-STATE.md).
4. **Proceed via Gated Pipeline:**
   Follow the stage workflows in `pipeline\` starting with [`pipeline\intake\README.md`](pipeline/intake/README.md) to register reference assets and request human sign-off for `REFERENCES_REGISTERED`.
