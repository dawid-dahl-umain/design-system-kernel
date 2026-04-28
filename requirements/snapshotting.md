# Snapshotting

Stage 1 of the DSK pipeline. An engine reads the source of truth and writes a `DesignSystemSnapshot` (see [types.md](types.md)) into the company zone. Stage 2 (Build) then takes that snapshot and produces the library pages; that step is described briefly at the end of this file.

Snapshotting is pluggable by engine. MVP ships with one engine only: `dsk:snapshot-ppt` for PowerPoint. Future engines (Keynote, Google Slides, Figma, design tokens) can be added without changing the kernel contract or the runtime.

An engine is a skill (`dsk:snapshot-<format>`) that the agent follows to read source files of one declared format and emit the `DesignSystemSnapshot`. Engines live in the kernel zone and are part of its portability. The manifest declares which engine handles which source: `engine: "ppt"` resolves to `dsk:snapshot-ppt`, `engine: "keynote"` to `dsk:snapshot-keynote`, and so on. If `engine` is omitted, the agent infers it from the file extension. Extraction is agentic; only schema validation is a deterministic script.

## Engine contract

Every engine, current or future, must emit two complementary outputs for each layout (and each example and each unparseable element):

1. **Structure.** The hard, parsed facts from the source format, stored as structured data (JSON). For PPT that means placeholder types and positions, master metadata, and so on. This is what the agent references precisely.
2. **Visuals.** Rendered images (PNG) of the actual layout, so the agent can see what it looks like, using whatever vision capability the underlying model provides. DSK does not dictate how the agent consumes these; it only guarantees they are present.

Structure-only or visuals-only output does not conform. Both are mandatory.

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

Extracts what the snapshot requires: layout catalog with placeholder metadata, filled example slides rendered as PNG, and a content catalog of tables, charts, diagrams, and similar elements found in the source.

Theme colors, fonts, logos, embedded images, and reusable brand components are deliberately not extracted into `snapshot.json`. Those are handled by the host AI Design Tool's native source-file support, the host's own design-system feature, or by the agent reading the declared source directly at runtime.

Elements the engine cannot cleanly parse (SmartArt, custom shapes, non-standard layouts) are rendered as PNG into `assets/fallback-screenshots/` and recorded in the snapshot's `fallbacks` array with a reason. System degrades rather than fails.

## Implementation: agentic, not scripted

The "engine" is not a monolithic Python program. Each engine is its own skill (e.g. `dsk:snapshot-ppt` for PowerPoint). The agent reads the appropriate engine skill's `SKILL.md` and uses its native tools (Python with python-pptx, bash with LibreOffice headless for the PPT engine) to perform the extraction. This keeps the kernel small, leverages the agent's existing capabilities, and aligns with principle 7 (behavior-level, not implementation).

The one part that ships as a deterministic script is `validate_snapshot.py`, which checks the produced snapshot against the schema (every screenshot path resolves, every `Example.layout_id` resolves to a `Layout.id`, no orphan assets). Validation must be reproducible; extraction can be agentic.

The validator and its Pydantic schema (`models.py`) live at plugin level in `dsk/lib/snapshot/`, not inside any one engine skill, because the `DesignSystemSnapshot` shape is engine-agnostic. Every engine invokes the same shared validator after extraction; no engine duplicates the schema.

This pattern applies to future engines too: they describe what to extract via SKILL.md, the agent drives the work, and the shared validator enforces the contract.

## Build (stage 2)

Once snapshotting is done, the Build stage takes over. The agent reads the snapshot and the kernel briefs, then produces the library pages (welcome page, layouts page, examples page, content gallery). Build is agentic and behavior-level (per principle 7); two runs may produce different rendered output while satisfying the same brief contract.

Snapshot is data; Build is visual. Keep them separate in your head.

---

[← Back to overview](../REQUIREMENTS.md)
