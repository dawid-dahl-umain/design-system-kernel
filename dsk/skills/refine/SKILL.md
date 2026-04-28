---
description: Refine a specific rendition (layout, example, or content item) based on user feedback. Use when the user identifies a rendition by id and asks for adjustments — typography tweaks, fidelity corrections, web-medium polish. Especially valuable for content items (diagrams, tables, charts) where source fidelity is critical. Runs a direction check and a DoF magnitude check before applying any change.
---

# DSK Refine — Tune a Rendition

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

When a user has been browsing the library and notices a rendition that needs adjustment — wrong title size, off colors, a chart's axis labels misaligned, a table header missing the source's accent — they can ask the agent to refine that specific rendition. This skill handles that flow.

## When to invoke

- User identifies a rendition by id and asks for changes ("make the title bigger in `title-slide-2`", "the bar chart in `bar-chart-stacked-by-year` has the legend in the wrong place").
- User has been chatting about a specific rendition and asks for an iteration.
- User notes a fidelity gap between a rendition and its source screenshot (especially common for content items).

## Why content items deserve extra attention

Layouts and examples are mostly typographic and structural; their first-pass renditions tend to land close to source. **Content items — bar charts, tables, diagrams, callouts — are where the agent's first-pass rendition is most likely to drift from the source**, because they have many small structural details (axis ticks, legend placement, data label formatting, header backgrounds, arrow heads, bullet styles) that are easy to miss in a single pass.

The "compare to source" affordance on every library entry exists so users can spot these gaps; this skill is how they close them. When invoked on a content rendition, lean in: read the source screenshot carefully, compare it to the current rendition, and make the rendition more faithful before considering you're done.

## Two-layer test (run in order on every request)

Every refinement request goes through two checks before any change is applied.

### Layer 1 — Direction check

Classify the requested change into one of three categories:

1. **Fidelity correction.** The rendition currently drifts from source; the refinement closes the gap. Examples: *"the title font weight is lighter than the source — make it match"*, *"the chart legend is on the right but the source shows it inside the chart area"*, *"the table header background is missing the brand accent color the source uses"*. Direction-wise, **always allowed** — moving toward source is principle 1's preferred direction.

2. **Opt-in web expressivity** (principle 10). Add medium-specific affordances that don't conflict with source: hover states, scroll behavior, accessibility improvements, live data binding, responsive behavior. Direction-wise, **allowed** because principle 10 explicitly permits opt-in additive expressivity, and the user invoking refine for this purpose is the opt-in.

3. **Brand or structural divergence.** Change to elements not in the source: a color not in the palette, a font not in the system, a new placeholder, a reorganized grid, a different chart type. Direction-wise, **blocked** — never apply. Hand off to `dsk:route-extension`: direct the user to update the source file and re-sync (principle 1).

If the request is ambiguous about direction (could be a correction OR a divergence), **ask the user to clarify** before proceeding. Don't guess. Example: *"You asked to change the chart's accent color. Is the current rendition's color drifting from the source's color (correction), or do you want a new color that isn't in the source (divergence)? The first I can do here; the second needs a source-of-truth update."*

### Layer 2 — DoF magnitude check

For requests that pass the direction check, classify the magnitude against the DoF ladder using `dsk:dof`. Compare to the manifest's `dof.silent_up_to` and `dof.ceiling`:

- **At or below `silent_up_to`** — apply silently.
- **Above `silent_up_to` but at or below `ceiling`** — stop, explain the proposed change in plain English, ask the user to confirm.
- **Above `ceiling`** — block. Hand off to `dsk:route-extension`.

For users on strict defaults (`ceiling: adapt`, `silent_up_to: match`): anything above `match` requires confirmation, anything above `adapt` is blocked. A stretch-level liberty in a refinement gets blocked unless the user loosens the manifest first.

## Layout propagation warning

Layout renditions are **reused as templates by `dsk:compose`** — every future slide using a given layout starts from that layout's rendition. A refinement to a layout rendition isn't a one-off; it changes the company's effective design system for that layout permanently.

When refining a **layout** rendition (i.e. a file under `library/renditions/layouts/`), include a propagation note in any confirm prompt: *"This will apply to every future slide that uses this layout. OK to proceed?"*

For **example** renditions: no propagation warning. Examples are QA-only references; they don't drive compose.

For **content item** renditions: light propagation note. Compose uses content renditions as templates when filling slide content slots (a slide with a "bar chart" placeholder draws from `library/renditions/content/bar-chart.html`), so refinements affect how future content of that type renders. Mention it in confirms but more lightly: *"Future slides using this content type will use the refined version."*

## Inputs

- **Rendition id** (provided by user or inferred from recent chat context).
- **Path to the rendition file**:
  - Layouts: `library/renditions/layouts/<id>.html`
  - Examples: `library/renditions/examples/<id>.html`
  - Content items: `library/renditions/content/<id>.html`
- **Source comparison reference**:
  - Layouts: `snapshot/assets/layout-screenshots/<id>.png`
  - Examples: `snapshot/assets/example-screenshots/<id>.png`
  - Content items: `snapshot/assets/content-screenshots/<id>.png`
- The manifest's `dof.ceiling` and `dof.silent_up_to`.
- The user's feedback message.

## What to do

1. **Identify the rendition.** Get the id from the user's message; resolve the file path and the source screenshot path. If the id is ambiguous or missing, ask the user to specify.
2. **Compare current rendition to source.** Open both files, understand what the user is asking for, and (especially for content items) note any other fidelity gaps that might be relevant.
3. **Run Layer 1 (direction).** Classify and act per the three categories above. If brand/structural divergence, route out via `dsk:route-extension` — never apply.
4. **Run Layer 2 (DoF magnitude).** Classify against the manifest thresholds and act on silent / confirm / block per `dsk:dof`'s runtime rules.
5. **Apply the change.** Open the rendition file, make the edit, save it. Touch only what the user asked about; don't restyle the whole rendition.
6. **Confirm to the user.** Summarize what changed in one sentence. If it was a layout rendition, remind that the change applies to future slides using that layout.
7. **Don't auto-rebuild library pages.** The library pages embed renditions via iframe/include, so the refresh is automatic on next browser reload. No need to re-run `dsk:build`.

## When to fall back to dsk:build

- If the user's "refinement" actually requires regenerating many renditions (e.g. *"the brand color is wrong across all the layouts"*), don't make 70 individual refinements. Suggest `/dsk:build` instead so the design-system resolution runs once, consistently across all renditions.
- If a rendition file is missing entirely, recommend `/dsk:build` to regenerate the library before refining.

## Output

The modified rendition file. No new artifacts; the existing file is overwritten.
