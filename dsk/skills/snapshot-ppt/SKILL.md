---
description: Stage 1 of the DSK pipeline, PowerPoint engine. Extract a DesignSystemSnapshot from a PowerPoint master (layouts, examples, content catalog, fallbacks). Use for /dsk:snapshot-ppt, when the manifest declares a PPT source, or whenever the snapshot needs to be (re)created from a PowerPoint file. Uses python-pptx and LibreOffice headless via tool calls. Other source formats use their own snapshot-* engine skill.
allowed-tools: Bash(python3 *) Bash(pip *) Bash(libreoffice *)
---

# DSK Snapshot (PowerPoint) — Stage 1

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

Extract a `DesignSystemSnapshot` from the source PPT. The "engine" is you, the agent, using your tools — there is no monolithic engine script. This is the PowerPoint engine; other source formats use their own `dsk:snapshot-<format>` engine skill.

## How to run extraction (read this first)

Extraction is **agentic, not scripted.** Run each step of the recipe through tool calls — Bash with inline Python (`python3 -c '...'` or `python3 <<'EOF' ... EOF`) or short standalone invocations. The recipe below is a checklist for you to execute step by step, not a program for you to compile into a single file.

**Do not write a Python file (e.g. `.snapshot-extract.py`, `extract.py`, `dsk-engine.py`) into the project folder.** The company zone is reserved for snapshot artifacts and user content, not for extraction scripts. Principle 2 (everything DSK generates is regenerable from source + manifest) explicitly excludes accumulating extraction code as project clutter.

If a step's logic is genuinely too complex to fit in an inline tool call, write a temporary helper to `/tmp/` (not the project folder), invoke it, and let it disappear with normal temp cleanup. The project folder should never contain a Python file you authored as part of running the snapshot.

Why this matters:
- **Adaptability.** Inline tool calls let you adjust to per-source quirks (an unusual placeholder type, a corrupt media file, a layout with no name) by reasoning at each step. A monolithic script captures one specific implementation and fails opaquely on edge cases.
- **Cleanliness.** Re-running snapshot from a clean filesystem produces only the snapshot artifact — no leftover `.snapshot-extract.py` from a previous run.
- **Principle alignment.** "Behavior level, not implementation" (principle 7) means the SKILL.md describes what to convey; you decide step-by-step how to render it. A single saved program is the opposite of behavior-level execution.

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

## Before extraction: large-source guard

Before starting any extraction step, check the source file's size. If it is **larger than 100 MB**, pause and ask the user for explicit consent before proceeding. Most corporate PPT templates are 10-50 MB; above 100 MB is unusual enough that the user might not realise the disk and time cost they are authorising, and principle 8 (destructive or large changes require explicit consent) applies.

When the threshold is exceeded:

1. **Compute the relevant numbers without extracting.** Read the source's stat for the file size. Open the PPTX as a zip and sum the sizes of every entry under `ppt/media/` to get the source-media subtotal. Both are cheap reads; no extraction needed.

2. **Surface this to the user, in plain English.** Suggested phrasing:

   > "Your source file is 320 MB, which is larger than typical (most are under 50 MB). Snapshotting will produce roughly 380-450 MB of files in `snapshot/` and may take 5-10 minutes. About 240 MB of that is embedded brand artwork (logos, photos, decorative shapes) that gets extracted to `snapshot/assets/source-media/` for the build stage to use as a brand-asset fallback when your host AI Design Tool does not expose the company's brand directly. How would you like to proceed?"
   >
   > - **Proceed with full extraction** (everything: structured data, screenshots, source media)
   > - **Proceed but skip source-media** (structured data and screenshots only, ~240 MB smaller and faster; choose this if your host already exposes the company's brand assets, or if you are iterating on layouts and don't need the artwork yet)
   > - **Cancel**

3. **Wait for an explicit choice. Don't proceed silently.** If the user picks "skip source-media," still extract everything else, but emit `source_media: []` and either skip creating `assets/source-media/` or leave it empty. If the user picks "cancel," stop and don't write anything.

4. **Estimates can be rough.** A factor-of-two error band on size and time estimates is fine; the goal is informed consent, not pinpoint accuracy. Round to the nearest whole MB and the nearest minute.

Below 100 MB, proceed silently as normal — no pause, no prompt.

## What to extract

### Canvas dimensions

- Read slide width and height via python-pptx (`presentation.slide_width`, `presentation.slide_height`, both EMU integers sourced from `presentation.xml`'s `<p:sldSz cx="..." cy="..."/>`).
- Record at the snapshot's top level: `canvas: { "width": <slide_width>, "height": <slide_height>, "unit": "emu" }`.
- The build stage uses this to set the slide aspect ratio for HTML rendering. Without it, build has to guess from screenshot pixel dimensions, which is unreliable (LibreOffice's PNG export size is not authoritative). The engine knows these values anyway because it needs them to compute the fractional placeholder positions on `Rect`.

### Layouts (every layout in the slide master)

- Stable id (slugify the layout name; on collision, append index suffix like `title-slide-2`).
- Name and placeholder positions as fractions 0..1 of layout width and height (convert from EMU using the canvas dimensions above).
- Placeholder `type` strings. Use lowercase with hyphens for compound terms.

  **Recommended vocabulary** (prefer these when python-pptx's `PP_PLACEHOLDER` enum maps cleanly; coin a new short hyphenated term only when nothing here fits):

  - **Titles:** `title`, `center-title`, `subtitle`
  - **Text:** `body`, `header`, `footer`
  - **Specialized content:** `picture`, `chart`, `table`, `diagram`, `media`
  - **Generic content:** `object` (when the slot is unspecialized; compose decides what to fill it with)
  - **Page metadata:** `slide-number`, `date`

  The list is recommended, not exhaustive or schema-enforced. Cross-engine: future engines (Keynote, Google Slides, Figma) should reuse these terms wherever the concept maps, and coin new terms only for genuinely engine-specific roles. Consistency within a snapshot matters more than cross-snapshot alignment.
- A PNG screenshot of the layout, rendered with as much of the layout's actual visual character as the source carries (background fills, decorative shapes, brand marks, image regions, photographic backgrounds). The recipe below preserves master inheritance and avoids the common failure modes (empty picture placeholders, lost master imagery, lost theme decoration). Save each into `assets/layout-screenshots/<id>.png`.

  **Specimen rendering recipe — follow this exactly.** Past runs that improvised this step produced screenshots stripped of the layout's image character (empty cream boxes where photographs should be, missing background photos, vanished decorative imagery). The reason was almost always one of: starting from a fresh `Presentation()` instead of the source; not pre-filling picture placeholders; relying on LibreOffice to inherit master imagery through a clean PPTX round-trip. The recipe below addresses each:

  1. **Duplicate the source PPTX into a temp working file** with `shutil.copy(source, temp)`. Do not start from `Presentation()` — a fresh document does not carry the source's theme parts, embedded media, or master XML, and master-image inheritance is unreliable in the round-trip.

  2. **Open the temp file with python-pptx and strip every existing slide.** For each slide id in `prs.slides._sldIdLst`, you must do **both** steps in this order: first drop the relationship to remove the slide part from the zip, then remove the `<p:sldId>` from the id list. Skipping the `drop_rel` step leaves orphan slide parts in the package that cause `UserWarning: Duplicate name: 'ppt/slides/slide1.xml'` on save and break soffice's PNG rendering — verified during testing. Concretely:

     ```python
     sld_id_lst = prs.slides._sldIdLst
     for sld_id in list(sld_id_lst):
         rId = sld_id.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
         prs.part.drop_rel(rId)
         sld_id_lst.remove(sld_id)
     ```

     The masters, layouts, themes, and embedded media all stay intact through this — `drop_rel` only removes the slide-level parts, not the layout/master/theme parts the slides referenced.

  3. **Generate a small grayscale stub PNG once** (e.g. `tmp/gray-stub.png`, 1×1 or larger, RGB around `(200, 200, 200)`). Pillow is already a transitive dependency of python-pptx, so use it; no extra install. This stub will fill picture placeholders so they render visibly.

  4. **For each `layout` in `prs.slide_layouts`, append a specimen slide** via `prs.slides.add_slide(layout)`. Then, for every placeholder on the new slide, populate it according to its type so it renders something:
     - **Text-bearing placeholders** (TITLE, CENTER_TITLE, SUBTITLE, BODY, HEADER, FOOTER, SLIDE_NUMBER, DATE): set `.text` to a neutral marker like `[TITLE]`, `[BODY]`, `[FOOTER]`. Skip if `.has_text_frame` is False.
     - **Picture and object placeholders** (PICTURE, OBJECT, CHART, TABLE, MEDIA, CLIP_ART, DIAGRAM, BITMAP): call `placeholder.insert_picture(gray_stub_png)`. Without this, picture placeholders render as empty space in a fresh slide and the layout's image character is lost.
     - Track the order of appended slides so you can map output PNGs back to layout ids.

  5. **Save the temp PPTX**, then convert with LibreOffice headless **at 1920×1080**:

     ```bash
     soffice --headless \
       --convert-to 'png:impress_png_Export:{"PixelWidth":{"type":"long","value":"1920"},"PixelHeight":{"type":"long","value":"1080"}}' \
       --outdir <out> <temp.pptx>
     ```

     LibreOffice writes one PNG per slide, named by index; rename each into `snapshot/assets/layout-screenshots/<layout-id>.png` per the order you appended. The 1920×1080 setting is intentional: LibreOffice's default is 1280×720, which downsamples photographic master content (e.g. brand decorative shapes, background imagery) to the point of visible mush. Full HD roughly doubles the working pixels with manageable file-size growth (solid-fill layouts stay ~15-25 KB; image-heavy layouts land around 1-1.5 MB). Same filter applies to example screenshots and content-screenshots; keep the resolution consistent across all asset folders.

  6. **Spot-check the output before claiming success.** Open at least three layout screenshots covering different visual treatments — one with a solid fill, one with photographic or gradient imagery, one with decorative shapes. If a screenshot is visibly impoverished compared to the source's appearance in a real PowerPoint or Keynote viewer (empty boxes where the source has photos, missing background imagery, missing decorative elements), the recipe failed for that layout. Fix and re-run before reporting success.

  **LibreOffice fidelity ceiling.** Even with the recipe followed correctly, LibreOffice headless has known limits on a small set of effects: complex gradient fills, certain theme-driven font substitutions (the company's brand fonts are usually unavailable), some custom shape effects, and a handful of non-standard embedded media formats. For these residual gaps, capture what you can and note the gap in the layout's `notes` field if it would mislead the build agent (e.g. `notes: "Source has a subtle radial gradient behind the title not visible in this render; treat as solid cream."`). LibreOffice is the cross-platform default; future engines on platforms with native PowerPoint or Keynote available may render at higher fidelity.
- Optional `notes` with usage guidance. Pull from the layout's speaker-notes part if PPT carries one; otherwise infer from placeholder types and the visual, or ask the user in ambiguous cases.

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

### Source media (raw assets extracted from the PPTX)

Every PPTX is a zip; embedded brand artwork (logos, decorative shapes, photographic backgrounds, custom fonts) lives at full source resolution under `ppt/media/`. These assets are valuable for the build stage when the host AI Design Tool does not expose the company's brand primitives directly: they let build use real source artwork rather than working from downsampled screenshots. Hosts that do expose brand primitives can ignore this tier.

**Extract everything in `ppt/media/`** into `snapshot/assets/source-media/`, preserving original filenames (the filename, e.g. `image9.png`, is the relationship target referenced by `r:embed r:id="rIdN"` throughout the source XML; preserving it keeps traceability intact).

**If the source has no embedded media** (no `ppt/media/` directory in the zip, or the directory is empty), this is a normal case: not every PPT carries decorative imagery, brand artwork, or embedded fonts. Do not error, do not warn, do not invent placeholder assets. Set `source_media: []` in the snapshot, and either skip creating `assets/source-media/` or leave it empty. The build stage handles the empty case gracefully (it falls through to asking the user when no level 1–3 source has what a rendition needs).

```python
import zipfile, shutil
from pathlib import Path
SRC = Path("source/Acme-Master.pptx")
OUT = Path("snapshot/assets/source-media")
OUT.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(SRC) as z:
    for name in z.namelist():
        if name.startswith("ppt/media/") and not name.endswith("/"):
            target = OUT / Path(name).name
            with z.open(name) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
```

For each extracted asset, append an entry to the snapshot's `source_media` array:

- **`id`**: stable id derived from the filename (e.g. `image9` from `image9.png`). Slugify if the source uses unusual characters.
- **`path`**: relative to `snapshot.json`, e.g. `assets/source-media/image9.png`.
- **`kind`** (recommended): one of `raster` (PNG, JPEG, GIF, WebP), `vector` (SVG, EMF, WMF), `font` (TTF, OTF, WOFF), `media` (MP3, WAV, MP4, MOV). Determine from extension.
- **`source_ref`** (recommended): the original path inside the source, e.g. `ppt/media/image9.png`. Preserves traceability to the source format.
- **`role`** (optional, only when confident): one of `brand-mark`, `decorative`, `photographic`, `icon`, `background`. Determine by inspecting which slides/layouts/masters reference the image's `rId`. A small PNG with transparency referenced from the slide master and positioned near a corner is almost certainly a brand mark; an image referenced via `<p:bg><p:blipFill>` on a layout is a background. **If you cannot classify confidently, omit `role`** rather than guessing — the build agent can re-classify by inspection.
- **`appears_in`** (optional): list of layout/example/content ids that reference this asset. Useful for the build agent to know "this logo appears in every layout" vs "this image is specific to one example."
- **`notes`** (optional): anything the build agent should know that isn't captured by the structured fields.

Engine-agnostic shape: the same `SourceMedia` schema is what every engine emits (Keynote will extract from package internals, Figma will fetch image fills via API, Google Slides will resolve API-referenced images). Only the extraction differs.

**File-size note.** Extraction is roughly 1:1 with the source's embedded media. A PPTX with 30 MB of photography produces a ~30 MB `source-media/` folder. The user keeps `source/<file>.pptx` already, so no net duplication on the project's overall disk footprint, but the snapshot itself grows. Future versions may add a manifest opt-out (`extract_source_media: false`) if a project has reason to skip this.

## What to skip on purpose

The snapshot's structured JSON is intentionally slim. **Do not** record theme colors, font definitions, color palettes, or reusable component primitives as structured fields in `snapshot.json`. Those belong to the host AI Design Tool's design-system feature, or the agent reads them from the source directly at build time. Do not invent brand primitives if the host cannot provide them.

Note the deliberate split with the **Source media** section above: that section *does* extract embedded image and font binaries from the PPTX zip into `assets/source-media/`. Those are raw files for the build stage to use as a brand-asset fallback, not structured fields in the JSON. Extracting binary asset files: yes. Parsing theme XML to populate JSON fields: no.

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
