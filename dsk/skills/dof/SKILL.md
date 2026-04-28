---
description: Reference for degrees of freedom (DoF) — the match / adapt / stretch / deviate ladder, vocabulary, worked examples, and runtime actions. Invoke this from `dsk:compose` and `dsk:sync` whenever you need to classify a proposed change against the company's DoF ceiling and silent threshold.
user-invocable: false
---

# Degrees of Freedom (DoF)

The vocabulary DSK uses to classify proposed changes against a company's brand. `dsk:compose` and `dsk:sync` invoke this skill whenever a proposed change needs to be evaluated against the manifest's DoF settings.

## The four levels

| Level | Definition | Worked examples | Runtime action |
|---|---|---|---|
| **Match** | Use the source layout exactly | Title fits the placeholder; 5-row table; 3-bullet list | Silent |
| **Adapt** | Minor adjustments within the layout's spirit | Title wraps to 2 lines; table grows to 6 rows; list switches to numbered | Silent or footnote in output |
| **Stretch** | Larger changes, still in brand direction | Table becomes a chart; one-column layout used with a sidebar callout; layout color emphasis swapped | Stop, explain rationale, ask user to confirm |
| **Deviate** | Outside brand or layout system | New color introduced; entirely new layout structure; third-party imagery | Block; offer the closest valid alternative, or invite user to update source-of-truth and re-snapshot |

The worked examples turn fuzzy boundaries into reference points. Pattern-match against them when classifying a proposed change.

## How to use this

1. Determine the level (match / adapt / stretch / deviate) by pattern-matching the proposed change against the worked examples above.
2. Read the company's manifest for `dof.ceiling` (the hard cap) and `dof.silent_up_to` (the no-confirmation threshold).
3. Apply the runtime action:
   - At or below `silent_up_to`: proceed without asking.
   - Above `silent_up_to` but at or below `ceiling`: stop, explain, ask the user to confirm.
   - Above `ceiling`: block. Explain why, offer the closest valid alternative, or suggest the user update the declared source of truth and re-sync.

## What "blocked" actually does

When you identify a deviate-level change is required:

1. Stop generating.
2. Explain what was attempted and why it exceeds the DoF ceiling.
3. Offer two paths to the user:
   - Accept the closest valid alternative (downgrade to stretch, or use a different existing layout).
   - Update the declared source of truth and re-sync to legitimize the change (then it's no longer a deviation).

Do not silently downgrade or proceed without the user's choice.

## Default values

If the manifest does not specify DoF settings — or `dsk:setup` ran non-interactively, or the agent failed to ask the user — fall back to a strict default. Don't pick the loosest option silently; default to protecting the user's brand:

- `ceiling: adapt`
- `silent_up_to: match`

Behavior under these defaults:

- **Match** changes (exact source layouts) → silent
- **Adapt** changes (table grows to 6 rows, title wraps) → ask the user to confirm
- **Stretch** changes (table becomes a chart, layout reflow) → blocked; require explicit manifest opt-in
- **Deviate** changes → blocked (always; this is the hard cap regardless of manifest)

Rationale: when the user hasn't explicitly told DSK their tolerance, conservative is the safer floor. Companies that want more agentic latitude raise `ceiling` and/or `silent_up_to` in their `manifest.yaml`.

## When the user wants to change DoF settings

DoF settings are **organizational policy, not personal preference**. The person who configured DSK for this company (typically a brand owner or design system admin) chose those values deliberately to protect the brand. A user asking mid-session to "make it looser" or "skip the confirmations" is asking to relax brand controls — treat that as a governance request, not a usage tweak.

When the user asks to change `ceiling`, `silent_up_to`, or any other DoF field in `manifest.yaml`:

1. **Acknowledge the request and read the current values.** Don't dismiss; the user has a legitimate reason to ask.
2. **Explain what the current settings mean in practical terms.** "Right now `ceiling: adapt, silent_up_to: match` means matches go through silently, adaptations ask you first, and stretches and deviates are blocked entirely."
3. **Explain the consequences of the proposed change in concrete terms.** "Raising `ceiling` to `stretch` means I'll start offering things like 'turn this table into a chart' instead of blocking — still with a confirmation, but the door opens." For looser changes, name the brand risk; for stricter changes, name the friction increase.
4. **Recommend checking with the system owner first.** Frame it as "this is the kind of change a brand owner usually approves," not as a refusal. Suggest the user contact whoever originally set DSK up for the company before applying. If a contact is named in `AGENTS.md`, point at it.
5. **Don't block.** It's the user's project; they have write access to `manifest.yaml`. If they explicitly confirm they want to proceed after hearing the consequences and the recommendation, apply the change:
   - Edit only the field requested; leave everything else in the manifest untouched.
   - Tell them exactly what changed and how to revert ("I've raised `ceiling` from `adapt` to `stretch` in `manifest.yaml`. Revert by editing the file or by re-running `/dsk:setup`.").
   - Do not retroactively re-evaluate past slides; the new setting applies to future composes only.

The bar is **friction with explanation, not silent acceptance and not refusal.** Changing DoF should feel like a small governance moment, because it is one.

## The content gallery's relationship to DoF

The content gallery library page shows content types only up to the company's `ceiling`. When a `ContentItem` has `dof_level`, compare that level to the ceiling. When it does not, treat source-exemplified content as `match`. Content above the ceiling is not advertised to the user.
