"""Pure scoring functions for line analysis."""

import re
from typing import List, Tuple


# Scoring constants from rubric
KEYWORDS = {"summary", "key", "result", "finding", "todo"}
MIN_LENGTH = 40
MAX_LENGTH = 160
MIN_CAPS_LENGTH = 3


def normalize_lines(raw: str) -> List[str]:
    """Split text into lines and normalize whitespace.
    
    Args:
        raw: Raw text content
        
    Returns:
        List of lines with trailing spaces stripped, preserving empty lines
        for stable line numbering
    """
    lines = raw.splitlines()
    return [line.rstrip() for line in lines]


def is_all_caps(line: str) -> bool:
    """Check if line is all caps (letters only, minimum 3 letters).
    
    Args:
        line: Line to check
        
    Returns:
        True if letters-only portion is uppercase and has ≥3 letters
    """
    # Extract only letters
    letters = re.sub(r'[^a-zA-Z]', '', line)
    
    # Must have at least 3 letters and be all uppercase
    return len(letters) >= MIN_CAPS_LENGTH and letters.isupper()


def score_line(line: str) -> Tuple[int, List[str]]:
    """Score a line according to the rubric.
    
    Scoring rules:
    +1 if line ends with period '.'
    +1 if contains any keyword (case-insensitive): {summary, key, result, finding, todo}
    +1 if starts with bullet (`- ` or `• `)
    +1 if 40 ≤ len(line) ≤ 160
    -1 if line is ALL CAPS (letters only)
    
    Args:
        line: Line to score
        
    Returns:
        Tuple of (score, list_of_reasons)
    """
    score = 0
    reasons = []
    
    # Skip empty/whitespace-only lines
    if not line.strip():
        return 0, []
    
    # +1 if line ends with period
    if line.endswith('.'):
        score += 1
        reasons.append("period")
    
    # +1 if contains keyword (case-insensitive)
    line_lower = line.lower()
    for keyword in KEYWORDS:
        if keyword in line_lower:
            score += 1
            reasons.append(f"keyword={keyword}")
            break  # Only count once per line
    
    # +1 if starts with bullet
    if line.startswith('- ') or line.startswith('• '):
        score += 1
        reasons.append("bullet")
    
    # +1 if length is in range
    line_len = len(line)
    if MIN_LENGTH <= line_len <= MAX_LENGTH:
        score += 1
        reasons.append(f"len={line_len}")
    
    # -1 if all caps
    if is_all_caps(line):
        score -= 1
        reasons.append("all_caps")
    
    return score, reasons
