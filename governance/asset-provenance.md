# Asset Provenance, Versioning & Storage Policy

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `governance\asset-provenance.md`  
**Version:** 1.0.0

---

## 1. Core Provenance Principles

To guarantee auditability, vessel fidelity, and reproducible quality across all yacht productions, the following seven provenance rules are strictly enforced:

1. **Original Source Assets Are Immutable:** Reference files placed in `productions\<PRODUCTION-ID>\references\` are never modified, overwritten, or deleted in place.
2. **Generated Media Must Be Traceable to Its Source:** Every prepared image, video candidate, and final export must explicitly reference its parent Asset ID(s) in `assets\asset-manifest.json`.
3. **Every Asset and Candidate Receives a Unique Identifier:** No two files or generation takes may share an ID or overwrite an existing ID.
4. **Prompt Versions and Model Settings Are Recorded:** Every AI-assisted enhancement or I2V generation is linked to an immutable prompt version record containing exact prompt text, negative constraints, and model configuration parameters.
5. **Rejected Candidates Remain Distinguishable from Approved Candidates:** Rejected takes are retained or logged with explicit `REJECTED` status and defect notes so they can never be confused with `APPROVED` assets.
6. **Approved Media Must Not Be Silently Overwritten:** Once an asset or candidate is marked `APPROVED`, its file is locked by convention. Any subsequent refinement must be saved as a new incremented asset/candidate ID, marking the prior version `SUPERSEDED` only upon human approval.
7. **Final Exports Must Be Traceable to Their Production Inputs:** Every deliverable in `deliverables\` records the exact list of approved candidate IDs, keyframe asset IDs, prompt version IDs, and reference IDs that produced it.

---

## 2. Standard Identifier & Naming Convention

All assets within a production (`<PROD-ID>`, e.g., `YACHT-001`) use deterministic, human-readable identifiers:

| Asset Category | ID Pattern | Filename Pattern Example | Storage Location |
|---|---|---|---|
| **Source Reference** | `REF-<NNN>` | `REF-001_exterior-starboard-profile.jpg` | `productions\<PROD-ID>\references\` |
| **Prepared Keyframe** | `IMG-S<SS>-<VV>` | `IMG-S01-v01_exterior-keyframe-1080p.png` | `productions\<PROD-ID>\assets\` |
| **Prompt Record** | `PRM-S<SS>-<VV>` | `PRM-S01-v01.md` | `productions\<PROD-ID>\prompts\` |
| **Video Candidate** | `CAND-S<SS>-<NNN>` | `CAND-S01-001_raw.mp4` | `productions\<PROD-ID>\generations\` |
| **Edit / Conform** | `EDIT-<VV>` | `EDIT-v01_timeline-notes.md` | `productions\<PROD-ID>\editing\` |
| **Final Deliverable** | `DELIV-<VV>` | `YACHT-001_DELIV-v01_1080p24.mp4` | `productions\<PROD-ID>\deliverables\` |

- `<SS>`: Two-digit Shot Number (`01`, `02`, `03`, ...).
- `<VV>`: Two-digit Version Number (`01`, `02`, ...).
- `<NNN>`: Three-digit Sequential Number (`001`, `002`, ...).

---

## 3. End-to-End Lineage Chain

Every final deliverable (`DELIV-<VV>`) must resolve a complete, unbroken lineage chain inside `productions\<PROD-ID>\assets\asset-manifest.json`:

```text
[REF-001: Original Yacht Photo]
       │
       ├──> [PRM-ENH-S01-v01: Enhancement Prompt & Params (if used)]
       ▼
[IMG-S01-v01: Approved 16:9 1080p Keyframe Image]
       │
       ├──> [PRM-I2V-S01-v01: I2V Prompt, Negative Constraints & Model Settings]
       ▼
[CAND-S01-002: Approved 4.0s Video Candidate]  (while CAND-S01-001 is logged REJECTED)
       │
       ├──> [EDIT-v01: Master Sequence Conform (S01 + S02 + S03 = 10.0s)]
       ├──> [QA-v01: Passed Technical & Visual QA Report]
       ▼
[DELIV-v01: Final Approved MP4 H.264 1920x1080 24fps Deliverable]
```

---

## 4. Separating Approved vs. Rejected Candidates

1. **Manifest-Driven Status:** The authoritative status (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED`) is recorded in `assets\asset-manifest.json`.
2. **Filesystem Organization in `generations\`:**
   - Candidates may either reside directly in `productions\<PROD-ID>\generations\` using strict `CAND-S<SS>-<NNN>` filenames or be sorted into shot subdirectories (`generations\S01\`, `generations\S02\`, `generations\S03\`).
   - Optionally, rejected takes may be moved to `generations\rejected\` provided their `relative_path` and `status: "REJECTED"` are updated in `asset-manifest.json`.
   - Under no circumstances may an unapproved or rejected candidate be imported into `editing\` for final master assembly.

---

## 5. Git vs. Local Media Storage Policy

### What Is Tracked in Git
- All Markdown documentation (`README.md`, `START-HERE.md`, `CURRENT-STATE.md`, `governance\`, `standards\`, `prompts\`, `pipeline\`).
- Reusable templates (`templates\`).
- Validation and media-processing scripts (`tools\`).
- Production briefs, shot lists, prompt logs, QA reports, and JSON asset manifests (`productions\<PROD-ID>\**\*.md`, `*.json`).
- Lightweight timeline exchange metadata (`.edl`, `.xml`, `.fcpxml`) if applicable.

### What Is Excluded from Git (Stored Locally)
- All binary media files (`.png`, `.jpg`, `.tif`, `.mp4`, `.mov`, `.wav`, etc.) inside `productions\<PROD-ID>\{references,assets,generations,editing,deliverables}\`.
- Temporary scratch files, NLE render caches, and proxy media.

### Configurable Local Media Storage Policy
1. **Default Mode (Colocated Workspace Storage):**
   - By default, binary media files reside directly inside their respective `productions\<PROD-ID>\` subdirectories on the local drive (`E:\Yacht-AI-Video-Production\productions\<PROD-ID>\...`).
   - `.gitignore` prevents Git from indexing these binary files while preserving the directory structure and metadata files (`asset-manifest.json`).
2. **External / Archive Media Root Override (Optional for Scale):**
   - If local disk capacity on `E:` becomes constrained across many future productions, `asset-manifest.json` supports a `storage_policy.media_root` field (defaulting to `"."` for colocated storage, or pointing to a configurable external/NAS volume path such as `"D:\\Yacht-Media-Archive\\YACHT-001"`).
   - File integrity is maintained via `sha256` checksums and relative paths recorded in `asset-manifest.json`, avoiding any need for databases or complex storage infrastructure.
