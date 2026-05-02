# Welcome page brief

## Intent

Onboard both the company's employees and the agent reading the system. Two audiences read this page; write it for both.

## Must include

- A brief explanation of what DSK is in this project (one or two sentences, plain language).
- A plain-language mental model: employees use the AI Design Tool instead of manually composing in PowerPoint or Keynote, while the official source layouts remain the trusted constraint system.
- An explicit acknowledgment that two audiences read this page: humans skimming for the rule, and the agent reading the whole system as context. Where guidance is specifically for one audience, say so.
- A clear pointer to how the user gets started, including at least one concrete example phrase the user can type in chat (e.g. "Make me a slide for our Q3 review").
- A grid or list of the other display artifacts (Layouts, Examples, Content gallery) with brief descriptions and links.
- The company's name (read from `manifest.yaml`).
- A short "Building a deck" primer: 3 to 6 numbered steps describing how an employee goes from intent to a finished deck via chat with the agent.

## Should consider

- A grid or card layout for the artifact links (more scannable than a bulleted list).
- A plain-language note on what the agent can and cannot do, translating the project's configured DoF settings and the source-of-truth-only rule into accessible terms. Don't use the words "DoF", "ceiling", or `match`/`adapt`/`stretch`/`deviate` verbatim; describe what they mean ("exact use", "small adjustments", "larger creative changes", "changes that break from the source"). Don't use the word "manifest"; if a setting needs to be referenced, say "the project's settings".
- A note that the agent can make revisions within the limits the project is configured for, so users can ask for changes without losing the source design system's guardrails. Phrase this in plain English.
- A callout on the collaboration philosophy: the agent does layout and rendering work; the user brings the angle and judgment.
- A quick visual or one example slide as eye candy.
- Accessibility: alt text on any screenshots, semantic HTML, keyboard navigation, sufficient color contrast.
- Responsive: works on mobile and desktop.
- Honor any company-specific writing rules in `AGENTS.md` (or its `CLAUDE.md` symlink) outside the DSK markers (writing style, terminology, audience-specific notes).

## Must not

- Include any content that contradicts the declared source of truth.
- Show layouts or content types that aren't in the snapshot.
- Read like marketing copy. The audience is internal employees, not prospects.
