"""Content hashing utilities for artifact comparison."""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_content(content: str) -> str:
    """Compute a SHA-256 hash of text content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def hash_bytes(data: bytes) -> str:
    """Compute a SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    """Hash a single file, using text mode for UTF-8 files and bytes for binary."""
    try:
        content = path.read_text(encoding="utf-8")
        return hash_content(content)
    except UnicodeDecodeError:
        return hash_bytes(path.read_bytes())


def hash_directory(dir_path: Path) -> str:
    """Compute a deterministic hash of all files in a directory.

    Files are sorted by relative path to ensure consistent ordering.
    The hash is computed over the concatenation of each file's
    relative path and its content hash.
    """
    file_hashes: list[str] = []
    for f in sorted(dir_path.rglob("*")):
        if f.is_file():
            rel = f.relative_to(dir_path)
            file_hashes.append(f"{rel}:{hash_file(f)}")

    combined = "\n".join(file_hashes)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
