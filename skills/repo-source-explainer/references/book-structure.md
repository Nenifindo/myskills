# Source Book Structure

Use this reference for chapter plans, long-form guides, reading paths, and full source books.

## Design The Table Of Contents

Organize the book around concepts and execution mechanisms, not a mirror of the directory tree. A useful progression is:

1. Project purpose, design pressures, and the smallest end-to-end example.
2. Repository map, architectural boundaries, and recommended reading paths.
3. Main execution lifecycle from public entry point to core result.
4. Core mechanisms and the data structures that make them work.
5. Major subsystems in dependency order.
6. Cross-cutting concerns such as configuration, concurrency, distribution, persistence, security, or performance.
7. Extension, debugging, testing, and operational guidance when relevant.
8. Appendices for type maps, symbol indexes, glossary, and alternative reading paths.

Split or merge these areas according to the repository. Do not force a fixed chapter count. A large repository may need separate paths for users, contributors, performance engineers, and integrators.

## Chapter Contract

Each substantive chapter should answer a coherent reader question and normally include:

- **Reader outcome:** what the reader will understand after the chapter.
- **Problem and role:** why the mechanism exists and where it sits in the system.
- **Source entry points:** a compact table of files, symbols, and responsibilities.
- **Execution walkthrough:** the control and data flow in actual call order.
- **State and invariants:** important types, queues, caches, ownership, transitions, and constraints.
- **Key implementation choices:** representative excerpts with explanation of tradeoffs.
- **Failure and edge behavior:** cancellation, retries, fallbacks, exhaustion, or invalid input where applicable.
- **Tests as contracts:** representative tests that confirm non-obvious behavior.
- **Version notes:** alternate implementations, migrations, deprecated paths, or backend differences.
- **Summary and next link:** what is now known and why the next chapter follows.

Not every short chapter needs every heading. The contract is about coverage, not rigid formatting.

## Diagrams

Use a diagram when relationships are easier to understand visually:

- Flowchart for request or compilation pipelines.
- Sequence diagram for cross-process, async, distributed, or protocol interactions.
- State diagram for lifecycle and scheduler behavior.
- Component diagram for ownership and dependency boundaries.
- Data-layout diagram for memory, storage, tensor, packet, or serialization formats.

Prefer Mermaid when the target renderer supports it; otherwise use a compact ASCII diagram. Derive nodes and arrows from verified calls or contracts. Label inferred or optional edges instead of presenting them as unconditional.

## Writing Quality

- Lead with the mechanism and its motivation, then descend into code.
- Keep terminology consistent with the repository and define overloaded terms.
- Explain code in context; avoid long excerpts and line-by-line narration.
- Separate current behavior from history and future plans.
- Avoid decorative quotations, repeated FAQs, generic praise, and claims such as "clean architecture" unless the source demonstrates the relevant property.
- Cross-link prerequisites and downstream chapters so readers can choose a path without reading strictly front to back.

## Suggested Front Matter

Include the following near the beginning of a full guide:

```markdown
# <Repository> Source Guide

- Analyzed revision: `<full commit SHA>`
- Working tree: clean | includes local changes
- Primary languages: ...
- Intended audience: ...
- Verification: tests/builds performed ...
- Known limits: generated code, unavailable backend, omitted vendored modules ...
```

Include a one-page architecture overview, a complete contents page, and at least one recommended reading path before deep chapters.
