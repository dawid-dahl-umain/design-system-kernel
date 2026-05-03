# DSK: Slides — Requirements

Draft v0. Focused and editable.

## Purpose

DSK is a family of plugins that turn a company's declared source of truth into an AI-readable design system, with stable intermediate snapshots and faithful web-rendered artifacts. **DSK: Slides** is the slides plugin in that family: it plugs into any folder-based AI Design Tool (Claude Design today, others later) and turns a company's declared slide-system source into an AI-readable slide system. Employees generate on-brand slides by chatting with the agent, not by composing manually in PowerPoint or Keynote. MVP uses a PowerPoint snapshot engine; the kernel contract is source-engine neutral. Future DSK plugins for other artifact families (posters, reports, branded documents, etc.) would follow the same source → snapshot → renditions shape, but those are out of scope for this document.

"AI Design Tool" is the generic term used throughout these docs for Claude Design or any equivalent folder-and-file based agentic design environment. DSK: Slides is deliberately not coupled to any specific one.

## Contents

Each topic lives in its own file under `requirements/`. New readers: start with **Principles**, then **Architecture**, then dig into specifics. For the system in use (end-user scenarios) and the runtime lifecycle diagrams, see the plugin at `dsk/skills/context/walkthrough.md` and `dsk/skills/context/lifecycles.md` — those live inside the plugin because they are runtime references for the agent.

### Concepts (the rules and ideas)

- [Principles](requirements/principles.md) — the rules of DSK itself
- [Source of truth](requirements/source-of-truth.md) — the per-dimension source model
- [Degrees of freedom](requirements/degrees-of-freedom.md) — match, adapt, stretch, deviate

### Architecture (the system shape)

- [Architecture](requirements/architecture.md) — system context diagram and how the parts relate
- [Separation](requirements/separation.md) — kernel zone vs company zone
- [Internal configuration](requirements/internal-configuration.md) — the concrete parts DSK is made of
- [Types](requirements/types.md) — formal shapes of DSK data structures

### Pipeline (data flowing through DSK)

- [Inputs](requirements/inputs.md) — what DSK always requires
- [Snapshotting](requirements/snapshotting.md) — phase 1: engine reads source, writes snapshot; build and verify (phases 2 and 3) summarized at the end
- [Content input](requirements/content-input.md) — plain and annotated modes for slide content
- [Outputs](requirements/outputs.md) — what DSK produces (and what it does not)

### Behavior (how DSK acts over time)

- [Developer testing](requirements/developer-testing.md) — DSK maintainer perspective; testing the snapshot stage outside an AI Design Tool

The runtime behavior references — end-user-perspective scenarios and the lifecycle diagrams (setup, compose, sync) — live inside the plugin alongside the `dsk:context` skill: `dsk/skills/context/walkthrough.md` and `dsk/skills/context/lifecycles.md`. They are loaded by the agent at runtime and form the canonical reference for how DSK operates.

### Reference

- [Glossary](requirements/glossary.md) — abbreviations and short term definitions
- [Open questions](requirements/open-questions.md) — still to be decided
