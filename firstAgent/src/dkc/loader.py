"""Load PDFs and TXTs from a folder."""

import os
from pathlib import Path
from typing import Dict, List, Any
from pypdf import PdfReader


# Constants
PDF_EXT = {".pdf"}
TXT_EXT = {".txt", ".md"}


def read_pdf(path: str) -> Dict[str, Any]:
    """Read PDF file and return structured data.
    
    Args:
        path: Path to PDF file
        
    Returns:
        Dictionary with path, kind, text, pages, lines, and bytes
    """
    file_path = Path(path)
    
    # Handle missing files
    if not file_path.exists():
        return {
            "path": path,
            "kind": "pdf",
            "text": "",
            "pages": [],
            "lines": None,
            "bytes": 0
        }
    
    file_size = file_path.stat().st_size
    
    try:
        reader = PdfReader(file_path)
        pages = []
        full_text = ""
        
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                pages.append(page_text)
                full_text += page_text + "\n"
            except Exception:
                # If page extraction fails, add empty string
                pages.append("")
                full_text += "\n"
        
        return {
            "path": path,
            "kind": "pdf",
            "text": full_text.strip(),
            "pages": pages,
            "lines": None,
            "bytes": file_size
        }
    except Exception:
        # If PDF reading fails completely, return empty structure
        return {
            "path": path,
            "kind": "pdf",
            "text": "",
            "pages": [],
            "lines": None,
            "bytes": file_size
        }


def read_txt(path: str) -> Dict[str, Any]:
    """Read TXT/MD file and return structured data.
    
    Args:
        path: Path to text file
        
    Returns:
        Dictionary with path, kind, text, pages, lines, and bytes
    """
    file_path = Path(path)
    
    # Handle missing files
    if not file_path.exists():
        return {
            "path": path,
            "kind": "txt",
            "text": "",
            "pages": None,
            "lines": [],
            "bytes": 0
        }
    
    file_size = file_path.stat().st_size
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        
        return {
            "path": path,
            "kind": "txt",
            "text": content,
            "pages": None,
            "lines": lines,
            "bytes": file_size
        }
    except Exception:
        # If text reading fails, return empty structure
        return {
            "path": path,
            "kind": "txt",
            "text": "",
            "pages": None,
            "lines": [],
            "bytes": file_size
        }


def load_folder(folder: str) -> List[Dict[str, Any]]:
    """Recursively load supported files from folder.
    
    Args:
        folder: Path to folder to scan
        
    Returns:
        List of loaded document dictionaries, sorted by filename
    """
    folder_path = Path(folder)
    if not folder_path.exists() or not folder_path.is_dir():
        return []
    
    documents = []
    
    # Walk directory recursively
    for root, dirs, files in os.walk(folder_path):
        # Sort files lexicographically for deterministic order
        files.sort()
        
        for file in files:
            file_path = Path(root) / file
            file_ext = file_path.suffix.lower()
            
            # Check if file extension is supported
            if file_ext in PDF_EXT:
                doc = read_pdf(str(file_path))
                documents.append(doc)
            elif file_ext in TXT_EXT:
                doc = read_txt(str(file_path))
                documents.append(doc)
            # Silently skip unsupported files
    
    # Sort documents by path for deterministic order
    documents.sort(key=lambda x: x["path"])
    
    return documents