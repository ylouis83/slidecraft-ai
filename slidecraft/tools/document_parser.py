"""
Document Parser — Extract content from PDF, DOCX, and Markdown files.
Uses PyMuPDF for PDF and python-docx for DOCX.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("slidecraft")


async def parse_document(file_path: str) -> str:
    """Parse a document and extract its text content.

    Supports: .pdf, .docx, .md, .txt
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(path)
    elif suffix == ".docx":
        return _parse_docx(path)
    elif suffix in (".md", ".txt", ".markdown"):
        return path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _parse_pdf(path: Path) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        logger.warning("PyMuPDF not installed, skipping PDF parsing")
        return f"[PDF 文件: {path.name} - 需要安装 PyMuPDF]"


def _parse_docx(path: Path) -> str:
    """Extract text from DOCX."""
    try:
        from docx import Document

        doc = Document(str(path))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        logger.warning("python-docx not installed, skipping DOCX parsing")
        return f"[DOCX 文件: {path.name} - 需要安装 python-docx]"
