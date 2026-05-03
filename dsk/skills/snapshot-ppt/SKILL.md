---
description: Stage 1 of the DSK pipeline, PowerPoint engine. Extract a DesignSystemSnapshot from a PowerPoint master (layouts, examples, content catalog, fallbacks). Use for /dsk:snapshot-ppt, when the manifest declares a PPT source, or whenever the snapshot needs to be (re)created from a PowerPoint file. Uses python-pptx and LibreOffice headless via tool calls. Other source formats use their own snapshot-* engine skill.
allowed-tools: Bash(python3 *) Bash(pip *) Bash(libreoffice *)
---

# DSK Snapshot (PowerPoint) — Stage 1

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

Extract a `DesignSystemSnapshot` from the source PPT. The "engine" is you, the agent, using your tools — there is no monolithic engine script. This is the PowerPoint engine; other source formats use their own `dsk:snapshot-<format>` engine skill.

## How to run extraction

Extraction is agentic, not scripted. Work step by step through your tool calls and reason between steps — that's how you adapt to per-source quirks (an unusual placeholder type, a corrupt media file, a layout with no name) instead of failing opaquely on edge cases.

**Any extraction code you write must be ephemeral.** It should not persist in the project folder after the snapshot is complete. The company zone is reserved for the snapshot artifact and the user's own content; principle 2 ("everything DSK generates is regenerable from source + manifest") doesn't license accumulating extraction code there. If a piece of logic is too long for a single tool call, place the helper somewhere ephemeral (your runtime's temp area is the natural choice) and let it disappear with normal cleanup.

Re-running snapshot from a clean filesystem should produce only the snapshot artifact — nothing else.

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

Most corporate PPT templates are 10-50 MB. When a source is markedly larger than that — roughly 100 MB and up — pause and get explicit consent before doing the work, because the disk and time cost may not be what the user expects. This is principle 8 ("destructive or large changes require explicit consent") applied to the size axis.

Surface, in plain English: the source's actual size, the embedded-media subtotal (from the source's directory listing — cheap to compute without extracting; an upper bound, since the actual `source-media/` extraction is filtered to design-system-layer references and is usually a fraction of the listing), and a rough estimate of total snapshot size and runtime. Then offer a choice. The natural three are: proceed with full extraction, proceed but skip source-media (useful when the host already exposes brand assets), or cancel. Wait for an explicit answer before proceeding. If the user opts to skip source-media, still extract everything else and leave `source_media` empty in the snapshot.

Estimates can be rough — factor-of-two on size and time is fine; the goal is informed consent, not pinpoint accuracy. Below the threshold, proceed silently as normal.

## What to extract

### Canvas dimensions

- Read the source's slide width and height (in PPTX they live in `presentation.xml` under `<p:sldSz cx="..." cy="..."/>` and are EMU integers; python-pptx exposes them on the `Presentation` object).
- Record at the snapshot's top level as `canvas: { "width": <w>, "height": <h>, "unit": "emu" }`.
- The build stage uses this to set the slide aspect ratio for HTML rendering. Without it, build has to guess from screenshot pixel dimensions, which is unreliable. The engine knows these values anyway because it needs them to compute the fractional placeholder positions on `Rect`.

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
- A PNG screenshot of the layout, rendered at **1920×1080** (LibreOffice's default of 1280×720 downsamples photographic master content to visible mush; HD roughly doubles working pixels with manageable file-size growth — solid-fill layouts stay ~15-25 KB, image-heavy ones around 1-1.5 MB). The screenshot must convey the layout's actual visual character — background fills, decorative shapes, brand marks, image regions, photographic backgrounds — not a stripped wireframe. Save each into `assets/layout-screenshots/<id>.png`. Use the same resolution for example and content screenshots so the asset folder is consistent.

  **What the screenshot must convey** is the contract; how you produce it is your call. That said, the failure modes below have come up repeatedly when this step is improvised, so keep them in mind:

  - **Empty picture placeholders.** A specimen slide created from a layout has the picture-placeholder geometry but no image content; the rendered PNG shows a hollow rectangle where the source has imagery. Mitigation: fill picture, object, chart, table, media, clip-art, diagram, and bitmap placeholders with a small neutral grayscale stub image (around RGB 200,200,200) before rendering, so the slot reads as an image region. Pillow comes along with python-pptx for free.
  - **Lost master imagery from a fresh-document round-trip.** Building a PPTX from `Presentation()` and pulling in the source's layouts loses master-level decorative imagery (brand artwork, photographic backgrounds, decorative graphics applied at the master level). Mitigation: start from a copy of the source PPTX so its theme parts, embedded media, and master XML stay intact; the specimen slides you append inherit cleanly from there.
  - **Orphan slide parts after stripping.** When you remove the source's existing slides from the copy so only your specimen slides render, you have to drop the slide *parts* from the package, not just the slide-id list. Stripping only the id list leaves orphan slide parts that cause `UserWarning: Duplicate name: 'ppt/slides/slide1.xml'` on save and break LibreOffice's PNG rendering. Both removals together (relationship/part dropped, then id-list entry removed) is the clean version. Verified against a real source. Check python-pptx's current API for the appropriate method names.
  - **Specimen-slide order vs layout id.** Track which appended slide corresponds to which layout id so you can name the output PNGs correctly when LibreOffice writes one per slide.
  - **Examples and layouts in one render pass.** Some agents have found it cleaner to keep the source's existing slides AND append the specimens, rendering all of them in one LibreOffice pass — the first N PNGs are then your example screenshots and the rest are your layout screenshots. That's a fine alternative to "strip then append," and it sidesteps the orphan-parts problem. Either approach is valid as long as the output meets the contract.

  Text-bearing placeholders on a specimen slide can carry a neutral marker (e.g. `[TITLE]`, `[BODY]`, `[FOOTER]`) so the layout's text regions remain visible. Don't invent customer content.

  **Spot-check before reporting success.** Open at least three layout screenshots covering different visual treatments (solid fill, photographic or gradient imagery, decorative shapes). If any is visibly impoverished compared to the source's appearance in a real PowerPoint or Keynote viewer — empty boxes where the source has photos, missing background imagery, missing decorative elements — fix and re-run.

  **LibreOffice fidelity ceiling.** Even with the failure modes above handled, LibreOffice headless has known limits on a small set of effects: complex gradient fills, theme-driven font substitution (the company's brand fonts are usually unavailable on the rendering machine), some custom shape effects, and a handful of non-standard embedded media formats. For residual gaps, capture what you can and note the gap in the layout's `notes` field if it would mislead the build agent (e.g. *"Source has a subtle radial gradient behind the title not visible in this render; treat as solid cream."*). LibreOffice is the cross-platform default; future engines on platforms with native PowerPoint or Keynote available may render at higher fidelity.
- Optional `notes` with usage guidance. Pull from the layout's speaker-notes part if PPT carries one; otherwise infer from placeholder types and the visual, or ask the user in ambiguous cases.

### Examples (filled non-empty slides in the master)

- Stable id and reference to the `layout_id` it uses.
- A PNG screenshot of the slide via LibreOffice. Save into `assets/example-screenshots/<id>.png`.

### Content catalog (each distinct content type in the PPT)

- Tables, charts, diagrams, callouts, etc.
- **Classify by what the slide actually shows, not by its embedded XML primitive.** Open the slide visually (or render it as the screenshot below and look at it) and describe the slide's overall composition before assigning a `type`. python-pptx will report XML-level facts ("this slide contains a `chart` element of subtype `column_stacked`"), but a slide whose XML reports a stacked column chart can in fact be a multi-region comparison dashboard with that chart as one tile inside it. In that case the right `type` is the dashboard's composition (e.g. `comparison-matrix` or a coined term like `regional-dashboard`), not `bar-chart`. The XML primitive is a hint; the slide's visual structure is the truth. If unsure, prefer the more compositional term over the embedded-element term — build can render the dashboard with mini charts inside, but cannot reconstruct a dashboard from a `bar-chart` label.
- Stable id; `type` label for the structural classifier. Use lowercase with hyphens for compound terms (e.g. `bar-chart`, not `BarChart` or `bar chart`).

  **Recommended vocabulary** (prefer these when one fits; coin a new short hyphenated term only when nothing in the list does):

  - **Tables:** `table`
  - **Charts:** `bar-chart`, `line-chart`, `pie-chart`, `scatter-chart`, `area-chart`, `bubble-chart`, `combo-chart`
  - **Diagrams:** `flowchart`, `org-chart`, `process-diagram`, `hierarchy-diagram`, `venn-diagram`, `swim-lane-diagram`
  - **Visual emphasis:** `callout`, `quote`, `metric`, `hero-metric`
  - **Lists & comparisons:** `list`, `numbered-list`, `comparison-matrix`, `feature-grid`
  - **Media:** `image`, `icon`, `map`, `timeline`

  The list is recommended, not exhaustive or schema-enforced. If the company's source uses something genuinely different (e.g. a sector-specific chart variant), coin a new short hyphenated term rather than force-fitting one above. Consistency within a snapshot matters more than cross-snapshot alignment.
- Optional `dof_level`: the minimum DoF level required to produce this item (`match`, `adapt`, `stretch`, `deviate`). **Do not auto-set `match` for everything sourced from the deck** — the user-facing translation is "exact use of the source," which becomes a lie when the build-stage rendition is a structural reconstruction with inferred or invented data. Use `match` only when the slide's content type is structurally unambiguous (a single dominant primitive filling the slide, where a faithful rendition can plausibly replicate the source's structure end-to-end). For multi-region slides, mixed compositions, or anything where the rendition is likely to be a sympathetic stand-in, omit `dof_level` rather than claiming `match`. Use `adapt` or `stretch` only when the source clearly supports that liberty. Use `deviate` only to document a seen but disallowed edge case; the content gallery hides items above the company's ceiling.
- Optional `display_name`: the company's preferred human-readable name for this content type, when it has one (e.g. "Pulse Chart" for what is structurally a bubble-chart, or "ARR Growth Chart" for a specific bar-chart variant). Capture this when the source PPT, slide titles, or speaker notes reveal a company-specific name; if ambiguous, ask the user. Omit when the company has no special name and the structural `type` is sufficient.
- PNG screenshot of a representative slide containing the content type — whole slide, no cropping. Save into `assets/content-screenshots/<id>.png` and reference it as the primary `screenshot`.
- Optional `additional_screenshots`: a list of supplementary screenshot paths to capture alternate views of the same type (e.g. the same chart with and without a legend, or a sparse vs full table). Use only when one canonical view does not suffice. Save under the same `assets/content-screenshots/` directory.
- Optional `notes` describing the slide's overall composition in plain English when it isn't obvious from the screenshot alone. Bias toward the slide's macro-structure (regions, columns, grids, embedded charts vs. surrounding prose), not just the central primitive's micro-rules. Examples: *"five-metric four-region dashboard: rows are metrics, columns are regions, the financial-results row contains mini stacked-column charts inline next to short prose"*; *"single stacked-bar chart filling most of the slide; Y-axis starts at 0; legend bottom-right"*. Build uses this to corroborate its own read of the screenshot and render the correct structure.

If a content type has structurally distinct variations the company uses (e.g. a metrics table and a comparison matrix), prefer modeling each as its own ContentItem with a distinct id. Use `additional_screenshots` only for alternate views of the same primitive, not for distinct variations.

### Fallbacks (elements you cannot cleanly parse)

- SmartArt, custom shapes, non-standard layouts.
- `source_ref` like `slide-12-shape-3`, PNG of the area in `assets/fallback-screenshots/`, and a `reason` explaining why the engine could not parse it.
- Degrade, don't skip silently.

### Source media (raw assets extracted from the PPTX)

Every PPTX is a zip; embedded brand artwork (logos, decorative shapes, photographic backgrounds, custom fonts) lives at full source resolution alongside the structured XML. These assets are valuable for the build stage when the host AI Design Tool does not expose the company's brand primitives directly: they let build use real source artwork rather than working from downsampled screenshots. Hosts that do expose brand primitives can ignore this tier.

**Extract media that the design system layer references** — the slide master(s), slide layouts, and theme. Trace each media file's references in the source and keep only those reachable from a design-system part. Save into `snapshot/assets/source-media/` with original filenames preserved; those filenames are the relationship targets referenced throughout the source, so keeping them intact preserves traceability for the build stage.

**Skip media that is only referenced by concrete slides in the source deck.** Those images are the original author's slide content (specific photos, product screenshots, diagrams placed on a single slide), not part of the brand system. Even when those slides are captured as Examples, their per-slide content is not brand-asset material; including it dilutes the pool the build stage draws from at level 3 (see `build` skill) and wastes disk on per-deck noise. The signal is "referenced by master / layout / theme"; the noise is "only referenced by individual slides we did not author." A real PPT template will commonly have only a handful of design-system assets (logo, one or two decorative artworks, perhaps a master background) even when `ppt/media/` lists dozens of files.

**If the design system layer references no media** — none on the master, none on any layout, no theme imagery — set `source_media` to an empty list, and either skip creating `assets/source-media/` or leave it empty. Not every template carries embedded brand artwork. Do not error, do not warn, do not invent placeholder assets. The build stage handles the empty case gracefully.

For each kept asset, append an entry to the snapshot's `source_media` array:

- **`id`**: stable id derived from the filename (e.g. `image9` from `image9.png`). Slugify if the source uses unusual characters.
- **`path`**: relative to `snapshot.json`, e.g. `assets/source-media/image9.png`.
- **`kind`** (recommended): one of `raster` (PNG, JPEG, GIF, WebP), `vector` (SVG, EMF, WMF), `font` (TTF, OTF, WOFF), `media` (MP3, WAV, MP4, MOV). Determine from extension.
- **`source_ref`** (recommended): the original path inside the source, e.g. `ppt/media/image9.png`. Preserves traceability to the source format.
- **`role`**: one of `brand-mark`, `decorative`, `photographic`, `icon`, `background`. The role splits into two kinds:
  - **`background` is structural — set it whenever the structural evidence is present.** Determined by *how* the image is referenced in the source, not by what it depicts. When the image is wired in as a layout's or master's background fill (rather than living inside a content placeholder), set `role: "background"`. Build relies on this to render the image as the slide's full-bleed background instead of trying to fit it into a picture placeholder; omitting it when the evidence is there causes downstream fidelity bugs.
  - **`brand-mark` / `decorative` / `photographic` / `icon` are visual — recommended when confident, optional otherwise.** Judgments about what the image depicts and where it appears: a small PNG with transparency in a corner of the master is likely `brand-mark`; an image referenced inside a content placeholder on a single example slide is likely `photographic`. **If you cannot classify confidently, omit** rather than guessing — the build agent can re-classify by inspection.
- **`appears_in`** (recommended): list of layout ids that reference this asset (and example or content ids when relevant). You already walked the references to decide what to keep, so populating this is essentially free and gives the build agent the "logo appears in every layout" vs "decorative artwork appears on three layouts" distinction it needs. Use the special token `master` when the asset is on the slide master and inherits to all layouts.
- **`notes`** (optional): anything the build agent should know that isn't captured by the structured fields.

Engine-agnostic shape: the same `SourceMedia` schema is what every engine emits (Keynote will extract from package internals, Figma will fetch image fills via API, Google Slides will resolve API-referenced images). The filter applies cross-engine too — keep design-system-layer assets, skip per-slide content.

**File-size note.** The extracted set is typically a small fraction of the source's total embedded media, since most photography and product imagery in a corporate template lives on individual slides rather than on the master or layouts. A source whose `ppt/media/` totals 30 MB can easily produce a `source-media/` folder under 5 MB after filtering. The user keeps `source/<file>.pptx` already, so the project's overall disk footprint is unaffected. Future versions may add a manifest opt-out (`extract_source_media: false`) if a project has reason to skip this entirely.

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
