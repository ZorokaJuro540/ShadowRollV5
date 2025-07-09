"""
Data models for Shadow Roll Bot
Defines the structure of characters, players, and achievements
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from core.config import BotConfig

@dataclass
class Character:
    """Character model with rarity and value"""
    id: int
    name: str
    anime: str
    rarity: str
    value: int
    image_url: Optional[str] = None
    
    def get_rarity_color(self) -> int:
        """Get Discord color for character rarity"""
        return BotConfig.RARITY_COLORS.get(self.rarity, 0x808080)
    
    def get_rarity_emoji(self) -> str:
        """Get emoji for character rarity"""
        return BotConfig.RARITY_EMOJIS.get(self.rarity, '◆')

@dataclass 
class Player:
    """Player model with stats and progress"""
    user_id: int
    username: str
    coins: int = 1000
    total_rerolls: int = 0
    last_reroll: Optional[str] = None
    last_daily: Optional[str] = None
    is_banned: bool = False
    created_at: Optional[str] = None

@dataclass
class Achievement:
    """Achievement model with requirements and rewards"""
    id: int
    name: str
    description: str
    requirement_type: str
    requirement_value: int
    reward_coins: int
    icon: str = "🏆"
    
    def check_completion(self, player_stats: Dict[str, Any]) -> bool:
        """Check if achievement is completed based on player stats"""
        if self.requirement_type == 'rerolls':
            return player_stats.get('total_rerolls', 0) >= self.requirement_value
        elif self.requirement_type == 'coins':
            return player_stats.get('coins', 0) >= self.requirement_value
        elif self.requirement_type == 'characters':
            return player_stats.get('unique_characters', 0) >= self.requirement_value
        elif self.requirement_type == 'rarity':
            rarity_counts = player_stats.get('rarity_counts', {})
            return rarity_counts.get(self.requirement_value, 0) > 0
        return False