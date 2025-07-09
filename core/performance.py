"""
Performance optimization module for Shadow Roll Bot
Handles query optimization, batch operations, and memory management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from core.cache import bot_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Optimizes database queries and bot performance"""
    
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self._query_cache = {}
        self._batch_operations = []
        
    async def optimize_inventory_query(self, user_id: int, page: int = 1, limit: int = 10) -> List[Dict]:
        """Optimized inventory query with smart caching"""
        cache_key = f"opt_inventory_{user_id}_{page}_{limit}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
            
        offset = (page - 1) * limit
        
        # Optimized query with pre-joined data
        cursor = await self.db_manager.db.execute("""
            SELECT 
                i.id, i.character_id, i.count, i.is_equipped, i.equipped_slot,
                c.name, c.anime, c.rarity, c.value, c.image_url
            FROM inventory i
            INNER JOIN characters c ON i.character_id = c.id
            WHERE i.user_id = ?
            ORDER BY 
                CASE c.rarity 
                    WHEN 'Secret' THEN 7
                    WHEN 'Fusion' THEN 6
                    WHEN 'Titan' THEN 5
                    WHEN 'Mythic' THEN 4
                    WHEN 'Legendary' THEN 3
                    WHEN 'Epic' THEN 2
                    WHEN 'Rare' THEN 1
                    ELSE 0
                END DESC,
                c.value DESC, c.name ASC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
        
        items = await cursor.fetchall()
        
        inventory = []
        for item in items:
            inventory.append({
                'id': item[0],
                'character_id': item[1],
                'count': item[2],
                'is_equipped': item[3],
                'equipped_slot': item[4],
                'name': item[5],
                'anime': item[6],
                'rarity': item[7],
                'value': item[8],
                'image_url': item[9]
            })
        
        # Cache for 60 seconds to balance freshness and performance
        bot_cache.set(cache_key, inventory, 60)
        return inventory
    
    async def batch_character_lookup(self, character_ids: List[int]) -> Dict[int, Dict]:
        """Batch lookup multiple characters efficiently"""
        cache_results = {}
        uncached_ids = []
        
        # Check cache first
        for char_id in character_ids:
            cache_key = f"character_{char_id}"
            cached_char = bot_cache.get(cache_key)
            if cached_char:
                cache_results[char_id] = cached_char
            else:
                uncached_ids.append(char_id)
        
        # Batch query for uncached characters
        if uncached_ids:
            placeholders = ','.join(['?' for _ in uncached_ids])
            cursor = await self.db_manager.db.execute(f"""
                SELECT id, name, anime, rarity, value, image_url
                FROM characters
                WHERE id IN ({placeholders})
            """, uncached_ids)
            
            rows = await cursor.fetchall()
            for row in rows:
                char_data = {
                    'id': row[0],
                    'name': row[1],
                    'anime': row[2],
                    'rarity': row[3],
                    'value': row[4],
                    'image_url': row[5]
                }
                cache_results[row[0]] = char_data
                # Cache individual characters for 10 minutes
                bot_cache.set(f"character_{row[0]}", char_data, 600)
        
        return cache_results
    
    async def optimize_player_data(self, user_id: int) -> Optional[Dict]:
        """Get player data with enhanced caching"""
        cache_key = f"opt_player_{user_id}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        # Single optimized query for all player data
        cursor = await self.db_manager.db.execute("""
            SELECT 
                p.user_id, p.username, p.coins, p.total_rerolls,
                p.last_reroll, p.last_daily, p.is_banned,
                COUNT(i.id) as total_characters,
                COUNT(DISTINCT i.character_id) as unique_characters,
                SUM(CASE WHEN i.is_equipped = 1 THEN 1 ELSE 0 END) as equipped_count
            FROM players p
            LEFT JOIN inventory i ON p.user_id = i.user_id
            WHERE p.user_id = ?
            GROUP BY p.user_id
        """, (user_id,))
        
        player_data = await cursor.fetchone()
        
        if player_data:
            result = {
                'user_id': player_data[0],
                'username': player_data[1],
                'coins': player_data[2],
                'total_rerolls': player_data[3],
                'last_reroll': player_data[4],
                'last_daily': player_data[5],
                'is_banned': player_data[6],
                'stats': {
                    'total_characters': player_data[7] or 0,
                    'unique_characters': player_data[8] or 0,
                    'equipped_count': player_data[9] or 0
                }
            }
            
            # Cache for 2 minutes
            bot_cache.set(cache_key, result, 120)
            return result
        
        return None
    
    async def get_leaderboard_optimized(self, category: str = 'coins', limit: int = 10) -> List[Dict]:
        """Optimized leaderboard query with caching"""
        cache_key = f"leaderboard_{category}_{limit}"
        cached_data = bot_cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        if category == 'coins':
            order_by = "p.coins DESC"
        elif category == 'characters':
            order_by = "character_count DESC"
        elif category == 'rerolls':
            order_by = "p.total_rerolls DESC"
        else:
            order_by = "p.coins DESC"
        
        cursor = await self.db_manager.db.execute(f"""
            SELECT 
                p.user_id, p.username, p.coins, p.total_rerolls,
                COUNT(i.id) as character_count,
                COUNT(DISTINCT i.character_id) as unique_count
            FROM players p
            LEFT JOIN inventory i ON p.user_id = i.user_id
            WHERE p.is_banned = 0
            GROUP BY p.user_id, p.username, p.coins, p.total_rerolls
            ORDER BY {order_by}
            LIMIT ?
        """, (limit,))
        
        leaderboard = []
        rank = 1
        
        async for row in cursor:
            leaderboard.append({
                'rank': rank,
                'user_id': row[0],
                'username': row[1],
                'coins': row[2],
                'total_rerolls': row[3],
                'character_count': row[4] or 0,
                'unique_count': row[5] or 0
            })
            rank += 1
        
        # Cache for 5 minutes
        bot_cache.set(cache_key, leaderboard, 300)
        return leaderboard
    
    async def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a user efficiently"""
        patterns_to_clear = [
            f"opt_player_{user_id}",
            f"player_{user_id}",
            f"opt_inventory_{user_id}",
            f"inventory_{user_id}",
            f"achievements_{user_id}",
            f"equipment_{user_id}"
        ]
        
        for pattern in patterns_to_clear:
            bot_cache.invalidate_pattern(pattern)
        
        # Also clear leaderboards since user data changed
        bot_cache.invalidate_pattern("leaderboard_")
    
    async def preload_frequently_used_data(self):
        """Preload frequently accessed data during bot startup"""
        try:
            # Preload top characters
            cursor = await self.db_manager.db.execute("""
                SELECT id, name, anime, rarity, value, image_url
                FROM characters
                WHERE rarity IN ('Mythic', 'Legendary', 'Epic', 'Titan', 'Fusion', 'Secret')
                ORDER BY rarity DESC, value DESC
                LIMIT 50
            """)
            
            chars = await cursor.fetchall()
            for char in chars:
                char_data = {
                    'id': char[0],
                    'name': char[1],
                    'anime': char[2],
                    'rarity': char[3],
                    'value': char[4],
                    'image_url': char[5]
                }
                bot_cache.set(f"character_{char[0]}", char_data, 3600)  # 1 hour
            
            logger.info(f"Preloaded {len(chars)} frequently used characters into cache")
            
        except Exception as e:
            logger.error(f"Error preloading data: {e}")
    
    async def cleanup_performance_data(self):
        """Clean up performance-related cache entries periodically"""
        # Clear old leaderboard cache
        bot_cache.invalidate_pattern("leaderboard_")
        
        # Clear expired inventory caches
        bot_cache.invalidate_pattern("opt_inventory_")
        
        logger.debug("Cleaned up performance cache data")

# Global performance optimizer instance
performance_optimizer = None

async def initialize_performance_optimizer(database_manager):
    """Initialize the global performance optimizer"""
    global performance_optimizer
    performance_optimizer = PerformanceOptimizer(database_manager)
    await performance_optimizer.preload_frequently_used_data()
    return performance_optimizer

async def get_performance_optimizer():
    """Get the global performance optimizer instance"""
    return performance_optimizer