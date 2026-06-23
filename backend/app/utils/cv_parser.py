"""CV text extraction utilities."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path


def extract_text_from_file(path: Path, mime_type: str) -> str:
    suffix = path.suffix.lower()
    data = path.read_bytes()
    return extract_text_from_bytes(data, mime_type, suffix=suffix)


def extract_text_from_bytes(
    data: bytes,
    mime_type: str,
    *,
    suffix: str | None = None,
) -> str:
    ext = (suffix or "").lower()
    if ext == ".pdf" or mime_type == "application/pdf":
        return _extract_pdf_bytes(data)
    if ext in (".docx",) or "wordprocessingml" in mime_type:
        return _extract_docx_bytes(data)
    raise ValueError(f"Format non supporté : {ext or mime_type}")


def _extract_pdf_bytes(data: bytes) -> str:
    errors: list[str] = []

    try:
        import fitz  # PyMuPDF

        text_parts: list[str] = []
        with fitz.open(stream=data, filetype="pdf") as doc:
            for page in doc:
                if t := page.get_text():
                    text_parts.append(t)
        if text_parts:
            return clean_text("\n".join(text_parts))
        errors.append("pymupdf: document vide ou image scannée")
    except Exception as exc:
        errors.append(f"pymupdf: {exc}")

    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(BytesIO(data)) as pdf:
            for page in pdf.pages:
                if t := page.extract_text():
                    text_parts.append(t)
        if text_parts:
            return clean_text("\n".join(text_parts))
        errors.append("pdfplumber: aucun texte extrait")
    except Exception as exc:
        errors.append(f"pdfplumber: {exc}")

    detail = "; ".join(errors) if errors else "lecteur PDF indisponible"
    raise ValueError(f"Impossible d'extraire le texte du PDF ({detail}).")


def _extract_pdf(path: Path) -> str:
    return _extract_pdf_bytes(path.read_bytes())


def _extract_docx_bytes(data: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(data))
    text = clean_text("\n".join(p.text for p in doc.paragraphs if p.text.strip()))
    if not text:
        raise ValueError("Le fichier DOCX ne contient pas de texte lisible.")
    return text


def _extract_docx(path: Path) -> str:
    return _extract_docx_bytes(path.read_bytes())


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
