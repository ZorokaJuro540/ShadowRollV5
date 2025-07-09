#!/usr/bin/env python3
"""
Debug script to check a specific user's equipment situation
"""
import asyncio
import logging
from core.database import DatabaseManager

logger = logging.getLogger(__name__)

async def debug_user_equipment():
    """Debug equipment for a specific user"""
    print("🔍 Debugging user equipment...")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # Get all users to see who has equipment issues
    cursor = await db_manager.db.execute("""
        SELECT DISTINCT user_id FROM players ORDER BY user_id
    """)
    users = await cursor.fetchall()
    
    print(f"Found {len(users)} users in database")
    
    for user_tuple in users:
        user_id = user_tuple[0]
        print(f"\n--- User {user_id} ---")
        
        # Check available characters
        available_chars = await db_manager.get_equippable_characters(user_id)
        print(f"Available for equipping: {len(available_chars)}")
        
        # Check equipped characters
        equipped_chars = await db_manager.get_equipped_characters(user_id)
        print(f"Currently equipped: {len(equipped_chars)}")
        
        # Check total Titan/Fusion/Secret characters
        cursor = await db_manager.db.execute("""
            SELECT COUNT(*) FROM inventory i
            JOIN characters c ON i.character_id = c.id
            WHERE i.user_id = ? AND c.rarity IN ('Titan', 'Fusion', 'Secret')
        """, (user_id,))
        total_equippable = await cursor.fetchone()
        print(f"Total Titan/Fusion/Secret owned: {total_equippable[0]}")
        
        # Show details for users with equipment
        if len(equipped_chars) > 0:
            print("Equipped characters:")
            for char in equipped_chars:
                print(f"  - {char['name']} ({char['rarity']}) - Slot: {char['slot_number']}")
        
        if len(available_chars) > 0:
            print("Available characters:")
            for char in available_chars[:3]:  # Show first 3
                print(f"  - {char['name']} ({char['rarity']}) - ID: {char['inventory_id']}")
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(debug_user_equipment())