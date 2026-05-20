# AiKhbar — Academic Report

`report.tex` is the LaTeX source for the project report, suitable for academic
submission.

## Building the PDF

### With a local LaTeX install
```bash
cd report
pdflatex report.tex
pdflatex report.tex   # run twice so the table of contents resolves
```

### With latexmk (recommended)
```bash
latexmk -pdf report.tex
```

### Online (no install)
Upload `report.tex` to [Overleaf](https://overleaf.com) and compile there.

## Output
`report.pdf` — the compiled report. Build artifacts (`.aux`, `.log`, `.toc`,
etc.) are ignored by git.
