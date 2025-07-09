"""
Script pour mettre à jour les valeurs Shadow Coins de tous les personnages
selon les nouvelles spécifications de rareté
"""
import asyncio
import aiosqlite
import random
import logging

# Configuration des nouvelles valeurs par rareté
RARITY_VALUES = {
    'Evolve': 200000,  # Valeur fixe
    'Fusion': 150000,  # Valeur fixe
    'Titan': 100000,   # Valeur fixe
    'Mythic': (65000, 75000),    # Range
    'Legendary': (40000, 50000), # Range
    'Epic': (15000, 25000),      # Range
    'Rare': (5000, 10000),       # Range
    'Common': (500, 1000)        # Range
}

async def update_character_values():
    """Met à jour toutes les valeurs des personnages selon les nouvelles spécifications"""
    
    db_path = "shadow_roll.db"
    
    try:
        # Connexion à la base de données
        db = await aiosqlite.connect(db_path)
        
        print("🔍 Récupération de tous les personnages...")
        
        # Récupérer tous les personnages avec leur rareté
        cursor = await db.execute("""
            SELECT id, name, rarity, value, anime 
            FROM characters 
            ORDER BY rarity, name
        """)
        characters = await cursor.fetchall()
        
        print(f"📊 {len(characters)} personnages trouvés")
        
        updated_count = 0
        
        for char_id, name, rarity, current_value, anime in characters:
            # Calculer la nouvelle valeur selon la rareté
            if rarity in RARITY_VALUES:
                value_config = RARITY_VALUES[rarity]
                
                if isinstance(value_config, tuple):
                    # Range de valeurs - choisir aléatoirement dans la plage
                    min_val, max_val = value_config
                    new_value = random.randint(min_val, max_val)
                else:
                    # Valeur fixe
                    new_value = value_config
                
                # Mettre à jour seulement si la valeur a changé
                if new_value != current_value:
                    await db.execute("""
                        UPDATE characters 
                        SET value = ? 
                        WHERE id = ?
                    """, (new_value, char_id))
                    
                    print(f"✅ {name} ({rarity}): {current_value:,} SC → {new_value:,} SC")
                    updated_count += 1
                else:
                    print(f"⏸️ {name} ({rarity}): {current_value:,} SC (inchangé)")
            else:
                print(f"⚠️ Rareté inconnue pour {name}: {rarity}")
        
        # Valider les changements
        await db.commit()
        await db.close()
        
        print(f"\n🎉 Mise à jour terminée!")
        print(f"📈 {updated_count} personnages mis à jour")
        print(f"💰 Nouvelles valeurs appliquées selon les spécifications de rareté")
        
        # Afficher un résumé par rareté
        print(f"\n📋 Résumé des nouvelles valeurs:")
        for rarity, value_config in RARITY_VALUES.items():
            if isinstance(value_config, tuple):
                min_val, max_val = value_config
                print(f"  {rarity}: {min_val:,} - {max_val:,} SC")
            else:
                print(f"  {rarity}: {value_config:,} SC")
                
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        import traceback
        traceback.print_exc()

async def show_current_values():
    """Affiche les valeurs actuelles pour vérification"""
    
    db_path = "shadow_roll.db"
    
    try:
        db = await aiosqlite.connect(db_path)
        
        print("📊 Valeurs actuelles par rareté:")
        
        for rarity in RARITY_VALUES.keys():
            cursor = await db.execute("""
                SELECT name, value, anime
                FROM characters 
                WHERE rarity = ?
                ORDER BY value DESC
                LIMIT 5
            """, (rarity,))
            chars = await cursor.fetchall()
            
            if chars:
                print(f"\n{rarity}:")
                for name, value, anime in chars:
                    print(f"  {name} ({anime}): {value:,} SC")
        
        await db.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

async def main():
    """Fonction principale"""
    print("🪙 MISE À JOUR DES VALEURS SHADOW COINS 🪙")
    print("=" * 50)
    
    # Afficher les valeurs actuelles
    print("AVANT:")
    await show_current_values()
    
    print("\n" + "=" * 50)
    
    # Effectuer la mise à jour
    await update_character_values()
    
    print("\n" + "=" * 50)
    
    # Afficher les nouvelles valeurs
    print("APRÈS:")
    await show_current_values()

if __name__ == "__main__":
    asyncio.run(main())