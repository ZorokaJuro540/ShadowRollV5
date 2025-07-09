"""
Achievement system for Shadow Roll Bot
Manages player achievements and progress tracking
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime

from core.config import BotConfig
from core.models import Achievement

logger = logging.getLogger(__name__)

class AchievementManager:
    """Manages player achievements and progress tracking"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def check_and_award_achievements(self, user_id: int, trigger_type: str, **kwargs) -> List[Achievement]:
        """Check and award achievements based on trigger type"""
        new_achievements = []
        
        try:
            # Get player data
            player = await self.db.get_or_create_player(user_id, kwargs.get('username', f'User_{user_id}'))
            inventory_stats = await self.db.get_inventory_stats(user_id)
            
            # Check different achievement types
            if trigger_type == 'reroll':
                new_achievements.extend(await self._check_reroll_achievements(user_id, player))
            
            elif trigger_type == 'character_obtained':
                character_rarity = kwargs.get('character_rarity')
                if character_rarity:
                    new_achievements.extend(await self._check_rarity_achievements(user_id, character_rarity))
            
            elif trigger_type == 'coins_updated':
                new_achievements.extend(await self._check_coin_achievements(user_id, player.coins))
            
            # Check collection-based achievements
            new_achievements.extend(await self._check_collection_achievements(user_id, inventory_stats))
            
            # Award coin rewards for achievements
            total_reward = 0
            for achievement in new_achievements:
                if achievement.reward_coins > 0:
                    total_reward += achievement.reward_coins
            
            if total_reward > 0:
                # Apply series and equipment coin bonuses to achievement rewards
                set_bonuses = await self.db.get_active_set_bonuses(user_id)
                coin_multiplier = set_bonuses.get('coin_boost', 1.0)
                reward_with_set_bonus = int(total_reward * coin_multiplier)
                final_reward = await self.db.apply_equipment_bonuses_to_coins(user_id, reward_with_set_bonus)
                
                new_coins = player.coins + final_reward
                await self.db.update_player_coins(user_id, new_coins)
            
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}")
        
        return new_achievements
    
    async def _check_reroll_achievements(self, user_id: int, player) -> List[Achievement]:
        """Check reroll-based achievements"""
        achievements = []
        reroll_count = player.total_rerolls
        
        # Achievement IDs for reroll-based achievements
        achievement_checks = [
            (1, 1),   # Premier Pas
            (2, 10),  # Invocateur Novice
            (3, 50),  # Invocateur Expérimenté
            (4, 100), # Maître Invocateur
        ]
        
        for achievement_id, required_count in achievement_checks:
            if reroll_count >= required_count:
                success = await self.db.award_achievement(user_id, achievement_id)
                if success:
                    # Get achievement details
                    cursor = await self.db.db.execute(
                        "SELECT achievement_name, achievement_description, reward_coins FROM achievements WHERE id = ?",
                        (achievement_id,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        achievement = Achievement(
                            id=achievement_id,
                            name=row[0],
                            description=row[1],
                            requirement_type='rerolls',
                            requirement_value=required_count,
                            reward_coins=row[2]
                        )
                        achievements.append(achievement)
        
        return achievements
    
    async def _check_rarity_achievements(self, user_id: int, rarity: str) -> List[Achievement]:
        """Check rarity-based achievements"""
        achievements = []
        
        # Achievement IDs for rarity-based achievements
        rarity_achievements = {
            'Epic': 8,      # Premier Épique
            'Legendary': 9, # Premier Légendaire  
            'Mythic': 10, # Premier Mythique
            'Titan': 13,    # Premier Titan
            'Fusion': 14       # Premier Fusion
        }
        
        achievement_id = rarity_achievements.get(rarity)
        if achievement_id:
            success = await self.db.award_achievement(user_id, achievement_id)
            if success:
                # Get achievement details
                cursor = await self.db.db.execute(
                    "SELECT achievement_name, achievement_description, reward_coins FROM achievements WHERE id = ?",
                    (achievement_id,)
                )
                row = await cursor.fetchone()
                if row:
                    achievement = Achievement(
                        id=achievement_id,
                        name=row[0],
                        description=row[1],
                        requirement_type='rarity',
                        requirement_value=rarity,
                        reward_coins=row[2]
                    )
                    achievements.append(achievement)
        
        return achievements
    
    async def _check_coin_achievements(self, user_id: int, coin_amount: int) -> List[Achievement]:
        """Check coin-based achievements"""
        achievements = []
        
        # Achievement IDs for coin-based achievements
        coin_achievements = [
            (11, 5000),  # Riche
            (12, 10000), # Très Riche
        ]
        
        for achievement_id, required_coins in coin_achievements:
            if coin_amount >= required_coins:
                success = await self.db.award_achievement(user_id, achievement_id)
                if success:
                    # Get achievement details
                    cursor = await self.db.db.execute(
                        "SELECT achievement_name, achievement_description, reward_coins FROM achievements WHERE id = ?",
                        (achievement_id,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        achievement = Achievement(
                            id=achievement_id,
                            name=row[0],
                            description=row[1],
                            requirement_type='coins',
                            requirement_value=required_coins,
                            reward_coins=row[2]
                        )
                        achievements.append(achievement)
        
        return achievements
    
    async def _check_collection_achievements(self, user_id: int, inventory_stats: Dict) -> List[Achievement]:
        """Check collection-based achievements"""
        achievements = []
        unique_count = inventory_stats.get('unique_characters', 0)
        
        # Achievement IDs for collection-based achievements
        collection_achievements = [
            (5, 10),  # Collectionneur
            (6, 25),  # Grand Collectionneur
            (7, 40),  # Maître Collectionneur
        ]
        
        for achievement_id, required_count in collection_achievements:
            if unique_count >= required_count:
                success = await self.db.award_achievement(user_id, achievement_id)
                if success:
                    # Get achievement details
                    cursor = await self.db.db.execute(
                        "SELECT achievement_name, achievement_description, reward_coins FROM achievements WHERE id = ?",
                        (achievement_id,)
                    )
                    row = await cursor.fetchone()
                    if row:
                        achievement = Achievement(
                            id=achievement_id,
                            name=row[0],
                            description=row[1],
                            requirement_type='characters',
                            requirement_value=required_count,
                            reward_coins=row[2]
                        )
                        achievements.append(achievement)
        
        return achievements
    
    async def get_player_achievements(self, user_id: int) -> List[Dict]:
        """Get all achievements for a player"""
        achievement_keys = await self.db.get_player_achievements(user_id)
        
        achievements = []
        for key in achievement_keys:
            achievement_data = BotConfig.ACHIEVEMENTS.get(key, {})
            achievements.append({
                'key': key,
                'name': achievement_data.get('name', 'Unknown'),
                'description': achievement_data.get('description', 'No description'),
                'reward': achievement_data.get('reward', 0)
            })
        
        return achievements
    
    async def get_available_achievements(self, user_id: int) -> List[Dict]:
        """Get achievements player hasn't earned yet"""
        earned_keys = await self.db.get_player_achievements(user_id)
        earned_set = set(earned_keys)
        
        available = []
        for key, data in BotConfig.ACHIEVEMENTS.items():
            if key not in earned_set:
                available.append({
                    'key': key,
                    'name': data.get('name', 'Unknown'),
                    'description': data.get('description', 'No description'),
                    'reward': data.get('reward', 0)
                })
        
        return available
    
    async def get_achievement_progress(self, user_id: int) -> Dict:
        """Get achievement progress for player"""
        player = await self.db.get_or_create_player(user_id, f'User_{user_id}')
        inventory_stats = await self.db.get_inventory_stats(user_id)
        earned_achievements = await self.db.get_player_achievements(user_id)
        
        progress = {
            'earned_count': len(earned_achievements),
            'total_count': len(BotConfig.ACHIEVEMENTS),
            'reroll_count': player.total_rerolls,
            'unique_characters': inventory_stats.get('unique_characters', 0),
            'coins': player.coins
        }
        
        return progress