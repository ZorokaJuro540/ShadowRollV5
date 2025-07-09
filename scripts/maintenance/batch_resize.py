"""
Batch image resizer with better rate limiting and retry logic
"""
import asyncio
import aiohttp
import aiosqlite
from PIL import Image, ImageOps
import io
import os
import logging
from datetime import datetime

class BatchImageResizer:
    def __init__(self, target_width=1920, target_height=1080, batch_size=5):
        self.target_width = target_width
        self.target_height = target_height
        self.batch_size = batch_size
        self.output_dir = "resized_images"
        self.delay_between_requests = 2  # 2 seconds between requests
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def download_and_resize_batch(self, characters_batch):
        """Process a batch of characters"""
        successful = 0
        failed = 0
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        ) as session:
            
            for char_id, char_name, image_url in characters_batch:
                try:
                    print(f"📥 Traitement: {char_name}")
                    
                    # Check if already processed
                    safe_name = "".join(c for c in char_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    output_path = os.path.join(self.output_dir, f"{safe_name}_1920x1080.jpg")
                    
                    if os.path.exists(output_path):
                        print(f"⏭️ Déjà traité: {char_name}")
                        successful += 1
                        continue
                    
                    # Download
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            
                            # Resize
                            if self.resize_image_smart(image_data, char_name):
                                print(f"✅ Succès: {char_name}")
                                successful += 1
                            else:
                                print(f"❌ Erreur redimensionnement: {char_name}")
                                failed += 1
                        else:
                            print(f"❌ Erreur téléchargement {response.status}: {char_name}")
                            failed += 1
                    
                    # Rate limiting
                    await asyncio.sleep(self.delay_between_requests)
                    
                except Exception as e:
                    print(f"❌ Erreur {char_name}: {str(e)[:50]}...")
                    failed += 1
        
        return successful, failed
    
    def resize_image_smart(self, image_data: bytes, character_name: str) -> bool:
        """Resize image to target dimensions while preserving aspect ratio"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate scaling
                img_ratio = img.width / img.height
                target_ratio = self.target_width / self.target_height
                
                if img_ratio > target_ratio:
                    new_width = self.target_width
                    new_height = int(self.target_width / img_ratio)
                else:
                    new_height = self.target_height
                    new_width = int(self.target_height * img_ratio)
                
                # Resize and center
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                final_img = Image.new('RGB', (self.target_width, self.target_height), (0, 0, 0))
                
                paste_x = (self.target_width - new_width) // 2
                paste_y = (self.target_height - new_height) // 2
                final_img.paste(resized_img, (paste_x, paste_y))
                
                # Save
                safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_path = os.path.join(self.output_dir, f"{safe_name}_1920x1080.jpg")
                final_img.save(output_path, 'JPEG', quality=90, optimize=True)
                
                return True
                
        except Exception as e:
            print(f"Erreur redimensionnement {character_name}: {e}")
            return False
    
    async def process_all_images(self):
        """Process all character images in batches"""
        async with aiosqlite.connect('shadow_roll.db') as db:
            cursor = await db.execute("""
                SELECT id, name, image_url 
                FROM characters 
                WHERE image_url IS NOT NULL 
                AND image_url != '' 
                AND image_url NOT LIKE 'resized_images/%'
                ORDER BY name
            """)
            characters = await cursor.fetchall()
        
        if not characters:
            print("✅ Toutes les images sont déjà traitées")
            return
        
        print(f"🎯 {len(characters)} personnages à traiter")
        print(f"📦 Traitement par lots de {self.batch_size}")
        print("=" * 60)
        
        total_successful = 0
        total_failed = 0
        
        # Process in batches
        for i in range(0, len(characters), self.batch_size):
            batch = characters[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(characters) + self.batch_size - 1) // self.batch_size
            
            print(f"📦 Lot {batch_num}/{total_batches} ({len(batch)} images)")
            
            successful, failed = await self.download_and_resize_batch(batch)
            total_successful += successful
            total_failed += failed
            
            # Longer pause between batches
            if i + self.batch_size < len(characters):
                print(f"⏳ Pause de 5 secondes...")
                await asyncio.sleep(5)
        
        print("=" * 60)
        print(f"📊 Résultats finaux:")
        print(f"  ✅ Succès: {total_successful}")
        print(f"  ❌ Échecs: {total_failed}")
        print(f"  📁 Dossier: {self.output_dir}")

async def main():
    print("🌌 Shadow Roll Batch Image Resizer")
    print("Redimensionnement par lots avec rate limiting")
    print()
    
    resizer = BatchImageResizer(batch_size=3)  # Smaller batches
    await resizer.process_all_images()

if __name__ == "__main__":
    asyncio.run(main())