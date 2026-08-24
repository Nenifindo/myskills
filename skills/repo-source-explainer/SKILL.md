---
name: repo-source-explainer
description: Generate source-grounded repository explanations, architecture walkthroughs, module deep dives, and book-style documentation from source code. Use when asked for source analysis, a code-reading guide, or a deep explanation of how a repository works. Do not use for setup-focused onboarding, ordinary code review, or API usage tutorials.
---

# Repo Source Explainer

Turn a repository into an evidence-backed explanation that helps readers form a correct mental model and navigate the implementation themselves.

## Choose The Deliverable

Match the depth to the request:

- **Focused explanation:** one symbol, module, algorithm, or execution path.
- **Architecture guide:** several modules, one subsystem, or a guided repository tour.
- **Source book/site:** a chaptered, navigable treatment of the full repository.

Do not expand a focused request into a full book without the user's direction. Preserve an existing documentation framework when one is already in use.

## Ground Every Explanation

- Identify the repository root, target revision, relevant repository instructions, and working-tree state before analysis.
- Treat source and tests at the target revision as primary evidence. Existing docs, issues, papers, and websites provide context but do not override the code.
- Trace real control flow, data flow, state transitions, resource lifecycles, and error paths. Do not infer architecture solely from directory names.
- Distinguish verified behavior from interpretation. State uncertainty when generated code, optional backends, dynamic registration, or unavailable runtime dependencies limit verification.
- Cite important claims with repository-relative paths, symbols, and line ranges. Use the stable visible form below and record the revision near the document front matter.

  ```markdown
  > Source: `path/to/file.py#L10-L42` (`SymbolName`)
  ```
- Prefer small, representative excerpts. Explain why code exists, what contract it enforces, and how callers depend on it instead of paraphrasing every line.

For a supervised comparison, treat the reference book as a second, versioned
evidence set rather than as an answer key. Record its repository revision and
date, compare them with the analyzed source revision, and probe every important
reference path against the target checkout. If the reference is older or points
to missing files/symbols, label the drift explicitly and prefer the current
source. Do not score textual or pathname overlap as correctness by itself.

## Workflow

1. Establish the baseline. Inspect instructions, manifests, build files, docs, tests, revision, and repository status. Run `scripts/repo_inventory.py` when a deterministic inventory will save time.
2. Build an evidence map before drafting: entry points, orchestration, domain core, boundaries, state, extension points, performance-critical paths, and representative tests.
3. Organize the explanation around reader questions and runtime mechanisms. Use the repository tree as a map, not as the table of contents.
4. Draft from macro to micro: design pressures, architecture, main flows, core mechanisms, cross-cutting behavior, then operational or extension details.
5. Verify source references and observable claims. Run relevant tests/builds and
   `scripts/validate_source_refs.py` for chaptered Markdown output. Then run
   `scripts/audit_source_guide.py` to check revision pinning, per-chapter
   citation coverage, and verification-report hygiene.
6. Report the analyzed revision, verification performed, known gaps, and any areas that remain inferred.

When writing `verification.md`, classify each check with an unambiguous state:
`planned`, `executed`, `passed`, `failed`, `blocked`, or `not run`. A blocked
check must name the concrete environment or authorization constraint; a not-run
check must say why it was out of scope. Never leave a later report with an old
"dependencies missing" claim after dependencies have been installed or a test
has been rerun. Replace superseded findings with the latest observed result and
retain earlier attempts only as historical context.

## Load Details Only When Needed

- Read [references/analysis-method.md](references/analysis-method.md) for full-repository, multi-module, or unfamiliar-codebase analysis.
- Read [references/book-structure.md](references/book-structure.md) when producing a chapter plan, long-form guide, reading path, or source book.
- Read [references/site-delivery.md](references/site-delivery.md) when the deliverable is a documentation website or when a static-site build must be created and verified.
- Read [references/evaluation.md](references/evaluation.md) when a reference book is supplied, the user asks for validation, or the guide will be used as a repeatable benchmark.
