"""
Placement Reality Check — Document parsers for PDF, DOCX, and plain text.
"""

import io
import oauthlib
from pypdf import PdfReader


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from file(PDF)."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_document(file_bytes: bytes, filename: str) -> str:
    """
    Auto-detect file format and extract text.
    Supports: .pdf, .docx, .txt
    """
    lower = filename.lower()

    if lower.endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return parse_docx(file_bytes)
    elif lower.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore").strip()
    else:
        raise ValueError(f"Unsupported file format: {filename}. Use PDF, DOCX, or TXT.")
