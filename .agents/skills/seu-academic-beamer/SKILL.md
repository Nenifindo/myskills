---
name: seu-academic-beamer
description: Create, scaffold, compile, review, and polish Southeast University academic report slide decks using the local SimplePlus Beamer theme adapted with the SEU logo. Use when the user asks for 东南大学学术汇报 PPT, SEU academic presentation slides, Beamer slides for Southeast University reports, seminar/defense/group-meeting decks with 东南大学 branding, or wants to turn papers, outlines, notes, or research results into a SEU-style academic report PDF.
---

# SEU Academic Beamer

## Overview

Use this skill to create Beamer-based academic presentation PDFs with the project-local `SimplePlus-BeamerTheme-SEU` assets. Treat "PPT" in this context as a presentation deck unless the user explicitly requests `.pptx`.

## Assets

The bundled template lives in `assets/simpleplus-seu/`.

Copy these files into any deck directory before compiling:

- `beamerthemeSimplePlus.sty`
- `beamercolorthemeSimplePlus.sty`
- `beamerfontthemeSimplePlus.sty`
- `beamerinnerthemeSimplePlus.sty`
- `seu_logo.png`
- `reference.bib` when BibTeX citations are needed

Prefer the scaffold script for new decks:

```bash
python3 PATH_TO_SKILL/scripts/create_seu_beamer_project.py OUTPUT_DIR \
  --title "汇报题目" \
  --subtitle "副标题" \
  --author "汇报人" \
  --institute "东南大学"
```

## Deck Creation Workflow

1. Clarify the talk type, duration, audience, source material, and required language. Infer reasonable defaults when the user already provides them.
2. Build a slide outline before drafting: title page, overview, motivation/background, method/result sections, summary, references, and optional backup slides.
3. Scaffold a deck directory with the script or copy the assets manually.
4. Write `main.tex` using `\documentclass[aspectratio=169,xcolor=dvipsnames]{beamer}` and `\usetheme{SimplePlus}`.
5. Place the SEU logo at the top-right with the TikZ overlay pattern from the bundled starter.
6. Compile with XeLaTeX; use BibTeX only if `\cite{}` is present.
7. Inspect the log for undefined citations/references and overfull boxes, then visually review the PDF.

## Beamer Defaults

Use this baseline unless the user provides a custom preamble:

```latex
\documentclass[aspectratio=169,xcolor=dvipsnames]{beamer}
\usetheme{SimplePlus}

\usepackage{ctex}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,calc}

\logo{
  \begin{tikzpicture}[remember picture, overlay]
    \node[anchor=north east, inner sep=2.5pt] at (current page.north east) {
      \includegraphics[width=1cm]{seu_logo.png}
    };
  \end{tikzpicture}
}
```

Use `ctex` for Chinese decks and XeLaTeX compilation. Remove `ctex` only for English-only decks when the local TeX environment lacks Chinese support.

## Slide Style

- Keep a 16:9 academic report format.
- Use concise slide text: keywords and short clauses, not manuscript paragraphs.
- Put one main idea on each slide.
- Prefer formulas, diagrams, tables, algorithms, or figures over text-only slides.
- Use `block`, `alertblock`, and `examples` sparingly; keep box content short to avoid overflow.
- Use `\begin{columns}[T]` for comparison or figure-text layouts; common widths are `0.48/0.48` or `0.52/0.43`.
- Keep references as the second-to-last main slide and a final "谢谢 / Q&A" slide.
- For defenses or seminar talks, add `\appendix` backup slides after Q&A.

## Compilation

For decks without citations:

```bash
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

For decks with BibTeX citations:

```bash
xelatex -interaction=nonstopmode main.tex
bibtex main
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

After compiling, check `main.log` for:

- `Undefined control sequence`
- `Citation ... undefined`
- `Reference ... undefined`
- `Overfull \hbox`
- `LaTeX Error`

Report the PDF path, slide count, and any remaining warnings.

## Quality Bar

Before handing off a deck, verify:

- The SEU logo appears on content slides and does not collide with frame titles.
- The title page has a clear title, speaker, affiliation, and date.
- Section order matches the approved outline.
- No text or equations spill outside blocks or slide boundaries.
- Figures and tables have readable labels.
- Citations resolve or unresolved citation keys are explicitly reported.
