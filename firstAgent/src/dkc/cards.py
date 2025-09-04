"""Knowledge card generation functionality."""

from pathlib import Path
from .schema import KnowledgeCard, Citation
from .utils import generate_doc_id, extract_facts, extract_acronyms, extract_entities


def create_knowledge_card(file_path: Path, text: str, checksum: str) -> KnowledgeCard:
    """Create a knowledge card from a document."""
    source_path = str(file_path)
    doc_id = generate_doc_id(source_path, checksum)
    
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
    
    return card


def enhance_card_with_metadata(card: KnowledgeCard, file_path: Path) -> KnowledgeCard:
    """Enhance a knowledge card with additional metadata."""
    # Try to extract date from filename or content
    # This is a simple implementation - could be enhanced
    import re
    
    # Look for date patterns in filename
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{4})'
    date_match = re.search(date_pattern, file_path.name)
    
    if date_match:
        card.date = date_match.group(1)
    
    return card


def validate_card(card: KnowledgeCard) -> bool:
    """Validate a knowledge card has required fields."""
    if not card.id or not card.title or not card.source_path:
        return False
    
    if len(card.facts) > 5:
        return False
    
    return True
