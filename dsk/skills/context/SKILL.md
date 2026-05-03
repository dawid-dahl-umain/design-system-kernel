---
description: Foundational DSK context — principles, lifecycle summaries, pointers to lifecycles.md and walkthrough.md. Invoke ONCE at the start of any chat session on a DSK project (detected by manifest.yaml, snapshot/, or DSK markers in AGENTS.md / CLAUDE.md), before routing to any other dsk:* skill. Once loaded for a session, do not re-invoke on subsequent turns — the context persists. Provides the why and the lay-of-the-land you need to operate correctly.
user-invocable: false
---

# DSK: Slides — Context

You are working on a project that uses **DSK: Slides** — the slides plugin in the Design System Kernel (DSK) family. This skill is the foundational context the other `dsk:*` skills assume — invoke it before any other DSK skill on the project, read it in full, and only then route to the specific skill the user's intent calls for.

## What this plugin is

DSK is a portable pattern: turn a company's declared source of truth into a stable intermediate snapshot, then have an AI agent generate web-rendered artifacts faithful to that source. **DSK: Slides** is the slides instantiation of that pattern — the agent reads a company's declared slide-system source and generates on-brand slides via chat, instead of having employees compose them manually in PowerPoint or Keynote. Other artifact families (posters, reports, branded documents) would have their own DSK plugins following the same source → snapshot → renditions shape; those are out of scope here.

DSK: Slides lives inside an AI Design Tool (Claude Design and equivalents) but stays vendor-neutral. MVP uses PowerPoint through `dsk:snapshot-ppt`; the kernel is designed for multiple source engines.

The mental model is: Claude Design becomes the slide authoring surface, but the company's existing slide system remains the constraint system. In PowerPoint or Keynote, users trust that an official layout looks like the official layout. In DSK: Slides, the snapshot gives you that same trusted boundary, then DoF defines how much agentic change is allowed inside it.

## Core principles

1. **Source of truth is authoritative and the only origin.** Read from it; never override it. New layouts, content types, or brand elements always originate in the declared source of truth and flow into DSK via snapshotting, never the other way.
2. **Everything DSK generates is regenerable.** Library pages and snapshots are build artifacts; can be deleted and rebuilt anytime.
3. **Strict kernel/company separation.** Plugin files (kernel zone) are identical across companies; project files (company zone) are unique per company. They meet only at the manifest.
4. **Respect, then stretch.** Match the source exactly first; take smallest brand-consistent liberty when needed; ask before larger deviations.
5. **Degrees of freedom are tunable per company** via manifest.yaml.
6. **Vendor neutral.** No platform-specific API calls.
7. **Behavior level, not implementation.** Briefs describe what to convey; you decide how to render. Like BDD scenarios.
8. **Destructive changes require explicit user consent.** Default behavior: preserve.
9. **Composable with upstream AI processes.** Content can arrive plain or annotated with metadata; use metadata when present.
10. **Faithful translation, additive expressivity.** Output medium is web technologies (HTML/CSS/JS), not PPT. Floor: never a downgrade. Ceiling: opt-in.
11. **Snapshot stage is host-portable.** Snapshot pipeline runs in any skill-compatible runtime; build/compose/sync are exercised in the AI Design Tool.

## The pipeline

Three named phases:

- **Snapshot stage**: extract a `DesignSystemSnapshot` from the source (slide-specific data plus PNG screenshots). Each source format has its own engine skill: MVP ships `dsk:snapshot-ppt` for PowerPoint. The "engine" is you using the appropriate tools (e.g. python-pptx and LibreOffice for PPT) via tool calls; there is no monolithic engine script. Future engines (`dsk:snapshot-keynote`, `dsk:snapshot-figma`, etc.) are skills that slot in alongside.
- **Build stage**: read the snapshot plus the kernel briefs and produce two artifact categories — **renditions** (web-rendered layouts, examples, and content items, the actual web slides DSK delivers) and **library pages** (the browser around them). Skill: `dsk:build`.
- **Verify pass**: the agent's final acceptance gate before declaring the library ready. Every rendition tile is held next to its source screenshot and confirmed to match on both axes — *structure* (regions, primitives, spatial relationships) and *character* (palette, key imagery, brand marks, decorative motifs, overall feel). Anything that diverges on either axis is fixed before the build is declared done. Implemented by `dsk:align`, which `dsk:build` invokes as its closing stage. `dsk:setup` and `dsk:sync` invoke `dsk:align` again as a fresh skill-boundary pass after build returns — the additional invocation is mechanical, not duplicative: a new skill call gives the agent a fresh attention reset that next-step-in-a-list framing has, in practice, sometimes failed to enforce. Users can also invoke `/dsk:align` directly anytime to run a thorough pass over the existing library without rebuilding from scratch.

## Rendition read/write rules

Renditions (`library/renditions/{layouts,examples,content}/<id>.html`) are the value layer DSK produces. Every skill has well-defined read/write semantics on them; mixing these up silently corrupts the design system, so be precise.

| Skill | Reads | Writes | Modifies existing renditions? |
|---|---|---|---|
| `dsk:build` | snapshot, briefs | renditions + library pages | **Creates** them (overwrites on rebuild) |
| `dsk:align` | rendition + source screenshot + snapshot entry | the same rendition file (only when drift is found) | **Yes — fidelity-only modifier**. Walks renditions in scope (whole library by default, or a user-specified subset), fixes drift toward source. Idempotent: clean renditions are left alone. |
| `dsk:compose` | rendition (as template) | new file in `decks/<...>/slide-XX.html` | **No — read-only**. Compose fills placeholders **in memory** and writes a NEW slide file to the deck folder. The rendition stays untouched and is reused by every subsequent slide using that layout. |
| `dsk:refine` | rendition + source screenshot | the same rendition file | **Yes — user-directed modifier**. Only touches a rendition when the user explicitly asks for a refinement on that specific id; can apply opt-in web expressivity that align would not. |
| `dsk:sync` | new snapshot, old snapshot backup | renditions + library pages | **Regenerates** them when the source has changed. |

The single most important rule: **`dsk:compose` never writes back to a rendition file.** A slide is always a new file under `decks/`, never a modification of the rendition. This is what keeps the design system stable across slides — every slide using the same layout starts from the same trusted template.

User-facing skills layer on top:

- `dsk:setup` orchestrates first-time install.
- `dsk:align` walks renditions and aligns each to its source. Invoked by `dsk:build`, `dsk:setup`, and `dsk:sync` as their closing pass over the whole library; also user-invocable as `/dsk:align` either with no arguments (full library) or with a subset (one or more ids, or a natural-language description like "the bar charts" or "the title slides").
- `dsk:compose` generates slides.
- `dsk:refine` adjusts a specific rendition (layout, example, or content item) based on user feedback. Useful when a rendition drifts from source — common for content items like charts, tables, diagrams.
- `dsk:sync` reconciles after source changes.
- `dsk:route-extension` handles out-of-scope requests.
- `dsk:help` diagnoses state and onboards new users.
- `dsk:dof` is the reference for degrees-of-freedom decisions.

## Lifecycles at a glance

Three core flows you participate in. This section gives you the operational shape; reach for an individual skill's SKILL.md when you actually need to act on one of them. Two companion files alongside this SKILL.md go deeper when needed:

- `${CLAUDE_PLUGIN_ROOT}/skills/context/lifecycles.md` — visual mermaid diagrams of each lifecycle. Show these to the user when explaining where they are.
- `${CLAUDE_PLUGIN_ROOT}/skills/context/walkthrough.md` — end-user-perspective scenarios with `[You]`/`[DSK]` markers. Read this to understand the expected user experience and shape your behavior to match.

- **Setup (once per company).** User drops the declared source file into `source/` and invokes `/dsk:setup`. You ask for company name and DoF settings, write `manifest.yaml` and the `AGENTS.md` DSK section (creating a `CLAUDE.md` symlink so Claude tooling sees the same content), run the snapshot engine skill for the source format (e.g. `dsk:snapshot-ppt` for PowerPoint), then run `dsk:build` to produce the library pages. Build ends with its own internal `dsk:align` invocation as its closing stage; setup invokes `dsk:align` again as a fresh skill-boundary pass over the freshly-generated library. Result: project is ready for slide generation.

- **Compose (per slide, ongoing).** User asks for a slide. You do smart layout selection from the snapshot, then smart content generation, then the DoF decision against the manifest's `silent_up_to` and `ceiling`. At or below `silent_up_to`: generate directly. Above `silent_up_to` but at or below `ceiling`: stop, explain, ask the user to confirm. Above `ceiling`: block; offer the closest valid alternative or invite the user to update the declared source and re-sync. Slides accumulate in `decks/<YYYY-MM-DD>-<slug>/`.

- **Sync (when source changes).** Detected by source mtime newer than the snapshot's `extracted_at`, or invoked explicitly via `/dsk:sync`. Back up the current `snapshot/` to `snapshot.previous/`, re-run the engine skill, diff new vs backup. Additive changes apply silently and trigger `dsk:build`. Destructive or large changes stop and ask the user (principle 8); on confirm, apply and rebuild; on reject, restore the backup over the new snapshot and pause sync.

## Where things live

Two zones, in two different locations on the filesystem:

- **Kernel zone** = this plugin. Skills, briefs, scripts, the shared validator. Identical across companies. Resolved via `${CLAUDE_PLUGIN_ROOT}` (or your runtime's equivalent). **Read-only for normal use** — you read SKILL.md files and scripts from here; you do not write to it.
- **Company zone** = the user's project folder. This is your **current working directory** when the user is chatting with you. Holds: `source/`, `manifest.yaml`, `snapshot/`, `library/`, `decks/`, plus `AGENTS.md` (and a `CLAUDE.md` symlink to it for Claude tooling). **All file outputs you produce land here.**

When a path in any DSK SKILL.md starts with `${CLAUDE_PLUGIN_ROOT}/`, it's plugin-relative (read). Every other path (e.g. `snapshot/`, `library/`, `decks/`) is project-relative (read or write, depending on the skill).

The manifest is the only contact point between zones. Read it for company-specific configuration; never embed company content in kernel files.

## How to behave

- **Pause and ask the user when you would otherwise have to assume something** (no fitting layout, ambiguous intent, unclear rendering choice). Do not guess.
- **Check for source drift on any DSK action that reads the snapshot** (compose, build). Compare the source file's mtime to the snapshot's `extracted_at`. If the source is newer, do not proceed silently; surface "I notice the source was updated since the last snapshot. Want to sync first?" and only continue once the user has chosen. This is what makes `dsk:sync` reliably trigger.
- Apply DoF rules consistently. See `dsk:dof` for the ladder, worked examples, and the governance protocol when a user asks to change DoF settings (treat that as a governance moment, not a usage tweak — explain consequences, recommend checking with the system owner, then apply if confirmed).
- Preserve the confidence users get from PowerPoint or Keynote layouts. A layout from the snapshot should still feel like that exact official layout when rendered in web technologies. Agentic flexibility happens through content fitting, small adaptations, and confirmed stretches, not by silently changing the underlying composition.
- For destructive changes, stop and ask before proceeding (principle 8).
- For requests that need a new layout, content type, or brand element, do not invent them in the company zone. Direct the user to update the declared source of truth and re-sync (`dsk:route-extension` covers this).
- When in doubt, run `dsk:help` to inspect state and surface useful next steps.
- Read `AGENTS.md` in full (or its `CLAUDE.md` symlink — same file). Content outside the `<!-- DSK BEGIN -->` / `<!-- DSK END -->` markers is the canonical place for company-specific rules (writing style, terminology, audience-specific notes). Honor those alongside DSK's rules.
- Use the host AI Design Tool for brand primitives. Claude Design and equivalent hosts may expose colors, typography, logos, assets, and components through their own design-system feature or through direct source-file reading. DSK does not duplicate those primitives in `snapshot.json`; its job is the slide-specific layer (layouts, examples, content catalog, DoF rules). If the host cannot access the brand primitives needed for faithful output, pause and ask the user to connect or provide that source rather than inventing substitutes.
- **Treat re-invocation as routine.** Any DSK skill may be called on a project that already has DSK state — by the same user a second time, by a teammate joining mid-work, or by you after a previous session was interrupted. Before any write-heavy operation, check current state (run `dsk:help`'s `inspect_state.py` if unsure) and prefer continuing or asking over silently overwriting. `dsk:setup` is explicitly gated by a state check; `dsk:sync` backs up before re-snapshotting; `dsk:compose` avoids same-day deck-folder collisions. Apply the same instinct anywhere a write would clobber existing state.
- **Respect host conventions for where work product lives.** DSK's defaults are `decks/<YYYY-MM-DD>-<slug>/` and `library/`, but the host AI Design Tool may have its own preferred locations or naming for user work product (e.g. an `outputs/` folder, a host-managed location, project-specific subdirectories). Resolve the output path in this order: (1) explicit `paths.decks` / `paths.library` overrides in `manifest.yaml`, (2) a host convention you can detect (existing host-managed folders, host config in the project, or established patterns from prior user work in this project), (3) DSK's defaults. When you adapt to a host convention, briefly tell the user where you wrote the file so they can confirm. DSK is vendor-neutral by design (principle 6); the defaults are sensible, not mandatory.
