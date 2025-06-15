from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_token_header
from pydantic import BaseModel
from typing import List, Optional

# Define Pydantic models
class Task(BaseModel):
    id: int
    agent_id: int
    title: str
    description: str
    status: str

# Sample data - in a real app, this would come from a database
tasks_db = [
    Task(id=1, agent_id=1, title="Search for Python tutorials", description="Find beginner Python tutorials", status="completed"),
    Task(id=2, agent_id=1, title="Research FastAPI", description="Find FastAPI documentation", status="pending"),
    Task(id=3, agent_id=2, title="Analyze repository", description="Analyze code repository structure", status="in_progress"),
    Task(id=4, agent_id=2, title="Generate test cases", description="Create unit tests for functions", status="pending"),
    Task(id=5, agent_id=3, title="Retrieve documentation", description="Get relevant documentation for RAG", status="completed")
]

# Create router
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Task not found"}}
)

# Get all tasks
@router.get("/", response_model=List[Task])
async def get_tasks(status: Optional[str] = None):
    """
    Get all tasks with optional status filter
    """
    if status:
        return [task for task in tasks_db if task.status == status]
    return tasks_db

# Get task by ID
@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """
    Get a specific task by ID
    """
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# Get tasks for a specific agent
@router.get("/agent/{agent_id}", response_model=List[Task])
async def get_agent_tasks(agent_id: int):
    """
    Get all tasks assigned to a specific agent
    """
    agent_tasks = [task for task in tasks_db if task.agent_id == agent_id]
    if not agent_tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found for agent with ID {agent_id}")
    return agent_tasks

# Create new task
@router.post("/", response_model=Task, status_code=201)
async def create_task(task: Task):
    """
    Create a new task
    """
    # In a real app, we would validate and save to database
    tasks_db.append(task)
    return task
