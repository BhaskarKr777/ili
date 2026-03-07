"""
PDF Reader Tool
===============
Extract and summarize text from PDF files.

Input formats:
  "C:/path/to/file.pdf"               — extract all text
  "C:/path/to/file.pdf | page 3"      — extract specific page
  "C:/path/to/file.pdf | pages 1-5"   — extract page range
  "C:/path/to/file.pdf | summary"     — first 500 chars as preview
"""

import os
import re
from .base_tool import BaseTool


class PDFReaderTool(BaseTool):
    name = "read_pdf"
    description = (
        "Read and extract text from a PDF file. "
        "Input: 'path/to/file.pdf' to read all text, "
        "'path/to/file.pdf | page 3' for a specific page, "
        "'path/to/file.pdf | pages 1-5' for a range, "
        "or 'path/to/file.pdf | summary' for a quick preview."
    )

    def run(self, input_text: str) -> str:
        # Clean LLM junk
        inp = re.sub(r'\s*[\(\[].*', '', input_text).strip()

        # ── Parse path and optional command ───────────────────────────────────
        if "|" in inp:
            parts   = inp.split("|", 1)
            path    = parts[0].strip()
            command = parts[1].strip().lower()
        else:
            path    = inp.strip()
            command = "all"

        # ── Validate file ──────────────────────────────────────────────────────
        if not path:
            return "No file path provided. Use: 'path/to/file.pdf'"

        if not os.path.exists(path):
            return f"File not found: {path}"

        if not path.lower().endswith(".pdf"):
            return f"Not a PDF file: {path}"

        # ── Load PDF ───────────────────────────────────────────────────────────
        try:
            import pypdf
        except ImportError:
            try:
                import PyPDF2 as pypdf
            except ImportError:
                return "pypdf is not installed. Run: pip install pypdf"

        try:
            reader     = pypdf.PdfReader(path)
            total_pages= len(reader.pages)
        except Exception as e:
            return f"Error opening PDF: {e}"

        filename = os.path.basename(path)

        # ── SUMMARY (preview) ─────────────────────────────────────────────────
        if command == "summary":
            text = ""
            for page in reader.pages[:3]:
                text += page.extract_text() or ""
                if len(text) >= 500:
                    break
            preview = text[:500].strip()
            return (
                f"📄 {filename} ({total_pages} pages)\n\n"
                f"Preview:\n{preview}…\n\n"
                f"Use 'read_pdf | {path}' to read full content."
            )

        # ── SPECIFIC PAGE ─────────────────────────────────────────────────────
        match = re.match(r'page\s+(\d+)', command)
        if match:
            page_num = int(match.group(1))
            if page_num < 1 or page_num > total_pages:
                return f"Page {page_num} doesn't exist. PDF has {total_pages} pages."
            text = reader.pages[page_num - 1].extract_text() or ""
            if not text.strip():
                return f"Page {page_num} appears to be empty or image-only."
            return (
                f"📄 {filename} — Page {page_num}/{total_pages}\n\n"
                f"{text.strip()}"
            )

        # ── PAGE RANGE ────────────────────────────────────────────────────────
        match = re.match(r'pages\s+(\d+)-(\d+)', command)
        if match:
            start = int(match.group(1))
            end   = int(match.group(2))
            start = max(1, start)
            end   = min(total_pages, end)
            text  = ""
            for i in range(start - 1, end):
                page_text = reader.pages[i].extract_text() or ""
                text += f"\n--- Page {i+1} ---\n{page_text}"
            if not text.strip():
                return f"Pages {start}-{end} appear to be empty or image-only."
            # Truncate if too long
            if len(text) > 3000:
                text = text[:3000] + f"\n\n… (truncated, showing pages {start}-{end})"
            return f"📄 {filename} — Pages {start} to {end}\n{text.strip()}"

        # ── ALL TEXT ──────────────────────────────────────────────────────────
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text() or "(empty page)\n"

        if not text.strip():
            return "Could not extract text. The PDF may be image-based — try OCR instead."

        # Truncate very long PDFs
        if len(text) > 4000:
            text = text[:4000] + f"\n\n… (truncated — {total_pages} pages total)"

        return f"📄 {filename} ({total_pages} pages)\n\n{text.strip()}"