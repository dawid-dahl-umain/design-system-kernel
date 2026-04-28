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
- A short instruction at the top of the page: how a user uses this page when building a deck, and how to refine a specific example rendition by id (handled by `dsk:refine`).
- **A "compare to source" affordance for every entry.** Provide a way to surface the source screenshot from `snapshot/assets/example-screenshots/<id>.png` for comparison, but **keep the source hidden by default — only reveal on explicit user interaction** (a toggle button, click-to-overlay, swap-on-press, or similar; the agent picks the specific pattern). The rendition is the headline; the source is the user's fidelity-check reference, available on demand. The toggle's visual treatment — button design, transition style, animation timing — should follow the page's overall chrome aesthetic, not introduce its own visual vocabulary.

## Should consider

- A hero section if the snapshot tags one example as primary or as the canonical reference deck.
- Allow filtering by layout.
- Make each entry's stable id easy to copy (visible label + click-to-copy affordance), since users will reference it by id when invoking `dsk:refine`.
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
