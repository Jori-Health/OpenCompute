"""Emit artifacts - write cards, chunks, and manifest."""

from typing import List
from .schema import KnowledgeCard, Chunk
from .utils import write_jsonl


def write_cards(path: str, cards: List[KnowledgeCard]) -> None:
    """Write knowledge cards to JSONL file.
    
    Args:
        path: Output file path
        cards: List of KnowledgeCard objects to write
    """
    # Convert cards to dictionaries for JSONL writing
    card_dicts = [card.model_dump() for card in cards]
    write_jsonl(path, card_dicts)


def write_chunks(path: str, chunks: List[Chunk]) -> None:
    """Write chunks to JSONL file.
    
    Args:
        path: Output file path
        chunks: List of Chunk objects to write
    """
    # Convert chunks to dictionaries for JSONL writing
    chunk_dicts = [chunk.model_dump() for chunk in chunks]
    write_jsonl(path, chunk_dicts)


def write_manifest(path: str, docs: List[dict], cards: List[KnowledgeCard], 
                  chunks: List[Chunk], skipped: List[str]) -> None:
    """Write manifest to JSON file.
    
    Args:
        path: Output file path
        docs: List of document dictionaries
        cards: List of KnowledgeCard objects
        chunks: List of Chunk objects
        skipped: List of skipped file paths
    """
    manifest = {
        "total_documents": len(docs),
        "total_cards": len(cards),
        "total_chunks": len(chunks),
        "skipped_files": skipped
    }
    
    # Write as single JSON object (not JSONL)
    import json
    from pathlib import Path
    
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')