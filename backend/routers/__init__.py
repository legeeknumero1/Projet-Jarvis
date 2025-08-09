"""Routers FastAPI modulaires"""
from . import health, chat, voice, websocket

__all__ = ["health", "chat", "voice", "websocket"]