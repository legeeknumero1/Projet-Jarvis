"""
🧠 Module de Mémoire Neuromorphique Jarvis
Architecture inspirée du cerveau humain avec système limbique, cortex préfrontal et hippocampe
"""

from .brain_memory_system import (
    BrainMemorySystem,
    MemoryFragment,
    EmotionalContext,
    MemoryType,
    ConsolidationLevel,
    EmotionalValence
)

from .limbic_system import LimbicSystem
from .prefrontal_cortex import PrefrontalCortex  
from .hippocampus import Hippocampus

__all__ = [
    'BrainMemorySystem',
    'LimbicSystem', 
    'PrefrontalCortex',
    'Hippocampus',
    'MemoryFragment',
    'EmotionalContext',
    'MemoryType',
    'ConsolidationLevel',
    'EmotionalValence'
]