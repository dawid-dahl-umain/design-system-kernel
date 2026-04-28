# Internal configuration — What DSK is made of

Concrete parts that live in the kernel zone. Not principles (those are in [principles.md](principles.md)), not outputs (those are in [outputs.md](outputs.md)). These are the fixed assets DSK ships with.

"Internal" because this is configuration internal to DSK itself. The user-facing configuration (per company) is the manifest, declared in the company zone.

## Plugin packaging

DSK is distributed as a plugin following Anthropic's plugin convention: a folder bundle that the AI Design Tool can install. Lives at `dsk/` in the repository, namespace is `dsk`, skills are referenced as `dsk:<skill-name>`.

```
dsk/                              # plugin root
  .claude-plugin/
    plugin.json                   # plugin manifest: name, description, version, author
  README.md                       # optional; for users and contributors
  lib/                            # plugin-level shared utilities (not skills)
    snapshot/
      models.py                   # Pydantic schema (canonical type definitions)
      validate_snapshot.py        # engine-agnostic validator, used by all snapshot-* engines
  skills/
    context/
      SKILL.md
      lifecycles.md             # mermaid diagrams of setup/compose/sync; canonical visual reference
      walkthrough.md            # end-user-perspective scenarios with [You]/[DSK] markers
    help/
      SKILL.md
      inspect_state.py
    setup/SKILL.md
    snapshot-ppt/
      SKILL.md
    build/
      SKILL.md
      briefs/
        welcome.md
        layouts.md
        examples.md
        content-gallery.md
    compose/SKILL.md
    refine/SKILL.md
    sync/SKILL.md
    route-extension/SKILL.md
    dof/SKILL.md
```

Conventions, per Anthropic's plugin docs:

- Only `plugin.json` lives in `.claude-plugin/`. Skills, scripts, and other content go at the plugin root, never inside `.claude-plugin/`.
- Each skill folder name (`context`, `snapshot`, etc.) becomes the skill name, prefixed automatically by the plugin namespace at runtime.
- `SKILL.md` is the entry point per skill. Supporting scripts (e.g. `ppt_engine.py`) and behavior-level briefs sit alongside the `SKILL.md` that uses them.

## Skills (markdown, read by the agent)

DSK ships as a plugin named `dsk`. Skills inside it are referenced as `dsk:<name>` (Anthropic plugin namespace convention). Export is delegated to the host AI Design Tool, so DSK has no export skill.

| Skill | Purpose | Includes (beyond SKILL.md) |
|---|---|---|
| `dsk:context` | Foundational context for the agent (`user-invocable: false`). Holds the principles in brief, pipeline overview, lifecycle summaries, and pointers to other skills. The agent invokes this first on any DSK project before routing to other skills; the `AGENTS.md` DSK section that `dsk:setup` writes directs this. | `lifecycles.md` (mermaid diagrams), `walkthrough.md` (user-perspective scenarios) |
| `dsk:help` | Diagnostic by project state. Inspects the company zone, reports what is set up vs missing, recommends the next action (setup, sync, etc.). User-invocable. | `inspect_state.py` |
| `dsk:setup` | First-time install. Add source, write manifest, write or extend the project `AGENTS.md` marker (with `CLAUDE.md` symlink for Claude tooling), write/extend `.gitignore`, run snapshot, run build. | — |
| `dsk:snapshot-ppt` | Stage 1, PowerPoint engine. Agent extracts the snapshot from a PPT source by following SKILL.md, using python-pptx and LibreOffice via tool calls (no monolithic engine script). Other source formats use their own `dsk:snapshot-*` engine skill. Validation is shared across engines (see `lib/snapshot/`). | — |
| `dsk:build` | Stage 2. Read snapshot plus briefs, produce two artifact categories under `library/`: **renditions** (one HTML file per layout and example, the actual web slides reused by compose) and **library pages** (the browser around them — welcome, layouts, examples, content-gallery). May pause for user input if no design system is available for the renditions. | `briefs/` (welcome, layouts, examples, content-gallery) |
| `dsk:compose` | Usage flow. Smart layout selection plus smart content generation plus DoF decision. | — |
| `dsk:refine` | Adjust a specific rendition (layout, example, or content item) based on user feedback. Two-layer test: direction check (fidelity correction or opt-in web expressivity → allowed; brand/structural divergence → blocked) and DoF magnitude check (same ladder compose uses). Especially useful for content items where first-pass renditions tend to drift from source. | — |
| `dsk:sync` | Re-snapshot, diff against current, classify changes, apply silently or ask user (principle 8). | — |
| `dsk:route-extension` | Handle out-of-scope requests by directing the user to update source-of-truth and re-sync. Enforces principle 1. | — |
| `dsk:dof` | Reference skill. DoF vocabulary, worked examples, runtime actions. The agent invokes it from compose and sync when classifying a proposed change. Not user-invocable as a slash command. | — |

`AGENTS.md` handling: `AGENTS.md` is the cross-vendor agent-context convention (read natively by Codex, Cursor, Aider, Copilot, and others). Claude Code and Claude Design read `CLAUDE.md` but follow symlinks transparently, so DSK creates `CLAUDE.md` as a symlink to `AGENTS.md` (one file, two names, zero drift). If absent, `dsk:setup` creates `AGENTS.md` and the symlink. If `AGENTS.md` is present, setup appends or updates the DSK section delimited by `<!-- DSK BEGIN -->` and `<!-- DSK END -->`. Existing user content outside the markers is never modified (principle 8). On systems where symlinks are problematic (some Windows configurations), setup falls back to writing `CLAUDE.md` as a one-line `@AGENTS.md` import.

Generated section content (between the markers):

```markdown
# Project context

This project uses DSK (Design System Kernel) for slide generation.

- Source of truth: source/<file>
- Manifest: manifest.yaml
- The agent routes to dsk:* skills based on intent. Run `/dsk:help` for orientation and project status.
```

Company-specific instructions: anything outside the DSK markers in `AGENTS.md` is user-controlled context and read by the agent on every interaction. This is the canonical place for company rules DSK itself does not encode: writing style preferences, terminology conventions, audience-specific notes, etc. The agent reads the entire file, so DSK's section and the company's section coexist without conflict. Example:

```markdown
# Project context

<!-- DSK BEGIN -->
[DSK-managed section]
<!-- DSK END -->

## Writing style

- Never use em dashes; prefer commas, semicolons, or periods.
- Use British English spelling.
- Refer to clients as "partners" in external-facing decks.
```

## Briefs (behavior-level specs the agent interprets)

One brief per library page. Each describes what the page must convey, not the rendered structure. See principle 7.

- Welcome page brief
- Layouts page brief
- Examples page brief
- Content gallery brief

### Brief format

Structured markdown with four sections, each a list of evaluable assertions:

- **Intent.** One sentence on what the artifact conveys.
- **Must include.** Required content; failing any of these means the brief is not satisfied.
- **Should consider.** Optional improvements; not required.
- **Must not.** Explicit exclusions.

This approximates BDD scenarios in markdown: a behavior contract, no rendering instructions.

## Snapshot engines

Each engine is its own skill that handles one source format. The agent picks the right engine based on the manifest's source declaration. MVP ships one:

- **`dsk:snapshot-ppt` (MVP).** Reads a PowerPoint master, emits the snapshot. See [snapshotting.md](snapshotting.md).
- Future engines (additional skills): `dsk:snapshot-keynote`, `dsk:snapshot-google-slides`, `dsk:snapshot-figma`, `dsk:snapshot-tokens`.

All engines emit the same `DesignSystemSnapshot` shape, so schema validation is shared and lives at the plugin level: `dsk/lib/snapshot/` holds `models.py` (canonical Pydantic schema) and `validate_snapshot.py` (engine-agnostic validator). Engines invoke it after extraction; they do not duplicate it.

## Vocabularies and policies

- Degrees of freedom vocabulary. See [degrees-of-freedom.md](degrees-of-freedom.md).
- Conflict resolution policy for manifest source disagreements. See [source-of-truth.md](source-of-truth.md).

## Possibly needed, not yet decided

Placeholders for parts we may add as the design matures:

- Manifest schema validator.
- CLI entry point or scripts.
- Example project scaffolding / templates for new company installations.
- Evaluation rubric and test harness.

---

[← Back to overview](../REQUIREMENTS.md)
