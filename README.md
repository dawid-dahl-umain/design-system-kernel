# Design System Kernel (DSK)

A Claude Code plugin that turns a company's PowerPoint master into a stable snapshot — structured data plus rendered screenshots — that the agent reads to generate on-brand slide decks via chat. Used today through Claude Design; lets employees build decks by chatting with the agent instead of composing them manually in PowerPoint or Keynote.

Scope today: PowerPoint as source, Claude Design as host. The kernel is designed vendor-neutral and engine-pluggable, so additional source engines (Keynote, Google Slides, Figma, design tokens, etc.) and other folder-based AI Design Tool hosts can be added in the future. Those are part of the design intent, not currently implemented.

## Repository layout

- **`dsk/`** — the plugin itself. Drop into a host AI Design Tool's plugin directory, or load via `claude --plugin-dir dsk` for development. See [`dsk/README.md`](dsk/README.md) for install instructions and the skill list.
- **[`REQUIREMENTS.md`](REQUIREMENTS.md)** — top-level table of contents for the design.
- **`requirements/`** — design documents (principles, architecture, types, content input, separation, snapshotting, degrees of freedom, glossary, developer testing, open questions). For DSK maintainers and contributors. The plugin runtime does not depend on these files; they describe the system from outside.

## Status

MVP. The plugin is structurally complete and self-contained:

- Nine skills (`dsk:context`, `dsk:help`, `dsk:setup`, `dsk:snapshot-ppt`, `dsk:build`, `dsk:compose`, `dsk:sync`, `dsk:route-extension`, `dsk:dof`)
- Shared snapshot schema and validator (`dsk/lib/snapshot/`)
- Vendor-neutral project context via `AGENTS.md` (with a `CLAUDE.md` symlink for Claude tooling)
- Six independent ownership fingerprints (skill namespace, AGENTS.md DSK section, .gitignore DSK section, manifest schema, snapshot schema, `.dsk-managed` markers)

End-to-end testing against a real PowerPoint master is the next milestone. The snapshot stage is host-portable (principle 11) and can be exercised in Claude Code or any skill-compatible runtime; see [`requirements/developer-testing.md`](requirements/developer-testing.md).

## Install

The plugin lives at `dsk/` inside this repository, so the repo doubles as a single-plugin **marketplace** (`.claude-plugin/marketplace.json` at the root). In Claude Code (and Claude Design when supported), install with:

```
/plugin marketplace add dawid-dahl-umain/design-system-kernel
/plugin install dsk@design-system-kernel
```

For local development without going through the marketplace flow, clone the repo and load the plugin folder directly:

```
claude --plugin-dir /path/to/design-system-kernel/dsk
```

## Quickstart

1. Install the plugin (see above).
2. Open a project folder and drop your company's PowerPoint master into `source/`.
3. Run `/dsk:setup` (or say "set up DSK"). The agent walks you through the rest.

For the full skill list, system dependencies, and the developer-testing flow, see [`dsk/README.md`](dsk/README.md).
