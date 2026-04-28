#!/usr/bin/env python3
"""Inspect a DSK project's company zone and emit a structured state report.

Usage:
    python3 inspect_state.py <project-root>

Outputs JSON to stdout describing what is present, what is missing, and any drift indicators.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def inspect(project_root: Path) -> dict:
    return {
        "project_root": str(project_root),
        "agents_md": _check_agents_md(project_root),
        "manifest": _check_manifest(project_root),
        "source": _check_source(project_root),
        "snapshot": _check_snapshot(project_root),
        "library": _check_library(project_root),
        "decks": _check_decks(project_root),
        "drift": _check_drift(project_root),
    }


def _check_agents_md(root: Path) -> dict:
    """Check the project's agent-context file.

    AGENTS.md is canonical (cross-vendor convention). CLAUDE.md is expected to
    be a symlink to AGENTS.md so Claude Code and Claude Design pick it up.
    Returns the state of both, plus whether the canonical file has the DSK section.
    """
    agents_path = root / "AGENTS.md"
    claude_path = root / "CLAUDE.md"
    agents_present = agents_path.exists()
    claude_present = claude_path.exists() or claude_path.is_symlink()
    claude_links_to_agents = (
        claude_path.is_symlink() and claude_path.resolve() == agents_path.resolve()
    )
    has_dsk_section = False
    if agents_present:
        content = agents_path.read_text()
        has_dsk_section = "<!-- DSK BEGIN -->" in content and "<!-- DSK END -->" in content
    return {
        "agents_md_present": agents_present,
        "claude_md_present": claude_present,
        "claude_md_links_to_agents": claude_links_to_agents,
        "has_dsk_section": has_dsk_section,
    }


def _check_manifest(root: Path) -> dict:
    path = root / "manifest.yaml"
    return {"present": path.exists()}


def _check_source(root: Path) -> dict:
    source_dir = root / "source"
    if not source_dir.exists():
        return {"present": False, "files": []}
    files = sorted(str(f.relative_to(root)) for f in source_dir.glob("*.pptx"))
    return {"present": True, "files": files, "count": len(files)}


def _check_snapshot(root: Path) -> dict:
    path = root / "snapshot" / "snapshot.json"
    if not path.exists():
        return {"present": False}
    validation = _validate_snapshot(path)
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {
            "present": True,
            "valid": False,
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
        }
    return {
        "present": True,
        "valid": validation.get("valid", False),
        "errors": validation.get("errors", []),
        "warnings": validation.get("warnings", []),
        "version": data.get("snapshot_version"),
        "extracted_at": data.get("source", {}).get("extracted_at"),
        "layout_count": len(data.get("layouts", [])),
        "example_count": len(data.get("examples", [])),
        "content_count": len(data.get("content_catalog", [])),
        "fallback_count": len(data.get("fallbacks", [])),
    }


def _check_library(root: Path) -> dict:
    library_dir = root / "library"
    if not library_dir.exists():
        return {"present": False, "pages": [], "complete": False}
    expected = ["welcome.html", "layouts.html", "examples.html", "content-gallery.html"]
    present = [name for name in expected if (library_dir / name).exists()]
    return {"present": True, "pages": present, "complete": len(present) == len(expected)}


def _check_decks(root: Path) -> dict:
    decks_dir = root / "decks"
    if not decks_dir.exists():
        return {"present": False, "count": 0, "decks": []}
    decks = sorted(d.name for d in decks_dir.iterdir() if d.is_dir())
    return {"present": True, "count": len(decks), "decks": decks}


def _check_drift(root: Path) -> dict:
    snapshot_path = root / "snapshot" / "snapshot.json"
    if not snapshot_path.exists():
        return {"detectable": False, "reason": "snapshot missing"}

    snapshot = _read_json(snapshot_path)
    if snapshot is None:
        return {"detectable": False, "reason": "snapshot unreadable"}

    source_path = _declared_source_path(root) or snapshot.get("source", {}).get("file")
    if not source_path:
        return {"detectable": False, "reason": "source path missing"}

    source_file = (root / source_path).resolve()
    if not source_file.exists():
        return {
            "detectable": False,
            "reason": "declared source missing",
            "source": source_path,
        }

    extracted_at = snapshot.get("source", {}).get("extracted_at")
    extracted_timestamp = _parse_extracted_at(extracted_at)
    if extracted_timestamp is None:
        return {
            "detectable": False,
            "reason": "snapshot source.extracted_at missing or invalid",
            "source": source_path,
            "extracted_at": extracted_at,
        }

    source_mtime = source_file.stat().st_mtime
    return {
        "detectable": True,
        "source": source_path,
        "source_newer": source_mtime > extracted_timestamp,
        "source_mtime": source_mtime,
        "snapshot_extracted_at": extracted_at,
        "snapshot_extracted_timestamp": extracted_timestamp,
    }


def _validate_snapshot(snapshot_path: Path) -> dict:
    snapshot_lib = Path(__file__).resolve().parents[2] / "lib" / "snapshot"
    if str(snapshot_lib) not in sys.path:
        sys.path.insert(0, str(snapshot_lib))
    try:
        from validate_snapshot import validate

        return validate(snapshot_path)
    except Exception as error:
        return {
            "valid": False,
            "errors": [f"snapshot validator unavailable: {error}"],
            "warnings": [],
        }


def _read_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _declared_source_path(root: Path) -> str | None:
    manifest_path = root / "manifest.yaml"
    if not manifest_path.exists():
        return None
    try:
        lines = manifest_path.read_text().splitlines()
    except OSError:
        return None
    for index, line in enumerate(lines):
        if not line.startswith("source:"):
            continue
        value = line.split(":", 1)[1].strip()
        if value:
            return _clean_yaml_scalar(value)
        return _first_nested_source_path(lines[index + 1 :])
    return None


def _first_nested_source_path(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line and not line.startswith((" ", "\t", "-")):
            return None
        if stripped.startswith("- path:"):
            return _clean_yaml_scalar(stripped.split(":", 1)[1].strip())
        if stripped.startswith("path:"):
            return _clean_yaml_scalar(stripped.split(":", 1)[1].strip())
    return None


def _clean_yaml_scalar(value: str) -> str:
    without_comment = value.split(" #", 1)[0].strip()
    return without_comment.strip("\"'")


def _parse_extracted_at(value: object) -> float | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: inspect_state.py <project-root>"}))
        return 1
    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        print(json.dumps({"error": f"path does not exist: {root}"}))
        return 1
    print(json.dumps(inspect(root), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
