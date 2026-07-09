# Contributing to pdf-chunk-reader

Thanks for your interest in improving pdf-chunk-reader! This document explains how to set up a local dev environment, the conventions we follow, and how to open a pull request.

## Code of conduct

Be respectful and constructive. We want this to stay a small, dependency-light, framework-agnostic tool that any agent can pick up and run.

## Development setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/pdf-chunk-reader.git
cd pdf-chunk-reader

# 2. Install the only runtime dependency
pip install pypdf

# 3. Try it on any PDF
python scripts/pdf_splitter.py --help
python scripts/pdf_splitter.py "your_test.pdf" --output-dir ./chunks
```

There is **no build step** and **no test framework required** — the script is plain Python 3 and the workflow is a Markdown file.

## Design principles

Please keep contributions aligned with these principles:

1. **Zero framework dependency.** The core must remain a single pure-Python script (`scripts/pdf_splitter.py`) plus a Markdown workflow (`SKILL.md`). Do not introduce agent-specific SDKs or network calls.
2. **Local-only.** The script must never upload, post, or phone home with user documents. Privacy is a feature.
3. **Cross-agent friendly.** Anything you add to `SKILL.md` should be understandable by an LLM agent that simply reads the file and runs the script. Avoid wording that only one product understands.
4. **Minimal dependencies.** `pypdf` is the only allowed third-party import. If you think another library is needed, open an issue first to discuss.

## Branching & PR conventions

- Branch from `main`: `git checkout -b fix/chunk-overlap` or `feat/bookmark-split`.
- Keep PRs focused — one logical change per PR.
- Update `README.md` / `SKILL.md` if your change affects usage or the workflow.
- Bump the version in `README.md` badges when the public behavior changes (we follow semantic-ish `v1.x.y`).
- Write clear commit messages in English, e.g. `feat: split by PDF bookmarks`, `fix: off-by-one in last chunk`.

## What kinds of contributions we love

- New chunking strategies (by bookmark / section, not just by page).
- Better text-extraction fallbacks for scanned pages.
- Adapter snippets for more agent frameworks (drop-in `CLAUDE.md` / `codex.md` / etc.).
- Documentation, translations, and example datasets (without copyrighted PDFs, please).
- Bug reports with a reproducible command.

## Reporting bugs

Open an issue with:

- The exact command you ran.
- PDF page count and (approximate) size.
- The error message / unexpected behavior.
- Python version (`python --version`) and OS.

> Do **not** attach copyrighted or confidential PDFs to public issues. Describe them instead.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
