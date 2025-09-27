import io, zipfile, shutil
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

# Supported file extensions for processing
ALLOWED = {".pdf", ".docx", ".txt", ".zip"}

# Common image extensions to skip
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"}

# Other common extensions to skip
SKIP_EXTENSIONS = {".csv", ".json", ".xml", ".yml", ".yaml", ".log", ".md", ".html", ".css", ".js", ".exe", ".dll", ".so", ".dmg"}

def _safe_join(base: Path, *paths: str) -> Path:
    """Safely join paths preventing directory traversal attacks"""
    # Join paths without resolving first
    final = base.joinpath(*paths)
    
    # Check if the final path is under the base directory
    try:
        # Use relative_to to check if final is under base
        final.relative_to(base)
    except ValueError:
        raise ValueError(f"Unsafe path in archive: {final}")
    
    return final

def _is_metadata_file(path: str) -> bool:
    """Check if file is metadata that should be skipped"""
    path_lower = path.lower()
    
    # macOS metadata
    if "__macosx" in path_lower or path.startswith("._"):
        return True
    
    # Windows metadata
    if "thumbs.db" in path_lower or "desktop.ini" in path_lower:
        return True
    
    # Version control
    if "/.git/" in path_lower or "/.svn/" in path_lower or "/.hg/" in path_lower:
        return True
    
    # IDE files
    if "/.vscode/" in path_lower or "/.idea/" in path_lower:
        return True
    
    return False

def _should_skip_file(file_path: Path) -> tuple[bool, str]:
    """
    Determine if file should be skipped and why
    Returns (should_skip, reason)
    """
    file_ext = file_path.suffix.lower()
    file_name = file_path.name.lower()
    path_str = str(file_path).lower()
    
    # Check metadata files
    if _is_metadata_file(str(file_path)):
        return True, "metadata file"
    
    # Check if it's a supported file type
    if file_ext in ALLOWED:
        return False, "supported file type"
    
    # Check image files
    if file_ext in IMAGE_EXTENSIONS:
        return True, f"image file ({file_ext})"
    
    # Check other unsupported files
    if file_ext in SKIP_EXTENSIONS:
        return True, f"unsupported file type ({file_ext})"
    
    # Skip empty files
    try:
        if file_path.exists() and file_path.stat().st_size == 0:
            return True, "empty file"
    except:
        pass
    
    # Skip very large individual files (>100MB)
    try:
        if file_path.exists() and file_path.stat().st_size > 100 * 1024 * 1024:
            return True, f"file too large ({file_path.stat().st_size // (1024*1024)}MB)"
    except:
        pass
    
    # If no extension, probably skip unless it's a known text file
    if not file_ext:
        if file_name in ["readme", "license", "changelog", "makefile"]:
            return False, "known text file without extension"
        return True, "no file extension"
    
    # Unknown extension - skip with warning
    return True, f"unknown file type ({file_ext})"

def extract_zip_recursive(zip_bytes: bytes, out_dir: Path, max_nested: int = 10) -> List[Path]:
    """
    Extract ZIP file recursively, handling nested folders and filtering unsupported files
    """
    logger.info(f"🔄 Starting ZIP extraction to {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    extracted_files = []
    skipped_files = []
    error_files = []

    # First level extraction
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            total_entries = len(z.infolist())
            logger.info(f"📋 ZIP contains {total_entries} entries")
            
            for idx, zi in enumerate(z.infolist()):
                name = zi.filename
                
                # Skip directories
                if name.endswith("/"):
                    logger.debug(f"📁 Creating directory: {name}")
                    continue
                
                # Check for metadata files early
                if _is_metadata_file(name):
                    logger.debug(f"⏭️ Skipping metadata file: {name}")
                    skipped_files.append((name, "metadata"))
                    continue
                
                try:
                    dest = _safe_join(out_dir, name)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract file
                    with z.open(zi) as src, open(dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    
                    extracted_files.append(dest)
                    
                    if (idx + 1) % 100 == 0:
                        logger.info(f"📤 Extracted {idx + 1}/{total_entries} files...")
                        
                except Exception as e:
                    logger.warning(f"❌ Failed to extract {name}: {e}")
                    error_files.append((name, str(e)))
                    continue

        logger.info(f"✅ Extracted {len(extracted_files)} files from main ZIP")
        
    except zipfile.BadZipFile:
        logger.error("❌ Invalid ZIP file format")
        raise ValueError("Invalid ZIP file format")
    except Exception as e:
        logger.error(f"❌ ZIP extraction error: {e}")
        raise ValueError(f"ZIP extraction failed: {e}")

    # Handle nested ZIP files recursively
    all_files = list(out_dir.rglob("*"))
    level = 0
    
    while level < max_nested:
        zip_files = [p for p in all_files if p.is_file() and p.suffix.lower() == ".zip"]
        if not zip_files:
            break
        
        logger.info(f"🔄 Processing {len(zip_files)} nested ZIP files (level {level + 1})")
        
        for zip_path in zip_files:
            try:
                logger.debug(f"📦 Extracting nested ZIP: {zip_path}")
                
                with zipfile.ZipFile(str(zip_path), "r") as z:
                    for zi in z.infolist():
                        if zi.filename.endswith("/"):
                            continue
                        
                        if _is_metadata_file(zi.filename):
                            continue
                        
                        dest = _safe_join(zip_path.parent, zi.filename)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        
                        with z.open(zi) as src, open(dest, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        
                        extracted_files.append(dest)
                
                # Remove the nested ZIP file after extraction
                zip_path.unlink(missing_ok=True)
                
            except Exception as e:
                logger.warning(f"❌ Failed to extract nested ZIP {zip_path}: {e}")
                error_files.append((str(zip_path), str(e)))
        
        # Update file list for next iteration
        all_files = list(out_dir.rglob("*"))
        level += 1

    if level >= max_nested:
        logger.warning(f"⚠️ Reached maximum nesting level ({max_nested})")

    # Filter files by supported types
    supported_files = []
    
    logger.info("🔍 Filtering extracted files by supported types...")
    
    for file_path in extracted_files:
        if not file_path.exists():
            continue
            
        should_skip, reason = _should_skip_file(file_path)
        
        if should_skip:
            logger.debug(f"⏭️ Skipping {file_path.name}: {reason}")
            skipped_files.append((str(file_path.relative_to(out_dir)), reason))
        else:
            logger.debug(f"✅ Including {file_path.name}: {reason}")
            supported_files.append(file_path)

    # Log summary
    logger.info(f"📊 Extraction Summary:")
    logger.info(f"   • Total extracted: {len(extracted_files)} files")
    logger.info(f"   • Supported files: {len(supported_files)}")
    logger.info(f"   • Skipped files: {len(skipped_files)}")
    logger.info(f"   • Errors: {len(error_files)}")
    
    if skipped_files:
        skip_reasons = {}
        for _, reason in skipped_files:
            skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
        
        logger.info("📋 Skipped file types:")
        for reason, count in skip_reasons.items():
            logger.info(f"   • {reason}: {count} files")

    if error_files:
        logger.warning(f"⚠️ {len(error_files)} files had extraction errors")

    return supported_files

