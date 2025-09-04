"""Document processing logic for PDFs and TXT files."""

import hashlib
import os
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from loguru import logger
from pypdf import PdfReader

from .schemas import KnowledgeCard, Chunk, Citation, Manifest


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA1 checksum of a file."""
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha1_hash.update(chunk)
    return sha1_hash.hexdigest()


def generate_doc_id(source_path: str, checksum: str) -> str:
    """Generate deterministic document ID from path and checksum."""
    canonical_string = f"{source_path}:{checksum}"
    return hashlib.sha1(canonical_string.encode()).hexdigest()


def generate_chunk_id(doc_id: str, ordinal: int) -> str:
    """Generate deterministic chunk ID from document ID and ordinal."""
    canonical_string = f"{doc_id}:{ordinal}"
    return hashlib.sha1(canonical_string.encode()).hexdigest()


def read_txt_file(file_path: Path) -> Tuple[str, List[str]]:
    """Read TXT file and return content with line-by-line breakdown."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.splitlines()
        return content, lines
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
        lines = content.splitlines()
        return content, lines


def read_pdf_file(file_path: Path) -> Tuple[str, List[str]]:
    """Read PDF file and return content with page-by-page breakdown."""
    try:
        reader = PdfReader(file_path)
        pages = []
        full_text = ""
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            pages.append(page_text)
            full_text += page_text + "\n"
        
        return full_text.strip(), pages
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        raise


def extract_facts(text: str, max_facts: int = 5) -> List[str]:
    """Extract key facts from text (simple implementation)."""
    # Simple fact extraction - split by sentences and take first few
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    facts = []
    
    for sentence in sentences[:max_facts]:
        if len(sentence) > 20:  # Filter out very short sentences
            facts.append(sentence)
    
    return facts


def extract_acronyms(text: str) -> List[str]:
    """Extract acronyms from text (simple implementation)."""
    import re
    # Look for patterns like "API", "CPU", "GPU", etc.
    acronym_pattern = r'\b[A-Z]{2,}\b'
    acronyms = re.findall(acronym_pattern, text)
    return list(set(acronyms))  # Remove duplicates


def extract_entities(text: str) -> List[str]:
    """Extract named entities from text (simple implementation)."""
    import re
    # Simple entity extraction - capitalized words/phrases
    entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    entities = re.findall(entity_pattern, text)
    return list(set(entities))  # Remove duplicates


def create_chunks(text: str, doc_id: str, source_path: str, 
                 pages: Optional[List[str]] = None) -> List[Chunk]:
    """Create stable chunks from text."""
    chunks = []
    
    # Simple chunking by paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    for i, paragraph in enumerate(paragraphs):
        if len(paragraph) < 50:  # Skip very short paragraphs
            continue
            
        chunk_id = generate_chunk_id(doc_id, i)
        
        # Determine page number if available
        page_num = None
        if pages:
            # Find which page this chunk likely belongs to
            for page_idx, page_text in enumerate(pages):
                if paragraph in page_text:
                    page_num = page_idx + 1
                    break
        
        chunk = Chunk(
            id=chunk_id,
            doc_id=doc_id,
            ordinal=i,
            text=paragraph,
            source_path=source_path,
            page=page_num
        )
        chunks.append(chunk)
    
    return chunks


def process_document(file_path: Path) -> Tuple[KnowledgeCard, List[Chunk], str]:
    """Process a single document and return knowledge card and chunks."""
    source_path = str(file_path)
    checksum = calculate_checksum(file_path)
    doc_id = generate_doc_id(source_path, checksum)
    
    # Read document based on file type
    if file_path.suffix.lower() == '.pdf':
        text, pages = read_pdf_file(file_path)
    elif file_path.suffix.lower() == '.txt':
        text, lines = read_txt_file(file_path)
        pages = None
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    
    # Extract information
    facts = extract_facts(text)
    acronyms = extract_acronyms(text)
    entities = extract_entities(text)
    
    # Create knowledge card
    card = KnowledgeCard(
        id=doc_id,
        title=file_path.stem,
        source_path=source_path,
        facts=facts,
        acronyms=acronyms,
        entities=entities,
        citations=[Citation(
            doc_id=doc_id,
            source_path=source_path,
            text_excerpt=text[:200] + "..." if len(text) > 200 else text
        )]
    )
    
    # Create chunks
    chunks = create_chunks(text, doc_id, source_path, pages)
    
    return card, chunks, checksum


def process_folder(input_folder: Path, output_folder: Path) -> None:
    """Process all documents in a folder and create output files."""
    # Ensure output folder exists
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Get all supported files, sorted lexicographically
    supported_extensions = {'.pdf', '.txt'}
    files = []
    for ext in supported_extensions:
        files.extend(input_folder.glob(f"*{ext}"))
    files.sort()  # Lexicographic sort for determinism
    
    cards = []
    all_chunks = []
    checksums = {}
    skipped_files = []
    
    logger.info(f"Processing {len(files)} files from {input_folder}")
    
    for file_path in files:
        try:
            card, chunks, checksum = process_document(file_path)
            cards.append(card)
            all_chunks.extend(chunks)
            checksums[str(file_path)] = checksum
            
            logger.info(f"Processed {file_path.name}: {len(chunks)} chunks, card created")
            
        except Exception as e:
            logger.warning(f"Skipped {file_path.name}: {e}")
            skipped_files.append(str(file_path))
    
    # Write output files
    write_cards_jsonl(cards, output_folder / "cards.jsonl")
    write_chunks_jsonl(all_chunks, output_folder / "chunks.jsonl")
    write_manifest(cards, all_chunks, skipped_files, checksums, output_folder / "manifest.json")
    
    logger.info(f"Completed processing: {len(cards)} cards, {len(all_chunks)} chunks")


def write_cards_jsonl(cards: List[KnowledgeCard], output_path: Path) -> None:
    """Write knowledge cards to JSONL file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for card in cards:
            f.write(card.model_dump_json() + '\n')


def write_chunks_jsonl(chunks: List[Chunk], output_path: Path) -> None:
    """Write chunks to JSONL file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(chunk.model_dump_json() + '\n')


def write_manifest(cards: List[KnowledgeCard], chunks: List[Chunk], 
                  skipped_files: List[str], checksums: dict, output_path: Path) -> None:
    """Write manifest to JSON file."""
    manifest = Manifest(
        total_documents=len(cards),
        total_cards=len(cards),
        total_chunks=len(chunks),
        skipped_files=skipped_files,
        checksums=checksums,
        created_at=datetime.now().isoformat()
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(manifest.model_dump_json(indent=2) + '\n')
