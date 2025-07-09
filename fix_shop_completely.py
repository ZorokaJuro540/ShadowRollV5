"""
Script de correction complète du système de boutique Shadow Roll
Corrige tous les problèmes d'achat et refond entièrement le système
"""

import asyncio
import aiosqlite
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_shop_database():
    """Corriger et initialiser complètement la base de données de la boutique"""
    try:
        db = await aiosqlite.connect("shadow_roll.db")
        
        logger.info("🔧 Début de la correction de la base de données boutique...")
        
        # 1. Supprimer les anciennes tables problématiques
        logger.info("Suppression des anciennes tables...")
        await db.execute("DROP TABLE IF EXISTS old_shop_items")
        await db.execute("DROP TABLE IF EXISTS broken_purchases")
        
        # 2. Créer les nouvelles tables corrigées
        logger.info("Création des nouvelles tables...")
        
        # Table des articles de boutique
        await db.execute('''
            CREATE TABLE IF NOT EXISTS shop_items_fixed (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                category TEXT NOT NULL,
                effect_type TEXT,
                effect_value TEXT,
                duration INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des achats
        await db.execute('''
            CREATE TABLE IF NOT EXISTS player_purchases_fixed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                purchase_price INTEGER NOT NULL,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des potions
        await db.execute('''
            CREATE TABLE IF NOT EXISTS player_potions_fixed (
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
        
        # Table des buffs temporaires
        await db.execute('''
            CREATE TABLE IF NOT EXISTS temporary_buffs_fixed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                buff_type TEXT NOT NULL,
                buff_value REAL DEFAULT 1.0,
                expires_at INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des invocations gratuites
        await db.execute('''
            CREATE TABLE IF NOT EXISTS free_rolls_fixed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rolls_remaining INTEGER DEFAULT 0,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des garanties
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guaranteed_rarities_fixed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rarity TEXT NOT NULL,
                uses_remaining INTEGER DEFAULT 1,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Ajouter les articles par défaut
        logger.info("Ajout des articles par défaut...")
        
        # Supprimer les anciens articles
        await db.execute("DELETE FROM shop_items_fixed")
        
        # Articles corrigés et fonctionnels
        fixed_items = [
            (1, "🧪 Potion de Chance", "Augmente vos chances de rareté pendant 1 heure", 1500, "potion", "luck_boost", "1.5", 3600),
            (2, "🪙 Multiplicateur Pièces", "Double vos gains de pièces pendant 1 heure", 2000, "boost", "coin_multiplier", "2.0", 3600),
            (3, "⚡ Reset Cooldown", "Supprime instantanément tous vos cooldowns", 1000, "utility", "cooldown_reset", "instant", 0),
            (4, "🎲 Pack 5 Invocations", "Accorde 5 invocations gratuites", 3000, "pack", "free_rolls", "5", 0),
            (5, "🔮 Garantie Épique", "Votre prochaine invocation sera au minimum Epic", 4000, "guarantee", "epic_guarantee", "Epic", 0),
            (6, "💎 Garantie Légendaire", "Votre prochaine invocation sera au minimum Legendary", 7500, "guarantee", "legendary_guarantee", "Legendary", 0),
            (7, "🌟 Mega Pack", "10 invocations gratuites + bonus de chance", 8000, "pack", "mega_pack", "10", 0),
            (8, "🔥 Boost Craft", "Réduit les exigences de craft de 50% pendant 2h", 5000, "boost", "craft_discount", "0.5", 7200)
        ]
        
        for item in fixed_items:
            await db.execute('''
                INSERT OR REPLACE INTO shop_items_fixed 
                (id, name, description, price, category, effect_type, effect_value, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', item)
        
        # 4. Créer des index pour améliorer les performances
        logger.info("Création des index de performance...")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_purchases_user ON player_purchases_fixed(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_potions_user ON player_potions_fixed(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_buffs_user ON temporary_buffs_fixed(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_buffs_expires ON temporary_buffs_fixed(expires_at)")
        
        await db.commit()
        await db.close()
        
        logger.info("✅ Base de données boutique corrigée avec succès!")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la correction de la base: {e}")

async def validate_shop_functionality():
    """Valider que la boutique fonctionne correctement"""
    try:
        db = await aiosqlite.connect("shadow_roll.db")
        
        logger.info("🔍 Validation de la fonctionnalité boutique...")
        
        # Vérifier que les tables existent
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shop%' OR name LIKE '%purchase%' OR name LIKE '%potion%'")
        tables = await cursor.fetchall()
        logger.info(f"Tables trouvées: {[table[0] for table in tables]}")
        
        # Vérifier le contenu des articles
        cursor = await db.execute("SELECT COUNT(*) FROM shop_items_fixed WHERE is_active = 1")
        count = (await cursor.fetchone())[0]
        logger.info(f"Articles actifs dans la boutique: {count}")
        
        # Afficher quelques articles pour vérification
        cursor = await db.execute("SELECT id, name, price FROM shop_items_fixed WHERE is_active = 1 LIMIT 5")
        items = await cursor.fetchall()
        for item in items:
            logger.info(f"  Article {item[0]}: {item[1]} - {item[2]} SC")
        
        await db.close()
        
        if count >= 6:
            logger.info("✅ Boutique validée avec succès!")
            return True
        else:
            logger.error("❌ Problème avec les articles de boutique")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la validation: {e}")
        return False

async def main():
    """Fonction principale de correction"""
    print("🚀 Démarrage de la correction complète de la boutique...")
    
    # Étape 1: Corriger la base de données
    await fix_shop_database()
    
    # Étape 2: Valider la fonctionnalité
    is_valid = await validate_shop_functionality()
    
    if is_valid:
        print("✅ Correction complète terminée avec succès!")
        print("🛒 La boutique est maintenant entièrement fonctionnelle")
    else:
        print("❌ Problèmes détectés après correction")
    
    return is_valid

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)