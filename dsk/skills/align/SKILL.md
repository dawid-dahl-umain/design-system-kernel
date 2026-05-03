---
description: Alignment pass over renditions. Walk each rendition in scope, hold it next to its source screenshot and snapshot entry, confirm correspondence on structure and character, and fix drift in place. Idempotent — clean renditions produce no changes. Default scope is the whole library; the user can narrow to a single rendition id, a set of ids, or a natural-language subset ("the bar charts", "the title slides") by passing arguments to `/dsk:align` or describing the subset in chat. Use as build's closing stage, as setup's closing pass after build, as sync's closing pass after rebuild, or directly via `/dsk:align` when the user wants a fresh sweep over the existing library (full or subset) without rebuilding from scratch.
---

# DSK Align — Alignment Pass

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

This is the **verify pass** — the agent's final acceptance gate before the library (or the requested subset of it) is declared faithful to the source. Walk every rendition in scope, compare it against its source screenshot and snapshot entry, and bring it into alignment where it has drifted. Idempotent: a rendition that already matches the source needs no edit, and an alignment pass over a clean scope produces no changes. The skill's job is to catch the cases where a rendition's structure or character has drifted from what the source actually shows, and close that gap.

Align lives between `dsk:build` (which generates the library from scratch and invokes align as its closing stage) and `dsk:refine` (which adjusts a single rendition on user request). Align operates over **the whole library or a user-specified subset** and **only ever moves toward source faithfulness**; refine is single-rendition, user-directed, and runs through the direction-and-DoF tests because the user can ask refine for opt-in web expressivity that align would have no business adding. When the user names a specific rendition (or set of renditions) and asks for fidelity correction toward source, align in subset mode is the right tool; when they want to direct a specific change that may include opt-in web expressivity, refine is the right tool.

## When to invoke

- **From `dsk:build`** as its closing stage, after the generation steps. Every build ends with align over the whole library.
- **From `dsk:setup`** as the final stage after build returns, giving the agent a fresh attention reset on a freshly-generated library at the moment setup completes. Always full library.
- **From `dsk:sync`** after sync regenerates renditions in response to a source change. Always full library (sync may have changed any rendition).
- **Direct user invocation via `/dsk:align`** when the user wants a pass over the existing library without rebuilding from scratch — e.g. they noticed drift after browsing, they want to re-run alignment with a more capable model, or they're following up after a build to make sure the in-flight discipline didn't slip. Direct invocation supports both **full library** (no arguments) and **subset** (arguments or chat description) modes; see Scope below.

## Scope

Align runs over either the **whole library** (default) or a **user-specified subset**. The mode is determined at invocation time and applies to the entire pass.

- **Full library mode** (default). Walk every rendition under `library/renditions/{layouts,examples,content}/`. This is the mode used by `dsk:build`, `dsk:setup`, and `dsk:sync` when they invoke align as their closing pass. Direct user invocation with no arguments — `/dsk:align` — also runs in this mode.

- **Subset mode.** The user narrows the scope at invocation. Two ways to express this:

  1. **By id** — one or more rendition ids passed as arguments: `/dsk:align bar-chart-1`, `/dsk:align title-hero divider-hero`, or stated in chat ("align bar-chart-1 and table-comparison"). Resolve each id to its rendition file and source screenshot. If an id doesn't resolve cleanly (typo, wrong category, ambiguous between layout and example with the same id), ask the user to clarify before proceeding.

  2. **By natural-language description** — a phrase the agent resolves to a set of renditions: "align the bar charts", "align the title slides", "just the content gallery", "everything in the case-study layout family", "the layouts that use the hero background". Translate the phrase to a concrete list using the snapshot data: content type for content items, layout id or naming family for layouts, examples grouped by `layout_id`. If the phrase is ambiguous (the user could plausibly mean two different sets) or returns zero or surprisingly many matches, list what you'd run against and confirm with the user before starting. Don't guess.

  When in subset mode, narrate the resolved set back to the user in plain English before doing any reads ("Aligning these 4 renditions: bar-chart-1, bar-chart-revenue, table-comparison, table-quarterly. OK?"). Wait for confirmation if the resolution involved any inference — proceed without asking only when the user passed exact ids that resolved cleanly.

The per-rendition discipline (how each rendition is read, compared, and aligned) is the same in both modes. Only the iteration scope changes.

## Inputs

- The **scope**: either the full library, or a user-specified subset (set of rendition ids resolved per Scope above).
- For each rendition in scope: its file under `library/renditions/{layouts,examples,content}/<id>.html`, its source screenshot under `snapshot/assets/{layout-screenshots,example-screenshots,content-screenshots}/<id>.png`, and its entry in `snapshot/snapshot.json` (placeholders, type, notes, ids, source_media references).
- The manifest, for company name and any company-specific overrides. Align does not consult `dof.ceiling` or `dof.silent_up_to` — alignment is fidelity correction toward source, which is principle 1's preferred direction and below `match` on the DoF ladder; the manifest's thresholds don't gate it.

## Outputs

- Modified rendition files where alignment changes were applied. Files that already matched source are left untouched.
- A run summary listing what was verified clean, what was aligned (one-line description per rendition), and any snapshot-level misclassifications spotted (e.g. a slide labelled `bar-chart` whose screenshot is actually a comparison matrix; surface these so the user can decide whether to re-snapshot with a corrected type).

No new files; no library-page rewrites. Library pages embed renditions via iframe/include, so they refresh automatically on next browser reload.

## How to do it

Work through every rendition **in scope** (full library or the resolved subset, per Scope above). Handle each as a complete unit before moving on:

1. **Load the three inputs together.** Open the rendition file. Open its source screenshot. Read its snapshot entry (placeholders, type, notes, ids, `source_media` references when present).
2. **Describe what the source actually shows in plain words.** Visible regions and dominant primitives, spatial relationships (rows, columns, grids, sidebars, headers), palette, key imagery, brand marks, decorative motifs, overall character. For matrix-structured sources (comparison tables, multi-section grids, anything with a left-side label column and entity columns), narrate the row × column orientation explicitly — transposition is the most expensive failure here, and naming the orientation in prose before doing anything else is what catches it.
3. **Compare the rendition to that description on both axes.** **Structure** (regions, primitives, spatial relationships, **proportions** — does each region sit at the same fraction of the slide as in the source?) and **character** (palette, key imagery, brand marks, overall feel). A rendition can fail either axis in several ways: same regions but wrong palette; same composition but missing the source's signature image; same layout but a different brand mark; right regions in wrong proportions (a body that runs past the slide's natural bottom margin, a footer at the wrong vertical position, a picture placeholder that crowds an adjacent text column) — all fail. When proportions are off, the correction comes from the snapshot's structural geometry: read the rendition's snapshot entry, transcribe each placeholder's position directly, do not eyeball.
4. **If it matches on both axes: leave it alone.** Emit a one-line audit-trail note in your chat output that names what the source actually shows, in enough detail that you couldn't have produced the note without looking at the screenshot. Vacuous notes ("rendition matches ✓") defeat the purpose. Move on.
5. **If it drifts on either axis: fix in place.** Edit the rendition file to close the gap. Touch only what needs changing — the goal is alignment, not a restyle. Re-read the modified file and re-check against the screenshot before declaring it aligned. Emit an audit-trail note describing what changed and what it now matches.
6. **Move to the next rendition.** Do not move on until step 4 or 5 is completed for the current one.

**Do not batch-process complex multi-region renditions.** A loop that emits or rewrites many HTML files at once collapses the per-rendition pause where the screenshot read and the structural check happen — the agent skips them silently and the alignments come out as plausible-looking sketches rather than faithful reads. Simple uniform renditions (a title slide, a divider, a section break — single dominant region, no matrix structure, no spatial complexity) can be processed in tighter passes. Anything with multi-region structure (matrices, dashboards, multi-card grids, charts surrounded by prose, comparison tables) must be handled one at a time, with the screenshot opened and the structure narrated per rendition. The determinant is structural complexity, not which bucket (layout / example / content) the rendition lives in.

## When the screenshot and the snapshot data conflict

**The screenshot wins on type, composition, and character; the snapshot wins on placeholder geometry (only it encodes geometry, so there's no conflict to resolve there — see step 3 above).** The snapshot's `type` label is a structural classifier that may describe an *embedded element* rather than the slide's *overall composition*. A slide classified as `bar-chart` because it contains an embedded stacked-column chart can in fact be a multi-metric multi-region dashboard with that chart as one tile inside it. Aligning to the metadata alone produces a textbook bar chart and the source character is lost. The screenshot is the truth on what the slide depicts; the metadata corroborates and refines, it does not override.

The same conflict pattern applies to layouts (a name like `two-content` may describe one of several possible structures) and examples (the snapshot may capture text content but the spatial structure — card grid vs. vertical stack — lives only in the screenshot). In all three cases, look at the screenshot first to understand what the slide actually is, then use the structured data to nail down precise positions, ids, and named slots.

When you spot a clear misclassification, align the rendition to what the screenshot actually shows, and flag the misclassification in the run summary so the user can decide whether to re-snapshot with a corrected type.

## What you do not do

- **Do not invent decoration the source clearly does not have.** If a layout is genuinely minimal — a neutral wash with a title and a wordmark — keep the rendition minimal. Skepticism about impoverished layout screenshots applies when the screenshot looks impoverished *relative to the source's actual character*, not as license to embellish past what the source shows.
- **Do not generalize a decoration from a few sampled renditions to the whole library.** Spot-checking a decorative motif on a couple of layouts and concluding "all light-themed layouts have it" is a recurring failure class with a specific shape: the agent reads N screenshots, sees a pattern, then applies it across the rest without reading those screenshots. Decorative motifs are usually family-specific in real templates; body-content layouts especially are often deliberate clean canvases. Every rendition's screenshot is its own ground truth; the audit-trail note for each rendition has to reflect what's actually in *its* screenshot, not what the previous rendition had.
- **Do not introduce changes that move away from source.** Align is fidelity correction only. New colors not in the palette, new fonts, new placeholders, reorganized grids — all out of scope here. If you spot something that warrants a brand or structural change, surface it in the run summary as a recommendation; do not apply it. User-directed brand or structural changes flow through `dsk:refine` and `dsk:route-extension`, not align.
- **Do not regenerate library pages or chrome.** Align modifies rendition files only. If the library is missing pages or has structurally invalid output, recommend `/dsk:build` to regenerate before re-running align.
- **Do not skip renditions because the previous one was clean.** Each rendition is read independently against its own screenshot. A clean run on the first ten renditions does not license skimming the eleventh.

## Memory-based generation has a tell

Precise-but-wrong numbers (a value of 286 reproduced as 266; a sequence "3/5/5/4" reproduced as "3/5/6/4"), text that's almost-but-not-quite the source's wording, and structures that resemble the source's general *type* but not its specific instance — these are the signature of filling in from training-pattern memory of similar slides rather than reading the screenshot. When you spot any of those in the rendition you're aligning, the previous build was sketching from memory. Read the screenshot and align the rendition to what's actually there, not to what a textbook version of that slide type looks like.

## Acceptance gate

Do not declare the alignment pass done until every rendition tile would survive a user clicking compare-to-source without spotting an obvious gap on either axis. This is the moment the agent stands behind the library; treat it accordingly. Schema validation cannot catch "rendition is off from source" on either axis — only this self-check can.

## Run summary

After the pass, surface to the user (in plain English):

- The scope of the pass (full library, or the specific subset that was aligned).
- How many renditions were verified clean.
- How many were aligned, with a brief description of what changed for each.
- Any snapshot misclassifications spotted (id, current `type` label, what the screenshot actually shows). Recommend `/dsk:sync` after the user corrects the source.
- Any rendition where alignment couldn't close the gap (id and what's still off). Recommend `/dsk:refine` for user-directed iteration on that rendition.

## When to fall back elsewhere

- If the library is missing entirely (no `library/` directory, or `library/renditions/` is empty): recommend `/dsk:build` first; align has nothing to walk.
- If many renditions need wholesale changes that look like a design-system shift (e.g. the brand color is wrong everywhere): recommend `/dsk:build` instead so the styling resolution runs once consistently across the library, rather than hand-aligning each rendition.
- If the user is pointing at one specific rendition and wants to *direct* a specific change (e.g. opt-in web expressivity, a tweak that may or may not be strict fidelity toward source): recommend `/dsk:refine`. Refine runs the direction check and the DoF magnitude check that align skips; align in subset mode (`/dsk:align <id>`) is appropriate when the user just wants the rendition aligned to source, not when they're directing a specific change.
