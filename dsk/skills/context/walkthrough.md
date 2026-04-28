# Walkthrough — DSK from a user's perspective

Concrete step-by-step scenarios showing what a user does, what the agent does in response, and what artifacts result. Read by you (the agent) when invoked from `dsk:context`, so you understand the expected user experience and shape your behavior to match. Read this for narrative calibration, not for visual reference; for diagrams of the same lifecycles see `lifecycles.md` alongside this file.

The typical use of DSK is building out a complete slide deck slide by slide, with the agent picking layouts and applying brand rules for each. It's not designed for one-off slides in isolation; the value compounds across a deck.

`[You]` marks user actions; `[DSK]` marks what the agent does in response. Every action below happens inside the company zone (`source/`, `manifest.yaml`, `snapshot/`, `library/`, `decks/`).

## 1. Installing DSK for the first time

1. `[You]` Obtain the DSK plugin (marketplace install, `npx skills add`, or local clone of the source repo).
2. `[You]` Place it in your AI Design Tool's plugin directory, or use `--plugin-dir <path>` for testing.
3. `[You]` Run `/reload-plugins` if the host requires explicit refresh.
4. `[You]` Verify: type `/dsk:` for autocomplete, or ask "what DSK skills are available?".

## 2. Setting up a new company project

1. `[You]` Open an empty project folder in your AI Design Tool.
2. `[You]` Drop the company's declared source file into `source/` (for MVP, a PowerPoint master such as `source/Acme-Master.pptx`).
3. `[You]` Invoke `/dsk:setup`, or say something like "set up DSK for this company".
4. `[DSK]` Asks: company name, DoF ceiling, silent threshold. Strict defaults if not specified: `ceiling: adapt`, `silent_up_to: match` (the agent stays close to the source unless you opt into more latitude).
5. `[DSK]` Writes `manifest.yaml`; writes or extends `AGENTS.md` and creates a `CLAUDE.md` symlink to it (existing user content preserved per principle 8).
6. `[DSK]` Runs the snapshot stage by invoking the engine skill for the declared source (`dsk:snapshot-ppt` for a PowerPoint source in MVP). Produces `snapshot/snapshot.json` plus PNG assets.
7. `[DSK]` Runs the build stage (`dsk:build`): produces `library/welcome.html`, `library/layouts.html`, `library/examples.html`, `library/content-gallery.html`. (`library/` is the DSK default — the agent may write to a different location if your host AI Design Tool has its own convention or if you've configured a different path in `manifest.yaml`; the agent will tell you where in that case.)
8. `[You]` Browse the library pages and confirm the design system looks right.

## 3. Building a deck

The typical workflow: a user has a meeting or report coming up and needs a full deck. The deck builds up slide by slide; each user request adds or revises a slide in the same deck folder.

**How content arrives.** The agent expects content per slide in one of two modes:

- **Plain mode** (most common): you type it in chat, e.g. "a slide showing revenue grew 18% YoY." There's nothing structured about it — just conversation.
- **Annotated mode**: you submit content as a structured payload that carries metadata (`style_hints`, `layout_hints`, `precedents`, `source`). The producer can be anything — an upstream AI system, a traditional content pipeline, an internal knowledge base, even a JSON blob you paste in. DSK doesn't care about the source; it cares that the metadata is attached and uses it to inform layout and rendering choices.

If content is missing or unclear ("just make a slide" with no topic), the agent pauses and asks rather than inventing. If your input doesn't obviously fit either mode, the agent asks how to treat it; if still ambiguous, it falls back to plain mode and does its best with whatever it can extract. You bring the angle and the data; the agent brings the layout and rendering.

1. `[You]` "Start a deck for our Q3 review. First slide: title page." (plain mode)
2. `[DSK]` Loads `dsk:compose` and reads the snapshot. Runs two smart steps:
   - **Smart layout selection** — picks the best matching layout. Uses `layout_hints` and `precedents` from any attached metadata; otherwise infers from your content's structure. If no layout fits cleanly, pauses and asks you instead of guessing.
   - **Smart content generation** — fills the chosen layout with your content. Uses `style_hints` from metadata when present, matches against the snapshot's content catalog by structural `type` and the company's `display_name` when defined, and applies brand primitives from the host AI Design Tool. Pauses if it would otherwise have to assume a rendering choice.
3. `[DSK]` Creates the deck folder (DSK default: `decks/<YYYY-MM-DD>-<slug>/`, e.g. `decks/2026-04-25-q3-review/`) and writes the first slide there. The agent may write elsewhere if your host AI Design Tool has its own convention for user work product or if you've configured a different path in `manifest.yaml`; in that case the agent says where.
4. `[You]` "Next: a slide showing revenue grew 18% year over year."
5. `[DSK]` Generates the next slide; same DoF rules apply per slide; saves it to the same deck folder.
6. `[DSK]` DoF decision per slide. The action depends on where the proposed change falls relative to the manifest's `silent_up_to` and `ceiling`. With the strict defaults (`ceiling: adapt`, `silent_up_to: match`):
   - **At or below `silent_up_to`** (Match only, by default): generate directly.
   - **Above `silent_up_to` but at or below `ceiling`** (Adapt by default): stops, explains the proposed change, asks you to confirm.
   - **Above `ceiling`** (Stretch and Deviate by default): blocks, offers the closest valid alternative, or invites you to update the declared source and re-sync.
7. `[DSK]` If the agent would otherwise have to assume something (no fitting layout, ambiguous intent), it asks you instead of guessing.
8. `[You]` Continue iterating until the deck is complete. Revise earlier slides as needed; ask for variants; reorder.

The deck accumulates in whatever folder the agent picked at step 3 (DSK default: `decks/<YYYY-MM-DD>-<slug>/`; can be a host-specific location). You're never locked into the first version of any slide.

## 4. Updating after the declared source changes

1. `[You]` Brand team updates the declared source (for MVP, something like `source/Acme-Master.pptx`).
2. `[You]` Ask for a slide, or invoke any DSK action.
3. `[DSK]` Checks source mtime against the last snapshot; detects the change.
4. `[DSK]` Surfaces: "I notice the source was updated since the last snapshot. Want to sync first?"
5. `[You]` Confirm.
6. `[DSK]` Loads `dsk:sync`. Backs up the current snapshot, then invokes the engine skill for the declared source (e.g. `dsk:snapshot-ppt`) to produce a new snapshot. Diffs new vs backup.
7. `[DSK]` Additive changes only (new layout, new content type): applies silently, regenerates library pages, deletes the backup.
8. `[DSK]` Destructive or large changes (removed layout, renamed layout, major content shift): stops, explains the change and consequence, asks for explicit confirmation (principle 8).
   - On confirm: applies, regenerates library pages, deletes the backup.
   - On reject: restores the backup over the new snapshot (returns to pre-sync state) and pauses sync.
9. `[DSK]` Once sync resolves, proceeds with your original action.
