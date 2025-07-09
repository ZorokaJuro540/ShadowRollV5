"""
Image Resizer for Shadow Roll Bot
Automatically resize character images to 1920x1080 while preserving aspect ratio
"""
import asyncio
import aiohttp
import aiosqlite
from PIL import Image, ImageOps
import io
import os
import logging

logger = logging.getLogger(__name__)

class ImageResizer:
    def __init__(self, target_width=1920, target_height=1080):
        self.target_width = target_width
        self.target_height = target_height
        self.output_dir = "resized_images"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def download_image(self, url: str) -> bytes:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to download image: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")
            return None
    
    def resize_image_smart(self, image_data: bytes, character_name: str) -> str:
        """
        Resize image to target dimensions while preserving aspect ratio
        Returns the path to the resized image
        """
        try:
            # Open image from bytes
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Calculate scaling to fit within target dimensions
                img_ratio = img.width / img.height
                target_ratio = self.target_width / self.target_height
                
                if img_ratio > target_ratio:
                    # Image is wider than target ratio
                    new_width = self.target_width
                    new_height = int(self.target_width / img_ratio)
                else:
                    # Image is taller than target ratio
                    new_height = self.target_height
                    new_width = int(self.target_height * img_ratio)
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Create final image with target dimensions (dark background for Shadow theme)
                final_img = Image.new('RGB', (self.target_width, self.target_height), (20, 20, 30))
                
                # Center the resized image
                paste_x = (self.target_width - new_width) // 2
                paste_y = (self.target_height - new_height) // 2
                final_img.paste(resized_img, (paste_x, paste_y))
                
                # Save image
                safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_path = os.path.join(self.output_dir, f"{safe_name}_{self.target_width}x{self.target_height}.jpg")
                final_img.save(output_path, 'JPEG', quality=90, optimize=True)
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error resizing image for {character_name}: {e}")
            return None
    
    async def process_character_image(self, character_id: int, character_name: str, image_url: str) -> str:
        """Process a single character image"""
        if not image_url or image_url == "":
            logger.warning(f"No image URL for {character_name}")
            return None
            
        print(f"📥 Téléchargement: {character_name}")
        image_data = await self.download_image(image_url)
        
        if not image_data:
            print(f"❌ Échec téléchargement: {character_name}")
            return None
        
        print(f"🖼️ Redimensionnement: {character_name}")
        resized_path = self.resize_image_smart(image_data, character_name)
        
        if resized_path:
            print(f"✅ Terminé: {character_name} -> {resized_path}")
            return resized_path
        else:
            print(f"❌ Échec redimensionnement: {character_name}")
            return None
    
    async def resize_all_character_images(self):
        """Resize all character images from database"""
        try:
            async with aiosqlite.connect('shadow_roll.db') as db:
                cursor = await db.execute("""
                    SELECT id, name, image_url 
                    FROM characters 
                    WHERE image_url IS NOT NULL AND image_url != ''
                    ORDER BY name
                """)
                characters = await cursor.fetchall()
                
                if not characters:
                    print("❌ Aucun personnage avec image trouvé")
                    return
                
                print(f"🎯 {len(characters)} personnages à traiter")
                print(f"📏 Taille cible: {self.target_width}x{self.target_height}")
                print("=" * 60)
                
                successful = 0
                failed = 0
                
                for char_id, char_name, image_url in characters:
                    result = await self.process_character_image(char_id, char_name, image_url)
                    if result:
                        successful += 1
                    else:
                        failed += 1
                    
                    # Small delay to avoid overwhelming servers
                    await asyncio.sleep(0.5)
                
                print("=" * 60)
                print(f"📊 Résultats:")
                print(f"  ✅ Succès: {successful}")
                print(f"  ❌ Échecs: {failed}")
                print(f"  📁 Dossier: {self.output_dir}")
                
        except Exception as e:
            logger.error(f"Error in resize_all_character_images: {e}")
            print(f"❌ Erreur: {e}")

async def main():
    """Main function to resize all images"""
    print("🌌 Shadow Roll Image Resizer")
    print("Redimensionnement automatique en 1920x1080")
    print()
    
    resizer = ImageResizer()
    await resizer.resize_all_character_images()

if __name__ == "__main__":
    asyncio.run(main())