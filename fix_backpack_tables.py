"""
Script pour réparer les tables manquantes du système de sac à dos
Crée toutes les tables nécessaires pour que les catégories s'affichent correctement
"""
import asyncio
import aiosqlite
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_missing_backpack_tables():
    """Créer toutes les tables manquantes pour le sac à dos"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            # Table player_equipment (manquante)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS player_equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    character_id INTEGER NOT NULL,
                    slot_number INTEGER NOT NULL,
                    equipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters(id),
                    UNIQUE(user_id, slot_number)
                )
            ''')
            logger.info("✅ Table player_equipment créée")
            
            # Vérifier/créer la table equipment (principale)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS equipment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    character_id INTEGER NOT NULL,
                    slot_number INTEGER NOT NULL DEFAULT 1,
                    equipped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            ''')
            logger.info("✅ Table equipment vérifiée/créée")
            
            # Assurer que les tables de potions existent avec les bonnes structures
            await db.execute('''
                CREATE TABLE IF NOT EXISTS player_potions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    potion_name TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 60,
                    quantity INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("✅ Table player_potions vérifiée/créée")
            
            # Table des effets actifs
            await db.execute('''
                CREATE TABLE IF NOT EXISTS active_effects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    effect_name TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    effect_value REAL DEFAULT 1.0,
                    expires_at INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("✅ Table active_effects vérifiée/créée")
            
            await db.commit()
            logger.info("🎒 Toutes les tables du sac à dos sont prêtes!")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des tables: {e}")
            await db.rollback()
            raise

async def add_sample_data_for_testing():
    """Ajouter quelques données de test pour vérifier que le sac à dos fonctionne"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            # Ajouter une potion de test
            await db.execute('''
                INSERT OR IGNORE INTO player_potions_fixed 
                (user_id, potion_name, effect_type, duration_minutes, quantity)
                VALUES (123456789, 'Potion de Chance', 'luck_boost', 60, 2)
            ''')
            
            # Ajouter un effet temporaire de test
            import time
            expires_at = int(time.time()) + 3600  # 1 heure
            await db.execute('''
                INSERT OR IGNORE INTO temporary_buffs_fixed 
                (user_id, buff_type, buff_value, expires_at)
                VALUES (123456789, 'coin_multiplier', 2.0, ?)
            ''', (expires_at,))
            
            await db.commit()
            logger.info("📦 Données de test ajoutées")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des données de test: {e}")

async def verify_backpack_functionality():
    """Vérifier que toutes les tables du sac à dos fonctionnent"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        print("\n🔍 VÉRIFICATION DES FONCTIONNALITÉS DU SAC À DOS")
        print("=" * 60)
        
        # Vérifier chaque catégorie
        categories = {
            'Personnages': 'SELECT COUNT(*) FROM inventory',
            'Potions': 'SELECT COUNT(*) FROM player_potions_fixed',
            'Titres': 'SELECT COUNT(*) FROM titles',
            'Équipement': 'SELECT COUNT(*) FROM player_equipment',
            'Effets': 'SELECT COUNT(*) FROM temporary_buffs_fixed'
        }
        
        for category, query in categories.items():
            try:
                cursor = await db.execute(query)
                count = (await cursor.fetchone())[0]
                print(f"✅ {category:12}: {count:>3} entrées disponibles")
            except Exception as e:
                print(f"❌ {category:12}: Erreur - {e}")
        
        # Vérifier les titres débloqués
        try:
            cursor = await db.execute('SELECT COUNT(*) FROM player_titles')
            unlocked_titles = (await cursor.fetchone())[0]
            print(f"🏆 Titres débloqués: {unlocked_titles}")
        except:
            print("❌ Impossible de vérifier les titres débloqués")

async def main():
    """Fonction principale"""
    print("🎒 RÉPARATION DU SYSTÈME DE SAC À DOS")
    print("=" * 50)
    
    # Créer les tables manquantes
    await create_missing_backpack_tables()
    
    # Ajouter des données de test
    await add_sample_data_for_testing()
    
    # Vérifier que tout fonctionne
    await verify_backpack_functionality()
    
    print("\n✅ RÉPARATION TERMINÉE!")
    print("Le sac à dos devrait maintenant afficher toutes les catégories:")
    print("- 👤 Personnages (collection de cartes)")
    print("- 🧪 Potions (objets de la boutique)")
    print("- 🏆 Titres (débloqués par succès)")
    print("- ⚔️ Équipement (personnages équipés)")
    print("- ✨ Effets (buffs temporaires actifs)")

if __name__ == "__main__":
    asyncio.run(main())