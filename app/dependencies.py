from typing import Annotated
from fastapi import Header, HTTPException, Query


async def get_token_header(x_token: Annotated[str, Header()] = None):
    """
    Dependency to validate X-Token header
    """
    if not x_token or x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    return x_token


async def get_query_token(token: str = Query(None)):
    """
    Dependency to validate token query parameter
    """
    if not token or token != "demo-token":
        raise HTTPException(status_code=400, detail="Query token required")
    return token
