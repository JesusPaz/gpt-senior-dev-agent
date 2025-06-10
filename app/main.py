#!/usr/bin/env python3
"""
Thought Processor API

A simple API for processing and storing thoughts using Ollama AI.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.endpoints import thoughts, transcriptions, procedures, technical_decisions, experiences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Thought Processor API",
    description="API for processing and storing thoughts using Ollama AI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(thoughts.router, prefix="/thoughts", tags=["thoughts"])
app.include_router(transcriptions.router, prefix="/transcriptions", tags=["transcriptions"])
app.include_router(procedures.router, prefix="/procedures", tags=["procedures"])
app.include_router(technical_decisions.router, prefix="/technical-decisions", tags=["technical-decisions"])
app.include_router(experiences.router, prefix="/experiences", tags=["experiences"])

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "Thought Processor API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "service": "thought-processor"}
