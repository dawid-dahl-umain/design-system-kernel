# Content gallery brief

## Intent

Catalog the content types (tables, charts, diagrams, callouts, etc.) the agent is allowed to produce, shown as web-rendered specimens (renditions) the user can recognize and refer to when chatting. The renditions are the same files compose reuses to fill layout content slots — this page is the user's window into them.

## Must include

- One entry per `ContentItem` in the snapshot's `content_catalog`, scoped by the company's DoF ceiling. If an item has `dof_level`, show it only when that level is at or below the ceiling. If `dof_level` is absent, treat source-exemplified items as `match`.
- Each entry embeds its content rendition from `library/renditions/content/<content-id>.html` as the primary visual (typically via `<iframe>` so slide-ratio and isolation are preserved). The rendition is the headline; do not substitute the source screenshot for it.
- Each entry shows: the `display_name` if present (the company's preferred name for this content type), otherwise the structural `type` label as the heading; the structural `type` as a secondary tag when `display_name` is shown; the rendition embedded at readable size; the entry's stable id; and any `notes` field content.
- If the entry has `additional_screenshots`, render those alongside or below the primary rendition as supplementary source references.
- Items grouped by `type` (all tables together, all charts together, etc.). Within a group, items ordered alphabetically by id. The grouping must be deterministic across runs.
- A short instruction at the top of the page: how a user uses this page when chatting with the agent (point at a content type for the slide they're building), and how to refine a specific content rendition by id (handled by `dsk:refine`). **Note: content items are where the agent's first-pass renditions are most likely to drift from source — encourage users to compare against the source screenshot per entry and refine if needed.**
- **A "compare to source" affordance for every entry.** Provide a way to surface the primary source screenshot from `snapshot/assets/content-screenshots/<id>.png` for comparison, but **keep the source hidden by default — only reveal on explicit user interaction** (a toggle button, click-to-overlay, swap-on-press, or similar; the agent picks the specific pattern). For content items this affordance is especially important: charts, tables, and diagrams have many small structural details (axis ticks, legend placement, header backgrounds, arrow styles) that are easy to miss without visual comparison. The toggle's visual treatment — button design, transition style, animation timing — should follow the page's overall chrome aesthetic, not introduce its own visual vocabulary.

## Should consider

- Note alongside each item the DoF level it represents, when known (e.g. "Match: this is exactly how the source uses it").
- A short paragraph at the top explaining how DoF affects what's shown on this page.
- Make each entry's stable id easy to copy (visible label + click-to-copy affordance), since users will reference it by id when invoking `dsk:refine`.
- Navigation links to the other display artifacts.
- Accessibility: alt text on visuals, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers.

## Must not

- Show content types beyond the configured DoF ceiling.
- Suggest constructions the declared source does not exemplify (that would invent content types, violating principle 1).
- Embed only the source screenshot. The rendition is the headline; the screenshot is the "compare to source" reference.
- Inline content HTML directly into this page. Renditions are reusable files; they get embedded, not duplicated.
