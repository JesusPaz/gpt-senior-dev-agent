"""
Procedures endpoints module.

This module contains API routes for procedure management.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Body, Query, Path, Depends, status
from app.schemas.procedures import (
    Procedure, ProcedureCreate, ProcedureList, 
    Step, StepCreate, StepBulkCreate,
    ProcedureUpdate, StepUpdate
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

@router.post("/", response_model=Procedure)
async def create_procedure(procedure: ProcedureCreate = Body(...)):
    """
    Create a new procedure.
    
    Args:
        procedure: The procedure data to create
        
    Returns:
        The created procedure
    """
    try:
        logger.info(f"Creating procedure with title: {procedure.title}")
        
        procedure_id = db.create_procedure(
            title=procedure.title,
            description=procedure.description,
            trigger_phrases=procedure.trigger_phrases
        )
        
        if not procedure_id:
            raise HTTPException(status_code=500, detail="Failed to create procedure")
        
        # Get the created procedure
        created_procedure = db.get_procedure(procedure_id)
        
        if not created_procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found after creation")
        
        return created_procedure
    except Exception as e:
        logger.error(f"Error creating procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating procedure: {str(e)}")

@router.get("/", response_model=List[ProcedureList])
async def get_procedures(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get a list of procedures.
    
    Args:
        limit: Maximum number of procedures to return
        offset: Number of procedures to skip
        
    Returns:
        A list of procedures
    """
    try:
        logger.info(f"Getting procedures with limit: {limit}, offset: {offset}")
        procedures = db.get_procedures(limit, offset)
        
        return procedures
    except Exception as e:
        logger.error(f"Error getting procedures: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting procedures: {str(e)}")

@router.get("/{procedure_id}", response_model=Procedure)
async def get_procedure(procedure_id: int = Path(..., ge=1)):
    """
    Get a specific procedure by ID.
    
    Args:
        procedure_id: The ID of the procedure to get
        
    Returns:
        The procedure data with its steps
    """
    try:
        logger.info(f"Getting procedure with ID: {procedure_id}")
        procedure = db.get_procedure(procedure_id)
        
        if not procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found")
        
        return procedure
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting procedure: {str(e)}")

@router.post("/{procedure_id}/steps", response_model=List[Step])
async def add_procedure_steps(
    procedure_id: int = Path(..., ge=1),
    steps_data: StepBulkCreate = Body(...)
):
    """
    Add steps to a procedure.
    
    Args:
        procedure_id: The ID of the procedure to add steps to
        steps_data: The steps data to add
        
    Returns:
        The added steps
    """
    try:
        logger.info(f"Adding {len(steps_data.steps)} steps to procedure with ID: {procedure_id}")
        
        # Check if procedure exists
        procedure = db.get_procedure(procedure_id)
        
        if not procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found")
        
        # Prepare steps for insertion
        steps_to_add = []
        current_max_order = 0
        
        # Find the current maximum order if steps exist
        if procedure['steps']:
            current_max_order = max(step['order'] for step in procedure['steps'])
        
        # Add steps with auto-incrementing order if not specified
        for i, step in enumerate(steps_data.steps):
            step_dict = {
                'content': step.content,
                'order': step.order if step.order > 0 else current_max_order + i + 1
            }
            steps_to_add.append(step_dict)
        
        # Add steps to the database
        step_ids = db.add_procedure_steps(procedure_id, steps_to_add)
        
        if not step_ids:
            raise HTTPException(status_code=500, detail="Failed to add steps to procedure")
        
        # Get the updated procedure with steps
        updated_procedure = db.get_procedure(procedure_id)
        
        if not updated_procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found after adding steps")
        
        # Return only the newly added steps
        new_steps = [step for step in updated_procedure['steps'] if step['id'] in step_ids]
        
        return new_steps
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding steps to procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding steps to procedure: {str(e)}")

@router.delete("/{procedure_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_procedure(procedure_id: int = Path(..., ge=1)):
    """
    Delete a procedure and all its steps by ID.
    
    Args:
        procedure_id: The ID of the procedure to delete
        
    Returns:
        No content on success
    """
    try:
        logger.info(f"Deleting procedure with ID: {procedure_id}")
        success = db.delete_procedure(procedure_id)
        
        if success:
            return None
        else:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found")
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error deleting procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting procedure: {str(e)}")

@router.put("/{procedure_id}", response_model=Procedure)
async def update_procedure(procedure_id: int = Path(..., ge=1), procedure_data: ProcedureUpdate = Body(...)):
    """
    Update a procedure by ID.
    
    Args:
        procedure_id: The ID of the procedure to update
        procedure_data: The updated procedure data
        
    Returns:
        The updated procedure with its steps
    """
    try:
        logger.info(f"Updating procedure with ID: {procedure_id}")
        
        updated_procedure = db.update_procedure(
            procedure_id=procedure_id,
            title=procedure_data.title,
            description=procedure_data.description,
            trigger_phrases=procedure_data.trigger_phrases
        )
        
        if not updated_procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found")
        
        return updated_procedure
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating procedure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating procedure: {str(e)}")

@router.put("/{procedure_id}/steps/{step_id}", response_model=Step)
async def update_procedure_step(
    procedure_id: int = Path(..., ge=1),
    step_id: int = Path(..., ge=1),
    step_data: StepUpdate = Body(...)
):
    """
    Update a procedure step by ID.
    
    Args:
        procedure_id: The ID of the procedure the step belongs to
        step_id: The ID of the step to update
        step_data: The updated step data
        
    Returns:
        The updated step
    """
    try:
        logger.info(f"Updating step {step_id} for procedure with ID: {procedure_id}")
        
        # First check if the step belongs to the specified procedure
        procedure = db.get_procedure(procedure_id)
        
        if not procedure:
            raise HTTPException(status_code=404, detail=f"Procedure with ID {procedure_id} not found")
        
        # Check if the step exists and belongs to this procedure
        step_exists = False
        for step in procedure['steps']:
            if step['id'] == step_id:
                step_exists = True
                break
        
        if not step_exists:
            raise HTTPException(
                status_code=404, 
                detail=f"Step with ID {step_id} not found in procedure with ID {procedure_id}"
            )
        
        # Update the step
        updated_step = db.update_procedure_step(
            step_id=step_id,
            content=step_data.content,
            order=step_data.order
        )
        
        if not updated_step:
            raise HTTPException(status_code=500, detail=f"Failed to update step with ID {step_id}")
        
        return updated_step
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Error updating procedure step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating procedure step: {str(e)}")
