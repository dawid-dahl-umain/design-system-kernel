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

Renditions are the value DSK delivers, so be careful here. Resolve in priority order:

1. **Host design system, if clearly available** (most preferred). Actively check the runtime:
   - The host AI Design Tool exposes a design-system feature directly (typography tokens, color tokens, component primitives, brand assets — e.g. Claude Design's design-system surface). Use it.
   - Or the host has discoverable design tokens / theme files / component libraries elsewhere (project-level config, host-managed folders, environment hints). Spend a brief look. If found, use it.

2. **User-provided design system in the project folder** (second preference). If the user has dropped tokens, a `design-system/` folder, brand guidelines, or anything design-system-shaped into the project, use it.

3. **Neither found → STOP and ask the user.** Don't silently approximate. Surface what was checked and offer concrete paths forward, in plain English. Suggested phrasing:

   > "I didn't find a design system to base your renditions on. Renditions are the actual web slides DSK will use to make your decks, so they need styling direction. How would you like to proceed?"

   - **Point me at brand guidelines or a design system file/folder** in your project. (User shares a path; agent reads it.)
   - **Tell me the essentials** — primary colors, font families, mood/feel — and I'll work from those. (Quick conversation; agent collects basics.)
   - **Approximate from your source screenshots.** I'll infer colors and typography character that feel of-a-piece with the source. Sympathetic, not pixel-perfect. (Good for testing or when no design system exists.)
   - **Use generic tasteful defaults.** Clean professional styling that doesn't claim to match your brand. (Last resort; rare.)

   Wait for the user's choice. Then act on it for all renditions in this build.

This pause is correct and intentional. Renditions warrant it because they're the product; chrome doesn't because chrome is just scaffolding.

### Quality bar for renditions

- **Match the source's visual character as closely as the chosen path allows.** Layouts and examples should feel like they belong to the company, not like generic web slides.
- **Preserve slide aspect ratio.** Each rendition file renders at the source slide ratio (typically 16:9 for modern PPT).
- **Placeholders are real, named slots.** When compose later fills a layout rendition, it should be obvious from the HTML where the title goes, where the body goes, where the chart goes. Use semantic class names or data attributes that match the snapshot's placeholder types.
- **Polish over pixel-perfect.** A tasteful approximation beats a clumsy literal match.

## Library page chrome — the browser around renditions

The four library pages (welcome, layouts, examples, content-gallery) are navigation and reference, not the value layer. Each page satisfies its brief and embeds the relevant renditions as the visual specimens. Chrome rules differ from rendition rules.

### Style stance for chrome (auto-resolves; never pauses)

Resolve the chrome aesthetic in this priority order:

1. **Host design system, if present** (most preferred). Same active-check-then-explore logic as for renditions, but if found, just use it.

2. **Source-derived aesthetic, if no host design system is found.** Infer a sympathetic chrome from the snapshot screenshots — colors, typography character, density, accent choices that feel of-a-piece with the source.

3. **Generic-but-pleasing fallback** (rare). Tasteful neutral defaults if source is unreadable or yields no coherent palette.

**Never pause to ask the user about chrome specifics.** Resolve via the priority order and run through. Chrome decisions are reversible and low-stakes; renditions are the moment that warrants user input, not chrome.

### Quality bar for chrome

- The output medium is web pages: HTML, CSS, JavaScript. Not PowerPoint.
- Two runs may produce different chrome and that's fine, as long as both satisfy the brief contract (principle 7).
- Faithful translation is the floor (principle 10).
- Ceiling: opt-in additive expressivity when invited by the user or annotated metadata; not by default.
- Restrained, content-led. Layout and example pages should read as slide-browser catalogs: a clean grid of slide-ratio thumbnails, grouped with headings, with the renditions carrying most of the visual weight. The screenshot in `snapshot/assets/` may be shown alongside as a "compare to source" reference if useful, but the rendition is the headline.
- Quality floor: looks nice to the user. Readable typography, sensible spacing, restrained color use, professional polish.

## Build order

1. **Resolve rendition styling first** (host design system check → user-provided check → ask the user if neither). Once resolved, hold the chosen styling for use across all renditions in this build.
2. **Generate renditions.** One file per layout, one file per example, in the structure above.
3. **Generate library pages.** Each satisfies its brief and embeds the relevant renditions (via iframe or include).
4. **Validate.** Every layout id in the snapshot has a matching rendition file; same for examples; library pages reference them correctly.

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
