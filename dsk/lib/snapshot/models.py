"""Pydantic types for the DSK snapshot schema.

Canonical schema definition for the DesignSystemSnapshot and its sub-types.
This is the runtime source of truth for the snapshot shape; the shared
validator (validate_snapshot.py) enforces it, and engine skills produce
JSON conforming to it.

Scope: snapshot schema only. Other DSK types — ContentRequest and
ContentMetadata (runtime, agent-facing) and Manifest and SourceEntry
(per-company config) — are conceptual contracts the agent reads from
its skill instructions, not Python types. They have no Pydantic mirror
because no Python consumer needs them yet. DoFLevel and EngineId are
canonically defined in this file.

Requires: pydantic >= 2.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DoFLevel = Literal["match", "adapt", "stretch", "deviate"]

# Identifies which snapshot engine produced the snapshot. The convention is
# engine: "X" resolves to the skill dsk:snapshot-X. MVP ships only "ppt"; add
# new engine ids here as their dsk:snapshot-<engine> skill lands.
EngineId = Literal["ppt"]


class Rect(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    w: float = Field(ge=0, le=1)
    h: float = Field(ge=0, le=1)


class Placeholder(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
    position: Rect


class Layout(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    screenshot: str
    placeholders: list[Placeholder]
    notes: str | None = None


class Example(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    layout_id: str
    screenshot: str


class ContentItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: str
    dof_level: DoFLevel | None = None
    display_name: str | None = None
    screenshot: str
    additional_screenshots: list[str] | None = None
    notes: str | None = None


class Fallback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_ref: str
    screenshot: str
    reason: str
    context: str | None = None


class SourceMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: EngineId
    engine_version: str
    file: str
    extracted_at: str


class DesignSystemSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot_version: str
    source: SourceMeta
    layouts: list[Layout]
    examples: list[Example]
    content_catalog: list[ContentItem]
    fallbacks: list[Fallback]
