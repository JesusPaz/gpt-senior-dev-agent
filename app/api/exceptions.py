"""
API exceptions module.

This module contains custom exceptions for API endpoints.
"""
from fastapi import HTTPException, status

class ThoughtProcessingError(HTTPException):
    """Exception raised when there is an error processing a thought."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing thought: {detail}"
        )

class ThoughtNotFoundError(HTTPException):
    """Exception raised when a thought is not found."""
    def __init__(self, thought_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thought with ID {thought_id} not found"
        )

class DatabaseError(HTTPException):
    """Exception raised when there is a database error."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {detail}"
        )

class OllamaServiceError(HTTPException):
    """Exception raised when there is an error with the Ollama service."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama service error: {detail}"
        )
