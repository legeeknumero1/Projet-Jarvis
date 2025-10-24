# Import direct pour éviter les imports relatifs
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from memory_manager import MemoryManager

__all__ = ["MemoryManager"]