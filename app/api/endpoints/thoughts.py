"""
Thoughts endpoints module.

This module contains API routes for thought processing and retrieval.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends, status
from app.schemas.thoughts import ThoughtRequest, ThoughtResponse, ThoughtUpdate
from app.services.thought_service import TextAnalyzer
from app.core.database import Database
from app.core.config import load_config

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Load configuration
config = load_config()

# Initialize components
analyzer = TextAnalyzer(config)
db = Database(config)

@router.post("/", response_model=ThoughtResponse)
async def process_thought(request: ThoughtRequest = Body(...)):
    """
    Process a thought and store it in the database.
    
    Args:
        request: The thought request containing the text to process
        
    Returns:
        A response containing the processed thought and status
    """
    try:
        logger.info(f"Received thought from source: {request.source}")
        
        # Check if text is empty
        if not request.text.strip():
            return ThoughtResponse(
                transcription=request.text,
                success=False,
                message="Thought text cannot be empty"
            )
        
        # Process with Ollama
        logger.info("Processing thought with Ollama")
        analysis_result = analyzer.analyze_with_ollama(request.text)
        
        thought_id = None
        
        # Only save if we have valid processed content
        if analysis_result and analysis_result.get('processed'):
            logger.info("Saving thought to database")
            thought_id = db.save_thought(request.text, analysis_result)
            
            return ThoughtResponse(
                thought_id=thought_id,
                transcription=request.text,
                processed=analysis_result.get('processed', ''),
                categories=analysis_result.get('categories', []),
                tags=analysis_result.get('tags', []),
                type=analysis_result.get('type', ''),
                priority=analysis_result.get('priority'),
                summary=analysis_result.get('summary', ''),
                success=True,
                message="Thought processed and saved successfully"
            )
        else:
            logger.warning("Failed to process thought with Ollama")
            return ThoughtResponse(
                transcription=request.text,
                success=False,
                message="Failed to process thought with Ollama"
            )
            
    except Exception as e:
        logger.error(f"Error processing thought: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing thought: {str(e)}")

@router.get("/{thought_id}", response_model=ThoughtResponse)
async def get_thought(thought_id: int):
    """
    Get a thought by ID.
    
    Args:
        thought_id: The ID of the thought to get
        
    Returns:
        The thought data
    """
    try:
        logger.info(f"Getting thought with ID: {thought_id}")
        thought = db.get_thought(thought_id)
        
        if thought:
            return ThoughtResponse(
                thought_id=thought['id'],
                transcription=thought['transcription'],
                processed=thought['processed'],
                categories=thought['categories'],
                tags=thought['tags'],
                type=thought['type'],
                priority=thought['priority'],
                summary=thought['summary'],
                success=True,
                message="Thought retrieved successfully"
            )
        else:
            raise HTTPException(status_code=404, detail=f"Thought with ID {thought_id} not found")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error getting thought: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting thought: {str(e)}")

@router.get("/", response_model=List[ThoughtResponse])
async def get_thoughts(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """
    Get multiple thoughts.
    
    Args:
        limit: Maximum number of thoughts to return
        offset: Number of thoughts to skip
        
    Returns:
        A list of thoughts
    """
    try:
        logger.info(f"Getting thoughts with limit: {limit}, offset: {offset}")
        thoughts = db.get_thoughts(limit, offset)
        
        return [
            ThoughtResponse(
                thought_id=thought['id'],
                transcription=thought['transcription'],
                processed=thought['processed'],
                categories=thought['categories'],
                tags=thought['tags'],
                type=thought['type'],
                priority=thought['priority'],
                summary=thought['summary'],
                success=True,
                message="Thought retrieved successfully"
            )
            for thought in thoughts
        ]
            
    except Exception as e:
        logger.error(f"Error getting thoughts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting thoughts: {str(e)}")

@router.delete("/{thought_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thought(thought_id: int = Path(..., ge=1)):
    """
    Delete a thought by ID.
    
    Args:
        thought_id: The ID of the thought to delete
        
    Returns:
        No content on success
    """
    try:
        logger.info(f"Deleting thought with ID: {thought_id}")
        success = db.delete_thought(thought_id)
        
        if success:
            return None
        else:
            raise HTTPException(status_code=404, detail=f"Thought with ID {thought_id} not found")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error deleting thought: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting thought: {str(e)}")

@router.put("/{thought_id}", response_model=ThoughtResponse)
async def update_thought(thought_id: int = Path(..., ge=1), thought_data: ThoughtUpdate = Body(...)):
    """
    Update a thought by ID.
    
    Args:
        thought_id: The ID of the thought to update
        thought_data: The updated thought data
        
    Returns:
        The updated thought
    """
    try:
        logger.info(f"Updating thought with ID: {thought_id}")
        
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in thought_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_thought = db.update_thought(thought_id, update_data)
        
        if not updated_thought:
            raise HTTPException(status_code=404, detail=f"Thought with ID {thought_id} not found")
        
        return ThoughtResponse(
            thought_id=updated_thought['id'],
            transcription=updated_thought['transcription'],
            processed=updated_thought['processed'],
            categories=updated_thought['categories'],
            tags=updated_thought['tags'],
            type=updated_thought['type'],
            priority=updated_thought['priority'],
            summary=updated_thought['summary'],
            success=True,
            message="Thought updated successfully"
        )
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating thought: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating thought: {str(e)}")
