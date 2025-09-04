"""Highlight selection logic."""

from typing import List, Dict


def pick_highlights(lines: List[str], k: int = 5) -> List[Dict]:
    """Select top k highlights from lines based on scoring.
    
    For each line (1-based index), compute score & reasons.
    Filter out lines with score ≤ 0.
    Sort by (score desc, line_no asc).
    Take first k.
    
    Args:
        lines: List of normalized lines
        k: Number of highlights to select (default 5)
        
    Returns:
        List of dicts with {rank, line_no, text, reason}
        rank starts at 1, reason is "; ".join(reasons)
    """
    from .score import score_line
    
    # Score each line and collect candidates
    candidates = []
    for i, line in enumerate(lines, 1):  # 1-based line numbers
        score, reasons = score_line(line)
        
        # Only include lines with positive scores
        if score > 0:
            candidates.append({
                'score': score,
                'line_no': i,
                'text': line,
                'reasons': reasons
            })
    
    # Sort by (score desc, line_no asc) for deterministic results
    candidates.sort(key=lambda x: (-x['score'], x['line_no']))
    
    # Take first k and assign ranks
    highlights = []
    for rank, candidate in enumerate(candidates[:k], 1):
        highlights.append({
            'rank': rank,
            'line_no': candidate['line_no'],
            'text': candidate['text'],
            'reason': '; '.join(candidate['reasons'])
        })
    
    return highlights
