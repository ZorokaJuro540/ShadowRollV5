"""
Award coin rewards for newly earned achievements
"""

import asyncio
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def award_achievement_coins():
    """Award coin rewards for all earned achievements"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Get all player achievements with their reward coins
        cursor = await db.execute("""
            SELECT pa.user_id, pa.achievement_id, a.reward_coins, a.achievement_name, p.username
            FROM player_achievements pa
            JOIN achievements a ON pa.achievement_id = a.id
            JOIN players p ON pa.user_id = p.user_id
            WHERE a.reward_coins > 0
        """)
        
        achievements_data = await cursor.fetchall()
        
        # Group by user_id to calculate total rewards per player
        user_rewards = {}
        for user_id, achievement_id, reward_coins, achievement_name, username in achievements_data:
            if user_id not in user_rewards:
                user_rewards[user_id] = {'username': username, 'total_coins': 0, 'achievements': []}
            user_rewards[user_id]['total_coins'] += reward_coins
            user_rewards[user_id]['achievements'].append((achievement_name, reward_coins))
        
        # Award coins to each player
        for user_id, data in user_rewards.items():
            await db.execute(
                "UPDATE players SET coins = coins + ? WHERE user_id = ?",
                (data['total_coins'], user_id)
            )
            
            logger.info(f"Awarded {data['total_coins']} coins to {data['username']} for {len(data['achievements'])} achievements")
            for achievement_name, coins in data['achievements']:
                logger.info(f"  - {achievement_name}: +{coins} coins")
        
        await db.commit()
        logger.info(f"Coin rewards awarded to {len(user_rewards)} players!")

if __name__ == "__main__":
    asyncio.run(award_achievement_coins())