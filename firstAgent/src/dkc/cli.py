"""Click-based CLI for Document Knowledge Converter."""

import json
from pathlib import Path
from typing import List

import click
from loguru import logger

from .loader import load_folder, read_pdf, read_txt
from .chunker import chunk_doc
from .writer import write_cards, write_chunks, write_manifest
from .schema import KnowledgeCard, Chunk, Citation
from .utils import sha1, canon


def build_knowledge_card(doc: dict) -> KnowledgeCard:
    """Build a knowledge card from a document."""
    doc_id = sha1(f"{canon(doc['path'])}:{doc['bytes']}")
    
    # Extract basic information
    text = doc.get('text', '')
    title = Path(doc['path']).stem
    
    # Simple fact extraction (first few sentences)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    facts = [s for s in sentences[:5] if len(s) > 20]
    
    # Simple acronym extraction
    import re
    acronyms = list(set(re.findall(r'\b[A-Z]{2,}\b', text)))
    
    # Simple entity extraction (capitalized words)
    entities = list(set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)))
    
    # Create citation
    citation = Citation(
        doc_id=doc_id,
        source_path=doc['path'],
        text_excerpt=text[:200] + "..." if len(text) > 200 else text
    )
    
    return KnowledgeCard(
        id=doc_id,
        title=title,
        source_path=doc['path'],
        facts=facts,
        acronyms=acronyms,
        entities=entities,
        citations=[citation]
    )


@click.group()
def dkc():
    """Document Knowledge Converter - converts PDFs/TXTs to knowledge cards and chunks."""
    pass


@dkc.command()
@click.option('--in', 'input_folder', required=True, type=click.Path(exists=True, file_okay=False, path_type=Path),
              help='Input folder containing PDF/TXT files')
@click.option('--out', 'output_folder', required=True, type=click.Path(path_type=Path),
              help='Output folder for generated files')
@click.option('--chunk', default=800, type=int, help='Chunk size in words (default: 800)')
@click.option('--overlap', default=120, type=int, help='Overlap size in words (default: 120)')
def build(input_folder: Path, output_folder: Path, chunk: int, overlap: int):
    """Load docs, build cards, chunk docs, write output files."""
    try:
        # Load documents
        docs = load_folder(str(input_folder))
        
        cards = []
        all_chunks = []
        skipped_files = []
        
        # Process each document
        for doc in docs:
            try:
                # Build knowledge card
                card = build_knowledge_card(doc)
                cards.append(card)
                
                # Create chunks
                doc_id = card.id
                chunks = chunk_doc(doc, doc_id, chunk, overlap)
                all_chunks.extend(chunks)
                
                # Log one line per doc
                logger.info(f"{doc['path']} {doc['bytes']} bytes card_ok {len(chunks)} chunks")
                
            except Exception as e:
                logger.warning(f"Skipped {doc['path']}: {e}")
                skipped_files.append(doc['path'])
        
        # Write output files
        write_cards(str(output_folder / "cards.jsonl"), cards)
        write_chunks(str(output_folder / "chunks.jsonl"), all_chunks)
        write_manifest(str(output_folder / "manifest.json"), docs, cards, all_chunks, skipped_files)
        
        logger.info(f"Build completed: {len(cards)} cards, {len(all_chunks)} chunks")
        
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise click.ClickException(f"Build failed: {e}")


@dkc.command()
@click.option('--file', 'file_path', required=True, type=click.Path(exists=True, path_type=Path),
              help='File to inspect')
def inspect(file_path: Path):
    """Load a single file, build one card, pretty-print JSON to stdout."""
    try:
        # Load single file
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.pdf':
            doc = read_pdf(str(file_path))
        elif file_ext in ['.txt', '.md']:
            doc = read_txt(str(file_path))
        else:
            raise click.ClickException(f"Unsupported file type: {file_ext}")
        
        # Build knowledge card
        card = build_knowledge_card(doc)
        
        # Pretty-print JSON to stdout
        print(json.dumps(card.model_dump(), indent=2))
        
    except Exception as e:
        logger.error(f"Inspection failed: {e}")
        raise click.ClickException(f"Inspection failed: {e}")


if __name__ == '__main__':
    dkc()