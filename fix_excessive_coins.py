"""
Script pour corriger les montants excessifs de Shadow Coins
"""

import asyncio
import aiosqlite

async def fix_excessive_coins():
    """Corriger les montants de coins anormalement élevés"""
    try:
        db = await aiosqlite.connect('shadow_roll.db')
        
        # Définir un seuil raisonnable (1 million)
        max_reasonable_coins = 1000000
        
        # Trouver les joueurs avec des montants excessifs
        cursor = await db.execute(
            'SELECT user_id, username, coins FROM players WHERE coins > ?', 
            (max_reasonable_coins,)
        )
        excessive_players = await cursor.fetchall()
        
        print(f"🔍 Trouvé {len(excessive_players)} joueurs avec des montants excessifs:")
        
        for user_id, username, coins in excessive_players:
            print(f"  - {username}: {coins:,} SC")
            
            # Réinitialiser à 100,000 SC (montant généreux mais raisonnable)
            new_amount = 100000
            
            await db.execute(
                'UPDATE players SET coins = ? WHERE user_id = ?', 
                (new_amount, user_id)
            )
            
            print(f"    ✅ Corrigé à: {new_amount:,} SC")
        
        await db.commit()
        
        # Vérification finale
        cursor = await db.execute(
            'SELECT COUNT(*) FROM players WHERE coins > ?', 
            (max_reasonable_coins,)
        )
        remaining = await cursor.fetchone()
        
        print(f"\n✅ Correction terminée. Joueurs avec +1M coins: {remaining[0]}")
        
        await db.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_excessive_coins())