"""
Games Module for Shadow Roll Bot
Manages all gaming systems and interactive features
"""

from .game_manager import GameManager
from .would_you_rather import WouldYouRatherGame

__all__ = ['GameManager', 'WouldYouRatherGame']