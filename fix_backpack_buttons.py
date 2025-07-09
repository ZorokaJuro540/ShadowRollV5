"""
Script pour corriger les boutons du sac à dos et s'assurer que toutes les catégories sont visibles
"""

import asyncio
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_missing_tables():
    """Créer toutes les tables manquantes pour le sac à dos"""
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Table pour les effets temporaires (buffs)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS temporary_buffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                buff_type TEXT NOT NULL,
                buff_value REAL NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les équipements de joueur
        await db.execute('''
            CREATE TABLE IF NOT EXISTS player_equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                character_id INTEGER NOT NULL,
                slot_number INTEGER NOT NULL,
                equipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters(id),
                UNIQUE(user_id, character_id),
                UNIQUE(user_id, slot_number)
            )
        ''')
        
        # Table pour les titres de joueur
        await db.execute('''
            CREATE TABLE IF NOT EXISTS player_titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title_id INTEGER NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_selected BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (title_id) REFERENCES titles(id),
                UNIQUE(user_id, title_id)
            )
        ''')
        
        # Table pour les titres disponibles
        await db.execute('''
            CREATE TABLE IF NOT EXISTS titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                unlock_requirement TEXT,
                coin_bonus_percentage REAL DEFAULT 0,
                summon_bonus_percentage REAL DEFAULT 0,
                icon TEXT DEFAULT '🏆',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les potions/objets de joueur
        await db.execute('''
            CREATE TABLE IF NOT EXISTS player_potions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                item_type TEXT DEFAULT 'potion',
                effect_type TEXT,
                effect_value REAL DEFAULT 0,
                duration_minutes INTEGER DEFAULT 60,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.commit()
        logger.info("✅ Tables du sac à dos créées avec succès")

async def add_sample_titles():
    """Ajouter des titres d'exemple pour tester"""
    async with aiosqlite.connect('shadow_roll.db') as db:
        titles_data = [
            ("Collectionneur Débutant", "Obtenez 10 personnages différents", "collect_10_chars", 5.0, 0.0, "🏆"),
            ("Maître Collectionneur", "Obtenez 50 personnages différents", "collect_50_chars", 10.0, 0.0, "👑"),
            ("Légende Gacha", "Obtenez 100 personnages différents", "collect_100_chars", 15.0, 5.0, "⭐"),
            ("Roi des Ombres", "Obtenez un personnage Secret", "get_secret_char", 20.0, 10.0, "🌑"),
            ("Maître de la Fusion", "Créez 5 personnages Fusion", "craft_5_fusion", 12.0, 3.0, "🔮"),
            ("Théoricien de l'Ombre", "Terminez tous les succès", "complete_all_achievements", 25.0, 15.0, "🎓")
        ]
        
        for title_data in titles_data:
            try:
                await db.execute('''
                    INSERT OR IGNORE INTO titles (name, description, unlock_requirement, coin_bonus_percentage, summon_bonus_percentage, icon)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', title_data)
            except Exception as e:
                logger.warning(f"Titre déjà existant: {title_data[0]}")
        
        await db.commit()
        logger.info("✅ Titres d'exemple ajoutés")

async def add_sample_data_for_testing():
    """Ajouter des données d'exemple pour tester le sac à dos"""
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Ajouter un utilisateur de test
        test_user_id = 123456789
        
        # Ajouter un titre débloqué
        await db.execute('''
            INSERT OR IGNORE INTO player_titles (user_id, title_id, is_selected)
            VALUES (?, 1, TRUE)
        ''', (test_user_id,))
        
        # Ajouter une potion d'exemple
        await db.execute('''
            INSERT OR IGNORE INTO player_potions (user_id, item_name, quantity, item_type, effect_type, effect_value, duration_minutes)
            VALUES (?, 'Potion de Chance', 3, 'potion', 'luck_boost', 25.0, 30)
        ''', (test_user_id,))
        
        # Ajouter un effet temporaire
        await db.execute('''
            INSERT OR IGNORE INTO temporary_buffs (user_id, buff_type, buff_value, end_time)
            VALUES (?, 'coin_multiplier', 1.5, datetime('now', '+1 hour'))
        ''', (test_user_id,))
        
        await db.commit()
        logger.info("✅ Données d'exemple ajoutées pour le test")

async def verify_backpack_data():
    """Vérifier que les données du sac à dos sont correctement configurées"""
    async with aiosqlite.connect('shadow_roll.db') as db:
        print("\n🔍 Vérification des données du sac à dos:")
        
        # Vérifier les titres
        cursor = await db.execute('SELECT COUNT(*) FROM titles')
        titles_count = await cursor.fetchone()
        print(f"📋 Titres disponibles: {titles_count[0]}")
        
        # Vérifier les équipements
        cursor = await db.execute('SELECT COUNT(*) FROM player_equipment')
        equipment_count = await cursor.fetchone()
        print(f"⚔️ Équipements en cours: {equipment_count[0]}")
        
        # Vérifier les potions
        cursor = await db.execute('SELECT COUNT(*) FROM player_potions')
        potions_count = await cursor.fetchone()
        print(f"🧪 Potions stockées: {potions_count[0]}")
        
        # Vérifier les effets actifs
        cursor = await db.execute('SELECT COUNT(*) FROM temporary_buffs WHERE end_time > datetime("now")')
        effects_count = await cursor.fetchone()
        print(f"✨ Effets actifs: {effects_count[0]}")
        
        # Vérifier les titres des joueurs
        cursor = await db.execute('SELECT COUNT(*) FROM player_titles')
        player_titles_count = await cursor.fetchone()
        print(f"🏆 Titres débloqués: {player_titles_count[0]}")

async def main():
    """Fonction principale de correction"""
    logger.info("🚀 Début de la correction des boutons du sac à dos")
    
    try:
        await create_missing_tables()
        await add_sample_titles()
        await add_sample_data_for_testing()
        await verify_backpack_data()
        
        logger.info("✅ Correction du sac à dos terminée avec succès!")
        print("\n🎒 Le sac à dos est maintenant prêt avec toutes les catégories:")
        print("- 🎴 Personnages (collection existante)")
        print("- 🧪 Potions (objets de boutique)")
        print("- 🏆 Titres (système de progression)")
        print("- ⚔️ Équipement (personnages équipés)")
        print("- ✨ Effets (bonus temporaires)")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())