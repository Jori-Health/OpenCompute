"""Output writers for JSON and Markdown formats."""

import json
from typing import List, Dict
from pathlib import Path


def write_json(path: str, highlights: List[Dict]) -> None:
    """Write highlights to JSON file.
    
    Args:
        path: Output file path
        highlights: List of highlight dictionaries
    """
    # Ensure parent directories exist
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(highlights, f, indent=2, ensure_ascii=False)


def write_markdown(path: str, highlights: List[Dict], source: str) -> None:
    """Write highlights to Markdown checklist format.
    
    Args:
        path: Output file path
        highlights: List of highlight dictionaries
        source: Source file name for reference
    """
    # Ensure parent directories exist
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write("# Highlights\n")
        
        for highlight in highlights:
            rank = highlight['rank']
            line_ref = f"L{highlight['line_no']}"
            text = highlight['text']
            reason = highlight['reason']
            
            f.write(f"- [ ] ({rank}) {line_ref}: {text}\n")
            f.write(f"      reason: {reason}\n\n")
