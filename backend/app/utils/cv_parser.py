"""CV text extraction utilities."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path


def extract_text_from_file(path: Path, mime_type: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf" or mime_type == "application/pdf":
        return _extract_pdf(path)
    if suffix in (".docx",) or "wordprocessingml" in mime_type:
        return _extract_docx(path)
    raise ValueError(f"Format non supporté : {suffix or mime_type}")


def _extract_pdf(path: Path) -> str:
    text_parts: list[str] = []
    try:
        import fitz  # PyMuPDF

        with fitz.open(path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
    except Exception:
        import pdfplumber

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                if t := page.extract_text():
                    text_parts.append(t)
    return clean_text("\n".join(text_parts))


def _extract_docx(path: Path) -> str:
    from docx import Document

    doc = Document(str(path))
    return clean_text("\n".join(p.text for p in doc.paragraphs if p.text.strip()))


def clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_github_username(url: str | None) -> str | None:
    if not url:
        return None
    url = url.strip().rstrip("/")
    if url.startswith("@"):
        return url[1:]
    match = re.search(r"github\.com/([A-Za-z0-9_-]+)", url, re.I)
    if match:
        return match.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]+", url):
        return url
    return None
