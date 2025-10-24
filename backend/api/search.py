"""
Endpoints API pour la recherche web via MCP Multi-Search
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from ..integration.mcp_client import MCPClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    count: Optional[int] = 10
    search_type: Optional[str] = "web"
    privacy_preference: Optional[str] = "medium"

class ParallelSearchRequest(BaseModel):
    query: str
    providers: Optional[List[str]] = None
    count: Optional[int] = 5

@router.post("/web")
async def search_web(request: SearchRequest):
    """Recherche web avec le système multi-provider"""
    try:
        mcp_client = MCPClient()
        result = await mcp_client.search_web(
            query=request.query,
            count=request.count,
            search_type=request.search_type,
            privacy_preference=request.privacy_preference
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parallel")
async def search_parallel(request: ParallelSearchRequest):
    """Recherche parallèle sur plusieurs providers"""
    try:
        mcp_client = MCPClient()
        result = await mcp_client.search_parallel(
            query=request.query,
            providers=request.providers,
            count=request.count
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Parallel search API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_search_providers():
    """Obtenir la liste des providers de recherche disponibles"""
    try:
        # Import du manager pour obtenir le statut
        import sys
        sys.path.append('/home/enzo/Projet-Jarvis/MCP/servers')
        from multi_search_manager import MultiSearchManagerMCP
        
        manager = MultiSearchManagerMCP()
        status = await manager.get_provider_status()
        await manager.close()
        
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Provider status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
