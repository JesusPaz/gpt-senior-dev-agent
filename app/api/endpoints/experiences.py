"""
Past experiences endpoints module.

This module contains API routes for past experience management.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends, status
from app.schemas.experiences import (
    Experience, ExperienceCreate, ExperienceUpdate
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

@router.post("/", response_model=Experience)
async def create_experience(experience: ExperienceCreate = Body(...)):
    """
    Create a new past experience.
    
    Args:
        experience: The experience data to create
        
    Returns:
        The created experience
    """
    try:
        logger.info(f"Creating experience with title: {experience.title}")
        
        experience_id = db.create_experience(
            title=experience.title,
            situation=experience.situation,
            actions=experience.actions,
            outcome=experience.outcome,
            learnings=experience.learnings,
            context=experience.context,
            tags=experience.tags,
            related_resources=experience.related_resources,
            importance=experience.importance
        )
        
        if not experience_id:
            raise HTTPException(status_code=500, detail="Failed to create experience")
        
        # Get the created experience
        created_experience = db.get_experience(experience_id)
        
        if not created_experience:
            raise HTTPException(status_code=404, detail=f"Experience with ID {experience_id} not found after creation")
        
        return created_experience
    except Exception as e:
        logger.error(f"Error creating experience: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating experience: {str(e)}")

@router.get("/", response_model=List[Experience])
async def get_experiences(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tags: Optional[List[str]] = Query(None),
    importance: Optional[str] = Query(None)
):
    """
    Get a list of past experiences.
    
    Args:
        limit: Maximum number of experiences to return
        offset: Number of experiences to skip
        tags: Optional list of tags to filter by
        importance: Optional importance level to filter by (low, medium, high)
        
    Returns:
        A list of experiences
    """
    try:
        logger.info(f"Getting experiences with limit: {limit}, offset: {offset}, tags: {tags}, importance: {importance}")
        experiences = db.get_experiences(limit, offset, tags, importance)
        
        return experiences
    except Exception as e:
        logger.error(f"Error getting experiences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting experiences: {str(e)}")

@router.get("/{experience_id}", response_model=Experience)
async def get_experience(experience_id: int = Path(..., ge=1)):
    """
    Get a specific past experience by ID.
    
    Args:
        experience_id: The ID of the experience to get
        
    Returns:
        The experience data
    """
    try:
        logger.info(f"Getting experience with ID: {experience_id}")
        experience = db.get_experience(experience_id)
        
        if not experience:
            raise HTTPException(status_code=404, detail=f"Experience with ID {experience_id} not found")
        
        return experience
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting experience: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting experience: {str(e)}")

@router.put("/{experience_id}", response_model=Experience)
async def update_experience(
    experience_id: int = Path(..., ge=1),
    experience_data: ExperienceUpdate = Body(...)
):
    """
    Update a past experience by ID.
    
    Args:
        experience_id: The ID of the experience to update
        experience_data: The updated experience data
        
    Returns:
        The updated experience
    """
    try:
        logger.info(f"Updating experience with ID: {experience_id}")
        
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in experience_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_experience = db.update_experience(experience_id, update_data)
        
        if not updated_experience:
            raise HTTPException(status_code=404, detail=f"Experience with ID {experience_id} not found")
        
        return updated_experience
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating experience: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating experience: {str(e)}")

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(experience_id: int = Path(..., ge=1)):
    """
    Delete a past experience by ID.
    
    Args:
        experience_id: The ID of the experience to delete
        
    Returns:
        No content on success
    """
    try:
        logger.info(f"Deleting experience with ID: {experience_id}")
        success = db.delete_experience(experience_id)
        
        if success:
            return None
        else:
            raise HTTPException(status_code=404, detail=f"Experience with ID {experience_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting experience: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting experience: {str(e)}")
