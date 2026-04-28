# Source of truth model

Snapshotting and runtime are deliberately separate.

Runtime: the agent reads one unified, compiled artifact in the company zone. It does not know or care where any of the content came from.

Snapshotting: the company zone declares a manifest of sources. For each dimension that the snapshot tracks, the manifest names the authoritative source. Default manifest says everything comes from the PPT, which collapses to the simple case.

When sources conflict, the snapshot stage surfaces the conflict to the maintainer. It never silently picks a winner.

## MVP scope

In MVP, the snapshot tracks only layouts, examples, content catalog, and unparseable-element fallbacks. Theme colors, typography, logos, embedded images, and reusable brand components are deliberately delegated to the host AI Design Tool's own design-system feature, native PPT extraction, or to the agent reading the source directly. The manifest in MVP therefore declares one source (a PPT file) for one engine (the PPT Snapshot Engine).

Future expansion: when additional engines arrive (Keynote, Google Slides, Figma, design tokens), companies could override per dimension (e.g. layouts from PPT, design tokens from a tokens repo). The manifest schema already supports multi-source via `SourceEntry[]` (see [types.md](types.md)); the engines just don't exist yet.

---

[← Back to overview](../REQUIREMENTS.md)
