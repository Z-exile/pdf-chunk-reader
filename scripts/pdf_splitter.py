#!/usr/bin/env python3
"""
Large PDF Splitter & Reader Workflow
=====================================
Splits large PDF files into readable chunks, extracts text per chunk,
and generates a structured manifest for sequential reading + consolidation.

Usage:
    python pdf_splitter.py <pdf_path> [--output-dir <dir>] [--pages-per-chunk <n>] [--extract-text]

Examples:
    # Auto-split with default settings (15 pages per chunk, extract text)
    python pdf_splitter.py "D:/docs/some_paper.pdf"

    # Custom chunk size, no text extraction (PDF chunks only)
    python pdf_splitter.py "D:/docs/thesis.pdf" --pages-per-chunk 20 --no-text

    # Specify output directory
    python pdf_splitter.py "input.pdf" --output-dir "C:/tmp/split_output"
"""

import argparse
import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf", file=sys.stderr)
    sys.exit(1)


def get_pdf_info(pdf_path: str) -> dict:
    """Extract PDF metadata and basic info."""
    reader = PdfReader(pdf_path)
    info = {
        "file_path": os.path.abspath(pdf_path),
        "file_name": os.path.basename(pdf_path),
        "file_size_mb": round(os.path.getsize(pdf_path) / (1024 * 1024), 2),
        "total_pages": len(reader.pages),
        "metadata": {},
    }
    meta = reader.metadata
    if meta:
        for key in ["/Title", "/Author", "/Subject", "/Keywords", "/Creator", "/Producer"]:
            val = meta.get(key)
            if val:
                info["metadata"][key.lstrip("/")] = str(val)
    return info


def auto_chunk_size(total_pages: int) -> int:
    """Determine optimal pages per chunk based on document size."""
    if total_pages <= 20:
        return total_pages  # Small enough to read in one go
    elif total_pages <= 50:
        return 10
    elif total_pages <= 100:
        return 15
    elif total_pages <= 300:
        return 20
    else:
        return 25


def split_pdf(pdf_path: str, output_dir: str, pages_per_chunk: int, extract_text: bool) -> list:
    """Split PDF into chunks and optionally extract text from each chunk."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    if pages_per_chunk <= 0 or pages_per_chunk >= total_pages:
        pages_per_chunk = total_pages  # No split needed

    chunks = []
    chunk_num = 0
    
    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk, total_pages)
        chunk_num += 1
        
        # Write PDF chunk
        writer = PdfWriter()
        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])
        
        chunk_filename = f"chunk_{chunk_num:03d}_p{start+1}-{end}.pdf"
        chunk_pdf_path = os.path.join(output_dir, chunk_filename)
        with open(chunk_pdf_path, "wb") as f:
            writer.write(f)
        
        chunk_info = {
            "chunk_number": chunk_num,
            "page_range": f"{start+1}-{end}",
            "start_page": start + 1,
            "end_page": end,
            "page_count": end - start,
            "pdf_file": chunk_filename,
            "pdf_path": os.path.abspath(chunk_pdf_path),
            "pdf_size_kb": round(os.path.getsize(chunk_pdf_path) / 1024, 1),
        }
        
        # Extract text if requested
        if extract_text:
            text_parts = []
            for page_num in range(start, end):
                try:
                    page_text = reader.pages[page_num].extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    text_parts.append(f"--- Page {page_num + 1} ---\n[TEXT EXTRACTION FAILED: {e}]")
            
            full_text = "\n\n".join(text_parts)
            text_filename = f"chunk_{chunk_num:03d}_p{start+1}-{end}.txt"
            text_path = os.path.join(output_dir, text_filename)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            chunk_info["text_file"] = text_filename
            chunk_info["text_path"] = os.path.abspath(text_path)
            chunk_info["text_size_kb"] = round(len(full_text.encode("utf-8")) / 1024, 1)
            chunk_info["text_chars"] = len(full_text)
        
        chunks.append(chunk_info)
        print(f"  Chunk {chunk_num}/{((total_pages - 1) // pages_per_chunk) + 1}: pages {start+1}-{end} "
              f"({'with text' if extract_text else 'PDF only'})")
    
    return chunks


def generate_manifest(pdf_info: dict, chunks: list, output_dir: str, pages_per_chunk: int) -> str:
    """Generate a JSON manifest file with all chunk metadata."""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "source_pdf": pdf_info,
        "split_config": {
            "pages_per_chunk": pages_per_chunk,
            "total_chunks": len(chunks),
            "text_extracted": any("text_file" in c for c in chunks),
        },
        "chunks": chunks,
        "reading_protocol": {
            "step_1": "Read each chunk's text file (or PDF) sequentially using the Read tool",
            "step_2": "For each chunk, extract: key findings, methods, data points, figures/tables referenced",
            "step_3": "After reading all chunks, consolidate into a unified summary",
            "step_4": "Cross-reference findings across chunks for completeness",
            "note": "If a chunk's text file is still too large (>256KB), use Read with offset/limit to paginate",
        },
        "consolidation_template": {
            "title": "Extract from manifest source_pdf.file_name",
            "sections": [
                "1. Bibliographic Info (title, authors, year, journal/source)",
                "2. Research Question & Hypothesis",
                "3. Methodology (materials, equipment, parameters)",
                "4. Key Results (quantitative data with units)",
                "5. Microstructure & Mechanism Analysis",
                "6. Performance Data (strength, hardness, elongation, corrosion, etc.)",
                "7. Conclusions & Implications",
                "8. Relevance to Your Project / Domain",
                "9. Figures/Tables Index (page numbers)",
                "10. Key Citations for Follow-up",
            ],
        },
    }
    
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    return manifest_path


def main():
    parser = argparse.ArgumentParser(
        description="Split large PDF into readable chunks with optional text extraction"
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to split")
    parser.add_argument("--output-dir", "-o", default=None, 
                        help="Output directory (default: <pdf_dir>/_split_<filename>)")
    parser.add_argument("--pages-per-chunk", "-p", type=int, default=0,
                        help="Pages per chunk (default: auto-calculated)")
    parser.add_argument("--no-text", action="store_true",
                        help="Skip text extraction (PDF chunks only)")
    parser.add_argument("--info-only", action="store_true",
                        help="Only print PDF info, don't split")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"ERROR: File not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    # Get PDF info
    print(f"Analyzing: {args.pdf_path}")
    pdf_info = get_pdf_info(args.pdf_path)
    
    print(f"\n=== PDF Info ===")
    print(f"  File: {pdf_info['file_name']}")
    print(f"  Size: {pdf_info['file_size_mb']} MB")
    print(f"  Pages: {pdf_info['total_pages']}")
    if pdf_info["metadata"]:
        for k, v in pdf_info["metadata"].items():
            print(f"  {k}: {v}")
    
    if args.info_only:
        print(json.dumps(pdf_info, ensure_ascii=False, indent=2))
        return
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        pdf_stem = Path(args.pdf_path).stem
        pdf_parent = os.path.dirname(os.path.abspath(args.pdf_path))
        output_dir = os.path.join(pdf_parent, f"_split_{pdf_stem}")
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    # Determine chunk size
    total_pages = pdf_info["total_pages"]
    if args.pages_per_chunk > 0:
        pages_per_chunk = args.pages_per_chunk
    else:
        pages_per_chunk = auto_chunk_size(total_pages)
    
    print(f"Chunk size: {pages_per_chunk} pages/chunk")
    print(f"Text extraction: {'No' if args.no_text else 'Yes'}")
    print(f"\nSplitting...")
    
    # Split PDF
    extract_text = not args.no_text
    chunks = split_pdf(args.pdf_path, output_dir, pages_per_chunk, extract_text)
    
    # Generate manifest
    manifest_path = generate_manifest(pdf_info, chunks, output_dir, pages_per_chunk)
    
    print(f"\n=== Done ===")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Manifest: {manifest_path}")
    print(f"  Output dir: {output_dir}")
    print(f"\nNext steps:")
    print(f"  1. Read manifest.json for chunk list and reading protocol")
    print(f"  2. Read each chunk's .txt file (or .pdf) sequentially")
    print(f"  3. Consolidate findings using the template in manifest")


if __name__ == "__main__":
    main()
