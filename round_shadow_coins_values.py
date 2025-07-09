"""
Script pour arrondir toutes les valeurs Shadow Coins à des chiffres ronds
Arrondit par 100 ou 1000 selon la valeur pour des chiffres plus simples
"""
import asyncio
import aiosqlite
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def round_to_nice_number(value):
    """Arrondit une valeur à un chiffre rond selon sa magnitude"""
    if value >= 100000:
        # Pour les valeurs > 100K, arrondir aux 10K
        return round(value / 10000) * 10000
    elif value >= 10000:
        # Pour les valeurs > 10K, arrondir aux 1K
        return round(value / 1000) * 1000
    elif value >= 1000:
        # Pour les valeurs > 1K, arrondir aux 100
        return round(value / 100) * 100
    else:
        # Pour les valeurs < 1K, arrondir aux 50
        return round(value / 50) * 50

async def round_all_character_values():
    """Arrondit toutes les valeurs des personnages à des chiffres ronds"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            # Récupérer tous les personnages avec leurs valeurs actuelles
            cursor = await db.execute("SELECT id, name, rarity, value FROM characters")
            characters = await cursor.fetchall()
            
            logger.info(f"Traitement de {len(characters)} personnages...")
            
            updated_count = 0
            
            for character_id, name, rarity, current_value in characters:
                # Calculer la nouvelle valeur arrondie
                rounded_value = round_to_nice_number(current_value)
                
                # Mettre à jour si la valeur a changé
                if rounded_value != current_value:
                    await db.execute(
                        "UPDATE characters SET value = ? WHERE id = ?",
                        (rounded_value, character_id)
                    )
                    
                    logger.info(f"{name} ({rarity}): {current_value:,} SC → {rounded_value:,} SC")
                    updated_count += 1
                else:
                    logger.info(f"{name} ({rarity}): {current_value:,} SC (inchangé)")
            
            await db.commit()
            
            logger.info(f"\n✅ Mise à jour terminée!")
            logger.info(f"📊 {updated_count} personnages mis à jour avec des valeurs arrondies")
            logger.info(f"📊 {len(characters) - updated_count} personnages gardent leur valeur")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            await db.rollback()
            raise

async def show_current_values():
    """Affiche les valeurs actuelles pour vérification"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        cursor = await db.execute("""
            SELECT rarity, COUNT(*) as count, MIN(value) as min_val, MAX(value) as max_val, AVG(value) as avg_val
            FROM characters 
            GROUP BY rarity 
            ORDER BY avg_val DESC
        """)
        
        results = await cursor.fetchall()
        
        print("\n📊 Valeurs actuelles par rareté:")
        print("=" * 60)
        for rarity, count, min_val, max_val, avg_val in results:
            print(f"{rarity:>10} ({count:>2}): {min_val:>8,} - {max_val:>8,} SC (moy: {avg_val:>8,.0f})")

async def main():
    """Fonction principale"""
    print("🪙 Arrondi des valeurs Shadow Coins à des chiffres ronds")
    print("=" * 60)
    
    # Afficher les valeurs actuelles
    await show_current_values()
    
    # Arrondir toutes les valeurs
    await round_all_character_values()
    
    # Afficher les nouvelles valeurs
    print("\n📊 Nouvelles valeurs après arrondi:")
    await show_current_values()

if __name__ == "__main__":
    asyncio.run(main())