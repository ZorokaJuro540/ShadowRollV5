#!/usr/bin/env python3
"""
Test script for the equipment system
Identifies and fixes equipment-related issues
"""
import asyncio
import logging
from core.database import DatabaseManager
from core.config import BotConfig

logger = logging.getLogger(__name__)

async def test_equipment_system():
    """Test the equipment system and fix any issues"""
    print("🔧 Testing equipment system...")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # Test user ID (replace with actual user ID for testing)
    test_user_id = 921428727307567115
    
    try:
        # Test 1: Get available characters for equipping
        print("\n1. Testing get_equippable_characters...")
        available_chars = await db_manager.get_equippable_characters(test_user_id)
        print(f"   Available characters for equipping: {len(available_chars)}")
        
        for char in available_chars[:3]:  # Show first 3
            print(f"   - {char['name']} ({char['rarity']}) - ID: {char['inventory_id']}")
        
        # Test 2: Get equipped characters
        print("\n2. Testing get_equipped_characters...")
        equipped_chars = await db_manager.get_equipped_characters(test_user_id)
        print(f"   Currently equipped: {len(equipped_chars)}")
        
        for char in equipped_chars:
            print(f"   - {char['name']} ({char['rarity']}) - Slot: {char['slot_number']}")
        
        # Test 3: Check equipped count
        print("\n3. Testing get_equipped_count...")
        equipped_count = await db_manager.get_equipped_count(test_user_id)
        print(f"   Equipped count: {equipped_count}")
        
        # Test 4: Check for duplicate values that might cause dropdown issues
        print("\n4. Checking for duplicate inventory IDs...")
        seen_ids = set()
        duplicates = []
        
        for char in available_chars:
            char_id = char['inventory_id']
            if char_id in seen_ids:
                duplicates.append(char_id)
            seen_ids.add(char_id)
        
        if duplicates:
            print(f"   ❌ Found duplicate inventory IDs: {duplicates}")
        else:
            print("   ✅ No duplicate inventory IDs found")
        
        # Test 5: Validate database structure
        print("\n5. Validating database structure...")
        cursor = await db_manager.db.execute("PRAGMA table_info(equipment)")
        equipment_columns = await cursor.fetchall()
        print("   Equipment table columns:")
        for col in equipment_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Test 6: Check for invalid equipment entries
        print("\n6. Checking for invalid equipment entries...")
        cursor = await db_manager.db.execute("""
            SELECT COUNT(*) FROM equipment e
            LEFT JOIN inventory i ON e.inventory_id = i.id
            WHERE i.id IS NULL
        """)
        invalid_count = await cursor.fetchone()
        print(f"   Invalid equipment entries: {invalid_count[0]}")
        
        # Test 7: Check character rarity distribution
        print("\n7. Character rarity distribution for equipment...")
        cursor = await db_manager.db.execute("""
            SELECT c.rarity, COUNT(*) as count
            FROM inventory i
            JOIN characters c ON i.character_id = c.id
            WHERE i.user_id = ? AND c.rarity IN ('Titan', 'Fusion', 'Secret')
            GROUP BY c.rarity
            ORDER BY count DESC
        """, (test_user_id,))
        
        rarity_counts = await cursor.fetchall()
        for rarity, count in rarity_counts:
            print(f"   - {rarity}: {count} characters")
        
        print("\n✅ Equipment system test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Equipment system test failed: {e}")
    
    finally:
        await db_manager.close()

async def fix_equipment_duplicates():
    """Fix duplicate equipment entries"""
    print("\n🔧 Fixing duplicate equipment entries...")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        # Remove duplicate equipment entries
        cursor = await db_manager.db.execute("""
            DELETE FROM equipment 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) 
                FROM equipment 
                GROUP BY user_id, inventory_id
            )
        """)
        
        deleted_count = cursor.rowcount
        await db_manager.db.commit()
        
        print(f"   ✅ Removed {deleted_count} duplicate equipment entries")
        
        # Clean up invalid equipment entries
        cursor = await db_manager.db.execute("""
            DELETE FROM equipment 
            WHERE inventory_id NOT IN (SELECT id FROM inventory)
        """)
        
        invalid_count = cursor.rowcount
        await db_manager.db.commit()
        
        print(f"   ✅ Removed {invalid_count} invalid equipment entries")
        
    except Exception as e:
        print(f"❌ Error fixing duplicates: {e}")
        logger.error(f"Failed to fix equipment duplicates: {e}")
    
    finally:
        await db_manager.close()

async def main():
    """Main test function"""
    await test_equipment_system()
    await fix_equipment_duplicates()

if __name__ == "__main__":
    asyncio.run(main())