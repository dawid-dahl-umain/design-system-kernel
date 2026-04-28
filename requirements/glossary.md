# Glossary

Abbreviations and short term definitions used across the docs. For full treatments, follow the links.

## Abbreviations

- **DSK** — Design System Kernel. The thing this repository describes.
- **DoF** — Degrees of Freedom. The match / adapt / stretch / deviate ladder. See [degrees-of-freedom.md](degrees-of-freedom.md).

## Terms

- **AI Design Tool.** Generic term for the host environment DSK plugs into. Claude Design today, Claude Code or any equivalent folder-and-file based agentic environment in the future.
- **Source of truth.** The authoritative input DSK reads from. MVP primary source is a PowerPoint master file, but the model is engine-neutral. See [source-of-truth.md](source-of-truth.md).
- **Manifest.** The small per-company config file that declares sources, the DoF ceiling, and any per-dimension overrides. Lives in the company zone.
- **Kernel zone.** The portable, company-agnostic part of the system. Identical across every install. See [separation.md](separation.md).
- **Company zone.** The per-company part. Holds source of truth, manifest, finished decks. See [separation.md](separation.md).
- **DesignSystemSnapshot (snapshot).** The typed output of a snapshot engine. Layouts, examples, content catalog, fallbacks. See [types.md](types.md).
- **Snapshot engine.** A deterministic tool that reads a source format and emits a snapshot. MVP ships the PPT Snapshot Engine. See [snapshotting.md](snapshotting.md).
- **Snapshotting.** Stage 1 of the DSK pipeline: engine reads source, writes snapshot. See [snapshotting.md](snapshotting.md).
- **Build.** Stage 2 of the DSK pipeline: agent reads snapshot plus briefs, produces the library — both renditions (web-rendered layouts and examples) and library pages (the browser around them). See [outputs.md](outputs.md).
- **Library page.** One of the web pages DSK causes to be generated for humans (welcome, layouts, examples, content gallery). Lives at the top of `library/` in the company zone. See [outputs.md](outputs.md).
- **Rendition.** A web-rendered version of a layout or example from the snapshot, produced by `dsk:build` and stored as one HTML file each at `library/renditions/{layouts,examples}/<id>.html`. Reused by `dsk:compose` as starting templates when generating slides. The actual product DSK delivers; the library pages are the browser around them. See [outputs.md](outputs.md).
- **Web technologies.** The umbrella term used in these docs for HTML, CSS, JavaScript, and related browser-rendered media. The output medium of DSK; distinct from whatever source format the snapshot engine reads.
- **Brief.** Behavior-level spec the agent reads to know what an artifact must convey. Not a template. See [internal-configuration.md](internal-configuration.md) and principle 7.
- **ContentRequest.** The shape content arrives in for slide generation. Plain (no metadata) or annotated (with metadata). See [content-input.md](content-input.md).

---

[← Back to overview](../REQUIREMENTS.md)
