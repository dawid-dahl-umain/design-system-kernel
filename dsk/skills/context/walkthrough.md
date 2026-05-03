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
7. `[DSK]` Runs the build stage (`dsk:build`). Produces two categories of artifacts under `library/`:
   - **Renditions** — web-rendered versions of every layout, example, and content item (charts, tables, diagrams, etc.), one file each at `library/renditions/{layouts,examples,content}/<id>.html`. These are the actual slides and content pieces DSK will reuse when you ask for a deck; they're the value layer.
   - **Library pages** — `welcome.html`, `layouts.html`, `examples.html`, `content-gallery.html`. The browser around the renditions; embeds them for navigation.

   **Possible pause for design-system input.** Renditions need styling direction. The agent first checks the runtime for a design system (host-exposed feature like Claude Design's design-system surface, or design tokens / theme files in your project folder). If found, the agent uses it and runs through. If neither is found, the agent stops and asks you in plain English: point at brand guidelines, give it the essentials (colors, fonts, mood), let it approximate from your source screenshots, or use generic tasteful defaults. You pick; the agent acts on the choice for all renditions in this build. Library page chrome doesn't pause — only renditions do, because renditions are the product.

   (`library/` is the DSK default — the agent may write to a different location if your host AI Design Tool has its own convention or if you've configured a different path in `manifest.yaml`; the agent will tell you where in that case.)
8. `[DSK]` Runs the verify pass before declaring the library done. Every rendition tile is held next to its source screenshot and confirmed to match on both axes — structure (regions, primitives, spatial relationships) and character (palette, key imagery, brand marks, decorative motifs, overall feel). Any divergence is fixed before completion. This is internal to build; you see it as part of build wrapping up, not as a separate step.
9. `[You]` Browse the library pages and confirm the renditions look right. The "compare to source" toggle on each entry lets you spot any subtle gap the agent's verify pass didn't catch and ask for refinement.

## 3. Building a deck

The typical workflow: a user has a meeting or report coming up and needs a full deck. The deck builds up slide by slide; each user request adds or revises a slide in the same deck folder.

**How content arrives.** The agent expects content per slide in one of two modes:

- **Plain mode** (most common): you type it in chat, e.g. "a slide showing revenue grew 18% YoY." There's nothing structured about it — just conversation.
- **Annotated mode**: you submit content as a structured payload that carries metadata (`style_hints`, `layout_hints`, `precedents`, `source`). The producer can be anything — an upstream AI system, a traditional content pipeline, an internal knowledge base, even a JSON blob you paste in. DSK doesn't care about the source; it cares that the metadata is attached and uses it to inform layout and rendering choices.

If content is missing or unclear ("just make a slide" with no topic), the agent pauses and asks rather than inventing. If your input doesn't obviously fit either mode, the agent asks how to treat it; if still ambiguous, it falls back to plain mode and does its best with whatever it can extract. You bring the angle and the data; the agent brings the layout and rendering.

1. `[You]` "Start a deck for our Q3 review. First slide: title page." (plain mode)
2. `[DSK]` Loads `dsk:compose` and reads the snapshot. Runs two smart steps:
   - **Smart layout selection** — picks the best matching layout from the snapshot. The chosen layout's rendition file (at `library/renditions/layouts/<id>.html`, generated by `dsk:build`) is the starting template. Uses `layout_hints` and `precedents` from any attached metadata; otherwise infers from your content's structure. If no layout fits cleanly, pauses and asks you instead of guessing.
   - **Smart content generation** — opens the chosen rendition and fills its placeholders with your content. The rendition already encodes the company's design system from build time; compose populates it, doesn't re-render it. Uses `style_hints` from metadata when present, matches against the snapshot's content catalog by structural `type` and the company's `display_name` when defined. Pauses if it would otherwise have to assume a rendering choice.
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

## 4. Refining a rendition that needs adjustment

After setup, while browsing the library, you might notice a rendition that doesn't quite match the source — a chart's legend in the wrong position, a table header missing the brand accent, a title's font weight slightly off. Each library entry has a "compare to source" toggle (hidden by default; reveal it on demand) so you can swap to the source screenshot and spot fidelity gaps. You can ask the agent to fix specific renditions in conversation; this is `dsk:refine`. For the visual flow with the direction × DoF × rendition-type branching, see `lifecycles.md` section 4.

1. `[You]` In the library, spot a fidelity gap on a specific entry (often a content item — charts, tables, diagrams are the most common refinement targets, since they have many small structural details).
2. `[You]` Note the entry's id (each entry shows it; usually click-to-copy). Ask the agent: "fix `<id>` — the legend should be inside the chart area, not on the right" (or similar).
3. `[DSK]` Loads `dsk:refine`. Opens the rendition file plus the source screenshot.
4. `[DSK]` Runs a **direction check**: is this a fidelity correction (toward source), opt-in web expressivity (allowed by principle 10), or a brand/structural divergence (not allowed — needs source-of-truth update)?
   - Fidelity correction or web expressivity → continue.
   - Brand/structural divergence → hand off to `dsk:route-extension`; explain that this kind of change should originate in the source.
5. `[DSK]` Runs a **DoF magnitude check** (same ladder compose uses): if at or below `silent_up_to`, apply silently; if above but at or below `ceiling`, ask you to confirm; if above `ceiling`, block.
6. `[DSK]` Applies the change to the rendition file. For **layout** renditions, includes a propagation note: "this will apply to every future slide using this layout." For **content** renditions, lighter note: "future slides using this content type will use the refined version." For **example** renditions, no propagation (examples are QA-only).
7. `[DSK]` Self-verifies: confirms the refined rendition now matches the source on the dimension that prompted the refine, before reporting back to you.
8. `[You]` Refresh the library page; the embedded rendition reflects the change.

This loop is especially useful for content items (charts, tables, diagrams) where the agent's first pass is most likely to miss source-specific details.

## 5. Updating after the declared source changes

1. `[You]` Brand team updates the declared source (for MVP, something like `source/Acme-Master.pptx`).
2. `[You]` Ask for a slide, or invoke any DSK action.
3. `[DSK]` Checks source mtime against the last snapshot; detects the change.
4. `[DSK]` Surfaces: "I notice the source was updated since the last snapshot. Want to sync first?"
5. `[You]` Confirm.
6. `[DSK]` Loads `dsk:sync`. Backs up the current snapshot, then invokes the engine skill for the declared source (e.g. `dsk:snapshot-ppt`) to produce a new snapshot. Diffs new vs backup.
7. `[DSK]` Additive changes only (new layout, new content type): applies silently, regenerates library pages, runs the verify pass on the regenerated renditions, deletes the backup.
8. `[DSK]` Destructive or large changes (removed layout, renamed layout, major content shift): stops, explains the change and consequence, asks for explicit confirmation (principle 8).
   - On confirm: applies, regenerates library pages, runs the verify pass on the regenerated renditions, deletes the backup.
   - On reject: restores the backup over the new snapshot (returns to pre-sync state) and pauses sync.
9. `[DSK]` Once sync resolves, proceeds with your original action.
