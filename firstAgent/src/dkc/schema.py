"""Data contracts using Pydantic v2 for document knowledge conversion."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation reference to source document.
    
    Represents a citation pointing back to the original source document.
    Used to maintain provenance and allow traceability from extracted
    knowledge back to the source material.
    """
    doc_id: str = Field(..., description="Document ID this citation references")
    source_path: str = Field(..., description="Path to the source file")
    text_excerpt: str = Field(..., description="Excerpt of the cited text")
    page: Optional[int] = Field(None, description="Page number if applicable")
    line: Optional[int] = Field(None, description="Line number if applicable")


class KnowledgeCard(BaseModel):
    """Knowledge card representing key information extracted from a document.
    
    A knowledge card captures the essential information from a source document
    in a structured format. It includes facts, entities, acronyms, and citations
    to maintain provenance. Typically contains <=5 facts but this is not enforced
    as a hard constraint to allow flexibility in extraction.
    
    Invariants:
    - id must be unique across all cards
    - source_path must point to an existing file
    - facts list should typically contain <=5 items for readability
    - citations must reference valid doc_ids
    """
    id: str = Field(..., description="Unique identifier for this knowledge card")
    title: str = Field(..., description="Title of the source document")
    date: Optional[str] = Field(None, description="Document date in YYYY-MM-DD format")
    source_path: str = Field(..., description="Path to the source file")
    facts: List[str] = Field(default_factory=list, description="List of key facts extracted from the document")
    acronyms: List[str] = Field(default_factory=list, description="List of acronyms found in the document")
    entities: List[str] = Field(default_factory=list, description="List of named entities extracted from the document")
    citations: List[Citation] = Field(default_factory=list, description="List of citations to source material")


class Chunk(BaseModel):
    """Text chunk with provenance information.
    
    Represents a segment of text from a document with full provenance
    information to enable traceability. Chunks are used for downstream
    processing like embedding generation or search indexing.
    
    Invariants:
    - id must be unique across all chunks
    - doc_id must reference a valid document
    - ordinal must be non-negative and unique within a document
    - text must not be empty
    - if line_start is provided, line_end must be >= line_start
    """
    id: str = Field(..., description="Unique identifier for this chunk")
    doc_id: str = Field(..., description="Document ID this chunk belongs to")
    ordinal: int = Field(..., description="Order of this chunk within the document")
    text: str = Field(..., description="Text content of this chunk")
    source_path: str = Field(..., description="Path to the source file")
    page: Optional[int] = Field(None, description="Page number if applicable")
    line_start: Optional[int] = Field(None, description="Starting line number if applicable")
    line_end: Optional[int] = Field(None, description="Ending line number if applicable")