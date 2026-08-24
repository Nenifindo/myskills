# Source Analysis Method

Use this reference for full-repository, multi-module, or unfamiliar-codebase work.

## Establish The Evidence Boundary

Record these facts before making architectural claims:

- Repository root and any nested repository or submodule boundaries.
- Commit SHA, branch or tag, and whether the working tree contains relevant uncommitted changes.
- Repository instructions such as `AGENTS.md`, contribution rules, generated-file notices, and ownership boundaries.
- Languages, manifests, build systems, test runners, generated code, vendored code, and optional platform backends.
- The audience and desired depth. A contributor guide, algorithm explanation, and full source book need different detail.

If the input is a remote repository, clone or fetch only when authorized and useful. Pin explanations to a commit rather than a moving branch name. If the input is a local dirty checkout, analyze the actual visible files and say that the result includes uncommitted state.

## Reconnaissance

Start broad, then follow evidence:

1. Read top-level manifests, primary documentation, build configuration, and repository instructions.
2. Inventory top-level directories and dominant file types. `../scripts/repo_inventory.py` can produce a deterministic baseline.
3. Find user-facing entry points: CLI commands, servers, library exports, plugin hooks, jobs, handlers, or application bootstrap code.
4. Trace one representative happy path end to end before cataloging subsystems.
5. Locate the data structures, state machines, queues, registries, caches, protocols, and resource owners on that path.
6. Read tests that encode contracts, edge cases, compatibility requirements, or failure handling.
7. Repeat for materially different paths such as offline/online, sync/async, local/distributed, CPU/GPU, read/write, or compile/runtime.

Use `rg` for symbols, imports, registrations, config keys, and tests. Use language-aware tooling when the repository already provides it. Do not claim that a dependency is one-way or that a function is unused without checking dynamic registration, reflection, generated code, and platform-specific paths.

## Build An Evidence Map

Maintain a lightweight ledger while investigating:

| Claim or question | Primary source | Supporting source | Confidence | Validation |
|---|---|---|---|---|
| Request enters through X | path + symbol + lines | integration test | high | traced caller chain |
| Cache eviction is LRU | implementation | focused unit test | high | test run |
| Component Y is optional | registry/config | docs | medium | static only |

The ledger is working material; it does not need to appear in the final output. It prevents attractive but unsupported explanations.

## Analysis Lenses

Apply only lenses that matter to the repository:

- **Responsibility:** What contract does each major component own, and what does it deliberately not own?
- **Control flow:** Which entry point calls which orchestrator, and where are decisions made?
- **Data flow:** What representations cross boundaries, and where are conversions or copies performed?
- **State:** What states and invariants exist? Which events cause transitions?
- **Resource lifecycle:** Who creates, shares, pools, retries, cancels, flushes, and releases resources?
- **Concurrency:** Which work runs in threads, processes, tasks, workers, devices, or nodes? Where are ordering and backpressure enforced?
- **Extensibility:** How are implementations registered, selected, configured, and tested?
- **Failure behavior:** How do errors propagate, recover, retry, degrade, or become user-visible?
- **Performance:** Which paths are intentionally optimized, batched, cached, fused, vectorized, or moved across language boundaries?
- **Evolution:** When multiple architectures coexist, explain the selection boundary and migration state at the pinned revision.

## Source Citations

For Markdown guides, use visible citations in this form:

```markdown
> Source: `src/runtime/scheduler.py#L120-L198` (`Scheduler.schedule`)
```

Use repository-relative paths and 1-based inclusive line ranges. Cite the smallest range that supports the claim. Add separate source blocks for distinct claims rather than one broad citation at the end of a long chapter.

Line numbers drift, so record the commit SHA in the guide front matter. When a remote URL is known, commit-pinned source links may supplement the stable text citation.

## Verification

Scale verification to the claim:

- Static structure: inspect declarations, imports, registrations, and callers.
- Behavioral contract: read and, when feasible, run focused tests.
- Generated output: build the docs and validate internal links and source references.
- Performance claim: require a benchmark, measurement, or authoritative result tied to a version; otherwise label it historical or unverified.
- Platform-specific behavior: state which backend was inspected and avoid generalizing to all backends.

Never fabricate execution results. If dependencies, hardware, credentials, or time prevent runtime verification, say exactly what was checked statically.
