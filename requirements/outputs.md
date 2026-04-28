# Outputs — What DSK produces

Two distinct kinds of output, which should not be confused with the DSK system itself.

## 1. DSK outputs: library pages

Produced by the AI Design Tool (Claude Design or equivalent) in the company zone, following the kernel's briefs. Rendered as web pages (HTML, CSS, JavaScript) for humans to browse. All regenerable from source of truth plus kernel rules.

- Welcome page: what this design system is, how to use it, how to talk to the agent.
- Layouts page: every layout from the source of truth, rendered as browsable specimens with usage notes.
- Examples page: layouts filled with representative content, showing what good looks like.
- Content gallery: the content types the agent is allowed to produce (tables, charts, diagrams, callouts, etc), scoped by the company's degrees of freedom setting.

## 2. AI Design Tool outputs: user work product

What users actually create by chatting with the agent: slides (most common, rendered using web technologies, not PPT), plus any other format the host tool supports (posters, websites, documents). The AI Design Tool becomes the authoring surface instead of PowerPoint or Keynote. DSK preserves the trusted constraints from the source slide system, then applies the company's degrees of freedom so the agent can help without silently breaking the system.

## Not outputs: the DSK system itself

The kernel skills, briefs, degrees of freedom vocabulary, and snapshot tooling are fixed parts of DSK. They live in the kernel zone and are dropped in verbatim. They are not produced; they are what produces. See [separation.md](separation.md) for the full kernel zone contents.

---

[← Back to overview](../REQUIREMENTS.md)
