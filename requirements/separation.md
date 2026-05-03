# Kernel/company separation

## Kernel zone (portable, identical across companies)

Holds skills, briefs, snapshot engines, and vocabularies. See [internal-configuration.md](internal-configuration.md) for the concrete parts list.

## Company zone (unique per company)

Concrete directory layout:

```
AGENTS.md                         # project marker (cross-vendor agent-context convention); DSK section between markers (dsk:setup writes/extends)
CLAUDE.md                         # symlink to AGENTS.md so Claude Code/Design read the same content; created by dsk:setup
.gitignore                        # DSK section between markers (dsk:setup writes/extends); ignores regenerable artifacts
source/                           # declared source files, PowerPoint for MVP (user-owned)
manifest.yaml                     # per-company config; see types.md (user-owned)
snapshot/                         # phase 1 output: structured data + screenshots (regenerable; gitignored)
  .dsk-managed                    # ownership marker (one-line plain text, written by the engine skill)
  snapshot.json
  assets/
library/                          # phase 2 output (verified by phase 3): web technologies (regenerable; gitignored)
  .dsk-managed                    # ownership marker (one-line plain text, written by dsk:build)
  welcome.html                    # browser pages — humans navigate the design system here
  layouts.html
  examples.html
  content-gallery.html
  renditions/                     # the value layer — actual web slides reused by dsk:compose
    layouts/
      <layout-id>.html            # one file per layout in the snapshot
    examples/
      <example-id>.html           # one file per example in the snapshot
    content/
      <content-id>.html           # one file per content type in the snapshot (charts, tables, diagrams, etc.)
  assets/                         # shared CSS, JS, images
decks/                            # finished decks; one folder per deck, date-prefixed (user work product; tracked)
  2026-04-25-q3-results/
  2026-05-10-board-update/
```

Tracked vs gitignored: the user's own content (`source/`, `manifest.yaml`, `AGENTS.md`, `CLAUDE.md` symlink, `decks/`, `.gitignore`) is tracked. The regenerable build artifacts (`snapshot/`, `library/`, plus the transient `snapshot.previous/` that `dsk:sync` creates and removes) are gitignored. `dsk:setup` writes the gitignore section idempotently between `# DSK BEGIN` / `# DSK END` markers, the same pattern used for `AGENTS.md`.

Ownership markers: each DSK-managed directory contains a `.dsk-managed` plain-text file (no extension, conventional marker pattern) saying who generated it and how to regenerate. The engine skill writes `snapshot/.dsk-managed` after extraction; `dsk:build` writes `library/.dsk-managed` after build. These act as filesystem-level signals to any agent or tool (the host AI Design Tool, other plugins, DSK itself) that the directory is owned by DSK and should not be edited manually. They complement the gitignore markers and the DSK section in `AGENTS.md` (read by Claude tooling via the `CLAUDE.md` symlink); together they make DSK's territory unambiguous.

The only contact point between the two zones is the manifest (in the company zone). Kernel skills read the manifest to locate sources and respect company specific settings; they never embed company specific content themselves.

## How the separation is enforced

- **Different folders.** Kernel zone lives in the AI Design Tool's plugin directory; company zone is your project folder. Not in the same place.
- **Different lifecycles.** Kernel zone changes only with plugin updates. Company zone evolves with your work, mostly through `dsk:setup` and ongoing slide generation.
- **Direction of dependency at runtime.** Kernel skills read inputs from the company zone, run scripts from the kernel zone, and write outputs to the company zone. The company zone never references kernel internals.
- **No company knowledge in the kernel.** No file in the kernel zone hardcodes brand names, paths, or company-specific content. Configuration flows in via the manifest.

This is what makes DSK portable: drop the same kernel into any new company's folder, point a manifest at their source, and it works without modification.

---

[← Back to overview](../REQUIREMENTS.md)
