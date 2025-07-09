"""
Commande Admin pour Modifier les Valeurs des Raretés Shadow Roll
Permet de modifier les valeurs de tous les personnages d'une rareté spécifique
"""

import asyncio
import aiosqlite
import random
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class RarityValueUpdater:
    def __init__(self, db_path: str = "shadow_roll.db"):
        self.db_path = db_path

    async def get_rarity_stats(self) -> Dict:
        """Obtenir les statistiques actuelles des raretés"""
        async with aiosqlite.connect(self.db_path) as db:
            query = """
            SELECT rarity, COUNT(*) as count, MIN(value) as min_val, MAX(value) as max_val, AVG(value) as avg_val
            FROM characters 
            GROUP BY rarity 
            ORDER BY 
                CASE rarity
                    WHEN 'Common' THEN 1
                    WHEN 'Rare' THEN 2
                    WHEN 'Epic' THEN 3
                    WHEN 'Legendary' THEN 4
                    WHEN 'Mythic' THEN 5
                    WHEN 'Titan' THEN 6
                    WHEN 'Fusion' THEN 7
                    WHEN 'Evolve' THEN 8
                    WHEN 'Secret' THEN 9
                    WHEN 'Ultimate' THEN 10
                END
            """
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                
            stats = {}
            for row in rows:
                rarity, count, min_val, max_val, avg_val = row
                stats[rarity] = {
                    'count': count,
                    'min_value': min_val,
                    'max_value': max_val,
                    'avg_value': round(avg_val, 0) if avg_val else 0
                }
            
            return stats

    async def update_rarity_values(self, rarity: str, min_value: int, max_value: int) -> Dict:
        """Mettre à jour les valeurs de tous les personnages d'une rareté"""
        async with aiosqlite.connect(self.db_path) as db:
            # Récupérer tous les personnages de cette rareté
            query = "SELECT id, name FROM characters WHERE rarity = ?"
            async with db.execute(query, (rarity,)) as cursor:
                characters = await cursor.fetchall()
            
            if not characters:
                return {"error": f"Aucun personnage trouvé avec la rareté '{rarity}'"}
            
            updated_count = 0
            updates = []
            
            # Générer de nouvelles valeurs aléatoirement dans la plage
            for char_id, char_name in characters:
                new_value = self._generate_round_value(min_value, max_value)
                
                # Mettre à jour dans la base de données
                await db.execute(
                    "UPDATE characters SET value = ? WHERE id = ?",
                    (new_value, char_id)
                )
                
                updates.append({
                    'id': char_id,
                    'name': char_name,
                    'new_value': new_value
                })
                updated_count += 1
            
            await db.commit()
            
            return {
                "success": True,
                "rarity": rarity,
                "updated_count": updated_count,
                "min_value": min_value,
                "max_value": max_value,
                "updates": updates[:10]  # Montrer seulement les 10 premiers
            }

    def _generate_round_value(self, min_val: int, max_val: int) -> int:
        """Générer une valeur arrondie dans la plage"""
        value = random.randint(min_val, max_val)
        
        # Arrondir selon la magnitude
        if value >= 100000:
            return round(value / 10000) * 10000  # Arrondi aux 10k
        elif value >= 10000:
            return round(value / 1000) * 1000   # Arrondi aux 1k
        elif value >= 1000:
            return round(value / 500) * 500     # Arrondi aux 500
        else:
            return round(value / 100) * 100     # Arrondi aux 100

    async def show_current_values(self) -> str:
        """Afficher les valeurs actuelles de toutes les raretés"""
        stats = await self.get_rarity_stats()
        
        result = "📊 **VALEURS ACTUELLES DES RARETÉS** 📊\n\n"
        
        for rarity, data in stats.items():
            result += f"**{rarity}** ({data['count']} personnages)\n"
            result += f"  └ Min: {data['min_value']:,} SC - Max: {data['max_value']:,} SC\n"
            result += f"  └ Moyenne: {data['avg_value']:,} SC\n\n"
        
        return result

async def setup_rarity_commands(bot):
    """Configurer les commandes de gestion des raretés"""
    
    updater = RarityValueUpdater()
    
    @bot.command(name='rarityvalues', aliases=['rv', 'showvalues'])
    async def show_rarity_values(ctx):
        """Afficher les valeurs actuelles des raretés - Admin seulement"""
        from core.config import BotConfig
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Cette commande est réservée aux administrateurs.")
            return
        
        try:
            values_text = await updater.show_current_values()
            await ctx.send(f"```\n{values_text}\n```")
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    @bot.command(name='updatevalues', aliases=['uv', 'setvalues'])
    async def update_rarity_values(ctx, rarity: str = None, min_value: int = None, max_value: int = None):
        """
        Mettre à jour les valeurs d'une rareté
        Usage: !updatevalues <rareté> <valeur_min> <valeur_max>
        Exemple: !updatevalues Rare 15000 25000
        """
        from core.config import BotConfig
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Cette commande est réservée aux administrateurs.")
            return
        
        if not all([rarity, min_value, max_value]):
            await ctx.send(
                "❌ Usage: `!updatevalues <rareté> <valeur_min> <valeur_max>`\n"
                "Exemple: `!updatevalues Rare 15000 25000`\n\n"
                "Raretés disponibles: Common, Rare, Epic, Legendary, Mythic, Titan, Fusion, Evolve, Secret, Ultimate"
            )
            return
        
        if min_value >= max_value:
            await ctx.send("❌ La valeur minimale doit être inférieure à la valeur maximale.")
            return
        
        # Vérifier que la rareté existe
        valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Evolve', 'Secret', 'Ultimate']
        if rarity not in valid_rarities:
            await ctx.send(f"❌ Rareté invalide. Raretés disponibles: {', '.join(valid_rarities)}")
            return
        
        try:
            await ctx.send(f"🔄 Mise à jour des valeurs pour la rareté **{rarity}** ({min_value:,} - {max_value:,} SC)...")
            
            result = await updater.update_rarity_values(rarity, min_value, max_value)
            
            if result.get("error"):
                await ctx.send(f"❌ {result['error']}")
                return
            
            # Message de confirmation
            response = f"✅ **MISE À JOUR TERMINÉE**\n\n"
            response += f"🎯 **Rareté**: {result['rarity']}\n"
            response += f"📊 **Personnages mis à jour**: {result['updated_count']}\n"
            response += f"💰 **Nouvelle plage**: {result['min_value']:,} - {result['max_value']:,} SC\n\n"
            
            if result.get("updates"):
                response += "📝 **Exemples de mise à jour**:\n"
                for update in result["updates"][:5]:
                    response += f"• {update['name']}: {update['new_value']:,} SC\n"
                
                if result['updated_count'] > 5:
                    response += f"... et {result['updated_count'] - 5} autres personnages\n"
            
            await ctx.send(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des valeurs: {e}")
            await ctx.send(f"❌ Erreur lors de la mise à jour: {e}")

async def main():
    """Test de la fonctionnalité"""
    updater = RarityValueUpdater()
    
    print("=== VALEURS ACTUELLES ===")
    values = await updater.show_current_values()
    print(values)
    
    print("\n=== TEST MISE À JOUR ===")
    result = await updater.update_rarity_values("Rare", 15000, 25000)
    print(f"Résultat: {result}")

if __name__ == "__main__":
    asyncio.run(main())