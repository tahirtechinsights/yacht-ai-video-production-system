# Yacht Identity Preservation Standard

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `standards\yacht-identity.md`  
**Version:** 1.0.0

---

## 1. Purpose

In luxury yacht marketing and visualization, the vessel is a specific, bespoke engineering artifact—not a generic boat. Even minor alterations to hull lines, window configurations, or deck layouts invalidate a video for client or brokerage use.

This standard defines the **Hard Technical & Structural Invariants** required to preserve exact yacht identity across all image preparation and Image-to-Video (I2V) stages.

---

## 2. Hard Structural Invariants (Zero-Tolerance Requirements)

Every enhanced image and generated video frame must remain 100% faithful to the registered reference assets (`references\REF-<NNN>`) across the following seven domains:

### 2.1 Hull & Naval Architecture
- **Sheer Line & Bow Profile:** Exact angle and curvature of the stem/bow (plumb bow, raked bow, bulbous bow relief), chine lines, and freeboard height.
- **Transom & Swim Platform:** Exact stern geometry, transom steps, garage door lines, and passerelle/swim platform proportions.
- **Hull Penetrations:** Exact count, shape, and horizontal spacing of hull portlights, anchor pockets, hawsepipes, and underwater exhaust reliefs.

### 2.2 Superstructure & Exterior Profile
- **Deck Tiers:** Exact number of decks (main deck, upper/bridge deck, sundeck/flybridge) and overhang proportions.
- **Hardtop, Radar Arch & Mast:** Exact geometry of radar domes, SATCOM domes, navigation light masts, antennas, and outriggers.
- **Architectural Styling Lines:** Fashion plates, louvers, wing stations, and structural pillars/supports must not shift, bend, or multiply.

### 2.3 Glazing & Windows
- **Window Geometry:** Exact shape, corner radii, and aspect ratio of salon windows, pilothouse windscreens, and hull glazing.
- **Mullions & Frames:** Structural window mullions and pillars must remain straight, equidistant, and unbroken across the entire duration of a video clip.
- **Glass Tint & Reflectivity:** Consistent tint density and realistic sky/water reflection behaviour without inventing fictional interior structures behind dark glass.

### 2.4 Livery, Paint & Exterior Materials
- **Hull & Superstructure Colour:** Exact paint/gelcoat shade (e.g., Matterhorn White, Kingston Grey, Flag Blue), metallic finish behaviour, and gloss level.
- **Boot-Top & Cove Stripes:** Exact colour, thickness, and waterline placement.
- **Decking Material:** Exact teak plank orientation, caulking colour (black vs. white/grey), and margin board geometry.

### 2.5 Deck Layout & Fittings
- **Fixed Furniture & Amenities:** Sunpads, exterior dining tables, wet bars, jacuzzis/pools, and helm chairs must retain exact placement and upholstery colour/stitching.
- **Hardware & Safety Rails:** Stainless steel stanchions, pulpits, handrails, glass bulwarks, cleats, and winches must remain rigid and geometrically solid (no melting or disappearing thin rails).

### 2.6 Interior Architecture & Finishes
- **Spatial Layout:** Exact bulkhead geometry, ceiling coffer heights, cabinetry proportions, and doorway alignments.
- **Materials & Joinery:** Wood grain orientation and tone (e.g., matte walnut, high-gloss ebony, bleached oak), marble/stone veining patterns, leather panelling, and fabric textures.
- **Lighting Fixtures:** Recessed downlights, LED cove strips, and decorative sconces must maintain fixed positions and consistent colour temperature (`K`).

### 2.7 Branding, Nameboards & Flags
- **Vessel Name & Builder Insignia:** If visible in the reference, builder logos or yacht nameboards must never gibberish-morph into illegible AI text.
- **Ensigns & Pennants:** Flags may exhibit subtle natural wind flutter only if their colour pattern and attachment point remain faithful to the source.

---

## 3. Known High-Risk AI Failure Modes to Prevent

Operators and QA reviewers must specifically watch for and reject these common I2V identity violations:

1. **Parallax Hallucination:** When a camera pans or pushes in, the AI invents non-existent windows, extra radar domes, or deformed bow rails at the edges of objects.
2. **Thin-Feature Melting:** Stainless steel railings, whip antennas, and window mullions dissolving, waving like noodles, or snapping in and out of existence.
3. **Hull Elongation / Compression:** Forward motion prompts causing the bow or stern to stretch telescopically while the camera moves.
4. **Reflection Drift:** Specular highlights on dark hull paint detaching from the hull geometry and sliding unnaturally across the vessel surface.

---

## 4. Operational Mitigation Rules

- **Minimal Camera Excursion:** Restrict I2V camera movement amplitude so the model never has to extrapolate unseen sides of the yacht.
- **Source-Locked Keyframes:** Always drive I2V generation from an approved, high-resolution keyframe (`IMG-S<SS>-<VV>`) derived directly from an authentic yacht reference (`REF-<NNN>`).
- **Mandatory Overlay Verification:** Before marking any prepared image `APPROVED`, compare it directly against its parent reference image at 100% zoom to confirm zero structural drift.
