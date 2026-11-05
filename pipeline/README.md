# Production Pipeline Stage Directory

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `pipeline\README.md`  
**Version:** 1.0.0

---

## 1. Purpose

The `pipeline\` directory organizes stage-specific Standard Operating Procedures (SOPs) and stage specifications across the five operational phases of a yacht video production.

---

## 2. Pipeline Stages & Lifecycle Mapping

| Stage Directory | Corresponding Lifecycle Transitions | Stage Scope |
|---|---|---|
| `pipeline\intake\` | `DRAFT` -> `REFERENCES_REGISTERED` -> `SHOTS_PLANNED` | Reference intake, immutability lock, SHA-256 registration in `asset-manifest.json`, reference coverage analysis, and shot list finalization (Targeted in `YVP-SYS-002`). |
| `pipeline\image-preparation\` | `SHOTS_PLANNED` -> `IMAGES_APPROVED` | Keyframe selection, `16:9` (`1920×1080`) framing, optical conditioning or fidelity upscaling, and vessel identity verification against parent references. |
| `pipeline\video-generation\` | `IMAGES_APPROVED` -> `VIDEO_CANDIDATES_READY` | Structured I2V prompt preparation, external AI video generation execution, candidate ID registration, and pre-edit candidate selection. |
| `pipeline\editing\` | `VIDEO_CANDIDATES_READY` -> `EDIT_READY` | Timeline assembly (`4s + 3s + 3s = 10s` provisional for `YACHT-001`), `24 fps` CFR conform, audio stripping, and release-candidate export. |
| `pipeline\delivery\` | `EDIT_READY` -> `QA_PASSED` -> `FINAL_APPROVED` -> `DELIVERED` | Technical/visual QA inspection (`qa-report.md`), executive sign-off, final deliverable packaging (`deliverables\`), and manifest lineage closure. |
