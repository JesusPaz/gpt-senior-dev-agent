"""
Thought schemas module.

This module contains Pydantic models for thought data validation and serialization.
"""
from typing import Optional, List
from pydantic import BaseModel

class ThoughtRequest(BaseModel):
    """Schema for thought request data."""
    text: str
    source: Optional[str] = "api"

class ThoughtResponse(BaseModel):
    """Schema for thought response data."""
    thought_id: Optional[int] = None
    transcription: str
    processed: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    summary: Optional[str] = None
    success: bool
    message: str

class ThoughtAnalysisResult(BaseModel):
    """Schema for thought analysis result data."""
    processed: str
    categories: List[str]
    tags: List[str]
    type: str  # Ideally would be Literal['idea', 'task', 'observation', 'reminder', 'question', 'note']
    priority: Optional[str] = None  # Ideally would be Optional[Literal['low', 'medium', 'high']]
    summary: str

class ThoughtUpdate(BaseModel):
    """Schema for updating a thought."""
    transcription: Optional[str] = None
    processed: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    summary: Optional[str] = None
