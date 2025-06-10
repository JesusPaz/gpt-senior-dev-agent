"""
Past experiences schemas module.

This module contains Pydantic models for past experience data validation and serialization.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ExperienceBase(BaseModel):
    """Base schema for past experience data."""
    title: str
    situation: str
    actions: List[str] = Field(default_factory=list)
    outcome: str
    learnings: List[str] = Field(default_factory=list)
    context: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    related_resources: List[str] = Field(default_factory=list)
    importance: Optional[str] = None  # Could be "low", "medium", "high"

class ExperienceCreate(ExperienceBase):
    """Schema for creating a past experience."""
    pass

class Experience(ExperienceBase):
    """Schema for past experience response data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ExperienceUpdate(BaseModel):
    """Schema for updating a past experience."""
    title: Optional[str] = None
    situation: Optional[str] = None
    actions: Optional[List[str]] = None
    outcome: Optional[str] = None
    learnings: Optional[List[str]] = None
    context: Optional[str] = None
    tags: Optional[List[str]] = None
    related_resources: Optional[List[str]] = None
    importance: Optional[str] = None
