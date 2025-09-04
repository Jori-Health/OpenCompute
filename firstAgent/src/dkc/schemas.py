"""Pydantic schemas for knowledge cards, chunks, and citations."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation reference to source document."""
    doc_id: str = Field(..., description="Document ID")
    source_path: str = Field(..., description="Path to source file")
    page: Optional[int] = Field(None, description="Page number if applicable")
    line: Optional[int] = Field(None, description="Line number if applicable")
    text_excerpt: str = Field(..., description="Excerpt of cited text")


class KnowledgeCard(BaseModel):
    """Knowledge card representing key information from a document."""
    id: str = Field(..., description="Unique card ID")
    title: str = Field(..., description="Document title")
    date: Optional[str] = Field(None, description="Document date if available")
    source_path: str = Field(..., description="Path to source file")
    facts: List[str] = Field(default_factory=list, max_length=5, description="Key facts (max 5)")
    acronyms: List[str] = Field(default_factory=list, description="Acronyms found in document")
    entities: List[str] = Field(default_factory=list, description="Named entities")
    citations: List[Citation] = Field(default_factory=list, description="Citations to source")


class Chunk(BaseModel):
    """Text chunk with provenance information."""
    id: str = Field(..., description="Unique chunk ID")
    doc_id: str = Field(..., description="Document ID this chunk belongs to")
    ordinal: int = Field(..., description="Order of chunk within document")
    text: str = Field(..., description="Chunk text content")
    source_path: str = Field(..., description="Path to source file")
    page: Optional[int] = Field(None, description="Page number if applicable")
    line_start: Optional[int] = Field(None, description="Starting line number")
    line_end: Optional[int] = Field(None, description="Ending line number")


class Manifest(BaseModel):
    """Manifest with provenance and checksums."""
    total_documents: int = Field(..., description="Total number of documents processed")
    total_cards: int = Field(..., description="Total number of knowledge cards created")
    total_chunks: int = Field(..., description="Total number of chunks created")
    skipped_files: List[str] = Field(default_factory=list, description="Files that were skipped")
    checksums: dict[str, str] = Field(default_factory=dict, description="File checksums")
    created_at: str = Field(..., description="Creation timestamp")
