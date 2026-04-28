# Degrees of freedom

Vocabulary: match, adapt, stretch, deviate. Each company sets a ceiling and a silent threshold in its manifest.

## Levels

| Level | Definition | Worked examples | Runtime action |
|---|---|---|---|
| Match | Use the source layout exactly | Title fits placeholder; 5-row table; 3-bullet list | Silent |
| Adapt | Minor adjustments within the layout's spirit | Title wraps to 2 lines; table grows to 6 rows; list switches to numbered | Silent or footnote in output |
| Stretch | Larger changes, still in brand direction | Table becomes a chart; one-column layout used with a sidebar callout | Stop, explain rationale, ask user to confirm |
| Deviate | Outside brand or layout system | New color introduced; entirely new layout structure; third-party imagery | Block; offer the closest valid alternative, or invite user to update source-of-truth and re-snapshot |

The worked examples turn fuzzy boundaries into reference points the agent pattern-matches against.

## Manifest configuration

Two values per company (see [types.md](types.md)):

- `ceiling`: the hard cap. Anything beyond requires source-of-truth changes.
- `silent_up_to`: everything up to and including this level proceeds without user confirmation.

Strict example (also the default when `manifest.yaml` does not specify): `ceiling: adapt`, `silent_up_to: match`. Looser example: `ceiling: stretch`, `silent_up_to: adapt`. Strictest possible: `ceiling: match`, `silent_up_to: match` (only exact-source matches allowed; any adaptation, stretch, or deviation is blocked — typically only used for highly regulated brand environments).

## What "blocked" means at deviate

When the agent identifies a deviate-level change is required:

1. Stop generating.
2. Explain what was attempted and why it exceeds the DoF ceiling.
3. Offer two paths: accept the closest valid alternative (downgrade to stretch, or use a different existing layout), or update the source of truth and re-sync to legitimize the change.

The content gallery displays content types up to the configured ceiling.

---

[← Back to overview](../REQUIREMENTS.md)
