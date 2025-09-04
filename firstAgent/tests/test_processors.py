"""Tests for document processing functionality."""

import json
import tempfile
from pathlib import Path
import pytest

from dkc.processors import (
    process_document, process_folder, calculate_checksum,
    generate_doc_id, generate_chunk_id, extract_facts,
    extract_acronyms, extract_entities
)
from dkc.schemas import KnowledgeCard, Chunk, Citation


def test_calculate_checksum():
    """Test checksum calculation."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = Path(f.name)
    
    try:
        checksum = calculate_checksum(temp_path)
        assert len(checksum) == 40  # SHA1 hex length
        assert isinstance(checksum, str)
    finally:
        temp_path.unlink()


def test_generate_doc_id():
    """Test document ID generation."""
    doc_id = generate_doc_id("/path/to/file.txt", "abc123")
    assert len(doc_id) == 40  # SHA1 hex length
    assert isinstance(doc_id, str)
    
    # Test determinism
    doc_id2 = generate_doc_id("/path/to/file.txt", "abc123")
    assert doc_id == doc_id2


def test_generate_chunk_id():
    """Test chunk ID generation."""
    chunk_id = generate_chunk_id("doc123", 0)
    assert len(chunk_id) == 40  # SHA1 hex length
    assert isinstance(chunk_id, str)
    
    # Test determinism
    chunk_id2 = generate_chunk_id("doc123", 0)
    assert chunk_id == chunk_id2


def test_extract_facts():
    """Test fact extraction."""
    text = "This is a fact. Another fact here. Short. This is a longer fact that should be included."
    facts = extract_facts(text, max_facts=3)
    
    assert len(facts) <= 3
    assert all(len(fact) > 20 for fact in facts)  # Should filter out short sentences
    assert "This is a fact" in facts[0]


def test_extract_acronyms():
    """Test acronym extraction."""
    text = "The API uses CPU and GPU resources. The ML model processes NLP data."
    acronyms = extract_acronyms(text)
    
    assert "API" in acronyms
    assert "CPU" in acronyms
    assert "GPU" in acronyms
    assert "ML" in acronyms
    assert "NLP" in acronyms


def test_extract_entities():
    """Test entity extraction."""
    text = "John Smith works at Google. The Python programming language is popular."
    entities = extract_entities(text)
    
    assert "John Smith" in entities
    assert "Google" in entities
    assert "Python" in entities


def test_process_txt_document():
    """Test processing a TXT document."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("""Machine Learning Overview

Machine Learning (ML) is a subset of AI. It uses algorithms to learn patterns.
Popular algorithms include Neural Networks and SVM.
Applications span healthcare, finance, and transportation.""")
        temp_path = Path(f.name)
    
    try:
        card, chunks, checksum = process_document(temp_path)
        
        # Test knowledge card
        assert isinstance(card, KnowledgeCard)
        assert card.title == temp_path.stem
        assert card.source_path == str(temp_path)
        assert len(card.facts) <= 5
        assert "ML" in card.acronyms
        assert "AI" in card.acronyms
        assert len(card.citations) == 1
        
        # Test chunks
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.doc_id == card.id for chunk in chunks)
        assert all(chunk.source_path == str(temp_path) for chunk in chunks)
        
        # Test checksum
        assert len(checksum) == 40
        
    finally:
        temp_path.unlink()


def test_process_folder():
    """Test processing a folder of documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample files
        sample1 = temp_path / "sample1.txt"
        sample1.write_text("""Python Programming

Python is a high-level language. It follows PEP 8 style guidelines.
Use pytest for testing. Write comprehensive docstrings.""")

        sample2 = temp_path / "sample2.txt"
        sample2.write_text("""Machine Learning Basics

ML algorithms learn from data. Popular methods include Neural Networks.
Applications include NLP and computer vision.""")

        # Create output directory
        output_dir = temp_path / "output"
        
        # Process folder
        process_folder(temp_path, output_dir)
        
        # Check output files exist
        assert (output_dir / "cards.jsonl").exists()
        assert (output_dir / "chunks.jsonl").exists()
        assert (output_dir / "manifest.json").exists()
        
        # Check cards.jsonl
        with open(output_dir / "cards.jsonl", 'r') as f:
            cards_data = [json.loads(line) for line in f]
        
        assert len(cards_data) == 2
        assert all("id" in card for card in cards_data)
        assert all("title" in card for card in cards_data)
        assert all("facts" in card for card in cards_data)
        
        # Check chunks.jsonl
        with open(output_dir / "chunks.jsonl", 'r') as f:
            chunks_data = [json.loads(line) for line in f]
        
        assert len(chunks_data) > 0
        assert all("id" in chunk for chunk in chunks_data)
        assert all("doc_id" in chunk for chunk in chunks_data)
        assert all("text" in chunk for chunk in chunks_data)
        
        # Check manifest.json
        with open(output_dir / "manifest.json", 'r') as f:
            manifest_data = json.load(f)
        
        assert manifest_data["total_documents"] == 2
        assert manifest_data["total_cards"] == 2
        assert manifest_data["total_chunks"] == len(chunks_data)
        assert "created_at" in manifest_data
        assert "checksums" in manifest_data


def test_deterministic_processing():
    """Test that processing is deterministic."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test document for deterministic processing.")
        temp_path = Path(f.name)
    
    try:
        # Process twice
        card1, chunks1, checksum1 = process_document(temp_path)
        card2, chunks2, checksum2 = process_document(temp_path)
        
        # Results should be identical
        assert card1.id == card2.id
        assert checksum1 == checksum2
        assert len(chunks1) == len(chunks2)
        
        # Chunk IDs should be identical
        chunk_ids1 = [chunk.id for chunk in chunks1]
        chunk_ids2 = [chunk.id for chunk in chunks2]
        assert chunk_ids1 == chunk_ids2
        
    finally:
        temp_path.unlink()
