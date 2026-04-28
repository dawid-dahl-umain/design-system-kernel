# Content input

Content for slide generation arrives at the agent in one of two modes. DSK supports both. Plain is the default; annotated is the optional path that lets DSK consume metadata produced by other systems.

This is a foundational feature (principle 9). It defines DSK's relationship to surrounding systems — AI or otherwise — in a company.

## Plain mode

The user submits raw content as part of the chat conversation: text, data, an idea, a paste from elsewhere. There is no structured object on the wire — the chat message itself is the content. The agent interprets it as the slide payload, picks the best matching layout from the snapshot catalog, and falls back to asking the user when intent is ambiguous. Nothing else is needed; this is the default and works for most casual use.

## Annotated mode

Content arrives as a structured payload bundled with metadata. **The producer can be anything — an AI process (knowledge base, content generator, research agent), a traditional software pipeline, an internal data system, or even the user pasting in a hand-built JSON blob.** From DSK's perspective, the source does not matter; what matters is that the metadata is attached and conforms to the conventions below.

The metadata can include rendering guidance, layout hints, references to past slides for similar content, and provenance details. DSK reads conventional metadata keys when present and uses them to inform layout selection and content rendering. It does not define what produces the metadata; that is up to each company. DSK stays at the design system layer while letting companies build sophisticated content pipelines around it.

## Classification and the robustness fallback

The agent classifies each incoming request as plain or annotated based on the input's shape. Plain is anything that arrives as ordinary chat conversation. Annotated is anything that arrives as a structured payload with recognizable metadata keys.

If the agent cannot tell — the input is structured but the metadata shape is unfamiliar, or the user pastes something ambiguous — it asks the user how to treat it. If the user can't or won't classify and the input is too vague to disambiguate, the agent **defaults to plain mode** and proceeds best-effort with whatever content it can interpret. Robustness over rigidity: a sensible plain-mode result beats refusing to act on ambiguous input.

## Concrete example: a "company brain" pattern

Imagine a company has an internal system — AI, traditional pipeline, or a hybrid — that processes years of past decks, case studies, and documentation. When a user generates new content through that system, it attaches metadata describing how similar content has historically been visualized inside the company (e.g. "this kind of YoY growth metric is usually rendered as a hero number with a small comparison line below, primary color for positive, neutral-700 for negative").

DSK reads that metadata when picking a layout and constructing the visualization, producing slides that are consistent with how the company has presented similar content in past projects. The user gets a brand-and-history-aware slide without having to remember any of the conventions.

This is the value loop: an upstream system does the hard work of finding the right precedents and producing brand-coherent content; DSK respects that work and renders accordingly.

## Conventional metadata keys

DSK understands the following keys when present. Other keys in the metadata bag are forwarded to the agent for interpretation but not specifically acted upon.

- `style_hints`: free-form rendering guidance, prose. Example: "Use stacked bars, primary segment on top."
- `layout_hints`: suggestions for which layout to use. The agent still validates fit against the snapshot catalog and may override if the suggestion does not exist or does not fit the content.
- `precedents`: references to past slides, cases, or projects the content is consistent with. Useful for the agent to inspect if it has access to those artifacts.
- `source`: identifier of the system that produced the metadata (any kind — AI, traditional, or otherwise).

For the formal shape, see [types.md](types.md).

## What metadata informs

DSK does two smart things on every slide generation regardless of mode: it selects a layout from the catalog, and it generates content into that layout. Metadata, when present, feeds both:

- Smart layout selection considers `layout_hints`, `precedents`, and any other metadata that helps pick the best layout for the content.
- Smart content generation considers `style_hints`, `precedents`, the degrees of freedom ceiling, the slide rules in the snapshot, and brand primitives available from the host or source files when filling the layout.

Plain mode runs the same two steps; metadata just adds another input when available.

## Why this design works

DSK does not depend on annotated mode existing. Plain mode is fully supported and stays the default, so simple use cases remain simple.

DSK does not depend on any specific upstream system. It just defines a small contract (`ContentRequest`) and a few conventional keys. Anyone can produce content in this shape; DSK consumes it.

Per principle 7, the metadata is behavior level. We do not dictate how the agent uses style hints or precedents; we just say it considers them. That keeps the system flexible and lets it improve as agents get smarter.

---

[← Back to overview](../REQUIREMENTS.md)
