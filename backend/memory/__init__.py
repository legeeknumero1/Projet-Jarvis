"""
>à Package mémoire neuromorphique Jarvis
"""

# Export des classes principales
try:
    from .brain_memory_system import BrainMemorySystem
    from .memory_manager import MemoryManager
    from .memory_types import (
        EmotionalValence, MemoryType, ConsolidationLevel,
        EmotionalContext, MemoryFragment
    )
    from .qdrant_adapter import QdrantMemoryAdapter
    
    __all__ = [
        'BrainMemorySystem',
        'MemoryManager',
        'EmotionalValence',
        'MemoryType', 
        'ConsolidationLevel',
        'EmotionalContext',
        'MemoryFragment',
        'QdrantMemoryAdapter'
    ]
    
except ImportError as e:
    # Fallback en cas d'imports manquants
    import logging
    logging.warning(f"  Imports mémoire partiels: {e}")
    __all__ = []