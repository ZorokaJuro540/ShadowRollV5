#!/usr/bin/env python3
"""
Script final pour corriger TOUTES les valeurs des personnages selon les spécifications exactes
Applique les valeurs fixes et les plages aléatoires avec chiffres ronds
"""
import asyncio
import random
from core.database import DatabaseManager

def get_rounded_value_for_rarity(rarity):
    """Obtenir une valeur arrondie pour chaque rareté"""
    if rarity == 'Ultimate':
        return 500000  # Fixe - la plus haute valeur
    elif rarity == 'Evolve':
        return 200000  # Fixe
    elif rarity == 'Fusion':
        return 150000  # Fixe
    elif rarity == 'Titan':
        return 100000  # Fixe
    elif rarity == 'Mythic':
        # Plage 65,000-75,000 SC avec chiffres ronds
        base_values = [65000, 66000, 67000, 68000, 69000, 70000, 71000, 72000, 73000, 74000, 75000]
        return random.choice(base_values)
    elif rarity == 'Legendary':
        # Plage 40,000-50,000 SC avec chiffres ronds
        base_values = [40000, 41000, 42000, 43000, 44000, 45000, 46000, 47000, 48000, 49000, 50000]
        return random.choice(base_values)
    elif rarity == 'Epic':
        # Plage 15,000-25,000 SC avec chiffres ronds
        base_values = [15000, 16000, 17000, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000]
        return random.choice(base_values)
    elif rarity == 'Rare':
        # Plage 5,000-10,000 SC avec chiffres ronds
        base_values = [5000, 6000, 7000, 8000, 9000, 10000]
        return random.choice(base_values)
    elif rarity == 'Common':
        # Plage 500-1,000 SC avec chiffres ronds
        base_values = [500, 600, 700, 800, 900, 1000]
        return random.choice(base_values)
    else:
        return 1000  # Par défaut

async def apply_final_character_values():
    """Appliquer les valeurs finales exactes à TOUS les personnages"""
    print("🔧 Application des valeurs finales à TOUS les personnages...")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        # Obtenir TOUS les personnages
        cursor = await db_manager.db.execute("""
            SELECT id, name, anime, rarity, value 
            FROM characters 
            ORDER BY rarity, name
        """)
        all_characters = await cursor.fetchall()
        
        print(f"Trouvé {len(all_characters)} personnages à mettre à jour")
        
        updated_count = 0
        rarity_counts = {}
        
        for char_id, name, anime, rarity, current_value in all_characters:
            # Calculer la nouvelle valeur selon la rareté
            new_value = get_rounded_value_for_rarity(rarity)
            
            # Compter par rareté
            if rarity not in rarity_counts:
                rarity_counts[rarity] = 0
            rarity_counts[rarity] += 1
            
            # Mettre à jour seulement si la valeur change
            if current_value != new_value:
                await db_manager.db.execute("""
                    UPDATE characters 
                    SET value = ? 
                    WHERE id = ?
                """, (new_value, char_id))
                
                print(f"  ✓ {name} ({rarity}): {current_value:,} SC → {new_value:,} SC")
                updated_count += 1
            else:
                print(f"  ≡ {name} ({rarity}): {current_value:,} SC (déjà correct)")
        
        await db_manager.db.commit()
        
        print(f"\n✅ Mise à jour terminée: {updated_count} personnages modifiés")
        print("\n📊 Répartition par rareté:")
        for rarity, count in sorted(rarity_counts.items()):
            print(f"  {rarity}: {count} personnages")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
    
    finally:
        await db_manager.close()

async def verify_final_values():
    """Vérifier que toutes les valeurs sont correctes"""
    print("\n🔍 Vérification des valeurs finales...")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        # Vérifier par rareté
        rarities = ['Evolve', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']
        
        for rarity in rarities:
            cursor = await db_manager.db.execute("""
                SELECT COUNT(*), MIN(value), MAX(value), AVG(value)
                FROM characters 
                WHERE rarity = ?
            """, (rarity,))
            result = await cursor.fetchone()
            
            if result and result[0] > 0:
                count, min_val, max_val, avg_val = result
                print(f"  {rarity}: {count} personnages - {min_val:,} à {max_val:,} SC (moyenne: {avg_val:,.0f} SC)")
                
                # Vérifier si les valeurs sont dans les bonnes plages
                if rarity == 'Evolve' and (min_val != 200000 or max_val != 200000):
                    print(f"    ❌ ERREUR: Evolve devrait être 200,000 SC")
                elif rarity == 'Fusion' and (min_val != 150000 or max_val != 150000):
                    print(f"    ❌ ERREUR: Fusion devrait être 150,000 SC")
                elif rarity == 'Titan' and (min_val != 100000 or max_val != 100000):
                    print(f"    ❌ ERREUR: Titan devrait être 100,000 SC")
                elif rarity == 'Mythic' and (min_val < 65000 or max_val > 75000):
                    print(f"    ❌ ERREUR: Mythic devrait être entre 65,000-75,000 SC")
                elif rarity == 'Legendary' and (min_val < 40000 or max_val > 50000):
                    print(f"    ❌ ERREUR: Legendary devrait être entre 40,000-50,000 SC")
                elif rarity == 'Epic' and (min_val < 15000 or max_val > 25000):
                    print(f"    ❌ ERREUR: Epic devrait être entre 15,000-25,000 SC")
                elif rarity == 'Rare' and (min_val < 5000 or max_val > 10000):
                    print(f"    ❌ ERREUR: Rare devrait être entre 5,000-10,000 SC")
                elif rarity == 'Common' and (min_val < 500 or max_val > 1000):
                    print(f"    ❌ ERREUR: Common devrait être entre 500-1,000 SC")
                else:
                    print(f"    ✅ Valeurs correctes pour {rarity}")
        
        print(f"\n✅ Vérification terminée")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    
    finally:
        await db_manager.close()

async def show_sample_characters():
    """Afficher quelques exemples de personnages par rareté"""
    print("\n📋 Exemples de personnages avec leurs nouvelles valeurs:")
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        rarities = ['Evolve', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']
        
        for rarity in rarities:
            cursor = await db_manager.db.execute("""
                SELECT name, anime, value 
                FROM characters 
                WHERE rarity = ? 
                ORDER BY name 
                LIMIT 3
            """, (rarity,))
            characters = await cursor.fetchall()
            
            if characters:
                print(f"\n  {rarity}:")
                for name, anime, value in characters:
                    print(f"    • {name} ({anime}): {value:,} SC")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des exemples: {e}")
    
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    await apply_final_character_values()
    await verify_final_values()
    await show_sample_characters()

if __name__ == "__main__":
    asyncio.run(main())