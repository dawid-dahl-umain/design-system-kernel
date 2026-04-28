# Layouts page brief

## Intent

A browsable slide-layout catalog where every layout from the snapshot appears as a source-ratio thumbnail, like the layout previews a user would see when opening the PPT in Keynote or PowerPoint.

## Must include

- One specimen per layout in the snapshot's `layouts` array.
- Each specimen shows the layout screenshot as the primary visual, preserving the source slide aspect ratio with no cropping or decorative treatment that changes the slide's perceived design.
- Each specimen reads visually like a deck thumbnail: screenshot above or beside compact metadata, with the screenshot carrying most of the visual weight.
- Each specimen shows the layout's name and a stable index or id so the user can refer to it in chat.
- Each specimen shows usage notes derived from the layout's `notes` field plus inferred guidance from placeholder types.
- Specimens grouped by inferred family from the layout name where the family is evident (Title, Content, Divider, Closer, etc.). Each group has a clear section header. Within a group, layouts ordered alphabetically by name. The grouping must be deterministic across runs.
- A way to open each specimen at full size (clickable card or equivalent).
- A short instruction at the top of the page: how a user picks a layout when chatting with the agent.

## Should consider

- Show placeholder types as labels on each specimen so the user can see at a glance "this layout has a title and three columns".
- A small summary of total layout count at the top of the page.
- Navigation links to the other display artifacts (Welcome, Examples, Content gallery).
- Accessibility: alt text on screenshots, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers when writing prose.

## Must not

- Invent layouts not in the snapshot.
- Rebuild the layout thumbnails from scratch when a snapshot screenshot exists; use the screenshot as the visual source.
- Crop thumbnails, place them inside decorative mockups, or alter their colors, typography, spacing, or proportions.
- Show theme colors or fonts as the primary content of this page.
- Show fallbacks here; fallbacks are a separate concern.
