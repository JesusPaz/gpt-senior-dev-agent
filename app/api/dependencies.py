"""
API dependencies module.

This module contains reusable dependencies for API endpoints.
"""
import logging
from typing import Dict, Any
from app.core.config import load_config
from app.core.database import Database
from app.services.thought_service import TextAnalyzer

logger = logging.getLogger(__name__)

# Load configuration once at module level
config = load_config()

def get_config() -> Dict[str, Any]:
    """
    Get application configuration.
    
    Returns:
        Configuration dictionary
    """
    return config

def get_db() -> Database:
    """
    Get database instance.
    
    Returns:
        Database instance
    """
    return Database(config)

def get_analyzer() -> TextAnalyzer:
    """
    Get text analyzer instance.
    
    Returns:
        TextAnalyzer instance
    """
    return TextAnalyzer(config)
