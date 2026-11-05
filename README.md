# Yacht AI Video Production System

**Repository Root:** `E:\Yacht-AI-Video-Production`  
**Release Baseline:** `v0.1.0` (`YVP-RELEASE-001`)  
**Current Phase:** Phase 02 Completed / Release Baseline (`YVP-RELEASE-001`)  
**Pilot Production:** `YACHT-001` (`DRAFT` — Infrastructure Ready; Creative Production Not Yet Begun)

---

## 1. Project Introduction

The **Yacht AI Video Production System** is a modular, reusable, AI-assisted cinematic video production framework engineered to transform authentic yacht photographs and reference material into premium, photorealistic, and architecturally faithful video productions.

Unlike ad-hoc generative video experiments that frequently suffer from hull morphing, structural hallucination, temporal flicker, and untraceable asset sprawl, this system establishes a deterministic production pipeline. It combines strict vessel identity protection, cryptographic asset provenance, structured prompt engineering, human-in-the-loop approval gates, and technical quality assurance into a repeatable engineering discipline.

---

## 2. Vision and Objectives

The system is architected to achieve nine core objectives across every production:

1. **Premium Photorealistic Yacht Marketing Videos:** Deliver broadcast- and brokerage-grade cinematic sequences free of synthetic CGI artifacts.
2. **Exterior, Deck, and Interior Cinematic Coverage:** Present cohesive visual storytelling across full-profile marine exteriors, open deck spaces, and luxury cabin/salon interiors.
3. **Source-Faithful Vessel Identity:** Guarantee `100%` structural fidelity to the subject vessel—never altering naval architecture, window counts, livery, or interior joinery.
4. **Stable, Believable Camera and Environmental Motion:** Emulate real gyro-stabilized aerial gimbals, smooth deck sliders, and physically grounded ocean water movement.
5. **Consistent Visual Quality and Colour:** Enforce unified colour profiles (`sRGB` / `Rec.709`), consistent exposure, and matched temporal pacing across cuts.
6. **Repeatable Production Workflows:** Standardize every step from reference intake through final delivery via stage-gated Standard Operating Procedures (SOPs).
7. **Reusable Governance and Prompt Engineering:** Maintain provider-agnostic prompt libraries, negative constraint modules, and lifecycle approval gates.
8. **Traceable AI Generation and Asset Provenance:** Link every final frame back to its winning video candidate, prompt version, model parameters, approved keyframe image, and immutable source reference via SHA-256 manifests.
9. **Scalable Support for Future Yacht Productions:** Isolate production workspaces (`productions/<PRODUCTION-ID>/`) so new vessels and campaigns can be launched without restructuring code or governance.

---

## 3. First Production — `YACHT-001`

The repository initializes with the isolated pilot workspace for **`YACHT-001`** (`productions/YACHT-001/`), governed by the following baseline target specification:

| Parameter | `YACHT-001` Pilot Requirement |
|---|---|
| **Production ID** | `YACHT-001` |
| **Total Duration** | `10.0 seconds` (`240 frames` exact at `24 fps`) |
| **Target Resolution** | `1920 × 1080` pixels (Full HD) |
| **Aspect Ratio** | `16:9` (`SAR 1:1`, `DAR 16:9`) |
| **Frame Rate** | `24 fps` Constant Frame Rate (`24/1` CFR) |
| **Final Container & Codec** | `MP4` (`.mp4`) / `H.264` (`libx264`, `yuv420p`, `Rec.709`) |
| **Audio Policy** | **None** (`0` audio streams present in final container) |
| **Titles and Labels** | **None** (no text overlays, watermarks, or burn-ins) |
| **Visual Style** | Premium cinematic realism |
| **Coverage Zones** | Exterior, Deck, and Interior |
| **Provisional Shot Allocation** | `4.0s` (Exterior `S01`) + `3.0s` (Deck `S02`) + `3.0s` (Interior `S03`) |

> **Current Pilot Status:** `YACHT-001` is currently in `DRAFT` state with its workspace and manifest initialized ([`productions/YACHT-001/assets/asset-manifest.json`](productions/YACHT-001/assets/asset-manifest.json)). **Real yacht reference intake and creative video production have not yet begun.** The `4s + 3s + 3s` shot plan remains provisional pending reference intake analysis in `YVP-PROD-001`.

---

## 4. End-to-End Production Methodology

Every yacht video production executes a 15-stage end-to-end operational workflow:

```text
 1. Production Brief           ──► Define target technical specs, scope, and provisional shot plan.
 2. Source Reference Intake    ──► Register original photos/videos via SHA-256 managed copy & manifest.
 3. Yacht Identity Analysis    ──► Catalogue hull geometry, deck tiers, glazing, livery, and key features.
 4. Shot Selection & Planning  ──► Map verified references to specific shots, durations, and camera moves.
 5. Source Image Assessment    ──► Evaluate resolution, framing, sharpness, and aspect ratio against standards.
 6. Image Enhancement          ──► Perform optical framing or low-denoise fidelity upscaling where needed.
 7. Image Approval             ──► Human sign-off confirming 16:9 1080p+ readiness and 100% identity fidelity.
 8. I2V Prompt Engineering     ──► Assemble layered preservation, camera motion, environment, & negative prompts.
 9. AI Video Generation        ──► Generate video candidates externally using approved keyframes & logged seeds.
10. Candidate Evaluation       ──► Screen takes for identity drift, flicker, or water physics defects.
11. Editing & Sequencing       ──► Conform approved shot candidates to exact frame counts and straight cuts.
12. Colour Matching & Finish   ──► Balance shot-to-shot exposure, white balance, and Rec.709 compliance.
13. Technical & Visual QA      ──► Execute automated container/codec checks and frame-by-frame visual QA.
14. Human Acceptance           ──► Executive Producer / Human Production Authority grants FINAL_APPROVED sign-off.
15. Final Delivery & Archival  ──► Export master deliverable and lock complete end-to-end manifest lineage.
```

---

## 5. System Architecture

The system cleanly decouples reusable infrastructure from per-production assets and external AI engines:

| Architectural Layer | Scope & Responsibility | Location |
|---|---|---|
| **Reusable Production Framework** | Stage workflows, CLI tooling, metadata extractors, and deterministic validators shared across all productions. | [`pipeline/`](pipeline/README.md), [`tools/`](tools/) |
| **Production-Specific Workspaces** | Isolated directory trees holding briefs, managed references, manifests, prompts, candidates, edits, QA reports, and deliverables per yacht. | `productions/<PRODUCTION-ID>/` |
| **Governance & Control Gates** | Operational policies, human authority rules, 9-state lifecycle definitions, and asset provenance contracts. | [`governance/`](governance/production-policy.md) |
| **Technical & Visual Standards** | Hard pass/fail technical specifications vs. creative preferences for images, video, vessel identity, and QA. | [`standards/`](standards/quality-assurance.md) |
| **Prompt Engineering Framework** | Provider-agnostic prompt structures, camera motion archetypes, and modular negative constraint libraries. | [`prompts/`](prompts/README.md) |
| **Managed Media Intake** | Verified read-only ingestion, SHA-256 deduplication, atomic manifest updates, and technical metadata inspection. | [`pipeline/intake/`](pipeline/intake/README.md) |
| **External AI Generation Platforms** | Decoupled third-party image enhancement and Image-to-Video (I2V) synthesis engines. | External (logged via manifest & prompt records) |
| **Video Editing, Finishing & QA** | Timeline assembly, `24 fps` CFR conform, colour finishing, and formal QA inspection reporting. | `productions/<ID>/{editing,qa,deliverables}/` |

---

## 6. Yacht Identity Preservation

A luxury yacht is a bespoke naval engineering artifact. The system enforces zero-tolerance identity protection ([`standards/yacht-identity.md`](standards/yacht-identity.md)) across eight structural domains:

- **Hull Geometry:** Exact sheer line, bow profile (plumb/raked/bulbous), chine lines, freeboard proportions, transom steps, and hull portlight spacing.
- **Yacht Colour & Livery:** Exact hull and superstructure paint/gelcoat shade, metallic finish, boot-top stripe thickness, and waterline placement.
- **Deck Arrangement:** Authentic teak plank orientation, caulking colour, margin boards, sunpads, exterior dining tables, wet bars, and helm stations.
- **Window Placement & Glazing:** Exact window count, corner radii, glass tint reflectivity, and straight, rigid structural mullions across every video frame.
- **Exterior Architecture:** Exact deck tier count, overhang proportions, hardtop/radar arch geometry, SATCOM domes, mast configuration, and fashion plates.
- **Interior Layout:** Faithful bulkhead geometry, ceiling coffer heights, doorway alignments, and cabin spatial proportions.
- **Materials and Furniture:** Authentic wood grain orientation and finish, marble/stone veining, leather paneling, upholstery stitching, and recessed lighting fixtures.
- **Recognizable Vessel Features:** Rigid stainless steel stanchions, pulpits, handrails, cleats, anchor pockets, builder insignia, and nameboards without AI text gibberish or thin-feature melting.

---

## 7. AI Production Methodology

### Image-to-Video (I2V) First Philosophy
All video generation in this system is **Image-to-Video (I2V) anchored** rather than unconstrained Text-to-Video (T2V). Every shot begins with an authentic, human-approved keyframe photograph (`IMG-S<SS>-v<VV>`) derived directly from a registered vessel reference (`REF-<NNN>`).

### Distinction Between Image Enhancement and Motion Generation
1. **Image Preparation & Enhancement (`pipeline/image-preparation/`):**
   - Focuses strictly on preparing a clean `16:9` (`1920×1080` minimum) static keyframe from a registered reference.
   - Prioritizes deterministic optical framing/cropping or ultra-low-denoise fidelity upscaling (`denoise <= 0.15`) so vessel geometry cannot drift.
2. **Motion Generation (`pipeline/video-generation/`):**
   - Takes the locked keyframe and introduces only controlled, low-amplitude single-axis camera movement and subtle environmental motion (water ripples, natural daylight reflections) while holding the vessel structure rigid.

### Division of Responsibility (External AI Platforms vs. Antigravity)
- **External AI Platforms:** Execute heavy neural rendering for super-resolution or I2V generation when operated by the production team.
- **Antigravity & Local Repository Tooling:** Manage repository governance, operational controls, managed media intake, cryptographic SHA-256 verification, technical metadata extraction, manifest lineage, deterministic validation, documentation, and reproducibility.

---

## 8. Prompt Engineering

The prompt engineering framework ([`prompts/README.md`](prompts/README.md)) decomposes every prompt into four isolated layers to prevent appearance drift:

1. **Foundational & Identity Preservation Constraints:** Explicit instructions anchoring first-frame fidelity and locking hull lines, windows, railings, and materials.
2. **Shot-Specific & Compositional Direction:** Tailored templates for Exterior (`S01`), Deck (`S02`), and Interior (`S03`) perspectives ([`prompts/image-to-video/image-to-video-guide.md`](prompts/image-to-video/image-to-video-guide.md)).
3. **Camera Movement Instructions:** Single-vector, low-amplitude camera trajectories (gyro-stabilized parallel track, linear deck slider, slow architectural dolly push-in) that avoid parallax hallucination.
4. **Environmental Motion:** Physically accurate calm sea ripples, hull water lap, and subtle window light caustics.
5. **Negative Constraints:** Modular exclusion lists (`NEG-GLOBAL-01`, `NEG-EXT-01`, `NEG-DECK-01`, `NEG-INT-01`, `NEG-ENH-01`) targeting morphing, temporal flicker, texture boiling, backwards waves, and melting railings ([`prompts/negative-constraints/negative-constraints-library.md`](prompts/negative-constraints/negative-constraints-library.md)).
6. **Prompt Versioning & Generation Metadata:** Every prompt iteration receives a versioned identifier (`PRM-S01-v01`) logging the external provider, model version, seed, motion scale, camera controls, and candidate outcomes (`APPROVED` vs. `REJECTED`).

---

## 9. Production Governance

All operations are bound by three core governance specifications in [`governance/`](governance/):

- **Human Approval Authority ([`governance/production-policy.md`](governance/production-policy.md)):** A designated Human Production Authority holds exclusive sign-off power over brief approval, lifecycle gate transitions, vessel identity verification, candidate selection, and final release. Automated tools never self-approve creative assets.
- **Source Immutability & Asset Provenance ([`governance/asset-provenance.md`](governance/asset-provenance.md)):** Original source files are never modified; managed copies in `references/{images,videos}/` are locked (`immutable_locked: true`) and verified via SHA-256.
- **Candidate Tracking:** Every generated take receives a unique ID (`CAND-S<SS>-<NNN>`) and explicit status (`PENDING_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED`). Technical validation status (`validation_status`) is strictly separated from creative approval (`approval_status`).
- **Nine-State Production Lifecycle ([`governance/approval-gates.md`](governance/approval-gates.md)):**
  `1. DRAFT` → `2. REFERENCES_REGISTERED` → `3. SHOTS_PLANNED` → `4. IMAGES_APPROVED` → `5. VIDEO_CANDIDATES_READY` → `6. EDIT_READY` → `7. QA_PASSED` → `8. FINAL_APPROVED` → `9. DELIVERED`.
- **QA Gates & Release Authorization:** No deliverable may transition to `FINAL_APPROVED` or `DELIVERED` without a signed `PASS` QA report and complete manifest lineage.

---

## 10. Technical Standards

Authoritative technical criteria are maintained in [`standards/`](standards/) and separate hard pass/fail requirements from creative preferences:

- **Image Standards ([`standards/image-standards.md`](standards/image-standards.md)):** Prepared keyframes require lossless `PNG`/`TIFF` (or high-quality `JPEG >= 95`), `16:9` aspect ratio (`PAR 1:1`), minimum `1920×1080` resolution, `sRGB`/`Rec.709` colour profile, and zero geometric warping. Lower-resolution raw references (`< 1920×1080` or `< 1280px` long edge) are accepted during intake with non-fatal `WARNING` flags so they can be evaluated for enhancement.
- **Video Standards ([`standards/video-standards.md`](standards/video-standards.md)):** Final deliverables (`YACHT-001`) require `MP4` container, `H.264` (`yuv420p`, `Rec.709`), `1920×1080`, `16:9`, `24.00 fps` CFR, `10.0s` (`240 frames`), `0` audio streams, and `0` titles/labels.
- **Yacht Identity Standard ([`standards/yacht-identity.md`](standards/yacht-identity.md)):** Defines structural invariants across hull, superstructure, glazing, livery, decks, and interiors.
- **Quality Assurance Standard ([`standards/quality-assurance.md`](standards/quality-assurance.md)):** Defines automated technical checks (`TECH-01` to `TECH-10`) and frame-by-frame visual realism checks (`VIS-01` to `VIS-08`) using `PASS`, `FAIL`, and `NOT TESTED` ratings.

---

## 11. Repository Structure

```text
E:\Yacht-AI-Video-Production\
│
├── README.md                                 # Complete project agenda, architecture, and operations guide
├── START-HERE.md                             # Operator onboarding, lifecycle rules, and quickstart
├── CURRENT-STATE.md                          # Live operational snapshot, phase status, and blockers
├── .gitignore                                # Excludes binary media, temp files, and caches from Git
│
├── governance\                               # Authoritative operational policies (Git-tracked)
│   ├── production-policy.md                  # Human authority, immutability, and candidate rules
│   ├── approval-gates.md                     # 9-state lifecycle entry/exit criteria and gate matrix
│   └── asset-provenance.md                   # ID conventions, lineage chains, and storage policy
│
├── standards\                                # Technical and visual standards (Git-tracked)
│   ├── image-standards.md                    # Source & keyframe image technical requirements
│   ├── video-standards.md                    # Video encoding, motion realism, and delivery specs
│   ├── yacht-identity.md                     # Non-negotiable vessel identity invariants
│   └── quality-assurance.md                  # TECH-* and VIS-* QA inspection criteria
│
├── prompts\                                  # Reusable prompt engineering library (Git-tracked)
│   ├── README.md                             # 4-layer prompt architecture overview
│   ├── image-enhancement\
│   │   └── image-enhancement-guide.md        # Source-fidelity keyframe preparation prompt patterns
│   ├── image-to-video\
│   │   └── image-to-video-guide.md           # Exterior, deck, and interior I2V prompt templates
│   └── negative-constraints\
│       └── negative-constraints-library.md   # Modular anti-morphing, anti-flicker, and physics exclusions
│
├── pipeline\                                 # Pipeline workflow modules and SOPs (Git-tracked)
│   ├── README.md                             # Pipeline stage-to-lifecycle mapping
│   ├── __init__.py
│   ├── intake\                               # Managed Media Intake & Manifest System (YVP-SYS-002)
│   │   ├── README.md                         # Complete intake architecture and CLI documentation
│   │   ├── __init__.py
│   │   ├── cli.py                            # Local CLI (intake, validate, list, inspect, report)
│   │   ├── manager.py                        # Safe temp-copy intake, SHA-256 check, & atomic manifest IO
│   │   ├── metadata.py                       # Pillow image & FFprobe / stdlib ISO-BMFF video extractors
│   │   ├── validator.py                      # Deterministic 11-check validation engine
│   │   └── test_intake_system.py             # 12-scenario automated unittest verification suite
│   ├── image-preparation\                    # Keyframe preparation stage workspace
│   ├── video-generation\                     # External I2V execution stage workspace
│   ├── editing\                              # Timeline conform and assembly stage workspace
│   └── delivery\                             # Final QA and delivery stage workspace
│
├── tools\                                    # Standalone validation and inspection scripts (Git-tracked)
│   ├── validation\
│   │   └── validate_manifest.py              # CLI wrapper for production manifest & asset validation
│   └── media-processing\
│       └── media_inspector.py                # Read-only technical metadata & dependency inspector
│
├── templates\                                # Versioned master templates (Git-tracked)
│   ├── production-brief\
│   │   └── production-brief-template.md      # TPL-PRODUCTION-BRIEF (v1.0.0)
│   ├── shot-list\
│   │   └── shot-list-template.md             # TPL-SHOT-LIST (v1.0.0)
│   ├── asset-manifest\
│   │   ├── asset-manifest-template.json      # TPL-ASSET-MANIFEST (v1.1.0 canonical JSON schema)
│   │   └── asset-manifest-template.md        # Schema documentation & status separation guide
│   └── qa-report\
│       └── qa-report-template.md             # TPL-QA-REPORT (v1.0.0)
│
└── productions\                              # Isolated production workspaces
    └── YACHT-001\                            # Pilot production workspace
        ├── brief\                            # Production brief & shot list (Git-tracked .md)
        ├── references\                       # Managed immutable source copies (Binaries Git-ignored)
        │   ├── images\                       # Managed reference images (REF-001.jpg, etc.)
        │   └── videos\                       # Managed reference videos (REF-002.mp4, etc.)
        ├── assets\                           # asset-manifest.json (Git-tracked) & prepared keyframes (Ignored)
        │   └── asset-manifest.json           # Authoritative YACHT-001 manifest (currently DRAFT, 0 assets)
        ├── prompts\                          # Shot prompt logs and parameter records (Git-tracked .md)
        ├── generations\                      # Raw I2V candidate renders (Binaries Git-ignored)
        ├── editing\                          # Timeline exchange metadata (.edl/.xml tracked; caches ignored)
        ├── qa\                               # Completed QA inspection reports (Git-tracked .md)
        └── deliverables\                     # Final approved MP4 masters (Binaries Git-ignored)
```

---

## 12. Production Operations & CLI Reference

The Managed Media Intake system ([`pipeline/intake/README.md`](pipeline/intake/README.md)) provides deterministic local operations for registering, inspecting, and validating production reference media:

### Managed Intake & Manifest Behavior
- **Non-Destructive Copy:** External source files are inspected in read-only mode, hashed with SHA-256, copied to a temporary `.part` file inside `productions/<ID>/references/{images|videos}/`, verified bit-for-bit (`source_sha256 == copied_sha256`), and atomically finalized as `REF-<NNN>.<ext>` (e.g., `REF-001.jpg`, `REF-002.mp4`).
- **SHA-256 Deduplication:** Identical files submitted to the same production are detected via SHA-256 (`DUPLICATE_SKIPPED`) without creating redundant copies.
- **Atomic Manifest Updates:** Registration writes to a temporary manifest file with `os.fsync()` before executing an atomic `os.replace()` on `productions/<ID>/assets/asset-manifest.json`.
- **Technical Metadata Extraction:** Extracts image metadata via `Pillow` (`width`, `height`, `format`, `colour_mode`, `colour_profile`, `orientation`, `file_size`, `aspect_ratio`) and video metadata via `ffprobe` (or a non-fabricating Python standard-library ISO-BMFF atom parser when `ffprobe` is absent, logging explicit dependency warnings).

### Implemented CLI Commands (`YVP-SYS-002`)

Run from the repository root (`E:\Yacht-AI-Video-Production`):

```powershell
# 1. Register one or more external reference files into a production
python -m pipeline.intake.cli intake --production YACHT-001 --zone exterior "C:\path\to\source.jpg"

# 2. Validate manifest integrity, SHA-256 checksums, and path containment
python -m pipeline.intake.cli validate --production YACHT-001

# 3. List all registered reference assets for a production
python -m pipeline.intake.cli list --production YACHT-001

# 4. Inspect full JSON technical metadata and provenance for a specific asset ID
python -m pipeline.intake.cli inspect --production YACHT-001 REF-001

# 5. Generate a production intake, validation, and dependency summary report
python -m pipeline.intake.cli report --production YACHT-001

# 6. Run standalone validation and media inspection wrappers
python tools/validation/validate_manifest.py --production YACHT-001
python tools/media-processing/media_inspector.py --check-deps

# 7. Execute the 12-scenario automated verification suite
python pipeline/intake/test_intake_system.py
```

*(Append `--json` to `intake`, `validate`, `list`, or `report` for structured JSON output.)*

---

## 13. Development Roadmap

The project is structured into sequential infrastructure, release, and production phases. Planned phases represent upcoming roadmap milestones, not completed features:

| Phase / Task ID | Milestone Name | Status | Scope Summary |
|---|---|---|---|
| **`YVP-SYS-001`** | Foundation and Governance | **Completed** | Repository architecture, governance policies, 9-state lifecycle gates, technical standards, prompt guides, and templates. |
| **`YVP-SYS-002`** | Managed Media Intake | **Completed** | Managed copy intake pipeline, SHA-256 deduplication, metadata extractors, deterministic validator, CLI, and 12-test verification suite. |
| **`YVP-RELEASE-001`** | Initial Repository Baseline | **In Progress** | Complete project agenda documentation, pre-release verification, initial Git baseline commit (`v0.1.0`), and authorized remote push gate. |
| **`YVP-PROD-001`** | Reference Analysis & Shot Planning | **Planned** | Live intake of real `YACHT-001` reference assets, vessel identity baseline analysis, and finalization of the `10s` shot list. |
| **`YVP-PROD-002`** | Image Preparation | **Planned** | Selection, `16:9` (`1920×1080`) framing, optical conditioning/enhancement, and `IMAGES_APPROVED` gate sign-off for `YACHT-001`. |
| **`YVP-PROD-003`** | Image-to-Video Generation | **Planned** | Shot-specific prompt engineering, external AI video candidate generation, candidate logging, and `VIDEO_CANDIDATES_READY` selection. |
| **`YVP-PROD-004`** | Editing and QA | **Planned** | Master timeline assembly (`4s + 3s + 3s = 10s`, `24 fps`, silent `H.264 MP4`), colour matching, and formal `TECH-*` / `VIS-*` QA inspection. |
| **`YVP-PROD-005`** | Final Pilot Delivery | **Planned** | Executive `FINAL_APPROVED` sign-off, final master export to `deliverables/`, lineage audit, and transition to `DELIVERED`. |

*Note: Future pipeline automation scripts (e.g., automated keyframe prep, candidate management CLI extensions, and automated deliverable QA runners) and advanced prompt-engineering refinements are planned capabilities for upcoming phases.*

---

## 14. Future Expansion

The architecture is designed to scale across future requirements without breaking existing manifests or governance:

- **Additional Yacht Productions:** Launch isolated workspaces (`productions/YACHT-002/`, `YACHT-003/`, etc.) via `--init-production` using shared governance and tooling.
- **Longer Videos & Multi-Sequence Campaigns:** Scale shot lists from 10-second hero teasers to 30-second, 60-second, or multi-minute charter and brokerage walkthroughs.
- **Multiple Aspect Ratios:** Support `16:9` widescreen (`1920×1080` / `3840×2160`), `9:16` vertical social reels (`1080×1920`), and `1:1` / `4:5` formats via per-production brief overrides.
- **Different AI Generation Providers:** Remain vendor-neutral as external image enhancement and I2V models evolve, recording model-specific parameters inside versioned prompt logs.
- **Reusable Camera-Motion Concepts:** Expand [`prompts/image-to-video/image-to-video-guide.md`](prompts/image-to-video/image-to-video-guide.md) with validated motion presets per vessel zone.
- **Batch Asset Processing & Automated Technical QA:** Add batch preparation and automated FFprobe deliverable verification under `tools/`.
- **Reusable Editing Workflows & Archival:** Support timeline interchange (`.edl`, `.xml`, `.fcpxml`) and configurable external archive media roots (`storage_policy.media_root`).

---

## 15. Getting Started

1. **Read the Onboarding Guide:** Start with [`START-HERE.md`](START-HERE.md) for operational rules, directory usage, and lifecycle gate protocols.
2. **Check Live Operational State:** Inspect [`CURRENT-STATE.md`](CURRENT-STATE.md) before running any task to confirm the active phase, blockers, and next authorized step.
3. **Verify Local Environment & Intake Pipeline:**
   ```powershell
   python tools/media-processing/media_inspector.py --check-deps
   python pipeline/intake/test_intake_system.py
   python -m pipeline.intake.cli report --production YACHT-001
   ```
4. **Review Stage Documentation:** Consult [`pipeline/README.md`](pipeline/README.md) and [`pipeline/intake/README.md`](pipeline/intake/README.md) for detailed intake and manifest instructions.

---

## 16. Current Project Status

| Domain | Current Status |
|---|---|
| **Repository & Governance Foundation (`YVP-SYS-001`)** | **Completed & Verified** |
| **Managed Media Intake & Manifest System (`YVP-SYS-002`)** | **Completed & Verified** (`12/12` automated tests passing) |
| **Documentation Baseline & Git Release (`YVP-RELEASE-001`)** | **In Progress** (`v0.1.0` baseline) |
| **`YACHT-001` Pilot Creative Production** | **Not Started (`DRAFT`)** — `0` real yacht references ingested; no keyframes enhanced; no video candidates or deliverables produced. |
