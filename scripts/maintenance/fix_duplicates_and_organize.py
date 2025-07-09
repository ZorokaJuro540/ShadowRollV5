"""
Fix character duplicates and organize database properly
Remove all duplicates and organize characters by anime series
"""

import aiosqlite
import asyncio

async def fix_database_duplicates():
    """Remove all duplicate characters and organize database"""
    db = await aiosqlite.connect("shadow_roll.db")
    
    print("🔍 Analyzing current database...")
    
    # Get all characters with their details
    cursor = await db.execute("""
        SELECT id, name, anime, rarity, value, image_url 
        FROM characters 
        ORDER BY name, id
    """)
    all_characters = await cursor.fetchall()
    
    print(f"📊 Total characters in database: {len(all_characters)}")
    
    # Find duplicates by name
    seen_names = set()
    duplicates_found = []
    unique_characters = []
    
    for char in all_characters:
        char_id, name, anime, rarity, value, image_url = char
        
        if name in seen_names:
            duplicates_found.append(char)
            print(f"❌ Duplicate found: {name} (ID: {char_id})")
        else:
            seen_names.add(name)
            unique_characters.append(char)
    
    print(f"❌ Found {len(duplicates_found)} duplicate characters")
    print(f"✅ Keeping {len(unique_characters)} unique characters")
    
    if duplicates_found:
        print("\n🧹 Removing duplicates...")
        
        # Get IDs of duplicates to remove
        duplicate_ids = [str(char[0]) for char in duplicates_found]
        
        # Remove duplicates from inventory first (foreign key constraint)
        for dup_id in duplicate_ids:
            await db.execute("DELETE FROM inventory WHERE character_id = ?", (dup_id,))
        
        # Remove duplicate characters
        placeholders = ','.join(['?' for _ in duplicate_ids])
        await db.execute(f"DELETE FROM characters WHERE id IN ({placeholders})", duplicate_ids)
        
        await db.commit()
        print(f"✅ Removed {len(duplicates_found)} duplicate characters")
    
    # Verify cleanup
    cursor = await db.execute("SELECT COUNT(*) FROM characters")
    final_count = (await cursor.fetchone())[0]
    
    cursor = await db.execute("SELECT COUNT(DISTINCT name) FROM characters")
    unique_count = (await cursor.fetchone())[0]
    
    print(f"\n📊 Final count: {final_count} characters")
    print(f"📊 Unique names: {unique_count}")
    
    if final_count == unique_count:
        print("✅ Database is now clean - no duplicates!")
    else:
        print("❌ Still have issues - manual check needed")
    
    # Display organized list by anime
    print("\n📚 Characters organized by anime:")
    cursor = await db.execute("""
        SELECT anime, COUNT(*) as count
        FROM characters 
        GROUP BY anime 
        ORDER BY anime
    """)
    anime_counts = await cursor.fetchall()
    
    for anime, count in anime_counts:
        print(f"  🎭 {anime}: {count} characters")
    
    await db.close()
    print("\n✅ Database cleanup completed!")

if __name__ == "__main__":
    asyncio.run(fix_database_duplicates())