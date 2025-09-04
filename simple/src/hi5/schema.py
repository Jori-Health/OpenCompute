"""Pydantic models for highlight data structures."""

from pydantic import BaseModel, Field


class Highlight(BaseModel):
    """A highlight entry with ranking and metadata.
    
    Fields:
        rank: Ranking position starting from 1, increasing (1, 2, 3, ...)
        line_no: 1-based line number in the original file
        text: The actual line content from the file
        reason: Semicolon-separated list of scoring criteria that matched
    """
    rank: int = Field(ge=1, description="Ranking position starting from 1")
    line_no: int = Field(ge=1, description="1-based line number in original file")
    text: str = Field(description="The actual line content")
    reason: str = Field(description="Semicolon-separated scoring criteria")
