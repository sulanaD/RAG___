from typing import Iterator, Tuple
from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument

def iter_txt_pages(path: Path, target_chars: int = 2500) -> Iterator[Tuple[int, str]]:
    text = path.read_text(errors="ignore")
    page = 1
    for i in range(0, len(text), target_chars):
        chunk = text[i:i+target_chars].strip()
        if chunk:
            yield page, chunk
            page += 1

def iter_pdf_pages(path: Path) -> Iterator[Tuple[int, str]]:
    reader = PdfReader(str(path))
    for i, page in enumerate(reader.pages, 1):
        txt = ""
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            yield i, txt

def iter_docx_pages(path: Path, target_chars: int = 2500) -> Iterator[Tuple[int, str]]:
    doc = DocxDocument(str(path))
    buf, total, page = [], 0, 1
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if total + len(t) > target_chars and buf:
            yield page, "\n".join(buf).strip()
            buf, total, page = [], 0, page + 1
        buf.append(t); total += len(t)
    if buf:
        yield page, "\n".join(buf).strip()

def iter_pages_for_file(path: Path):
    sfx = path.suffix.lower()
    if sfx == ".pdf":
        yield from iter_pdf_pages(path)
    elif sfx == ".docx":
        yield from iter_docx_pages(path)
    elif sfx == ".txt":
        yield from iter_txt_pages(path)
    else:
        return

