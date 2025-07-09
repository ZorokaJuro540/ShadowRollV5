"""
Admin commands for Shadow Roll Bot
Comprehensive admin functionality with security
"""
import discord
from discord.ext import commands
import logging
from typing import Optional
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name

logger = logging.getLogger(__name__)

class AdminManager:
    """Admin command manager for Shadow Roll Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in BotConfig.ADMIN_IDS
    
    async def setup_commands(self):
        """Setup all admin commands"""
        
        @self.bot.command(name='synccommands')
        async def sync_commands(ctx):
            """Sync slash commands to Discord - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                synced = await self.bot.tree.sync()
                await ctx.send(f"✅ {len(synced)} commandes slash synchronisées avec Discord.")
                logger.info(f"Admin {ctx.author.id} synced {len(synced)} slash commands")
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la synchronisation: {e}")
                logger.error(f"Failed to sync commands via admin: {e}")
        


        @self.bot.command(name='givecoins')
        async def give_coins(ctx, user: discord.Member, amount: int):
            """Give coins to a user - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            if amount <= 0:
                await ctx.send("❌ Le montant doit être positif.")
                return
            
            try:
                username = get_display_name(user)
                player = await self.db.get_or_create_player(user.id, username)
                new_coins = player.coins + amount
                
                await self.db.update_player_coins(user.id, new_coins)
                
                embed = discord.Embed(
                    title="🪙 Pièces Ajoutées",
                    description=f"Ajouté {format_number(amount)} pièces à {username}",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Nouveau Solde",
                    value=f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                    inline=False
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error giving coins: {e}")
                await ctx.send("❌ Erreur lors de l'ajout des pièces.")
        
        @self.bot.command(name='removecoins')
        async def remove_coins(ctx, user: discord.Member, amount: int):
            """Remove coins from a user - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            if amount <= 0:
                await ctx.send("❌ Le montant doit être positif.")
                return
            
            try:
                username = get_display_name(user)
                player = await self.db.get_or_create_player(user.id, username)
                new_coins = max(0, player.coins - amount)
                
                await self.db.update_player_coins(user.id, new_coins)
                
                embed = discord.Embed(
                    title="🪙 Pièces Retirées",
                    description=f"Retiré {format_number(amount)} pièces de {username}",
                    color=0xff9900
                )
                embed.add_field(
                    name="Nouveau Solde",
                    value=f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                    inline=False
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error removing coins: {e}")
                await ctx.send("❌ Erreur lors de la suppression des pièces.")
        
        @self.bot.command(name='createchar')
        async def create_character(ctx, name: str, rarity: str, anime: str, value: int, image_url: str = None):
            """Create a new character - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            if rarity not in BotConfig.RARITY_WEIGHTS:
                valid_rarities = ', '.join(BotConfig.RARITY_WEIGHTS.keys())
                await ctx.send(f"❌ Rareté invalide! Options valides: {valid_rarities}")
                return
            
            if value <= 0:
                await ctx.send("❌ La valeur doit être positive.")
                return
            
            try:
                character_id = await self.db.create_character(name, anime, rarity, value, image_url)
                
                embed = discord.Embed(
                    title="✅ Personnage Créé",
                    description=f"Le personnage '{name}' a été créé avec succès!",
                    color=BotConfig.RARITY_COLORS.get(rarity, 0x4A4A4A)
                )
                embed.add_field(name="Nom", value=name, inline=True)
                embed.add_field(name="Anime", value=anime, inline=True)
                embed.add_field(name="Rareté", value=f"{BotConfig.RARITY_EMOJIS.get(rarity, '◆')} {rarity}", inline=True)
                embed.add_field(name="Valeur", value=f"{format_number(value)} pièces", inline=True)
                embed.add_field(name="ID", value=str(character_id), inline=True)
                
                if image_url:
                    embed.set_thumbnail(url=image_url)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error creating character: {e}")
                await ctx.send("❌ Erreur lors de la création du personnage.")
        
        @self.bot.command(name='deletechar')
        async def delete_character(ctx, user: discord.Member, *, character_name: str):
            """Delete a character from user's inventory - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                username = get_display_name(user)
                inventory = await self.db.get_player_inventory(user.id, page=1, limit=1000)
                
                char_to_delete = None
                for item in inventory:
                    if item.get('character_name', '').lower() == character_name.lower():
                        char_to_delete = item
                        break
                
                if not char_to_delete:
                    await ctx.send(f"❌ Personnage '{character_name}' non trouvé dans l'inventaire de {username}.")
                    return
                
                # Delete one instance of the character
                await self.db.db.execute("""
                    DELETE FROM player_characters 
                    WHERE user_id = ? AND character_id = ? 
                    LIMIT 1
                """, (user.id, char_to_delete['character_id']))
                await self.db.db.commit()
                
                embed = discord.Embed(
                    title="🗑️ Personnage Supprimé",
                    description=f"Supprimé '{character_name}' de l'inventaire de {username}",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error deleting character: {e}")
                await ctx.send("❌ Erreur lors de la suppression du personnage.")
        
        @self.bot.command(name='resetuser')
        async def reset_user(ctx, user: discord.Member):
            """Reset a user's profile completely - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                username = get_display_name(user)
                
                # Delete all characters
                await self.db.db.execute("""
                    DELETE FROM player_characters WHERE user_id = ?
                """, (user.id,))
                
                # Reset player stats
                await self.db.db.execute("""
                    UPDATE players SET 
                    coins = ?, 
                    total_rerolls = 0, 
                    last_daily = NULL, 
                    last_reroll = NULL 
                    WHERE user_id = ?
                """, (BotConfig.STARTING_COINS, user.id))
                
                # Delete achievements
                await self.db.db.execute("""
                    DELETE FROM player_achievements WHERE user_id = ?
                """, (user.id,))
                
                await self.db.db.commit()
                
                embed = discord.Embed(
                    title="🔄 Utilisateur Réinitialisé",
                    description=f"Profil de {username} réinitialisé avec succès",
                    color=0x0099ff
                )
                embed.add_field(
                    name="Données Réinitialisées",
                    value=f"• Pièces: {format_number(BotConfig.STARTING_COINS)}\n• Personnages: 0\n• Succès: 0\n• Invocations: 0",
                    inline=False
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error resetting user: {e}")
                await ctx.send("❌ Erreur lors de la réinitialisation de l'utilisateur.")
        
        @self.bot.command(name='banuser')
        async def ban_user(ctx, user: discord.Member, *, reason: str = "Aucune raison spécifiée"):
            """Ban a user from using the bot - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                username = get_display_name(user)
                await self.db.ban_user(user.id, ctx.author.id, reason)
                
                embed = discord.Embed(
                    title="🔨 Utilisateur Banni",
                    description=f"{username} a été banni du bot",
                    color=0xff0000
                )
                embed.add_field(name="Raison", value=reason, inline=False)
                embed.add_field(name="Banni par", value=get_display_name(ctx.author), inline=True)
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error banning user: {e}")
                await ctx.send("❌ Erreur lors du bannissement de l'utilisateur.")
        
        @self.bot.command(name='unbanuser')
        async def unban_user(ctx, user: discord.Member):
            """Unban a user - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                username = get_display_name(user)
                await self.db.unban_user(user.id)
                
                embed = discord.Embed(
                    title="✅ Utilisateur Débanni",
                    description=f"{username} peut maintenant utiliser le bot",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error unbanning user: {e}")
                await ctx.send("❌ Erreur lors du débannissement de l'utilisateur.")
        
        @self.bot.command(name='wipeall')
        async def wipeall(ctx, user: discord.Member):
            """Completely wipe all player data - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                # Delete all player data
                await self.bot.db.db.execute("DELETE FROM inventory WHERE user_id = ?", (user.id,))
                await self.bot.db.db.execute("DELETE FROM player_achievements WHERE user_id = ?", (user.id,))
                await self.bot.db.db.execute("DELETE FROM player_items WHERE user_id = ?", (user.id,))
                await self.bot.db.db.execute("DELETE FROM marketplace_listings WHERE seller_id = ?", (user.id,))
                await self.bot.db.db.execute("DELETE FROM players WHERE user_id = ?", (user.id,))
                await self.bot.db.db.commit()

                embed = discord.Embed(
                    title="💥 Suppression Totale",
                    description=f"Toutes les données de {user.mention} ont été supprimées :",
                    color=0xff0000)
                embed.add_field(name="✅ Supprimé", value="• Coins\n• Inventaire\n• Succès\n• Objets\n• Listings marketplace\n• Statistiques", inline=False)
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la suppression: {e}")

        @self.bot.command(name='viewprofile')
        async def viewprofile(ctx, user: discord.Member):
            """View complete player profile - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                player = await self.bot.db.get_or_create_player(user.id, user.name)
                inventory_stats = await self.bot.db.get_inventory_stats(user.id)
                achievements = await self.bot.db.get_all_achievements_with_status(user.id)
                
                completed_achievements = [a for a in achievements if a['is_completed']]
                active_effects = await self.bot.db.get_active_effects(user.id)

                embed = discord.Embed(
                    title=f"📜 Profil Complet - {user.display_name}",
                    color=0x4169E1)

                # Basic stats
                embed.add_field(
                    name="🪙 Économie",
                    value=f"Coins: {player.coins:,} {BotConfig.CURRENCY_EMOJI}\nRerolls: {player.total_rerolls:,}",
                    inline=True)

                # Inventory stats
                embed.add_field(
                    name="🎴 Collection",
                    value=f"Personnages uniques: {inventory_stats['unique_characters']}\nTotal: {inventory_stats['total_characters']}\nValeur: {inventory_stats['total_value']:,}",
                    inline=True)

                # Achievements
                embed.add_field(
                    name="🏆 Succès",
                    value=f"Débloqués: {len(completed_achievements)}/{len(achievements)}",
                    inline=True)

                # Active effects
                if active_effects:
                    effects_text = "\n".join([f"• {effect['item_name']}" for effect in active_effects])
                    embed.add_field(name="⚡ Effets Actifs", value=effects_text, inline=False)

                # Rarity breakdown
                if inventory_stats['rarity_counts']:
                    rarity_text = []
                    for rarity in ['Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                        count = inventory_stats['rarity_counts'].get(rarity, 0)
                        if count > 0:
                            emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                            rarity_text.append(f"{emoji} {rarity}: {count}")
                    embed.add_field(name="📊 Répartition par Rareté", value="\n".join(rarity_text), inline=False)

                embed.set_footer(text=f"Créé le: {player.created_at or 'Inconnu'}")
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l'affichage du profil: {e}")

        @self.bot.command(name='forcepull')
        async def forcepull(ctx, user: discord.Member, rarity: str):
            """Force a character pull of specific rarity - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            rarity = rarity.capitalize()
            if rarity not in BotConfig.RARITY_WEIGHTS:
                await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
                return

            try:
                # Get random character of specific rarity
                cursor = await self.bot.db.db.execute(
                    "SELECT * FROM characters WHERE rarity = ? ORDER BY RANDOM() LIMIT 1",
                    (rarity,))
                char_row = await cursor.fetchone()
                
                if not char_row:
                    await ctx.send(f"❌ Aucun personnage {rarity} trouvé")
                    return

                from core.models import Character
                character = Character(
                    id=char_row[0], name=char_row[1], anime=char_row[2],
                    rarity=char_row[3], value=char_row[4], image_url=char_row[5])

                # Add to player inventory
                await self.bot.db.add_character_to_inventory(user.id, character.id)
                
                # Create embed
                embed = discord.Embed(
                    title="🔄 Pull Forcé",
                    description=f"**{user.mention}** a reçu:",
                    color=character.get_rarity_color())
                
                embed.add_field(
                    name=f"{character.get_rarity_emoji()} {character.name}",
                    value=f"**Anime:** {character.anime}\n**Rareté:** {character.rarity}\n**Valeur:** {character.value} {BotConfig.CURRENCY_EMOJI}",
                    inline=False)
                
                if character.image_url:
                    embed.set_thumbnail(url=character.image_url)
                
                embed.set_footer(text=f"Pull forcé par {ctx.author.display_name}")
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur lors du pull forcé: {e}")

        @self.bot.command(name='giveallcoins')
        async def giveallcoins(ctx, amount: int):
            """Give coins to all registered players - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            if amount <= 0:
                await ctx.send("❌ Le montant doit être positif")
                return

            try:
                # Get all players
                cursor = await self.bot.db.db.execute("SELECT user_id, username FROM players")
                players = await cursor.fetchall()
                
                if not players:
                    await ctx.send("❌ Aucun joueur trouvé dans la base de données")
                    return

                # Update all players
                await self.bot.db.db.execute(
                    "UPDATE players SET coins = coins + ?", (amount,))
                await self.bot.db.db.commit()

                embed = discord.Embed(
                    title="🪙 Distribution Globale",
                    description=f"**{amount:,}** {BotConfig.CURRENCY_EMOJI} ont été donnés à tous les joueurs !",
                    color=0x00ff00)
                embed.add_field(name="👥 Joueurs affectés", value=f"{len(players):,} joueurs", inline=False)
                embed.set_footer(text=f"Distribution par {ctx.author.display_name}")
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur lors de la distribution: {e}")

        @self.bot.command(name='setstatus')
        async def setstatus(ctx, user: discord.Member, status: str):
            """Set player ban status - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            status = status.lower()
            if status not in ['ban', 'unban']:
                await ctx.send("❌ Statut invalide. Utilisez: ban ou unban")
                return

            try:
                is_banned = status == 'ban'
                await self.bot.db.db.execute(
                    "UPDATE players SET is_banned = ? WHERE user_id = ?", 
                    (is_banned, user.id))
                await self.bot.db.db.commit()

                action = "banni" if is_banned else "débanni"
                embed = discord.Embed(
                    title=f"⚖️ Statut Modifié",
                    description=f"{user.mention} a été **{action}**",
                    color=0xff0000 if is_banned else 0x00ff00)
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")

        @self.bot.command(name='addachievement')
        async def addachievement(ctx, user: discord.Member, achievement_id: int):
            """Award achievement to player - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                success = await self.bot.db.award_achievement(user.id, achievement_id)
                if success:
                    # Get achievement details
                    cursor = await self.bot.db.db.execute(
                        "SELECT name, reward_coins FROM achievements WHERE id = ?", 
                        (achievement_id,))
                    achievement = await cursor.fetchone()
                    
                    if achievement:
                        embed = discord.Embed(
                            title="🏆 Succès Accordé",
                            description=f"{user.mention} a reçu le succès **{achievement[0]}**",
                            color=0xffd700)
                        embed.add_field(name="🪙 Récompense", value=f"{achievement[1]} {BotConfig.CURRENCY_EMOJI}", inline=False)
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Succès introuvable")
                else:
                    await ctx.send("❌ Le joueur possède déjà ce succès")

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")

        @self.bot.command(name='marketstats')
        async def marketstats(ctx):
            """Display marketplace statistics - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                stats = await self.bot.db.get_marketplace_stats()
                
                embed = discord.Embed(title="📊 Statistiques Marketplace", color=0x4169E1)
                embed.add_field(name="📦 Listings Actifs", value=f"{stats['active_listings']}", inline=True)
                embed.add_field(name="🪙 Valeur Totale", value=f"{stats['total_value']:,} {BotConfig.CURRENCY_EMOJI}", inline=True)
                embed.add_field(name="📈 Prix Moyen", value=f"{stats['average_price']:,.0f} {BotConfig.CURRENCY_EMOJI}", inline=True)
                
                if stats.get('top_sellers'):
                    sellers_text = []
                    for seller in stats['top_sellers'][:5]:
                        sellers_text.append(f"<@{seller['seller_id']}>: {seller['listings']} listings")
                    embed.add_field(name="🏪 Top Vendeurs", value="\n".join(sellers_text), inline=False)
                
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")

        @self.bot.command(name='setnextpull')
        async def setnextpull(ctx, user: discord.Member, rarity: str):
            """Force next pull rarity for a specific player - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            rarity = rarity.capitalize()
            if rarity not in BotConfig.RARITY_WEIGHTS:
                await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
                return

            try:
                # Store the forced rarity in database or bot memory
                if not hasattr(self.bot, 'forced_pulls'):
                    self.bot.forced_pulls = {}
                
                self.bot.forced_pulls[user.id] = rarity
                
                embed = discord.Embed(
                    title="🎯 Pull Forcé Programmé",
                    description=f"Le prochain pull de {user.mention} sera **{rarity}**",
                    color=BotConfig.RARITY_COLORS.get(rarity, 0x808080))
                
                embed.add_field(
                    name="⚠️ Note", 
                    value="Cette modification s'appliquera au prochain `/roll` ou invocation menu.",
                    inline=False)
                
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")

        @self.bot.command(name='clearnextpull')
        async def clearnextpull(ctx, user: discord.Member):
            """Clear forced next pull for a player - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                if hasattr(self.bot, 'forced_pulls') and user.id in self.bot.forced_pulls:
                    del self.bot.forced_pulls[user.id]
                    await ctx.send(f"✅ Pull forcé annulé pour {user.mention}")
                else:
                    await ctx.send(f"❌ Aucun pull forcé programmé pour {user.mention}")

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")

        @self.bot.command(name='playerstats')
        async def playerstats(ctx):
            """Display general player statistics - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                # Get total players
                cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
                total_players = (await cursor.fetchone())[0]
                
                # Get active players (played in last 7 days)
                cursor = await self.bot.db.db.execute(
                    "SELECT COUNT(*) FROM players WHERE last_reroll > datetime('now', '-7 days')")
                active_players = (await cursor.fetchone())[0]
                
                # Get total coins in circulation
                cursor = await self.bot.db.db.execute("SELECT SUM(coins) FROM players")
                total_coins = (await cursor.fetchone())[0] or 0
                
                # Get total characters collected
                cursor = await self.bot.db.db.execute("SELECT SUM(count) FROM inventory")
                total_chars = (await cursor.fetchone())[0] or 0
                
                embed = discord.Embed(title="📊 Statistiques des Joueurs", color=0x4169E1)
                embed.add_field(name="👥 Joueurs Total", value=f"{total_players:,}", inline=True)
                embed.add_field(name="🎯 Joueurs Actifs", value=f"{active_players:,}", inline=True)
                embed.add_field(name="🪙 Coins en Circulation", value=f"{total_coins:,} {BotConfig.CURRENCY_EMOJI}", inline=True)
                embed.add_field(name="🎴 Personnages Collectés", value=f"{total_chars:,}", inline=True)
                
                await ctx.send(embed=embed)

            except Exception as e:
                await ctx.send(f"❌ Erreur: {e}")



        # Initialize search cache
        if not hasattr(self, '_search_cache'):
            self._search_cache = {}

        @self.bot.command(name='adminhelp', aliases=['admin'])
        async def admin_panel(ctx):
            """Launch admin interface with buttons - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            view = AdminPanelView(self, ctx.author.id)
            embed = await view.create_main_embed()
            await ctx.send(embed=embed, view=view)

        @self.bot.command(name='addimage')
        async def add_image_simple(ctx, *, args: str):
            """Add image to a character manually - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return
            
            try:
                # Parse arguments (character name and URL)
                parts = args.rsplit(' ', 1)  # Split from the right to separate URL
                if len(parts) != 2:
                    await ctx.send("❌ Usage: `!addimage nom_personnage url_image`")
                    return
                
                character_name, image_url = parts
                
                if not image_url.startswith('http'):
                    await ctx.send("❌ L'URL doit commencer par http:// ou https://")
                    return
                
                # Find character by name
                cursor = await self.db.db.execute(
                    "SELECT id, name, anime FROM characters WHERE LOWER(name) LIKE LOWER(?)",
                    (f"%{character_name}%",)
                )
                characters = await cursor.fetchall()
                
                if not characters:
                    await ctx.send(f"❌ Aucun personnage trouvé avec le nom '{character_name}' pour la commande addimage")
                    return
                
                if len(characters) > 1:
                    # Create selection view for multiple matches
                    view = CharacterSelectionView(self, ctx.author.id, characters, image_url)
                    embed = discord.Embed(
                        title="🔍 Sélection de Personnage",
                        description=f"Plusieurs personnages trouvés avec '{character_name}'. Choisissez:",
                        color=0xffa500
                    )
                    
                    char_list = []
                    for i, (char_id, name, anime) in enumerate(characters[:10], 1):  # Limit to 10
                        char_list.append(f"`{i}` **{name}** ({anime})")
                    
                    embed.add_field(
                        name="Personnages disponibles:",
                        value="\n".join(char_list),
                        inline=False
                    )
                    
                    embed.set_footer(text="Utilisez les boutons pour sélectionner le bon personnage")
                    await ctx.send(embed=embed, view=view)
                    return
                
                char_id, char_name, char_anime = characters[0]
                
                # Update character image without validation for speed
                await self.db.db.execute(
                    "UPDATE characters SET image_url = ? WHERE id = ?",
                    (image_url, char_id)
                )
                await self.db.db.commit()
                
                embed = discord.Embed(
                    title="✅ Image ajoutée",
                    description=f"Image mise à jour pour **{char_name}** ({char_anime})",
                    color=0x00ff00
                )
                embed.set_image(url=image_url)
                await ctx.send(embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur lors de l'ajout de l'image: {str(e)}")
                logger.error(f"Error adding image: {e}")

# Character Selection View for multiple matches
class CharacterSelectionView(discord.ui.View):
    def __init__(self, admin_manager, user_id: int, characters: list, image_url: str):
        super().__init__(timeout=60)
        self.admin_manager = admin_manager
        self.user_id = user_id
        self.characters = characters[:10]  # Limit to 10 characters
        self.image_url = image_url
        
        # Add number buttons for each character
        for i, (char_id, name, anime) in enumerate(self.characters, 1):
            button = discord.ui.Button(
                label=f"{i}",
                style=discord.ButtonStyle.primary,
                custom_id=f"char_{i}"
            )
            button.callback = self.create_callback(i-1)
            self.add_item(button)
    
    def create_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette sélection.", ephemeral=True)
                return
            
            char_id, char_name, char_anime = self.characters[index]
            
            try:
                # Update character image
                await self.admin_manager.db.db.execute(
                    "UPDATE characters SET image_url = ? WHERE id = ?",
                    (self.image_url, char_id)
                )
                await self.admin_manager.db.db.commit()
                
                embed = discord.Embed(
                    title="✅ Image ajoutée",
                    description=f"Image mise à jour pour **{char_name}** ({char_anime})",
                    color=0x00ff00
                )
                embed.set_image(url=self.image_url)
                
                self.clear_items()
                await interaction.response.edit_message(embed=embed, view=self)
                
            except Exception as e:
                await interaction.response.send_message(f"❌ Erreur: {str(e)}", ephemeral=True)
        
        return callback
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

        @self.bot.command(name='applygifs')
        async def apply_gifs_bulk(ctx):
            """Apply GIFs to all characters automatically - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                from gif_manager import GifManager
                gif_manager = GifManager(self.db)
                
                # Send initial message
                msg = await ctx.send("🎬 Application des GIFs en cours...")
                
                # Apply GIFs
                results = await gif_manager.bulk_apply_suggested_gifs()
                
                # Create result embed
                embed = discord.Embed(
                    title="🎬 Application des GIFs Terminée",
                    color=0x00ff00
                )
                embed.add_field(name="✅ GIFs Appliqués", value=str(results['applied']), inline=True)
                embed.add_field(name="⏭️ Ignorés", value=str(results['skipped']), inline=True)
                embed.add_field(name="❌ Échecs", value=str(results['failed']), inline=True)
                
                total = sum(results.values())
                if total > 0:
                    embed.add_field(
                        name="📊 Résumé",
                        value=f"**{results['applied']}/{total}** personnages ont maintenant des GIFs animés!",
                        inline=False
                    )
                
                await msg.edit(content="", embed=embed)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur: {str(e)}")

        @self.bot.command(name='suggest')
        async def suggest_character(ctx):
            """Start interactive GIF/image adding session - Admin only"""
            if not self.is_admin(ctx.author.id):
                await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
                return

            try:
                from gif_manager import GifManager
                gif_manager = GifManager(self.db)
                
                # Get characters needing media upgrades
                characters = await gif_manager.get_characters_needing_gifs()
                
                if not characters:
                    await ctx.send("✅ Tous les personnages ont déjà des GIFs ou images optimisées!")
                    return
                
                # Start interactive session
                view = GifSuggestView(self, ctx.author.id, characters, gif_manager)
                embed = await view.create_embed()
                await ctx.send(embed=embed, view=view)
                
            except Exception as e:
                await ctx.send(f"❌ Erreur: {str(e)}")

# Interactive GIF/Image Suggestion View
class GifSuggestView(discord.ui.View):
    def __init__(self, admin_manager, user_id: int, characters: list):
        super().__init__(timeout=300)
        self.admin_manager = admin_manager
        self.user_id = user_id
        self.characters = characters
        self.current_index = 0
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_embed(self) -> discord.Embed:
        if self.current_index >= len(self.characters):
            embed = discord.Embed(
                title="✅ Session terminée",
                description="Tous les personnages proposés ont été traités!",
                color=0x00ff00
            )
            embed.add_field(name="Merci!", value="Vous avez fini la session d'ajout d'images.", inline=False)
            return embed
            
        char_id, name, anime, current_url = self.characters[self.current_index]
        status = "❌ Aucune image" if not current_url else "⚠️ Image placeholder"
        
        embed = discord.Embed(
            title="🖼️ Ajout d'Image",
            description=f"**Personnage:** {name}\n**Anime:** {anime}\n**Status:** {status}",
            color=0xff6b35
        )
        
        embed.add_field(
            name="📝 Instructions",
            value="Utilisez le bouton **Ajouter Image** puis collez l'URL de l'image",
            inline=False
        )
        
        embed.set_footer(text=f"Personnage {self.current_index + 1}/{len(self.characters)}")
        return embed
    
    @discord.ui.button(label="Ajouter Image", style=discord.ButtonStyle.primary, emoji="🖼️")
    async def add_image_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ImageUrlModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Passer", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_index += 1
        embed = await self.create_embed()
        
        if self.current_index >= len(self.characters):
            self.clear_items()
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Arrêter", style=discord.ButtonStyle.danger, emoji="🛑")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛑 Session arrêtée",
            description="Session d'ajout d'images interrompue par l'utilisateur.",
            color=0xff0000
        )
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def update_current_character(self, image_url: str, interaction: discord.Interaction):
        char_id, name, anime, _ = self.characters[self.current_index]
        
        # Validate and update image
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(image_url, timeout=10) as response:
                    if response.status != 200:
                        await interaction.followup.send(f"❌ L'URL de l'image n'est pas accessible (status {response.status})", ephemeral=True)
                        return False
                    
                    content_type = response.headers.get('content-type', '').lower()
                    if 'image' not in content_type:
                        await interaction.followup.send(f"❌ L'URL ne semble pas pointer vers une image valide", ephemeral=True)
                        return False
        except Exception as e:
            await interaction.followup.send(f"❌ Impossible de valider l'URL de l'image: {str(e)}", ephemeral=True)
            return False
        
        # Update character image
        await self.admin_manager.db.db.execute(
            "UPDATE characters SET image_url = ? WHERE id = ?",
            (image_url, char_id)
        )
        await self.admin_manager.db.db.commit()
        
        # Success message
        success_embed = discord.Embed(
            title="✅ Image ajoutée",
            description=f"Image mise à jour pour **{name}** ({anime})",
            color=0x00ff00
        )
        success_embed.set_image(url=image_url)
        await interaction.followup.send(embed=success_embed, ephemeral=True)
        
        # Move to next character
        self.current_index += 1
        embed = await self.create_embed()
        
        if self.current_index >= len(self.characters):
            self.clear_items()
        
        await interaction.edit_original_response(embed=embed, view=self)
        return True

# Modal for GIF/Image URL input
class GifUrlModal(discord.ui.Modal, title="Ajouter un GIF ou une image"):
    def __init__(self, image_view):
        super().__init__()
        self.image_view = image_view
    
    url_input = discord.ui.TextInput(
        label="URL du GIF ou de l'image",
        placeholder="https://example.com/animation.gif ou https://example.com/image.jpg",
        style=discord.TextStyle.short,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = self.url_input.value.strip()
        
        if not url.startswith('http'):
            await interaction.followup.send("❌ L'URL doit commencer par http:// ou https://", ephemeral=True)
            return
        
        await self.image_view.update_current_character(url, interaction)

# Interface Admin avec boutons
class AdminPanelView(discord.ui.View):
    def __init__(self, admin_manager, user_id: int):
        super().__init__(timeout=300)
        self.admin_manager = admin_manager
        self.user_id = user_id
        self.current_page = 0
        self.players_per_page = 10
        self.selected_player = None
        self.mode = "main"  # main, players, player_actions, system
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_main_embed(self) -> discord.Embed:
        """Interface principale admin"""
        embed = discord.Embed(
            title="🛠️ ═══════〔 P A N N E A U   A D M I N 〕═══════ 🛠️",
            description="```\n◆ Interface d'administration Shadow Roll ◆\n```",
            color=0x9370DB
        )
        
        embed.add_field(
            name="👥 Gestion des Joueurs",
            value="• Voir la liste des joueurs\n• Gérer les profils et statuts\n• Modifier les pièces et personnages",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Système & Stats",
            value="• Statistiques générales\n• Gestion des personnages\n• Outils d'administration",
            inline=False
        )
        
        embed.set_footer(text=f"Shadow Roll Admin • {BotConfig.VERSION} • Sélectionnez une option")
        return embed
    
    async def create_players_embed(self) -> discord.Embed:
        """Liste des joueurs avec pagination"""
        # Get players with basic info
        cursor = await self.admin_manager.db.db.execute(
            """SELECT user_id, username, coins, is_banned
               FROM players 
               ORDER BY coins DESC 
               LIMIT ? OFFSET ?""",
            (self.players_per_page, self.current_page * self.players_per_page)
        )
        player_rows = await cursor.fetchall()
        
        # Get character counts for each player
        players = []
        for row in player_rows:
            user_id, username, coins, is_banned = row
            
            # Count characters for this player
            cursor = await self.admin_manager.db.db.execute(
                "SELECT COALESCE(SUM(count), 0) FROM inventory WHERE user_id = ?",
                (user_id,)
            )
            char_count = (await cursor.fetchone())[0]
            
            status = '🔴 BANNI' if is_banned else '🟢 ACTIF'
            players.append((user_id, username, coins, char_count, status))
        
        # Total count
        cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
        total_players = (await cursor.fetchone())[0]
        
        embed = discord.Embed(
            title="👥 ═══════〔 L I S T E   J O U E U R S 〕═══════ 👥",
            description=f"```\n◆ Page {self.current_page + 1} • {total_players} joueurs total ◆\n```",
            color=0x3498db
        )
        
        if players:
            player_list = []
            for i, (user_id, username, coins, chars, status) in enumerate(players, 1):
                index = self.current_page * self.players_per_page + i
                player_list.append(f"**{index}.** {username or f'ID:{user_id}'}")
                player_list.append(f"     🪙 {coins:,} • 🎴 {chars} • {status}")
            
            embed.add_field(
                name="📋 Joueurs",
                value="\n".join(player_list),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Joueurs",
                value="Aucun joueur sur cette page",
                inline=False
            )
        
        embed.set_footer(text="Sélectionnez un joueur par son numéro ou naviguez")
        return embed
    
    async def create_player_actions_embed(self) -> discord.Embed:
        """Actions pour le joueur sélectionné"""
        if not self.selected_player:
            return await self.create_main_embed()
            
        user_id, username, coins, chars, banned = self.selected_player
        status = "🔴 BANNI" if banned else "🟢 ACTIF"
        
        embed = discord.Embed(
            title="⚙️ ═══════〔 A C T I O N S   J O U E U R 〕═══════ ⚙️",
            description=f"```\n◆ Gestion de {username or f'ID:{user_id}'} ◆\n```",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="📊 Informations",
            value=f"**Nom:** {username or f'ID:{user_id}'}\n**Statut:** {status}\n**Pièces:** {coins:,}\n**Personnages:** {chars}",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Actions Disponibles",
            value="• Voir le profil complet\n• Donner/Retirer des pièces\n• Bannir/Débannir\n• Forcer un pull\n• Réinitialiser le profil",
            inline=False
        )
        
        embed.set_footer(text="Choisissez une action à effectuer")
        return embed
    
    async def create_system_embed(self) -> discord.Embed:
        """Interface système"""
        cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
        total_players = (await cursor.fetchone())[0]
        
        cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM characters")
        total_chars = (await cursor.fetchone())[0]
        
        embed = discord.Embed(
            title="🎮 ═══════〔 S Y S T È M E 〕═══════ 🎮",
            description="```\n◆ Statistiques et outils système ◆\n```",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Joueurs:** {total_players}\n**Personnages:** {total_chars}\n**Version:** {BotConfig.VERSION}",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Outils Disponibles",
            value="• Donner des pièces à tous\n• Statistiques détaillées\n• Gestion des images\n• Créer un personnage",
            inline=False
        )
        
        embed.set_footer(text="Outils d'administration système")
        return embed
    
    @discord.ui.button(label="👥 Joueurs", style=discord.ButtonStyle.primary, row=0)
    async def players_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mode = "players"
        self.current_page = 0
        embed = await self.create_players_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎮 Système", style=discord.ButtonStyle.secondary, row=0)
    async def system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mode = "system"
        embed = await self.create_system_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode == "players" and self.current_page > 0:
            self.current_page -= 1
            embed = await self.create_players_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode == "players":
            cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            max_pages = (total_players - 1) // self.players_per_page
            
            if self.current_page < max_pages:
                self.current_page += 1
                embed = await self.create_players_embed()
                await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu", style=discord.ButtonStyle.success, row=1)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mode = "main"
        self.selected_player = None
        embed = await self.create_main_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def update_view(self):
        """Met à jour les boutons selon le mode"""
        self.clear_items()
        
        if self.mode == "main":
            # Boutons principaux
            btn_players = discord.ui.Button(label="👥 Joueurs", style=discord.ButtonStyle.primary, row=0)
            btn_players.callback = self.players_callback
            self.add_item(btn_players)
            
            btn_system = discord.ui.Button(label="🎮 Système", style=discord.ButtonStyle.secondary, row=0)
            btn_system.callback = self.system_callback
            self.add_item(btn_system)
            
        elif self.mode == "players":
            # Navigation
            btn_prev = discord.ui.Button(label="◀️", style=discord.ButtonStyle.secondary, row=0)
            btn_prev.callback = self.prev_callback
            self.add_item(btn_prev)
            
            btn_next = discord.ui.Button(label="▶️", style=discord.ButtonStyle.secondary, row=0)
            btn_next.callback = self.next_callback
            self.add_item(btn_next)
            
            btn_home = discord.ui.Button(label="🏠 Menu", style=discord.ButtonStyle.success, row=0)
            btn_home.callback = self.home_callback
            self.add_item(btn_home)
            
            # Sélection joueurs (numéros 1-10)
            for i in range(1, 11):
                btn = discord.ui.Button(
                    label=str(i), 
                    style=discord.ButtonStyle.primary, 
                    row=1 if i <= 5 else 2
                )
                btn.callback = self.create_select_callback(i)
                self.add_item(btn)
                
        elif self.mode == "player_actions":
            # Actions joueur
            btn_profile = discord.ui.Button(label="👤 Profil", style=discord.ButtonStyle.primary, row=0)
            btn_profile.callback = self.profile_callback
            self.add_item(btn_profile)
            
            btn_coins = discord.ui.Button(label="🪙 Pièces", style=discord.ButtonStyle.secondary, row=0)
            btn_coins.callback = self.coins_callback
            self.add_item(btn_coins)
            
            btn_ban = discord.ui.Button(label="🔨 Ban/Unban", style=discord.ButtonStyle.danger, row=0)
            btn_ban.callback = self.ban_callback
            self.add_item(btn_ban)
            
            btn_pull = discord.ui.Button(label="🎲 Force Pull", style=discord.ButtonStyle.secondary, row=1)
            btn_pull.callback = self.pull_callback
            self.add_item(btn_pull)
            
            btn_reset = discord.ui.Button(label="🔄 Reset", style=discord.ButtonStyle.danger, row=1)
            btn_reset.callback = self.reset_callback
            self.add_item(btn_reset)
            
            btn_back = discord.ui.Button(label="↩️ Retour", style=discord.ButtonStyle.success, row=1)
            btn_back.callback = self.back_callback
            self.add_item(btn_back)
            
        elif self.mode == "system":
            btn_coins_all = discord.ui.Button(label="🪙 Pièces Tous", style=discord.ButtonStyle.secondary, row=0)
            btn_coins_all.callback = self.coins_all_callback
            self.add_item(btn_coins_all)
            
            btn_stats = discord.ui.Button(label="📊 Stats", style=discord.ButtonStyle.primary, row=0)
            btn_stats.callback = self.stats_callback
            self.add_item(btn_stats)
            
            btn_images = discord.ui.Button(label="🖼️ Images", style=discord.ButtonStyle.secondary, row=0)
            btn_images.callback = self.images_callback
            self.add_item(btn_images)
            
            btn_home = discord.ui.Button(label="🏠 Menu", style=discord.ButtonStyle.success, row=0)
            btn_home.callback = self.home_callback
            self.add_item(btn_home)
    
    # Callbacks pour les boutons
    async def players_callback(self, interaction: discord.Interaction):
        self.mode = "players"
        self.current_page = 0
        embed = await self.create_players_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def system_callback(self, interaction: discord.Interaction):
        self.mode = "system"
        embed = await self.create_system_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def home_callback(self, interaction: discord.Interaction):
        self.mode = "main"
        self.selected_player = None
        embed = await self.create_main_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def prev_callback(self, interaction: discord.Interaction):
        if self.mode == "players" and self.current_page > 0:
            self.current_page -= 1
            embed = await self.create_players_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_callback(self, interaction: discord.Interaction):
        if self.mode == "players":
            cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            max_pages = (total_players - 1) // self.players_per_page
            
            if self.current_page < max_pages:
                self.current_page += 1
                embed = await self.create_players_embed()
                await interaction.response.edit_message(embed=embed, view=self)
    
    async def back_callback(self, interaction: discord.Interaction):
        self.mode = "players"
        embed = await self.create_players_embed()
        await self.update_view()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_select_callback(self, player_num: int):
        async def callback(interaction: discord.Interaction):
            if self.mode != "players":
                return
                
            player_index = player_num - 1
            real_index = self.current_page * self.players_per_page + player_index
            
            cursor = await self.admin_manager.db.db.execute(
                """SELECT p.user_id, p.username, p.coins, 
                          COALESCE(SUM(i.count), 0) as total_chars, p.is_banned
                   FROM players p
                   LEFT JOIN inventory i ON p.user_id = i.user_id
                   GROUP BY p.user_id, p.username, p.coins, p.is_banned
                   ORDER BY p.coins DESC 
                   LIMIT 1 OFFSET ?""",
                (real_index,)
            )
            player_data = await cursor.fetchone()
            
            if player_data:
                self.selected_player = player_data
                self.mode = "player_actions"
                embed = await self.create_player_actions_embed()
                await self.update_view()
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Joueur non trouvé", ephemeral=True)
        
        return callback
    
    # Actions spécifiques avec fonctionnalités complètes
    async def profile_callback(self, interaction: discord.Interaction):
        if not self.selected_player:
            return
            
        user_id, username, coins, chars, banned = self.selected_player
        
        # Récupérer plus d'infos sur le joueur
        cursor = await self.admin_manager.db.db.execute(
            """SELECT last_daily, created_at, total_rerolls 
               FROM players WHERE user_id = ?""",
            (user_id,)
        )
        player_details = await cursor.fetchone()
        
        # Récupérer les personnages les plus rares
        cursor = await self.admin_manager.db.db.execute(
            """SELECT c.name, c.rarity, i.count 
               FROM inventory i 
               JOIN characters c ON i.character_id = c.id 
               WHERE i.user_id = ? 
               ORDER BY c.value DESC LIMIT 5""",
            (user_id,)
        )
        top_chars = await cursor.fetchall()
        
        embed = discord.Embed(
            title="👤 ═══════〔 P R O F I L   J O U E U R 〕═══════ 👤",
            description=f"```\n◆ Profil complet de {username or f'ID:{user_id}'} ◆\n```",
            color=0x3498db
        )
        
        embed.add_field(name="📊 Informations Générales", 
                       value=f"**ID:** {user_id}\n**Nom:** {username or 'Inconnu'}\n**Statut:** {'🔴 Banni' if banned else '🟢 Actif'}", 
                       inline=True)
        
        embed.add_field(name="🪙 Économie", 
                       value=f"**Pièces:** {coins:,}\n**Rerolls:** {player_details[2] if player_details else 0}\n**Daily:** {'✅' if player_details and player_details[0] else '❌'}", 
                       inline=True)
        
        embed.add_field(name="🎴 Collection", 
                       value=f"**Total:** {chars} personnages\n**Créé:** {player_details[1][:10] if player_details else 'Inconnu'}", 
                       inline=True)
        
        if top_chars:
            top_list = []
            for char_name, rarity, count in top_chars:
                emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                top_list.append(f"{emoji} {char_name} ({count}x)")
            
            embed.add_field(name="🪙 Top Personnages", 
                           value="\n".join(top_list), 
                           inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def coins_callback(self, interaction: discord.Interaction):
        if not self.selected_player:
            return
        modal = CoinsModal(self.admin_manager, self.selected_player)
        await interaction.response.send_modal(modal)
    
    async def ban_callback(self, interaction: discord.Interaction):
        if not self.selected_player:
            return
            
        user_id, username, coins, chars, banned = self.selected_player
        action = "débannir" if banned else "bannir"
        new_status = not banned
        
        try:
            await self.admin_manager.db.db.execute(
                "UPDATE players SET is_banned = ? WHERE user_id = ?",
                (new_status, user_id)
            )
            await self.admin_manager.db.db.commit()
            
            status_text = "🔴 BANNI" if new_status else "🟢 ACTIF"
            embed = discord.Embed(
                title="🔨 Statut Modifié",
                description=f"Joueur **{username or f'ID:{user_id}'}** maintenant **{status_text}**",
                color=0xe74c3c if new_status else 0x2ecc71
            )
            
            # Mettre à jour les données locales
            self.selected_player = (user_id, username, coins, chars, new_status)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    async def pull_callback(self, interaction: discord.Interaction):
        if not self.selected_player:
            return
        modal = ForcePullModal(self.admin_manager, self.selected_player)
        await interaction.response.send_modal(modal)
    
    async def reset_callback(self, interaction: discord.Interaction):
        if not self.selected_player:
            return
        view = ConfirmResetView(self.admin_manager, self.selected_player)
        
        user_id, username, coins, chars, banned = self.selected_player
        embed = discord.Embed(
            title="⚠️ Confirmation Reset",
            description=f"**ATTENTION**: Cette action va complètement réinitialiser le profil de **{username or f'ID:{user_id}'}**\n\n• Toutes les pièces perdues\n• Tous les personnages supprimés\n• Tous les succès effacés\n\n**Cette action est IRRÉVERSIBLE**",
            color=0xe74c3c
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def coins_all_callback(self, interaction: discord.Interaction):
        modal = CoinsAllModal(self.admin_manager)
        await interaction.response.send_modal(modal)
    
    async def stats_callback(self, interaction: discord.Interaction):
        try:
            # Statistiques générales
            cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM characters")
            total_chars = (await cursor.fetchone())[0]
            
            cursor = await self.admin_manager.db.db.execute("SELECT SUM(coins) FROM players")
            total_coins = (await cursor.fetchone())[0] or 0
            
            cursor = await self.admin_manager.db.db.execute("SELECT SUM(count) FROM inventory")
            total_collected = (await cursor.fetchone())[0] or 0
            
            # Top joueurs
            cursor = await self.admin_manager.db.db.execute(
                "SELECT username, coins FROM players ORDER BY coins DESC LIMIT 5"
            )
            top_players = await cursor.fetchall()
            
            # Répartition des raretés
            cursor = await self.admin_manager.db.db.execute(
                """SELECT c.rarity, COUNT(*) as count 
                   FROM inventory i 
                   JOIN characters c ON i.character_id = c.id 
                   GROUP BY c.rarity 
                   ORDER BY COUNT(*) DESC"""
            )
            rarity_stats = await cursor.fetchall()
            
            embed = discord.Embed(
                title="📊 ═══════〔 S T A T I S T I Q U E S 〕═══════ 📊",
                description="```\n◆ Statistiques complètes du bot ◆\n```",
                color=0x9370DB
            )
            
            embed.add_field(name="👥 Joueurs", 
                           value=f"**Total:** {total_players}\n**Pièces totales:** {total_coins:,}\n**Personnages collectés:** {total_collected:,}", 
                           inline=True)
            
            embed.add_field(name="🎴 Système", 
                           value=f"**Personnages disponibles:** {total_chars}\n**Version:** {BotConfig.VERSION}", 
                           inline=True)
            
            if top_players:
                top_list = []
                for i, (username, coins) in enumerate(top_players, 1):
                    top_list.append(f"**{i}.** {username or 'Inconnu'} - {coins:,}")
                
                embed.add_field(name="🏆 Top Joueurs", 
                               value="\n".join(top_list), 
                               inline=False)
            
            if rarity_stats:
                rarity_list = []
                for rarity, count in rarity_stats:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                    rarity_list.append(f"{emoji} {rarity}: {count:,}")
                
                embed.add_field(name="🎯 Raretés Collectées", 
                               value="\n".join(rarity_list), 
                               inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    async def images_callback(self, interaction: discord.Interaction):
        view = ImageSuggestView(self.admin_manager, interaction.user.id, [])
        embed = await view.create_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Modales pour les actions admin
class CoinsModal(discord.ui.Modal, title="Gestion des Pièces"):
    def __init__(self, admin_manager, selected_player):
        super().__init__()
        self.admin_manager = admin_manager
        self.selected_player = selected_player
        
    amount = discord.ui.TextInput(
        label="Montant (+ pour donner, - pour retirer)",
        placeholder="Exemple: +1000 ou -500",
        style=discord.TextStyle.short,
        max_length=10
    )
    
    reason = discord.ui.TextInput(
        label="Raison (optionnel)",
        placeholder="Raison de la modification...",
        style=discord.TextStyle.short,
        required=False,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount_str = self.amount.value.strip()
            if not amount_str:
                await interaction.response.send_message("❌ Montant requis", ephemeral=True)
                return
                
            # Parse le montant
            if amount_str.startswith(('+', '-')):
                amount = int(amount_str)
            else:
                amount = int(amount_str)
                
            user_id, username, current_coins, chars, banned = self.selected_player
            new_coins = max(0, current_coins + amount)
            
            await self.admin_manager.db.db.execute(
                "UPDATE players SET coins = ? WHERE user_id = ?",
                (new_coins, user_id)
            )
            await self.admin_manager.db.db.commit()
            
            action = "ajouté" if amount > 0 else "retiré"
            embed = discord.Embed(
                title="🪙 Pièces Modifiées",
                description=f"**{abs(amount):,}** pièces {action} pour **{username or f'ID:{user_id}'}**",
                color=0x2ecc71 if amount > 0 else 0xe74c3c
            )
            embed.add_field(name="Avant", value=f"{current_coins:,}", inline=True)
            embed.add_field(name="Après", value=f"{new_coins:,}", inline=True)
            embed.add_field(name="Différence", value=f"{amount:+,}", inline=True)
            
            if self.reason.value:
                embed.add_field(name="Raison", value=self.reason.value, inline=False)
                
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Montant invalide", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

class ForcePullModal(discord.ui.Modal, title="Forcer un Pull"):
    def __init__(self, admin_manager, selected_player):
        super().__init__()
        self.admin_manager = admin_manager
        self.selected_player = selected_player
        
    rarity = discord.ui.TextInput(
        label="Rareté à forcer",
        placeholder="Common, Rare, Epic, Legendary, Mythic, Titan, Fusion, Secret",
        style=discord.TextStyle.short,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            rarity_input = self.rarity.value.strip().title()
            valid_rarities = list(BotConfig.RARITY_WEIGHTS.keys())
            
            if rarity_input not in valid_rarities:
                await interaction.response.send_message(
                    f"❌ Rareté invalide. Raretés valides: {', '.join(valid_rarities)}", 
                    ephemeral=True
                )
                return
                
            user_id, username, coins, chars, banned = self.selected_player
            
            # Programmer le prochain pull
            await self.admin_manager.db.db.execute(
                "INSERT OR REPLACE INTO forced_pulls (user_id, forced_rarity) VALUES (?, ?)",
                (user_id, rarity_input)
            )
            await self.admin_manager.db.db.commit()
            
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity_input, "◆")
            embed = discord.Embed(
                title="🎲 Pull Forcé Programmé",
                description=f"Le prochain pull de **{username or f'ID:{user_id}'}** sera forcé en **{rarity_emoji} {rarity_input}**",
                color=BotConfig.RARITY_COLORS.get(rarity_input, 0x000000)
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

class CoinsAllModal(discord.ui.Modal, title="Pièces pour Tous"):
    def __init__(self, admin_manager):
        super().__init__()
        self.admin_manager = admin_manager
        
    amount = discord.ui.TextInput(
        label="Montant à donner à tous les joueurs",
        placeholder="Exemple: 1000",
        style=discord.TextStyle.short,
        max_length=10
    )
    
    reason = discord.ui.TextInput(
        label="Raison (optionnel)",
        placeholder="Événement spécial, compensation...",
        style=discord.TextStyle.short,
        required=False,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value.strip())
            if amount <= 0:
                await interaction.response.send_message("❌ Le montant doit être positif", ephemeral=True)
                return
                
            await interaction.response.defer(ephemeral=True)
            
            cursor = await self.admin_manager.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            await self.admin_manager.db.db.execute(
                "UPDATE players SET coins = coins + ?",
                (amount,)
            )
            await self.admin_manager.db.db.commit()
            
            embed = discord.Embed(
                title="🪙 Pièces Distribuées",
                description=f"**{amount:,}** pièces données à **{total_players}** joueurs",
                color=0x2ecc71
            )
            embed.add_field(name="Total distribué", value=f"{amount * total_players:,} pièces", inline=True)
            
            if self.reason.value:
                embed.add_field(name="Raison", value=self.reason.value, inline=False)
                
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.followup.send("❌ Montant invalide", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}", ephemeral=True)

class ConfirmResetView(discord.ui.View):
    def __init__(self, admin_manager, selected_player):
        super().__init__(timeout=30)
        self.admin_manager = admin_manager
        self.selected_player = selected_player
        
    @discord.ui.button(label="✅ CONFIRMER RESET", style=discord.ButtonStyle.danger)
    async def confirm_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            user_id, username, coins, chars, banned = self.selected_player
            
            # Supprimer tout l'inventaire
            await self.admin_manager.db.db.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
            
            # Supprimer les succès
            await self.admin_manager.db.db.execute("DELETE FROM player_achievements WHERE user_id = ?", (user_id,))
            
            # Reset les données du joueur
            await self.admin_manager.db.db.execute(
                """UPDATE players SET 
                   coins = 1000, 
                   total_rerolls = 0, 
                   last_reroll = NULL, 
                   last_daily = NULL 
                   WHERE user_id = ?""",
                (user_id,)
            )
            await self.admin_manager.db.db.commit()
            
            embed = discord.Embed(
                title="🔄 Reset Terminé",
                description=f"Profil de **{username or f'ID:{user_id}'}** complètement réinitialisé",
                color=0x2ecc71
            )
            embed.add_field(name="✅ Actions effectuées", 
                           value="• Inventaire vidé\n• Succès supprimés\n• Pièces reset à 1000\n• Statistiques remises à zéro", 
                           inline=False)
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="❌ ANNULER", style=discord.ButtonStyle.secondary)
    async def cancel_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Reset Annulé",
            description="Aucune modification effectuée",
            color=0x95a5a6
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)