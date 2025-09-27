import io, zipfile, shutil
from pathlib import Path
from typing import List

ALLOWED = {".pdf", ".docx", ".txt", ".zip"}

def _safe_join(base: Path, *paths: str) -> Path:
    final = base.joinpath(*paths).resolve()
    if not str(final).startswith(str(base.resolve())):
        raise ValueError("Unsafe path in archive")
    return final

def extract_zip_recursive(zip_bytes: bytes, out_dir: Path, max_nested: int = 10) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    # First level
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for zi in z.infolist():
            name = zi.filename
            if name.endswith("/"):
                continue
            dest = _safe_join(out_dir, name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(zi) as src, open(dest, "wb") as dst:
                shutil.copyfileobj(src, dst)

    # Recurse nested zips
    all_files = list(out_dir.rglob("*"))
    level = 0
    while level < max_nested:
        zips = [p for p in all_files if p.is_file() and p.suffix.lower() == ".zip"]
        if not zips:
            break
        for zp in zips:
            with zipfile.ZipFile(str(zp), "r") as z:
                for zi in z.infolist():
                    if zi.filename.endswith("/"): continue
                    dest = _safe_join(zp.parent, zi.filename)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(zi) as src, open(dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)
            zp.unlink(missing_ok=True)
        all_files = list(out_dir.rglob("*"))
        level += 1

    return [p for p in out_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf",".docx",".txt"}]

