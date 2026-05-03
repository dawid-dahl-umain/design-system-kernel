# Types

Formal shapes of the data structures DSK reads, writes, and exchanges. Where a type has a runtime implementation, that implementation is the canonical source and this file references it. Where no runtime implementation exists yet, the TypeScript-style interface notation here is the spec.

## DesignSystemSnapshot

The typed output of any snapshot engine. Lives at `snapshot/snapshot.json` in the company zone. A sibling `assets/` directory holds binaries referenced by path.

Slim by design: only DSK-essential slide information is in the snapshot. Theme colors, fonts, logos, embedded images, and reusable brand components are delegated to the host AI Design Tool's own design-system feature, native PPT extraction, or direct source-file reading.

**Canonical source**: the Pydantic models in [`dsk/lib/snapshot/models.py`](../dsk/lib/snapshot/models.py). The interfaces `DesignSystemSnapshot`, `SourceMeta`, `Canvas`, `Layout`, `Placeholder`, `Rect`, `Example`, `ContentItem`, `Fallback`, and `SourceMedia` are defined there. `models.py` is also what `validate_snapshot.py` (alongside it) enforces, so the type definitions and runtime validation cannot drift apart. The schema and validator live at plugin level (not inside any one engine skill) because they are engine-agnostic; every `dsk:snapshot-*` engine emits the same shape and uses the same validator.

`Canvas` records the source slide dimensions (`width`, `height`, `unit`). It is required at the snapshot's top level and drives aspect-ratio decisions in the build stage. The unit is engine-specific (`emu` for PPT, `pt` for Keynote and Google Slides, `px` for Figma); fractional positions on `Rect` are unit-free, but the canvas tells consumers what those fractions are fractions of.

`SourceMedia` is a list of raw assets extracted from the source's design system layer (logos, decorative artwork, photographic backgrounds, embedded fonts referenced by the master, layouts, or theme — not per-slide content from the original deck). Each entry records a stable `id`, the asset's `path` inside the snapshot, and optional structured hints (`kind`, `role`, `source_ref`, `appears_in`, `notes`). Build uses this as a fallback tier when the host AI Design Tool does not expose the company's brand primitives directly; it is host-agnostic by construction (the same files are available in Claude Code, Claude Design, or any future folder-based host). Engine-agnostic too: every engine extracts from its own format's design-system parts (PPT from master/layouts/theme rels, Keynote from package internals, Figma via image-fill API, Google Slides via API references). The on-disk shape is uniform.

JSON example:

```json
{
  "snapshot_version": "0.1",
  "source": {
    "engine": "ppt",
    "file": "source/Acme-Master.pptx",
    "extracted_at": "2026-04-25T10:30:00Z"
  },
  "canvas": {
    "width": 9144000,
    "height": 5143500,
    "unit": "emu"
  },
  "layouts": [
    {
      "id": "title-slide",
      "name": "Title Slide",
      "screenshot": "assets/layout-screenshots/title-slide.png",
      "placeholders": [
        { "type": "title",    "position": { "x": 0.08, "y": 0.36, "w": 0.84, "h": 0.11 } },
        { "type": "subtitle", "position": { "x": 0.08, "y": 0.50, "w": 0.84, "h": 0.06 } }
      ],
      "notes": "Opening slide. One title and one subtitle."
    }
  ],
  "examples": [
    {
      "id": "ex-quarterly-results",
      "layout_id": "content-with-sidebar",
      "screenshot": "assets/example-screenshots/ex-quarterly-results.png"
    }
  ],
  "content_catalog": [
    {
      "id": "chart-arr-growth",
      "type": "bar-chart",
      "dof_level": "match",
      "display_name": "ARR Growth Chart",
      "screenshot": "assets/content-screenshots/chart-arr-growth.png",
      "notes": "Stacked bars by segment. Y-axis always starts at 0."
    }
  ],
  "fallbacks": [],
  "source_media": [
    {
      "id": "image9",
      "path": "assets/source-media/image9.png",
      "kind": "raster",
      "role": "decorative",
      "source_ref": "ppt/media/image9.png",
      "appears_in": ["title-fifth-element", "divider-fifth-element", "title-large-fifth-element"],
      "notes": "Brand-defining swirling decorative shape; appears across the 'Fifth element' family of layouts."
    }
  ]
}
```

## ContentRequest

The conceptual shape of content arriving at the agent for slide generation. Two modes:

- **Plain** (no metadata): in practice this is the user's chat conversation — there's no structured `ContentRequest` object on the wire. The agent interprets the chat message as `content` with no `metadata`.
- **Annotated** (metadata included): a structured payload from any producer (AI system, traditional software, knowledge base, etc.). DSK doesn't care about the source.

See [content-input.md](content-input.md) for the conceptual model and the robustness fallback (when classification is unclear, default to plain).

```ts
interface ContentRequest<TMeta extends ContentMetadata = ContentMetadata> {
  content: unknown;             // the content itself: text, data, structured payload
  metadata?: TMeta;             // optional; present in annotated mode
}

interface ContentMetadata {
  // Conventional keys DSK understands when present:
  style_hints?: string[];       // free-form rendering guidance
  layout_hints?: string[];      // layout suggestions (agent validates against snapshot catalog)
  precedents?: string[];        // references to past slides or cases
  source?: string;              // identifier of the producing system (any kind — AI or otherwise)
  // Open-ended: any additional keys are forwarded to the agent for interpretation:
  [key: string]: unknown;
}
```

The metadata shape is deliberately open. Companies with a known upstream system can extend `ContentMetadata` with their own typed shape and pass it as the generic parameter:

```ts
// Company-specific extension, not part of DSK itself
interface CompanyBrainMetadata extends ContentMetadata {
  brain_version: string;
  case_references: { id: string; title: string }[];
}

type CompanyBrainRequest = ContentRequest<CompanyBrainMetadata>;
```

DSK itself only knows the base `ContentMetadata`. Whatever extra keys a company adds are visible to the agent and acted upon to whatever extent the agent understands them, per principle 7.

JSON examples:

```json
// Plain mode
{
  "content": "Q3 revenue grew 18% year over year, led by enterprise renewals."
}

// Annotated mode
{
  "content": {
    "title": "Q3 Results",
    "metric": { "value": 0.18, "type": "yoy_growth" },
    "narrative": "Driven by enterprise renewals."
  },
  "metadata": {
    "source": "company-brain",
    "style_hints": [
      "YoY growth metrics rendered as a single hero number with a small comparison line below."
    ],
    "layout_hints": ["title-with-hero-metric"],
    "precedents": ["case-2024-acme-q4-results", "case-2023-globex-h1-update"]
  }
}
```

## Manifest

The per-company config file. Lives at `manifest.yaml` in the company zone. YAML for human-editability and comments.

```ts
interface Manifest {
  version: string;                    // schema version, e.g. "0.1"
  company: { name: string };
  source: string | SourceEntry[];     // path, or array for multi-source
  dof: {
    ceiling: DoFLevel;                // hard cap
    silent_up_to: DoFLevel;           // proceed without confirmation up to this level
  };
  paths?: {                           // optional overrides; sensible defaults otherwise
    snapshot?: string;
    library?: string;
    decks?: string;
  };
}

interface SourceEntry {
  path: string;
  engine?: EngineId;                  // inferred from extension if omitted.
                                      // Resolves to skill dsk:snapshot-<engine>.
}
```

`DoFLevel` and `EngineId` referenced above are **canonically defined as Pydantic Literals in [`dsk/lib/snapshot/models.py`](../dsk/lib/snapshot/models.py)**. Current values, for reference:

- `DoFLevel = "match" | "adapt" | "stretch" | "deviate"`
- `EngineId = "ppt"` (MVP; extend in lockstep with new `dsk:snapshot-<engine>` skills)

Treat the Python definitions as authoritative; this file mirrors them in prose for readers without Python access.

YAML example (minimum viable; values shown match the strict defaults):

```yaml
version: 0.1
company:
  name: "Acme Inc"
source: source/Acme-Master.pptx
dof:
  ceiling: adapt
  silent_up_to: match
```

---

[← Back to overview](../REQUIREMENTS.md)
