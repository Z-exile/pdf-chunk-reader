---
name: pdf-chunk-reader
description: "A portable, framework-free AI-agent workflow for reading oversized PDFs (theses, reviews, long papers): split into page-based chunks, extract text per chunk, read each chunk sequentially with your agent's file-read tool, then consolidate into a structured 10-section summary. Auto-triggers for PDFs >15 pages or >5MB. Works with WorkBuddy, CodeBuddy, Claude Code, Codex, Cursor, Cline, Aider, or any agent that can run shell commands and read files. Solves the 'cannot read large PDF in one pass' problem."
version: "1.0.0"
agent_created: true
trigger_when:
  - "Reading a PDF with more than 15 pages"
  - "Reading a PDF larger than 5MB"
  - "Read tool returns truncated content for a PDF"
  - "User asks to analyze/summarize a large paper, thesis, or report"
  - "Expert needs to extract detailed information from a lengthy PDF"
---

# PDF Chunk Reader

## The problem it solves

When reading a large PDF (long paper, thesis, review, report), the file-read tool (e.g. Read) may:
- truncate content due to context limits
- drop middle pages
- fail to extract figure/table data

This skill provides a standard **split → read chunk-by-chunk → consolidate** workflow that handles PDFs of any size systematically.

## Installation & dependencies

1. **Dependencies**: Python 3.8+ and `pypdf`
   ```bash
   pip install pypdf
   ```
2. **Location (any agent)**: This repo is a **self-contained package** — one Python script + one workflow doc, **with no dependency on any agent framework**. Drop it into your agent's "skills / commands / instructions" load location:
   - WorkBuddy / CodeBuddy: `~/.workbuddy/skills/pdf-chunk-reader/`
   - Claude Code: `~/.claude/skills/pdf-chunk-reader/` (reads SKILL.md directly)
   - Codex: merge this file into `codex.md` / `AGENTS.md`, or read and run the script per the workflow
   - Cursor / Cline / Aider / others: let the agent read this file and run `scripts/pdf_splitter.py` when needed
   - Pure CLI: no install; just `python scripts/pdf_splitter.py ...`
   Final layout: `.../pdf-chunk-reader/SKILL.md` and `.../pdf-chunk-reader/scripts/pdf_splitter.py`.
3. **Activate**: In auto-trigger-capable agents, refresh/restart and large PDFs will auto-trigger per `trigger_when`; other agents can be told "read this large PDF" in chat, or follow this workflow.

## Workflow overview

```
Large PDF → [1. Analyze] → [2. Split by page] → [3. Read chunk-by-chunk] → [4. Structured note extraction] → [5. Consolidate] → Unified summary
```

## Step-by-step

### Step 1: Analyze the PDF

Run the splitter in info-only mode to get page count, size, and metadata:

```bash
"<python_path>" "<skill_dir>/scripts/pdf_splitter.py" "<pdf_path>" --info-only
```

- `<python_path>`: your Python interpreter. WorkBuddy users can use its managed environment (e.g. `<workbuddy_dir>/.workbuddy/binaries/python/envs/default/Scripts/python.exe`); other environments use `python3` (after `pip install pypdf`).
- If pages ≤ 15 and file < 3MB: read directly with the Read tool, no split needed.
- If pages > 15 or file > 5MB: go to Step 2.

### Step 2: Split the PDF

Run the splitter with defaults (auto chunk size + text extraction):

```bash
"<python_path>" "<skill_dir>/scripts/pdf_splitter.py" "<pdf_path>" --output-dir "<output_dir>"
```

- Default output dir: `<pdf_parent>/_split_<filename>/`
- The script auto-selects chunk size:
  - ≤20 pages: no split (single block)
  - 21–50 pages: 10 per chunk
  - 51–100 pages: 15 per chunk
  - 101–300 pages: 20 per chunk
  - 300+ pages: 25 per chunk
- Each chunk yields both a `.pdf` file and a `.txt` text extraction
- A `manifest.json` is generated with all chunk metadata and the reading protocol

**Custom chunk size** (optional):
```bash
"<python_path>" "<skill_dir>/scripts/pdf_splitter.py" "<pdf_path>" --pages-per-chunk 15 --output-dir "<output_dir>"
```

### Step 3: Read chunks in order

1. **Read the manifest first** to understand the layout:
   ```
   Read("<output_dir>/manifest.json")
   ```
2. **Read each chunk's `.txt` in order** (smaller and faster than PDF):
   ```
   Read("<output_dir>/chunk_001_p1-10.txt")
   Read("<output_dir>/chunk_002_p11-20.txt")
   ...
   ```
3. **If a `.txt` is still too large** (>256KB), paginate with offset/limit:
   ```
   Read("<output_dir>/chunk_001_p1-10.txt", offset=0, limit=500)
   Read("<output_dir>/chunk_001_p1-10.txt", offset=500, limit=500)
   ```
4. **For figures/tables**: read the chunk PDF directly (most agents' file-read tools support PDF visualization):
   ```
   Read("<output_dir>/chunk_003_p21-25.pdf")
   ```

### Step 4: Extract structured notes per chunk

For each chunk, extract (into a note file or inline notes):

```
## Chunk N (pages X-Y)

### Key findings
- ...

### Method / parameters
- ...

### Quantitative data
- Tensile strength: XXX MPa
- Yield strength: XXX MPa
- Elongation: XX%
- Hardness: XX HV
- ...

### Referenced figures/tables
- Fig. X (p.XX): ...
- Tab. Y (p.XX): ...

### Citations worth tracking
- Author et al., Year, Journal — relevance ...
```

### Step 5: Consolidate into a unified summary

After reading all chunks, merge the per-chunk notes into one document using this template:

```
# Literature Analysis: [Paper Title]

## 1. Bibliographic info
- Title: ...
- Authors: ...
- Year: ...
- Journal/Source: ...
- DOI: ...

## 2. Research question & hypothesis
...

## 3. Experimental method
- Materials: ...
- Equipment: ...
- Key parameters: ...

## 4. Key results (with units and page numbers)
...

## 5. Microstructure & mechanism analysis
...

## 6. Performance data table
| Metric | Value | Condition | Source page |
|--------|-------|-----------|-------------|
| ... | ... | ... | p.XX |

## 7. Conclusions & implications
...

## 8. Relevance to your project / domain
...

## 9. Figures & tables index
...

## 10. Citations worth tracking
...
```

Save the consolidated summary to the output dir:
```
Write("<output_dir>/consolidated_summary.md", ...)
```

## Integrating with expert systems

When this skill is invoked inside an expert agent (e.g. your research expert), the expert should:

1. **Auto-trigger**: when the user asks about a large PDF and the file is big, run this workflow first, then answer.
2. **Domain extraction**: fill the domain-specific sections of the consolidation template with the expert's domain knowledge.
3. **Cross-reference**: after consolidation, check the expert's literature index and annotate related papers.
4. **Cache for reuse**: save the consolidated summary as `.txt` into the expert's `references/fulltext/` directory for later retrieval.

## Important notes

- **Text extraction limits**: pypdf may fail to capture in-figure text, complex-layout tables, or scanned PDFs. In such cases read the chunk PDF directly (the Read tool handles visualization).
- **Encoding**: text files are UTF-8, full Chinese support.
- **Cleanup**: chunk files are temporary; after consolidation you may delete the output dir to save space. If you'll reference it later, keep `consolidated_summary.md`.
- **Performance**: splitting a 100-page PDF takes ~5–10s; text extraction adds ~2–5s per chunk.
- **Very long theses** (200+ pages): prefer `--pages-per-chunk 25`, and read only relevant sections via the table of contents (usually in the first chunk).

## File locations

- Script: `<skill_dir>/scripts/pdf_splitter.py`
- Python: any Python 3.8+ interpreter (needs `pip install pypdf`); replace `<python_path>` in commands with the actual path.
- Default output: `<pdf_parent>/_split_<pdf_stem>/`
