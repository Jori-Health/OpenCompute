"""Command-line interface for hi5 highlight picker."""

import click
from pathlib import Path
from loguru import logger

from .score import normalize_lines
from .select import pick_highlights
from .writer import write_json, write_markdown


@click.group()
def hi5():
    """hi5 - Highlight picker for text files."""
    pass


@hi5.command()
@click.option('--path', required=True, help='Path to input file (.txt or .md)')
def pick(path: str):
    """Pick top highlights from a text file."""
    input_path = Path(path)
    
    if not input_path.exists():
        logger.error(f"File not found: {path}")
        raise click.Abort()
    
    if not input_path.suffix.lower() in ['.txt', '.md']:
        logger.error(f"Unsupported file type: {input_path.suffix}")
        raise click.Abort()
    
    # Read and process file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise click.Abort()
    
    # Process content
    lines = normalize_lines(raw_content)
    highlights = pick_highlights(lines, k=5)
    
    # Write outputs to same folder as input
    input_dir = input_path.parent
    json_path = input_dir / "highlights.json"
    md_path = input_dir / "highlights.md"
    
    write_json(str(json_path), highlights)
    write_markdown(str(md_path), highlights, input_path.name)
    
    # Log summary
    total_lines = len(lines)
    candidates = len([line for line in lines if line.strip()])  # Non-empty lines
    selected = len(highlights)
    
    logger.info(f"Processed {total_lines} lines, {candidates} candidates, selected {selected} highlights -> {json_path}, {md_path}")


if __name__ == '__main__':
    hi5()
