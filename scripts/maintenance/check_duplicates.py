#!/usr/bin/env python3
"""
Script to check and clean duplicate characters in the Shadow Roll database
"""
import asyncio
import aiosqlite

async def check_and_clean_duplicates():
    """Check for duplicate characters and clean them up"""
    db = await aiosqlite.connect("shadow_roll.db")
    
    # First, check for duplicates
    print("🔍 Checking for duplicate characters...")
    cursor = await db.execute("""
        SELECT name, COUNT(*) as count 
        FROM characters 
        GROUP BY name 
        HAVING COUNT(*) > 1 
        ORDER BY count DESC
    """)
    duplicates = await cursor.fetchall()
    
    if duplicates:
        print(f"❌ Found {len(duplicates)} characters with duplicates:")
        for name, count in duplicates:
            print(f"  - {name}: {count} copies")
        
        # Clean up duplicates - keep only the first occurrence of each character
        print("\n🧹 Cleaning up duplicates...")
        for name, count in duplicates:
            # Get all IDs for this character name
            cursor = await db.execute("""
                SELECT id FROM characters 
                WHERE name = ? 
                ORDER BY id ASC
            """, (name,))
            ids = await cursor.fetchall()
            
            # Keep the first ID, delete the rest
            if len(ids) > 1:
                ids_to_delete = [str(id[0]) for id in ids[1:]]
                placeholders = ','.join(['?' for _ in ids_to_delete])
                
                # Delete duplicate character records
                await db.execute(f"""
                    DELETE FROM characters 
                    WHERE id IN ({placeholders})
                """, ids_to_delete)
                
                print(f"  ✓ Removed {len(ids_to_delete)} duplicate(s) of {name}")
        
        await db.commit()
        print("✅ Duplicate cleanup completed!")
        
    else:
        print("✅ No duplicate characters found!")
    
    # Verify cleanup
    print("\n🔍 Verifying cleanup...")
    cursor = await db.execute("SELECT COUNT(*) FROM characters")
    total_count = await cursor.fetchone()
    
    cursor = await db.execute("SELECT COUNT(DISTINCT name) FROM characters")
    unique_count = await cursor.fetchone()
    
    print(f"📊 Total characters: {total_count[0]}")
    print(f"📊 Unique characters: {unique_count[0]}")
    
    if total_count[0] == unique_count[0]:
        print("✅ All characters are unique!")
    else:
        print("❌ Still have duplicates - manual intervention needed")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(check_and_clean_duplicates())