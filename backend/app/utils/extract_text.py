import json
import os
from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json"}

def is_supported_format(filename: str) -> bool:
    """Check if the file format is supported."""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS

def extract_text_from_bytes(content: bytes, filename: str) -> str:
    """Extract readable text from bytes based on file extension."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: '{ext}'. Supported formats are: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

    try:
        raw_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = content.decode("latin-1")

    if ext == ".json":
        try:
            parsed = json.loads(raw_text)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError as err:
            raise ValueError(f"Invalid JSON content: {err}")

    return raw_text

def extract_text_from_file(file_path: str, filename: str = None) -> str:
    """Extract readable text from a file on disk."""
    fname = filename or os.path.basename(file_path)
    with open(file_path, "rb") as f:
        content = f.read()
    return extract_text_from_bytes(content, fname)
