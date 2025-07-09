"""
Cache system for Shadow Roll Bot
Improves performance by caching frequently accessed data
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BotCache:
    """High-performance cache system for Shadow Roll Bot"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl: Dict[str, float] = {}  # Time to live for each cache key
        self._hit_count = 0
        self._miss_count = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            self._miss_count += 1
            return None
            
        # Check if expired
        if key in self._ttl and time.time() > self._ttl[key]:
            del self._cache[key]
            del self._ttl[key]
            self._miss_count += 1
            return None
            
        self._hit_count += 1
        return self._cache[key]['value']
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with optional TTL"""
        self._cache[key] = {
            'value': value,
            'created_at': time.time()
        }
        
        if ttl_seconds > 0:
            self._ttl[key] = time.time() + ttl_seconds
    
    def invalidate(self, key: str) -> None:
        """Remove specific key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Remove all keys matching pattern"""
        keys_to_remove = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_remove:
            self.invalidate(key)
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._ttl.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hit_count': self._hit_count,
            'miss_count': self._miss_count,
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_size': len(self._cache),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> str:
        """Estimate cache memory usage"""
        import sys
        total_size = sys.getsizeof(self._cache) + sys.getsizeof(self._ttl)
        
        for key, value in self._cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        
        if total_size < 1024:
            return f"{total_size} B"
        elif total_size < 1024 * 1024:
            return f"{total_size / 1024:.2f} KB"
        else:
            return f"{total_size / (1024 * 1024):.2f} MB"

# Global cache instance
bot_cache = BotCache()

class CachedDatabaseMixin:
    """Mixin to add caching capabilities to database operations"""
    
    async def get_player_cached(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player data with caching"""
        cache_key = f"player_{user_id}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        # Fetch from database
        cursor = await self.db.execute(
            "SELECT user_id, username, coins, total_rerolls, last_reroll, last_daily, is_banned FROM players WHERE user_id = ?",
            (user_id,)
        )
        player_data = await cursor.fetchone()
        
        if player_data:
            player_dict = {
                'user_id': player_data[0],
                'username': player_data[1],
                'coins': player_data[2],
                'total_rerolls': player_data[3],
                'last_reroll': player_data[4],
                'last_daily': player_data[5],
                'is_banned': player_data[6]
            }
            # Cache for 2 minutes
            bot_cache.set(cache_key, player_dict, 120)
            return player_dict
        
        return None
    
    async def get_character_cached(self, character_id: int) -> Optional[Dict[str, Any]]:
        """Get character data with caching"""
        cache_key = f"character_{character_id}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        # Fetch from database
        cursor = await self.db.execute(
            "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE id = ?",
            (character_id,)
        )
        char_data = await cursor.fetchone()
        
        if char_data:
            char_dict = {
                'id': char_data[0],
                'name': char_data[1],
                'anime': char_data[2],
                'rarity': char_data[3],
                'value': char_data[4],
                'image_url': char_data[5]
            }
            # Cache for 10 minutes (characters change less frequently)
            bot_cache.set(cache_key, char_dict, 600)
            return char_dict
        
        return None
    
    async def get_inventory_cached(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user inventory with caching"""
        cache_key = f"inventory_{user_id}_{limit}_{offset}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        # Fetch from database with optimized query
        cursor = await self.db.execute("""
            SELECT i.character_id, i.count, c.name, c.anime, c.rarity, c.value, c.image_url
            FROM inventory i
            JOIN characters c ON i.character_id = c.id
            WHERE i.user_id = ?
            ORDER BY c.rarity DESC, c.value DESC, c.name
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        inventory_data = await cursor.fetchall()
        inventory_list = []
        
        for row in inventory_data:
            inventory_list.append({
                'character_id': row[0],
                'count': row[1],
                'name': row[2],
                'anime': row[3],
                'rarity': row[4],
                'value': row[5],
                'image_url': row[6]
            })
        
        # Cache for 1 minute (inventory changes frequently)
        bot_cache.set(cache_key, inventory_list, 60)
        return inventory_list
    
    async def invalidate_player_cache(self, user_id: int) -> None:
        """Invalidate all cache entries for a specific player"""
        bot_cache.invalidate(f"player_{user_id}")
        bot_cache.invalidate_pattern(f"inventory_{user_id}")
        bot_cache.invalidate_pattern(f"achievements_{user_id}")
    
    async def invalidate_character_cache(self, character_id: int) -> None:
        """Invalidate cache for a specific character"""
        bot_cache.invalidate(f"character_{character_id}")

def cache_performance_monitor():
    """Monitor cache performance and log statistics"""
    stats = bot_cache.get_stats()
    logger.info(f"Cache Stats - Hits: {stats['hit_count']}, Misses: {stats['miss_count']}, Hit Rate: {stats['hit_rate']}, Size: {stats['cache_size']}, Memory: {stats['memory_usage']}")

# Utility functions for cache management
async def warm_cache_characters():
    """Preload frequently used characters into cache"""
    # This would be called during bot startup
    pass

async def cleanup_expired_cache():
    """Clean up expired cache entries"""
    # This could be called periodically
    current_time = time.time()
    expired_keys = [key for key, ttl in bot_cache._ttl.items() if current_time > ttl]
    
    for key in expired_keys:
        bot_cache.invalidate(key)
    
    if expired_keys:
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")