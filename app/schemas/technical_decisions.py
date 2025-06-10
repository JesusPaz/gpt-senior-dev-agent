"""
Technical decisions schemas module.

This module contains Pydantic models for technical decision data validation and serialization.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class AlternativeOption(BaseModel):
    """Schema for alternative options considered in a technical decision."""
    name: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)

class TechnicalDecisionBase(BaseModel):
    """Base schema for technical decision data."""
    title: str
    context: str
    decision: str
    reasoning: str
    alternatives: List[AlternativeOption] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    related_resources: List[str] = Field(default_factory=list)

class TechnicalDecisionCreate(TechnicalDecisionBase):
    """Schema for creating a technical decision."""
    pass

class TechnicalDecision(TechnicalDecisionBase):
    """Schema for technical decision response data."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TechnicalDecisionUpdate(BaseModel):
    """Schema for updating a technical decision."""
    title: Optional[str] = None
    context: Optional[str] = None
    decision: Optional[str] = None
    reasoning: Optional[str] = None
    alternatives: Optional[List[AlternativeOption]] = None
    consequences: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    related_resources: Optional[List[str]] = None
