"""Dépendances FastAPI pour sécurité et authentification"""
from fastapi import Depends, HTTPException, Header, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Optional
import logging

def setup_cors(app: FastAPI, allowed_origins: list[str]):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging.info(f"✅ [CORS] Configured for origins: {allowed_origins}")

async def _get_api_key(x_api_key: Optional[str] = Header(default=None)) -> Optional[str]:
    """Extract API key from X-API-Key header"""
    return x_api_key

async def api_key_required(
    req_key: Annotated[Optional[str], Depends(_get_api_key)]
):
    """Dependency: require valid API key"""
    from ..config import Settings
    
    settings = Settings()
    if not req_key or req_key != settings.api_key:
        logging.warning(f"🔒 [AUTH] Invalid API key attempt: {req_key[:4] if req_key else 'None'}***")
        raise HTTPException(401, "Invalid or missing API key")
    
    logging.debug(f"✅ [AUTH] Valid API key: {req_key[:4]}***")
    return req_key

async def api_key_optional():
    """Dependency: API key optional (no-op for consistency)"""
    return True