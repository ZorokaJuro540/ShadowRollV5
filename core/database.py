"""
Database manager for Shadow Roll Bot
Handles SQLite operations for players, characters, and inventory
"""
import aiosqlite
import logging
import random
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.models import Character, Player, Achievement
from core.config import BotConfig
from core.cache import CachedDatabaseMixin, bot_cache

logger = logging.getLogger(__name__)


class DatabaseManager(CachedDatabaseMixin):
    """Manages all database operations for Shadow Roll Bot"""

    def __init__(self, db_path: str = "shadow_roll.db"):
        self.db_path = db_path
        self.db = None

    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            self.db = await aiosqlite.connect(self.db_path)
            # Optimisations de performance
            await self.db.execute("PRAGMA journal_mode=WAL")
            await self.db.execute("PRAGMA synchronous=NORMAL") 
            await self.db.execute("PRAGMA cache_size=10000")
            await self.db.execute("PRAGMA temp_store=MEMORY")
            await self.db.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            await self.create_tables()
            await self.create_indexes()
            await self.populate_characters()
            await self.populate_achievements()
            await self.populate_shop_items()
            await self.populate_titles()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def create_tables(self):
        """Create all necessary database tables"""
        tables = [
            '''CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                coins INTEGER DEFAULT 1000,
                total_rerolls INTEGER DEFAULT 0,
                last_reroll TEXT,
                last_daily TEXT,
                is_banned BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                selected_title_id INTEGER DEFAULT NULL,
                FOREIGN KEY (selected_title_id) REFERENCES titles (id)
            )''', '''CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                anime TEXT NOT NULL,
                rarity TEXT NOT NULL,
                value INTEGER NOT NULL,
                image_url TEXT
            )''', '''CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                character_id INTEGER,
                count INTEGER DEFAULT 1,
                obtained_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (character_id) REFERENCES characters (id),
                UNIQUE(user_id, character_id)
            )''', '''CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                achievement_name TEXT NOT NULL,
                achievement_description TEXT NOT NULL,
                requirement_type TEXT NOT NULL,
                requirement_value TEXT NOT NULL,
                reward_coins INTEGER DEFAULT 0,
                icon TEXT DEFAULT "🏆"
            )''', '''CREATE TABLE IF NOT EXISTS player_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                achievement_id INTEGER,
                earned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (achievement_id) REFERENCES achievements (id)
            )''', '''CREATE TABLE IF NOT EXISTS marketplace_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER NOT NULL,
                character_id INTEGER NOT NULL,
                inventory_item_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                listed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (seller_id) REFERENCES players (user_id),
                FOREIGN KEY (character_id) REFERENCES characters (id),
                FOREIGN KEY (inventory_item_id) REFERENCES inventory (id)
            )''', '''CREATE TABLE IF NOT EXISTS marketplace_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                seller_id INTEGER NOT NULL,
                character_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                transaction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (listing_id) REFERENCES marketplace_listings (id),
                FOREIGN KEY (buyer_id) REFERENCES players (user_id),
                FOREIGN KEY (seller_id) REFERENCES players (user_id),
                FOREIGN KEY (character_id) REFERENCES characters (id)
            )''', '''CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                item_type TEXT NOT NULL,
                price INTEGER NOT NULL,
                effect_type TEXT,
                effect_value REAL,
                duration_minutes INTEGER,
                icon TEXT DEFAULT "🧪",
                is_available BOOLEAN DEFAULT TRUE
            )''', '''CREATE TABLE IF NOT EXISTS player_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                obtained_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (item_id) REFERENCES shop_items (id),
                UNIQUE(user_id, item_id)
            )''', '''CREATE TABLE IF NOT EXISTS forced_pulls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                forced_rarity TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                UNIQUE(user_id)
            )''', '''CREATE TABLE IF NOT EXISTS active_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                effect_type TEXT NOT NULL,
                effect_value REAL NOT NULL,
                expires_at TEXT NOT NULL,
                activated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id)
            )''', '''CREATE TABLE IF NOT EXISTS character_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_name TEXT NOT NULL UNIQUE,
                anime_series TEXT NOT NULL,
                description TEXT NOT NULL,
                bonus_type TEXT NOT NULL,
                bonus_value REAL NOT NULL,
                bonus_description TEXT NOT NULL,
                icon TEXT DEFAULT "🎖️"
            )''', '''CREATE TABLE IF NOT EXISTS set_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                set_id INTEGER NOT NULL,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (set_id) REFERENCES character_sets (id),
                UNIQUE(user_id, set_id)
            )''', '''CREATE TABLE IF NOT EXISTS series_rewards_claimed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                anime_series TEXT NOT NULL,
                reward_type TEXT NOT NULL,
                reward_amount INTEGER NOT NULL,
                claimed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                UNIQUE(user_id, anime_series)
            )''', '''CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                inventory_id INTEGER NOT NULL,
                slot INTEGER NOT NULL,
                equipped_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                UNIQUE(user_id, slot),
                UNIQUE(user_id, inventory_id)
            )''', '''CREATE TABLE IF NOT EXISTS character_hunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_character_id INTEGER NOT NULL,
                progress INTEGER DEFAULT 0,
                target_progress INTEGER NOT NULL,
                daily_bonus_used BOOLEAN DEFAULT FALSE,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (target_character_id) REFERENCES characters (id),
                UNIQUE(user_id)
            )''', '''CREATE TABLE IF NOT EXISTS titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                description TEXT NOT NULL,
                unlock_type TEXT NOT NULL,
                unlock_requirement TEXT NOT NULL,
                icon TEXT NOT NULL,
                bonus_type TEXT DEFAULT NULL,
                bonus_value REAL DEFAULT 0,
                bonus_description TEXT DEFAULT NULL,
                is_hidden BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )''', '''CREATE TABLE IF NOT EXISTS player_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title_id INTEGER NOT NULL,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players (user_id),
                FOREIGN KEY (title_id) REFERENCES titles (id),
                UNIQUE(user_id, title_id)
            )'''
        ]

        for table in tables:
            await self.db.execute(table)
        await self.db.commit()
        
        # Créer les index pour optimiser les performances (de manière sécurisée)
        try:
            await self.create_indexes()
        except Exception as e:
            logger.warning(f"Index creation skipped due to error: {e}")

    async def create_indexes(self):
        """Create database indexes for better performance"""
        indexes = [
            # Index pour les requêtes de joueurs (colonnes vérifiées)
            "CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id)",
            
            # Index pour les personnages (colonnes vérifiées)
            "CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name)",
            "CREATE INDEX IF NOT EXISTS idx_characters_anime ON characters(anime)",
            "CREATE INDEX IF NOT EXISTS idx_characters_rarity ON characters(rarity)",
            
            # Index pour l'inventaire (optimisation critique)
            "CREATE INDEX IF NOT EXISTS idx_inventory_user_id ON inventory(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_character_id ON inventory(character_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_user_char ON inventory(user_id, character_id)",
            
            # Index pour les effets actifs
            "CREATE INDEX IF NOT EXISTS idx_active_effects_user_id ON active_effects(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_active_effects_expires ON active_effects(expires_at)",
        ]
        
        # Créer les index de manière sécurisée
        for index_sql in indexes:
            try:
                await self.db.execute(index_sql)
            except Exception as e:
                logger.warning(f"Index creation failed: {index_sql} - {e}")
        
        await self.db.commit()

    async def sync_characters(self):
        """Synchronize characters in database - insert new ones and update existing"""
        # First, check if we need to add a unique constraint on character names
        await self.ensure_character_name_uniqueness()
        # Ensure inventory has proper unique constraints
        await self.ensure_inventory_uniqueness()

        # Populate character sets
        await self.populate_character_sets()

        characters = [

            # Naruto characters
            ("Naruto Uzumaki", "Naruto", "Legendary", 1400,
             "https://static.wikia.nocookie.net/naruto/images/d/dd/Naruto_Part_II.png"
             ),
            ("Sasuke Uchiha", "Naruto", "Legendary", 1450,
             "https://static.wikia.nocookie.net/naruto/images/2/21/Sasuke_Part_2.png"
             ),
            ("Kakashi Hatake", "Naruto", "Epic", 800,
             "https://static.wikia.nocookie.net/naruto/images/2/27/Kakashi_Hatake.png"
             ),
            ("Sakura Haruno", "Naruto", "Epic", 700,
             "https://static.wikia.nocookie.net/naruto/images/9/94/Sakura_Part_II.png"
             ),
            ("Itachi Uchiha", "Naruto", "Mythic", 3500,
             "https://static.wikia.nocookie.net/naruto/images/b/bb/Itachi.png"
             ),
            ("Madara Uchiha", "Naruto", "Mythic", 4000,
             "https://static.wikia.nocookie.net/naruto/images/a/a5/Madara_Uchiha.png"
             ),
            ("Gaara", "Naruto", "Epic", 750,
             "https://static.wikia.nocookie.net/naruto/images/0/0f/Gaara_Part_II.png"
             ),
            ("Jiraiya", "Naruto", "Legendary", 1300,
             "https://static.wikia.nocookie.net/naruto/images/2/2c/Jiraiya.png"
             ),
            ("Minato Namikaze", "Naruto", "Legendary", 1500,
             "https://static.wikia.nocookie.net/naruto/images/7/7f/Minato_Namikaze.png"
             ),
            ("Hinata Hyuga", "Naruto", "Rare", 400,
             "https://static.wikia.nocookie.net/naruto/images/3/37/Hinata_Part_II.png"
             ),
            ("Rock Lee", "Naruto", "Rare", 350,
             "https://static.wikia.nocookie.net/naruto/images/7/7d/Rock_Lee_Part_II.png"
             ),
            ("Neji Hyuga", "Naruto", "Rare", 400,
             "https://static.wikia.nocookie.net/naruto/images/7/79/Neji_Part_II.png"
             ),
            ("Shikamaru Nara", "Naruto", "Rare", 350,
             "https://static.wikia.nocookie.net/naruto/images/a/a5/Shikamaru_Part_II.png"
             ),
            ("Orochimaru", "Naruto", "Mythic", 3200,
             "https://static.wikia.nocookie.net/naruto/images/3/32/Orochimaru_Infobox.png"
             ),
            ("Tsunade", "Naruto", "Epic", 850,
             "https://static.wikia.nocookie.net/naruto/images/b/b3/Tsunade_infobox2.png"
             ),

            # Dragon Ball characters
            ("Son Goku", "Dragon Ball", "Titan", 45000,
             "https://static.wikia.nocookie.net/dragonball/images/5/5b/Goku_GT.png"
             ),
            ("Vegeta", "Dragon Ball", "Legendary", 1600,
             "https://static.wikia.nocookie.net/dragonball/images/8/8a/Vegeta_GT.png"
             ),
            ("Son Gohan", "Dragon Ball", "Legendary", 1400,
             "https://static.wikia.nocookie.net/dragonball/images/7/7b/Gohan_GT.png"
             ),
            ("Piccolo", "Dragon Ball", "Epic", 800,
             "https://static.wikia.nocookie.net/dragonball/images/f/fb/PiccoloNV.png"
             ),
            ("Frieza", "Dragon Ball", "Mythic", 3800,
             "https://static.wikia.nocookie.net/dragonball/images/c/c7/FriezaFinalForm.png"
             ),
            ("Cell", "Dragon Ball", "Mythic", 3600,
             "https://static.wikia.nocookie.net/dragonball/images/d/d2/CellPerfectReturns.png"
             ),
            ("Majin Buu", "Dragon Ball", "Mythic", 3400,
             "https://static.wikia.nocookie.net/dragonball/images/4/4f/BuuSuperNV.png"
             ),
            ("Trunks", "Dragon Ball", "Epic", 750,
             "https://static.wikia.nocookie.net/dragonball/images/2/2c/Trunks_GT.png"
             ),
            ("Krillin", "Dragon Ball", "Rare", 300,
             "https://static.wikia.nocookie.net/dragonball/images/6/6f/Krillin_GT.png"
             ),

            # One Piece characters (updated with real images)
            ("Monkey D. Luffy", "One Piece", "Legendary", 1400,
             "https://static.wikia.nocookie.net/onepiece/images/6/6d/Monkey_D._Luffy_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Roronoa Zoro", "One Piece", "Titan", 50000,
             "https://static.wikia.nocookie.net/onepiece/images/7/77/Roronoa_Zoro_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Nami", "One Piece", "Epic", 600,
             "https://static.wikia.nocookie.net/onepiece/images/f/f4/Nami_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Usopp", "One Piece", "Rare", 350,
             "https://static.wikia.nocookie.net/onepiece/images/7/7c/Usopp_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Sanji", "One Piece", "Legendary", 1300,
             "https://static.wikia.nocookie.net/onepiece/images/0/06/Sanji_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Chopper", "One Piece", "Rare", 250,
             "https://static.wikia.nocookie.net/onepiece/images/b/b3/Tony_Tony_Chopper_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Robin", "One Piece", "Epic", 700,
             "https://static.wikia.nocookie.net/onepiece/images/5/57/Nico_Robin_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Franky", "One Piece", "Epic", 650,
             "https://static.wikia.nocookie.net/onepiece/images/d/d4/Franky_Anime_Post_Timeskip_Infobox.png"
             ),
            ("Portgas D. Ace", "One Piece", "Legendary", 1500,
             "https://static.wikia.nocookie.net/onepiece/images/e/ea/Portgas_D._Ace_Anime_Infobox.png"
             ),
            ("Shanks", "One Piece", "Mythic", 3700,
             "https://static.wikia.nocookie.net/onepiece/images/d/d0/Shanks_Anime_Infobox.png"
             ),

            # Attack on Titan characters (updated with real images)
            ("Eren Yeager", "Attack on Titan", "Legendary", 1500,
             "https://i.imgur.com/gV6zE2X.png"),
            ("Mikasa Ackerman", "Attack on Titan", "Legendary", 1400,
             "https://i.imgur.com/hW7aF3Y.png"),
            ("Armin Arlert", "Attack on Titan", "Epic", 750,
             "https://i.imgur.com/iX8bG4Z.png"),
            ("Levi Ackerman", "Attack on Titan", "Mythic", 2500,
             "https://i.imgur.com/jY9cH5A.png"),
            ("Erwin Smith", "Attack on Titan", "Epic", 800,
             "https://i.imgur.com/kZ2dI6B.png"),
            ("Historia Reiss", "Attack on Titan", "Rare", 300,
             "https://i.imgur.com/lA3eJ7C.png"),
            ("Sasha Blouse", "Attack on Titan", "Rare", 250,
             "https://i.imgur.com/mB4fK8D.png"),
            ("Connie Springer", "Attack on Titan", "Common", 100,
             "https://i.imgur.com/nC5gL9E.png"),
            ("Jean Kirstein", "Attack on Titan", "Rare", 250,
             "https://i.imgur.com/oD6hM2F.png"),
            ("Reiner Braun", "Attack on Titan", "Epic", 650,
             "https://i.imgur.com/pE7iN3G.png"),

            # Death Note characters
            ("Light Yagami", "Death Note", "Legendary", 1400,
             "https://static1.cbrimages.com/wordpress/wp-content/uploads/2019/10/Featured-Image-9.jpg"
             ),
            ("L", "Death Note", "Mythic", 3500,
             "https://m.media-amazon.com/images/S/pv-target-images/76042d970583cd486abe63fe0f61cc1b1867734b8ced9f9016993f91c28ebcfe.jpg"
             ),
            ("Misa Amane", "Death Note", "Epic", 600,
             "https://www.darkcuts.club/cdn/shop/articles/Misa_Amane.png?v=1724542013&width=1100"
             ),
            ("Near", "Death Note", "Epic", 700,
             "https://static1.cbrimages.com/wordpress/wp-content/uploads/2020/04/Death-Note-Near-Cropped.jpg"
             ),
            ("Mello", "Death Note", "Epic", 650,
             "https://www.manga-city.fr/wp-content/uploads/2022/01/mello-death-note.jpg"
             ),
            ("Ryuk", "Death Note", "Legendary", 1200,
             "https://static1.srcdn.com/wordpress/wp-content/uploads/2024/02/ryuk-death-note.jpg?q=70&fit=contain&w=1200&h=628&dpr=1"
             ),

            # My Hero Academia characters (updated with real images)
            ("Izuku Midoriya", "My Hero Academia", "Legendary", 1300,
             "https://i.imgur.com/wL6pU2N.png"),
            ("Katsuki Bakugo", "My Hero Academia", "Legendary", 1200,
             "https://i.imgur.com/xM7qV3P.png"),
            ("Ochaco Uraraka", "My Hero Academia", "Epic", 500,
             "https://i.imgur.com/yN8rW4Q.png"),
            ("Tenya Iida", "My Hero Academia", "Epic", 450,
             "https://i.imgur.com/zO9sX5R.png"),
            ("Shoto Todoroki", "My Hero Academia", "Legendary", 1250,
             "https://i.imgur.com/aP2tY6S.png"),
            ("All Might", "My Hero Academia", "Mythic", 3600,
             "https://i.imgur.com/bQ3uZ7T.png"),
            ("Eraser Head", "My Hero Academia", "Epic", 750,
             "https://i.imgur.com/cR4vA8U.png"),
            ("Endeavor", "My Hero Academia", "Epic", 800,
             "https://i.imgur.com/dS5wB9V.png"),

            # Demon Slayer characters (updated with real images)
            ("Tanjiro Kamado", "Demon Slayer", "Legendary", 1200,
             "https://i.imgur.com/eT6xC2W.png"),
            ("Nezuko Kamado", "Demon Slayer", "Legendary", 1100,
             "https://i.imgur.com/fU7yD3X.png"),
            ("Zenitsu Agatsuma", "Demon Slayer", "Epic", 600,
             "https://i.imgur.com/gV8zE4Y.png"),
            ("Inosuke Hashibira", "Demon Slayer", "Epic", 550,
             "https://i.imgur.com/hW9aF5Z.png"),
            ("Giyu Tomioka", "Demon Slayer", "Epic", 900,
             "https://i.imgur.com/iX2bG6A.png"),
            ("Shinobu Kocho", "Demon Slayer", "Epic", 800,
             "https://i.imgur.com/jY3cH7B.png"),
            ("Kyojuro Rengoku", "Demon Slayer", "Legendary", 1300,
             "https://i.imgur.com/kZ4dI8C.png"),
            ("Muzan Kibutsuji", "Demon Slayer", "Mythic", 3000,
             "https://i.imgur.com/lA5eJ9D.png"),

            # JoJo's Bizarre Adventure (top tier)
            ("Jonathan Joestar", "JoJo's Bizarre Adventure", "Legendary", 1500,
             "https://i.imgur.com/example82.jpg"),
            ("Joseph Joestar", "JoJo's Bizarre Adventure", "Titan", 50000,
             "https://i.imgur.com/example82.jpg"),
            ("Jotaro Kujo", "JoJo's Bizarre Adventure", "Legendary", 1700,
             "https://i.imgur.com/example83.jpg"),
            ("Josuke Higashikata", "JoJo's Bizarre Adventure", "Legendary",
             1600, "https://i.imgur.com/example84.jpg"),
            ("Giorno Giovanna", "JoJo's Bizarre Adventure", "Legendary", 1700,
             "https://i.imgur.com/example85.jpg"),
            ("Jolyne Cujoh", "JoJo's Bizarre Adventure", "Legendary", 1600,
             "https://i.imgur.com/example86.jpg"),
            ("Dio Brando", "JoJo's Bizarre Adventure", "Mythic", 4000,
             "https://i.imgur.com/example87.jpg"),

            # Dio Evolve - Craftable uniquement avec 10 Dio Brando
            ("Dio Brando Evolve", "JoJo's Bizarre Adventure", "Evolve", 150000,
             "https://static.wikia.nocookie.net/jjba/images/thumb/b/b7/DIO_Infobox_Manga.png/1200px-DIO_Infobox_Manga.png"),
            ("Kars", "JoJo's Bizarre Adventure", "Mythic", 4200,
             "https://i.imgur.com/example88.jpg"),
            ("Enrico Pucci", "JoJo's Bizarre Adventure", "Mythic", 3900,
             "https://i.imgur.com/example89.jpg"),

            # The Eminence in Shadow (top tier)
            ("Shadow", "The Eminence in Shadow", "Titan", 50000,
             "https://images5.alphacoders.com/129/1294187.png"),
            ("Alpha", "The Eminence in Shadow", "Legendary", 1000,
             "https://images6.alphacoders.com/129/1294188.png"),
            ("Beta", "The Eminence in Shadow", "Epic", 500,
             "https://images6.alphacoders.com/129/1294189.png"),
            ("Gamma", "The Eminence in Shadow", "Rare", 250,
             "https://images6.alphacoders.com/129/1294190.png"),
            ("Delta", "The Eminence in Shadow", "Epic", 500,
             "https://images6.alphacoders.com/129/1294191.png"),
            ("Epsilon", "The Eminence in Shadow", "Rare", 250,
             "https://images6.alphacoders.com/129/1294192.png"),
            ("Zeta", "The Eminence in Shadow", "Rare", 250,
             "https://images6.alphacoders.com/129/1294193.png"),
            ("Eta", "The Eminence in Shadow", "Rare", 250,
             "https://images6.alphacoders.com/129/1294194.png"),
            ("Aurora", "The Eminence in Shadow", "Epic", 500,
             "https://static0.gamerantimages.com62323639323032383.jpg"),
            ("Iris Midgar", "The Eminence in Shadow", "Epic", 500,
             "https://otakusinh.com/wp-content0208-205936.png?w=1024"),
            ("Alexia Midgar", "The Eminence in Shadow", "Rare", 250,
             "https://i.ytimg.com/vi/ZgkysKvO2ss/maxresdefault.jpg"),

            # Demon Slayer (rééquilibré)
            ("Tanjiro Kamado", "Demon Slayer", "Legendary", 1200,
             "https://i.imgur.com/example1.jpg"),
            ("Nezuko Kamado", "Demon Slayer", "Legendary", 1100,
             "https://i.imgur.com/example2.jpg"),
            ("Zenitsu Agatsuma", "Demon Slayer", "Epic", 600,
             "https://i.imgur.com/example3.jpg"),
            ("Inosuke Hashibira", "Demon Slayer", "Epic", 550,
             "https://i.imgur.com/example4.jpg"),
            ("Giyu Tomioka", "Demon Slayer", "Epic", 900,
             "https://i.imgur.com/example5.jpg"),
            ("Shinobu Kocho", "Demon Slayer", "Epic", 800,
             "https://i.imgur.com/example6.jpg"),
            ("Kyojuro Rengoku", "Demon Slayer", "Legendary", 1300,
             "https://i.imgur.com/example7.jpg"),
            ("Tengen Uzui", "Demon Slayer", "Epic", 700,
             "https://i.imgur.com/example8.jpg"),
            ("Mitsuri Kanroji", "Demon Slayer", "Rare", 450,
             "https://i.imgur.com/example9.jpg"),
            ("Muzan Kibutsuji", "Demon Slayer", "Mythic", 3000,
             "https://i.imgur.com/example10.jpg"),

            # Black Clover (rééquilibré)
            ("Asta", "Black Clover", "Legendary", 1400,
             "https://i.imgur.com/example90.jpg"),
            ("Yuno", "Black Clover", "Legendary", 1400,
             "https://i.imgur.com/example91.jpg"),
            ("Noelle Silva", "Black Clover", "Epic", 700,
             "https://i.imgur.com/example92.jpg"),
            ("Yami Sukehiro", "Black Clover", "Legendary", 1500,
             "https://i.imgur.com/example93.jpg"),
            ("Luck Voltia", "Black Clover", "Rare", 400,
             "https://i.imgur.com/example94.jpg"),

            # Hunter x Hunter (rééquilibré)
            ("Gon Freecss", "Hunter x Hunter", "Legendary", 1400,
             "https://i.imgur.com/example95.jpg"),
            ("Killua Zoldyck", "Hunter x Hunter", "Legendary", 1400,
             "https://i.imgur.com/example96.jpg"),
            ("Kurapika", "Hunter x Hunter", "Epic", 700,
             "https://i.imgur.com/example97.jpg"),
            ("Leorio Paradinight", "Hunter x Hunter", "Rare", 300,
             "https://i.imgur.com/example98.jpg"),
            ("Hisoka Morow", "Hunter x Hunter", "Mythic", 3700,
             "https://i.imgur.com/example99.jpg"),

            # Sword Art Online (rééquilibré)
            ("Kirito", "Sword Art Online", "Legendary", 1400,
             "https://i.imgur.com/example100.jpg"),
            ("Asuna", "Sword Art Online", "Legendary", 1350,
             "https://i.imgur.com/example101.jpg"),
            ("Sinon", "Sword Art Online", "Epic", 700,
             "https://i.imgur.com/example102.jpg"),
            ("Klein", "Sword Art Online", "Rare", 300,
             "https://i.imgur.com/example103.jpg"),

            # Attack on Titan (rééquilibré)
            ("Eren Yeager", "Attack on Titan", "Legendary", 1500,
             "https://i.imgur.com/example11.jpg"),
            ("Mikasa Ackerman", "Attack on Titan", "Legendary", 1400,
             "https://i.imgur.com/example12.jpg"),
            ("Armin Arlert", "Attack on Titan", "Epic", 750,
             "https://i.imgur.com/example13.jpg"),
            ("Levi Ackerman", "Attack on Titan", "Mythic", 2500,
             "https://i.imgur.com/example14.jpg"),
            ("Annie Leonhart", "Attack on Titan", "Epic", 600,
             "https://i.imgur.com/example15.jpg"),
            ("Reiner Braun", "Attack on Titan", "Epic", 650,
             "https://i.imgur.com/example16.jpg"),
            ("Historia Reiss", "Attack on Titan", "Rare", 300,
             "https://i.imgur.com/example17.jpg"),
            ("Sasha Blouse", "Attack on Titan", "Rare", 250,
             "https://i.imgur.com/example18.jpg"),
            ("Connie Springer", "Attack on Titan", "Common", 100,
             "https://i.imgur.com/example19.jpg"),
            ("Jean Kirstein", "Attack on Titan", "Rare", 250,
             "https://i.imgur.com/example20.jpg"),

            # My Hero Academia (rééquilibré)
            ("Izuku Midoriya", "My Hero Academia", "Legendary", 1300,
             "https://i.imgur.com/example21.jpg"),
            ("Katsuki Bakugo", "My Hero Academia", "Legendary", 1200,
             "https://i.imgur.com/example22.jpg"),
            ("Shoto Todoroki", "My Hero Academia", "Legendary", 1250,
             "https://i.imgur.com/example23.jpg"),
            ("Ochaco Uraraka", "My Hero Academia", "Epic", 500,
             "https://i.imgur.com/example24.jpg"),
            ("Tenya Iida", "My Hero Academia", "Epic", 450,
             "https://i.imgur.com/example25.jpg"),
            ("Tsuyu Asui", "My Hero Academia", "Rare", 300,
             "https://i.imgur.com/example26.jpg"),

            # One Piece (rééquilibré)
            ("Monkey D. Luffy", "One Piece", "Legendary", 1400,
             "https://i.imgur.com/example27.jpg"),
            ("Roronoa Zoro", "One Piece", "Titan", 50000,
             "https://i.imgur.com/example28.jpg"),
            ("Nami", "One Piece", "Epic", 600,
             "https://i.imgur.com/example29.jpg"),
            ("Sanji", "One Piece", "Legendary", 1300,
             "https://i.imgur.com/example30.jpg"),
            ("Trafalgar Law", "One Piece", "Epic", 700,
             "https://i.imgur.com/example31.jpg"),
            ("Boa Hancock", "One Piece", "Rare", 400,
             "https://i.imgur.com/example32.jpg"),

            # Others (divers rare/common)
            ("Saitama", "One Punch Man", "Legendary", 1500,
             "https://i.imgur.com/example33.jpg"),
            ("Genos", "One Punch Man", "Epic", 700,
             "https://i.imgur.com/example34.jpg"),
            ("Megumin", "Konosuba", "Epic", 600,
             "https://i.imgur.com/example35.jpg"),
            ("Kazuma Satou", "Konosuba", "Rare", 300,
             "https://i.imgur.com/example36.jpg"),

            # Ajouts récents

            # Jujutsu Kaisen
            ("Yuji Itadori", "Jujutsu Kaisen", "Legendary", 1300,
             "https://i.imgur.com/exampleJJK1.jpg"),
            ("Megumi Fushiguro", "Jujutsu Kaisen", "Epic", 700,
             "https://i.imgur.com/exampleJJK2.jpg"),
            ("Nobara Kugisaki", "Jujutsu Kaisen", "Epic", 700,
             "https://i.imgur.com/exampleJJK3.jpg"),
            ("Sukuna", "Jujutsu Kaisen", "Mythic", 3500,
             "https://i.imgur.com/exampleJJK4.jpg"),

            # Tokyo Revengers
            ("Takemichi Hanagaki", "Tokyo Revengers", "Epic", 650,
             "https://i.imgur.com/exampleTR1.jpg"),
            ("Mikey (Manjiro Sano)", "Tokyo Revengers", "Legendary", 1400,
             "https://i.imgur.com/exampleTR2.jpg"),
            ("Draken (Ken Ryuguji)", "Tokyo Revengers", "Legendary", 1300,
             "https://i.imgur.com/exampleTR3.jpg"),

            # Blue Lock characters
            ("Rin Itoshi", "Blue Lock", "Titan", 50000,
             "https://media.tenor.com/DEr44y_-fioAAAAM/itoshi-rin-blue-lock.gif"),

            ("Shidou Ryusei", "Blue Lock", "Titan", 50000,
             "https://static.wikia.nocookie.net/bluelock/images/8/85/Shidou_Anime_Profile.png"),

            ("Yoichi Isagi", "Blue Lock", "Mythic", 3800,
             "https://static.wikia.nocookie.net/bluelock/images/0/0e/Yoichi_Isagi_Anime_Profile.png"),

            ("Nagi Seishiro", "Blue Lock", "Mythic", 3700,
             "https://static.wikia.nocookie.net/bluelock/images/7/77/Nagi_Anime_Profile.png"),

            ("Isagi & Bachira", "Blue Lock", "Fusion", 100000,
             "https://gifdb.com/images/high/isagi-yoichi-and-bachira-meguru-o7ajwlqg055r1qbx.gif"),

            ("Barou Shoei", "Blue Lock", "Mythic", 5000,
             "https://static.wikia.nocookie.net/bluelock/images/1/1e/Barou_Anime_Profile.png"),

            ("Bachira Meguru", "Blue Lock", "Legendary", 1400,
             "https://static.wikia.nocookie.net/bluelock/images/e/e1/Bachira_Anime_Profile.png"),

            ("Reo Mikage", "Blue Lock", "Epic", 800,
             "https://static.wikia.nocookie.net/bluelock/images/1/1d/Reo_Anime_Profile.png"),

            ("Karasu Tabito", "Blue Lock", "Epic", 700,
             "https://static.wikia.nocookie.net/bluelock/images/d/d3/Karasu_Anime_Profile.png"),

            ("Aoshi Tokimitsu", "Blue Lock", "Rare", 450,
             "https://static.wikia.nocookie.net/bluelock/images/3/3d/Tokimitsu_Anime_Profile.png"),

            # Spy x Family
            ("Loid Forger", "Spy x Family", "Epic", 700,
             "https://i.imgur.com/exampleSpy1.jpg"),
            ("Anya Forger", "Spy x Family", "Rare", 300,
             "https://i.imgur.com/exampleSpy2.jpg"),
            ("Yor Forger", "Spy x Family", "Rare", 300,
             "https://i.imgur.com/exampleSpy3.jpg"),

            # Chainsaw Man
            ("Denji", "Chainsaw Man", "Legendary", 1350,
             "https://i.imgur.com/exampleCSM1.jpg"),
            ("Power", "Chainsaw Man", "Epic", 700,
             "https://i.imgur.com/exampleCSM2.jpg"),
            ("Makima", "Chainsaw Man", "Mythic", 3800,
             "https://i.imgur.com/exampleCSM3.jpg"),



            # SECRET RARITY - Ultra Rare
            ("Akane Kurokawa", "Oshi no Ko", "Secret", 150000,
             "https://cdn.discordapp.com/attachments/1302916458866671636/1386689962308534312/Screenshot_20250605_210558_YouTube.jpg?ex=685a9f2a&is=68594daa&hm=971656f025b461532007a3cad745c7e0c67d9c0dd9875a404e53901a15cd2c67&"
             ),
        ]

        # Tous les personnages sont maintenant gérés via les commandes admin
        # Utilisez !createchar ou le panneau admin (!admin) pour ajouter des personnages
        # Plus de section custom_characters pour éviter les doublons

        # Track synchronized characters for logging
        new_characters = 0
        updated_characters = 0

        for name, anime, rarity, value, image_url in characters:
            # Check if character already exists
            cursor = await self.db.execute(
                'SELECT id FROM characters WHERE name = ?', (name, ))
            existing = await cursor.fetchone()

            if existing:
                # Update existing character BUT preserve custom image_url if it's not a placeholder
                cursor_img = await self.db.execute(
                    'SELECT image_url FROM characters WHERE name = ?',
                    (name, ))
                current_img = await cursor_img.fetchone()

                # Only update image if current one is a placeholder or invalid
                if current_img and current_img[0] and not current_img[
                        0].startswith('https://i.imgur.com/example'):
                    # Keep existing custom image
                    await self.db.execute(
                        '''
                        UPDATE characters
                        SET anime=?, rarity=?, value=?
                        WHERE name=?
                    ''', (anime, rarity, value, name))
                else:
                    # Update with default image (placeholder or no image)
                    await self.db.execute(
                        '''
                        UPDATE characters
                        SET anime=?, rarity=?, value=?, image_url=?
                        WHERE name=?
                    ''', (anime, rarity, value, image_url, name))
                updated_characters += 1
            else:
                # Insert new character
                await self.db.execute(
                    '''
                    INSERT INTO characters (name, anime, rarity, value, image_url)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, anime, rarity, value, image_url))
                new_characters += 1
                # Auto-create series for new anime if it doesn't exist
                await self.auto_create_series(anime)

        await self.db.commit()
        logger.info(
            f"Character sync completed: {new_characters} new, {updated_characters} updated, {len(characters)} total"
        )

    async def auto_create_series(self, anime_name: str):
        """Automatically create a series for a new anime if it doesn't exist"""
        try:
            # Check if series already exists
            cursor = await self.db.execute(
                "SELECT id FROM series WHERE LOWER(series_name) = LOWER(?)",
                (anime_name,)
            )
            existing = await cursor.fetchone()
            
            if not existing:
                # Calculate bonus based on anime popularity/size (simple heuristic)
                # Popular animes get lower bonuses to balance gameplay
                popular_animes = ['Naruto', 'One Piece', 'Dragon Ball Z', 'Attack on Titan', 'My Hero Academia']
                
                if anime_name in popular_animes:
                    coin_bonus = 1.5  # Lower bonus for popular series
                    rarity_bonus = 0.3
                else:
                    coin_bonus = 2.0  # Higher bonus for smaller series
                    rarity_bonus = 0.5
                
                # Create new series
                await self.db.execute("""
                    INSERT INTO series (series_name, coin_bonus_percentage, rarity_bonus_percentage, is_complete)
                    VALUES (?, ?, ?, FALSE)
                """, (anime_name, coin_bonus, rarity_bonus))
                
                await self.db.commit()
                logger.info(f"Auto-created series: {anime_name} (Coin: +{coin_bonus}%, Rarity: +{rarity_bonus}%)")
                
        except Exception as e:
            logger.error(f"Error auto-creating series for {anime_name}: {e}")

    async def ensure_character_name_uniqueness(self):
        """Ensure character names are unique by adding constraint if needed"""
        try:
            # Check if we already have a unique constraint
            cursor = await self.db.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='index' AND name='idx_characters_name_unique'
            """)
            constraint_exists = await cursor.fetchone()

            if not constraint_exists:
                # Create unique index on character name
                await self.db.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_name_unique 
                    ON characters (name)
                ''')
                await self.db.commit()
                logger.info("Added unique constraint on character names")

        except Exception as e:
            logger.warning(
                f"Could not add unique constraint (might already exist): {e}")

    async def ensure_inventory_uniqueness(self):
        """Ensure inventory has unique constraint on user_id, character_id"""
        try:
            # Check if we already have a unique constraint on inventory
            cursor = await self.db.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='index' AND name='idx_inventory_user_character_unique'
            """)
            constraint_exists = await cursor.fetchone()

            if not constraint_exists:
                # First, consolidate any duplicate entries
                await self.db.execute('''
                    UPDATE inventory 
                    SET count = (
                        SELECT SUM(count) 
                        FROM inventory i2 
                        WHERE i2.user_id = inventory.user_id 
                        AND i2.character_id = inventory.character_id
                    )
                    WHERE id IN (
                        SELECT MIN(id) 
                        FROM inventory 
                        GROUP BY user_id, character_id
                    )
                ''')

                # Delete duplicate entries, keeping only the first one
                await self.db.execute('''
                    DELETE FROM inventory 
                    WHERE id NOT IN (
                        SELECT MIN(id) 
                        FROM inventory 
                        GROUP BY user_id, character_id
                    )
                ''')

                # Create unique index on user_id, character_id
                await self.db.execute('''
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_user_character_unique 
                    ON inventory (user_id, character_id)
                ''')
                await self.db.commit()
                logger.info(
                    "Added unique constraint on inventory user_id, character_id"
                )

        except Exception as e:
            logger.warning(
                f"Could not add inventory unique constraint (might already exist): {e}"
            )

    async def populate_characters(self):
        """Populate characters table with anime characters - Legacy method"""
        # This method is now replaced by sync_characters()
        # Keep for backward compatibility but call sync_characters instead
        await self.sync_characters()

    async def populate_achievements(self):
        """Populate achievements table"""
        existing = await self.db.execute("SELECT COUNT(*) FROM achievements")
        count = await existing.fetchone()

        if count[0] > 0:
            return

        achievements = [
            ("Premier Pas", "Effectuer votre première invocation", "rerolls",
             "1", 50),
            ("Invocateur Novice", "Effectuer 10 invocations", "rerolls", "10",
             100),
            ("Invocateur Expérimenté", "Effectuer 50 invocations", "rerolls",
             "50", 250),
            ("Maître Invocateur", "Effectuer 100 invocations", "rerolls",
             "100", 500),
            ("Collectionneur", "Obtenir 10 personnages uniques", "characters",
             "10", 200),
            ("Grand Collectionneur", "Obtenir 25 personnages uniques",
             "characters", "25", 500),
            ("Maître Collectionneur", "Obtenir 40 personnages uniques",
             "characters", "40", 1000),
            ("Premier Épique", "Obtenir votre premier personnage Épique",
             "rarity", "Epic", 150),
            ("Premier Légendaire",
             "Obtenir votre premier personnage Légendaire", "rarity",
             "Legendary", 300),
            ("Premier Mythique", "Obtenir votre premier personnage Mythique",
             "rarity", "Mythic", 1000),
            ("Riche", "Posséder 5000 Shadow Coins", "coins", "5000", 0),
            ("Très Riche", "Posséder 10000 Shadow Coins", "coins", "10000", 0),
        ]

        await self.db.executemany(
            "INSERT INTO achievements (achievement_name, achievement_description, requirement_type, requirement_value, reward_coins) VALUES (?, ?, ?, ?, ?)",
            achievements)
        await self.db.commit()

    async def populate_titles(self):
        """Populate titles table with predefined titles"""
        existing = await self.db.execute("SELECT COUNT(*) FROM titles")
        count = await existing.fetchone()

        if count[0] > 0:
            return

        titles = [
            # Titres basés sur les réussites gacha
            ("master_fusion", "🥇 Maître de la Fusion", 
             "Avoir créé 5 personnages via le système de craft", 
             "craft", "5", "⚔️", "coin_boost", 1.03, 
             "Bonus Coins: +3% sur tous les gains"),
            
            ("shadow_theorist", "🧠 Théoricien de l'Ombre", 
             "Avoir complété 10 séries de personnages", 
             "series_completed", "10", "🔬", "rarity_boost", 0.002, 
             "Bonus Rareté: +0.2% sur toutes les invocations"),
            
            ("gacha_legend", "🃏 Légende Gacha", 
             "Avoir effectué 1000 invocations", 
             "rerolls", "1000", "🎰", "daily_boost", 1.15, 
             "Bonus Quotidien: +15% sur les récompenses journalières"),
            
            # Titres basés sur la collection
            ("titan_collector", "🏔️ Collectionneur Titan", 
             "Posséder 5 personnages Titan", 
             "rarity_collection", "Titan:5", "⚡", "coin_boost", 1.05, 
             "Bonus Coins: +5% sur tous les gains"),
            
            ("mythic_hunter", "🔥 Chasseur Mythique", 
             "Posséder 10 personnages Mythique", 
             "rarity_collection", "Mythic:10", "🪙", "hunt_boost", 1.10, 
             "Bonus Recherche: +10% progression hunt"),
            
            ("fusion_master", "💎 Maître Fusion", 
             "Posséder 3 personnages Fusion", 
             "rarity_collection", "Fusion:3", "✨", "craft_boost", 0.90, 
             "Réduction Craft: -10% coût en personnages"),
            
            # Titres basés sur la richesse
            ("shadow_merchant", "🪙 Marchand des Ombres", 
             "Posséder 50000 Shadow Coins", 
             "coins", "50000", "🪙", "sell_boost", 1.08, 
             "Bonus Vente: +8% sur toutes les ventes"),
            
            ("coin_emperor", "👑 Empereur des Coins", 
             "Posséder 100000 Shadow Coins", 
             "coins", "100000", "🏆", "coin_boost", 1.07, 
             "Bonus Coins: +7% sur tous les gains"),
            
            # Titres basés sur les succès
            ("achievement_seeker", "🎯 Chasseur de Succès", 
             "Débloquer 15 succès", 
             "achievements", "15", "🏅", "daily_boost", 1.05, 
             "Bonus Quotidien: +5% sur les récompenses journalières"),
            
            ("completionist", "📜 Complétionniste", 
             "Débloquer tous les succès disponibles", 
             "achievements", "100", "🎖️", "global_boost", 1.10, 
             "Bonus Global: +10% sur tous les gains et chances"),
            
            # Titres spéciaux et secrets
            ("shadow_lord", "🌑 Seigneur des Ombres", 
             "Posséder 1 personnage Secret", 
             "rarity_collection", "Secret:1", "🖤", "secret_boost", 1.25, 
             "Bonus Secret: +25% chance personnages rares"),
            
            ("first_pioneer", "🚀 Premier Pionnier", 
             "Être parmi les 10 premiers joueurs du bot", 
             "special", "early_user", "🪙", "pioneer_boost", 1.20, 
             "Bonus Pionnier: +20% sur tous les gains"),
            
            # Titres sans bonus (purement décoratifs)
            ("anime_connoisseur", "🎭 Connaisseur d'Anime", 
             "Posséder des personnages de 15 animes différents", 
             "anime_diversity", "15", "🎨", None, 0, None),
            
            ("dedicated_player", "⭐ Joueur Dévoué", 
             "Récupérer sa récompense quotidienne 30 jours consécutifs", 
             "daily_streak", "30", "📅", None, 0, None),
            
            ("shadow_initiate", "🔮 Initié des Ombres", 
             "Effectuer sa première invocation", 
             "rerolls", "1", "🌫️", None, 0, None),
        ]

        await self.db.executemany(
            "INSERT INTO titles (name, display_name, description, unlock_type, unlock_requirement, icon, bonus_type, bonus_value, bonus_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            titles)
        await self.db.commit()

    async def check_and_unlock_titles(self, user_id: int) -> List[Dict]:
        """Check and unlock new titles for a player"""
        newly_unlocked = []
        
        try:
            # Get player stats
            player = await self.get_or_create_player(user_id, f"User_{user_id}")
            inventory_stats = await self.get_inventory_stats(user_id)
            
            # Get all titles and check which ones are unlocked
            cursor = await self.db.execute(
                "SELECT id, name, display_name, unlock_type, unlock_requirement FROM titles"
            )
            all_titles = await cursor.fetchall()
            
            # Get already unlocked titles
            cursor = await self.db.execute(
                "SELECT title_id FROM player_titles WHERE user_id = ?", (user_id,)
            )
            unlocked_title_ids = {row[0] for row in await cursor.fetchall()}
            
            for title_id, name, display_name, unlock_type, requirement in all_titles:
                if title_id in unlocked_title_ids:
                    continue
                    
                # Check if requirement is met
                if await self._check_title_requirement(user_id, unlock_type, requirement, player, inventory_stats):
                    # Unlock the title
                    current_time = datetime.now().isoformat()
                    await self.db.execute(
                        "INSERT INTO player_titles (user_id, title_id, unlocked_at) VALUES (?, ?, ?)",
                        (user_id, title_id, current_time)
                    )
                    
                    newly_unlocked.append({
                        'id': title_id,
                        'name': name,
                        'display_name': display_name,
                        'unlocked_at': current_time
                    })
            
            if newly_unlocked:
                await self.db.commit()
                
        except Exception as e:
            logger.error(f"Error checking titles for user {user_id}: {e}")
            
        return newly_unlocked

    async def _check_title_requirement(self, user_id: int, unlock_type: str, requirement: str, player, inventory_stats: Dict) -> bool:
        """Check if a title requirement is met"""
        try:
            if unlock_type == "rerolls":
                return player.total_rerolls >= int(requirement)
                
            elif unlock_type == "coins":
                return player.coins >= int(requirement)
                
            elif unlock_type == "craft":
                # Count crafted characters (this would need tracking)
                cursor = await self.db.execute(
                    "SELECT COUNT(*) FROM inventory WHERE user_id = ? AND obtained_via_craft = 1",
                    (user_id,)
                )
                crafted_count = await cursor.fetchone()
                return crafted_count[0] >= int(requirement) if crafted_count else False
                
            elif unlock_type == "series_completed":
                cursor = await self.db.execute(
                    "SELECT COUNT(*) FROM set_completions WHERE user_id = ? AND is_active = 1",
                    (user_id,)
                )
                completed_series = await cursor.fetchone()
                return completed_series[0] >= int(requirement) if completed_series else False
                
            elif unlock_type == "rarity_collection":
                rarity, count_needed = requirement.split(':')
                count_needed = int(count_needed)
                
                cursor = await self.db.execute(
                    """SELECT SUM(i.count) FROM inventory i 
                       JOIN characters c ON i.character_id = c.id 
                       WHERE i.user_id = ? AND c.rarity = ?""",
                    (user_id, rarity)
                )
                current_count = await cursor.fetchone()
                return (current_count[0] or 0) >= count_needed
                
            elif unlock_type == "achievements":
                cursor = await self.db.execute(
                    "SELECT COUNT(*) FROM player_achievements WHERE user_id = ?",
                    (user_id,)
                )
                achievement_count = await cursor.fetchone()
                return achievement_count[0] >= int(requirement) if achievement_count else False
                
            elif unlock_type == "anime_diversity":
                cursor = await self.db.execute(
                    """SELECT COUNT(DISTINCT c.anime) FROM inventory i 
                       JOIN characters c ON i.character_id = c.id 
                       WHERE i.user_id = ?""",
                    (user_id,)
                )
                anime_count = await cursor.fetchone()
                return anime_count[0] >= int(requirement) if anime_count else False
                
            elif unlock_type == "special":
                if requirement == "early_user":
                    cursor = await self.db.execute(
                        "SELECT user_id FROM players ORDER BY created_at LIMIT 10"
                    )
                    early_users = await cursor.fetchall()
                    return user_id in [row[0] for row in early_users]
                    
        except Exception as e:
            logger.error(f"Error checking title requirement {unlock_type}:{requirement}: {e}")
            
        return False

    async def get_player_titles(self, user_id: int) -> List[Dict]:
        """Get all titles available to a player with unlock status"""
        cursor = await self.db.execute(
            """SELECT t.id, t.name, t.display_name, t.description, t.icon, 
                      t.bonus_type, t.bonus_value, t.bonus_description,
                      CASE WHEN pt.user_id IS NOT NULL THEN 1 ELSE 0 END as is_unlocked,
                      pt.unlocked_at,
                      CASE WHEN p.selected_title_id = t.id THEN 1 ELSE 0 END as is_selected
               FROM titles t 
               LEFT JOIN player_titles pt ON t.id = pt.title_id AND pt.user_id = ?
               LEFT JOIN players p ON p.user_id = ?
               ORDER BY is_unlocked DESC, t.display_name""",
            (user_id, user_id)
        )
        
        titles = []
        for row in await cursor.fetchall():
            titles.append({
                'id': row[0],
                'name': row[1],
                'display_name': row[2],
                'description': row[3],
                'icon': row[4],
                'bonus_type': row[5],
                'bonus_value': row[6],
                'bonus_description': row[7],
                'is_unlocked': bool(row[8]),
                'unlocked_at': row[9],
                'is_selected': bool(row[10])
            })
        
        return titles

    async def select_title(self, user_id: int, title_id: int) -> bool:
        """Select a title for a player"""
        try:
            # Check if player has unlocked this title
            cursor = await self.db.execute(
                "SELECT 1 FROM player_titles WHERE user_id = ? AND title_id = ?",
                (user_id, title_id)
            )
            
            if not await cursor.fetchone():
                return False
                
            # Update player's selected title
            await self.db.execute(
                "UPDATE players SET selected_title_id = ? WHERE user_id = ?",
                (title_id, user_id)
            )
            await self.db.commit()
            
            # Invalidate cache
            await self.invalidate_player_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error selecting title for user {user_id}: {e}")
            return False

    async def unselect_title(self, user_id: int) -> bool:
        """Remove selected title from a player"""
        try:
            await self.db.execute(
                "UPDATE players SET selected_title_id = NULL WHERE user_id = ?",
                (user_id,)
            )
            await self.db.commit()
            
            # Invalidate cache
            await self.invalidate_player_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error unselecting title for user {user_id}: {e}")
            return False

    async def get_selected_title(self, user_id: int) -> Optional[Dict]:
        """Get a player's currently selected title"""
        cursor = await self.db.execute(
            """SELECT t.id, t.name, t.display_name, t.icon, 
                      t.bonus_type, t.bonus_value, t.bonus_description
               FROM players p
               JOIN titles t ON p.selected_title_id = t.id
               WHERE p.user_id = ?""",
            (user_id,)
        )
        
        row = await cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'display_name': row[2],
                'icon': row[3],
                'bonus_type': row[4],
                'bonus_value': row[5],
                'bonus_description': row[6]
            }
        
        return None

    async def get_title_bonuses(self, user_id: int) -> Dict:
        """Get all active title bonuses for a player"""
        bonuses = {
            'coin_boost': 1.0,
            'rarity_boost': 0.0,
            'daily_boost': 1.0,
            'hunt_boost': 1.0,
            'craft_boost': 1.0,
            'sell_boost': 1.0,
            'secret_boost': 1.0,
            'pioneer_boost': 1.0,
            'global_boost': 1.0
        }
        
        selected_title = await self.get_selected_title(user_id)
        if selected_title and selected_title['bonus_type']:
            bonus_type = selected_title['bonus_type']
            bonus_value = selected_title['bonus_value']
            
            if bonus_type in bonuses:
                if bonus_type.endswith('_boost') and bonus_type != 'rarity_boost':
                    bonuses[bonus_type] = bonus_value
                elif bonus_type == 'rarity_boost':
                    bonuses[bonus_type] = bonus_value
                    
        return bonuses

    async def populate_shop_items(self):
        """Populate shop items table with luck potions and consumables"""
        # Clear existing items to force refresh with redesigned shop
        await self.db.execute("DELETE FROM shop_items")
        await self.db.commit()

        shop_items = [
            # Basic Luck Potions - REBALANCED PRICES x10
            ("Essence des Ombres",
             "Augmente les chances de Rares de 25% pendant 30 minutes",
             "luck_potion", 4000, "rare_boost", 0.25, 30, "🧪"),
            ("Philtre d'Épopée",
             "Augmente les chances d'Épiques de 50% pendant 20 minutes",
             "luck_potion", 8000, "epic_boost", 0.50, 20, "⚗️"),
            ("Élixir Légendaire",
             "Augmente les chances de Légendaires de 75% pendant 15 minutes",
             "luck_potion", 18000, "legendary_boost", 0.75, 15, "🍶"),
            ("Sérum Mythique",
             "Double les chances de Mythiques pendant 10 minutes",
             "luck_potion", 25000, "mythical_boost", 1.0, 10, "🔮"),

            # Premium Potions - REBALANCED PRICES x10
            ("Potion d'Ombre Totale",
             "Augmente TOUTES les raretés de 30% pendant 25 minutes",
             "luck_potion", 22000, "all_boost", 0.30, 25, "✨"),
            ("Elixir du Chaos",
             "Triple toutes les chances pendant 8 minutes - TRÈS RARE",
             "luck_potion", 65000, "mega_boost", 3.0, 8, "💫"),

            # Economy Items - REBALANCED PRICES x10
            ("Amulette de Fortune",
             "Double les Shadow Coins gagnés pendant 45 minutes", "utility",
             12000, "coin_boost", 2.0, 45, "🪙"),
            ("Pierre de Prospérité",
             "Triple les gains de coins pendant 20 minutes", "utility", 35000,
             "coin_boost", 3.0, 20, "💎"),

            # Special Items - REBALANCED PRICES x10
            ("Cristal de Garantie Rare",
             "Votre prochaine invocation sera au minimum Rare", "special",
             10000, "guaranteed_rare", 1.0, 0, "🔶"),
            ("Orbe de Destinée",
             "Votre prochaine invocation sera au minimum Épique", "special",
             25000, "guaranteed_epic", 1.0, 0, "🔮"),
        ]

        await self.db.executemany(
            "INSERT INTO shop_items (name, description, item_type, price, effect_type, effect_value, duration_minutes, icon) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            shop_items)
        await self.db.commit()

    async def get_or_create_player(self, user_id: int,
                                   username: str) -> Player:
        """Get existing player or create new one"""
        cursor = await self.db.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id, ))
        row = await cursor.fetchone()

        if row:
            return Player(user_id=row[0],
                          username=row[1],
                          coins=row[2],
                          total_rerolls=row[3],
                          last_reroll=row[4],
                          last_daily=row[5],
                          is_banned=bool(row[6]),
                          created_at=row[7])
        else:
            # Create new player
            current_time = datetime.now().isoformat()
            await self.db.execute(
                "INSERT INTO players (user_id, username, created_at) VALUES (?, ?, ?)",
                (user_id, username, current_time))
            await self.db.commit()
            return Player(user_id=user_id,
                          username=username,
                          created_at=current_time)

    async def get_player_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player data as dictionary"""
        try:
            cursor = await self.db.execute(
                "SELECT user_id, username, coins, total_rerolls, last_reroll, last_daily, is_banned, created_at FROM players WHERE user_id = ?", 
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'coins': row[2] or 1000,  # Default starting coins
                    'total_rerolls': row[3] or 0,
                    'last_reroll': row[4],
                    'last_daily': row[5],
                    'is_banned': bool(row[6]),
                    'created_at': row[7]
                }
            else:
                # Create new player if not exists
                current_time = datetime.now().isoformat()
                await self.db.execute(
                    "INSERT INTO players (user_id, username, coins, created_at) VALUES (?, ?, ?, ?)",
                    (user_id, f"User_{user_id}", BotConfig.STARTING_COINS, current_time)
                )
                await self.db.commit()
                
                return {
                    'user_id': user_id,
                    'username': f"User_{user_id}",
                    'coins': BotConfig.STARTING_COINS,
                    'total_rerolls': 0,
                    'last_reroll': None,
                    'last_daily': None,
                    'is_banned': False,
                    'created_at': current_time
                }
        except Exception as e:
            logger.error(f"Error getting player data for {user_id}: {e}")
            return None

    async def update_player_coins(self, user_id: int, coins: int):
        """Update player coins to exact amount"""
        await self.db.execute("UPDATE players SET coins = ? WHERE user_id = ?",
                              (coins, user_id))
        await self.db.commit()
    
    async def add_player_coins(self, user_id: int, amount: int):
        """Add coins to player (for rewards)"""
        await self.db.execute("UPDATE players SET coins = coins + ? WHERE user_id = ?",
                              (amount, user_id))
        await self.db.commit()
    
    async def subtract_player_coins(self, user_id: int, amount: int):
        """Subtract coins from player (for purchases)"""
        await self.db.execute("UPDATE players SET coins = coins - ? WHERE user_id = ?",
                              (amount, user_id))
        await self.db.commit()

    async def update_player_reroll_stats(self, user_id: int, last_reroll: str):
        """Update player reroll statistics"""
        await self.db.execute(
            "UPDATE players SET total_rerolls = total_rerolls + 1, last_reroll = ? WHERE user_id = ?",
            (last_reroll, user_id))
        await self.db.commit()

    async def update_daily_reward(self, user_id: int, last_daily: str):
        """Update player daily reward timestamp"""
        await self.db.execute(
            "UPDATE players SET last_daily = ? WHERE user_id = ?",
            (last_daily, user_id))
        await self.db.commit()

    async def sync_player_stats(self, user_id: int):
        """Sync player statistics with current data"""
        # Update username if player exists
        await self.db.execute(
            "UPDATE players SET username = (SELECT username FROM players WHERE user_id = ?) WHERE user_id = ?",
            (user_id, user_id))
        await self.db.commit()

    async def get_character_by_rarity_weight(self,
                                             user_id: int = None,
                                             bot=None) -> Optional[Character]:
        """Get random character based on rarity weights, considering active luck effects and forced pulls"""
        import random

        # Check for forced pull first
        if bot and user_id and hasattr(
                bot, 'forced_pulls') and user_id in bot.forced_pulls:
            forced_rarity = bot.forced_pulls[user_id]
            # Remove forced pull after use
            del bot.forced_pulls[user_id]

            # Get random character of forced rarity (exclude Evolve rarity which is craft-only)
            cursor = await self.db.execute(
                "SELECT * FROM characters WHERE rarity = ? AND rarity != 'Evolve' ORDER BY RANDOM() LIMIT 1",
                (forced_rarity, ))
            char_row = await cursor.fetchone()

            if char_row:
                return Character(id=char_row[0],
                                 name=char_row[1],
                                 anime=char_row[2],
                                 rarity=char_row[3],
                                 value=char_row[4],
                                 image_url=char_row[5])

        # Get base rarity weights
        base_weights = BotConfig.RARITY_WEIGHTS.copy()

        # Apply equipment bonuses first if user provided
        if user_id:
            base_weights = await self.apply_equipment_bonuses_to_rarity_weights(user_id, base_weights)

        # Apply luck potion effects if user provided
        if user_id:
            active_effects = await self.get_active_effects(user_id)
            for effect in active_effects:
                effect_type = effect['effect_type']
                effect_value = effect['effect_value']

                if effect_type == 'rare_boost':
                    base_weights['Rare'] *= (1 + effect_value)
                elif effect_type == 'epic_boost':
                    base_weights['Epic'] *= (1 + effect_value)
                elif effect_type == 'legendary_boost':
                    base_weights['Legendary'] *= (1 + effect_value)
                elif effect_type == 'mythical_boost':
                    base_weights['Mythic'] *= (1 + effect_value)
                # Note: Titan, Fusion, and Secret rarities are NOT affected by potions
                elif effect_type == 'all_boost':
                    # Boost only Common to Mythic rarities (exclude ultra-rare tiers)
                    for rarity in ['Rare', 'Epic', 'Legendary', 'Mythic']:
                        base_weights[rarity] *= (1 + effect_value)
                elif effect_type == 'mega_boost':
                    # Triple only Common to Mythic rarities (exclude ultra-rare tiers)
                    for rarity in ['Rare', 'Epic', 'Legendary', 'Mythic']:
                        base_weights[rarity] *= effect_value

            # Apply set bonuses (these still affect all rarities including ultra-rares)
            set_bonuses = await self.get_active_set_bonuses(user_id)
            if set_bonuses.get('rarity_boost', 0) > 0:
                # Apply global rarity boost to all rarities except Common
                global_boost = 1 + set_bonuses['rarity_boost']
                for rarity in [
                        'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan',
                        'Fusion', 'Secret'
                ]:
                    base_weights[rarity] *= global_boost

        # Calculate total weight and convert to integer scale
        total_weight = sum(base_weights.values())
        # Scale up by 100 to handle decimal weights like 0.1
        scale = 100
        total_weight_scaled = int(total_weight * scale)

        if total_weight_scaled <= 0:
            # Fallback to Common if weights are invalid
            selected_rarity = 'Common'
        else:
            random_num = random.randint(1, total_weight_scaled)

            # Determine rarity based on weight
            current_weight = 0
            selected_rarity = None
            for rarity, weight in base_weights.items():
                current_weight += int(weight * scale)
                if random_num <= current_weight:
                    selected_rarity = rarity
                    break

            if not selected_rarity:
                selected_rarity = 'Common'

        # Get random character of selected rarity (exclude Evolve rarity which is craft-only)
        cursor = await self.db.execute(
            "SELECT * FROM characters WHERE rarity = ? AND rarity != 'Evolve' ORDER BY RANDOM() LIMIT 1",
            (selected_rarity, ))
        row = await cursor.fetchone()

        if row:
            return Character(id=row[0],
                             name=row[1],
                             anime=row[2],
                             rarity=row[3],
                             value=row[4],
                             image_url=row[5])
        return None

    async def calculate_luck_bonus(self, user_id: int) -> dict:
        """Calculate current luck bonus percentages for display - showing combined multiplicative effect"""
        active_effects = await self.get_active_effects(user_id)

        # Calculate multipliers for each rarity (only affected rarities)
        # Note: Titan, Fusion, and Secret are NOT affected by potions
        multipliers = {
            'rare': 1.0,
            'epic': 1.0,
            'legendary': 1.0,
            'mythical': 1.0
        }

        for effect in active_effects:
            effect_type = effect['effect_type']
            effect_value = effect['effect_value']

            if effect_type == 'rare_boost':
                multipliers['rare'] *= (1 + effect_value)
            elif effect_type == 'epic_boost':
                multipliers['epic'] *= (1 + effect_value)
            elif effect_type == 'legendary_boost':
                multipliers['legendary'] *= (1 + effect_value)
            elif effect_type == 'mythical_boost':
                multipliers['mythical'] *= (1 + effect_value)
            elif effect_type == 'all_boost':
                # Only boost Common to Mythic rarities
                bonus_multiplier = (1 + effect_value)
                multipliers['rare'] *= bonus_multiplier
                multipliers['epic'] *= bonus_multiplier
                multipliers['legendary'] *= bonus_multiplier
                multipliers['mythical'] *= bonus_multiplier
            elif effect_type == 'mega_boost':
                # Only boost Common to Mythic rarities
                multipliers['rare'] *= effect_value
                multipliers['epic'] *= effect_value
                multipliers['legendary'] *= effect_value
                multipliers['mythical'] *= effect_value

        # Convert multipliers to bonus percentages for display
        # Only show bonuses for rarities affected by potions
        luck_bonuses = {
            'rare': int((multipliers['rare'] - 1) * 100),
            'epic': int((multipliers['epic'] - 1) * 100),
            'legendary': int((multipliers['legendary'] - 1) * 100),
            'mythical': int((multipliers['mythical'] - 1) * 100)
        }

        # Calculate average total bonus (only for affected rarities)
        total_bonus = int(sum(luck_bonuses.values()) /
                          4) if any(luck_bonuses.values()) else 0
        luck_bonuses['total'] = total_bonus

        return luck_bonuses

    async def add_character_to_inventory(self, user_id: int,
                                         character_id: int):
        """Add character to player inventory"""
        # Check if character already exists in inventory
        cursor = await self.db.execute(
            "SELECT count FROM inventory WHERE user_id = ? AND character_id = ?",
            (user_id, character_id))
        existing = await cursor.fetchone()

        if existing:
            # Increment count
            await self.db.execute(
                "UPDATE inventory SET count = count + 1 WHERE user_id = ? AND character_id = ?",
                (user_id, character_id))
        else:
            # Add new entry
            current_time = datetime.now().isoformat()
            await self.db.execute(
                "INSERT INTO inventory (user_id, character_id, obtained_at) VALUES (?, ?, ?)",
                (user_id, character_id, current_time))

        await self.db.commit()

    async def get_player_inventory(self,
                                   user_id: int,
                                   page: int = 1,
                                   limit: int = 10) -> List[Dict]:
        """Get player inventory with pagination"""
        offset = (page - 1) * limit
        cursor = await self.db.execute(
            '''SELECT i.id, c.name, c.anime, c.rarity, c.value, i.count, c.image_url
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ?
               ORDER BY 
                   CASE c.rarity
                       WHEN 'Secret' THEN 8
                       WHEN 'Fusion' THEN 7
                       WHEN 'Titan' THEN 6
                       WHEN 'Mythic' THEN 5
                       WHEN 'Legendary' THEN 4
                       WHEN 'Epic' THEN 3
                       WHEN 'Rare' THEN 2
                       WHEN 'Common' THEN 1
                   END DESC,
                   c.value DESC, c.name
               LIMIT ? OFFSET ?''', (user_id, limit, offset))

        rows = await cursor.fetchall()
        return [{
            'inventory_item_id': row[0],
            'character_name': row[1],
            'anime': row[2],
            'rarity': row[3],
            'value': row[4],
            'count': row[5],
            'image_url': row[6]
        } for row in rows]

    async def get_user_inventory(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Get user inventory with pagination (alias for get_player_characters)"""
        cursor = await self.db.execute(
            '''SELECT i.id, i.character_id, c.name, c.anime, c.rarity, c.value, i.count, c.image_url
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ?
               ORDER BY 
                   CASE c.rarity
                       WHEN 'Secret' THEN 8
                       WHEN 'Fusion' THEN 7
                       WHEN 'Titan' THEN 6
                       WHEN 'Mythic' THEN 5
                       WHEN 'Legendary' THEN 4
                       WHEN 'Epic' THEN 3
                       WHEN 'Rare' THEN 2
                       WHEN 'Common' THEN 1
                   END DESC,
                   c.value DESC, c.name
               LIMIT ? OFFSET ?''', (user_id, limit, offset))

        rows = await cursor.fetchall()
        return [{
            'inventory_id': row[0],  # ID de la ligne d'inventaire pour les ventes
            'id': row[1],  # Character ID as 'id' for compatibility
            'character_id': row[1],
            'name': row[2],
            'anime': row[3],
            'rarity': row[4],
            'value': row[5],
            'quantity': row[6],  # Both 'quantity' and 'count' for compatibility
            'count': row[6],
            'image_url': row[7]
        } for row in rows]

    async def get_player_characters(self, user_id: int) -> List[Dict]:
        """Get all characters owned by a player"""
        cursor = await self.db.execute(
            '''SELECT i.character_id, c.name, c.anime, c.rarity, c.value, i.count, c.image_url
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ?
               ORDER BY 
                   CASE c.rarity
                       WHEN 'Secret' THEN 8
                       WHEN 'Fusion' THEN 7
                       WHEN 'Titan' THEN 6
                       WHEN 'Mythic' THEN 5
                       WHEN 'Legendary' THEN 4
                       WHEN 'Epic' THEN 3
                       WHEN 'Rare' THEN 2
                       WHEN 'Common' THEN 1
                   END DESC,
                   c.value DESC, c.name''', (user_id,))

        rows = await cursor.fetchall()
        return [{
            'character_id': row[0],
            'name': row[1],
            'anime': row[2],
            'rarity': row[3],
            'value': row[4],
            'count': row[5],
            'image_url': row[6]
        } for row in rows]

    async def get_character_by_id(self, character_id: int) -> Optional[Dict]:
        """Get character by ID"""
        cursor = await self.db.execute(
            "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE id = ?",
            (character_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'anime': row[2],
                'rarity': row[3],
                'value': row[4],
                'image_url': row[5]
            }
        return None

    async def add_character_to_player(self, user_id: int, character_id: int) -> bool:
        """Add character to player inventory (alias for add_character_to_inventory)"""
        return await self.add_character_to_inventory(user_id, character_id)

    async def remove_character_from_inventory(self, user_id: int, character_id: int) -> bool:
        """Remove character from player inventory"""
        try:
            # First check if user has this character
            cursor = await self.db.execute(
                "SELECT count FROM inventory WHERE user_id = ? AND character_id = ?",
                (user_id, character_id)
            )
            row = await cursor.fetchone()
            
            if not row or row[0] <= 0:
                return False
            
            current_count = row[0]
            
            if current_count == 1:
                # Remove completely if only one left
                await self.db.execute(
                    "DELETE FROM inventory WHERE user_id = ? AND character_id = ?",
                    (user_id, character_id)
                )
            else:
                # Decrease count by 1
                await self.db.execute(
                    "UPDATE inventory SET count = count - 1 WHERE user_id = ? AND character_id = ?",
                    (user_id, character_id)
                )
            
            await self.db.commit()
            
            # Invalidate cache
            bot_cache.invalidate_pattern(f"inventory_{user_id}")
            bot_cache.invalidate_pattern(f"player_{user_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing character from inventory: {e}")
            return False

    async def get_player_potions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all potions owned by a player"""
        try:
            cursor = await self.db.execute(
                '''SELECT potion_name, effect_type, duration_minutes, quantity, purchased_at
                   FROM player_potions 
                   WHERE user_id = ? 
                   ORDER BY purchased_at DESC''', 
                (user_id,)
            )
            rows = await cursor.fetchall()
            
            potions = []
            for row in rows:
                potions.append({
                    'name': row[0],
                    'effect_type': row[1],
                    'duration': row[2],
                    'quantity': row[3],
                    'purchased_at': row[4],
                    'icon': self.get_potion_icon(row[1])
                })
            
            return potions
            
        except Exception as e:
            logger.error(f"Error getting player potions for {user_id}: {e}")
            return []
    
    def get_potion_icon(self, effect_type: str) -> str:
        """Get icon for potion type"""
        icons = {
            'luck_boost': '🧪',
            'coin_boost': '🪙', 
            'rare_boost': '🔮',
            'epic_boost': '⚗️',
            'legendary_boost': '🍶',
            'mythical_boost': '🔮',
            'all_boost': '✨',
            'mega_boost': '💫'
        }
        return icons.get(effect_type, '🧪')

    async def get_inventory_stats(self, user_id: int) -> Dict[str, Any]:
        """Get inventory statistics for player"""
        # Get unique characters count
        cursor = await self.db.execute(
            "SELECT COUNT(DISTINCT character_id) FROM inventory WHERE user_id = ?",
            (user_id, ))
        unique_count = await cursor.fetchone()

        # Get total characters count
        cursor = await self.db.execute(
            "SELECT SUM(count) FROM inventory WHERE user_id = ?", (user_id, ))
        total_count = await cursor.fetchone()

        # Get total value
        cursor = await self.db.execute(
            '''SELECT SUM(c.value * i.count)
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ?''', (user_id, ))
        total_value = await cursor.fetchone()

        # Get rarity counts
        cursor = await self.db.execute(
            '''SELECT c.rarity, SUM(i.count)
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ?
               GROUP BY c.rarity''', (user_id, ))
        rarity_rows = await cursor.fetchall()
        rarity_counts = {row[0]: row[1] for row in rarity_rows}

        return {
            'unique_characters': unique_count[0] if unique_count[0] else 0,
            'total_characters': total_count[0] if total_count[0] else 0,
            'total_value': total_value[0] if total_value[0] else 0,
            'rarity_counts': rarity_counts
        }

    async def get_leaderboard(self,
                              category: str = 'coins',
                              limit: int = 10) -> List[Dict]:
        """Get leaderboard rankings"""
        if category == 'coins':
            cursor = await self.db.execute(
                '''SELECT username, coins, 
                   ROW_NUMBER() OVER (ORDER BY coins DESC) as rank
                   FROM players 
                   WHERE is_banned = FALSE
                   ORDER BY coins DESC 
                   LIMIT ?''', (limit, ))
        elif category == 'collection_value':
            cursor = await self.db.execute(
                '''SELECT p.username, 
                   COALESCE(SUM(c.value), 0) as collection_value,
                   ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(c.value), 0) DESC) as rank
                   FROM players p
                   LEFT JOIN inventory i ON p.user_id = i.user_id
                   LEFT JOIN characters c ON i.character_id = c.id
                   WHERE p.is_banned = FALSE
                   GROUP BY p.user_id, p.username
                   ORDER BY collection_value DESC 
                   LIMIT ?''', (limit, ))
        else:
            cursor = await self.db.execute(
                '''SELECT username, total_rerolls as value,
                   ROW_NUMBER() OVER (ORDER BY total_rerolls DESC) as rank
                   FROM players 
                   WHERE is_banned = FALSE
                   ORDER BY total_rerolls DESC 
                   LIMIT ?''', (limit, ))

        rows = await cursor.fetchall()
        if category == 'coins':
            return [{
                'username': row[0],
                'coins': row[1],
                'rank': row[2]
            } for row in rows]
        elif category == 'collection_value':
            return [{
                'username': row[0],
                'collection_value': row[1],
                'rank': row[2]
            } for row in rows]
        else:
            return [{
                'username': row[0],
                'rerolls': row[1],
                'rank': row[2]
            } for row in rows]

    async def is_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        cursor = await self.db.execute(
            "SELECT is_banned FROM players WHERE user_id = ?", (user_id, ))
        result = await cursor.fetchone()
        return result[0] if result else False

    async def ban_user(self, user_id: int, username: str):
        """Ban user"""
        await self.get_or_create_player(user_id, username)
        await self.db.execute(
            "UPDATE players SET is_banned = TRUE WHERE user_id = ?",
            (user_id, ))
        await self.db.commit()

    async def unban_user(self, user_id: int):
        """Unban user"""
        await self.db.execute(
            "UPDATE players SET is_banned = FALSE WHERE user_id = ?",
            (user_id, ))
        await self.db.commit()

    async def get_all_characters(self,
                                 page: int = 1,
                                 limit: int = 10) -> List[Character]:
        """Get all available characters with pagination"""
        offset = (page - 1) * limit
        cursor = await self.db.execute(
            '''SELECT id, name, anime, rarity, value, image_url
               FROM characters
               ORDER BY 
                   CASE rarity 
                       WHEN 'Mythic' THEN 1
                       WHEN 'Legendary' THEN 2
                       WHEN 'Epic' THEN 3
                       WHEN 'Rare' THEN 4
                       WHEN 'Common' THEN 5
                   END,
                   value DESC, name
               LIMIT ? OFFSET ?''', (limit, offset))

        rows = await cursor.fetchall()
        return [
            Character(id=row[0],
                      name=row[1],
                      anime=row[2],
                      rarity=row[3],
                      value=row[4],
                      image_url=row[5]) for row in rows
        ]

    async def get_total_characters_count(self) -> int:
        """Get total number of characters available"""
        cursor = await self.db.execute("SELECT COUNT(*) FROM characters")
        result = await cursor.fetchone()
        return result[0] if result else 0

    async def get_all_achievements_with_status(self,
                                               user_id: int) -> List[Dict]:
        """Get all achievements with their completion status for a player"""
        # Get all achievements
        cursor = await self.db.execute("""
            SELECT id, achievement_name, achievement_description, 
                   requirement_type, requirement_value, reward_coins
            FROM achievements
            ORDER BY id
        """)
        all_achievements = await cursor.fetchall()

        # Get player's earned achievements
        cursor = await self.db.execute(
            """
            SELECT achievement_id, earned_at
            FROM player_achievements
            WHERE user_id = ?
        """, (user_id, ))
        earned_achievements = {
            row[0]: row[1]
            for row in await cursor.fetchall()
        }

        # Get player stats for progress checking
        player = await self.get_or_create_player(user_id, f"User_{user_id}")
        inventory_stats = await self.get_inventory_stats(user_id)

        # Build achievement list with status
        achievements_with_status = []
        for achievement in all_achievements:
            achievement_id, name, description, req_type, req_value, reward = achievement

            # Check if earned
            is_earned = achievement_id in earned_achievements
            earned_at = earned_achievements.get(achievement_id)

            # Calculate progress
            progress = self._calculate_achievement_progress(
                req_type, req_value, player, inventory_stats)

            achievements_with_status.append({
                'id':
                achievement_id,
                'name':
                name,
                'description':
                description,
                'requirement_type':
                req_type,
                'requirement_value':
                req_value,
                'reward_coins':
                reward,
                'is_earned':
                is_earned,
                'earned_at':
                earned_at,
                'progress':
                progress,
                'progress_text':
                self._format_progress_text(req_type, progress, req_value)
            })

        return achievements_with_status

    async def get_all_characters_with_ownership(self,
                                                user_id: int) -> List[Dict]:
        """Get all characters with ownership status for a specific user"""
        try:
            cursor = await self.db.execute(
                """
                SELECT 
                    c.id,
                    c.name,
                    c.anime,
                    c.rarity,
                    c.value,
                    c.image_url,
                    CASE WHEN i.character_id IS NOT NULL THEN 1 ELSE 0 END as owned,
                    COALESCE(i.count, 0) as count
                FROM characters c
                LEFT JOIN inventory i ON c.id = i.character_id AND i.user_id = ?
                ORDER BY 
                    CASE c.rarity
                        WHEN 'Secret' THEN 8
                        WHEN 'Fusion' THEN 7
                        WHEN 'Titan' THEN 6
                        WHEN 'Mythic' THEN 5
                        WHEN 'Legendary' THEN 4
                        WHEN 'Epic' THEN 3
                        WHEN 'Rare' THEN 2
                        WHEN 'Common' THEN 1
                    END DESC,
                    c.value DESC,
                    c.name
            """, (user_id, ))

            rows = await cursor.fetchall()
            characters = []

            for row in rows:
                characters.append({
                    'id': row[0],
                    'name': row[1],
                    'anime': row[2],
                    'rarity': row[3],
                    'value': row[4],
                    'image_url': row[5],
                    'owned': bool(row[6]),
                    'count': row[7]
                })

            return characters
        except Exception as e:
            logger.error(f"Error getting characters with ownership: {e}")
            return []

    async def get_collection_stats_by_anime(self,
                                            user_id: int) -> Dict[str, Dict]:
        """Get collection completion stats by anime series"""
        try:
            cursor = await self.db.execute(
                """
                SELECT 
                    c.anime,
                    COUNT(c.id) as total_characters,
                    COUNT(i.character_id) as owned_characters,
                    SUM(c.value) as total_value,
                    SUM(CASE WHEN i.character_id IS NOT NULL THEN c.value ELSE 0 END) as owned_value
                FROM characters c
                LEFT JOIN inventory i ON c.id = i.character_id AND i.user_id = ?
                GROUP BY c.anime
                ORDER BY owned_characters DESC, c.anime
            """, (user_id, ))

            rows = await cursor.fetchall()
            stats = {}

            for row in rows:
                anime = row[0]
                total_chars = row[1]
                owned_chars = row[2]
                total_value = row[3]
                owned_value = row[4]

                completion_percentage = (owned_chars / total_chars *
                                         100) if total_chars > 0 else 0
                value_percentage = (owned_value / total_value *
                                    100) if total_value > 0 else 0

                stats[anime] = {
                    'total_characters': total_chars,
                    'owned_characters': owned_chars,
                    'completion_percentage': completion_percentage,
                    'total_value': total_value,
                    'owned_value': owned_value,
                    'value_percentage': value_percentage
                }

            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats by anime: {e}")
            return {}

    async def populate_character_sets(self):
        """Populate character sets table with predefined sets"""
        # Clear existing sets to force refresh
        await self.db.execute("DELETE FROM character_sets")
        await self.db.commit()

        character_sets = [
            # Grandes séries (11+ personnages) - Bonus puissants
            ("Ninjas de Konoha", "Naruto",
             "Les ninjas du village caché de la Feuille", "rarity_boost", 0.025,
             "Bonus Rareté Globale: +2.5% sur toutes les invocations", "🍃"),
            
            ("Héros Plus Ultra", "My Hero Academia", 
             "Les héros de l'Académie U.A.", "coin_boost", 1.3,
             "Bonus Coins: +30% sur tous les gains de Shadow Coins", "💥"),
            
            ("Équipage du Chapeau de Paille", "One Piece",
             "Les pirates à la recherche du One Piece", "coin_boost", 1.25,
             "Bonus Coins: +25% sur tous les gains de Shadow Coins", "🏴‍☠️"),
            
            ("Régiment d'Exploration", "Attack on Titan",
             "Les soldats qui combattent les Titans pour l'humanité", "coin_boost", 1.25,
             "Bonus Coins: +25% sur tous les gains de Shadow Coins", "⚔️"),
            
            ("Organisation Shadow Garden", "The Eminence in Shadow",
             "Les membres secrets de l'organisation dirigée par Shadow", "rarity_boost", 0.02,
             "Bonus Rareté Globale: +2% sur toutes les invocations", "🌑"),

            # Séries moyennes (5-10 personnages) - Bonus modérés
            ("Pourfendeurs de Démons", "Demon Slayer",
             "Les guerriers qui combattent les démons", "rarity_boost", 0.015,
             "Bonus Rareté Globale: +1.5% sur toutes les invocations", "⚡"),
            
            ("Aventure Bizarre", "JoJo's Bizarre Adventure",
             "La lignée des Joestar et leurs aventures", "coin_boost", 1.2,
             "Bonus Coins: +20% sur tous les gains de Shadow Coins", "💎"),
            
            ("Guerriers Z", "Dragon Ball",
             "Les défenseurs de la Terre face aux menaces", "coin_boost", 1.2,
             "Bonus Coins: +20% sur tous les gains de Shadow Coins", "🐉"),
            
            ("Enquêteurs Kira", "Death Note",
             "La bataille intellectuelle entre Light et L", "rarity_boost", 0.01,
             "Bonus Rareté Globale: +1% sur toutes les invocations", "📓"),
            
            ("Mages de Clover", "Black Clover",
             "Les chevaliers magiques du royaume de Clover", "coin_boost", 1.15,
             "Bonus Coins: +15% sur tous les gains de Shadow Coins", "🍀"),
            
            ("Guilde Fairy Tail", "Fairy Tail",
             "Les mages de la guilde la plus turbulente", "coin_boost", 1.15,
             "Bonus Coins: +15% sur tous les gains de Shadow Coins", "🧚"),
            
            ("Chasseurs Professionnels", "Hunter x Hunter",
             "Les chasseurs en quête d'aventures dangereuses", "rarity_boost", 0.01,
             "Bonus Rareté Globale: +1% sur toutes les invocations", "🎯"),

            # Petites séries (2-4 personnages) - Bonus légers
            ("Exorcistes de Tokyo", "Jujutsu Kaisen",
             "Les exorcistes combattant les fléaux", "coin_boost", 1.1,
             "Bonus Coins: +10% sur tous les gains de Shadow Coins", "👹"),
            
            ("Héros Classe S", "One Punch Man",
             "Les héros les plus puissants de l'Association", "coin_boost", 1.1,
             "Bonus Coins: +10% sur tous les gains de Shadow Coins", "👊"),
            
            ("Joueurs d'ALO", "Sword Art Online",
             "Les aventuriers des mondes virtuels", "coin_boost", 1.05,
             "Bonus Coins: +5% sur tous les gains de Shadow Coins", "⚔️"),
            
            ("Devils Hunters", "Chainsaw Man",
             "Les chasseurs de démons publics", "rarity_boost", 0.005,
             "Bonus Rareté Globale: +0.5% sur toutes les invocations", "🔥"),
            
            ("Famille Forger", "Spy x Family",
             "La famille d'espions la plus adorable", "coin_boost", 1.05,
             "Bonus Coins: +5% sur tous les gains de Shadow Coins", "🕵️"),
            
            ("Manji Tokyo", "Tokyo Revengers",
             "Les membres du gang légendaire", "coin_boost", 1.05,
             "Bonus Coins: +5% sur tous les gains de Shadow Coins", "🏍️"),
            
            ("Aventuriers Konosuba", "Konosuba",
             "Le groupe d'aventuriers le plus chaotique", "coin_boost", 1.05,
             "Bonus Coins: +5% sur tous les gains de Shadow Coins", "🎭"),

            # Séries uniques spéciales
            ("Légende Saiyan", "Dragon Ball Z",
             "L'héritage des guerriers Saiyan", "rarity_boost", 0.005,
             "Bonus Rareté Globale: +0.5% sur toutes les invocations", "🔥"),
            
            ("Idoles B-Komachi", "Oshi no Ko",
             "Le monde sombre du divertissement", "rarity_boost", 0.005,
             "Bonus Rareté Globale: +0.5% sur toutes les invocations", "⭐"),
            
            # Nouvelles séries ajoutées
            ("Footballeurs Élites", "Blue Lock",
             "Les footballeurs d'élite du projet Blue Lock", "coin_boost", 1.10,
             "Bonus Coins: +10% sur tous les gains de Shadow Coins", "⚽"),
             
            ("Animatroniques", "Five Nights at Freddy's",
             "Les animatroniques terrifiants de Freddy Fazbear's Pizza", "coin_boost", 1.08,
             "Bonus Coins: +8% sur tous les gains de Shadow Coins", "🤖"),
        ]

        await self.db.executemany(
            "INSERT INTO character_sets (set_name, anime_series, description, bonus_type, bonus_value, bonus_description, icon) VALUES (?, ?, ?, ?, ?, ?, ?)",
            character_sets)
        await self.db.commit()

    async def get_character_sets_with_progress(self,
                                               user_id: int) -> List[Dict]:
        """Get all character sets with completion progress for a user"""
        try:
            cursor = await self.db.execute(
                """
                SELECT 
                    cs.id,
                    cs.set_name,
                    cs.anime_series,
                    cs.description,
                    cs.bonus_type,
                    cs.bonus_value,
                    cs.bonus_description,
                    cs.icon,
                    CASE WHEN sc.id IS NOT NULL THEN 1 ELSE 0 END as is_completed
                FROM character_sets cs
                LEFT JOIN set_completions sc ON cs.id = sc.set_id AND sc.user_id = ? AND sc.is_active = TRUE
                ORDER BY is_completed DESC, cs.set_name
            """, (user_id, ))

            sets_data = await cursor.fetchall()
            sets_with_progress = []

            for set_data in sets_data:
                set_id, set_name, anime_series, description, bonus_type, bonus_value, bonus_desc, icon, is_completed = set_data

                # Get all characters from this anime series
                cursor = await self.db.execute(
                    "SELECT id, name FROM characters WHERE anime = ? ORDER BY name",
                    (anime_series, ))
                all_chars = await cursor.fetchall()

                # Get owned characters from this series
                cursor = await self.db.execute(
                    """
                    SELECT c.id, c.name 
                    FROM characters c
                    JOIN inventory i ON c.id = i.character_id
                    WHERE c.anime = ? AND i.user_id = ?
                    ORDER BY c.name
                """, (anime_series, user_id))
                owned_chars = await cursor.fetchall()

                total_chars = len(all_chars)
                owned_count = len(owned_chars)
                completion_percentage = (owned_count / total_chars *
                                         100) if total_chars > 0 else 0

                sets_with_progress.append({
                    'id':
                    set_id,
                    'set_name':
                    set_name,
                    'anime_series':
                    anime_series,
                    'description':
                    description,
                    'bonus_type':
                    bonus_type,
                    'bonus_value':
                    bonus_value,
                    'bonus_description':
                    bonus_desc,
                    'icon':
                    icon,
                    'is_completed':
                    bool(is_completed),
                    'total_characters':
                    total_chars,
                    'owned_characters':
                    owned_count,
                    'completion_percentage':
                    completion_percentage,
                    'all_characters': [{
                        'id': c[0],
                        'name': c[1]
                    } for c in all_chars],
                    'owned_characters_list': [{
                        'id': c[0],
                        'name': c[1]
                    } for c in owned_chars]
                })

            return sets_with_progress

        except Exception as e:
            logger.error(f"Error getting character sets with progress: {e}")
            return []

    async def check_and_complete_sets(self, user_id: int) -> List[Dict]:
        """Check if user has completed any new sets and mark them as complete"""
        try:
            sets_data = await self.get_character_sets_with_progress(user_id)
            newly_completed = []

            for set_info in sets_data:
                if not set_info['is_completed'] and set_info[
                        'completion_percentage'] == 100:
                    # User just completed this set!
                    await self.db.execute(
                        """
                        INSERT OR REPLACE INTO set_completions (user_id, set_id) 
                        VALUES (?, ?)
                    """, (user_id, set_info['id']))

                    set_info['is_completed'] = True
                    newly_completed.append(set_info)

            await self.db.commit()
            return newly_completed

        except Exception as e:
            logger.error(f"Error checking and completing sets: {e}")
            return []

    async def get_active_set_bonuses(self, user_id: int) -> Dict[str, float]:
        """Get all active set bonuses for a user"""
        try:
            cursor = await self.db.execute(
                """
                SELECT cs.bonus_type, cs.bonus_value
                FROM character_sets cs
                JOIN set_completions sc ON cs.id = sc.set_id
                WHERE sc.user_id = ? AND sc.is_active = 1
            """, (user_id, ))

            bonuses = {}
            rows = await cursor.fetchall()
            for bonus_type, bonus_value in rows:
                if bonus_type not in bonuses:
                    bonuses[bonus_type] = 0
                bonuses[bonus_type] += bonus_value

            return bonuses

        except Exception as e:
            logger.error(f"Error getting active set bonuses: {e}")
            return {}

    def _calculate_achievement_progress(self, req_type: str, req_value, player,
                                        inventory_stats: Dict) -> int:
        """Calculate current progress towards an achievement"""
        try:
            if req_type == 'rerolls':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return min(player.total_rerolls, target)
            elif req_type == 'coins':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return min(player.coins, target)
            elif req_type == 'characters':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return min(inventory_stats.get('unique_characters', 0), target)
            elif req_type == 'rarity':
                rarity_counts = inventory_stats.get('rarity_counts', {})
                return 1 if rarity_counts.get(req_value, 0) > 0 else 0
        except (ValueError, TypeError):
            return 0
        return 0

    def _format_progress_text(self, req_type: str, progress: int,
                              req_value) -> str:
        """Format progress text for display"""
        try:
            if req_type == 'rerolls':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return f"{progress}/{target} invocations"
            elif req_type == 'coins':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return f"{progress:,}/{target:,} {BotConfig.CURRENCY_EMOJI}"
            elif req_type == 'characters':
                target = int(req_value) if isinstance(req_value,
                                                      str) else req_value
                return f"{progress}/{target} personnages uniques"
            elif req_type == 'rarity':
                if progress > 0:
                    return f"Personnage {req_value} obtenu ✅"
                else:
                    return f"Obtenir un personnage {req_value}"
        except (ValueError, TypeError):
            return f"Progression non disponible"
        return f"{progress}/{req_value}"

    async def award_achievement(self, user_id: int,
                                achievement_id: int) -> bool:
        """Award an achievement to a player"""
        try:
            # Check if already earned
            cursor = await self.db.execute(
                """
                SELECT id FROM player_achievements 
                WHERE user_id = ? AND achievement_id = ?
            """, (user_id, achievement_id))

            if await cursor.fetchone():
                return False  # Already earned

            # Award the achievement
            current_time = datetime.now().isoformat()
            await self.db.execute(
                """
                INSERT INTO player_achievements (user_id, achievement_id, earned_at)
                VALUES (?, ?, ?)
            """, (user_id, achievement_id, current_time))
            await self.db.commit()
            return True

        except Exception as e:
            logger.error(
                f"Error awarding achievement {achievement_id} to user {user_id}: {e}"
            )
            return False

    async def create_marketplace_listing(self, seller_id: int,
                                         inventory_item_id: int,
                                         price: int) -> bool:
        """Create a new marketplace listing"""
        try:
            # Get inventory item details
            cursor = await self.db.execute(
                """
                SELECT character_id, count FROM inventory WHERE id = ? AND user_id = ?
            """, (inventory_item_id, seller_id))
            item = await cursor.fetchone()

            if not item or item[1] <= 0:
                return False  # Item not found or count is 0

            character_id, count = item

            # Check if seller already has max listings (3)
            cursor = await self.db.execute(
                """
                SELECT COUNT(*) FROM marketplace_listings 
                WHERE seller_id = ? AND is_active = TRUE
            """, (seller_id, ))
            active_listings = await cursor.fetchone()

            if active_listings[0] >= 3:
                return False  # Max listings reached

            # Set expiration date (7 days from now)
            from datetime import datetime, timedelta
            expires_at = (datetime.now() + timedelta(days=7)).isoformat()

            # Create listing
            await self.db.execute(
                """
                INSERT INTO marketplace_listings 
                (seller_id, character_id, inventory_item_id, price, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (seller_id, character_id, inventory_item_id, price,
                  expires_at))

            # Remove item from inventory (set count to 0 or delete)
            if count > 1:
                await self.db.execute(
                    """
                    UPDATE inventory SET count = count - 1 WHERE id = ?
                """, (inventory_item_id, ))
            else:
                await self.db.execute(
                    """
                    DELETE FROM inventory WHERE id = ?
                """, (inventory_item_id, ))

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error creating marketplace listing: {e}")
            return False

    async def get_marketplace_listings(self,
                                       page: int = 1,
                                       limit: int = 10) -> List[Dict]:
        """Get active marketplace listings with pagination"""
        try:
            offset = (page - 1) * limit

            cursor = await self.db.execute(
                """
                SELECT 
                    ml.id, ml.seller_id, ml.character_id, ml.price, ml.listed_at,
                    c.name, c.anime, c.rarity, c.value, c.image_url,
                    p.username as seller_name
                FROM marketplace_listings ml
                JOIN characters c ON ml.character_id = c.id
                JOIN players p ON ml.seller_id = p.user_id
                WHERE ml.is_active = TRUE 
                    AND datetime(ml.expires_at) > datetime('now')
                ORDER BY ml.listed_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            listings = []
            for row in await cursor.fetchall():
                listings.append({
                    'id': row[0],
                    'seller_id': row[1],
                    'character_id': row[2],
                    'price': row[3],
                    'listed_at': row[4],
                    'character_name': row[5],
                    'anime': row[6],
                    'rarity': row[7],
                    'character_value': row[8],
                    'image_url': row[9],
                    'seller_name': row[10]
                })

            return listings

        except Exception as e:
            logger.error(f"Error getting marketplace listings: {e}")
            return []

    async def get_player_marketplace_listings(self,
                                              user_id: int) -> List[Dict]:
        """Get player's active marketplace listings"""
        try:
            cursor = await self.db.execute(
                """
                SELECT 
                    ml.id, ml.character_id, ml.price, ml.listed_at, ml.expires_at,
                    c.name, c.anime, c.rarity, c.value
                FROM marketplace_listings ml
                JOIN characters c ON ml.character_id = c.id
                WHERE ml.seller_id = ? AND ml.is_active = TRUE
                ORDER BY ml.listed_at DESC
            """, (user_id, ))

            listings = []
            for row in await cursor.fetchall():
                listings.append({
                    'id': row[0],
                    'character_id': row[1],
                    'price': row[2],
                    'listed_at': row[3],
                    'expires_at': row[4],
                    'character_name': row[5],
                    'anime': row[6],
                    'rarity': row[7],
                    'character_value': row[8]
                })

            return listings

        except Exception as e:
            logger.error(f"Error getting player marketplace listings: {e}")
            return []

    async def purchase_marketplace_item(self, buyer_id: int,
                                        listing_id: int) -> bool:
        """Purchase an item from the marketplace"""
        try:
            # Get listing details
            cursor = await self.db.execute(
                """
                SELECT seller_id, character_id, price, is_active 
                FROM marketplace_listings 
                WHERE id = ? AND is_active = TRUE
                    AND datetime(expires_at) > datetime('now')
            """, (listing_id, ))

            listing = await cursor.fetchone()
            if not listing:
                return False  # Listing not found or expired

            seller_id, character_id, price, is_active = listing

            # Prevent self-purchase
            if buyer_id == seller_id:
                return False

            # Check buyer has enough coins
            buyer = await self.get_or_create_player(buyer_id,
                                                    f"User_{buyer_id}")
            if buyer.coins < price:
                return False

            # Process transaction
            current_time = datetime.now().isoformat()

            # Deduct coins from buyer
            await self.db.execute(
                """
                UPDATE players SET coins = coins - ? WHERE user_id = ?
            """, (price, buyer_id))

            # Add coins to seller
            await self.db.execute(
                """
                UPDATE players SET coins = coins + ? WHERE user_id = ?
            """, (price, seller_id))

            # Add character to buyer's inventory
            await self.db.execute(
                """
                INSERT INTO inventory (user_id, character_id, count, obtained_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id, character_id) DO UPDATE SET count = count + 1
            """, (buyer_id, character_id, current_time))

            # Mark listing as inactive
            await self.db.execute(
                """
                UPDATE marketplace_listings SET is_active = FALSE WHERE id = ?
            """, (listing_id, ))

            # Record transaction
            await self.db.execute(
                """
                INSERT INTO marketplace_transactions
                (listing_id, buyer_id, seller_id, character_id, price)
                VALUES (?, ?, ?, ?, ?)
            """, (listing_id, buyer_id, seller_id, character_id, price))

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error purchasing marketplace item: {e}")
            return False

    async def cancel_marketplace_listing(self, user_id: int,
                                         listing_id: int) -> bool:
        """Cancel a marketplace listing and return item to inventory"""
        try:
            # Get listing details
            cursor = await self.db.execute(
                """
                SELECT character_id FROM marketplace_listings 
                WHERE id = ? AND seller_id = ? AND is_active = TRUE
            """, (listing_id, user_id))

            listing = await cursor.fetchone()
            if not listing:
                return False

            character_id = listing[0]
            current_time = datetime.now().isoformat()

            # Return item to inventory
            await self.db.execute(
                """
                INSERT INTO inventory (user_id, character_id, count, obtained_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id, character_id) DO UPDATE SET count = count + 1
            """, (user_id, character_id, current_time))

            # Mark listing as inactive
            await self.db.execute(
                """
                UPDATE marketplace_listings SET is_active = FALSE WHERE id = ?
            """, (listing_id, ))

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error canceling marketplace listing: {e}")
            return False

    async def cleanup_expired_listings(self):
        """Clean up expired marketplace listings"""
        try:
            # Get expired listings
            cursor = await self.db.execute("""
                SELECT id, seller_id, character_id 
                FROM marketplace_listings 
                WHERE is_active = TRUE AND datetime(expires_at) <= datetime('now')
            """)

            expired_listings = await cursor.fetchall()
            current_time = datetime.now().isoformat()

            for listing_id, seller_id, character_id in expired_listings:
                # Return item to seller's inventory
                await self.db.execute(
                    """
                    INSERT INTO inventory (user_id, character_id, count, obtained_at)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(user_id, character_id) DO UPDATE SET count = count + 1
                """, (seller_id, character_id, current_time))

                # Mark listing as inactive
                await self.db.execute(
                    """
                    UPDATE marketplace_listings SET is_active = FALSE WHERE id = ?
                """, (listing_id, ))

            await self.db.commit()
            logger.info(
                f"Cleaned up {len(expired_listings)} expired marketplace listings"
            )

        except Exception as e:
            logger.error(f"Error cleaning up expired listings: {e}")

    async def get_marketplace_stats(self) -> Dict:
        """Get marketplace statistics"""
        try:
            # Active listings count
            cursor = await self.db.execute("""
                SELECT COUNT(*) FROM marketplace_listings 
                WHERE is_active = TRUE AND datetime(expires_at) > datetime('now')
            """)
            active_listings = (await cursor.fetchone())[0]

            # Total transactions
            cursor = await self.db.execute(
                "SELECT COUNT(*) FROM marketplace_transactions")
            total_transactions = (await cursor.fetchone())[0]

            # Total coins traded
            cursor = await self.db.execute(
                "SELECT SUM(price) FROM marketplace_transactions")
            total_coins_traded = (await cursor.fetchone())[0] or 0

            return {
                'active_listings': active_listings,
                'total_transactions': total_transactions,
                'total_coins_traded': total_coins_traded
            }

        except Exception as e:
            logger.error(f"Error getting marketplace stats: {e}")
            return {
                'active_listings': 0,
                'total_transactions': 0,
                'total_coins_traded': 0
            }

    # Shop and Items Methods
    async def get_shop_items(self, item_type: str = None) -> List[Dict]:
        """Get available shop items, optionally filtered by type"""
        try:
            if item_type:
                cursor = await self.db.execute(
                    "SELECT * FROM shop_items WHERE is_available = TRUE AND item_type = ? ORDER BY price",
                    (item_type, ))
            else:
                cursor = await self.db.execute(
                    "SELECT * FROM shop_items WHERE is_available = TRUE ORDER BY item_type, price"
                )

            items = []
            for row in await cursor.fetchall():
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'item_type': row[3],
                    'price': row[4],
                    'effect_type': row[5],
                    'effect_value': row[6],
                    'duration_minutes': row[7],
                    'icon': row[8]
                })
            return items
        except Exception as e:
            logger.error(f"Error getting shop items: {e}")
            return []

    async def purchase_item(self, user_id: int, item_id: int) -> bool:
        """Purchase an item from the shop"""
        try:
            # Get item details
            cursor = await self.db.execute(
                "SELECT price FROM shop_items WHERE id = ? AND is_available = TRUE",
                (item_id, ))
            item = await cursor.fetchone()

            if not item:
                return False

            price = item[0]

            # Check player has enough coins
            player = await self.get_or_create_player(user_id,
                                                     f"User_{user_id}")
            if player.coins < price:
                return False

            # Deduct coins
            new_coins = player.coins - price
            await self.update_player_coins(user_id, new_coins)

            # Add item to player inventory
            await self.db.execute(
                """INSERT INTO player_items (user_id, item_id, quantity)
                   VALUES (?, ?, 1)
                   ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + 1""",
                (user_id, item_id))

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error purchasing item: {e}")
            return False

    async def transfer_character(self, from_user_id: int, to_user_id: int, character_id: int) -> bool:
        """Transfer a character from one player to another (for trading)"""
        try:
            # Check if from_user has the character
            cursor = await self.db.execute(
                "SELECT id, count FROM inventory WHERE user_id = ? AND character_id = ? AND count > 0",
                (from_user_id, character_id))
            from_item = await cursor.fetchone()
            
            if not from_item:
                return False
                
            inventory_id, count = from_item
            
            # Remove one from sender
            if count > 1:
                await self.db.execute(
                    "UPDATE inventory SET count = count - 1 WHERE id = ?",
                    (inventory_id,))
            else:
                await self.db.execute(
                    "DELETE FROM inventory WHERE id = ?",
                    (inventory_id,))
            
            # Add to recipient
            await self.db.execute(
                """INSERT INTO inventory (user_id, character_id, count, obtained_at)
                   VALUES (?, ?, 1, ?)
                   ON CONFLICT(user_id, character_id) DO UPDATE SET count = count + 1""",
                (to_user_id, character_id, datetime.now().isoformat()))
            
            await self.db.commit()
            
            # Invalidate caches
            await self.invalidate_player_cache(from_user_id)
            await self.invalidate_player_cache(to_user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error transferring character: {e}")
            return False

    async def get_player_items(self,
                               user_id: int,
                               item_type: str = None) -> List[Dict]:
        """Get player's items inventory"""
        try:
            if item_type:
                cursor = await self.db.execute(
                    """SELECT pi.id, pi.quantity, si.name, si.description, si.item_type,
                              si.effect_type, si.effect_value, si.duration_minutes, si.icon
                       FROM player_items pi
                       JOIN shop_items si ON pi.item_id = si.id
                       WHERE pi.user_id = ? AND si.item_type = ? AND pi.quantity > 0
                       ORDER BY si.name""", (user_id, item_type))
            else:
                cursor = await self.db.execute(
                    """SELECT pi.id, pi.quantity, si.name, si.description, si.item_type,
                              si.effect_type, si.effect_value, si.duration_minutes, si.icon
                       FROM player_items pi
                       JOIN shop_items si ON pi.item_id = si.id
                       WHERE pi.user_id = ? AND pi.quantity > 0
                       ORDER BY si.item_type, si.name""", (user_id, ))

            items = []
            for row in await cursor.fetchall():
                items.append({
                    'player_item_id': row[0],
                    'quantity': row[1],
                    'name': row[2],
                    'description': row[3],
                    'item_type': row[4],
                    'effect_type': row[5],
                    'effect_value': row[6],
                    'duration_minutes': row[7],
                    'icon': row[8]
                })
            return items
        except Exception as e:
            logger.error(f"Error getting player items: {e}")
            return []

    async def use_item(self, user_id: int, player_item_id: int) -> bool:
        """Use an item from player's inventory"""
        try:
            # Get item details
            cursor = await self.db.execute(
                """SELECT pi.quantity, si.effect_type, si.effect_value, si.duration_minutes
                   FROM player_items pi
                   JOIN shop_items si ON pi.item_id = si.id
                   WHERE pi.id = ? AND pi.user_id = ?""",
                (player_item_id, user_id))

            item = await cursor.fetchone()
            if not item or item[0] <= 0:
                return False

            quantity, effect_type, effect_value, duration_minutes = item

            # Apply effect if it has duration
            if duration_minutes > 0:
                from datetime import datetime, timedelta
                expires_at = datetime.now() + timedelta(
                    minutes=duration_minutes)

                await self.db.execute(
                    """INSERT INTO active_effects (user_id, effect_type, effect_value, expires_at)
                       VALUES (?, ?, ?, ?)""",
                    (user_id, effect_type, effect_value,
                     expires_at.isoformat()))

            # Reduce quantity
            if quantity > 1:
                await self.db.execute(
                    "UPDATE player_items SET quantity = quantity - 1 WHERE id = ?",
                    (player_item_id, ))
            else:
                await self.db.execute("DELETE FROM player_items WHERE id = ?",
                                      (player_item_id, ))

            await self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error using item: {e}")
            return False

    async def get_active_effects(self, user_id: int) -> List[Dict]:
        """Get player's active effects"""
        try:
            from datetime import datetime
            current_time = datetime.now().isoformat()

            # Clean expired effects
            await self.db.execute(
                "DELETE FROM active_effects WHERE expires_at < ?",
                (current_time, ))

            # Get active effects
            cursor = await self.db.execute(
                """SELECT effect_type, effect_value, expires_at
                   FROM active_effects
                   WHERE user_id = ? AND expires_at > ?
                   ORDER BY expires_at""", (user_id, current_time))

            effects = []
            for row in await cursor.fetchall():
                effects.append({
                    'effect_type': row[0],
                    'effect_value': row[1],
                    'expires_at': row[2]
                })

            await self.db.commit()
            return effects

        except Exception as e:
            logger.error(f"Error getting active effects: {e}")
            return []

    async def sell_character(self, user_id: int,
                             inventory_item_id: int) -> tuple[bool, str, int]:
        """Sell a character from player's inventory"""
        try:
            # Get character details and check ownership
            cursor = await self.db.execute(
                '''SELECT i.count, c.name, c.value, c.rarity
                   FROM inventory i
                   JOIN characters c ON i.character_id = c.id
                   WHERE i.id = ? AND i.user_id = ?''',
                (inventory_item_id, user_id))
            result = await cursor.fetchone()

            if not result:
                return False, "Personnage non trouvé dans votre inventaire", 0

            count, char_name, char_value, char_rarity = result

            if count <= 0:
                return False, "Vous n'avez pas ce personnage", 0

            # Calculate sell price with series and equipment bonuses
            base_sell_price = char_value
            
            # Apply series coin bonuses first
            set_bonuses = await self.get_active_set_bonuses(user_id)
            coin_multiplier = set_bonuses.get('coin_boost', 1.0)
            price_with_set_bonus = int(base_sell_price * coin_multiplier)
            
            # Then apply equipment bonuses
            sell_price = await self.apply_equipment_bonuses_to_coins(user_id, price_with_set_bonus)

            # Remove one copy from inventory
            if count == 1:
                # Remove the inventory entry completely
                await self.db.execute("DELETE FROM inventory WHERE id = ?",
                                      (inventory_item_id, ))
            else:
                # Decrease count by 1
                await self.db.execute(
                    "UPDATE inventory SET count = count - 1 WHERE id = ?",
                    (inventory_item_id, ))

            # Add coins to player
            await self.db.execute(
                "UPDATE players SET coins = coins + ? WHERE user_id = ?",
                (sell_price, user_id))

            await self.db.commit()

            return True, f"Vendu {char_name} ({char_rarity}) pour {sell_price} pièces", sell_price

        except Exception as e:
            return False, f"Erreur lors de la vente: {str(e)}", 0

    async def get_player_sellable_inventory(self,
                                            user_id: int,
                                            page: int = 1,
                                            limit: int = 10) -> List[Dict]:
        """Get player's sellable inventory with pagination"""
        offset = (page - 1) * limit
        cursor = await self.db.execute(
            '''SELECT i.id, c.name, c.anime, c.rarity, c.value, i.count, c.image_url
               FROM inventory i
               JOIN characters c ON i.character_id = c.id
               WHERE i.user_id = ? AND i.count > 0
               ORDER BY 
                   CASE c.rarity 
                       WHEN 'Mythic' THEN 1
                       WHEN 'Legendary' THEN 2
                       WHEN 'Epic' THEN 3
                       WHEN 'Rare' THEN 4
                       WHEN 'Common' THEN 5
                   END,
                   c.value DESC, c.name
               LIMIT ? OFFSET ?''', (user_id, limit, offset))

        rows = await cursor.fetchall()
        
        inventory = []
        for row in rows:
            inventory.append({
                'inventory_id': row[0],
                'character_name': row[1],
                'anime': row[2],
                'rarity': row[3],
                'value': row[4],
                'count': row[5],
                'image_url': row[6] if row[6] else ""
            })
        
        return inventory
        
    # Series Rewards Persistence Methods
    async def claim_series_completion_reward(self, user_id: int, anime_series: str, reward_type: str, reward_amount: int) -> bool:
        """Claim and save series completion reward to prevent duplicates"""
        try:
            # Check if reward already claimed
            cursor = await self.db.execute(
                "SELECT id FROM series_rewards_claimed WHERE user_id = ? AND anime_series = ?",
                (user_id, anime_series)
            )
            existing = await cursor.fetchone()
            
            if existing:
                return False  # Already claimed
            
            # Mark reward as claimed
            await self.db.execute(
                """INSERT INTO series_rewards_claimed 
                   (user_id, anime_series, reward_type, reward_amount)
                   VALUES (?, ?, ?, ?)""",
                (user_id, anime_series, reward_type, reward_amount)
            )
            
            # Award the reward
            if reward_type == "coins":
                await self.db.execute(
                    "UPDATE players SET coins = coins + ? WHERE user_id = ?",
                    (reward_amount, user_id)
                )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error claiming series reward: {e}")
            return False
    
    async def is_series_reward_claimed(self, user_id: int, anime_series: str) -> bool:
        """Check if user has already claimed reward for this series"""
        try:
            cursor = await self.db.execute(
                "SELECT id FROM series_rewards_claimed WHERE user_id = ? AND anime_series = ?",
                (user_id, anime_series)
            )
            result = await cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.error(f"Error checking series reward: {e}")
            return False
    
    async def get_user_claimed_series_rewards(self, user_id: int) -> List[Dict]:
        """Get all series rewards claimed by user"""
        try:
            cursor = await self.db.execute(
                """SELECT anime_series, reward_type, reward_amount, claimed_at
                   FROM series_rewards_claimed 
                   WHERE user_id = ?
                   ORDER BY claimed_at DESC""",
                (user_id,)
            )
            
            rewards = []
            for row in await cursor.fetchall():
                rewards.append({
                    'anime_series': row[0],
                    'reward_type': row[1],
                    'reward_amount': row[2],
                    'claimed_at': row[3]
                })
            return rewards
        except Exception as e:
            logger.error(f"Error getting user series rewards: {e}")
            return []
        return [{
            'inventory_id': row[0],
            'character_name': row[1],
            'anime': row[2],
            'rarity': row[3],
            'value': row[4],
            'count': row[5],
            'image_url': row[6]
        } for row in rows]

    async def execute_query(self, query: str, params: tuple = None):
        """Execute a raw SQL query"""
        async with self.db.execute(query, params or ()) as cursor:
            return await cursor.fetchall()

    async def get_equipped_characters(self, user_id: int) -> List[Dict]:
        """Get all equipped characters for a user"""
        cursor = await self.db.execute("""
            SELECT e.id, e.slot_number, i.id as inventory_id, c.name, c.anime, c.rarity, c.value
            FROM equipment e
            JOIN inventory i ON e.inventory_id = i.id
            JOIN characters c ON i.character_id = c.id
            WHERE e.user_id = ?
            ORDER BY e.slot_number
        """, (user_id,))
        rows = await cursor.fetchall()
        
        return [{
            'equipment_id': row[0],
            'slot_number': row[1],
            'inventory_id': row[2],
            'name': row[3],
            'anime': row[4],
            'rarity': row[5],
            'value': row[6]
        } for row in rows]

    async def get_equipped_count(self, user_id: int) -> int:
        """Get number of equipped characters for a user"""
        cursor = await self.db.execute("""
            SELECT COUNT(*) FROM equipment WHERE user_id = ?
        """, (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else 0

    async def get_equippable_characters(self, user_id: int) -> List[Dict]:
        """Get characters that can be equipped (Titan/Fusion/Secret, not already equipped)"""
        cursor = await self.db.execute("""
            SELECT i.id as inventory_id, c.name, c.anime, c.rarity, c.value
            FROM inventory i
            JOIN characters c ON i.character_id = c.id
            LEFT JOIN equipment e ON i.id = e.inventory_id
            WHERE i.user_id = ? AND c.rarity IN ('Titan', 'Fusion', 'Secret') AND e.id IS NULL
            ORDER BY 
                CASE c.rarity 
                    WHEN 'Secret' THEN 1 
                    WHEN 'Fusion' THEN 2 
                    WHEN 'Titan' THEN 3 
                END, c.name
        """, (user_id,))
        rows = await cursor.fetchall()
        
        return [{
            'inventory_id': row[0],
            'name': row[1],
            'anime': row[2],
            'rarity': row[3],
            'value': row[4]
        } for row in rows]

    async def equip_character(self, user_id: int, inventory_id: int) -> bool:
        """Equip a character to the next available slot"""
        try:
            # Check if user has room
            equipped_count = await self.get_equipped_count(user_id)
            if equipped_count >= 3:
                return False
            
            # Check if character is equippable
            cursor = await self.db.execute("""
                SELECT c.rarity FROM inventory i
                JOIN characters c ON i.character_id = c.id
                WHERE i.id = ? AND i.user_id = ?
            """, (inventory_id, user_id))
            result = await cursor.fetchone()
            
            if not result or result[0] not in ['Titan', 'Fusion', 'Secret']:
                return False
            
            # Find next available slot
            cursor = await self.db.execute("""
                SELECT slot_number FROM equipment WHERE user_id = ? ORDER BY slot_number
            """, (user_id,))
            used_slots = {row[0] for row in await cursor.fetchall()}
            
            next_slot = 1
            while next_slot in used_slots and next_slot <= 3:
                next_slot += 1
            
            if next_slot > 3:
                return False
            
            # Equip the character
            await self.db.execute("""
                INSERT INTO equipment (user_id, inventory_id, slot_number)
                VALUES (?, ?, ?)
            """, (user_id, inventory_id, next_slot))
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error equipping character: {e}")
            return False

    async def unequip_character(self, user_id: int, inventory_id: int) -> bool:
        """Unequip a character"""
        try:
            cursor = await self.db.execute("""
                DELETE FROM equipment 
                WHERE user_id = ? AND inventory_id = ?
            """, (user_id, inventory_id))
            
            if cursor.rowcount > 0:
                await self.db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unequipping character: {e}")
            return False

    # ===== CHARACTER HUNT SYSTEM =====
    
    async def get_player_hunt(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get player's active character hunt"""
        try:
            cursor = await self.db.execute("""
                SELECT target_character_id, progress, target_progress, 
                       daily_bonus_used, started_at, last_updated
                FROM character_hunts 
                WHERE user_id = ?
            """, (user_id,))
            result = await cursor.fetchone()
            
            if result:
                return {
                    'target_character_id': result[0],
                    'progress': result[1],
                    'target_progress': result[2],
                    'daily_bonus_used': bool(result[3]),
                    'started_at': result[4],
                    'last_updated': result[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting player hunt: {e}")
            return None
    
    async def start_character_hunt(self, user_id: int, character_id: int, target_progress: int) -> bool:
        """Start hunting a specific character"""
        try:
            # Remove any existing hunt
            await self.db.execute("DELETE FROM character_hunts WHERE user_id = ?", (user_id,))
            
            # Start new hunt
            await self.db.execute("""
                INSERT INTO character_hunts (user_id, target_character_id, target_progress)
                VALUES (?, ?, ?)
            """, (user_id, character_id, target_progress))
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error starting character hunt: {e}")
            return False
    
    async def update_hunt_progress(self, user_id: int, new_progress: int) -> bool:
        """Update hunt progress"""
        try:
            await self.db.execute("""
                UPDATE character_hunts 
                SET progress = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (new_progress, user_id))
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating hunt progress: {e}")
            return False
    
    async def mark_hunt_daily_bonus_used(self, user_id: int) -> bool:
        """Mark daily bonus as used for hunt"""
        try:
            await self.db.execute("""
                UPDATE character_hunts 
                SET daily_bonus_used = TRUE, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user_id,))
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error marking hunt daily bonus: {e}")
            return False
    
    async def stop_character_hunt(self, user_id: int) -> bool:
        """Stop active character hunt"""
        try:
            await self.db.execute("DELETE FROM character_hunts WHERE user_id = ?", (user_id,))
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error stopping character hunt: {e}")
            return False
    
    async def reset_daily_hunt_bonuses(self) -> bool:
        """Reset daily bonuses for all active hunts"""
        try:
            await self.db.execute("""
                UPDATE character_hunts 
                SET daily_bonus_used = FALSE, last_updated = CURRENT_TIMESTAMP
            """)
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error resetting hunt daily bonuses: {e}")
            return False
    
    async def search_characters_by_name(self, search_term: str) -> List[Dict[str, Any]]:
        """Search characters by name"""
        try:
            cursor = await self.db.execute("""
                SELECT id, name, anime, rarity, value, image_url
                FROM characters 
                WHERE name LIKE ? OR anime LIKE ?
                ORDER BY name
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            results = await cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'anime': row[2], 
                    'rarity': row[3],
                    'value': row[4],
                    'image_url': row[5]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching characters: {e}")
            return []

    async def calculate_equipment_bonuses(self, user_id: int) -> Dict[str, float]:
        """Calculate total bonuses from equipped characters and titles"""
        equipped_chars = await self.get_equipped_characters(user_id)
        
        bonuses = {
            'rarity_boost': 0.0,
            'coin_boost': 0.0,
            'daily_boost': 0.0,
            'achievement_boost': 0.0
        }
        
        # Equipment bonuses
        for char in equipped_chars:
            rarity = char['rarity']
            if rarity == 'Titan':
                bonuses['rarity_boost'] += 2.0  # +2% all rarities
            elif rarity == 'Fusion':
                bonuses['coin_boost'] += 5.0    # +5% coins everywhere
            elif rarity == 'Secret':
                bonuses['rarity_boost'] += 3.0  # +3% rarities
                bonuses['coin_boost'] += 3.0    # +3% coins
        
        # Title bonuses
        title_bonuses = await self.get_title_bonuses(user_id)
        for bonus_type, bonus_value in title_bonuses.items():
            if bonus_type in bonuses:
                bonuses[bonus_type] += bonus_value
        
        return bonuses

    async def apply_equipment_bonuses_to_coins(self, user_id: int, base_amount: int) -> int:
        """Apply equipment coin bonuses to an amount"""
        bonuses = await self.calculate_equipment_bonuses(user_id)
        coin_boost = bonuses.get('coin_boost', 0)
        
        if coin_boost > 0:
            bonus_amount = int(base_amount * (coin_boost / 100))
            return base_amount + bonus_amount
        
        return base_amount

    async def apply_equipment_bonuses_to_rarity_weights(self, user_id: int, base_weights: Dict[str, float]) -> Dict[str, float]:
        """Apply equipment rarity bonuses to rarity weights"""
        bonuses = await self.calculate_equipment_bonuses(user_id)
        rarity_boost = bonuses.get('rarity_boost', 0)
        
        if rarity_boost > 0:
            # Increase chances for rare tiers
            modified_weights = base_weights.copy()
            boost_multiplier = 1 + (rarity_boost / 100)
            
            # Boost ALL rare tiers (not just ultra-rare)
            for rarity in ['Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']:
                if rarity in modified_weights:
                    modified_weights[rarity] *= boost_multiplier
            
            # Reduce common slightly to balance
            if 'Common' in modified_weights:
                modified_weights['Common'] *= 0.9
            
            return modified_weights
        
        return base_weights

    async def close(self):
        """Close database connection"""
        if self.db:
            await self.db.close()
