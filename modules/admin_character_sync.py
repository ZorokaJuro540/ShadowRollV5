"""
Système de synchronisation des personnages admin avec le code
Assure que tous les personnages créés via commandes admin sont sauvegardés dans le code
"""

import asyncio
import logging
import os
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

class AdminCharacterSync:
    """Synchronise les personnages admin avec le fichier database.py"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.database_file_path = "core/database.py"
        
    async def sync_admin_characters_to_code(self):
        """Synchronise tous les personnages admin créés vers le code"""
        try:
            # Récupérer tous les personnages de la base de données
            cursor = await self.db.db.execute("""
                SELECT name, anime, rarity, value, image_url 
                FROM characters 
                ORDER BY anime, name
            """)
            all_characters = await cursor.fetchall()
            
            # Séparer les personnages de base des personnages personnalisés
            base_characters = self._get_base_characters()
            custom_characters = []
            
            for char in all_characters:
                name, anime, rarity, value, image_url = char
                if (name, anime) not in [(c[0], c[1]) for c in base_characters]:
                    custom_characters.append((name, anime, rarity, value, image_url or "https://i.imgur.com/example.jpg"))
            
            # Mettre à jour le fichier database.py
            await self._update_database_file(custom_characters)
            
            # Créer automatiquement les séries manquantes
            await self._create_missing_series(custom_characters)
            
            logger.info(f"Synchronisation terminée: {len(custom_characters)} personnages personnalisés")
            return len(custom_characters)
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation: {e}")
            return 0
    
    def _get_base_characters(self) -> List[Tuple[str, str]]:
        """Retourne la liste des personnages de base (nom, anime)"""
        return [
            # Naruto
            ("Naruto Uzumaki", "Naruto"), ("Sasuke Uchiha", "Naruto"), ("Sakura Haruno", "Naruto"),
            ("Kakashi Hatake", "Naruto"), ("Itachi Uchiha", "Naruto"), ("Madara Uchiha", "Naruto"),
            ("Hashirama Senju", "Naruto"), ("Minato Namikaze", "Naruto"), ("Jiraiya", "Naruto"),
            ("Tsunade", "Naruto"), ("Orochimaru", "Naruto"), ("Pain", "Naruto"), ("Gaara", "Naruto"),
            ("Rock Lee", "Naruto"), ("Neji Hyuga", "Naruto"), ("Hinata Hyuga", "Naruto"),
            ("Shikamaru Nara", "Naruto"), ("Choji Akimichi", "Naruto"), ("Ino Yamanaka", "Naruto"),
            ("Kiba Inuzuka", "Naruto"), ("Shino Aburame", "Naruto"), ("Tenten", "Naruto"),
            
            # One Piece
            ("Monkey D. Luffy", "One Piece"), ("Roronoa Zoro", "One Piece"), ("Nami", "One Piece"),
            ("Usopp", "One Piece"), ("Sanji", "One Piece"), ("Tony Tony Chopper", "One Piece"),
            ("Nico Robin", "One Piece"), ("Franky", "One Piece"), ("Brook", "One Piece"),
            ("Jinbe", "One Piece"), ("Portgas D. Ace", "One Piece"), ("Sabo", "One Piece"),
            ("Trafalgar D. Water Law", "One Piece"), ("Eustass Kid", "One Piece"), ("Shanks", "One Piece"),
            ("Edward Newgate", "One Piece"), ("Gol D. Roger", "One Piece"), ("Monkey D. Garp", "One Piece"),
            ("Dracule Mihawk", "One Piece"), ("Boa Hancock", "One Piece"), ("Crocodile", "One Piece"),
            ("Donquixote Doflamingo", "One Piece"), ("Bartholomew Kuma", "One Piece"), ("Buggy", "One Piece"),
            
            # Dragon Ball Z
            ("Son Goku", "Dragon Ball Z"), ("Vegeta", "Dragon Ball Z"), ("Son Gohan", "Dragon Ball Z"),
            ("Piccolo", "Dragon Ball Z"), ("Trunks", "Dragon Ball Z"), ("Son Goten", "Dragon Ball Z"),
            ("Krillin", "Dragon Ball Z"), ("Tien Shinhan", "Dragon Ball Z"), ("Yamcha", "Dragon Ball Z"),
            ("Android 17", "Dragon Ball Z"), ("Android 18", "Dragon Ball Z"), ("Cell", "Dragon Ball Z"),
            ("Majin Buu", "Dragon Ball Z"), ("Frieza", "Dragon Ball Z"), ("Broly", "Dragon Ball Z"),
            
            # Attack on Titan
            ("Eren Yeager", "Attack on Titan"), ("Mikasa Ackerman", "Attack on Titan"), ("Armin Arlert", "Attack on Titan"),
            ("Levi Ackerman", "Attack on Titan"), ("Erwin Smith", "Attack on Titan"), ("Hange Zoe", "Attack on Titan"),
            ("Jean Kirstein", "Attack on Titan"), ("Connie Springer", "Attack on Titan"), ("Sasha Blouse", "Attack on Titan"),
            ("Historia Reiss", "Attack on Titan"), ("Ymir", "Attack on Titan"), ("Reiner Braun", "Attack on Titan"),
            ("Bertholdt Hoover", "Attack on Titan"), ("Annie Leonhart", "Attack on Titan"), ("Zeke Yeager", "Attack on Titan"),
            
            # My Hero Academia
            ("Izuku Midoriya", "My Hero Academia"), ("Katsuki Bakugo", "My Hero Academia"), ("Ochaco Uraraka", "My Hero Academia"),
            ("Tenya Ida", "My Hero Academia"), ("Shoto Todoroki", "My Hero Academia"), ("Tsuyu Asui", "My Hero Academia"),
            ("All Might", "My Hero Academia"), ("Shota Aizawa", "My Hero Academia"), ("Toshinori Yagi", "My Hero Academia"),
            ("Tomura Shigaraki", "My Hero Academia"), ("Dabi", "My Hero Academia"), ("Himiko Toga", "My Hero Academia"),
            
            # Death Note
            ("Light Yagami", "Death Note"), ("L", "Death Note"), ("Near", "Death Note"), ("Misa Amane", "Death Note"),
            
            # Demon Slayer
            ("Tanjiro Kamado", "Demon Slayer"), ("Nezuko Kamado", "Demon Slayer"), ("Zenitsu Agatsuma", "Demon Slayer"),
            ("Inosuke Hashibira", "Demon Slayer"), ("Giyu Tomioka", "Demon Slayer"), ("Kyojuro Rengoku", "Demon Slayer"),
            ("Tengen Uzui", "Demon Slayer"), ("Muichiro Tokito", "Demon Slayer"), ("Mitsuri Kanroji", "Demon Slayer"),
            ("Obanai Iguro", "Demon Slayer"), ("Sanemi Shinazugawa", "Demon Slayer"), ("Gyomei Himejima", "Demon Slayer"),
            ("Shinobu Kocho", "Demon Slayer"), ("Muzan Kibutsuji", "Demon Slayer"), ("Akaza", "Demon Slayer"),
            ("Doma", "Demon Slayer"), ("Kokushibo", "Demon Slayer"),
            
            # JoJo's Bizarre Adventure
            ("Jonathan Joestar", "JoJo's Bizarre Adventure"), ("Joseph Joestar", "JoJo's Bizarre Adventure"),
            ("Jotaro Kujo", "JoJo's Bizarre Adventure"), ("Josuke Higashikata", "JoJo's Bizarre Adventure"),
            ("Giorno Giovanna", "JoJo's Bizarre Adventure"), ("Jolyne Cujoh", "JoJo's Bizarre Adventure"),
            ("DIO", "JoJo's Bizarre Adventure"), ("Joseph µ", "JoJo's Bizarre Adventure"),
            
            # Hunter x Hunter
            ("Gon Freecss", "Hunter x Hunter"), ("Killua Zoldyck", "Hunter x Hunter"), ("Kurapika", "Hunter x Hunter"),
            ("Leorio Paradinight", "Hunter x Hunter"), ("Hisoka Morow", "Hunter x Hunter"), ("Chrollo Lucilfer", "Hunter x Hunter"),
            ("Isaac Netero", "Hunter x Hunter"), ("Meruem", "Hunter x Hunter"), ("Neferpitou", "Hunter x Hunter"),
            
            # Tokyo Ghoul
            ("Ken Kaneki", "Tokyo Ghoul"), ("Touka Kirishima", "Tokyo Ghoul"), ("Rize Kamishiro", "Tokyo Ghoul"),
            ("Yoshimura", "Tokyo Ghoul"), ("Uta", "Tokyo Ghoul"), ("Juuzou Suzuya", "Tokyo Ghoul"),
            
            # Blue Lock (personnages existants)
            ("Yoichi Isagi", "Blue Lock"), ("Meguru Bachira", "Blue Lock"), ("Hyoma Chigiri", "Blue Lock"),
            ("Rensuke Kunigami", "Blue Lock"), ("Gin Gagamaru", "Blue Lock"), ("Wataru Kuon", "Blue Lock"),
            ("Asahi Naruhaya", "Blue Lock"), ("Jingo Raichi", "Blue Lock"), ("Okuhito Iemura", "Blue Lock"),
            ("Reo Mikage", "Blue Lock"), ("Seishiro Nagi", "Blue Lock"), ("Jinpachi Ego", "Blue Lock"),
            ("Shoei Baro", "Blue Lock"), ("Jyubei Aryu", "Blue Lock"), ("Aoshi Tokimitsu", "Blue Lock"),
            
            # Spy x Family
            ("Loid Forger", "Spy x Family"), ("Anya Forger", "Spy x Family"), ("Yor Forger", "Spy x Family"),
            
            # Chainsaw Man
            ("Denji", "Chainsaw Man"), ("Power", "Chainsaw Man"), ("Makima", "Chainsaw Man"),
            
            # Personnages spéciaux
            ("Akane Kurokawa", "Oshi no Ko"),
        ]
    
    async def _update_database_file(self, custom_characters: List[Tuple]):
        """Met à jour le fichier database.py avec les personnages personnalisés"""
        try:
            with open(self.database_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Trouver la section des personnages personnalisés
            start_marker = "# 🎯 VOS PERSONNAGES PERSONNALISÉS - MODIFIEZ ICI FACILEMENT"
            end_marker = "# Combiner les personnages de base avec vos personnages personnalisés"
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                logger.error("Marqueurs de section personnalisée non trouvés dans database.py")
                return
            
            # Générer le nouveau contenu pour les personnages personnalisés
            new_custom_section = self._generate_custom_characters_section(custom_characters)
            
            # Remplacer la section
            new_content = (
                content[:start_idx] + 
                start_marker + "\n" +
                new_custom_section + "\n        ]\n        \n        " +
                content[end_idx:]
            )
            
            # Écrire le fichier mis à jour
            with open(self.database_file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info("Fichier database.py mis à jour avec les personnages personnalisés")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du fichier: {e}")
    
    def _generate_custom_characters_section(self, custom_characters: List[Tuple]) -> str:
        """Génère la section des personnages personnalisés formatée"""
        lines = [
            "        # ═══════════════════════════════════════════════════════════════════════",
            "        # Ajoutez, modifiez ou supprimez vos personnages directement dans cette section",
            "        # Format: (\"Nom\", \"Anime/Série\", \"Rareté\", Valeur, \"URL_Image\")",
            "        # Raretés disponibles: Common, Rare, Epic, Legendary, Mythic, Titan, Fusion, Secret",
            "        ",
            "        custom_characters = ["
        ]
        
        if not custom_characters:
            lines.extend([
                "            # Aucun personnage personnalisé pour le moment",
                "            # Utilisez !createchar pour en ajouter",
                "            # Exemple: (\"Nom du Personnage\", \"Nom de l'Anime\", \"Rareté\", Valeur, \"URL_Image\"),"
            ])
        else:
            # Grouper par anime
            by_anime = {}
            for name, anime, rarity, value, image_url in custom_characters:
                if anime not in by_anime:
                    by_anime[anime] = []
                by_anime[anime].append((name, anime, rarity, value, image_url))
            
            # Générer les lignes par anime
            for anime, chars in sorted(by_anime.items()):
                lines.append(f"            # {anime}")
                for name, _, rarity, value, image_url in chars:
                    # Échapper les guillemets dans le nom
                    safe_name = name.replace('"', '\\"')
                    safe_anime = anime.replace('"', '\\"')
                    safe_url = image_url.replace('"', '\\"') if image_url else "https://i.imgur.com/example.jpg"
                    
                    lines.append(f'            ("{safe_name}", "{safe_anime}", "{rarity}", {value},')
                    lines.append(f'             "{safe_url}"),')
                lines.append("")
        
        return "\n".join(lines)
    
    async def _create_missing_series(self, custom_characters: List[Tuple]):
        """Crée automatiquement les séries manquantes pour les nouveaux animes"""
        try:
            # Récupérer tous les animes uniques des personnages personnalisés
            animes = set(char[1] for char in custom_characters)
            
            for anime in animes:
                await self.db.auto_create_series(anime)
                
        except Exception as e:
            logger.error(f"Erreur lors de la création des séries: {e}")

async def sync_admin_characters(db_manager):
    """Fonction utilitaire pour synchroniser les personnages admin"""
    sync_manager = AdminCharacterSync(db_manager)
    return await sync_manager.sync_admin_characters_to_code()