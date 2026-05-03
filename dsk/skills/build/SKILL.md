---
description: Stage 2 of the DSK pipeline. Read the snapshot plus the kernel briefs and produce two kinds of artifacts in the library — renditions (web-rendered slides that compose reuses) and library pages (the browser around them). Use for /dsk:build or after any snapshot change.
---

# DSK Build — Stage 2

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

Read the snapshot and the kernel briefs, then produce two distinct categories of output: **renditions** (the actual web-rendered slides — reusable, modular, the real product of DSK) and **library pages** (the browser around them — chrome and structure for navigation). This is agentic and behavior-level: the briefs describe what each library page must convey; you decide how to render. Renditions and chrome have different rules — see the two sections below.

## Inputs

- `snapshot/snapshot.json` and its `assets/` directory (in the company zone).
- The four briefs, located alongside this `SKILL.md` under `briefs/`:
  - `briefs/welcome.md`
  - `briefs/layouts.md`
  - `briefs/examples.md`
  - `briefs/content-gallery.md`

## Outputs

Two distinct artifact categories, both under the library directory:

```
library/
  welcome.html              # browser page: project intro
  layouts.html              # browser page: layout catalog (embeds layout renditions)
  examples.html             # browser page: example gallery (embeds example renditions)
  content-gallery.html      # browser page: content type catalog (embeds content renditions)
  renditions/
    layouts/
      <layout-id>.html      # one file per layout in the snapshot — reusable by compose
      ...
    examples/
      <example-id>.html     # one file per example in the snapshot
      ...
    content/
      <content-id>.html     # one file per content type in the snapshot — reusable by compose's content slots
      ...
  assets/                   # shared CSS, JS, fonts you generate
```

**The split matters.** Renditions are the real product — compose reuses them as starting templates when the user asks for a slide. Library pages are just the browser. Chrome decisions auto-resolve from the environment; rendition decisions may pause to ask the user (see below).

Resolve the actual library location in this order (per `dsk:context`):

1. `manifest.yaml` `paths.library` if explicitly set.
2. A host AI Design Tool convention for where reference/library pages live (if detectable — host-managed output folders, host project config).
3. DSK default: `library/` at the project root.

When you depart from the DSK default, briefly tell the user where you wrote the pages.

## How to read a brief

Each brief has four sections:

- **Intent**: one-sentence summary of what the page conveys.
- **Must include**: required content. Failing any of these means the brief is not satisfied.
- **Should consider**: optional improvements; not required.
- **Must not**: explicit exclusions.

Treat each line in the lists as an independent assertion. The page must satisfy every "must include" item and must not violate any "must not" item. "Should consider" items are nice-to-haves.

## Renditions — the real product

Renditions are web-rendered versions of every layout and every example in the snapshot, produced once at build time and reused by compose. They are what makes DSK useful: the user gets actual web slides, not just a screenshot gallery of the source.

**Rendition file lifecycle:** `dsk:build` writes them; `dsk:compose` reads them (never modifies them — slides are written to the deck folder as new files); `dsk:refine` is the only skill that modifies a rendition file, and only on explicit user request; `dsk:sync` regenerates them when the source changes.

### Modular reuse principle

- **One file per layout** at `library/renditions/layouts/<layout-id>.html`.
- **One file per example** at `library/renditions/examples/<example-id>.html`.
- **One file per content type** at `library/renditions/content/<content-id>.html`. These are canonical web renditions of each content type from the snapshot's `content_catalog` (a representative bar chart, a representative table, etc.). Compose reuses them when filling layout content slots.
- **Each rendition is self-contained or shares `library/assets/`.** Never inline rendition HTML directly into library pages — library pages embed renditions via `<iframe>` (preserves slide-ratio isolation) or include them in slots. This keeps renditions reusable by compose and keeps the browser pages thin.
- **The `<layout-id>`, `<example-id>`, and `<content-id>` match the ids in `snapshot/snapshot.json`** so compose and refine can resolve them.

### Stylistic resolution for renditions (asymmetric with chrome — may pause)

Renditions are the value DSK delivers, so be careful here. Two distinct categories of input matter:

- **Design tokens**: typography, colors, spacing, component primitives. Drive the overall styling.
- **Brand assets**: logos, decorative artwork, photographic backgrounds, custom fonts. Drive the layout's visual identity at full fidelity.

Resolve each category through the priority order below. Walk the four levels per asset, not per build: when a rendition needs typography, check level 1 first, fall through to 2, 3, and 4 only as needed; do the same independently for the next asset (a logo, a photographic background, a decorative shape). It's normal for design tokens to resolve at level 1 (host) and a specific logo to resolve at level 3 (source-media) in the same run.

1. **Host design system, if clearly available** (most preferred). Actively check the runtime:
   - The host AI Design Tool exposes a design-system feature directly (typography tokens, color tokens, component primitives, brand assets — e.g. Claude Design's design-system surface). Use it.
   - Or the host has discoverable design tokens / theme files / component libraries elsewhere (project-level config, host-managed folders, environment hints). Spend a brief look. If found, use it.

2. **User-provided design system in the project folder.** If the user has dropped tokens, a `design-system/` folder, brand guidelines, or anything design-system-shaped into the project, use it.

3. **Source-extracted media** in `snapshot/assets/source-media/`, listed in `snapshot.json`'s `source_media` array. **Brand assets only at this level** — design tokens (typography, colors, spacing) don't live here, only the actual asset files (logos, decorative artwork, photographic backgrounds, embedded fonts). When neither the host (level 1) nor the user-provided folder (level 2) supplies the specific asset a rendition needs, **use this automatically — do not pause to ask first.** Source-media is part of the snapshot the user already authorized by running `dsk:snapshot-*`; reaching for it requires no additional confirmation. Read each entry's `kind` and `role` (when present) to pick assets with confidence; fall back to inspecting the file directly when `role` is absent. Source-media is host-agnostic by construction: the same files are available in Claude Code, in Claude Design, and in any future folder-based host. This is the fallback that makes DSK self-sufficient when the host has no design-system feature.

   **`source_media` may be empty** (`[]` in the snapshot, with no or empty `assets/source-media/` directory). Some sources genuinely carry no embedded brand artwork; that's a normal case, not a bug. When the array is empty, or when it has entries but none match the asset a rendition specifically needs, treat this level as a no-op for that asset and fall through to level 4. Don't fabricate, don't loop, don't warn the user about an empty source-media — the snapshot is what it is.

4. **Nothing in levels 1–3 covers what's needed → STOP and ask the user.** Reach this only when the asset a rendition genuinely needs is missing from the host, missing from the user-provided folder, *and* missing from source-media. Don't silently approximate, and don't skip ahead to this level when level 3 has what's needed. Surface what was checked and offer concrete paths forward, in plain English. Suggested phrasing:

   > "I didn't find a design system to base your renditions on. Renditions are the actual web slides DSK will use to make your decks, so they need styling direction. How would you like to proceed?"

   - **Point me at brand guidelines or a design system file/folder** in your project. (User shares a path; agent reads it.)
   - **Tell me the essentials** — primary colors, font families, mood/feel — and I'll work from those. (Quick conversation; agent collects basics.)
   - **Approximate from your source screenshots.** I'll infer colors and typography character that feel of-a-piece with the source. Sympathetic, not pixel-perfect. (Good for testing or when no design system exists.)
   - **Use generic tasteful defaults.** Clean professional styling that doesn't claim to match your brand. (Last resort; rare.)

   Wait for the user's choice. Then act on it for all renditions in this build.

This pause is correct and intentional. Renditions warrant it because they're the product; chrome doesn't because chrome is just scaffolding.

**Important:** the four levels above are an asset-resolution priority, not an "all or nothing" gate. Use what you can from higher levels and fill the rest from lower levels; only pause at level 4 when *something specific* a rendition needs is genuinely missing across levels 1–3.

### Quality bar for renditions

- **Match the source's visual character as closely as the chosen path allows.** Layouts and examples should feel like they belong to the company, not like generic web slides.
- **Preserve slide aspect ratio.** Each rendition file renders at the slide ratio derived from `snapshot.json`'s `canvas` (`width / height`). The canvas field is authoritative; do not infer the ratio from screenshot pixel dimensions.
- **Placeholders are real, named slots.** When compose later fills a layout rendition, it should be obvious from the HTML where the title goes, where the body goes, where the chart goes. Use semantic class names or data attributes that match the snapshot's placeholder types.
- **Polish over pixel-perfect.** A tasteful approximation beats a clumsy literal match.

### Reading the source screenshots and the snapshot data together

**Both the screenshot and the snapshot's structured data are required inputs to every rendition; use them together.** The screenshot is the visual ground truth for what the slide actually depicts (composition, regions, dominant primitives, spatial arrangement, structural features like rows, columns, grids, sidebars, headers, footers). The structured data gives precise placeholder positions, stable ids, the `type` label, the `notes` field, and per-engine specifics — facts the screenshot can't convey alone. Before writing any rendition's HTML, load the relevant screenshot and read the snapshot entry, describe in plain words what's depicted, and reconcile both into a complete picture.

**Where they conflict, the screenshot wins.** This is the failure mode that has cost the most fidelity in past runs: the snapshot's `type` label is a structural classifier that may describe an *embedded element* rather than the slide's *overall composition*. A slide classified as `bar-chart` because it contains an embedded stacked-column chart can in fact be a five-metric four-region dashboard with that chart as one tile inside it. Generating from metadata alone produces a textbook bar chart and the source character is lost. The screenshot is the truth; the metadata corroborates and refines, it does not override.

The same conflict pattern applies to layouts (a name like `two-content` may describe one of several possible structures) and examples (the snapshot may capture text content but the spatial structure — 2×2 card grid vs. vertical stack — lives only in the screenshot). In all three cases, look at the screenshot first to understand what the slide actually is, then use the structured data to nail down precise positions, ids, and named slots.

After writing each rendition, **structurally self-check** before moving on: compare the rendition's structure to the screenshot. Count distinct visual regions and dominant primitives on each side. If they don't match — e.g. screenshot has a four-column grid with mini charts and prose blocks, and the rendition has one large chart with a sidebar — the rendition is structurally wrong. Fix and re-generate. A vertical text dump is never a faithful rendition of a slide arranged as a card grid.

**Pre-write narration for matrix-structured sources.** When the source has a row × column structure — matrices, comparison tables, multi-section grids, anything with a left-side label column and entity columns — narrate the structure in prose *before* writing HTML, not after. The most expensive failure here is **transposition**: the source presents rows-as-sections (financials, regions, offerings, strengths) and columns-as-entities (companies, products, time periods); the rendition then presents the inverse — M vertical stacks each containing every section label, with the label column duplicated M times instead of appearing once on the left, and the cross-entity comparison the source affords is destroyed. Pre-write narration makes transposition obvious before any code is written; post-write self-check often catches it too late, when reshuffling every cell is the cost of fixing it. Whenever the source has a left-side label column, preserve the row-as-section, column-as-entity orientation.

**Memory-based generation has a tell.** Precise-but-wrong numbers (a value of 286 reproduced as 266; a sequence "3/5/5/4" reproduced as "3/5/6/4"), text that's almost-but-not-quite the source's wording, and structures that resemble the source's general *type* but not its specific instance — these are the signature of filling in from training-pattern memory of similar slides rather than reading the screenshot. When you spot any of those in your own output, you weren't reading; you were sketching from memory. Reset and read carefully.

The screenshots are visual ground truth, but they are not infallible. Treat them with appropriate skepticism, especially for layouts whose distinguishing character is image content.

- **Prefer example screenshots over layout screenshots when both exist for the same layout.** For each Layout, look up Examples whose `layout_id` matches it. Example screenshots show the layout populated with real content and render at full fidelity (no empty picture placeholders, no synthetic specimen artifacts). When at least one example exists for a layout, treat the example screenshot(s) as the primary visual reference and the layout screenshot as a supporting reference for empty-state structure. When no example exists, the layout screenshot is the only reference.

- **Distinguish layout backgrounds from picture-placeholder content.** Two kinds of imagery can appear on a layout, with very different rendering targets:

  - A **picture placeholder** is a content slot the user fills with their own image at slide-creation time. It appears in the layout's `placeholders` list with `type: "picture"` and has its own geometry. Render it as a subtle, labelled image region at the placeholder's coordinates; keep the slide background at the master's neutral fill. If a `source_media` entry's `appears_in` includes this layout AND its `role` is *not* `background`, fill the placeholder with that image; otherwise leave the slot empty and labelled (the user supplies content).

  - A **layout-level background image** is part of the layout's design — applied at the master or layout level (e.g. in PPT, as a layout-scoped background fill), not as a content slot. There is no `placeholder` entry for it; it's a fixed feature of the layout. In `source_media`, this is typically an entry with `role: "background"` whose `appears_in` lists the layouts that use it. Render this image as the slide's full-bleed background, behind everything else; there is no picture placeholder for the user to fill.

  These two concerns are independent: a layout can have one, both, or neither. The decision is structural — read it off the data, do not guess from the layout name. A `picture` placeholder in `placeholders` ⇒ slot rendering. A `source_media` entry with `role: "background"` and `appears_in` for this layout ⇒ slide-background rendering. Neither ⇒ the slide background is the master's neutral fill, with no image at all.

- **Watch for impoverished layout screenshots.** The snapshot engine renders specimen slides via LibreOffice headless, which has known fidelity limits on photographic backgrounds, gradient fills, and certain theme effects. Symptoms: empty boxes where the placeholder geometry implies an image should be, missing background photography, decorative elements that the layout's name suggests but the screenshot doesn't show. When you spot this, do not faithfully reproduce the impoverished render — that propagates the fidelity gap into the rendition. Instead:
  - Lean harder on the host design system for visual primitives (colors, typography, photographic style, decorative motifs).
  - Cross-reference any example screenshots for the same layout; they often show what the layout actually looks like populated.
  - Read the layout's `notes` field; the engine may have flagged a known gap there (e.g. "subtle radial gradient not visible in this render; treat as solid cream").
  - If the layout's name implies imagery the screenshots don't show (e.g. `case-image-light` rendering as a plain cream box), do not synthesize a decorative slide-wide background to compensate. Use the rule above: if the layout has a picture placeholder, render that placeholder slot as a subtle labelled image region at its own geometry and keep the slide background at the master's neutral fill; if the layout has a `source_media` entry with `role: "background"` and `appears_in` for this layout, use that as the slide-background fill. Neither path involves inventing a gradient.

- **Content screenshots are full-slide captures.** Each `content-screenshots/<id>.png` shows a representative slide containing the catalogued content type, framed at full slide width. The catalogued content may be one tile in a multi-region slide, the dominant primitive of the slide, or anything in between. Read the whole screenshot to identify what's actually being catalogued, then render that — not the textbook version of the snapshot's `type` label. When the slide's overall structure clearly diverges from the `type` label (e.g. `bar-chart` on a comparison-matrix slide), the rendition should reflect the slide's actual structure, and you should flag the misclassification in your run summary so the user can decide whether to re-snapshot with a corrected type.

- **Do not invent decoration the source clearly does not have.** This is the inverse risk. If a layout is genuinely minimal (e.g. a `title-cream` layout is just a cream wash with a title and the company's wordmark), keep the rendition minimal. The skepticism above applies when the screenshot looks impoverished *relative to the source's actual character*, not as license to embellish past what the source shows.

  **In particular, do not synthesize a slide-wide visual treatment (gradient, photographic backdrop, decorative theme) by inferring it from a layout's name or any other indirect signal.** Layout names commonly encode which placeholder slots a layout exposes, what master-level imagery it carries, or an internal brand-team label — they do not describe a decorative slide-wide treatment. The rendition's slide character is determined by what the source shows, not by what the name suggests: read it off the screenshot, the `placeholders` list, and `source_media`. If those three agree the slide background is the master's neutral fill, the rendition's slide background is the master's neutral fill, regardless of how evocative the layout name sounds. The same applies to any inferential text — `notes`, `type` labels, naming conventions — none of them license a visual treatment the screenshot, placeholders, and source_media don't jointly carry.

## Library page chrome — the browser around renditions

The four library pages (welcome, layouts, examples, content-gallery) are navigation and reference, not the value layer. Each page satisfies its brief and embeds the relevant renditions as the visual specimens. Chrome rules differ from rendition rules.

### Style stance for chrome (auto-resolves; never pauses)

Resolve the chrome aesthetic in this priority order:

1. **Host design system, if present** (most preferred). Same active-check-then-explore logic as for renditions, but if found, just use it.

2. **Source-derived aesthetic, if no host design system is found.** Infer a sympathetic chrome from the snapshot screenshots — colors, typography character, density, accent choices that feel of-a-piece with the source.

3. **Generic-but-pleasing fallback** (rare). Tasteful neutral defaults if source is unreadable or yields no coherent palette.

**Never pause to ask the user about chrome specifics.** Resolve via the priority order and run through. Chrome decisions are reversible and low-stakes; renditions are the moment that warrants user input, not chrome.

### Writing for the user — language UX principle

Library pages have human readers (the company's employees), not just the agent. You reason internally in DSK's vocabulary (DoF, ceiling, silent_up_to, manifest, rendition, placeholder, match/adapt/stretch/deviate, source-of-truth, snapshot, content_catalog). **The user does not.** When you write prose into library pages, translate everything to plain English. The user shouldn't have to learn DSK's classification system to use the project productively.

- **Don't write** "This project's DoF ceiling is `adapt`."
- **Do write** something like *"Right now this project is set up so the agent can match the source exactly or make small adjustments. Bigger changes need your confirmation; changes that break from the source aren't allowed."*
- **Don't write** "Items above `silent_up_to` aren't shown."
- **Do write** *"Some content types from the source aren't shown here because the project's settings don't allow them yet."*
- **The "match / adapt / stretch / deviate" ladder is internal vocabulary — don't expose those words verbatim.** If you need to describe what kinds of changes are allowed, name them in plain language: "exact use", "small adjustments", "larger creative changes", "changes that break from the source's design."
- **"Rendition" is OK in moderation** since it shows up in the library navigation as a UX concept. But "the slide", "the chart", "the layout" is often more natural for the specific thing being discussed. Pick what flows best.
- **"Placeholder" is borderline** — fine in obvious context, but "where the title goes" or "the image slot" is plainer.
- **Stable ids are OK to surface** — users see them in the library and use them when asking the agent to refine a specific entry. Treat them like filenames: visible labels users can copy.
- **Don't reference internal field names, file paths, or config files as casual asides** (`dof_level`, `silent_up_to`, `display_name`, `additional_screenshots`, `appears_in`, `manifest.yaml`, `snapshot/`, `library/`, `briefs/`). Translate to plain language ("the project's settings", "what the system has captured from the source"), or omit. **Slash commands are fine when the user actually needs to run one** ("Type `/dsk:setup` to start" is good; "edit `manifest.yaml` and re-sync" is bad — the latter assumes the user knows what `manifest.yaml` is and what re-syncing means). When you do mention a slash command, frame it as a thing the user can do, not as a reference to internal mechanics.
- **Footers stay light.** A useful footer names the company (read from `manifest.yaml`) and the source file path; that's enough. It does not need to advertise that the page is "regenerable from snapshot/ + briefs" — that's an internal property the user doesn't need to think about.
- **Library's self-name and branding.** This plugin is **DSK: Slides** (the slides plugin in the Design System Kernel family). When a library page needs to brand itself in navigation, `<title>` tags, headers, or footers, use one of: *"DSK: Slides"*, *"[Company name] Slide Library"*, or *"Slide Library"*. Don't use the unqualified *"DSK Library"* — DSK is now the family name, not this plugin's identity. *"Design System Kernel"* spelled out is fine in a one-line subtitle that explains the family context, but keep the primary brand short and slide-specific.

The same principle applies to every brief's "Must include" and "Should consider" instructions: where a brief tells you to surface a DSK concept on the page, you do, but you do it in plain English in the rendered output, never by typing the internal term verbatim. The brief tells you *what* to convey; the principle here governs *how* to phrase it for human readers.

### Quality bar for chrome

- The output medium is web pages: HTML, CSS, JavaScript. Not PowerPoint.
- Two runs may produce different chrome and that's fine, as long as both satisfy the brief contract (principle 7).
- Faithful translation is the floor (principle 10).
- Ceiling: opt-in additive expressivity when invited by the user or annotated metadata; not by default.
- Restrained, content-led. Layout and example pages should read as slide-browser catalogs: a clean grid of slide-ratio thumbnails, grouped with headings, with the renditions carrying most of the visual weight. The screenshot in `snapshot/assets/` may be shown alongside as a "compare to source" reference if useful, but the rendition is the headline.
- Quality floor: looks nice to the user. Readable typography, sensible spacing, restrained color use, professional polish.

## Build order

1. **Resolve rendition styling first** (host design system check → user-provided check → ask the user if neither). Once resolved, hold the chosen styling for use across all renditions in this build.
2. **Generate renditions.** One file per layout, one file per example, one file per content item, in the structure above. **Per rendition:** load its source screenshot *and* read its snapshot entry (placeholders, type, notes, ids), describe what's depicted using both — for matrix-structured sources, narrate the structure in prose before writing HTML — then write the file. After writing, structurally self-check against the screenshot (see the "Reading the source screenshots and the snapshot data together" section above), then **emit a one-line self-check note in your chat output** confirming the rendition matches its source. The note's shape is up to you; the load-bearing constraint is specificity — the note has to name what the source actually shows in enough detail that you couldn't have produced it without looking at the screenshot. Vacuous notes ("rendition matches ✓") defeat the purpose. The act of writing a specific note is what forces the look. Only then move to the next rendition.

   **Do not batch-generate complex multi-region renditions in a single script run.** A loop that emits many HTML files at once collapses the per-rendition pause where the screenshot read, structural narration, and self-check happen — the agent skips them silently and the renditions come out as plausible-looking sketches, not faithful reads. Simple uniform renditions (a title slide, a divider, a section break — single dominant region, no matrix structure, no spatial complexity) can be batched safely. Anything with multi-region structure (matrices, dashboards, multi-card grids, charts surrounded by prose, comparison tables) must be generated one at a time, with the screenshot opened and the structure narrated per rendition. The determinant is structural complexity, not which bucket (layout / example / content) the rendition lives in.
3. **Generate library pages.** Each satisfies its brief and embeds the relevant renditions (via iframe or include).
4. **Validate paths and ids.** Every layout id in the snapshot has a matching rendition file; same for examples and content items; library pages reference them correctly.
5. **Self-verify renditions against their source screenshots — structural pass.** Sweep through every rendition one by one — re-read the rendition HTML, look at its source screenshot, and confirm structural correspondence: visible regions match, dominant primitives match, spatial relationships preserved (rows, columns, grids, sidebars, headers). This step is mandatory; do not declare the build done without it. Schema validation in step 4 cannot catch "rendition is structurally unrelated to source" — only this self-check can. Fix any divergent rendition before reporting completion. If you spot a misclassification at the snapshot level (e.g. a slide labelled `bar-chart` that is actually a comparison matrix), flag it in the run summary so the user can decide whether to re-snapshot with a corrected type.

6. **Verify the library against the source — character pass and final acceptance gate.** Step 5 catches *structural* divergence; this step catches *character* divergence, the kind that has the right region count but feels wrong next to the source. For every rendition tile across `layouts.html`, `examples.html`, and `content-gallery.html`, hold the rendition next to its source screenshot and ask whether the character matches: palette and color, key imagery (the source's signature decorative artwork, photographic backgrounds, layout-level background images), brand marks (logos, wordmarks, decorative motifs like corner dots, rule lines, accent bars), and the slide's overall visual feel. A rendition that shares the source's structure but misses its character — same regions, wrong palette; same layout, missing the source's signature image; same composition, different brand mark — fails this gate even if step 5 passed. Fix and re-verify. Do not declare the build done until every tile would survive a user clicking compare-to-source without spotting an obvious gap. This is the acceptance gate for whether the library actually represents the company faithfully; treat it accordingly.

## After building

Surface the entry point (`library/welcome.html`) to the user using whatever consumption channel your runtime supports — host-native preview if the host AI Design Tool renders HTML inline, otherwise instruct the user to open the file in a browser. Same artifacts in either case; the difference is only how the user views them.

Write a marker file at `library/.dsk-managed` with this single line of plain text:

```
DSK-managed. Generated by /dsk:build; regenerable from snapshot/ + the kernel briefs. Do not edit manually.
```

This signals to any agent or tool walking the filesystem (Claude Design, other plugins, DSK itself) that this directory is owned by DSK. Overwrite the marker on every rebuild.

## When to rebuild

- After any snapshot engine skill runs (e.g. `dsk:snapshot-ppt`), since the snapshot has changed.
- When briefs are updated (kernel update).
- User invokes `/dsk:build`.

Library pages are regenerable from snapshot plus briefs (principle 2). Deleting them is low-stakes; you can always rebuild.
