# Examples page brief

## Intent

Show a gallery of filled example slides as web-rendered specimens (renditions), so users see what good looks like in the same medium compose will use, and have material to point at when building decks.

## Must include

- One example per `Example` entry in the snapshot.
- Each example embeds its rendition from `library/renditions/examples/<example-id>.html` as the primary visual (typically via `<iframe>` so slide ratio and isolation are preserved). The rendition is the headline.
- Each example reads visually like a deck thumbnail: rendition above or beside compact metadata, with the rendition carrying most of the visual weight.
- Each example shows the layout it uses (via `layout_id` lookup, with the layout name displayed).
- Each example shows a stable id, the layout it uses, and any sub-classification tags discernible from the layout name or notes (theme variant, visual style, fidelity level, content type).
- Examples grouped by their underlying layout, with deterministic group ordering (alphabetical by layout name). Each group has a clear section header.
- A short instruction at the top of the page: how a user uses this page when building a deck.

## Should consider

- A hero section if the snapshot tags one example as primary or as the canonical reference deck.
- Allow filtering by layout.
- A "compare to source" affordance — show the source screenshot from `snapshot/assets/example-screenshots/<id>.png` alongside the rendition for QA.
- A side-by-side view showing the underlying layout rendition (from `library/renditions/layouts/<layout-id>.html`) next to the filled example rendition, to illustrate how content flows in.
- Navigation links to the other display artifacts.
- Accessibility: alt text on visuals, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers.

## Must not

- Invent example slides not in the snapshot.
- Embed only the source screenshot. The rendition is the headline; the screenshot is at most a "compare to source" reference.
- Inline example HTML directly into this page. Renditions are reusable files; they get embedded, not duplicated.
- Edit or annotate the rendition contents themselves from this page (examples are read-only references; modifications happen at build time per the company's design system).
