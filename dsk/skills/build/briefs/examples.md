# Examples page brief

## Intent

Show a slide examples gallery where filled source slides appear as source-ratio thumbnails, like deck previews in Keynote or PowerPoint, so users see what good looks like and have material to point at when chatting with the agent.

## Must include

- One example per `Example` entry in the snapshot.
- Each example shows its screenshot as the primary visual, preserving the source slide aspect ratio with no cropping or decorative treatment that changes the slide's perceived design.
- Each example reads visually like a deck thumbnail: screenshot above or beside compact metadata, with the screenshot carrying most of the visual weight.
- Each example shows the layout it uses (via `layout_id` lookup, with the layout name displayed).
- Each example shows a stable index or id, the layout it uses, and any sub-classification tags discernible from the layout name or notes (theme variant, visual style, fidelity level, content type).
- Examples grouped by their underlying layout, with deterministic group ordering (alphabetical by layout name). Each group has a clear section header.
- A short instruction at the top of the page: how a user uses this page when building a deck.

## Should consider

- A hero section if the snapshot tags one example as primary or as the canonical reference deck.
- Allow filtering by layout.
- A side-by-side view showing the underlying layout (from `layout-screenshots/`) next to the filled example, to illustrate how content flows in.
- Navigation links to the other display artifacts.
- Accessibility: alt text on screenshots, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers.

## Must not

- Invent example slides not in the snapshot.
- Edit or annotate the example screenshots themselves.
- Crop thumbnails, place them inside decorative mockups, or alter their colors, typography, spacing, or proportions.
