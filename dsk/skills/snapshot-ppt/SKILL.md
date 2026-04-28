---
description: Stage 1 of the DSK pipeline, PowerPoint engine. Extract a DesignSystemSnapshot from a PowerPoint master (layouts, examples, content catalog, fallbacks). Use for /dsk:snapshot-ppt, when the manifest declares a PPT source, or whenever the snapshot needs to be (re)created from a PowerPoint file. Uses python-pptx and LibreOffice headless via tool calls. Other source formats use their own snapshot-* engine skill.
allowed-tools: Bash(python3 *) Bash(pip *) Bash(libreoffice *)
---

# DSK Snapshot (PowerPoint) — Stage 1

Extract a `DesignSystemSnapshot` from the source PPT. The "engine" is you, the agent, using your tools — there is no monolithic engine script. This is the PowerPoint engine; other source formats use their own `dsk:snapshot-<format>` engine skill.

## Output you produce

You write everything into the **company zone** — the user's project folder, which is your current working directory. NOT into the plugin folder; the plugin (kernel zone) is a separate read-only location accessible via `${CLAUDE_PLUGIN_ROOT}`.

Inside the project, create a `snapshot/` subdirectory with the following layout:

```
<project-root>/
  snapshot/
    snapshot.json          # the structured snapshot
    assets/
      layout-screenshots/  # one PNG per layout in the master
      example-screenshots/ # one PNG per filled example slide
      content-screenshots/ # one PNG per catalogued content type
      fallback-screenshots/ # PNGs for elements you could not parse
```

**Two path forms — keep them straight:**

- **Disk paths** (where you actually save the file) are relative to the project root, e.g. `snapshot/assets/layout-screenshots/title-slide.png`.
- **JSON paths** (the `screenshot` string inside `snapshot.json`) are relative to `snapshot.json` itself, e.g. `assets/layout-screenshots/title-slide.png` (no leading `snapshot/`).

The validator joins the JSON path against the snapshot directory to resolve it on disk. In the rest of this SKILL.md, when you see a path like `assets/layout-screenshots/<id>.png`, that's the JSON form; the corresponding disk path is the same with `snapshot/` prefixed.

The formal shape of `snapshot.json` and all sub-types is the Pydantic schema in `${CLAUDE_PLUGIN_ROOT}/lib/snapshot/models.py`. Conform to it; the shared validator (`lib/snapshot/validate_snapshot.py`) enforces it.

## Inputs

- `manifest.yaml` at the project root — read for the source PPT path.
- The source PPT.

## Tools

- **python-pptx** for parsing PPTX layouts and slides. Install on first use if missing: `pip install python-pptx --quiet`.
- **pydantic** (v2) for the validation script's typed schema. Install on first use if missing: `pip install pydantic --quiet`.
- **LibreOffice headless** for rendering PNGs. Install via the system package manager if missing. Convert with `libreoffice --headless --convert-to png <file.pptx>`.

## What to extract

### Layouts (every layout in the slide master)

- Stable id (slugify the layout name; on collision, append index suffix like `title-slide-2`).
- Name, placeholder types, and placeholder positions as fractions 0..1 of layout width and height (convert from EMU).
- A PNG screenshot of the layout. PowerPoint slide layouts cannot be directly rendered by LibreOffice, and empty slides may export without visible placeholder structure. Generate a temporary PPTX containing one specimen slide per layout, using neutral placeholder labels or a lightweight visual overlay so the layout's regions are visible. Do not modify the source PPT and do not use invented customer content. Convert the temporary PPTX to PNGs via LibreOffice, then save each into `assets/layout-screenshots/<id>.png`.
- Optional `notes` with usage guidance you can infer from the placeholder types and the visual. (Or from the user if so explicitly provided, or if you ask them for help in ambiguous cases.)

### Examples (filled non-empty slides in the master)

- Stable id and reference to the `layout_id` it uses.
- A PNG screenshot of the slide via LibreOffice. Save into `assets/example-screenshots/<id>.png`.

### Content catalog (each distinct content type in the PPT)

- Tables, charts, diagrams, callouts, etc.
- Stable id; `type` label for the structural classifier. Use lowercase with hyphens for compound terms (e.g. `bar-chart`, not `BarChart` or `bar chart`).

  **Recommended vocabulary** (prefer these when one fits; coin a new short hyphenated term only when nothing in the list does):

  - **Tables:** `table`
  - **Charts:** `bar-chart`, `line-chart`, `pie-chart`, `scatter-chart`, `area-chart`, `bubble-chart`, `combo-chart`
  - **Diagrams:** `flowchart`, `org-chart`, `process-diagram`, `hierarchy-diagram`, `venn-diagram`, `swim-lane-diagram`
  - **Visual emphasis:** `callout`, `quote`, `metric`, `hero-metric`
  - **Lists & comparisons:** `list`, `numbered-list`, `comparison-matrix`, `feature-grid`
  - **Media:** `image`, `icon`, `map`, `timeline`

  The list is recommended, not exhaustive or schema-enforced. If the company's source uses something genuinely different (e.g. a sector-specific chart variant), coin a new short hyphenated term rather than force-fitting one above. Consistency within a snapshot matters more than cross-snapshot alignment.
- Optional `dof_level`: the minimum DoF level required to produce this item (`match`, `adapt`, `stretch`, `deviate`). Use `match` when the item is directly exemplified by the source. Use `adapt` or `stretch` only when the source clearly supports that liberty. Use `deviate` only to document a seen but disallowed edge case; the content gallery hides items above the company's ceiling.
- Optional `display_name`: the company's preferred human-readable name for this content type, when it has one (e.g. "Pulse Chart" for what is structurally a bubble-chart, or "ARR Growth Chart" for a specific bar-chart variant). Capture this when the source PPT, slide titles, or speaker notes reveal a company-specific name; if ambiguous, ask the user. Omit when the company has no special name and the structural `type` is sufficient.
- PNG screenshot of a representative slide containing the content type — whole slide, no cropping. Save into `assets/content-screenshots/<id>.png` and reference it as the primary `screenshot`.
- Optional `additional_screenshots`: a list of supplementary screenshot paths to capture alternate views of the same type (e.g. the same chart with and without a legend, or a sparse vs full table). Use only when one canonical view does not suffice. Save under the same `assets/content-screenshots/` directory.
- Optional `notes` if the construction rule isn't obvious from the screenshot (e.g. "stacked bars by segment, Y-axis starts at 0").

If a content type has structurally distinct variations the company uses (e.g. a metrics table and a comparison matrix), prefer modeling each as its own ContentItem with a distinct id. Use `additional_screenshots` only for alternate views of the same primitive, not for distinct variations.

### Fallbacks (elements you cannot cleanly parse)

- SmartArt, custom shapes, non-standard layouts.
- `source_ref` like `slide-12-shape-3`, PNG of the area in `assets/fallback-screenshots/`, and a `reason` explaining why the engine could not parse it.
- Degrade, don't skip silently.

## What to skip on purpose

Theme colors, fonts, logos, embedded images. These are delegated to the host AI Design Tool's native PPT support, the host's own design-system feature, or runtime reading of the source. The snapshot is intentionally slim and slide-specific. Do not extract what isn't required, and do not invent brand primitives if the host cannot provide them.

## After extraction

Run the shared snapshot validator against the produced JSON. The script lives in the plugin's shared library at `lib/snapshot/validate_snapshot.py` (engine-agnostic; all `dsk:snapshot-*` engines use it). Resolve its absolute path from `${CLAUDE_PLUGIN_ROOT}` (or the equivalent in your runtime) and invoke:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/lib/snapshot/validate_snapshot.py snapshot/snapshot.json
```

The validator checks: schema shape, every screenshot path resolves on disk, every `Example.layout_id` resolves to a `Layout.id`, no orphan assets. If validation fails, fix and re-run before reporting success.

After validation succeeds, write a marker file at `snapshot/.dsk-managed` with this single line of plain text:

```
DSK-managed. Generated by /dsk:snapshot-ppt (or the engine for the declared source); regenerable from source/ + manifest.yaml. Do not edit manually.
```

This signals to any agent or tool walking the filesystem (Claude Design, other plugins, DSK itself) that this directory is owned by DSK. Overwrite the marker on every re-snapshot.

## When to re-snapshot

- Source PPT mtime is newer than snapshot's `extracted_at`.
- User invoked `/dsk:sync`.
- Validation reported issues.

Re-snapshotting overwrites the snapshot. It never modifies the source (principle 1).
