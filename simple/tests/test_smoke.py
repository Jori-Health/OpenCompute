"""Smoke tests for hi5 highlight picker."""

import pytest
from pathlib import Path
import json
import tempfile
from click.testing import CliRunner

from src.hi5.score import normalize_lines, score_line, is_all_caps
from src.hi5.select import pick_highlights
from src.hi5.writer import write_json, write_markdown
from src.hi5.cli import hi5


def test_normalize_lines():
    """Test line normalization."""
    raw = "Line 1\nLine 2  \n\nLine 3"
    lines = normalize_lines(raw)
    assert lines == ["Line 1", "Line 2", "", "Line 3"]


def test_is_all_caps():
    """Test all caps detection."""
    assert is_all_caps("HELLO WORLD") == True
    assert is_all_caps("Hello World") == False
    assert is_all_caps("AB") == False  # Too short
    assert is_all_caps("123 HELLO") == True
    assert is_all_caps("") == False


def test_score_line():
    """Test line scoring."""
    # Test period scoring
    score, reasons = score_line("This ends with a period.")
    assert score >= 1
    assert "period" in reasons
    
    # Test keyword scoring
    score, reasons = score_line("This is a summary of findings.")
    assert score >= 1
    assert any("keyword=" in reason for reason in reasons)
    
    # Test bullet scoring
    score, reasons = score_line("- This is a bullet point")
    assert score >= 1
    assert "bullet" in reasons
    
    # Test length scoring
    long_line = "This is a reasonably long line that should score well for length criteria."
    score, reasons = score_line(long_line)
    assert score >= 1
    assert any("len=" in reason for reason in reasons)
    
    # Test all caps penalty
    score, reasons = score_line("THIS IS ALL CAPS")
    assert "all_caps" in reasons
    
    # Test empty line
    score, reasons = score_line("")
    assert score == 0
    assert reasons == []


def test_pick_highlights():
    """Test highlight selection."""
    lines = [
        "Short line",
        "This is a longer line that ends with a period.",
        "- This is a bullet point",
        "This line contains the word summary.",
        "ANOTHER ALL CAPS LINE",
        "This line has good length and ends properly."
    ]
    
    highlights = pick_highlights(lines, k=3)
    
    assert len(highlights) <= 3
    assert all(h['rank'] == i + 1 for i, h in enumerate(highlights))
    assert all(h['line_no'] >= 1 for h in highlights)
    assert all('reason' in h for h in highlights)


def test_determinism():
    """Test that same input produces same output."""
    lines = [
        "This is a test line with good length.",
        "- Bullet point with keyword summary",
        "Another line ending with period."
    ]
    
    # Run multiple times
    results = []
    for _ in range(3):
        highlights = pick_highlights(lines, k=2)
        results.append(highlights)
    
    # All results should be identical
    assert all(result == results[0] for result in results)


def test_writer_functions():
    """Test output writing functions."""
    highlights = [
        {
            'rank': 1,
            'line_no': 2,
            'text': 'Test line',
            'reason': 'period; len=9'
        }
    ]
    
    # Test JSON writing
    write_json('test_highlights.json', highlights)
    assert Path('test_highlights.json').exists()
    
    # Verify JSON content
    with open('test_highlights.json', 'r') as f:
        data = json.load(f)
    assert data == highlights
    
    # Test Markdown writing
    write_markdown('test_highlights.md', highlights, 'test.txt')
    assert Path('test_highlights.md').exists()
    
    # Clean up test files
    Path('test_highlights.json').unlink()
    Path('test_highlights.md').unlink()


def test_sample_file():
    """Test with the sample data file."""
    sample_path = Path(__file__).parent.parent / "data" / "sample_notes.txt"
    
    if sample_path.exists():
        with open(sample_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        lines = normalize_lines(raw_content)
        highlights = pick_highlights(lines, k=5)
        
        # Should find some highlights
        assert len(highlights) > 0
        assert all(h['rank'] == i + 1 for i, h in enumerate(highlights))
        assert all(h['line_no'] >= 1 for h in highlights)


def test_cli_runner():
    """Test CLI using CliRunner."""
    runner = CliRunner()
    
    # Create a temporary file with test content
    test_content = """# Test Document

## Summary
This is a test document for CLI testing.

## Key Findings
- This bullet point should score well.
- Another bullet with good length and period.

## Results
Our testing shows that the scoring system works effectively.

## TODO Items
- Add more test cases
- Improve error handling

This line is quite long and should score well due to its length being within the optimal range for readability.

SHORT LINE

This is another good candidate because it ends with a period and has a reasonable length.

• This bullet point uses a different bullet character and should also score well.

FINAL THOUGHTS - THIS LINE IS ALL CAPS AND SHOULD BE PENALIZED

The final result shows that our implementation works as expected.
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Run the CLI command
        result = runner.invoke(hi5, ['pick', '--path', temp_file])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Check that output files exist
        temp_dir = Path(temp_file).parent
        json_path = temp_dir / "highlights.json"
        md_path = temp_dir / "highlights.md"
        
        assert json_path.exists()
        assert md_path.exists()
        
        # Check JSON content
        with open(json_path, 'r', encoding='utf-8') as f:
            highlights = json.load(f)
        
        assert len(highlights) <= 5
        assert all(h['rank'] == i + 1 for i, h in enumerate(highlights))
        assert all(h['line_no'] >= 1 for h in highlights)
        assert all('reason' in h for h in highlights)
        
        # Test determinism - run twice and compare
        result2 = runner.invoke(hi5, ['pick', '--path', temp_file])
        assert result2.exit_code == 0
        
        with open(json_path, 'r', encoding='utf-8') as f:
            highlights2 = json.load(f)
        
        # JSON content should be identical
        assert highlights == highlights2
        
    finally:
        # Clean up
        Path(temp_file).unlink(missing_ok=True)
        Path(json_path).unlink(missing_ok=True)
        Path(md_path).unlink(missing_ok=True)
