"""
Achievement Fix Script for Shadow Roll Bot
Retroactively awards achievements to players who should have already earned them
"""

import asyncio
import aiosqlite
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_achievements():
    """Fix achievement system by awarding missing achievements"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Get all players
        cursor = await db.execute("SELECT user_id, username, total_rerolls, coins FROM players")
        players = await cursor.fetchall()
        
        logger.info(f"Processing {len(players)} players...")
        
        for user_id, username, total_rerolls, coins in players:
            logger.info(f"Processing player {username} (ID: {user_id})")
            
            # Get player's inventory stats
            inventory_cursor = await db.execute("""
                SELECT COUNT(DISTINCT character_id) as unique_characters,
                       COUNT(*) as total_items
                FROM inventory 
                WHERE user_id = ?
            """, (user_id,))
            inventory_stats = await inventory_cursor.fetchone()
            unique_characters = inventory_stats[0] if inventory_stats else 0
            
            # Get player's rarity counts
            rarity_cursor = await db.execute("""
                SELECT c.rarity, COUNT(*) as count
                FROM inventory i
                JOIN characters c ON i.character_id = c.id
                WHERE i.user_id = ?
                GROUP BY c.rarity
            """, (user_id,))
            rarity_counts = dict(await rarity_cursor.fetchall())
            
            # Check and award reroll achievements
            reroll_achievements = [
                (1, 1),   # Premier Pas
                (2, 10),  # Invocateur Novice
                (3, 50),  # Invocateur Expérimenté
                (4, 100), # Maître Invocateur
            ]
            
            for achievement_id, required_rerolls in reroll_achievements:
                if total_rerolls >= required_rerolls:
                    await award_if_not_exists(db, user_id, achievement_id)
            
            # Check and award collection achievements
            collection_achievements = [
                (5, 10),  # Collectionneur
                (6, 25),  # Grand Collectionneur
                (7, 40),  # Maître Collectionneur
            ]
            
            for achievement_id, required_characters in collection_achievements:
                if unique_characters >= required_characters:
                    await award_if_not_exists(db, user_id, achievement_id)
            
            # Check and award rarity achievements
            rarity_achievements = {
                'Epic': 8,      # Premier Épique
                'Legendary': 9, # Premier Légendaire  
                'Mythical': 10  # Premier Mythique
            }
            
            for rarity, achievement_id in rarity_achievements.items():
                if rarity_counts.get(rarity, 0) > 0:
                    await award_if_not_exists(db, user_id, achievement_id)
            
            # Check and award coin achievements
            coin_achievements = [
                (11, 5000),  # Riche
                (12, 10000), # Très Riche
            ]
            
            for achievement_id, required_coins in coin_achievements:
                if coins >= required_coins:
                    await award_if_not_exists(db, user_id, achievement_id)
        
        await db.commit()
        logger.info("Achievement fix completed!")

async def award_if_not_exists(db, user_id: int, achievement_id: int):
    """Award achievement if player doesn't already have it"""
    # Check if already earned
    cursor = await db.execute(
        "SELECT id FROM player_achievements WHERE user_id = ? AND achievement_id = ?",
        (user_id, achievement_id)
    )
    
    if not await cursor.fetchone():
        # Award the achievement
        current_time = datetime.now().isoformat()
        await db.execute(
            "INSERT INTO player_achievements (user_id, achievement_id, earned_at) VALUES (?, ?, ?)",
            (user_id, achievement_id, current_time)
        )
        
        # Get achievement name for logging
        name_cursor = await db.execute(
            "SELECT achievement_name FROM achievements WHERE id = ?",
            (achievement_id,)
        )
        achievement_name = await name_cursor.fetchone()
        if achievement_name:
            logger.info(f"Awarded '{achievement_name[0]}' to user {user_id}")

if __name__ == "__main__":
    asyncio.run(fix_achievements())