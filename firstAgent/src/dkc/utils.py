"""Small helper functions for document processing."""

import hashlib
import json
from pathlib import Path
from typing import Iterable, Dict, Any


def sha1(s: str) -> str:
    """Generate SHA1 hex digest of UTF-8 encoded string.
    
    Args:
        s: Input string to hash
        
    Returns:
        SHA1 hex digest as string
    """
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def canon(path: str) -> str:
    """Normalize path for use in IDs.
    
    Converts path to absolute, normalized form for consistent ID generation.
    
    Args:
        path: Input path string
        
    Returns:
        Normalized absolute path string
    """
    return str(Path(path).resolve())


def write_jsonl(path: str, items: Iterable[Dict[str, Any]]) -> None:
    """Write items to JSONL file.
    
    Creates parent directory if needed, writes one JSON object per line
    with trailing newline. Uses UTF-8 encoding.
    
    Args:
        path: Output file path
        items: Iterable of dictionaries to write
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(json.dumps(item) + '\n')