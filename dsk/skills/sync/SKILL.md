---
description: Reconcile DSK after the declared source has changed. Use for /dsk:sync, when source mtime differs from the snapshot, or when the user says "sync". Re-snapshots, diffs, and applies changes; asks user for destructive or large changes (principle 8).
---

# DSK Sync — Reconcile After Source Changes

Run when the declared source has been updated and the snapshot is stale.

## When to invoke

- User runs `/dsk:sync`.
- You detect drift (source mtime newer than snapshot's `extracted_at`) on any DSK action. In that case, surface a polite reminder: "I notice the source was updated since the last snapshot. Want to sync first?" — and proceed only if confirmed.

## Steps

1. **Back up the current snapshot.** Move (or copy) the existing `snapshot/` directory to `snapshot.previous/` — a sibling folder at the project root, not loose files scattered elsewhere. The name is fixed: `snapshot.previous/` is the canonical backup location, matches the `.gitignore` entry that `dsk:setup` writes (so it never gets committed), and lives in the company zone alongside `snapshot/`. Do not pick a different name; do not place it inside `snapshot/` itself; do not write it to the host AI Design Tool's root or any other location. This preserves the old state for diffing and rollback in step 4.

2. **Re-snapshot.** Invoke the snapshot engine skill for the declared source (e.g. `dsk:snapshot-ppt` for PPT sources). It writes the new snapshot to the standard `snapshot/` location (snapshot always overwrites; that's its contract).

3. **Diff against the backup.** Compare `layouts`, `examples`, `content_catalog`, and `fallbacks` between the backup and the new snapshot. Classify each change as additive or destructive/large:

   **Additive (apply silently):**
   - New layout added.
   - New example added.
   - New content type added.
   - New fallback recorded.
   - Existing layout's `notes` updated.

   **Destructive or large (ask user, per principle 8):**
   - Layout removed from source.
   - Example removed.
   - Content type removed.
   - Layout renamed (treat as removal plus addition; ambiguous intent — ask).
   - Layout's placeholders structurally changed (placeholder removed, type changed).
   - Master visual changes that materially affect existing decks.

4. **Apply changes.**
   - Additive only: keep the new snapshot in place, regenerate library pages via `dsk:build`, then delete the backup. Done.
   - Destructive or large: stop. Explain to the user what would change, what the consequence is for any existing decks, and ask for explicit confirmation. On confirm, regenerate library pages and delete the backup. On reject, restore the backup over the new snapshot (so the company zone returns to its pre-sync state) and pause sync.

5. **Surface the result** to the user: what was applied, what was preserved, and (if any) what to revisit.

## What sync does not do

- It does not modify or delete existing decks in `decks/`. Those are the user's work product. If a deck was generated against an older snapshot, it stays as-is unless the user explicitly asks to regenerate it (a separate operation, out of scope for sync).
- It does not modify the declared source. The source is read-only from DSK's perspective (principle 1).
