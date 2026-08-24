# Documentation Site Delivery

Use this reference when the result must be a browsable documentation website.

## Select The Site Framework

1. Reuse the repository's existing documentation framework and conventions when practical.
2. If the user specifies a framework, follow it.
3. If no framework exists and a standalone source book is requested, VitePress is a suitable default for Markdown-first technical documentation.

Do not replace an existing docs stack merely to match an example site.

## Output Layout

Keep generated analysis isolated from unrelated project documentation. Use the user-specified destination. Otherwise:

- Place it under an existing documentation tree when the request clearly targets the repository's docs.
- Use a dedicated `source-guide/` or sibling `<repo>-source-guide/` directory for a standalone book.

A small standalone VitePress site commonly needs:

```text
source-guide/
|-- package.json
|-- index.md
|-- contents.md
|-- chapters/
|   `-- ...
`-- .vitepress/
    `-- config.ts
```

Generate navigation from the actual chapter plan. Keep titles short enough for the sidebar. Provide search when supported by the chosen framework.

## Source Links

Every chapter should display the analyzed revision. Use visible repository-relative citations as the durable baseline:

```markdown
> Source: `src/engine/core.py#L80-L147` (`EngineCore.run_step`)
```

When the repository has a remote origin, add commit-pinned links for reader convenience. Do not link to a moving `main` or `master` branch for version-sensitive explanations.

## Build And QA

Before delivery:

1. Install dependencies using the repository's existing package manager and lockfile policy.
2. Run the production documentation build, not only the development server.
3. Run the skill's `scripts/validate_source_refs.py <repo> <docs>` helper.
4. Check internal links, sidebar order, code fences, Mermaid rendering, and previous/next navigation.
5. Inspect representative desktop and mobile pages when visual tooling is available. Confirm that tables, code blocks, diagrams, and long paths do not overflow or overlap.
6. Start the local preview server when the user needs to try the site and provide its URL.

Report build commands, verification results, the pinned revision, and any unverified platform-specific sections.

## Attribution And Licensing

Respect the source repository's license and documentation attribution requirements. Quote only the code needed for explanation. Do not copy an example book's prose, branding, or assets; use it only as structural inspiration.
