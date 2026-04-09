#!/usr/bin/env python3
"""
Export user guide markdown files to PDF using Eisvogel + xelatex.

Usage:
    cd docs/
    python3 export_pdf.py managers      # exports user_guide_managers.pdf
    python3 export_pdf.py all_users     # exports user_guide_all_users.pdf
    python3 export_pdf.py all           # exports both

Requirements:
    - pandoc
    - xelatex (texlive)
    - Eisvogel template (~/.pandoc/templates/eisvogel.latex)
"""

import re
import subprocess
import sys
import os

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_hashes_to_bold(content):
    """
    Convert ##### and ###### headings to bold paragraphs.
    LaTeX \paragraph is a run-in heading that flows into the following text
    regardless of blank lines; bold text on its own line behaves correctly.
    """
    content = re.sub(r'^#{6} (.+)$', r'\n**\1**\n', content, flags=re.MULTILINE)
    content = re.sub(r'^#{5} (.+)$', r'\n**\1**\n', content, flags=re.MULTILINE)
    return content


def ensure_blank_line_after_headings(content):
    """
    Ensure a blank line follows every ##### heading.
    pandoc maps ##### to LaTeX \paragraph, which runs inline into the
    following text unless there is a blank line after the heading.
    """
    lines = content.split('\n')
    result = []
    for i, line in enumerate(lines):
        result.append(line)
        if line.startswith('#####') and not line.startswith('######'):
            # Insert blank line after this heading if there isn't one already
            next_line = lines[i + 1] if i + 1 < len(lines) else ''
            if next_line.strip() != '':
                result.append('')
    return '\n'.join(result)


def ensure_blank_lines_before_blocks(content):
    """
    Insert a blank line before lists, tables, and blockquotes when the
    preceding non-empty line would not naturally separate them.
    Also handles the case of a list item label ending with ':' immediately
    followed by a table (nested table inside a list item).
    """
    lines = content.split('\n')
    result = []

    def is_block_start(line):
        s = line.lstrip()
        return (
            bool(re.match(r'^[-*+] ', s)) or   # unordered list item
            bool(re.match(r'^\d+\. ', s)) or    # ordered list item
            s.startswith('|') or                 # table row
            s.startswith('>')                    # blockquote
        )

    def is_continuation(line):
        """Lines that don't need a blank before a following block."""
        s = line.strip()
        return (
            not s or
            s.startswith('#') or
            s.startswith('\\')          # LaTeX command e.g. \newpage
        )

    def ends_with_colon_list_item(line):
        """A list item label that ends with ':' (the table is its content)."""
        s = line.rstrip()
        return bool(re.match(r'\s*[-*+] .+:$', s))

    for i, line in enumerate(lines):
        prev_nonempty = next(
            (result[j] for j in range(len(result) - 1, -1, -1) if result[j].strip()),
            None
        )

        if is_block_start(line) and prev_nonempty is not None:
            prev_s = prev_nonempty.strip()
            # Always insert a blank line unless the previous non-empty line
            # is already a blank, a heading, a LaTeX command, OR is itself
            # the same type of block AND does NOT end with ':'
            need_blank = not is_continuation(prev_nonempty) and (
                ends_with_colon_list_item(prev_nonempty) or
                not is_block_start(prev_nonempty)
            )
            if need_blank:
                result.append('')

        result.append(line)

    return '\n'.join(result)


def convert_managers():
    print("Converting user_guide_managers.md → user_guide_managers_latex.md ...")

    with open(os.path.join(DOCS_DIR, "user_guide_managers.md"), "r") as f:
        content = f.read()

    # 1. Strip H1 title + metadata block + trailing ---
    content = re.sub(
        r"^# GL-Ecologie.*?\n\n\*\*Version:.*?\n\*\*Last updated:.*?\n\*\*Prepared by:.*?\n\n---\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    # 1b. Strip the manually-written Table of Contents section.
    #     Pandoc will generate it automatically with --toc, ensuring
    #     all anchor links are correct.
    content = re.sub(
        r"## Table of Contents\n.*?\n---\n",
        "",
        content,
        flags=re.DOTALL,
    )

    # 2. Convert page-break divs to \newpage
    content = content.replace(
        '<div style="page-break-before: always;"></div>', "\n\\newpage\n"
    )

    # 3. Convert <p align="center"> image blocks → ![caption](src)
    def replace_image_block(m):
        return f"\n![{m.group(2)}]({m.group(1)})\n"

    content = re.sub(
        r'[ \t]*<br>[ \t]*\n[ \t]*<p align="center">[ \t]*\n[ \t]*<img src="([^"]+)" alt="[^"]*"\s*/?>\s*\n[ \t]*</p>[ \t]*\n[ \t]*<center><i>(.*?)</i></center>[ \t]*\n(?:[ \t]*<br>[ \t]*\n)?',
        replace_image_block,
        content,
        flags=re.DOTALL,
    )
    # Indented variants (inside list items)
    content = re.sub(
        r'[ \t]*<br>[ \t]*\n[ \t]*<p align="center">[ \t]*\n[ \t]*<img src="([^"]+)" alt="[^"]*"\s*/?>\s*\n[ \t]*</p>[ \t]*\n[ \t]*<center><i>(.*?)</i></center>[ \t]*\n[ \t]*<br>',
        lambda m: f"\n\n![{m.group(2)}]({m.group(1)})\n\n",
        content,
        flags=re.DOTALL,
    )

    # 4. Remove remaining <br> tags — only consume spaces/tabs on same line,
    #    NOT newlines, so blank lines around blockquotes/lists are preserved.
    content = re.sub(r'[ \t]*<br>[ \t]*\n?', '\n', content)

    # 5. Strip standalone --- (thematic breaks) from the body —
    #    these cause YAML parse errors when pandoc sees them.
    content = re.sub(r'\n---\n', '\n', content)

    # 6. Remove leftover bare HTML tags
    content = re.sub(r'[ \t]*<p align="center">[ \t]*\n?', '', content)
    content = re.sub(r'[ \t]*</p>[ \t]*\n?', '\n', content)
    content = re.sub(r'[ \t]*<center><i>(.*?)</i></center>[ \t]*\n?', '', content, flags=re.DOTALL)

    # 7. Convert ###### headings → bold paragraphs (too deep for LaTeX heading hierarchy)
    content = convert_hashes_to_bold(content)

    # 8. Ensure blank line after every ##### heading (LaTeX \paragraph runs inline otherwise)
    content = ensure_blank_line_after_headings(content)

    # 9. Ensure blank lines before lists, tables, and blockquotes
    content = ensure_blank_lines_before_blocks(content)

    # 10. Collapse 3+ blank lines into 2
    content = re.sub(r'\n{3,}', '\n\n', content)

    # 11. Prepend YAML frontmatter
    frontmatter = """\
---
title: "GL-Ecologie — Odoo Planning System: Manager User Guide"
author: "Ruiz Burgos Ecology and Software"
date: "2026-04-09"
titlepage: true
titlepage-color: "1b4332"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "2d6a4f"
toc-own-page: true
colorlinks: true
linkcolor: teal
urlcolor: teal
header-includes:
  - |
    \\usepackage{graphicx}
    \\setkeys{Gin}{width=\\linewidth,height=0.45\\textheight,keepaspectratio}
    \\usepackage{mdframed}
    \\definecolor{calloutbg}{HTML}{FFF3E0}
    \\definecolor{calloutborder}{HTML}{E67E22}
    \\AtBeginDocument{\\renewenvironment{quote}{\\begin{mdframed}[backgroundcolor=calloutbg,linecolor=calloutborder,linewidth=3pt,topline=false,bottomline=false,rightline=false,innerleftmargin=10pt,innerrightmargin=10pt,innertopmargin=6pt,innerbottommargin=6pt]\\small}{\\end{mdframed}}}
    \\makeatletter
    \\renewcommand\\paragraph{\\@startsection{paragraph}{4}{\\z@}{-1.5ex\\@plus-1ex\\@minus-.2ex}{1ex\\@plus.2ex}{\\normalfont\\normalsize\\bfseries}}
    \\makeatother
---

"""

    output = frontmatter + content.lstrip()

    latex_md = os.path.join(DOCS_DIR, "user_guide_managers_latex.md")
    with open(latex_md, "w") as f:
        f.write(output)

    print(f"  Written: {latex_md}")
    return latex_md


def build_pdf(latex_md, output_pdf):
    print(f"Building PDF: {output_pdf} ...")
    result = subprocess.run(
        [
            "pandoc", latex_md,
            "--pdf-engine=xelatex",
            "--template=eisvogel",
            "--from", "markdown",
            "--toc",
            "--toc-depth=4",
            "-o", output_pdf,
        ],
        cwd=DOCS_DIR,
    )
    if result.returncode == 0:
        size = os.path.getsize(output_pdf)
        print(f"  Done: {output_pdf} ({size // 1024} KB)")
    else:
        print(f"  ERROR: pandoc exited with code {result.returncode}")
        sys.exit(result.returncode)


def export_managers():
    latex_md = convert_managers()
    build_pdf(latex_md, os.path.join(DOCS_DIR, "user_guide_managers.pdf"))


def export_all_users():
    print("Building user_guide_all_users.pdf (using existing _latex.md) ...")
    build_pdf(
        os.path.join(DOCS_DIR, "user_guide_all_users_latex.md"),
        os.path.join(DOCS_DIR, "user_guide_all_users.pdf"),
    )


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    os.chdir(DOCS_DIR)

    if target == "managers":
        export_managers()
    elif target == "all_users":
        export_all_users()
    elif target == "all":
        export_managers()
        export_all_users()
    else:
        print(f"Unknown target: {target}. Use: managers | all_users | all")
        sys.exit(1)
