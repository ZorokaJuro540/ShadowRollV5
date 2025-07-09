"""
Commandes Legacy pour la Gestion des Séries - Shadow Roll Bot
Commandes textuelles rapides pour les admins expérimentés
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List

from core.config import BotConfig
from modules.utils import get_display_name

logger = logging.getLogger(__name__)

async def setup_legacy_series_commands(bot):
    """Setup des commandes legacy pour les séries"""
    
    @bot.command(name='createseries', aliases=['newseries'])
    async def create_series_command(ctx, series_name: str, bonus_type: str = None, bonus_value: float = 0.0):
        """Créer une nouvelle série rapidement
        
        Usage: !createseries "Nom Série" [coins/rarity] [valeur]
        Exemple: !createseries "Jujutsu Kaisen" coins 8.0
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Vérifier si la série existe déjà
            async with bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (series_name,)) as cursor:
                exists = (await cursor.fetchone())[0] > 0
            
            if exists:
                await ctx.send(f"❌ La série '{series_name}' existe déjà!")
                return
            
            # Valider le type de bonus
            if bonus_type and bonus_type not in ['coins', 'rarity']:
                await ctx.send("❌ Type de bonus invalide. Utilisez 'coins' ou 'rarity'")
                return
            
            # Sauvegarder temporairement les infos de bonus
            if not hasattr(bot, 'temp_series_bonuses'):
                bot.temp_series_bonuses = {}
            
            if bonus_type:
                bot.temp_series_bonuses[series_name] = {
                    'bonus_type': bonus_type,
                    'bonus_value': bonus_value
                }
            
            embed = discord.Embed(
                title="✅ Série Préparée",
                description=(f"**{series_name}** préparée!\n"
                           f"Bonus: {bonus_type} +{bonus_value}% (si spécifié)\n\n"
                           f"Utilisez `!assign` pour ajouter des personnages."),
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur création série: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='assign', aliases=['assignchar'])
    async def assign_character_command(ctx, character_id: int, series_name: str):
        """Assigner un personnage à une série
        
        Usage: !assign [ID_personnage] "Nom Série"
        Exemple: !assign 25 "Jujutsu Kaisen"
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Vérifier que le personnage existe
            async with bot.db.db.execute("""
                SELECT name, anime FROM characters WHERE id = ?
            """, (character_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                await ctx.send(f"❌ Aucun personnage avec l'ID {character_id}")
                return
            
            char_name, old_series = result
            
            # Assigner le personnage à la série
            await bot.db.db.execute("""
                UPDATE characters SET anime = ? WHERE id = ?
            """, (series_name, character_id))
            
            await bot.db.db.commit()
            
            old_text = f" (était dans '{old_series}')" if old_series else ""
            embed = discord.Embed(
                title="✅ Assignation Réussie",
                description=f"**{char_name}** assigné à '{series_name}'{old_text}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur assignation: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='assignmulti', aliases=['massassign'])
    async def assign_multiple_command(ctx, series_name: str, *character_ids):
        """Assigner plusieurs personnages à une série
        
        Usage: !assignmulti "Nom Série" [ID1] [ID2] [ID3]...
        Exemple: !assignmulti "Jujutsu Kaisen" 25 26 27 28
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        if not character_ids:
            await ctx.send("❌ Veuillez spécifier au moins un ID de personnage")
            return
        
        try:
            assigned_count = 0
            assigned_names = []
            
            for char_id_str in character_ids:
                try:
                    char_id = int(char_id_str)
                    
                    # Vérifier que le personnage existe
                    async with bot.db.db.execute("""
                        SELECT name FROM characters WHERE id = ?
                    """, (char_id,)) as cursor:
                        result = await cursor.fetchone()
                    
                    if result:
                        # Assigner le personnage
                        await bot.db.db.execute("""
                            UPDATE characters SET anime = ? WHERE id = ?
                        """, (series_name, char_id))
                        
                        assigned_names.append(result[0])
                        assigned_count += 1
                    else:
                        await ctx.send(f"⚠️ Personnage ID {char_id} introuvable, ignoré")
                        
                except ValueError:
                    await ctx.send(f"⚠️ ID invalide '{char_id_str}', ignoré")
            
            await bot.db.db.commit()
            
            if assigned_count > 0:
                names_text = ", ".join(assigned_names[:5])
                if len(assigned_names) > 5:
                    names_text += f" et {len(assigned_names) - 5} autres"
                
                embed = discord.Embed(
                    title="✅ Assignation Multiple Réussie",
                    description=f"{assigned_count} personnages assignés à '{series_name}'\n\n**Assignés:** {names_text}",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Aucun personnage n'a pu être assigné")
                
        except Exception as e:
            logger.error(f"Erreur assignation multiple: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='renameseries', aliases=['renameanime'])
    async def rename_series_command(ctx, old_name: str, new_name: str):
        """Renommer une série
        
        Usage: !renameseries "Ancien Nom" "Nouveau Nom"
        Exemple: !renameseries "One Piece" "One Piece: New World"
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Vérifier que l'ancienne série existe
            async with bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (old_name,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count == 0:
                await ctx.send(f"❌ Aucune série nommée '{old_name}'")
                return
            
            # Vérifier que le nouveau nom n'existe pas déjà
            async with bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (new_name,)) as cursor:
                exists = (await cursor.fetchone())[0] > 0
            
            if exists and new_name != old_name:
                await ctx.send(f"❌ Une série nommée '{new_name}' existe déjà")
                return
            
            # Effectuer le renommage
            await bot.db.db.execute("""
                UPDATE characters SET anime = ? WHERE anime = ?
            """, (new_name, old_name))
            
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Renommage Réussi",
                description=f"'{old_name}' → '{new_name}'\n{count} personnages mis à jour",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur renommage série: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='deleteseries', aliases=['removeseries'])
    async def delete_series_command(ctx, series_name: str, confirmation: str = None):
        """Supprimer une série (retire l'assignation des personnages)
        
        Usage: !deleteseries "Nom Série" CONFIRM
        Exemple: !deleteseries "Série Test" CONFIRM
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        if confirmation != "CONFIRM":
            await ctx.send(f"⚠️ **ATTENTION:** Cette action retirera la série de tous les personnages!\n"
                          f"Tapez: `!deleteseries \"{series_name}\" CONFIRM` pour confirmer")
            return
        
        try:
            # Vérifier que la série existe et compter les personnages
            async with bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (series_name,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count == 0:
                await ctx.send(f"❌ Aucune série nommée '{series_name}'")
                return
            
            # Supprimer la série (mettre anime à NULL)
            await bot.db.db.execute("""
                UPDATE characters SET anime = NULL WHERE anime = ?
            """, (series_name,))
            
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Série Supprimée",
                description=f"Série '{series_name}' supprimée\n{count} personnages libérés",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur suppression série: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='listseries', aliases=['allseries'])
    async def list_series_command(ctx):
        """Lister toutes les séries existantes
        
        Usage: !listseries
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Récupérer toutes les séries avec compte de personnages
            async with bot.db.db.execute("""
                SELECT anime, COUNT(*) as count 
                FROM characters 
                WHERE anime IS NOT NULL AND anime != ''
                GROUP BY anime 
                ORDER BY count DESC, anime
            """) as cursor:
                series_data = await cursor.fetchall()
            
            if not series_data:
                await ctx.send("📋 Aucune série trouvée")
                return
            
            embed = discord.Embed(
                title="📋 ═══════〔 T O U T E S   L E S   S É R I E S 〕═══════ 📋",
                description=f"```{len(series_data)} séries trouvées```",
                color=BotConfig.RARITY_COLORS['Legendary']
            )
            
            series_list = ""
            total_chars = 0
            
            for i, (series_name, char_count) in enumerate(series_data, 1):
                series_list += f"{i:2d}. {series_name}: {char_count} personnages\n"
                total_chars += char_count
                
                # Créer un nouveau field tous les 15 séries pour éviter la limite Discord
                if i % 15 == 0 or i == len(series_data):
                    embed.add_field(
                        name=f"🎭 Séries {max(1, i-14)} à {i}",
                        value=f"```{series_list}```",
                        inline=False
                    )
                    series_list = ""
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"```Total: {total_chars} personnages assignés```",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur liste séries: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='seriesinfo', aliases=['showseries'])
    async def series_info_command(ctx, series_name: str):
        """Afficher les détails d'une série
        
        Usage: !seriesinfo "Nom Série"
        Exemple: !seriesinfo "Naruto"
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Récupérer les personnages de la série
            async with bot.db.db.execute("""
                SELECT name, rarity, value FROM characters 
                WHERE anime = ?
                ORDER BY 
                    CASE rarity 
                        WHEN 'Secret' THEN 1
                        WHEN 'Fusion' THEN 2
                        WHEN 'Titan' THEN 3
                        WHEN 'Mythic' THEN 4
                        WHEN 'Legendary' THEN 5
                        WHEN 'Epic' THEN 6
                        WHEN 'Rare' THEN 7
                        WHEN 'Common' THEN 8
                        ELSE 9
                    END, name
            """, (series_name,)) as cursor:
                characters = await cursor.fetchall()
            
            if not characters:
                await ctx.send(f"❌ Aucune série nommée '{series_name}'")
                return
            
            embed = discord.Embed(
                title=f"🎭 ═══════〔 {series_name} 〕═══════ 🎭",
                description=f"```{len(characters)} personnages dans cette série```",
                color=BotConfig.RARITY_COLORS['Epic']
            )
            
            # Grouper par rareté
            rarity_groups = {}
            total_value = 0
            
            for char_name, rarity, value in characters:
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(f"{char_name} ({value} SC)")
                total_value += value
            
            # Afficher par rareté
            for rarity in ['Secret', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                if rarity in rarity_groups:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    chars_text = "\n".join(rarity_groups[rarity])
                    
                    embed.add_field(
                        name=f"{emoji} {rarity} ({len(rarity_groups[rarity])})",
                        value=f"```{chars_text}```",
                        inline=False
                    )
            
            embed.add_field(
                name="🪙 Valeur Totale",
                value=f"```{total_value:,} Shadow Coins```",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur info série: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    @bot.command(name='unassign')
    async def unassign_character_command(ctx, character_id: int):
        """Retirer un personnage de sa série
        
        Usage: !unassign [ID_personnage]
        Exemple: !unassign 25
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        try:
            # Vérifier que le personnage existe
            async with bot.db.db.execute("""
                SELECT name, anime FROM characters WHERE id = ?
            """, (character_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                await ctx.send(f"❌ Aucun personnage avec l'ID {character_id}")
                return
            
            char_name, current_series = result
            
            if not current_series:
                await ctx.send(f"⚠️ {char_name} n'est assigné à aucune série")
                return
            
            # Retirer l'assignation
            await bot.db.db.execute("""
                UPDATE characters SET anime = NULL WHERE id = ?
            """, (character_id,))
            
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Désassignation Réussie",
                description=f"**{char_name}** retiré de '{current_series}'",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erreur désassignation: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")
    
    logger.info("Legacy series admin commands setup completed")