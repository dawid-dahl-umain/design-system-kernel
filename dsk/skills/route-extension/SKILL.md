---
description: Handle requests that require extending the design system itself (new layout, new content type, new brand element). Use when a user's slide request implies adding to the system rather than using existing primitives. Redirects user to update the declared source of truth and re-sync (principle 1).
---

# DSK Route Extension

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

When a user request would require extending the design system itself (a new layout, a new content type, a new brand element not in the snapshot), do not invent it inside the company zone. The source of truth is authoritative and the only origin (principle 1).

## When this skill applies

The user asks for something like:

- "Add a new layout for case studies."
- "Use a different color for emphasis."
- "Make me a slide with a Sankey diagram." (when no diagrams of that type are in the snapshot)
- "Change how the title bar looks across all layouts."

These all imply changes to the system, not just usage of it.

## What to do

1. **Explain the constraint.** Tell the user, briefly: DSK does not invent layouts, content types, or brand elements on its own. New primitives originate in the declared source of truth.

2. **Recommend the path.** Two options:
   - **Update the declared source of truth** to include the desired new layout, content type, or brand element, then run `/dsk:sync` to bring the change into DSK. This is the canonical path.
   - **Use the closest existing primitive instead.** Suggest one or two alternatives from the current snapshot that come close to what they want. Make the offer; don't decide unilaterally.

3. **Do not proceed silently.** Do not generate a slide that would require the new primitive without the user's explicit confirmation that they accept a fallback. If they confirm an alternative, hand off to `dsk:compose` with the alternative.

## How to recognize "extension required"

A request is an extension request if it cannot be satisfied by:

- An existing layout in the snapshot.
- An existing content type in the snapshot.
- The brand elements (colors, typography, logos) the agent has access to.

If the request can be satisfied at the **stretch** DoF level using existing primitives, that's not an extension — it's a normal compose request with confirmation. Only **deviate**-level requests trigger this skill.

(Invoked by you from `dsk:compose` when you detect a deviate-level request, or directly when the user explicitly asks to extend the design system.)
