"""
Technical decisions endpoints module.

This module contains API routes for technical decision management.
"""
import logging
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends, status
from app.schemas.technical_decisions import (
    TechnicalDecision, TechnicalDecisionCreate, TechnicalDecisionUpdate
)
from app.core.database import Database
from app.core.config import load_config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Load configuration
config = load_config()

# Initialize database
db = Database(config)

@router.post("/", response_model=TechnicalDecision)
async def create_technical_decision(decision: TechnicalDecisionCreate = Body(...)):
    """
    Create a new technical decision.
    
    Args:
        decision: The technical decision data to create
        
    Returns:
        The created technical decision
    """
    try:
        logger.info(f"Creating technical decision with title: {decision.title}")
        
        decision_id = db.create_technical_decision(
            title=decision.title,
            context=decision.context,
            decision=decision.decision,
            reasoning=decision.reasoning,
            alternatives=[alt.dict() for alt in decision.alternatives],
            consequences=decision.consequences,
            tags=decision.tags,
            related_resources=decision.related_resources
        )
        
        if not decision_id:
            raise HTTPException(status_code=500, detail="Failed to create technical decision")
        
        # Get the created decision
        created_decision = db.get_technical_decision(decision_id)
        
        if not created_decision:
            raise HTTPException(status_code=404, detail=f"Technical decision with ID {decision_id} not found after creation")
        
        return created_decision
    except Exception as e:
        logger.error(f"Error creating technical decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating technical decision: {str(e)}")

@router.get("/", response_model=List[TechnicalDecision])
async def get_technical_decisions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tags: Optional[List[str]] = Query(None)
):
    """
    Get a list of technical decisions.
    
    Args:
        limit: Maximum number of decisions to return
        offset: Number of decisions to skip
        tags: Optional list of tags to filter by
        
    Returns:
        A list of technical decisions
    """
    try:
        logger.info(f"Getting technical decisions with limit: {limit}, offset: {offset}, tags: {tags}")
        decisions = db.get_technical_decisions(limit, offset, tags)
        
        return decisions
    except Exception as e:
        logger.error(f"Error getting technical decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting technical decisions: {str(e)}")

@router.get("/{decision_id}", response_model=TechnicalDecision)
async def get_technical_decision(decision_id: int = Path(..., ge=1)):
    """
    Get a specific technical decision by ID.
    
    Args:
        decision_id: The ID of the technical decision to get
        
    Returns:
        The technical decision data
    """
    try:
        logger.info(f"Getting technical decision with ID: {decision_id}")
        decision = db.get_technical_decision(decision_id)
        
        if not decision:
            raise HTTPException(status_code=404, detail=f"Technical decision with ID {decision_id} not found")
        
        return decision
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technical decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting technical decision: {str(e)}")

@router.put("/{decision_id}", response_model=TechnicalDecision)
async def update_technical_decision(
    decision_id: int = Path(..., ge=1),
    decision_data: TechnicalDecisionUpdate = Body(...)
):
    """
    Update a technical decision by ID.
    
    Args:
        decision_id: The ID of the technical decision to update
        decision_data: The updated technical decision data
        
    Returns:
        The updated technical decision
    """
    try:
        logger.info(f"Updating technical decision with ID: {decision_id}")
        
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in decision_data.dict().items() if v is not None}
        
        # Handle alternatives specially
        if 'alternatives' in update_data and update_data['alternatives'] is not None:
            update_data['alternatives'] = [alt.dict() for alt in update_data['alternatives']]
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_decision = db.update_technical_decision(decision_id, update_data)
        
        if not updated_decision:
            raise HTTPException(status_code=404, detail=f"Technical decision with ID {decision_id} not found")
        
        return updated_decision
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating technical decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating technical decision: {str(e)}")

@router.delete("/{decision_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technical_decision(decision_id: int = Path(..., ge=1)):
    """
    Delete a technical decision by ID.
    
    Args:
        decision_id: The ID of the technical decision to delete
        
    Returns:
        No content on success
    """
    try:
        logger.info(f"Deleting technical decision with ID: {decision_id}")
        success = db.delete_technical_decision(decision_id)
        
        if success:
            return None
        else:
            raise HTTPException(status_code=404, detail=f"Technical decision with ID {decision_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting technical decision: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting technical decision: {str(e)}")
