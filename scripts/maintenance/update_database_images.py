"""
Update database with resized image paths
"""
import asyncio
import aiosqlite
import os

async def update_database_with_resized_images():
    """Update character image URLs in database to point to resized local images"""
    resized_dir = "resized_images"
    
    if not os.path.exists(resized_dir):
        print("❌ Dossier resized_images introuvable")
        return
    
    # Get list of resized images
    resized_files = [f for f in os.listdir(resized_dir) if f.endswith('.jpg')]
    print(f"📁 {len(resized_files)} images redimensionnées trouvées")
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        updated_count = 0
        
        for filename in resized_files:
            # Extract character name from filename (remove _1920x1080.jpg)
            char_name = filename.replace('_1920x1080.jpg', '')
            
            # Update database
            await db.execute("""
                UPDATE characters 
                SET image_url = ? 
                WHERE name = ?
            """, (f"resized_images/{filename}", char_name))
            
            updated_count += 1
            print(f"✅ Mis à jour: {char_name}")
        
        await db.commit()
        print(f"📊 {updated_count} personnages mis à jour dans la base")

if __name__ == "__main__":
    asyncio.run(update_database_with_resized_images())