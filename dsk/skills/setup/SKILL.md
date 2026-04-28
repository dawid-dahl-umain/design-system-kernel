---
description: First-time DSK install for a company project. Use for /dsk:setup or when the user says "set up DSK" or similar. Adds the declared source file, writes manifest, generates AGENTS.md project marker (with CLAUDE.md symlink for Claude tooling), writes/extends .gitignore for DSK-managed regenerable artifacts, runs snapshot, runs build.
---

# DSK Setup

Orchestrate the first-time installation of DSK for a company project.

## Preconditions

- The user has a company source-of-truth file ready. MVP expects a PowerPoint source handled by `dsk:snapshot-ppt`.
- DSK plugin is installed in the host AI Design Tool.

## Flow

1. **Detect existing state and fork behavior.** Before writing anything, inspect the project to see whether DSK is already set up. The cheapest way is to invoke `dsk:help` (which runs `inspect_state.py`) or read the key indicators directly: `manifest.yaml`, `AGENTS.md` DSK section, `snapshot/snapshot.json` validity, `library/` completeness.

   **For non-empty branches (anything other than "no DSK artifacts"), invoke `dsk:context` first before deciding what to do.** At that point the project is already a DSK project, and dsk:context's principles and lifecycle summaries inform every state-recovery decision in this step. The "no DSK artifacts" branch can skip dsk:context — there's nothing to load yet, and setup's own SKILL.md carries enough context for the bootstrap.

   **UX principle for every prompt in this step.** When asking the user about state, never expose internal step numbers, skill names, or DSK vocabulary (`snapshot`, `library`, `DoF`, `manifest`). Describe in plain English what happened and what the choices mean. Most users running setup are non-technical (a marketing manager at the company, not a developer). The agent translates between user intent and the underlying invocations.

   Then route based on state:

   - **Empty / no DSK artifacts** → proceed with the full flow below (steps 2–10).

   - **Fully set up** (manifest valid, snapshot valid, library complete): do **not** overwrite. Re-running the full setup would clobber a customized manifest. Ask the user what they actually want, in plain English. Suggested phrasing: "Looks like DSK is already set up here. What would you like to do?"

     Suggested options (agent resolves the chosen option to the right invocation):

     - **My source file changed; pick up the new version.** → invoke `/dsk:sync` (re-reads the source, regenerates the reference library).
     - **Regenerate the reference library pages.** → invoke `/dsk:build` (rebuilds library only, e.g. to fix visual issues).
     - **Change a setting** (company name, agent latitude). → walk the user through the relevant manifest edit.
     - **Show me what state DSK is in.** → invoke `/dsk:help`.

     Wait for the choice before acting.

   - **Partial state** (e.g. manifest present but no snapshot, or snapshot present but no library): complete only what is missing. Skip steps that already produced valid output. Confirm with the user before continuing — describe the gap in plain English, not by step number. Examples:

     - Manifest written but source not yet read: "DSK is partway set up — the configuration file is in place but the agent hasn't read your source file yet. Want me to read it now and finish the setup?"
     - Source read but reference library not generated: "DSK has read your source file but the reference library pages haven't been generated yet. Want me to generate them now?"

   - **Drift detected** (source mtime newer than snapshot's `extracted_at`): tell the user the source has changed and recommend `/dsk:sync` instead of re-running setup. Plain-English version: "Your source file has changed since the last time DSK read it. Want to re-read the new version? (That's `/dsk:sync`.)"

   - **Conflicting state.** Pause and ask before touching anything; never free-form. Use a template per conflict type:

     - **`AGENTS.md` has non-DSK content the agent can't safely preserve.** Describe what's there in user terms, propose adding the DSK section without touching the rest, ask for confirmation. Example: "Your project already has an `AGENTS.md` file with instructions for AI tools. I'd like to add DSK's section to it without changing anything else you've written. OK to proceed?"
     - **`manifest.yaml` has fields I don't recognize.** List the unknown fields, ask whether they're from a newer DSK version (don't touch — recommend updating the plugin) or were added by mistake (offer to remove or ignore them). Don't guess.
     - **Snapshot fails validation.** Say what's invalid in user terms ("the saved version of your design system looks corrupted or incomplete"), recommend `/dsk:sync` to regenerate from the source, and confirm before running.

   Only proceed past this step once the route is clear. Setup must be idempotent: a second invocation on a complete project should never silently destroy customizations.

2. **Verify the declared source is in `source/`.** Check the project root for a supported source file. For MVP, check `source/<file>.pptx`.
   - If missing **and you can ask the user**: ask them to drop the source file into `source/` and confirm when ready.
   - If missing **and running non-interactively**: fail with a clear error message: "no supported source found in source/. For MVP, add a PowerPoint source and re-run /dsk:setup."

3. **Gather configuration.** Use `AskUserQuestion` when available.

   - **Company name** (required).

   - **Latitude preference.** Don't expose DSK's internal vocabulary (`match` / `adapt` / `stretch` / `deviate`) to the user during setup — that's manifest schema, not UX. Most users setting DSK up will be non-technical (e.g. a marketing manager at the company). Ask one plain-English question and translate the answer behind the scenes into `ceiling` and `silent_up_to`.

     Suggested phrasing: "How much creative latitude should the agent have when generating slides for your company?"

     Suggested options (the agent maps the chosen option to manifest values, the user never sees the tokens):

     - **Recommended (most users).** The agent stays close to your existing layouts and content, and confirms any meaningful change with you before applying it. → `ceiling: adapt`, `silent_up_to: match`.
     - **A bit looser.** The agent can take small brand-consistent liberties beyond what's in the source (e.g. an accent color you've used elsewhere) without asking. → `ceiling: stretch`, `silent_up_to: adapt`.
     - **Maximum flexibility.** The agent has wide discretion to depart from the source when it judges it useful. → `ceiling: deviate`, `silent_up_to: stretch`.
     - **Let me set the values manually** (advanced / technical users only). Drop into the four-level vocabulary and ask for `ceiling` and `silent_up_to` separately, with the worked examples from `dsk:dof`.

   - **Defaults if no answer** or running non-interactively: `ceiling: adapt`, `silent_up_to: match` — same as the "Recommended" option above. Strict by design; the user can loosen later by editing `manifest.yaml`.

   - After choices are made, briefly tell the user (one sentence) that DoF settings are stored in `manifest.yaml` under `dof:` and can be adjusted anytime, and that `dsk:dof` documents the full vocabulary if they want the technical reference. This is the bridge: the setup UX stays plain-English, but the door to the underlying model is left open for the curious or the technical.

4. **Create a rollback point before writing setup files.** Record the current state of `manifest.yaml`, `AGENTS.md`, `CLAUDE.md`, and `.gitignore` before editing them. Preserve enough information to restore each path exactly:
   - missing path vs regular file vs symlink;
   - file content for regular files;
   - symlink target for symlinks.

   Also note whether `snapshot/` and `library/` existed before setup. If setup fails before the snapshot stage succeeds, restore the recorded files, remove any newly-created `snapshot/` or `library/`, and report that setup was rolled back. This keeps a failed setup from marking the project as configured.

5. **Write `manifest.yaml`** to the project root. Minimum:

   ```yaml
   version: 0.1
   company:
     name: "<provided>"
   source: source/<filename>.pptx
   dof:
     ceiling: <chosen>
     silent_up_to: <chosen>
   ```

6. **Write or extend `AGENTS.md`** with the DSK section between `<!-- DSK BEGIN -->` and `<!-- DSK END -->` markers. `AGENTS.md` is the cross-vendor agent-context convention (Codex, Cursor, Aider, Copilot, and others read it natively); Claude tooling is bridged via a `CLAUDE.md` symlink (next sub-step).
   - If `AGENTS.md` does not exist: create it.
   - If it exists with no DSK section: append the section at the end.
   - If it exists with a DSK section already: update the section in place.
   - **Existing user content outside the markers must never be modified** (principle 8).

   Section content:

   ```markdown
   # Project context

   This project uses DSK (Design System Kernel) for slide generation.

   - Source of truth: source/<file>
   - Manifest: manifest.yaml

   **Agent: on any interaction with this project, invoke `dsk:context` first** to load DSK's principles and lifecycle context. After that, route to specific `dsk:*` skills based on intent (`dsk:compose` for slide generation, `dsk:sync` after source updates, `dsk:help` for project status, etc.).
   ```

   **Bridge `CLAUDE.md` to `AGENTS.md`.** Claude Code and Claude Design read `CLAUDE.md` by default but follow symlinks transparently. Create a symlink so both filenames point at the same file (zero drift):
   - If `CLAUDE.md` does not exist: create symlink `CLAUDE.md` → `AGENTS.md` (`ln -s AGENTS.md CLAUDE.md`).
   - If `CLAUDE.md` exists as a symlink already pointing at `AGENTS.md`: leave it.
   - If `CLAUDE.md` exists as a real file with content: ask the user before touching it, but recommend the migrate path explicitly and frame the choice in user terms — most users won't know what `AGENTS.md` is or why DSK cares about `CLAUDE.md`.

     Suggested phrasing: "I found an existing `CLAUDE.md` file with content in this project. AI tools have been moving toward a shared instructions file called `AGENTS.md` so that Claude, Codex, Cursor, Copilot and others all see the same project context. I'd like to move your existing `CLAUDE.md` content into `AGENTS.md`, then link `CLAUDE.md` to it so nothing changes for you on the Claude side. That way DSK's instructions are visible to every AI tool you use, without duplication. OK to do that, or would you prefer to keep them separate?"

     Two paths:
     - **Migrate (recommended).** Copy any non-DSK content from `CLAUDE.md` into `AGENTS.md`, then replace `CLAUDE.md` with the symlink. This is the right choice in almost every case.
     - **Keep separate.** Leave `CLAUDE.md` alone. Warn the user explicitly: "If you keep them separate, DSK's instructions will only be visible to AI tools that read `AGENTS.md` — Claude Code and Claude Design read `CLAUDE.md` by default and won't see them. You'd have to manually duplicate the DSK section into `CLAUDE.md` to keep both files in sync."
   - On systems where symlinks are problematic (some Windows configurations), fall back to writing `CLAUDE.md` as a one-line file containing `@AGENTS.md` (Claude Code's import syntax). Note this in your output to the user.

7. **Write or extend `.gitignore`** with the DSK section between `# DSK BEGIN` and `# DSK END` markers. Same idempotent pattern as `AGENTS.md`:
   - If `.gitignore` does not exist: create it.
   - If it exists with no DSK section: append the section at the end.
   - If it exists with a DSK section already: update the section in place.
   - **Existing user content outside the markers must never be modified** (principle 8).

   Section content:

   ```gitignore
   # DSK BEGIN
   # Regenerable DSK artifacts (principle 2). Recreate by re-running snapshot + build.
   snapshot/
   library/
   snapshot.previous/
   # DSK END
   ```

   Rationale: `source/`, `manifest.yaml`, `AGENTS.md`, the `CLAUDE.md` symlink, and `decks/` represent user-owned content (input, config, project marker, work product) and should be tracked. `snapshot/` and `library/` are build artifacts. `snapshot.previous/` is a transient backup `dsk:sync` creates and removes; it should never be committed.

8. **Run the snapshot stage** by invoking the snapshot engine skill for the declared source (`dsk:snapshot-ppt` for a PowerPoint source; future engines for other formats). This produces `snapshot/snapshot.json` plus PNG assets in the company zone. Once this stage validates successfully, the core setup files may stay in place even if the later build stage needs a retry.

9. **Run the build stage** by invoking `dsk:build`. This produces `library/welcome.html`, `library/layouts.html`, `library/examples.html`, `library/content-gallery.html`.

10. **Confirm completion to the user.** Point them at `library/welcome.html` as the entry point, using whatever consumption channel your runtime supports — host-native preview if the host AI Design Tool renders HTML inline, otherwise instruct them to open the file in a browser. Then suggest they start building decks via chat.

## Failure handling

- If snapshot fails (parsing error, missing dependency): explain the issue, restore the rollback point, remove partial generated artifacts, and offer to retry. Do not leave a partial manifest, partial `AGENTS.md`, partial `CLAUDE.md`, partial `.gitignore`, or partial `snapshot/`.
- If build fails after snapshot succeeds: snapshot is preserved; the user can re-invoke `/dsk:build` later.
- If `AGENTS.md`, `CLAUDE.md`, or `.gitignore` has unusual existing content that's hard to preserve safely: ask the user before editing.
