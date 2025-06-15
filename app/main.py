from fastapi import FastAPI, Depends

from .dependencies import get_query_token, get_token_header
from .routers import agents, tasks

app = FastAPI(
    title="Agent RAG Demo API",
    description="A simple API to demonstrate agents and their tasks",
    version="0.1.0",
    dependencies=[Depends(get_query_token)]
)

# Include routers
app.include_router(agents.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Agent RAG Demo API. Visit /docs for the API documentation."}
