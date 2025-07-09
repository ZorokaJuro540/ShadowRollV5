"""
Script pour augmenter drastiquement les prix de la boutique
Rend les articles vraiment chers (200,000+ SC) comme demandé
"""
import asyncio
import aiosqlite
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Nouveaux prix ultra-chers pour les articles
EXPENSIVE_SHOP_ITEMS = {
    # Prix énormément augmentés - maintenant il faut vendre plusieurs personnages Legendary/Mythic
    1: 200000,  # 🧪 Potion de Chance (était 1,500 SC)
    2: 300000,  # 💰 Multiplicateur Pièces (était 2,000 SC)
    3: 150000,  # ⚡ Reset Cooldown (était 1,000 SC)
    4: 400000,  # 🎲 Pack 5 Invocations (était 3,000 SC)
    5: 500000,  # 🔮 Garantie Épique (était 4,000 SC)
    6: 750000,  # 💎 Garantie Légendaire (était 7,500 SC)
    7: 1000000, # 🌟 Mega Pack (était 8,000 SC)
    8: 600000,  # 🔥 Boost Craft (était 5,000 SC)
}

async def update_shop_prices():
    """Mettre à jour tous les prix de la boutique pour qu'ils soient vraiment chers"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        try:
            # Récupérer les articles actuels
            cursor = await db.execute("SELECT id, name, price FROM shop_items_fixed ORDER BY id")
            current_items = await cursor.fetchall()
            
            logger.info(f"Mise à jour des prix pour {len(current_items)} articles...")
            
            print("\n🪙 ANCIENS PRIX vs NOUVEAUX PRIX")
            print("=" * 70)
            
            updated_count = 0
            
            for item_id, name, old_price in current_items:
                if item_id in EXPENSIVE_SHOP_ITEMS:
                    new_price = EXPENSIVE_SHOP_ITEMS[item_id]
                    
                    # Mettre à jour le prix
                    await db.execute(
                        "UPDATE shop_items_fixed SET price = ? WHERE id = ?",
                        (new_price, item_id)
                    )
                    
                    multiplier = new_price / old_price
                    print(f"{name:25} : {old_price:>8,} SC → {new_price:>9,} SC (x{multiplier:.0f})")
                    updated_count += 1
                else:
                    print(f"{name:25} : {old_price:>8,} SC (inchangé)")
            
            await db.commit()
            
            print("\n✅ MISE À JOUR TERMINÉE!")
            print(f"📊 {updated_count} articles mis à jour avec des prix ultra-chers")
            
            # Afficher les statistiques des nouveaux prix
            print("\n💰 ANALYSE DES NOUVEAUX PRIX:")
            print("=" * 50)
            
            cursor = await db.execute("SELECT MIN(price), MAX(price), AVG(price) FROM shop_items_fixed")
            min_price, max_price, avg_price = await cursor.fetchone()
            
            print(f"Prix minimum      : {min_price:>9,} SC")
            print(f"Prix maximum      : {max_price:>9,} SC")
            print(f"Prix moyen        : {avg_price:>9,.0f} SC")
            
            print("\n🔥 IMPACT ÉCONOMIQUE:")
            print("=" * 50)
            print("Pour acheter l'article le moins cher (150,000 SC):")
            print("- Il faut vendre ~3 personnages Legendary (50,000 SC chacun)")
            print("- Ou vendre ~2 personnages Mythic (70,000 SC chacun)")
            print("- Ou vendre 1 personnage Titan (100,000 SC)")
            print("")
            print("Pour acheter l'article le plus cher (1,000,000 SC):")
            print("- Il faut vendre ~20 personnages Legendary")
            print("- Ou vendre ~14 personnages Mythic")  
            print("- Ou vendre 10 personnages Titan")
            print("- Ou vendre 5 personnages Evolve (200,000 SC chacun)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            await db.rollback()
            raise

async def show_updated_prices():
    """Afficher les nouveaux prix après mise à jour"""
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        cursor = await db.execute('SELECT id, name, price, description FROM shop_items_fixed ORDER BY price ASC')
        items = await cursor.fetchall()
        
        print("\n🛒 NOUVEAUX PRIX DE LA BOUTIQUE:")
        print("=" * 80)
        for item_id, name, price, description in items:
            print(f'{item_id:2d}. {name:25} - {price:>9,} SC - {description}')

async def main():
    """Fonction principale"""
    print("💰 MISE À JOUR DES PRIX DE LA BOUTIQUE - VERSION ULTRA-CHÈRE")
    print("=" * 80)
    
    # Mettre à jour tous les prix
    await update_shop_prices()
    
    # Afficher les nouveaux prix
    await show_updated_prices()

if __name__ == "__main__":
    asyncio.run(main())