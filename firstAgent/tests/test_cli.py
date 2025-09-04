"""Tests for CLI functionality."""

import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

from dkc.cli import main


def test_cli_build_command():
    """Test the build CLI command."""
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample files
        input_dir = temp_path / "input"
        input_dir.mkdir()
        
        sample_file = input_dir / "test.txt"
        sample_file.write_text("""Test Document

This is a test document for CLI testing.
It contains some facts about testing.
The CLI should process this correctly.""")

        output_dir = temp_path / "output"
        
        # Run build command
        result = runner.invoke(main, ['build', '--in', str(input_dir), '--out', str(output_dir)])
        
        assert result.exit_code == 0
        assert (output_dir / "cards.jsonl").exists()
        assert (output_dir / "chunks.jsonl").exists()
        assert (output_dir / "manifest.json").exists()


def test_cli_inspect_command():
    """Test the inspect CLI command."""
    runner = CliRunner()
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("""Inspection Test Document

This document is for testing the inspect command.
It should show facts, acronyms, and entities.
The CLI should display structured information.""")
        temp_path = Path(f.name)
    
    try:
        result = runner.invoke(main, ['inspect', '--file', str(temp_path)])
        
        assert result.exit_code == 0
        assert "Document:" in result.output
        assert "Checksum:" in result.output
        assert "Document ID:" in result.output
        assert "Title:" in result.output
        assert "Facts:" in result.output
        assert "Chunks:" in result.output
        
    finally:
        temp_path.unlink()


def test_cli_help():
    """Test CLI help output."""
    runner = CliRunner()
    
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert "Document Knowledge Converter" in result.output
    
    result = runner.invoke(main, ['build', '--help'])
    assert result.exit_code == 0
    assert "Build knowledge cards" in result.output
    
    result = runner.invoke(main, ['inspect', '--help'])
    assert result.exit_code == 0
    assert "Inspect a single document" in result.output


def test_cli_verbose_flag():
    """Test verbose logging flag."""
    runner = CliRunner()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample file
        input_dir = temp_path / "input"
        input_dir.mkdir()
        
        sample_file = input_dir / "test.txt"
        sample_file.write_text("Test document for verbose logging.")
        
        output_dir = temp_path / "output"
        
        # Run with verbose flag
        result = runner.invoke(main, ['-v', 'build', '--in', str(input_dir), '--out', str(output_dir)])
        
        assert result.exit_code == 0
        # Verbose output should contain more detailed logging
        assert "Starting build process" in result.output or "Processed" in result.output
