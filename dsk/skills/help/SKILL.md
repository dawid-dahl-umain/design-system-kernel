---
description: Diagnose a DSK project's state and recommend the next action. Use when the user asks for help, status, "what's set up", "where am I", or runs /dsk:help. Onboards new users.
allowed-tools: Bash(python3 *)
---

# DSK Help

Diagnose a DSK project's state and tell the user what to do next.

## How

1. Run `inspect_state.py` (in this skill's folder) against the project root. It returns a structured JSON report of what is present in the company zone and what is missing.
2. Summarize the report in concise human-readable form. Cover: setup state (manifest, source, snapshot, library), drift between source mtime and last snapshot, deck count, any validation issues.
3. Recommend the next concrete action.

## Recommendation rules

- **Empty folder** → "Drop your company's source file into `source/` and run `/dsk:setup`. For MVP, use a PowerPoint source."
- **Source present but no manifest or snapshot** → "Run `/dsk:setup` to complete installation."
- **Source updated since last snapshot** → "Source has changed. Run `/dsk:sync` to reconcile."
- **Setup complete, no decks yet** → "You're ready. Say 'Make me a slide for...' to start a deck."
- **Validation failure** → explain the specific issue and recommend re-running the snapshot engine for the declared source (e.g. `/dsk:snapshot-ppt` for PPT sources).
- **All systems green** → confirm setup is healthy and remind the user how to start a deck.

## Onboarding new users

If the user appears new (empty folder, asks "what is this?"), briefly explain: DSK turns a company's declared design system source into an AI-readable slide system. Drop the source in `source/` (PowerPoint for MVP), then build decks by chatting. Output is web pages, not PPT files. `/dsk:setup` starts you off.

Be concise. Action-oriented. Not over-explanatory. The user can ask follow-up questions for depth.
