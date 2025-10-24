"""
Endpoints API pour les capacités web de Jarvis via MCP
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl
import logging

from services.web_service import get_web_service, WebService

router = APIRouter()
logger = logging.getLogger(__name__)

# Modèles Pydantic pour les requêtes
class SearchRequest(BaseModel):
    query: str
    
class WebContentRequest(BaseModel):
    url: HttpUrl
    
class ScreenshotRequest(BaseModel):
    url: HttpUrl
    full_page: bool = True
    
class InteractionRequest(BaseModel):
    url: HttpUrl
    instruction: str

@router.get("/capabilities")
async def get_web_capabilities(web_service: WebService = Depends(get_web_service)):
    """Retourne les capacités web disponibles de Jarvis"""
    try:
        capabilities = await web_service.get_capabilities()
        return {
            "status": "success",
            "capabilities": capabilities,
            "message": "Capacités web de Jarvis"
        }
    except Exception as e:
        logger.error(f"Erreur récupération capacités web: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_web(
    request: SearchRequest, 
    web_service: WebService = Depends(get_web_service)
):
    """Effectue une recherche sur le web"""
    try:
        logger.info(f"🔍 Recherche web demandée: {request.query}")
        
        result = await web_service.search_web(request.query)
        
        if result:
            return {
                "status": "success",
                "data": result,
                "message": f"Recherche web réussie pour '{request.query}'"
            }
        else:
            return {
                "status": "error",
                "message": f"Aucun résultat pour '{request.query}'"
            }
            
    except Exception as e:
        logger.error(f"Erreur recherche web: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content")
async def get_web_content(
    request: WebContentRequest,
    web_service: WebService = Depends(get_web_service)
):
    """Récupère le contenu d'une page web"""
    try:
        logger.info(f"📄 Contenu web demandé: {request.url}")
        
        result = await web_service.get_web_content(str(request.url))
        
        if result:
            return {
                "status": "success", 
                "data": result,
                "message": f"Contenu récupéré de {request.url}"
            }
        else:
            return {
                "status": "error",
                "message": f"Impossible de récupérer le contenu de {request.url}"
            }
            
    except Exception as e:
        logger.error(f"Erreur récupération contenu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/screenshot")
async def take_screenshot(
    request: ScreenshotRequest,
    web_service: WebService = Depends(get_web_service)
):
    """Prend une capture d'écran d'une page web"""
    try:
        logger.info(f"📸 Capture d'écran demandée: {request.url}")
        
        result = await web_service.take_screenshot(str(request.url), request.full_page)
        
        if result:
            return {
                "status": "success",
                "data": result,
                "message": f"Capture d'écran prise de {request.url}"
            }
        else:
            return {
                "status": "error", 
                "message": f"Impossible de capturer {request.url}"
            }
            
    except Exception as e:
        logger.error(f"Erreur capture d'écran: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interact")
async def interact_with_page(
    request: InteractionRequest,
    web_service: WebService = Depends(get_web_service)
):
    """Interagit avec une page web selon des instructions"""
    try:
        logger.info(f"🤝 Interaction demandée: {request.url} - {request.instruction}")
        
        result = await web_service.interact_with_page(str(request.url), request.instruction)
        
        if result:
            return {
                "status": "success",
                "data": result,
                "message": f"Interaction réussie avec {request.url}"
            }
        else:
            return {
                "status": "error",
                "message": f"Interaction échouée avec {request.url}"
            }
            
    except Exception as e:
        logger.error(f"Erreur interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_web_status(web_service: WebService = Depends(get_web_service)):
    """Retourne le statut du service web de Jarvis"""
    try:
        return {
            "status": "success",
            "initialized": web_service.is_initialized,
            "message": "Service web " + ("actif" if web_service.is_initialized else "inactif")
        }
    except Exception as e:
        logger.error(f"Erreur statut web: {e}")
        raise HTTPException(status_code=500, detail=str(e))