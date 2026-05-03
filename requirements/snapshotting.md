# Snapshotting

Stage 1 of the DSK pipeline. An engine reads the source of truth and writes a `DesignSystemSnapshot` (see [types.md](types.md)) into the company zone. Stage 2 (Build) then takes that snapshot and produces the library pages; that step is described briefly at the end of this file.

Snapshotting is pluggable by engine. MVP ships with one engine only: `dsk:snapshot-ppt` for PowerPoint. Future engines (Keynote, Google Slides, Figma, design tokens) can be added without changing the kernel contract or the runtime.

An engine is a skill (`dsk:snapshot-<format>`) that the agent follows to read source files of one declared format and emit the `DesignSystemSnapshot`. Engines live in the kernel zone and are part of its portability. The manifest declares which engine handles which source: `engine: "ppt"` resolves to `dsk:snapshot-ppt`, `engine: "keynote"` to `dsk:snapshot-keynote`, and so on. If `engine` is omitted, the agent infers it from the file extension. Extraction is agentic; only schema validation is a deterministic script.

## Engine contract

Every engine, current or future, must emit two complementary outputs for each layout (and each example and each unparseable element):

1. **Structure.** The hard, parsed facts from the source format, stored as structured data (JSON). For PPT that means slide canvas dimensions, placeholder types and positions, master metadata, and so on. This is what the agent references precisely.
2. **Visuals.** Rendered images (PNG) of the actual layout, so the agent can see what it looks like, using whatever vision capability the underlying model provides. DSK does not dictate how the agent consumes these; it only guarantees they are present.

Structure-only or visuals-only output does not conform. Both are mandatory.

### Pre-flight size guard

Every engine must check the source file's size before starting extraction. If the source is **larger than 100 MB**, the engine pauses and surfaces to the user, in plain English: the source's size, an upper-bound estimate of embedded media that could land in `source-media/` (cheap to compute from the source format's directory listing; the actual extraction is filtered to design-system-layer references and is usually a fraction of that), a rough estimate of total snapshot size and runtime, and three options — proceed full, proceed but skip source-media, or cancel. Below the threshold, extraction proceeds silently as normal. This honours principle 8 (destructive or large changes require explicit consent) for the case of large source files where the user might not realise the disk and time cost they're authorising. The 100 MB threshold is shared across engines so the user experience stays consistent regardless of source format.

## The DesignSystemSnapshot

The snapshot is the typed output of any engine. One `snapshot.json` holds the structured facts; a sibling `assets/` directory holds binaries referenced by path. For MVP the snapshot is also the compiled design system the agent reads at runtime (if multi-engine support lands later, a small compile step will merge multiple snapshots into one).

The snapshot is deliberately slim: only DSK-essential slide information (layouts, examples, content catalog, fallbacks). Theme colors, fonts, logos, embedded images, and reusable brand components are brand primitives, not DSK's slide-structure layer. They are delegated to the host AI Design Tool's own design-system feature, the host's native PPT extraction, or direct runtime reading of the source file. DSK does not duplicate that layer.

Runtime expectation: when composing or building, the agent combines DSK's snapshot with brand primitives available from the host or source files. If those primitives are unavailable, the agent must ask the user to provide or connect them rather than inventing substitutes.

Directory layout in the company zone:

```
snapshot/
  snapshot.json
  assets/
    layout-screenshots/       # PNG renders of each source layout
    example-screenshots/      # PNG renders of filled example slides
    content-screenshots/      # PNG renders of catalogued content types
    fallback-screenshots/     # PNG renders of unparseable elements
```

Stable id convention: slugify the source layout name (`Title Slide` → `title-slide`); on collision, append index suffix (`title-slide-2`). The id appears in both the JSON entry and the screenshot filename so structure and visual can be eyeball-matched without opening the file.

Formal shape and JSON example: see [types.md](types.md).

## PPT Snapshot Engine (`dsk:snapshot-ppt`, MVP)

Extracts what the snapshot requires: slide canvas dimensions, layout catalog with placeholder metadata, filled example slides rendered as PNG, a content catalog of tables, charts, diagrams, and similar elements, and raw source media (embedded images, decorative artwork, fonts) under `assets/source-media/` for the build stage to use as a brand-asset fallback.

Theme colors, fonts as styling tokens, and reusable brand components remain delegated to the host AI Design Tool's design-system feature or to the agent reading the declared source directly. The snapshot itself stays slim on the structured-data side; only the actual asset binaries are physically copied, because they are the one thing build cannot reconstruct from screenshots when the host has no brand-asset surface.

Elements the engine cannot cleanly parse (SmartArt, custom shapes, non-standard layouts) are rendered as PNG into `assets/fallback-screenshots/` and recorded in the snapshot's `fallbacks` array with a reason. System degrades rather than fails.

Layout screenshots are produced by appending one specimen slide per layout to a copy of the source PPTX (preserving theme, masters, and embedded media), pre-filling picture placeholders with a neutral grayscale stub so they render visibly, and converting via LibreOffice headless. The recipe is specified in `dsk/skills/snapshot-ppt/SKILL.md`. LibreOffice has a known fidelity ceiling on certain effects (complex gradients, custom fonts, some theme decoration); residual gaps are recorded in the affected layout's `notes` field rather than silently absorbed.

## Implementation: agentic, not scripted

The "engine" is not a monolithic Python program. Each engine is its own skill (e.g. `dsk:snapshot-ppt` for PowerPoint). The agent reads the appropriate engine skill's `SKILL.md` and uses its native tools (Python with python-pptx, bash with LibreOffice headless for the PPT engine) to perform the extraction. This keeps the kernel small, leverages the agent's existing capabilities, and aligns with principle 7 (behavior-level, not implementation).

The one part that ships as a deterministic script is `validate_snapshot.py`, which checks the produced snapshot against the schema (every screenshot path resolves, every `Example.layout_id` resolves to a `Layout.id`, no orphan assets). Validation must be reproducible; extraction can be agentic.

The validator and its Pydantic schema (`models.py`) live at plugin level in `dsk/lib/snapshot/`, not inside any one engine skill, because the `DesignSystemSnapshot` shape is engine-agnostic. Every engine invokes the same shared validator after extraction; no engine duplicates the schema.

This pattern applies to future engines too: they describe what to extract via SKILL.md, the agent drives the work, and the shared validator enforces the contract.

## Build and verify (phases 2 and 3)

Once snapshotting is done, the Build phase takes over. The agent reads the snapshot and the kernel briefs and produces renditions plus the library pages (welcome page, layouts page, examples page, content gallery). Build is agentic and behavior-level (per principle 7); two runs may produce different rendered output while satisfying the same brief contract.

The **Verify pass** is implemented as its own skill, `dsk:align`, which `dsk:build` invokes as its closing stage. Every rendition tile is held next to its source screenshot and confirmed to match on both axes — *structure* (regions, primitives, spatial relationships) and *character* (palette, key imagery, brand marks, decorative motifs, overall feel). Anything that diverges on either axis is aligned in place before the pass is declared done. `dsk:setup` and `dsk:sync` invoke `dsk:align` again as a closing pass after build returns: the additional invocation is mechanical, not duplicative — a skill-boundary call gives the agent a fresh attention reset that next-step-in-a-list framing has, in practice, sometimes failed to enforce. Users can also invoke `/dsk:align` directly for a thorough sweep over the existing library without rebuilding from scratch. See `dsk/skills/align/SKILL.md` for the per-rendition mechanics and `dsk/skills/context/lifecycles.md` for the phase's place in the overall flow.

Snapshot is data; Build is visual; Verify is accountability. Keep the three separate in your head.

---

[← Back to overview](../REQUIREMENTS.md)
