"""
Script pour configurer des données de sac à dos pour un utilisateur
S'assure qu'il y a des titres, potions, et effets à voir
"""
import asyncio
import aiosqlite
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_user_backpack():
    """Configurer des données de sac à dos pour un utilisateur réel"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            # Obtenir un ID utilisateur réel depuis la base de données
            cursor = await db.execute("SELECT user_id, username FROM players ORDER BY last_reroll DESC LIMIT 1")
            user_data = await cursor.fetchone()
            
            if not user_data:
                logger.info("Aucun utilisateur trouvé")
                return
            
            user_id, username = user_data
            logger.info(f"Configuration du sac à dos pour {username} (ID: {user_id})")
            
            # 1. Débloquer quelques titres
            cursor = await db.execute("SELECT id, display_name FROM titles LIMIT 3")
            titles = await cursor.fetchall()
            
            for title_id, title_name in titles:
                await db.execute('''
                    INSERT OR IGNORE INTO player_titles (user_id, title_id, unlocked_at)
                    VALUES (?, ?, ?)
                ''', (user_id, title_id, time.time()))
                logger.info(f"✅ Titre débloqué: {title_name}")
            
            # 2. Ajouter des potions
            potions_to_add = [
                ('Potion de Chance', 'luck_boost', 60, 3),
                ('Multiplicateur Pièces', 'coin_multiplier', 120, 1),
                ('Potion de Vitesse', 'speed_boost', 30, 2)
            ]
            
            for potion_name, effect_type, duration, quantity in potions_to_add:
                await db.execute('''
                    INSERT OR REPLACE INTO player_potions_fixed 
                    (user_id, potion_name, effect_type, duration_minutes, quantity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, potion_name, effect_type, duration, quantity))
                logger.info(f"✅ Potion ajoutée: {potion_name} x{quantity}")
            
            # 3. Ajouter des effets temporaires actifs
            expires_at = int(time.time()) + 7200  # 2 heures
            effects_to_add = [
                ('coin_multiplier', 1.5, expires_at),
                ('luck_boost', 1.2, expires_at + 1800),
                ('craft_discount', 0.5, expires_at + 3600)
            ]
            
            for buff_type, buff_value, exp_time in effects_to_add:
                await db.execute('''
                    INSERT OR REPLACE INTO temporary_buffs_fixed 
                    (user_id, buff_type, buff_value, expires_at, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (user_id, buff_type, buff_value, exp_time))
                logger.info(f"✅ Effet actif: {buff_type} (x{buff_value})")
            
            # 4. Équiper un personnage si possible
            cursor = await db.execute('''
                SELECT i.id, c.name, c.rarity 
                FROM inventory i
                JOIN characters c ON i.character_id = c.id
                WHERE i.user_id = ? AND c.rarity IN ('Titan', 'Fusion', 'Secret', 'Mythic')
                ORDER BY 
                    CASE c.rarity 
                        WHEN 'Secret' THEN 1 
                        WHEN 'Fusion' THEN 2 
                        WHEN 'Titan' THEN 3 
                        WHEN 'Mythic' THEN 4
                    END
                LIMIT 1
            ''', (user_id,))
            
            equippable = await cursor.fetchone()
            if equippable:
                inventory_id, char_name, char_rarity = equippable
                
                await db.execute('''
                    INSERT OR IGNORE INTO player_equipment 
                    (user_id, character_id, slot_number)
                    SELECT ?, character_id, 1
                    FROM inventory WHERE id = ?
                ''', (user_id, inventory_id))
                
                logger.info(f"✅ Personnage équipé: {char_name} ({char_rarity})")
            
            await db.commit()
            
            # Vérification finale
            print(f"\n📊 RÉSUMÉ POUR {username}:")
            print("=" * 50)
            
            # Titres
            cursor = await db.execute("SELECT COUNT(*) FROM player_titles WHERE user_id = ?", (user_id,))
            title_count = (await cursor.fetchone())[0]
            print(f"🏆 Titres débloqués: {title_count}")
            
            # Potions
            cursor = await db.execute("SELECT COUNT(*) FROM player_potions_fixed WHERE user_id = ?", (user_id,))
            potion_count = (await cursor.fetchone())[0]
            print(f"🧪 Potions: {potion_count}")
            
            # Équipement
            cursor = await db.execute("SELECT COUNT(*) FROM player_equipment WHERE user_id = ?", (user_id,))
            equipment_count = (await cursor.fetchone())[0]
            print(f"⚔️ Équipement: {equipment_count}")
            
            # Effets
            cursor = await db.execute("SELECT COUNT(*) FROM temporary_buffs_fixed WHERE user_id = ? AND is_active = 1", (user_id,))
            effects_count = (await cursor.fetchone())[0]
            print(f"✨ Effets actifs: {effects_count}")
            
            print(f"\n✅ Sac à dos configuré pour {username}!")
            print("Toutes les catégories devraient maintenant s'afficher avec du contenu.")
            
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(setup_user_backpack())