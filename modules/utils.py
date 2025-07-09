"""
Utility functions for Shadow Roll Bot
Centralized helper functions and utilities
"""
from datetime import datetime, timedelta
from typing import Optional

def format_number(number: int) -> str:
    """Format large numbers with commas"""
    return f"{number:,}"

def format_coins(amount: int, emoji: str = "🪙") -> str:
    """Format coin amounts with emoji"""
    return f"{format_number(amount)} {emoji}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def get_cooldown_remaining(last_used: Optional[str], cooldown_seconds: int) -> float:
    """Calculate remaining cooldown time in seconds"""
    if not last_used:
        return 0.0
    
    try:
        last_time = datetime.fromisoformat(last_used)
        elapsed = (datetime.now() - last_time).total_seconds()
        remaining = max(0, cooldown_seconds - elapsed)
        return remaining
    except (ValueError, TypeError):
        return 0.0

def get_display_name(user) -> str:
    """Get user display name (global name or username)"""
    return user.global_name or user.display_name or user.name

def get_rarity_cooldown(rarity: str) -> float:
    """Get cooldown time based on character rarity"""
    from core.config import BotConfig
    
    # Ultra-rare characters get longer cooldown to appreciate the pull
    ultra_rare_rarities = ['Mythic', 'Evolve', 'Titan', 'Fusion', 'Secret']
    
    if rarity in ultra_rare_rarities:
        return BotConfig.REROLL_COOLDOWN_RARE  # 2.0 seconds
    else:
        return BotConfig.REROLL_COOLDOWN  # 0.5 seconds

def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    duration_str = duration_str.lower().strip()
    
    if duration_str.endswith('s'):
        return int(duration_str[:-1])
    elif duration_str.endswith('m'):
        return int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        return int(duration_str[:-1]) * 3600
    elif duration_str.endswith('d'):
        return int(duration_str[:-1]) * 86400
    else:
        return int(duration_str)  # Assume seconds if no unit

def get_display_name(user) -> str:
    """Get user display name with fallback - FIXES 'User: Unknown' bug"""
    if hasattr(user, 'display_name') and user.display_name:
        return user.display_name
    elif hasattr(user, 'global_name') and user.global_name:
        return user.global_name
    elif hasattr(user, 'name') and user.name:
        return user.name
    else:
        return f"User {user.id}"

def format_time_until(target_time: datetime) -> str:
    """Format time remaining until target time"""
    now = datetime.now()
    if target_time <= now:
        return "maintenant"
    
    delta = target_time - now
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def truncate_field_value(text: str, max_length: int = 1000) -> str:
    """Tronquer un texte pour éviter les erreurs d'embed Discord"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def safe_embed_field(embed, name: str, value: str, inline: bool = False):
    """Ajouter un field à un embed en vérifiant la longueur"""
    if len(value) > 1024:
        value = truncate_field_value(value, 1020)
    if len(name) > 256:
        name = truncate_field_value(name, 252)
    embed.add_field(name=name, value=value, inline=inline)
