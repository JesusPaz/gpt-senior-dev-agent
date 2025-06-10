"""
Procedure schemas module.

This module contains Pydantic models for procedure data validation and serialization.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class StepBase(BaseModel):
    """Base schema for procedure step data."""
    content: str
    order: int

class StepCreate(StepBase):
    """Schema for creating a procedure step."""
    pass

class Step(StepBase):
    """Schema for procedure step response data."""
    id: int
    procedure_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProcedureBase(BaseModel):
    """Base schema for procedure data."""
    title: str
    description: Optional[str] = None
    trigger_phrases: List[str] = Field(default_factory=list)

class ProcedureCreate(ProcedureBase):
    """Schema for creating a procedure."""
    pass

class Procedure(ProcedureBase):
    """Schema for procedure response data."""
    id: int
    created_at: datetime
    steps: List[Step] = Field(default_factory=list)

    class Config:
        from_attributes = True

class ProcedureList(ProcedureBase):
    """Schema for procedure list item response data."""
    id: int
    created_at: datetime
    step_count: int = 0

    class Config:
        from_attributes = True

class StepBulkCreate(BaseModel):
    """Schema for creating multiple steps at once."""
    steps: List[StepCreate]

class ProcedureUpdate(BaseModel):
    """Schema for updating a procedure."""
    title: str
    description: Optional[str] = None
    trigger_phrases: List[str] = Field(default_factory=list)

class StepUpdate(BaseModel):
    """Schema for updating a procedure step."""
    content: str
    order: Optional[int] = None
