# Outputs — What DSK produces

Two distinct kinds of output, which should not be confused with the DSK system itself.

## 1. DSK outputs: the library (renditions + browser pages)

Produced by the AI Design Tool (Claude Design or equivalent) in the company zone, following the kernel's briefs. Rendered as web technologies (HTML, CSS, JavaScript). All regenerable from source of truth plus kernel rules.

The library has **two distinct artifact categories** — they serve different purposes and are governed by different rules in `dsk:build`:

### 1a. Renditions — the value layer

Web-rendered versions of every layout, every example, and every content item in the snapshot. **One file per layout, one file per example, one file per content type**, in `library/renditions/{layouts,examples,content}/<id>.html`. Self-contained or sharing `library/assets/`.

These are the actual web slides DSK produces. `dsk:compose` reuses them as starting templates: layout renditions become the starting frame for a slide; content renditions fill the slide's content slots (a chart, a table, a diagram). The same renditions are what the user sees when browsing the library pages.

Renditions are the value: without them, DSK would be just a screenshot gallery of the source. With them, DSK produces a working web slide system the agent can actually compose with — and refine, via `dsk:refine`, when a specific rendition drifts from source intent.

When no design system is available in the runtime (no host design system feature like Claude Design's, no user-provided design system in the project folder), `dsk:build` pauses and asks the user how to style the renditions before generating them. This is the one place in build where pausing is correct, because renditions are the product.

### 1b. Library pages — the browser around the renditions

Four web pages humans browse to navigate the design system:

- **Welcome page**: what this design system is, how to use it, how to talk to the agent.
- **Layouts page**: every layout from the source of truth, embedded via the layout renditions, with usage notes.
- **Examples page**: example renditions filled with representative content, showing what good looks like.
- **Content gallery**: the content types the agent is allowed to produce (tables, charts, diagrams, callouts, etc.), scoped by the company's degrees of freedom setting.

Library pages embed the renditions (typically via `<iframe>` to preserve slide-ratio isolation), they don't inline them. Page chrome (nav, headings, accent colors) auto-resolves from the runtime — host design system → source-derived → generic fallback — and never pauses the user.

## 2. AI Design Tool outputs: user work product

What users actually create by chatting with the agent: slides (most common, rendered using web technologies, not PPT), plus any other format the host tool supports (posters, websites, documents). The AI Design Tool becomes the authoring surface instead of PowerPoint or Keynote. DSK preserves the trusted constraints from the source slide system, then applies the company's degrees of freedom so the agent can help without silently breaking the system.

## Not outputs: the DSK system itself

The kernel skills, briefs, degrees of freedom vocabulary, and snapshot tooling are fixed parts of DSK. They live in the kernel zone and are dropped in verbatim. They are not produced; they are what produces. See [separation.md](separation.md) for the full kernel zone contents.

---

[← Back to overview](../REQUIREMENTS.md)
