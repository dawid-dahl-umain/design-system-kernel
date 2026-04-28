---
description: Stage 2 of the DSK pipeline. Read the snapshot plus the kernel briefs and produce the library pages (welcome, layouts, examples, content gallery) as web pages. Use for /dsk:build or after any snapshot change.
---

# DSK Build — Stage 2

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

Read the snapshot and the kernel briefs, then produce the library pages as web pages (HTML, CSS, JavaScript). This is agentic and behavior-level: the briefs describe what each page must convey; you decide how to render.

## Inputs

- `snapshot/snapshot.json` and its `assets/` directory (in the company zone).
- The four briefs, located alongside this `SKILL.md` under `briefs/`:
  - `briefs/welcome.md`
  - `briefs/layouts.md`
  - `briefs/examples.md`
  - `briefs/content-gallery.md`

## Output

The default location is a `library/` directory at the project root:

```
library/
  welcome.html
  layouts.html
  examples.html
  content-gallery.html
  assets/                # shared CSS, JS, images you generate
```

Resolve the actual location in this order (per `dsk:context`):

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

## How to render

- The output medium is web pages: HTML, CSS, JavaScript. Not PowerPoint.
- Two runs may produce different rendering and that's fine, as long as both satisfy the brief contract (principle 7).
- Faithful translation is the floor: web rendering must not feel like a downgrade from the declared source (principle 10).
- Ceiling: opt-in additive expressivity (interactivity, live data, custom typography) when invited by the user or annotated metadata; not by default.
- Embed snapshot screenshots as images in the rendered pages. Reference them via relative paths from `library/`.
- Layout and example pages should read as slide-browser catalogs: a clean grid of source-ratio slide thumbnails, grouped with headings, similar to the preview strip/grid you see when opening a deck in Keynote or PowerPoint. The screenshot is the visual specimen; surrounding UI supports browsing and identification.

### Style stance

Library pages should feel visually at home with the company's design system — sympathetic to the source, not generic documentation chrome. Two rendering paths depending on what the host AI Design Tool offers:

1. **If the host exposes a design system feature** (typography tokens, color tokens, component primitives, brand assets — e.g. Claude Design's design-system surface): use those directly. The library pages render in the host's native vocabulary, which is the closest you'll get to brand-faithful chrome.

2. **If the host has no such feature** (e.g. running in Claude Code or a similar agent runtime where only filesystem access exists): infer a sympathetic aesthetic from the snapshot screenshots — colors, typography character, density, accent choices that feel of-a-piece with the source. You don't need a pixel-perfect match; the goal is "looks nice and feels related to the brand," not exact mimicry.

3. **In either case**, the embedded snapshot screenshots are the brand-faithful visual specimens. The surrounding UI supports browsing without trying to compete with them. Restrained chrome, content-led.

4. **Quality bar — practical floor.** The rendered pages should look nice to the user. Readable typography, sensible spacing, restrained color use, professional polish. If choosing between brand fidelity and polish, choose polish — a tasteful approximation beats a clumsy literal match.

5. **Never pause to ask the user** for colors, fonts, or brand specifics during build. If the host has a design system feature, use it; otherwise infer from screenshots. Build runs through end-to-end (per principle 11's spirit and the same pacing principle setup uses).

## Build all four pages

Run through each brief in turn. Each page can be a single self-contained HTML file or share a `library/assets/` directory for common CSS and JS. Either approach is fine.

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
