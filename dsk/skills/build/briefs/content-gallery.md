# Content gallery brief

## Intent

Catalog the content types (tables, charts, diagrams, callouts, etc.) that the agent is allowed to produce, with visual reference and any construction notes.

## Must include

- One entry per `ContentItem` in the snapshot's `content_catalog`, scoped by the company's DoF ceiling. If an item has `dof_level`, show it only when that level is at or below the ceiling. If `dof_level` is absent, treat source-exemplified items as `match`.
- Each entry shows: the `display_name` if present (the company's preferred name for this content type), otherwise the structural `type` label as the heading; the structural `type` as a secondary tag when `display_name` is shown; the primary screenshot at readable size; and any `notes` field content.
- If the entry has `additional_screenshots`, render those alongside or below the primary as supplementary views of the same content type.
- Items grouped by `type` (all tables together, all charts together, etc.). Within a group, items ordered alphabetically by id. The grouping must be deterministic across runs.
- A short instruction at the top of the page: how a user uses this page when chatting with the agent (point at a content type for the slide they're building).

## Should consider

- Note alongside each item the DoF level it represents, when known (e.g. "Match: this is exactly how the source uses it").
- A short paragraph at the top explaining how DoF affects what's shown on this page.
- Navigation links to the other display artifacts.
- Accessibility: alt text on screenshots, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers.

## Must not

- Show content types beyond the configured DoF ceiling.
- Suggest constructions the declared source does not exemplify (that would invent layouts, violating principle 1).
