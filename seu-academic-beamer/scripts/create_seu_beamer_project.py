#!/usr/bin/env python3
"""Scaffold a Southeast University SimplePlus Beamer deck."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


THEME_FILES = [
    "beamerthemeSimplePlus.sty",
    "beamercolorthemeSimplePlus.sty",
    "beamerfontthemeSimplePlus.sty",
    "beamerinnerthemeSimplePlus.sty",
    "seu_logo.png",
    "reference.bib",
]


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def starter_tex(title: str, subtitle: str, author: str, institute: str) -> str:
    return rf"""% !TeX program = xelatex
\documentclass[aspectratio=169,xcolor=dvipsnames]{{beamer}}
\usetheme{{SimplePlus}}

\usepackage{{ctex}}
\usepackage{{amsmath,amssymb,mathtools}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{tikz}}
\usetikzlibrary{{arrows.meta,positioning,calc}}

\logo{{
  \begin{{tikzpicture}}[remember picture, overlay]
    \node[anchor=north east, inner sep=2.5pt] at (current page.north east) {{
      \includegraphics[width=1cm]{{seu_logo.png}}
    }};
  \end{{tikzpicture}}
}}

\title{{{latex_escape(title)}}}
\subtitle{{{latex_escape(subtitle)}}}
\author{{{latex_escape(author)}}}
\institute{{{latex_escape(institute)}}}
\date{{\today}}

\begin{{document}}

\begin{{frame}}
  \titlepage
\end{{frame}}

\begin{{frame}}{{目录}}
  \tableofcontents
\end{{frame}}

\section{{研究背景}}

\begin{{frame}}{{研究背景}}
  \begin{{itemize}}
    \item 问题场景：说明研究对象与核心挑战
    \item 现有方法：概括代表性路线与不足
    \item 本次汇报：突出主要贡献与结论
  \end{{itemize}}
\end{{frame}}

\section{{方法与结果}}

\begin{{frame}}{{核心方法}}
  \begin{{block}}{{关键思想}}
    用一句话概括方法主线，并配合公式、图示或表格展开。
  \end{{block}}
\end{{frame}}

\begin{{frame}}{{实验或分析结果}}
  \begin{{table}}
    \centering
    \begin{{tabular}}{{lcc}}
      \toprule
      方法 & 指标一 & 指标二 \\
      \midrule
      Baseline & -- & -- \\
      Proposed & -- & -- \\
      \bottomrule
    \end{{tabular}}
  \end{{table}}
\end{{frame}}

\section{{总结}}

\begin{{frame}}{{总结}}
  \begin{{itemize}}
    \item 结论一：回答研究问题
    \item 结论二：说明方法优势或适用边界
    \item 后续工作：列出可扩展方向
  \end{{itemize}}
\end{{frame}}

\begin{{frame}}{{参考文献}}
  \footnotesize
  \bibliography{{reference.bib}}
  \bibliographystyle{{apalike}}
\end{{frame}}

\begin{{frame}}
  \Huge{{\centerline{{\textbf{{谢谢}}}}}}
  \vspace{{0.5cm}}
  \Large{{\centerline{{Q\&A}}}}
\end{{frame}}

\end{{document}}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--filename", default="main.tex")
    parser.add_argument("--title", default="东南大学学术汇报")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--author", default="汇报人")
    parser.add_argument("--institute", default="东南大学")
    parser.add_argument("--force", action="store_true", help="overwrite an existing .tex file")
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    asset_dir = skill_root / "assets" / "simpleplus-seu"
    if not asset_dir.exists():
        raise SystemExit(f"Missing asset directory: {asset_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for name in THEME_FILES:
        src = asset_dir / name
        if src.exists():
            shutil.copy2(src, args.output_dir / name)

    tex_path = args.output_dir / args.filename
    if tex_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {tex_path} (use --force)")

    tex_path.write_text(
        starter_tex(args.title, args.subtitle, args.author, args.institute),
        encoding="utf-8",
    )
    print(f"Created {tex_path}")
    print(f"Copied SimplePlus SEU theme assets to {args.output_dir}")


if __name__ == "__main__":
    main()
