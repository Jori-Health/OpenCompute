"""Smoke test using click.testing.CliRunner."""

import tempfile
import json
from pathlib import Path
from click.testing import CliRunner

from dkc.cli import dkc


def test_smoke_build():
    """Smoke test: create temp folder with two small TXT docs, invoke dkc build, assert output files exist and are non-empty."""
    
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create input folder with two small TXT documents
        input_folder = temp_path / "input"
        input_folder.mkdir()
        
        # Create first TXT document
        doc1_path = input_folder / "doc1.txt"
        doc1_path.write_text("""Machine Learning Basics

Machine Learning (ML) is a subset of artificial intelligence.
It uses algorithms to learn patterns from data.
Popular algorithms include Neural Networks and SVM.
Applications span healthcare, finance, and transportation.""")

        # Create second TXT document
        doc2_path = input_folder / "doc2.txt"
        doc2_path.write_text("""Python Programming

Python is a high-level programming language.
It follows PEP 8 style guidelines.
Use pytest for testing and write comprehensive docstrings.
Leverage built-in functions and libraries for performance.""")

        # Create output folder
        output_folder = temp_path / "output"
        
        # Invoke dkc build command
        result = runner.invoke(dkc, [
            'build',
            '--in', str(input_folder),
            '--out', str(output_folder)
        ])
        
        # Assert command succeeded
        assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}: {result.output}"
        
        # Assert output files exist
        cards_file = output_folder / "cards.jsonl"
        chunks_file = output_folder / "chunks.jsonl"
        manifest_file = output_folder / "manifest.json"
        
        assert cards_file.exists(), "cards.jsonl file does not exist"
        assert chunks_file.exists(), "chunks.jsonl file does not exist"
        assert manifest_file.exists(), "manifest.json file does not exist"
        
        # Assert files are non-empty
        assert cards_file.stat().st_size > 0, "cards.jsonl file is empty"
        assert chunks_file.stat().st_size > 0, "chunks.jsonl file is empty"
        assert manifest_file.stat().st_size > 0, "manifest.json file is empty"
        
        # Verify cards.jsonl contains valid JSON objects
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = [json.loads(line.strip()) for line in f if line.strip()]
        
        assert len(cards) > 0, "cards.jsonl contains no cards"
        assert len(cards) == 2, f"Expected 2 cards, got {len(cards)}"
        
        # Verify each card has required fields
        for card in cards:
            assert 'id' in card, "Card missing 'id' field"
            assert 'title' in card, "Card missing 'title' field"
            assert 'source_path' in card, "Card missing 'source_path' field"
            assert 'facts' in card, "Card missing 'facts' field"
            assert 'acronyms' in card, "Card missing 'acronyms' field"
            assert 'entities' in card, "Card missing 'entities' field"
            assert 'citations' in card, "Card missing 'citations' field"
        
        # Verify chunks.jsonl contains valid JSON objects
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = [json.loads(line.strip()) for line in f if line.strip()]
        
        assert len(chunks) > 0, "chunks.jsonl contains no chunks"
        
        # Verify each chunk has required fields
        for chunk in chunks:
            assert 'id' in chunk, "Chunk missing 'id' field"
            assert 'doc_id' in chunk, "Chunk missing 'doc_id' field"
            assert 'ordinal' in chunk, "Chunk missing 'ordinal' field"
            assert 'text' in chunk, "Chunk missing 'text' field"
            assert 'source_path' in chunk, "Chunk missing 'source_path' field"
        
        # Verify manifest.json contains expected structure
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        assert 'total_documents' in manifest, "Manifest missing 'total_documents' field"
        assert 'total_cards' in manifest, "Manifest missing 'total_cards' field"
        assert 'total_chunks' in manifest, "Manifest missing 'total_chunks' field"
        assert 'skipped_files' in manifest, "Manifest missing 'skipped_files' field"
        
        assert manifest['total_documents'] == 2, f"Expected 2 documents, got {manifest['total_documents']}"
        assert manifest['total_cards'] == 2, f"Expected 2 cards, got {manifest['total_cards']}"
        assert manifest['total_chunks'] == len(chunks), f"Chunk count mismatch in manifest"
        
        print(f"✅ Smoke test passed: {len(cards)} cards, {len(chunks)} chunks generated successfully")
