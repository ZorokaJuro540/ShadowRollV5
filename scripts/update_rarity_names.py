#!/usr/bin/env python3
"""
Script to update rarity names in database
- Duo -> Fusion
- Mythical -> Mythic
"""
import asyncio
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_rarity_names():
    """Update rarity names in database"""
    try:
        async with aiosqlite.connect("shadow_roll.db") as db:
            # Update characters table
            cursor = await db.execute("UPDATE characters SET rarity = 'Fusion' WHERE rarity = 'Duo'")
            duo_updated = cursor.rowcount
            
            cursor = await db.execute("UPDATE characters SET rarity = 'Mythic' WHERE rarity = 'Mythical'")
            mythical_updated = cursor.rowcount
            
            # Update player_characters table if it exists
            try:
                cursor = await db.execute("UPDATE player_characters SET rarity = 'Fusion' WHERE rarity = 'Duo'")
                pc_duo_updated = cursor.rowcount
                
                cursor = await db.execute("UPDATE player_characters SET rarity = 'Mythic' WHERE rarity = 'Mythical'")
                pc_mythical_updated = cursor.rowcount
            except Exception as e:
                logger.warning(f"Could not update player_characters: {e}")
                pc_duo_updated = pc_mythical_updated = 0
            
            # Update any other tables with rarity references
            try:
                cursor = await db.execute("UPDATE character_hunts SET target_rarity = 'Fusion' WHERE target_rarity = 'Duo'")
                hunt_duo_updated = cursor.rowcount
                
                cursor = await db.execute("UPDATE character_hunts SET target_rarity = 'Mythic' WHERE target_rarity = 'Mythical'")
                hunt_mythical_updated = cursor.rowcount
            except Exception as e:
                logger.warning(f"Could not update character_hunts: {e}")
                hunt_duo_updated = hunt_mythical_updated = 0
            
            await db.commit()
            
            logger.info(f"Rarity names updated successfully:")
            logger.info(f"  Characters: {duo_updated} Duo->Fusion, {mythical_updated} Mythical->Mythic")
            logger.info(f"  Player Characters: {pc_duo_updated} Duo->Fusion, {pc_mythical_updated} Mythical->Mythic")
            logger.info(f"  Character Hunts: {hunt_duo_updated} Duo->Fusion, {hunt_mythical_updated} Mythical->Mythic")
            
    except Exception as e:
        logger.error(f"Error updating rarity names: {e}")

if __name__ == "__main__":
    asyncio.run(update_rarity_names())