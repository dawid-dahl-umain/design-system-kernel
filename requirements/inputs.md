# Inputs — What DSK always requires

## From the company (dropped into the company zone)

1. Source of truth. A declared design system source that an engine can snapshot. MVP supports a PowerPoint file with a defined slide master. Additional sources (Keynote, Google Slides, Figma exports, design tokens, brand PDFs) are future or optional and declared in the manifest as engines exist.
2. Manifest. A small config file stating where the source of truth lives, the degrees of freedom ceiling, and any per-dimension source overrides. Sensible defaults exist for most fields, so the minimum viable manifest is a few lines.

## Environment prerequisites

- The kernel zone: DSK's fixed portion, copied verbatim into the working folder. See [separation.md](separation.md) for what it contains.
- An AI Design Tool: Claude Design or any equivalent folder-and-file based agentic environment for full pipeline use. For snapshot-stage development and testing, Claude Code or Codex (or any skill-compatible runtime) works equally well; see principle 11.

---

[← Back to overview](../REQUIREMENTS.md)
