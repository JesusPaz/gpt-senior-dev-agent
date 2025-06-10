"""
Transcription schemas module.

This module contains Pydantic models for audio transcription data validation and serialization.
"""
from typing import Optional
from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    """Schema for transcription response data."""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    success: bool
    message: str
