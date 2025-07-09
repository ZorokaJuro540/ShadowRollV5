"""
Script pour corriger EXACTEMENT les prix des personnages selon les spécifications
Applique les valeurs EXACTES définies par l'utilisateur
"""

import asyncio
import aiosqlite
import random

# Valeurs exactes définies
EXACT_VALUES = {
    'Ultimate': 500000,   # 500,000 SC exactement - la plus haute valeur
    'Evolve': 200000,     # 200,000 SC exactement
    'Secret': 200000,     # 200,000 SC exactement  
    'Fusion': 150000,     # 150,000 SC exactement
    'Titan': 100000,      # 100,000 SC exactement
    'Mythic': (65000, 75000),    # 65,000-75,000 SC en chiffres ronds
    'Legendary': (40000, 50000),  # 40,000-50,000 SC en chiffres ronds
    'Epic': (15000, 25000),      # 15,000-25,000 SC en chiffres ronds
    'Rare': (5000, 10000),       # 5,000-10,000 SC en chiffres ronds
    'Common': (500, 1000)        # 500-1,000 SC en chiffres ronds
}

def get_exact_value(rarity):
    """Obtenir la valeur exacte pour une rareté"""
    value_spec = EXACT_VALUES.get(rarity)
    
    if isinstance(value_spec, tuple):
        # Pour les plages, générer une valeur arrondie
        min_val, max_val = value_spec
        
        if rarity == 'Common':
            # Common: multiples de 100 (500, 600, 700, 800, 900, 1000)
            return random.choice([500, 600, 700, 800, 900, 1000])
        elif rarity == 'Rare':
            # Rare: multiples de 500 (5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000)
            return random.choice([i for i in range(5000, 10500, 500)])
        elif rarity == 'Epic':
            # Epic: multiples de 1000 (15000, 16000, 17000, ..., 25000)
            return random.choice([i for i in range(15000, 26000, 1000)])
        elif rarity == 'Legendary':
            # Legendary: multiples de 2000 (40000, 42000, 44000, 46000, 48000, 50000)
            return random.choice([i for i in range(40000, 52000, 2000)])
        elif rarity == 'Mythic':
            # Mythic: multiples de 2500 (65000, 67500, 70000, 72500, 75000)
            return random.choice([65000, 67500, 70000, 72500, 75000])
    else:
        # Pour les valeurs fixes
        return value_spec

async def apply_exact_character_values():
    """Appliquer les valeurs exactes à TOUS les personnages"""
    db_path = "shadow_roll.db"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Récupérer tous les personnages avec leur rareté
            async with db.execute("SELECT id, name, rarity, value FROM characters ORDER BY rarity, name") as cursor:
                characters = await cursor.fetchall()
            
            print(f"🎯 Correction des prix pour {len(characters)} personnages...")
            
            updates = []
            rarity_stats = {}
            
            for char_id, name, rarity, current_value in characters:
                new_value = get_exact_value(rarity)
                
                if new_value != current_value:
                    updates.append((new_value, char_id))
                    print(f"  📝 {name} ({rarity}): {current_value:,} SC → {new_value:,} SC")
                
                # Statistiques
                if rarity not in rarity_stats:
                    rarity_stats[rarity] = []
                rarity_stats[rarity].append(new_value)
            
            # Appliquer les mises à jour
            if updates:
                await db.executemany("UPDATE characters SET value = ? WHERE id = ?", updates)
                await db.commit()
                print(f"✅ {len(updates)} personnages mis à jour")
            else:
                print("✅ Tous les prix sont déjà corrects")
            
            # Afficher les statistiques par rareté
            print("\n📊 Statistiques par rareté:")
            for rarity in ['Secret', 'Evolve', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                if rarity in rarity_stats:
                    values = rarity_stats[rarity]
                    min_val = min(values)
                    max_val = max(values)
                    avg_val = sum(values) / len(values)
                    count = len(values)
                    
                    if min_val == max_val:
                        print(f"  {rarity}: {count} personnages à {min_val:,} SC (fixe)")
                    else:
                        print(f"  {rarity}: {count} personnages de {min_val:,} à {max_val:,} SC (moyenne: {avg_val:,.0f} SC)")
                        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback
        traceback.print_exc()

async def verify_exact_values():
    """Vérifier que toutes les valeurs sont correctes"""
    db_path = "shadow_roll.db"
    
    try:
        async with aiosqlite.connect(db_path) as db:
            print("\n🔍 Vérification des valeurs exactes...")
            
            all_correct = True
            
            for rarity in ['Secret', 'Evolve', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                async with db.execute("SELECT name, value FROM characters WHERE rarity = ? ORDER BY value DESC", (rarity,)) as cursor:
                    characters = await cursor.fetchall()
                
                if not characters:
                    continue
                
                value_spec = EXACT_VALUES.get(rarity)
                
                for name, value in characters:
                    is_correct = False
                    
                    if isinstance(value_spec, tuple):
                        min_val, max_val = value_spec
                        is_correct = min_val <= value <= max_val
                    else:
                        is_correct = value == value_spec
                    
                    if not is_correct:
                        print(f"❌ {name} ({rarity}): {value:,} SC - INCORRECT")
                        all_correct = False
                    else:
                        print(f"✅ {name} ({rarity}): {value:,} SC - OK")
            
            if all_correct:
                print("\n🎉 Toutes les valeurs sont correctes!")
            else:
                print("\n⚠️ Certaines valeurs nécessitent une correction")
                
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

async def main():
    """Fonction principale"""
    print("🎯 Correction des prix des personnages Shadow Roll")
    print("=" * 50)
    
    await apply_exact_character_values()
    await verify_exact_values()
    
    print("\n✅ Correction terminée!")

if __name__ == "__main__":
    asyncio.run(main())