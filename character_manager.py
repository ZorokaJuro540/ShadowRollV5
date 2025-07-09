"""
Gestionnaire Central de Personnages pour Shadow Roll Bot
Centralise tous les personnages et garantit la persistance des créations admin
"""

import aiosqlite
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class CharacterManager:
    """Gestionnaire centralisé pour tous les personnages du système"""
    
    def __init__(self, db_path: str = "shadow_roll.db"):
        self.db_path = db_path
        self.characters_file = "all_characters.json"
        
    async def initialize(self):
        """Initialiser le gestionnaire et synchroniser tous les personnages"""
        await self.sync_all_characters()
        
    async def sync_all_characters(self):
        """Synchroniser tous les personnages (base + admin) vers fichier JSON"""
        try:
            # Connecter à la base de données
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters ORDER BY anime, name"
                )
                db_characters = await cursor.fetchall()
            
            # Convertir en format dictionnaire
            all_characters = []
            for char in db_characters:
                character_data = {
                    "id": char[0],
                    "name": char[1],
                    "anime": char[2],
                    "rarity": char[3],
                    "value": char[4],
                    "image_url": char[5] or "",
                    "source": "database",
                    "created_at": datetime.now().isoformat()
                }
                all_characters.append(character_data)
            
            # Sauvegarder dans le fichier JSON
            characters_data = {
                "last_sync": datetime.now().isoformat(),
                "total_characters": len(all_characters),
                "characters": all_characters,
                "sync_info": {
                    "database_characters": len(all_characters),
                    "admin_created": len([c for c in all_characters if c.get("source") == "admin"]),
                    "base_characters": len([c for c in all_characters if c.get("source") == "database"])
                }
            }
            
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Synchronisation complète: {len(all_characters)} personnages sauvegardés")
            return all_characters
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation des personnages: {e}")
            return []
    
    async def add_admin_character(self, name: str, anime: str, rarity: str, value: int, image_url: str = "", admin_id: Optional[int] = None) -> bool:
        """Ajouter un personnage créé par admin et le sauvegarder définitivement"""
        try:
            # Ajouter à la base de données
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "INSERT INTO characters (name, anime, rarity, value, image_url) VALUES (?, ?, ?, ?, ?)",
                    (name, anime, rarity, value, image_url)
                )
                character_id = cursor.lastrowid or 0
                await db.commit()
            
            # Charger le fichier JSON existant
            try:
                with open(self.characters_file, 'r', encoding='utf-8') as f:
                    characters_data = json.load(f)
            except FileNotFoundError:
                characters_data = {
                    "last_sync": datetime.now().isoformat(),
                    "total_characters": 0,
                    "characters": [],
                    "sync_info": {
                        "database_characters": 0,
                        "admin_created": 0,
                        "base_characters": 0
                    }
                }
            
            # Ajouter le nouveau personnage
            new_character = {
                "id": character_id,
                "name": name,
                "anime": anime,
                "rarity": rarity,
                "value": value,
                "image_url": image_url,
                "source": "admin",
                "created_at": datetime.now().isoformat(),
                "created_by": admin_id or 0
            }
            
            characters_data["characters"].append(new_character)
            characters_data["total_characters"] = len(characters_data["characters"])
            characters_data["last_sync"] = datetime.now().isoformat()
            characters_data["sync_info"]["admin_created"] += 1
            
            # Sauvegarder
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Personnage admin ajouté: {name} ({anime}) - ID: {character_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du personnage admin: {e}")
            return False
    
    async def get_all_characters(self) -> List[Dict]:
        """Récupérer tous les personnages depuis le fichier JSON"""
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
            return characters_data.get("characters", [])
        except FileNotFoundError:
            # Synchroniser si le fichier n'existe pas
            return await self.sync_all_characters()
        except Exception as e:
            logger.error(f"Erreur lors de la lecture des personnages: {e}")
            return []
    
    async def get_characters_by_anime(self, anime: str) -> List[Dict]:
        """Récupérer tous les personnages d'un anime spécifique"""
        all_chars = await self.get_all_characters()
        return [char for char in all_chars if char["anime"].lower() == anime.lower()]
    
    async def get_characters_by_rarity(self, rarity: str) -> List[Dict]:
        """Récupérer tous les personnages d'une rareté spécifique"""
        all_chars = await self.get_all_characters()
        return [char for char in all_chars if char["rarity"].lower() == rarity.lower()]
    
    async def search_characters(self, search_term: str) -> List[Dict]:
        """Rechercher des personnages par nom"""
        all_chars = await self.get_all_characters()
        search_lower = search_term.lower()
        return [char for char in all_chars if search_lower in char["name"].lower()]
    
    async def get_character_by_id(self, character_id: int) -> Optional[Dict]:
        """Récupérer un personnage par son ID"""
        all_chars = await self.get_all_characters()
        for char in all_chars:
            if char["id"] == character_id:
                return char
        return None
    
    async def update_character_field(self, character_id: int, field: str, new_value) -> bool:
        """Mettre à jour un champ spécifique d'un personnage"""
        try:
            # Mettre à jour dans la base de données
            import aiosqlite
            async with aiosqlite.connect(self.db_path) as db:
                if field == "name":
                    await db.execute("UPDATE characters SET name = ? WHERE id = ?", (new_value, character_id))
                elif field == "anime":
                    await db.execute("UPDATE characters SET anime = ? WHERE id = ?", (new_value, character_id))
                elif field == "rarity":
                    await db.execute("UPDATE characters SET rarity = ? WHERE id = ?", (new_value, character_id))
                elif field == "value":
                    await db.execute("UPDATE characters SET value = ? WHERE id = ?", (new_value, character_id))
                elif field == "image_url":
                    await db.execute("UPDATE characters SET image_url = ? WHERE id = ?", (new_value, character_id))
                else:
                    return False
                
                await db.commit()
            
            # Resynchroniser le fichier JSON
            await self.sync_all_characters()
            
            logger.info(f"Character {character_id} field '{field}' updated to: {new_value}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du personnage {character_id}: {e}")
            return False
    
    async def update_character_image(self, character_id: int, new_image_url: str) -> bool:
        """Mettre à jour l'image d'un personnage"""
        try:
            # Mettre à jour en base de données
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE characters SET image_url = ? WHERE id = ?",
                    (new_image_url, character_id)
                )
                await db.commit()
            
            # Mettre à jour dans le fichier JSON
            try:
                with open(self.characters_file, 'r', encoding='utf-8') as f:
                    characters_data = json.load(f)
                
                for char in characters_data["characters"]:
                    if char["id"] == character_id:
                        char["image_url"] = new_image_url
                        char["last_updated"] = datetime.now().isoformat()
                        break
                
                characters_data["last_sync"] = datetime.now().isoformat()
                
                with open(self.characters_file, 'w', encoding='utf-8') as f:
                    json.dump(characters_data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Image mise à jour pour le personnage ID {character_id}")
                return True
                
            except Exception as e:
                logger.error(f"Erreur lors de la mise à jour du fichier JSON: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'image: {e}")
            return False
    
    async def get_statistics(self) -> Dict:
        """Obtenir des statistiques sur tous les personnages"""
        all_chars = await self.get_all_characters()
        
        stats = {
            "total_characters": len(all_chars),
            "by_anime": {},
            "by_rarity": {},
            "by_source": {"database": 0, "admin": 0},
            "with_images": 0,
            "without_images": 0
        }
        
        for char in all_chars:
            # Par anime
            anime = char["anime"]
            stats["by_anime"][anime] = stats["by_anime"].get(anime, 0) + 1
            
            # Par rareté
            rarity = char["rarity"]
            stats["by_rarity"][rarity] = stats["by_rarity"].get(rarity, 0) + 1
            
            # Par source
            source = char.get("source", "database")
            stats["by_source"][source] += 1
            
            # Images
            if char.get("image_url"):
                stats["with_images"] += 1
            else:
                stats["without_images"] += 1
        
        return stats
    
    async def backup_characters(self, backup_name: Optional[str] = None) -> str:
        """Créer une sauvegarde des personnages"""
        if not backup_name:
            backup_name = f"characters_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            all_chars = await self.get_all_characters()
            backup_data = {
                "backup_date": datetime.now().isoformat(),
                "total_characters": len(all_chars),
                "characters": all_chars
            }
            
            with open(backup_name, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Sauvegarde créée: {backup_name}")
            return backup_name
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
            return ""

# Fonction utilitaire pour l'intégration avec les commandes admin
async def setup_character_manager():
    """Initialiser et retourner le gestionnaire de personnages"""
    manager = CharacterManager()
    await manager.initialize()
    return manager

# Fonctions d'aide pour les commandes admin
async def add_character_with_persistence(name: str, anime: str, rarity: str, value: int, image_url: str = "", admin_id: Optional[int] = None):
    """Ajouter un personnage avec persistance garantie"""
    manager = CharacterManager()
    return await manager.add_admin_character(name, anime, rarity, value, image_url, admin_id)

async def get_all_persistent_characters():
    """Récupérer tous les personnages persistants"""
    manager = CharacterManager()
    return await manager.get_all_characters()

async def sync_characters_to_storage():
    """Synchroniser tous les personnages vers le stockage persistant"""
    manager = CharacterManager()
    return await manager.sync_all_characters()