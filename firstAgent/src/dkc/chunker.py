"""Produce overlapping word-window chunks with stable IDs."""

from typing import List
from .schema import Chunk
from .utils import sha1


def chunk_doc(doc: dict, doc_id: str, size: int = 800, overlap: int = 120) -> List[Chunk]:
    """Create overlapping word-window chunks from a document.
    
    Args:
        doc: Document dictionary with 'text' and 'path' keys
        doc_id: Document ID for generating chunk IDs
        size: Target chunk size in words (default: 800)
        overlap: Number of overlapping words between chunks (default: 120)
        
    Returns:
        List of Chunk objects with stable IDs
    """
    text = doc.get('text', '')
    source_path = doc.get('path', '')
    
    # Split text into words on whitespace
    words = text.split()
    
    # Handle empty or very short documents
    if len(words) == 0:
        return []
    
    if len(words) <= size:
        # Single chunk for short documents
        chunk_id = sha1(f"{doc_id}:1")
        chunk_text = ' '.join(words)
        
        return [Chunk(
            id=chunk_id,
            doc_id=doc_id,
            ordinal=1,
            text=chunk_text,
            source_path=source_path
        )]
    
    # Create overlapping chunks for longer documents
    chunks = []
    ordinal = 1
    start = 0
    
    while start < len(words):
        # Calculate end position for this chunk
        end = min(start + size, len(words))
        
        # Extract words for this chunk
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        
        # Generate stable chunk ID
        chunk_id = sha1(f"{doc_id}:{ordinal}")
        
        # Create chunk
        chunk = Chunk(
            id=chunk_id,
            doc_id=doc_id,
            ordinal=ordinal,
            text=chunk_text,
            source_path=source_path
        )
        chunks.append(chunk)
        
        # Move to next chunk with overlap
        if end >= len(words):
            break
        
        # Calculate next start position with overlap
        start = end - overlap
        ordinal += 1
    
    return chunks