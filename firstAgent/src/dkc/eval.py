"""Tiny evaluator for completeness."""

import json
from pathlib import Path
from typing import Dict


def eval_cards(cards_path: str) -> Dict[str, float]:
    """Evaluate knowledge cards for completeness and citation coverage.
    
    Args:
        cards_path: Path to cards.jsonl file
        
    Returns:
        Dictionary with completeness and citation_coverage scores
    """
    cards_file = Path(cards_path)
    
    # Handle empty or missing files
    if not cards_file.exists() or cards_file.stat().st_size == 0:
        return {
            "completeness": 0.0,
            "citation_coverage": 0.0
        }
    
    try:
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = [json.loads(line.strip()) for line in f if line.strip()]
    except (json.JSONDecodeError, FileNotFoundError):
        return {
            "completeness": 0.0,
            "citation_coverage": 0.0
        }
    
    if not cards:
        return {
            "completeness": 0.0,
            "citation_coverage": 0.0
        }
    
    # Calculate completeness score
    total_fields = 0
    filled_fields = 0
    
    for card in cards:
        # Check required fields
        required_fields = ['id', 'title', 'source_path']
        for field in required_fields:
            total_fields += 1
            if card.get(field) and str(card[field]).strip():
                filled_fields += 1
        
        # Check optional but important fields
        optional_fields = ['facts', 'acronyms', 'entities', 'citations']
        for field in optional_fields:
            total_fields += 1
            if card.get(field) and len(card[field]) > 0:
                filled_fields += 1
    
    completeness = filled_fields / total_fields if total_fields > 0 else 0.0
    
    # Calculate citation coverage
    total_cards = len(cards)
    cards_with_citations = 0
    
    for card in cards:
        citations = card.get('citations', [])
        if citations and len(citations) > 0:
            cards_with_citations += 1
    
    citation_coverage = cards_with_citations / total_cards if total_cards > 0 else 0.0
    
    return {
        "completeness": completeness,
        "citation_coverage": citation_coverage
    }