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

   Then route based on state:

   - **Empty / no DSK artifacts** → proceed with the full flow below (steps 2–10).
   - **Fully set up** (manifest valid, snapshot valid, library complete): do **not** overwrite. Tell the user: "DSK is already set up here. Did you want to re-snapshot the source (`/dsk:sync`), rebuild the library (`/dsk:build`), or change a config value (DoF settings, company name)?" Wait for their choice. Re-running the full setup would clobber a customized manifest.
   - **Partial state** (e.g. manifest present but no snapshot, or snapshot present but no library): complete only what is missing. Skip steps that already produced valid output. Confirm with the user before continuing: "Looks like DSK setup was started but not finished — picking up at <step>. OK?"
   - **Drift detected** (source mtime newer than snapshot's `extracted_at`): tell the user the source has changed and recommend `/dsk:sync` instead of re-running setup.
   - **Conflicting state** (existing `AGENTS.md` with non-DSK content the agent can't safely preserve, manifest with unrecognized fields, snapshot that fails validation): pause and ask the user how to proceed before touching anything.

   Only proceed past this step once the route is clear. Setup must be idempotent: a second invocation on a complete project should never silently destroy customizations.

2. **Verify the declared source is in `source/`.** Check the project root for a supported source file. For MVP, check `source/<file>.pptx`.
   - If missing **and you can ask the user**: ask them to drop the source file into `source/` and confirm when ready.
   - If missing **and running non-interactively**: fail with a clear error message: "no supported source found in source/. For MVP, add a PowerPoint source and re-run /dsk:setup."

3. **Gather configuration.** Ask the user for the following (use `AskUserQuestion` when available; otherwise fall through to defaults or values from a manifest stub):
   - Company name (required).
   - DoF ceiling: `match` / `adapt` / `stretch` / `deviate`. **Default if unset or unasked: `adapt`** (strict; stretch and deviate require explicit opt-in).
   - DoF silent threshold (`silent_up_to`): `match` / `adapt` / `stretch` / `deviate`. **Default if unset or unasked: `match`** (strict; even adaptations require user confirmation).

   When asking the user, briefly explain the trade-off: looser settings (e.g. `ceiling: stretch, silent_up_to: adapt`) give the agent more agentic latitude per slide; stricter settings keep the agent closer to the source. If the user is unsure, prefer the strict defaults — they can always loosen later in `manifest.yaml`.

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
   - If `CLAUDE.md` exists as a real file with content: ask the user before touching it. Two paths:
     - **Migrate (recommended):** copy any non-DSK content from `CLAUDE.md` into `AGENTS.md`, then replace `CLAUDE.md` with the symlink.
     - **Keep separate:** leave `CLAUDE.md` alone; the user accepts that DSK directives live only in `AGENTS.md` and the Claude-side experience may not see them. Warn the user explicitly.
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

10. **Confirm completion to the user.** Suggest they browse `library/welcome.html` first, then start building decks via chat.

## Failure handling

- If snapshot fails (parsing error, missing dependency): explain the issue, restore the rollback point, remove partial generated artifacts, and offer to retry. Do not leave a partial manifest, partial `AGENTS.md`, partial `CLAUDE.md`, partial `.gitignore`, or partial `snapshot/`.
- If build fails after snapshot succeeds: snapshot is preserved; the user can re-invoke `/dsk:build` later.
- If `AGENTS.md`, `CLAUDE.md`, or `.gitignore` has unusual existing content that's hard to preserve safely: ask the user before editing.
