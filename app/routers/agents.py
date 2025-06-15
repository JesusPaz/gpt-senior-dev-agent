from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_token_header
from pydantic import BaseModel
from typing import List, Optional

# Define Pydantic models
class Agent(BaseModel):
    id: int
    name: str
    description: str
    status: str

# Sample data - in a real app, this would come from a database
agents_db = [
    Agent(id=1, name="SearchAgent", description="Searches the web for information", status="active"),
    Agent(id=2, name="CodeAgent", description="Analyzes and generates code", status="active"),
    Agent(id=3, name="RAGAgent", description="Retrieves and generates content", status="inactive")
]

# Create router
router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Agent not found"}}
)

# Get all agents
@router.get("/", response_model=List[Agent])
async def get_agents(status: Optional[str] = None):
    """
    Get all agents with optional status filter
    """
    if status:
        return [agent for agent in agents_db if agent.status == status]
    return agents_db

# Get agent by ID
@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: int):
    """
    Get a specific agent by ID
    """
    for agent in agents_db:
        if agent.id == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")

# Create new agent
@router.post("/", response_model=Agent, status_code=201)
async def create_agent(agent: Agent):
    """
    Create a new agent
    """
    # In a real app, we would validate and save to database
    agents_db.append(agent)
    return agent
