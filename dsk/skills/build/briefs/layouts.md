# Layouts page brief

## Intent

A browsable catalog of every layout in the snapshot, shown as web-rendered specimens (renditions) the user can recognize and refer to when chatting with the agent. The renditions are the same files compose will reuse to make real slides — this page is the user's window into them.

## Must include

- One specimen per layout in the snapshot's `layouts` array.
- Each specimen embeds the layout's rendition from `library/renditions/layouts/<layout-id>.html` as the primary visual (typically via `<iframe>` so the rendition's slide-ratio and isolation are preserved). The rendition is the headline; do not substitute the source screenshot for it.
- Each specimen reads visually like a deck thumbnail: rendition above or beside compact metadata, with the rendition carrying most of the visual weight.
- Each specimen shows the layout's name and its stable id so the user can refer to it in chat.
- Each specimen shows usage notes derived from the layout's `notes` field plus inferred guidance from placeholder types.
- Specimens grouped by inferred family from the layout name where the family is evident (Title, Content, Divider, Closer, etc.). Each group has a clear section header. Within a group, layouts ordered alphabetically by name. The grouping must be deterministic across runs.
- A way to open each rendition at full size (clickable card linking to the rendition file, or equivalent).
- A short instruction at the top of the page: how a user picks a layout when chatting with the agent, and how to ask the agent to refine a specific rendition by id (handled by `dsk:refine`).
- **A "compare to source" affordance for every entry.** Provide a way to surface the source screenshot from `snapshot/assets/layout-screenshots/<id>.png` for comparison, but **keep the source hidden by default — only reveal on explicit user interaction** (a toggle button, click-to-overlay, swap-on-press, or similar; the agent picks the specific pattern). The rendition is the headline; the source is a comparison reference users invoke when they want to spot fidelity gaps. The toggle's visual treatment — button design, transition style, animation timing — should follow the page's overall chrome aesthetic, not introduce its own visual vocabulary.

## Should consider

- Show placeholder types as labels on each specimen so the user can see at a glance "this layout has a title and three columns".
- Make each entry's stable id easy to copy (visible label + click-to-copy affordance), since users will reference it by id when invoking `dsk:refine`.
- A small summary of total layout count at the top of the page.
- Navigation links to the other display artifacts (Welcome, Examples, Content gallery).
- Accessibility: alt text on visuals, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers when writing prose.

## Must not

- Invent layouts not in the snapshot.
- Embed only the source screenshot. The rendition is the headline; the screenshot is at most a "compare to source" reference.
- Inline layout HTML directly into this page. Renditions are reusable files; they get embedded, not duplicated.
- Show theme colors or fonts as the primary content of this page.
- Show fallbacks here; fallbacks are a separate concern.
