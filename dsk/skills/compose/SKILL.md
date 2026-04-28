---
description: Generate a slide. Use when the user asks for a slide, says "make me a slide", "add a slide", "start a deck", wants to revise an existing slide, or runs /dsk:compose. Smart layout selection plus smart content generation plus DoF decision.
---

# DSK Compose — Generate a Slide

**First:** if this is your first DSK action in this chat session, invoke `dsk:context` to load principles and lifecycle context before continuing.

Generate a slide for the user, using the snapshot, the briefs, the manifest, and any metadata that arrives with the content. The typical use case is building out a multi-slide deck one slide at a time.

## Authoring model

The user is using the AI Design Tool instead of PowerPoint or Keynote, but they should get the same confidence that official layouts remain official layouts. Treat the snapshot as the allowed slide system: layout screenshots and placeholder structures are constraints to preserve, not loose inspiration.

Your added value is that the user can chat instead of manually composing, and that slides can change more fluidly within the company's configured DoF. Match first. Adapt when the content needs it. Stretch only with confirmation when the manifest requires it. Do not silently turn an official layout into a different composition.

## Inputs

- The user's content. `ContentRequest` is the conceptual shape; in practice content arrives in one of two modes:
  - **Plain mode** (most common): the user types content into the chat conversation. There is no formal `ContentRequest` object on the wire — the chat message itself is the content. No metadata.
  - **Annotated mode**: content arrives as a structured payload that carries metadata. The producer can be anything — an upstream AI system, a traditional software pipeline, an internal knowledge base, a content generator, the user pasting in a JSON blob. DSK does not care about the source; it cares that the metadata is attached. Conventional keys DSK acts on when present: `style_hints` (free-form rendering guidance), `layout_hints` (layout suggestions; validate against the snapshot catalog), `precedents` (references to past slides for similar content), `source` (origin identifier). Other keys in the metadata bag are forwarded to you for interpretation.
- The snapshot in the company zone (`snapshot/snapshot.json` plus assets).
- The manifest's `dof.ceiling` and `dof.silent_up_to`.
- Any in-flight deck the user is building (look in `decks/` for the most recent or referenced one).

## What to do

Before any smart step, confirm you have content to work with. Compose has two operating modes for receiving it:

- **Plain mode** (most common): the user types the content in chat. Take the chat message as the content payload; there is no structured object to parse.
- **Annotated mode**: content arrives as a structured payload bundled with metadata (`style_hints`, `layout_hints`, `precedents`, `source`). The producer can be any system — AI or otherwise. Carry the metadata into the smart steps below.

**If you can't classify the input** (e.g. the user pastes something structured but you don't recognize the metadata shape, or the content is genuinely ambiguous), ask the user how to treat it. **If they can't or won't classify and the input is too vague to disambiguate, default to plain mode** — extract whatever content you can interpret as a slide payload and proceed best-effort. Robustness over rigidity: a sensible plain-mode result is better than refusing to act on ambiguous input.

**If content is missing, ambiguous, or under-specified, pause and ask before running smart layout selection.** Examples that warrant asking:

- The user said "make me a slide" with no topic or content.
- The user gave a topic but no concrete data (e.g. "a slide about Q3" with no numbers, narrative, or angle).
- The content references information the agent doesn't have access to ("show our Acme campaign metrics" without the metrics).
- The user's intent could plausibly map to several different content types.

Never invent content. The user brings the angle and judgment; you bring the layout and rendering. Once content is clear, run the two smart steps and the DoF decision below.

### 1. Smart layout selection

Read `snapshot/snapshot.json` from the company zone. Pick the best matching layout from its `layouts` array.

- Use `layout_hints` from metadata if present (validate they exist in the catalog; override if the suggestion does not fit the content).
- Use `precedents` from metadata if present, to bias toward layouts used in similar past slides.
- Otherwise, infer from the content's structure: title-only → title slide; title plus body text → content layout; title plus tabular data → table layout; etc.
- **If no fitting layout exists or intent is ambiguous, stop and ask the user for clarification.** Do not guess.

### 2. Smart content generation

Fill the chosen layout with the user's content.

- Use `style_hints` from metadata if present, for rendering guidance.
- Use the snapshot's `notes` fields on layouts and content items for construction conventions.
- When matching user intent to a `ContentItem` (e.g. user asks for "a Pulse Chart"), check both the structural `type` and the optional `display_name` field. `display_name` carries the company's preferred name when one exists; prefer it for user-facing matching.
- If a matching `ContentItem` has `dof_level`, use that as the starting point for the DoF decision, then raise the level if the user's specific request requires more liberty.
- Apply slide rules from the snapshot (placeholder types, structure, content catalog) and brand primitives from the host AI Design Tool or the readable source files. Do not assume brand primitives are encoded in `snapshot.json`.
- **If you would otherwise have to assume a rendering choice (chart type, color emphasis, layout reflow), stop and ask the user.**

### 3. DoF decision

Determine the DoF level of the proposed change (`dsk:dof` provides the ladder, worked examples, and the threshold rules). Then apply the runtime action by comparing the level to the manifest's `silent_up_to` and `ceiling`:

- **At or below `silent_up_to`**: generate directly. Note Adapt-level changes in the output if any.
- **Above `silent_up_to` but at or below `ceiling`**: stop, explain the proposed change, ask the user to confirm.
- **Above `ceiling`**: hand off to `dsk:route-extension` (block, offer the closest valid alternative, or invite the user to update the declared source of truth and re-sync).

Do not hardcode specific level→action mappings. The thresholds are per-company; the action depends on where the proposed change falls relative to those thresholds.

## Output

A slide rendered as web technologies (HTML, CSS, JS). Save it into the appropriate deck folder.

Resolve the deck location in this order (per `dsk:context`):

1. `manifest.yaml` `paths.decks` if explicitly set.
2. A host AI Design Tool convention you can detect for user work product (existing host-managed output folders, host project config, established patterns from prior decks in this project).
3. DSK default: `decks/<YYYY-MM-DD>-<slug>/` at the project root.

Then:

- If continuing an existing deck (user's recent context or explicit reference), save into the same deck folder it already lives in.
- If starting a new deck, create a new folder using today's date and a slug derived from the deck's working title or purpose. Briefly tell the user where you wrote the file when you depart from the DSK default.
- If a folder with that exact path already exists (same date and slug, possibly from an earlier same-day deck on the same topic), do not overwrite it. Append a numeric suffix (`-2`, `-3`, …) until you find a free path, and tell the user there was a collision so they can rename or merge if they prefer.

Each slide is a separate file inside its deck folder (`slide-01.html`, `slide-02.html`, etc.). Optionally maintain an `index.html` in the deck folder for navigation.

After writing slides, surface them to the user using whatever consumption and export channels your runtime supports:

- **Host-native preview and export if available.** If the host AI Design Tool renders HTML inline and offers export to PPTX, PDF, public URL, Canva, or similar, use those — tell the user which options are on the table and let them pick. The HTML files in `decks/` remain the source of truth; host export is a delivery channel.
- **Otherwise fall back to filesystem and browser.** Tell the user where the files were written and how to view them (open `slide-01.html` or `index.html` in a browser). They can still hand the deck folder off downstream (zip it, commit it, pipe it to another tool).

Same artifacts in either case; the runtime determines the delivery options, not DSK. Do not hardcode host names or assume specific export targets exist.

## When the user revises

The user can ask for revisions of any slide in the active deck. Treat each revision as a new compose call against the same deck folder; overwrite the slide file or version it (e.g. `slide-03.v2.html`) as appropriate.

## When the user is starting fresh

If no current deck context exists and the user requests their first slide, ask the working title or purpose of the deck before generating, so the deck folder is named meaningfully.
