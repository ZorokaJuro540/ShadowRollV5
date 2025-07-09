"""
Simple Admin Interface for Shadow Roll Bot
Clean, working admin panel with basic functionality
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any
from core.config import BotConfig
from modules.utils import get_display_name

logger = logging.getLogger(__name__)

class SimpleAdminView(discord.ui.View):
    """Interface admin simplifiée et fonctionnelle"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.players_per_page = 10
        self.selected_player = None
        
    @discord.ui.button(label="👥 Joueurs", style=discord.ButtonStyle.primary, row=0)
    async def players_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher la liste des joueurs"""
        try:
            embed = await self.create_players_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Erreur liste joueurs: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger la liste des joueurs",
                color=0xe74c3c
            )
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary, row=0)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les statistiques"""
        try:
            embed = await self.create_stats_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Erreur stats: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger les statistiques",
                color=0xe74c3c
            )
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🪙 Pièces", style=discord.ButtonStyle.success, row=0)
    async def coins_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner des pièces à tous"""
        modal = CoinsModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 Actualiser", style=discord.ButtonStyle.secondary, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Actualiser l'affichage"""
        embed = await self.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def create_main_embed(self) -> discord.Embed:
        """Interface principale admin"""
        embed = discord.Embed(
            title="⚙️ ═══════〔 P A N N E A U   A D M I N 〕═══════ ⚙️",
            description="```\n◆ Interface d'administration simplifiée ◆\n```",
            color=0x2c3e50
        )
        
        # Stats rapides
        try:
            db = self.bot.db
            
            # Nombre de joueurs
            cursor = await db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            # Nombre de personnages total
            cursor = await db.db.execute("SELECT COUNT(*) FROM characters")
            total_chars = (await cursor.fetchone())[0]
            
            # Joueur le plus riche
            cursor = await db.db.execute("SELECT username, coins FROM players ORDER BY coins DESC LIMIT 1")
            top_player = await cursor.fetchone()
            
            embed.add_field(
                name="📊 Aperçu Système",
                value=f"**Joueurs:** {total_players}\n**Personnages:** {total_chars}\n**Top joueur:** {top_player[0] if top_player else 'Aucun'} ({top_player[1]:,} pièces)" if top_player else f"**Joueurs:** {total_players}\n**Personnages:** {total_chars}\n**Top joueur:** Aucun",
                inline=False
            )
            
        except Exception as e:
            logger.error(f"Erreur stats principales: {e}")
            embed.add_field(
                name="📊 Aperçu Système",
                value="Erreur de chargement des statistiques",
                inline=False
            )
        
        embed.add_field(
            name="🛠️ Actions Disponibles",
            value="• **👥 Joueurs** - Gérer les joueurs\n• **📊 Stats** - Voir les statistiques\n• **🪙 Pièces** - Donner des pièces à tous\n• **🔄 Actualiser** - Recharger l'interface",
            inline=False
        )
        
        embed.set_footer(text=f"Shadow Roll Admin • {BotConfig.VERSION}")
        return embed
    
    async def create_players_embed(self) -> discord.Embed:
        """Liste des joueurs simplifiée"""
        embed = discord.Embed(
            title="👥 ═══════〔 L I S T E   J O U E U R S 〕═══════ 👥",
            color=0x3498db
        )
        
        try:
            db = self.bot.db
            
            # Récupérer les joueurs
            cursor = await db.db.execute(
                """SELECT user_id, username, coins, is_banned 
                   FROM players 
                   ORDER BY coins DESC 
                   LIMIT ? OFFSET ?""",
                (self.players_per_page, self.current_page * self.players_per_page)
            )
            players = await cursor.fetchall()
            
            if players:
                player_list = []
                for i, (user_id, username, coins, is_banned) in enumerate(players, 1):
                    status = "🔴" if is_banned else "🟢"
                    player_list.append(f"`{i:2d}.` {status} **{username or f'ID:{user_id}'}** - {coins:,} pièces")
                
                embed.add_field(
                    name="📋 Joueurs (Page " + str(self.current_page + 1) + ")",
                    value="\n".join(player_list),
                    inline=False
                )
            else:
                embed.add_field(
                    name="📋 Joueurs",
                    value="Aucun joueur trouvé",
                    inline=False
                )
                
        except Exception as e:
            logger.error(f"Erreur liste joueurs: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de charger la liste des joueurs",
                inline=False
            )
        
        return embed
    
    async def create_stats_embed(self) -> discord.Embed:
        """Statistiques du système"""
        embed = discord.Embed(
            title="📊 ═══════〔 S T A T I S T I Q U E S 〕═══════ 📊",
            color=0x9b59b6
        )
        
        try:
            db = self.bot.db
            
            # Stats joueurs
            cursor = await db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            cursor = await db.db.execute("SELECT COUNT(*) FROM players WHERE is_banned = 1")
            banned_players = (await cursor.fetchone())[0]
            
            # Stats personnages
            cursor = await db.db.execute("SELECT COUNT(*) FROM characters")
            total_chars = (await cursor.fetchone())[0]
            
            cursor = await db.db.execute("SELECT SUM(count) FROM inventory")
            total_owned = (await cursor.fetchone())[0] or 0
            
            # Stats économie
            cursor = await db.db.execute("SELECT SUM(coins), AVG(coins) FROM players")
            economy = await cursor.fetchone()
            total_coins = economy[0] or 0
            avg_coins = economy[1] or 0
            
            embed.add_field(
                name="👥 Joueurs",
                value=f"**Total:** {total_players}\n**Actifs:** {total_players - banned_players}\n**Bannis:** {banned_players}",
                inline=True
            )
            
            embed.add_field(
                name="🎭 Personnages",
                value=f"**Disponibles:** {total_chars}\n**Possédés:** {total_owned}\n**Taux:** {(total_owned/total_chars/total_players*100):.1f}%" if total_players > 0 else f"**Disponibles:** {total_chars}\n**Possédés:** {total_owned}\n**Taux:** 0%",
                inline=True
            )
            
            embed.add_field(
                name="🪙 Économie",
                value=f"**Total:** {total_coins:,}\n**Moyenne:** {avg_coins:,.0f}\n**Par joueur:** {total_coins//total_players:,}" if total_players > 0 else f"**Total:** {total_coins:,}\n**Moyenne:** {avg_coins:,.0f}\n**Par joueur:** 0",
                inline=True
            )
            
        except Exception as e:
            logger.error(f"Erreur statistiques: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de charger les statistiques",
                inline=False
            )
        
        return embed

class CoinsModal(discord.ui.Modal):
    """Modal pour donner des pièces à tous les joueurs"""
    
    def __init__(self, bot):
        super().__init__(title="🪙 Donner des Pièces à Tous")
        self.bot = bot
        
        self.amount = discord.ui.TextInput(
            label="Montant",
            placeholder="Entrez le montant à donner (ex: 1000)",
            required=True,
            max_length=10
        )
        self.add_item(self.amount)
        
        self.reason = discord.ui.TextInput(
            label="Raison",
            placeholder="Raison de la distribution (optionnel)",
            required=False,
            max_length=100
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
            reason = self.reason.value or "Distribution admin"
            
            # Donner les pièces à tous les joueurs
            cursor = await self.bot.db.db.execute("SELECT user_id FROM players WHERE is_banned = 0")
            players = await cursor.fetchall()
            
            for (user_id,) in players:
                await self.bot.db.db.execute(
                    "UPDATE players SET coins = coins + ? WHERE user_id = ?",
                    (amount, user_id)
                )
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Distribution Terminée",
                description=f"**{amount:,} pièces** distribuées à **{len(players)} joueurs**\n\n**Raison:** {reason}",
                color=0x27ae60
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Le montant doit être un nombre valide",
                color=0xe74c3c
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"Erreur distribution pièces: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de distribuer les pièces",
                color=0xe74c3c
            )
            await interaction.response.edit_message(embed=embed, view=None)

async def setup_simple_admin_commands(bot):
    """Configuration des commandes admin simplifiées"""
    
    @bot.command(name='admin', aliases=['adminpanel', 'adminhelp'])
    async def simple_admin_command(ctx):
        """Interface d'administration simplifiée"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas les permissions d'administrateur.")
            return
        
        try:
            view = SimpleAdminView(bot, ctx.author.id)
            embed = await view.create_main_embed()
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Erreur interface admin: {e}")
            await ctx.send("❌ Erreur lors du chargement de l'interface admin.")
    
    logger.info("Commandes admin simplifiées configurées")