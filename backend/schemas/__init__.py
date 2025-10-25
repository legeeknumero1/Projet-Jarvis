"""Schemas Pydantic pour l'API Jarvis"""
from .chat import MessageRequest, MessageResponse
from .voice import TranscriptionResponse, TTSRequest
from .memory import MemoryQuery, MemoryItem, MemoryResponse, ConversationSaveRequest
from .common import APIResponse, HealthResponse, ErrorResponse, MetricsResponse

__all__ = [
    # Chat
    "MessageRequest",
    "MessageResponse",
    
    # Voice
    "TranscriptionResponse", 
    "TTSRequest",
    
    # Memory
    "MemoryQuery",
    "MemoryItem", 
    "MemoryResponse",
    "ConversationSaveRequest",
    
    # Common
    "APIResponse",
    "HealthResponse",
    "ErrorResponse",
    "MetricsResponse"
]