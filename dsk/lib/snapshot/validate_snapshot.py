#!/usr/bin/env python3
"""Validate a DSK snapshot against the canonical schema.

Usage:
    python3 validate_snapshot.py <snapshot.json>

Exits 0 if valid, 1 otherwise. Prints a JSON report to stdout.

Engine-agnostic: every dsk:snapshot-* engine emits the same DesignSystemSnapshot
shape and uses this validator. The Pydantic models live in models.py (alongside
this script) and are the canonical schema. This script imports them and performs
cross-cutting integrity checks (id uniqueness, screenshot path resolution,
layout_id resolution, orphan assets) on top of Pydantic's schema enforcement.

Naming note: models.py rather than types.py because the latter shadows
Python's stdlib `types` module.

Requires: pydantic >= 2 (install: pip install pydantic --quiet).
"""
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from models import DesignSystemSnapshot, Example, Layout


def validate(snapshot_path: Path) -> dict:
    if not snapshot_path.exists():
        return _result(False, [f"snapshot.json not found at {snapshot_path}"], [])

    try:
        data = json.loads(snapshot_path.read_text())
    except json.JSONDecodeError as e:
        return _result(False, [f"invalid JSON: {e}"], [])

    try:
        snapshot = DesignSystemSnapshot.model_validate(data)
    except ValidationError as e:
        return _result(False, _format_pydantic_errors(e), [])

    errors: list[str] = []
    warnings: list[str] = []
    snapshot_dir = snapshot_path.parent
    referenced: set[str] = set()

    _check_unique_layout_ids(snapshot.layouts, errors)
    layout_ids = {layout.id for layout in snapshot.layouts}
    _check_layout_id_references(snapshot.examples, layout_ids, errors)
    _collect_and_check_screenshots(snapshot, snapshot_dir, referenced, errors)
    _check_orphans(snapshot_dir / "assets", snapshot_dir, referenced, warnings)

    return _result(len(errors) == 0, errors, warnings)


def _result(valid: bool, errors: list[str], warnings: list[str]) -> dict:
    return {"valid": valid, "errors": errors, "warnings": warnings}


def _format_pydantic_errors(error: ValidationError) -> list[str]:
    formatted: list[str] = []
    for err in error.errors():
        location = ".".join(str(x) for x in err["loc"]) or "<root>"
        formatted.append(f"{location}: {err['msg']}")
    return formatted


def _check_unique_layout_ids(layouts: list[Layout], errors: list[str]) -> None:
    seen: set[str] = set()
    for layout in layouts:
        if layout.id in seen:
            errors.append(f"duplicate layout id: {layout.id}")
        seen.add(layout.id)


def _check_layout_id_references(examples: list[Example], layout_ids: set[str], errors: list[str]) -> None:
    for example in examples:
        if example.layout_id not in layout_ids:
            errors.append(f"example '{example.id}'.layout_id does not resolve to a Layout.id: {example.layout_id}")


def _collect_and_check_screenshots(snapshot: DesignSystemSnapshot, snapshot_dir: Path, referenced: set[str], errors: list[str]) -> None:
    paths_to_check: list[tuple[str, str]] = []
    for layout in snapshot.layouts:
        paths_to_check.append((f"layout '{layout.id}' screenshot", layout.screenshot))
    for example in snapshot.examples:
        paths_to_check.append((f"example '{example.id}' screenshot", example.screenshot))
    for content in snapshot.content_catalog:
        paths_to_check.append((f"content_catalog '{content.id}' screenshot", content.screenshot))
        for i, additional in enumerate(content.additional_screenshots or []):
            paths_to_check.append((f"content_catalog '{content.id}' additional_screenshots[{i}]", additional))
    for fallback in snapshot.fallbacks:
        paths_to_check.append((f"fallback '{fallback.source_ref}' screenshot", fallback.screenshot))
    for media in snapshot.source_media:
        paths_to_check.append((f"source_media '{media.id}' path", media.path))
    for label, path in paths_to_check:
        referenced.add(path)
        if not (snapshot_dir / path).exists():
            errors.append(f"{label} does not resolve on disk: {path}")


def _check_orphans(assets_dir: Path, snapshot_dir: Path, referenced: set[str], warnings: list[str]) -> None:
    if not assets_dir.exists():
        return
    asset_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".emf",
                        ".ttf", ".otf", ".woff", ".woff2", ".mp3", ".wav", ".mp4", ".mov"}
    for asset in assets_dir.rglob("*"):
        if not asset.is_file():
            continue
        if asset.suffix.lower() not in asset_extensions:
            continue
        relative = asset.relative_to(snapshot_dir).as_posix()
        if relative not in referenced:
            warnings.append(f"orphan asset (no snapshot entry references it): {relative}")


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps(_result(False, ["usage: validate_snapshot.py <snapshot.json>"], [])))
        return 1
    path = Path(sys.argv[1]).resolve()
    report = validate(path)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
