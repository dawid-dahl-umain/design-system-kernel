# Design System Kernel (DSK)

A portable plugin that plugs into any folder-based AI Design Tool (Claude Design and equivalents) and turns a company's declared design system source into an AI-readable slide system. Employees generate on-brand slides by chatting with the agent, not by composing manually in PowerPoint or Keynote. MVP ships a PowerPoint snapshot engine; the engine model is pluggable for Keynote, Google Slides, Figma, design tokens, and other future sources.

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

## Quickstart

1. Install the plugin into your AI Design Tool's plugin directory (or load locally with `claude --plugin-dir <path-to-dsk>`).
2. Open a project folder and drop your company's PowerPoint master into `source/`.
3. Run `/dsk:setup` (or say "set up DSK"). The agent walks you through the rest.

For the full skill list, system dependencies, and the developer-testing flow, see [`dsk/README.md`](dsk/README.md).
