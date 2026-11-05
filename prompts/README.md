# Prompt Engineering Foundation & Architecture

**Repository:** `E:\Yacht-AI-Video-Production`  
**Document Path:** `prompts\README.md`  
**Version:** 1.0.0

---

## 1. Purpose

This directory contains the reusable, provider-agnostic prompt engineering framework for the **Yacht AI Video Production System**.

To prevent AI hallucination and ensure repeatable cinematic results across different external image and video generation models, every prompt in this system is decomposed into four strictly separated layers:

1. **Preservation & Source-Fidelity Constraints** (What must NOT change from the source image).
2. **Creative & Cinematic Direction** (Camera movement, framing, and natural environmental motion).
3. **Negative Constraints** (Explicit exclusions of morphing, flicker, bad physics, and artifacts).
4. **Technical Generation Settings & Parameter Records** (Provider-neutral model controls, seeds, motion scales, and version history).

---

## 2. Directory Structure

- [`image-enhancement\image-enhancement-guide.md`](image-enhancement/image-enhancement-guide.md)  
  Reusable patterns and constraints for preparing, upscaling, outpainting (if required for 16:9 framing), and conditioning source reference photos into `IMAGES_APPROVED` keyframes without altering vessel identity.
- [`image-to-video\image-to-video-guide.md`](image-to-video/image-to-video-guide.md)  
  Reusable prompt structures for Exterior, Deck, and Interior I2V shots covering source-image fidelity, yacht identity lock, cinematic composition, stabilized camera motion, natural water/lighting physics, parameter records, and version history.
- [`negative-constraints\negative-constraints-library.md`](negative-constraints/negative-constraints-library.md)  
  Standardized negative prompt modules categorized by vessel geometry, marine water physics, temporal stability, and interior realism.

---

## 3. Provider-Agnostic Design Principles

1. **No Provider Lock-In:** Prompt templates do not hardcode proprietary syntax for any single vendor. Model-specific flags or sliders are recorded strictly inside the **Technical Generation Settings** block of a production's prompt record (`productions\<ID>\prompts\PRM-S<SS>-v<VV>.md`).
2. **Image-First Anchoring:** In Image-to-Video (I2V) workflows, the approved input keyframe (`IMG-S<SS>-v<VV>`) already contains the visual appearance of the yacht. Text prompts must focus on **preserving that exact image** and describing **only the desired camera trajectory and subtle environmental motion**, rather than re-describing generic yacht features that could trigger appearance drift.
3. **Version Control & Lineage:** Every modification to prompt wording, negative constraints, or motion parameters increments the prompt version (`v01` -> `v02`) and is logged in the prompt's version history table.
