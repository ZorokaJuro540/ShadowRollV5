"""
Script pour corriger les valeurs incorrectes des personnages
Assure que tous les personnages ont les bonnes valeurs selon leur rareté
"""
import asyncio
import aiosqlite
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Valeurs correctes par rareté (valeurs fixes)
CORRECT_VALUES = {
    'Evolve': 200000,    # Valeur fixe
    'Fusion': 150000,    # Valeur fixe  
    'Titan': 100000,     # Valeur fixe
    'Secret': 150000,    # Valeur de base, peut varier
    # Les autres raretés gardent leurs valeurs aléatoirement assignées
}

async def fix_incorrect_values():
    """Corriger les valeurs incorrectes des personnages selon leur rareté"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            fixed_count = 0
            
            # Corriger les valeurs pour chaque rareté fixe
            for rarity, correct_value in CORRECT_VALUES.items():
                # Trouver les personnages avec de mauvaises valeurs
                cursor = await db.execute('''
                    SELECT id, name, value FROM characters 
                    WHERE rarity = ? AND value != ?
                ''', (rarity, correct_value))
                
                incorrect_chars = await cursor.fetchall()
                
                if incorrect_chars:
                    logger.info(f"Correction des valeurs pour {rarity} (devrait être {correct_value:,} SC):")
                    
                    for char_id, name, old_value in incorrect_chars:
                        # Mettre à jour la valeur
                        await db.execute('''
                            UPDATE characters SET value = ? WHERE id = ?
                        ''', (correct_value, char_id))
                        
                        logger.info(f"  {name}: {old_value:,} SC → {correct_value:,} SC")
                        fixed_count += 1
            
            await db.commit()
            
            logger.info(f"\n✅ Correction terminée!")
            logger.info(f"📊 {fixed_count} personnages corrigés")
            
            # Vérification finale
            print("\n📊 Vérification finale des valeurs par rareté:")
            print("=" * 60)
            
            cursor = await db.execute('''
                SELECT rarity, COUNT(*) as count, MIN(value) as min_val, MAX(value) as max_val
                FROM characters 
                WHERE rarity IN ('Evolve', 'Fusion', 'Titan', 'Secret')
                GROUP BY rarity 
                ORDER BY max_val DESC
            ''')
            results = await cursor.fetchall()
            
            for rarity, count, min_val, max_val in results:
                if min_val == max_val:
                    print(f"{rarity:>8} ({count:>2}): {min_val:>8,} SC (valeur fixe)")
                else:
                    print(f"{rarity:>8} ({count:>2}): {min_val:>8,} - {max_val:>8,} SC")
            
        except Exception as e:
            logger.error(f"Erreur lors de la correction: {e}")
            await db.rollback()
            raise

async def show_all_values():
    """Afficher toutes les valeurs après correction"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        cursor = await db.execute('''
            SELECT rarity, COUNT(*) as count, MIN(value) as min_val, MAX(value) as max_val, AVG(value) as avg_val
            FROM characters 
            GROUP BY rarity 
            ORDER BY avg_val DESC
        ''')
        
        results = await cursor.fetchall()
        
        print("\n💰 Toutes les valeurs par rareté après correction:")
        print("=" * 70)
        for rarity, count, min_val, max_val, avg_val in results:
            if min_val == max_val:
                print(f"{rarity:>10} ({count:>2}): {min_val:>8,} SC (valeur fixe)")
            else:
                print(f"{rarity:>10} ({count:>2}): {min_val:>8,} - {max_val:>8,} SC (moy: {avg_val:>8,.0f})")

async def main():
    """Fonction principale"""
    print("🔧 CORRECTION DES VALEURS INCORRECTES DES PERSONNAGES")
    print("=" * 60)
    
    # Corriger les valeurs incorrectes
    await fix_incorrect_values()
    
    # Afficher toutes les valeurs finales
    await show_all_values()

if __name__ == "__main__":
    asyncio.run(main())