# DSK — Design System Kernel

A Claude Code plugin that turns a company's PowerPoint master into a stable snapshot — structured data plus rendered screenshots — that the agent reads to generate on-brand slide decks via chat in Claude Design.

Scope today: PowerPoint as source, Claude Design as host. The kernel is designed vendor-neutral and engine-pluggable; additional source engines (Keynote, Google Slides, Figma, design tokens, etc.) and other folder-based AI Design Tool hosts are possible future extensions, not currently implemented.

Source repository: <https://github.com/dawid-dahl-umain/design-system-kernel>. The full requirements and design rationale live there in `REQUIREMENTS.md` and the `requirements/` folder.

## Install

This plugin is published from the source repository as a marketplace of one plugin. In Claude Code (and Claude Design when supported), install with:

```
/plugin marketplace add dawid-dahl-umain/design-system-kernel
/plugin install dsk@design-system-kernel
```

For local development without going through the marketplace flow, clone the repo and load this folder directly:

```
claude --plugin-dir /path/to/design-system-kernel/dsk
```

## Quickstart

1. Install the plugin (see above).
2. Open a project folder and drop your company's declared source file into `source/` (for MVP, a PowerPoint master).
3. Invoke `/dsk:setup` (or say "set up DSK for this company"). The agent walks you through the rest.
4. Once setup is done, browse the generated `library/` pages and start building decks via chat.

## Skills

- `dsk:context` — foundational context the agent invokes first on any DSK project (not user-invocable as a slash command).
- `dsk:help` — project state diagnostic and onboarding.
- `dsk:setup` — first-time install.
- `dsk:snapshot-ppt` — stage 1: read a PowerPoint source, write snapshot.
- `dsk:build` — stage 2: read snapshot + briefs, produce library pages.
- `dsk:compose` — generate a slide.
- `dsk:sync` — reconcile after the declared source changes.
- `dsk:route-extension` — handle out-of-scope requests.
- `dsk:dof` — degrees of freedom reference (invoked by compose and sync; not user-invocable as a slash command).

## System dependencies

The snapshot stage uses standard tools the agent installs and calls on demand:

- Python 3 with `python-pptx` (the agent installs on first use if missing).
- LibreOffice headless for PPT to PNG rendering. Install with your package manager (`brew install --cask libreoffice` on macOS, `apt install libreoffice` on Debian/Ubuntu).

There is no `requirements.txt` shipped with the plugin; the agent manages dependencies as it works.

## Testing the snapshot stage

The snapshot stage is host-portable (principle 11). Test it in Claude Code or any skill-compatible runtime without an AI Design Tool:

```bash
claude --plugin-dir path/to/dsk
```

Then invoke `/dsk:snapshot-ppt` against a sample PPT (you bring your own; the plugin does not ship a fixture).

The full developer workflow is documented in `requirements/developer-testing.md` in the source repository.
