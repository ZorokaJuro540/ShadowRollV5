"""
Nouveau Système d'Administration Shadow Roll - Redesign Complet
Interface admin moderne avec commandes fonctionnelles
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta
import aiosqlite

from core.config import BotConfig
from modules.utils import format_number, get_display_name

logger = logging.getLogger(__name__)

class ShadowAdminView(discord.ui.View):
    """Interface admin principale redesignée avec style Shadow"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            return False
        if not BotConfig.is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Accès refusé - Admin requis", ephemeral=True)
            return False
        return True
    
    async def create_main_admin_embed(self) -> discord.Embed:
        """Créer l'embed principal d'administration"""
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"Admin {self.user_id}"
        
        # Obtenir des statistiques pour l'affichage
        try:
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            total_characters = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT SUM(coins) FROM players")
            total_coins = (await cursor.fetchone())[0] or 0
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM series")
            total_series = (await cursor.fetchone())[0]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats admin: {e}")
            total_players = total_characters = total_coins = total_series = 0
        
        embed = discord.Embed(
            title="🌌 ═══════〔 A D M I N I S T R A T I O N   S H A D O W 〕═══════ 🌌",
            description=f"```\n◆ Administrateur: {username} ◆\n◆ Contrôle Total du Système ◆\n```",
            color=BotConfig.RARITY_COLORS['Secret']
        )
        
        embed.add_field(
            name="🌑 ═══〔 Statistiques Système 〕═══ 🌑",
            value=(f"```\n"
                   f"Joueurs Actifs: {total_players}\n"
                   f"Personnages: {total_characters}\n"
                   f"Séries Anime: {total_series}\n"
                   f"Shadow Coins Total: {format_number(total_coins)}\n"
                   f"```"),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Catégories Disponibles",
            value=("```\n"
                   "👥 Joueurs - Gestion utilisateurs\n"
                   "🎴 Personnages - Création/Edition\n"
                   "🎖️ Séries - Organisation anime\n"
                   "🪙 Économie - Gestion coins\n"
                   "🔧 Système - Configuration\n"
                   "📊 Stats - Données détaillées\n"
                   "```"),
            inline=True
        )
        
        embed.add_field(
            name="⚡ Actions Rapides",
            value=("```\n"
                   "🚀 Commandes Express\n"
                   "🔍 Recherche Rapide\n"
                   "🛠️ Outils Maintenance\n"
                   "📋 Logs Système\n"
                   "💾 Sauvegarde DB\n"
                   "🔄 Sync Discord\n"
                   "```"),
            inline=True
        )
        
        embed.set_footer(
            text="Shadow Roll • Administration",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        return embed
    
    # ═══════════════════ BOUTONS PRINCIPAUX ═══════════════════
    
    @discord.ui.button(label="👥 Joueurs", style=discord.ButtonStyle.primary, row=0)
    async def players_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des joueurs"""
        await interaction.response.defer()
        view = PlayersManagementView(self.bot, self.user_id)
        embed = await view.create_players_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🎴 Personnages", style=discord.ButtonStyle.secondary, row=0)
    async def characters_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des personnages"""
        await interaction.response.defer()
        view = CharactersManagementView(self.bot, self.user_id)
        embed = await view.create_characters_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🎖️ Séries", style=discord.ButtonStyle.success, row=0)
    async def series_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des séries anime"""
        await interaction.response.defer()
        from modules.admin_series import SeriesManagementView
        view = SeriesManagementView(self.bot, self.user_id)
        embed = await view.create_main_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🪙 Économie", style=discord.ButtonStyle.success, row=0)
    async def economy_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion économique"""
        await interaction.response.defer()
        view = EconomyManagementView(self.bot, self.user_id)
        embed = await view.create_economy_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🔧 Système", style=discord.ButtonStyle.danger, row=1)
    async def system_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Administration système"""
        await interaction.response.defer()
        view = SystemManagementView(self.bot, self.user_id)
        embed = await view.create_system_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, row=1)
    async def stats_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Statistiques détaillées"""
        await interaction.response.defer()
        view = StatsManagementView(self.bot, self.user_id)
        embed = await view.create_stats_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🚀 Actions Rapides", style=discord.ButtonStyle.primary, row=1)
    async def quick_actions(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Actions rapides"""
        await interaction.response.defer()
        view = QuickActionsView(self.bot, self.user_id)
        embed = await view.create_quick_actions_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        await interaction.response.defer()
        from modules.menu import create_main_menu_embed, ShadowMenuView
        embed = await create_main_menu_embed(self.bot, self.user_id)
        view = ShadowMenuView(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class PlayersManagementView(discord.ui.View):
    """Gestion des joueurs avec fonctionnalités complètes"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.players_per_page = 5
        self.search_query = ""
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_players_embed(self) -> discord.Embed:
        """Créer l'embed de gestion des joueurs"""
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"Admin {self.user_id}"
        
        embed = discord.Embed(
            title="🌌 ═══════〔 G E S T I O N   J O U E U R S 〕═══════ 🌌",
            description=f"```\n◆ Administrateur: {username} ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        try:
            # Récupérer les joueurs avec pagination
            offset = self.current_page * self.players_per_page
            
            if self.search_query:
                cursor = await self.bot.db.db.execute("""
                    SELECT user_id, username, coins, total_rerolls, is_banned, created_at
                    FROM players 
                    WHERE username LIKE ?
                    ORDER BY coins DESC, total_rerolls DESC
                    LIMIT ? OFFSET ?
                """, (f"%{self.search_query}%", self.players_per_page, offset))
                
                count_cursor = await self.bot.db.db.execute("""
                    SELECT COUNT(*) FROM players WHERE username LIKE ?
                """, (f"%{self.search_query}%",))
            else:
                cursor = await self.bot.db.db.execute("""
                    SELECT user_id, username, coins, total_rerolls, is_banned, created_at
                    FROM players 
                    ORDER BY coins DESC, total_rerolls DESC
                    LIMIT ? OFFSET ?
                """, (self.players_per_page, offset))
                
                count_cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            
            players = await cursor.fetchall()
            total_players = (await count_cursor.fetchone())[0]
            
            if not players:
                embed.add_field(
                    name="🌑 ═══〔 Aucun Joueur Trouvé 〕═══ 🌑",
                    value="```\n◆ Aucun joueur ne correspond aux critères\n◆ Modifiez votre recherche\n```",
                    inline=False
                )
            else:
                players_text = ""
                for i, (user_id, username, coins, rerolls, banned, created) in enumerate(players):
                    status = "🔴 BAN" if banned else "🟢 ACTIF"
                    rank = offset + i + 1
                    # Tronquer le nom d'utilisateur s'il est trop long
                    display_name = username[:15] + "..." if len(username) > 15 else username
                    new_line = f"{rank}. **{display_name}**\n   🪙 {format_number(coins)} SC | 🎲 {rerolls} | {status}\n\n"
                    
                    # Vérifier si ajouter cette ligne dépasserait la limite de 1024 caractères
                    if len(players_text + new_line) > 1000:
                        players_text += "... (liste tronquée)\n"
                        break
                    players_text += new_line
                
                # S'assurer que le texte ne dépasse pas 1024 caractères
                if len(players_text) > 1024:
                    players_text = players_text[:1000] + "... (tronqué)"
                
                embed.add_field(
                    name=f"🌑 ═══〔 Joueurs {offset+1}-{min(offset+len(players), total_players)} sur {total_players} 〕═══ 🌑",
                    value=players_text or "Aucun joueur à afficher",
                    inline=False
                )
                
                # Navigation
                total_pages = (total_players + self.players_per_page - 1) // self.players_per_page
                embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages} • Recherche: {self.search_query or 'Tous'}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des joueurs: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de récupérer les données des joueurs",
                inline=False
            )
        
        return embed
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.primary, row=0)
    async def search_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un joueur"""
        modal = PlayerSearchModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎒 Voir Inventaire", style=discord.ButtonStyle.success, row=0)
    async def view_player_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Voir l'inventaire d'un joueur"""
        modal = PlayerInventoryModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎁 Donner Personnage", style=discord.ButtonStyle.primary, row=0)
    async def give_character_to_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner un personnage à un joueur par nom"""
        modal = GiveCharacterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🆔 Donner par ID", style=discord.ButtonStyle.primary, row=1)
    async def give_character_by_id(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner un personnage à un joueur par ID"""
        modal = GiveCharacterByIdModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 Rafraîchir", style=discord.ButtonStyle.secondary, row=0)
    async def refresh_players(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rafraîchir la liste"""
        await interaction.response.defer()
        embed = await self.create_players_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_players_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la première page", ephemeral=True)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        try:
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            total_pages = (total_players + self.players_per_page - 1) // self.players_per_page
            
            if self.current_page < total_pages - 1:
                self.current_page += 1
                await interaction.response.defer()
                embed = await self.create_players_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("Déjà à la dernière page", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Erreur lors du changement de page", ephemeral=True)
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class PlayerSearchModal(discord.ui.Modal, title='🔍 Rechercher un Joueur'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    search_input = discord.ui.TextInput(
        label='Nom du joueur',
        placeholder='Tapez le nom du joueur à rechercher...',
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.search_query = self.search_input.value.strip()
        self.parent_view.current_page = 0
        await interaction.response.defer()
        embed = await self.parent_view.create_players_embed()
        await interaction.edit_original_response(embed=embed, view=self.parent_view)


class PlayerInventoryModal(discord.ui.Modal, title='🎒 Inventaire Joueur'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='ID Discord ou nom du joueur',
        placeholder='123456789012345678 ou @username',
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_input = self.user_input.value.strip()
        
        # Chercher le joueur
        try:
            # Essayer d'abord par ID Discord
            if user_input.isdigit():
                user_id = int(user_input)
            else:
                # Chercher par nom d'utilisateur
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{user_input}%",)
                )
                result = await cursor.fetchone()
                if not result:
                    await interaction.followup.send("❌ Aucun joueur trouvé avec ce nom", ephemeral=True)
                    return
                user_id = result[0]
            
            # Créer la vue d'inventaire
            view = PlayerInventoryView(self.parent_view.bot, self.parent_view.user_id, user_id)
            embed = await view.create_inventory_embed()
            await interaction.edit_original_response(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Erreur recherche inventaire: {e}")
            await interaction.followup.send(f"❌ Erreur lors de la recherche: {str(e)}", ephemeral=True)


class PlayerInventoryView(discord.ui.View):
    """Vue pour afficher l'inventaire d'un joueur spécifique"""
    
    def __init__(self, bot, admin_id: int, target_user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.admin_id = admin_id
        self.target_user_id = target_user_id
        self.current_page = 0
        self.items_per_page = 15
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.admin_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_inventory_embed(self) -> discord.Embed:
        """Créer l'embed d'inventaire du joueur"""
        try:
            # Récupérer les informations du joueur
            cursor = await self.bot.db.db.execute(
                "SELECT username, coins, total_rerolls, is_banned FROM players WHERE user_id = ?",
                (self.target_user_id,)
            )
            player_data = await cursor.fetchone()
            
            if not player_data:
                embed = discord.Embed(
                    title="❌ Joueur Introuvable",
                    description="Ce joueur n'existe pas dans la base de données",
                    color=0xff0000
                )
                return embed
            
            username, coins, total_rerolls, is_banned = player_data
            user = self.bot.get_user(self.target_user_id)
            display_name = user.display_name if user else username
            
            # Récupérer l'inventaire avec pagination
            offset = self.current_page * self.items_per_page
            cursor = await self.bot.db.db.execute(
                '''SELECT i.id, c.name, c.anime, c.rarity, c.value, i.count, c.image_url
                   FROM inventory i
                   JOIN characters c ON i.character_id = c.id
                   WHERE i.user_id = ?
                   ORDER BY 
                       CASE c.rarity
                           WHEN 'Secret' THEN 8
                           WHEN 'Fusion' THEN 7
                           WHEN 'Titan' THEN 6
                           WHEN 'Evolve' THEN 5.5
                           WHEN 'Mythic' THEN 5
                           WHEN 'Legendary' THEN 4
                           WHEN 'Epic' THEN 3
                           WHEN 'Rare' THEN 2
                           WHEN 'Common' THEN 1
                       END DESC,
                       c.value DESC, c.name
                   LIMIT ? OFFSET ?''',
                (self.target_user_id, self.items_per_page, offset)
            )
            inventory_items = await cursor.fetchall()
            
            # Compter le total d'éléments
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE user_id = ?",
                (self.target_user_id,)
            )
            total_items = (await cursor.fetchone())[0]
            
            # Statistiques d'inventaire
            cursor = await self.bot.db.db.execute(
                '''SELECT 
                       COUNT(DISTINCT i.character_id) as unique_characters,
                       SUM(i.count) as total_characters,
                       SUM(c.value * i.count) as total_value,
                       c.rarity,
                       SUM(i.count) as rarity_count
                   FROM inventory i
                   JOIN characters c ON i.character_id = c.id
                   WHERE i.user_id = ?
                   GROUP BY c.rarity''',
                (self.target_user_id,)
            )
            stats_data = await cursor.fetchall()
            
            # Calculer les statistiques
            unique_chars = sum(row[0] for row in stats_data) if stats_data else 0
            total_chars = sum(row[1] for row in stats_data) if stats_data else 0
            total_value = sum(row[2] for row in stats_data) if stats_data else 0
            
            rarity_counts = {}
            for row in stats_data:
                rarity_counts[row[3]] = row[4]
            
            # Créer l'embed
            status_icon = "🔴" if is_banned else "🟢"
            embed = discord.Embed(
                title=f"🎒 ═══════〔 I N V E N T A I R E   J O U E U R 〕═══════ 🎒",
                description=f"```\n◆ {display_name} ({self.target_user_id}) {status_icon} ◆\n```",
                color=BotConfig.RARITY_COLORS['Mythic']
            )
            
            # Informations générales
            embed.add_field(
                name="🪙 Richesse",
                value=f"```\n{format_number(coins)} SC\n```",
                inline=True
            )
            
            embed.add_field(
                name="🎲 Invocations",
                value=f"```\n{format_number(total_rerolls)}\n```",
                inline=True
            )
            
            embed.add_field(
                name="🎴 Collection",
                value=f"```\n{unique_chars} uniques\n{total_chars} total\n```",
                inline=True
            )
            
            # Répartition par rareté
            if rarity_counts:
                rarity_text = ""
                for rarity in ['Secret', 'Fusion', 'Titan', 'Evolve', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                    count = rarity_counts.get(rarity, 0)
                    if count > 0:
                        emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                        rarity_text += f"{emoji} {rarity}: {count}\n"
                
                if rarity_text:
                    embed.add_field(
                        name="📊 Répartition par Rareté",
                        value=f"```\n{rarity_text}```",
                        inline=False
                    )
            
            # Liste des personnages (page actuelle)
            if inventory_items:
                items_text = ""
                for item in inventory_items:
                    _, name, anime, rarity, value, count, _ = item
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    count_text = f"x{count}" if count > 1 else ""
                    items_text += f"{emoji} **{name}** {count_text}\n"
                    items_text += f"└─ {anime} • {format_number(value)} SC\n"
                
                embed.add_field(
                    name=f"🎴 Personnages (Page {self.current_page + 1})",
                    value=items_text[:1024],  # Limite Discord
                    inline=False
                )
            else:
                embed.add_field(
                    name="📭 Collection Vide",
                    value="Ce joueur n'a aucun personnage",
                    inline=False
                )
            
            # Footer avec pagination
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page if total_items > 0 else 1
            embed.set_footer(
                text=f"Page {self.current_page + 1}/{total_pages} • Valeur totale: {format_number(total_value)} SC"
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur création inventaire admin: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible d'afficher l'inventaire: {str(e)}",
                color=0xff0000
            )
            return embed
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_inventory_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la première page", ephemeral=True)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        try:
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE user_id = ?",
                (self.target_user_id,)
            )
            total_items = (await cursor.fetchone())[0]
            total_pages = (total_items + self.items_per_page - 1) // self.items_per_page if total_items > 0 else 1
            
            if self.current_page < total_pages - 1:
                self.current_page += 1
                await interaction.response.defer()
                embed = await self.create_inventory_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("Déjà à la dernière page", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Erreur lors du changement de page", ephemeral=True)
    
    @discord.ui.button(label="🔄 Rafraîchir", style=discord.ButtonStyle.primary, row=0)
    async def refresh_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rafraîchir l'inventaire"""
        await interaction.response.defer()
        embed = await self.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Retour Admin", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = PlayersManagementView(self.bot, self.admin_id)
        embed = await view.create_players_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class PlayerActionModal(discord.ui.Modal, title='⚡ Action sur Joueur'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='ID ou nom du joueur',
        placeholder='Tapez l\'ID Discord ou le nom du joueur...',
        required=True,
        max_length=100
    )
    
    action_input = discord.ui.TextInput(
        label='Action',
        placeholder='ban, unban, givecoins, removecoins, reset, profile',
        required=True,
        max_length=50
    )
    
    amount_input = discord.ui.TextInput(
        label='Montant (pour coins)',
        placeholder='Montant de coins (optionnel)',
        required=False,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_identifier = self.user_input.value.strip()
        action = self.action_input.value.strip().lower()
        amount = self.amount_input.value.strip()
        
        try:
            # Trouver le joueur
            if user_identifier.isdigit():
                user_id = int(user_identifier)
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE user_id = ?", (user_id,)
                )
            else:
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE username LIKE ?", (f"%{user_identifier}%",)
                )
            
            player = await cursor.fetchone()
            if not player:
                await interaction.followup.send("❌ Joueur non trouvé", ephemeral=True)
                return
            
            user_id, username = player
            result_message = ""
            
            # Exécuter l'action
            if action == "ban":
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET is_banned = TRUE WHERE user_id = ?", (user_id,)
                )
                await self.parent_view.bot.db.db.commit()
                result_message = f"✅ Joueur {username} banni avec succès"
                
            elif action == "unban":
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET is_banned = FALSE WHERE user_id = ?", (user_id,)
                )
                await self.parent_view.bot.db.db.commit()
                result_message = f"✅ Joueur {username} débanni avec succès"
                
            elif action == "givecoins" and amount.isdigit():
                amount_int = int(amount)
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET coins = coins + ? WHERE user_id = ?", (amount_int, user_id)
                )
                await self.parent_view.bot.db.db.commit()
                result_message = f"✅ {format_number(amount_int)} Shadow Coins donnés à {username}"
                
            elif action == "removecoins" and amount.isdigit():
                amount_int = int(amount)
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET coins = MAX(0, coins - ?) WHERE user_id = ?", (amount_int, user_id)
                )
                await self.parent_view.bot.db.db.commit()
                result_message = f"✅ {format_number(amount_int)} Shadow Coins retirés à {username}"
                
            elif action == "reset":
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET coins = ?, total_rerolls = 0, last_reroll = NULL, last_daily = NULL WHERE user_id = ?", 
                    (BotConfig.STARTING_COINS, user_id)
                )
                await self.parent_view.bot.db.db.commit()
                result_message = f"✅ Profil de {username} réinitialisé"
                
            elif action == "profile":
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT coins, total_rerolls, is_banned, created_at FROM players WHERE user_id = ?", (user_id,)
                )
                profile_data = await cursor.fetchone()
                coins, rerolls, banned, created = profile_data
                status = "🔴 BANNI" if banned else "🟢 ACTIF"
                result_message = (f"📊 **Profil de {username}**\n"
                                f"🪙 Coins: {format_number(coins)}\n"
                                f"🎲 Rolls: {rerolls}\n"
                                f"📅 Créé: {created}\n"
                                f"🏷️ Statut: {status}")
            else:
                result_message = "❌ Action invalide ou montant manquant"
            
            await interaction.followup.send(result_message, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'action joueur: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class GiveCharacterModal(discord.ui.Modal, title='🎁 Donner Personnage'):
    """Modal pour donner un personnage par nom"""
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='Joueur cible',
        placeholder='ID Discord ou nom du joueur...',
        required=True,
        max_length=100
    )
    
    character_input = discord.ui.TextInput(
        label='Nom du personnage',
        placeholder='Nom exact ou partiel du personnage...',
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_identifier = self.user_input.value.strip()
        character_name = self.character_input.value.strip()
        
        try:
            # Importer la fonction de commande
            from modules.admin_character_persistent import give_character_to_user
            
            # Exécuter la commande give character
            success, message = await give_character_to_user(
                self.parent_view.bot, 
                interaction.user.id,
                user_identifier, 
                character_name
            )
            
            if success:
                await interaction.followup.send(f"✅ {message}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du don de personnage: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class GiveCharacterByIdModal(discord.ui.Modal, title='🆔 Donner Personnage par ID'):
    """Modal pour donner un personnage par ID"""
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='Joueur cible',
        placeholder='ID Discord ou nom du joueur...',
        required=True,
        max_length=100
    )
    
    character_id_input = discord.ui.TextInput(
        label='ID du personnage',
        placeholder='ID numérique du personnage...',
        required=True,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_identifier = self.user_input.value.strip()
        character_id = self.character_id_input.value.strip()
        
        try:
            if not character_id.isdigit():
                await interaction.followup.send("❌ L'ID du personnage doit être un nombre", ephemeral=True)
                return
            
            # Importer la fonction de commande
            from modules.admin_character_persistent import give_character_by_id_to_user
            
            # Exécuter la commande give character by ID
            success, message = await give_character_by_id_to_user(
                self.parent_view.bot, 
                interaction.user.id,
                user_identifier, 
                int(character_id)
            )
            
            if success:
                await interaction.followup.send(f"✅ {message}", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ {message}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du don de personnage par ID: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class CharactersManagementView(discord.ui.View):
    """Gestion des personnages avec création/édition/suppression"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.characters_per_page = 10
        self.search_query = ""
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_characters_embed(self) -> discord.Embed:
        """Créer l'embed de gestion des personnages"""
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"Admin {self.user_id}"
        
        embed = discord.Embed(
            title="🌌 ═══════〔 G E S T I O N   P E R S O N N A G E S 〕═══════ 🌌",
            description=f"```\n◆ Administrateur: {username} ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        try:
            # Récupérer les personnages avec pagination
            offset = self.current_page * self.characters_per_page
            
            if self.search_query:
                cursor = await self.bot.db.db.execute("""
                    SELECT id, name, anime, rarity, value, image_url
                    FROM characters 
                    WHERE name LIKE ? OR anime LIKE ?
                    ORDER BY rarity, name
                    LIMIT ? OFFSET ?
                """, (f"%{self.search_query}%", f"%{self.search_query}%", self.characters_per_page, offset))
                
                count_cursor = await self.bot.db.db.execute("""
                    SELECT COUNT(*) FROM characters WHERE name LIKE ? OR anime LIKE ?
                """, (f"%{self.search_query}%", f"%{self.search_query}%"))
            else:
                cursor = await self.bot.db.db.execute("""
                    SELECT id, name, anime, rarity, value, image_url
                    FROM characters 
                    ORDER BY rarity, name
                    LIMIT ? OFFSET ?
                """, (self.characters_per_page, offset))
                
                count_cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            
            characters = await cursor.fetchall()
            total_characters = (await count_cursor.fetchone())[0]
            
            if not characters:
                embed.add_field(
                    name="🌑 ═══〔 Aucun Personnage Trouvé 〕═══ 🌑",
                    value="```\n◆ Aucun personnage ne correspond aux critères\n◆ Modifiez votre recherche\n```",
                    inline=False
                )
            else:
                characters_text = ""
                for char_id, name, anime, rarity, value, image_url in characters:
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                    has_image = "🖼️" if image_url else "📷"
                    characters_text += f"{rarity_emoji} **{name}** ({anime})\n"
                    characters_text += f"   💎 {rarity} | 🪙 {format_number(value)} SC | {has_image}\n\n"
                
                embed.add_field(
                    name=f"🌑 ═══〔 Personnages {offset+1}-{min(offset+len(characters), total_characters)} sur {total_characters} 〕═══ 🌑",
                    value=characters_text,
                    inline=False
                )
                
                # Navigation
                total_pages = (total_characters + self.characters_per_page - 1) // self.characters_per_page
                embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages} • Recherche: {self.search_query or 'Tous'}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des personnages: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de récupérer les données des personnages",
                inline=False
            )
        
        return embed
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.primary, row=0)
    async def search_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un personnage"""
        modal = CharacterSearchModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➕ Créer", style=discord.ButtonStyle.success, row=0)
    async def create_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un nouveau personnage"""
        modal = CreateCharacterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="✏️ Modifier", style=discord.ButtonStyle.secondary, row=0)
    async def edit_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modifier un personnage existant par nom ou ID"""
        modal = ModifyCharacterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, row=0)
    async def delete_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer un personnage"""
        modal = DeleteCharacterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_characters_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la première page", ephemeral=True)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        try:
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            total_characters = (await cursor.fetchone())[0]
            total_pages = (total_characters + self.characters_per_page - 1) // self.characters_per_page
            
            if self.current_page < total_pages - 1:
                self.current_page += 1
                await interaction.response.defer()
                embed = await self.create_characters_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("Déjà à la dernière page", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Erreur lors du changement de page", ephemeral=True)
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class CharacterSearchModal(discord.ui.Modal, title='🔍 Rechercher un Personnage'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    search_input = discord.ui.TextInput(
        label='Nom du personnage ou anime',
        placeholder='Tapez le nom du personnage ou de l\'anime...',
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.search_query = self.search_input.value.strip()
        self.parent_view.current_page = 0
        await interaction.response.defer()
        embed = await self.parent_view.create_characters_embed()
        await interaction.edit_original_response(embed=embed, view=self.parent_view)


class CreateCharacterModal(discord.ui.Modal, title='➕ Créer un Personnage'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    name_input = discord.ui.TextInput(
        label='Nom du personnage',
        placeholder='Ex: Naruto Uzumaki',
        required=True,
        max_length=100
    )
    
    anime_input = discord.ui.TextInput(
        label='Anime/Série',
        placeholder='Ex: Naruto',
        required=True,
        max_length=100
    )
    
    rarity_input = discord.ui.TextInput(
        label='Rareté',
        placeholder='Common, Rare, Epic, Legendary, Mythic, Titan, Fusion, Secret, Evolve',
        required=True,
        max_length=20
    )
    
    value_input = discord.ui.TextInput(
        label='Valeur en Shadow Coins',
        placeholder='Ex: 1000',
        required=True,
        max_length=20
    )
    
    image_input = discord.ui.TextInput(
        label='URL de l\'image (optionnel)',
        placeholder='https://example.com/image.png',
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            name = self.name_input.value.strip()
            anime = self.anime_input.value.strip()
            rarity = self.rarity_input.value.strip()
            value = int(self.value_input.value.strip())
            image_url = self.image_input.value.strip() or None
            
            # Valider la rareté
            if rarity not in BotConfig.RARITY_WEIGHTS:
                await interaction.followup.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}", ephemeral=True)
                return
            
            # Vérifier si le personnage existe déjà
            cursor = await self.parent_view.bot.db.db.execute(
                "SELECT COUNT(*) FROM characters WHERE name = ? AND anime = ?", (name, anime)
            )
            if (await cursor.fetchone())[0] > 0:
                await interaction.followup.send(f"❌ Le personnage {name} de {anime} existe déjà", ephemeral=True)
                return
            
            # Créer le personnage avec persistance garantie
            from character_manager import add_character_with_persistence
            success = await add_character_with_persistence(
                name, anime, rarity, value, image_url or "", interaction.user.id
            )
            
            if success:
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                await interaction.followup.send(
                    f"✅ Personnage créé avec succès et sauvegardé!\n"
                    f"{rarity_emoji} **{name}** ({anime})\n"
                    f"💎 {rarity} | 🪙 {format_number(value)} SC\n"
                    f"📁 Stocké de manière permanente",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Erreur lors de la création du personnage {name}",
                    ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_characters_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except ValueError:
            await interaction.followup.send("❌ Valeur invalide pour les Shadow Coins", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur lors de la création du personnage: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class ModifyCharacterModal(discord.ui.Modal, title='📝 Modifier Personnage'):
    """Modal pour modifier un personnage par nom ou ID"""
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    character_input = discord.ui.TextInput(
        label='Nom ou ID du personnage',
        placeholder='Ex: L ou 283',
        required=True,
        max_length=100
    )
    
    field_input = discord.ui.TextInput(
        label='Champ à modifier',
        placeholder='name, anime, rarity, value, image_url',
        required=True,
        max_length=20
    )
    
    new_value_input = discord.ui.TextInput(
        label='Nouvelle valeur',
        placeholder='Nouvelle valeur pour le champ...',
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            character_input = self.character_input.value.strip()
            field = self.field_input.value.strip().lower()
            new_value = self.new_value_input.value.strip()
            
            # Valider le champ
            valid_fields = ['name', 'anime', 'rarity', 'value', 'image_url']
            if field not in valid_fields:
                await interaction.followup.send(f"❌ Champ invalide. Utilisez: {', '.join(valid_fields)}", ephemeral=True)
                return
            
            # Importer le gestionnaire de personnages
            from character_manager import setup_character_manager
            character_manager = await setup_character_manager()
            
            # Déterminer si l'input est un ID ou un nom
            character = None
            search_type = ""
            
            if character_input.isdigit():
                # Recherche par ID
                char_id = int(character_input)
                character = await character_manager.get_character_by_id(char_id)
                search_type = f"ID {char_id}"
                
                if not character:
                    await interaction.followup.send(f"❌ Aucun personnage trouvé avec l'ID {char_id}", ephemeral=True)
                    return
            else:
                # Recherche par nom
                characters = await character_manager.search_characters(character_input)
                search_type = f"nom '{character_input}'"
                
                if not characters:
                    await interaction.followup.send(f"❌ Aucun personnage trouvé pour '{character_input}'", ephemeral=True)
                    return
                
                if len(characters) > 1:
                    # Multiple characters found
                    char_list = ""
                    for i, char in enumerate(characters[:5], 1):
                        char_list += f"{i}. ID {char['id']}: **{char['name']}** ({char['anime']}) - {char['rarity']}\n"
                    
                    await interaction.followup.send(
                        f"🔍 **{len(characters)} personnages trouvés**\n"
                        f"{char_list}\n"
                        f"💡 **Utilisez l'ID pour être précis:**\n"
                        f"Exemple: {characters[0]['id']} au lieu de {character_input}",
                        ephemeral=True
                    )
                    return
                
                character = characters[0]
            
            old_value = character.get(field, 'N/A')
            
            # Valider les valeurs spéciales
            if field == 'rarity':
                if new_value not in BotConfig.RARITY_WEIGHTS:
                    await interaction.followup.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}", ephemeral=True)
                    return
            elif field == 'value':
                try:
                    new_value = int(new_value)
                except ValueError:
                    await interaction.followup.send("❌ La valeur doit être un nombre entier", ephemeral=True)
                    return
            
            # Appliquer la modification
            success = await character_manager.update_character_field(character['id'], field, new_value)
            
            if success:
                # Créer l'embed de confirmation
                rarity_color = BotConfig.RARITY_COLORS.get(character.get('rarity', 'Common'), 0x808080)
                embed = discord.Embed(
                    title="✅ Personnage Modifié avec Succès",
                    description=f"**{character['name']}** ({character['anime']})",
                    color=rarity_color
                )
                
                embed.add_field(name="🆔 ID", value=str(character['id']), inline=True)
                embed.add_field(name="🔍 Trouvé par", value=search_type, inline=True)
                embed.add_field(name="📝 Champ", value=field.capitalize(), inline=True)
                embed.add_field(name="📋 Ancienne valeur", value=str(old_value), inline=True)
                embed.add_field(name="✨ Nouvelle valeur", value=str(new_value), inline=True)
                embed.add_field(name="💾 Statut", value="✅ Sauvegardé", inline=True)
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                logger.info(f"Admin {interaction.user.id} modified character {character['id']} via {search_type}: {field} = {new_value}")
                
                # Actualiser l'affichage
                embed = await self.parent_view.create_characters_embed()
                await interaction.edit_original_response(embed=embed, view=self.parent_view)
            else:
                await interaction.followup.send(f"❌ Erreur lors de la modification du personnage trouvé par {search_type}", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Erreur lors de la modification du personnage: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class EditCharacterModal(discord.ui.Modal, title='✏️ Modifier un Personnage'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    search_input = discord.ui.TextInput(
        label='Nom du personnage à modifier',
        placeholder='Tapez le nom exact du personnage...',
        required=True,
        max_length=100
    )
    
    field_input = discord.ui.TextInput(
        label='Champ à modifier',
        placeholder='name, anime, rarity, value, image_url',
        required=True,
        max_length=20
    )
    
    new_value_input = discord.ui.TextInput(
        label='Nouvelle valeur',
        placeholder='Nouvelle valeur pour le champ...',
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            char_name = self.search_input.value.strip()
            field = self.field_input.value.strip().lower()
            new_value = self.new_value_input.value.strip()
            
            # Valider le champ
            valid_fields = ['name', 'anime', 'rarity', 'value', 'image_url']
            if field not in valid_fields:
                await interaction.followup.send(f"❌ Champ invalide. Utilisez: {', '.join(valid_fields)}", ephemeral=True)
                return
            
            # Vérifier si le personnage existe
            cursor = await self.parent_view.bot.db.db.execute(
                "SELECT id, name, anime FROM characters WHERE name LIKE ?", (f"%{char_name}%",)
            )
            character = await cursor.fetchone()
            
            if not character:
                await interaction.followup.send(f"❌ Personnage '{char_name}' non trouvé", ephemeral=True)
                return
            
            char_id, old_name, anime = character
            
            # Valider la nouvelle valeur selon le champ
            if field == 'value':
                try:
                    new_value = int(new_value)
                except ValueError:
                    await interaction.followup.send("❌ La valeur doit être un nombre entier", ephemeral=True)
                    return
            elif field == 'rarity' and new_value not in BotConfig.RARITY_WEIGHTS:
                await interaction.followup.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}", ephemeral=True)
                return
            
            # Mettre à jour le personnage
            await self.parent_view.bot.db.db.execute(
                f"UPDATE characters SET {field} = ? WHERE id = ?", (new_value, char_id)
            )
            await self.parent_view.bot.db.db.commit()
            
            await interaction.followup.send(
                f"✅ Personnage modifié avec succès!\n"
                f"**{old_name}** ({anime})\n"
                f"Champ '{field}' mis à jour: {new_value}",
                ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_characters_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur lors de la modification du personnage: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class DeleteCharacterModal(discord.ui.Modal, title='🗑️ Supprimer un Personnage'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    search_input = discord.ui.TextInput(
        label='Nom ou ID du personnage à supprimer',
        placeholder='Tapez le nom exact du personnage ou son ID (ex: 283)...',
        required=True,
        max_length=100
    )
    
    confirm_input = discord.ui.TextInput(
        label='Confirmation (tapez "SUPPRIMER")',
        placeholder='SUPPRIMER',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            char_input = self.search_input.value.strip()
            confirmation = self.confirm_input.value.strip()
            
            if confirmation != "SUPPRIMER":
                await interaction.followup.send("❌ Confirmation incorrecte. Tapez exactement 'SUPPRIMER'", ephemeral=True)
                return
            
            # Vérifier si l'input est un ID numérique
            character = None
            if char_input.isdigit():
                # Recherche par ID
                char_id = int(char_input)
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT id, name, anime FROM characters WHERE id = ?", (char_id,)
                )
                character = await cursor.fetchone()
                search_type = f"ID {char_id}"
            else:
                # Recherche par nom (exacte d'abord, puis partielle)
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT id, name, anime FROM characters WHERE LOWER(name) = LOWER(?)", (char_input,)
                )
                character = await cursor.fetchone()
                
                if not character:
                    # Si pas trouvé exactement, recherche partielle
                    cursor = await self.parent_view.bot.db.db.execute(
                        "SELECT id, name, anime FROM characters WHERE name LIKE ?", (f"%{char_input}%",)
                    )
                    character = await cursor.fetchone()
                search_type = f"nom '{char_input}'"
            
            if not character:
                await interaction.followup.send(f"❌ Personnage avec {search_type} non trouvé", ephemeral=True)
                return
            
            char_id, name, anime = character
            
            # Vérifier s'il y a des inventaires liés
            cursor = await self.parent_view.bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE character_id = ?", (char_id,)
            )
            inventory_count = (await cursor.fetchone())[0]
            
            # Supprimer le personnage et ses données liées
            await self.parent_view.bot.db.db.execute("DELETE FROM inventory WHERE character_id = ?", (char_id,))
            await self.parent_view.bot.db.db.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            await self.parent_view.bot.db.db.commit()
            
            await interaction.followup.send(
                f"✅ Personnage supprimé avec succès!\n"
                f"**{name}** (ID: {char_id}) - {anime}\n"
                f"Également supprimé de {inventory_count} inventaire(s)",
                ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_characters_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du personnage: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class EconomyManagementView(discord.ui.View):
    """Gestion de l'économie du jeu"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_economy_embed(self) -> discord.Embed:
        """Créer l'embed de gestion économique"""
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"Admin {self.user_id}"
        
        embed = discord.Embed(
            title="🌌 ═══════〔 G E S T I O N   É C O N O M I E 〕═══════ 🌌",
            description=f"```\n◆ Administrateur: {username} ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        try:
            # Statistiques économiques
            cursor = await self.bot.db.db.execute("SELECT SUM(coins), AVG(coins), MAX(coins), MIN(coins) FROM players")
            stats = await cursor.fetchone()
            total_coins, avg_coins, max_coins, min_coins = stats
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players WHERE coins > 0")
            active_players = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            # Top joueurs
            cursor = await self.bot.db.db.execute("""
                SELECT username, coins FROM players 
                ORDER BY coins DESC LIMIT 5
            """)
            top_players = await cursor.fetchall()
            
            embed.add_field(
                name="🌑 ═══〔 Statistiques Économiques 〕═══ 🌑",
                value=(f"```\n"
                       f"Total Shadow Coins: {format_number(total_coins or 0)}\n"
                       f"Moyenne par joueur: {format_number(int(avg_coins or 0))}\n"
                       f"Plus riche: {format_number(max_coins or 0)}\n"
                       f"Plus pauvre: {format_number(min_coins or 0)}\n"
                       f"Joueurs actifs: {active_players}/{total_players}\n"
                       f"```"),
                inline=False
            )
            
            if top_players:
                top_text = ""
                for i, (username, coins) in enumerate(top_players):
                    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    top_text += f"{medal} {username}: {format_number(coins)} SC\n"
                
                embed.add_field(
                    name="🏆 Top 5 Joueurs",
                    value=top_text,
                    inline=True
                )
            
            embed.add_field(
                name="⚡ Actions Disponibles",
                value=("```\n"
                       "🪙 Donner Coins - Ajouter à un joueur\n"
                       "🗑️ Retirer Coins - Retirer d'un joueur\n"
                       "🎁 Distribution - Donner à tous\n"
                       "📊 Rapport - Stats détaillées\n"
                       "🔄 Reset Économie - Tout remettre\n"
                       "```"),
                inline=True
            )
            
        except Exception as e:
            logger.error(f"Erreur lors des stats économiques: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de récupérer les statistiques économiques",
                inline=False
            )
        
        return embed
    
    @discord.ui.button(label="🪙 Donner Coins", style=discord.ButtonStyle.success, row=0)
    async def give_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner des coins à un joueur"""
        modal = GiveCoinsModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Retirer Coins", style=discord.ButtonStyle.danger, row=0)
    async def remove_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retirer des coins d'un joueur"""
        modal = RemoveCoinsModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎁 Distribution", style=discord.ButtonStyle.primary, row=0)
    async def distribute_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Distribuer des coins à tous les joueurs"""
        modal = DistributeCoinsModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Rapport", style=discord.ButtonStyle.secondary, row=0)
    async def economy_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Générer un rapport économique détaillé"""
        await interaction.response.defer()
        
        try:
            # Rapport détaillé
            cursor = await self.bot.db.db.execute("""
                SELECT 
                    COUNT(*) as total_players,
                    SUM(coins) as total_coins,
                    AVG(coins) as avg_coins,
                    COUNT(CASE WHEN coins = 0 THEN 1 END) as broke_players,
                    COUNT(CASE WHEN coins > 10000 THEN 1 END) as rich_players,
                    COUNT(CASE WHEN coins BETWEEN 1000 AND 10000 THEN 1 END) as middle_players
                FROM players
            """)
            stats = await cursor.fetchone()
            
            cursor = await self.bot.db.db.execute("""
                SELECT username, coins FROM players 
                WHERE coins = (SELECT MAX(coins) FROM players)
            """)
            richest = await cursor.fetchone()
            
            report_embed = discord.Embed(
                title="📊 Rapport Économique Détaillé",
                color=BotConfig.RARITY_COLORS['Mythic']
            )
            
            total, total_coins, avg_coins, broke, rich, middle = stats
            
            report_embed.add_field(
                name="Population Économique",
                value=(f"```\n"
                       f"Total joueurs: {total}\n"
                       f"Riches (>10K): {rich}\n"
                       f"Classe moyenne (1K-10K): {middle}\n"
                       f"Pauvres (0): {broke}\n"
                       f"```"),
                inline=True
            )
            
            report_embed.add_field(
                name="Données Monétaires",
                value=(f"```\n"
                       f"Total en circulation: {format_number(total_coins or 0)}\n"
                       f"Moyenne par joueur: {format_number(int(avg_coins or 0))}\n"
                       f"Plus riche: {richest[0] if richest else 'N/A'}\n"
                       f"Fortune max: {format_number(richest[1]) if richest else '0'}\n"
                       f"```"),
                inline=True
            )
            
            # Distribution par tranche
            distribution = [
                (broke, "0 SC", "🔴"),
                (middle, "1K-10K SC", "🟡"),
                (rich, ">10K SC", "🟢")
            ]
            
            dist_text = ""
            for count, range_desc, emoji in distribution:
                percentage = (count / total * 100) if total > 0 else 0
                dist_text += f"{emoji} {range_desc}: {count} ({percentage:.1f}%)\n"
            
            report_embed.add_field(
                name="Distribution de Richesse",
                value=dist_text,
                inline=False
            )
            
            await interaction.followup.send(embed=report_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du rapport économique: {e}")
            await interaction.followup.send("❌ Erreur lors de la génération du rapport", ephemeral=True)
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class GiveCoinsModal(discord.ui.Modal, title='🪙 Donner des Shadow Coins'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='Joueur (ID ou nom)',
        placeholder='ID Discord ou nom du joueur...',
        required=True,
        max_length=100
    )
    
    amount_input = discord.ui.TextInput(
        label='Montant',
        placeholder='Nombre de Shadow Coins à donner...',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            user_identifier = self.user_input.value.strip()
            amount = int(self.amount_input.value.strip())
            
            if amount <= 0:
                await interaction.followup.send("❌ Le montant doit être positif", ephemeral=True)
                return
            
            # Trouver le joueur
            if user_identifier.isdigit():
                user_id = int(user_identifier)
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE user_id = ?", (user_id,)
                )
            else:
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE username LIKE ?", (f"%{user_identifier}%",)
                )
            
            player = await cursor.fetchone()
            if not player:
                await interaction.followup.send("❌ Joueur non trouvé", ephemeral=True)
                return
            
            user_id, username, old_coins = player
            
            # Donner les coins
            await self.parent_view.bot.db.db.execute(
                "UPDATE players SET coins = coins + ? WHERE user_id = ?", (amount, user_id)
            )
            await self.parent_view.bot.db.db.commit()
            
            new_coins = old_coins + amount
            
            await interaction.followup.send(
                f"✅ **{format_number(amount)} Shadow Coins** donnés à **{username}**\n"
                f"Ancien solde: {format_number(old_coins)} SC\n"
                f"Nouveau solde: {format_number(new_coins)} SC",
                ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_economy_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except ValueError:
            await interaction.followup.send("❌ Montant invalide", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur lors du don de coins: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class RemoveCoinsModal(discord.ui.Modal, title='🗑️ Retirer des Shadow Coins'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    user_input = discord.ui.TextInput(
        label='Joueur (ID ou nom)',
        placeholder='ID Discord ou nom du joueur...',
        required=True,
        max_length=100
    )
    
    amount_input = discord.ui.TextInput(
        label='Montant',
        placeholder='Nombre de Shadow Coins à retirer...',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            user_identifier = self.user_input.value.strip()
            amount = int(self.amount_input.value.strip())
            
            if amount <= 0:
                await interaction.followup.send("❌ Le montant doit être positif", ephemeral=True)
                return
            
            # Trouver le joueur
            if user_identifier.isdigit():
                user_id = int(user_identifier)
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE user_id = ?", (user_id,)
                )
            else:
                cursor = await self.parent_view.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE username LIKE ?", (f"%{user_identifier}%",)
                )
            
            player = await cursor.fetchone()
            if not player:
                await interaction.followup.send("❌ Joueur non trouvé", ephemeral=True)
                return
            
            user_id, username, old_coins = player
            
            # Retirer les coins (minimum 0)
            await self.parent_view.bot.db.db.execute(
                "UPDATE players SET coins = MAX(0, coins - ?) WHERE user_id = ?", (amount, user_id)
            )
            await self.parent_view.bot.db.db.commit()
            
            new_coins = max(0, old_coins - amount)
            actually_removed = old_coins - new_coins
            
            await interaction.followup.send(
                f"✅ **{format_number(actually_removed)} Shadow Coins** retirés à **{username}**\n"
                f"Ancien solde: {format_number(old_coins)} SC\n"
                f"Nouveau solde: {format_number(new_coins)} SC",
                ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_economy_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except ValueError:
            await interaction.followup.send("❌ Montant invalide", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur lors du retrait de coins: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class DistributeCoinsModal(discord.ui.Modal, title='🎁 Distribution Globale'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    amount_input = discord.ui.TextInput(
        label='Montant par joueur',
        placeholder='Shadow Coins à donner à TOUS les joueurs...',
        required=True,
        max_length=20
    )
    
    confirm_input = discord.ui.TextInput(
        label='Confirmation (tapez "DISTRIBUER")',
        placeholder='DISTRIBUER',
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            amount = int(self.amount_input.value.strip())
            confirmation = self.confirm_input.value.strip()
            
            if confirmation != "DISTRIBUER":
                await interaction.followup.send("❌ Confirmation incorrecte. Tapez exactement 'DISTRIBUER'", ephemeral=True)
                return
            
            if amount <= 0:
                await interaction.followup.send("❌ Le montant doit être positif", ephemeral=True)
                return
            
            # Compter les joueurs
            cursor = await self.parent_view.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            # Distribuer à tous
            await self.parent_view.bot.db.db.execute(
                "UPDATE players SET coins = coins + ?", (amount,)
            )
            await self.parent_view.bot.db.db.commit()
            
            total_distributed = amount * total_players
            
            await interaction.followup.send(
                f"✅ **Distribution globale réussie!**\n"
                f"🪙 {format_number(amount)} SC donnés à chaque joueur\n"
                f"👥 {total_players} joueurs concernés\n"
                f"📊 Total distribué: {format_number(total_distributed)} SC",
                ephemeral=True
            )
            
            # Actualiser l'affichage
            embed = await self.parent_view.create_economy_embed()
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
            
        except ValueError:
            await interaction.followup.send("❌ Montant invalide", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur lors de la distribution: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


# SeriesManagementView supprimé - utilise maintenant modules/admin_series.py


class SystemManagementView(discord.ui.View):
    """Gestion du système"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_system_embed(self) -> discord.Embed:
        """Créer l'embed de gestion système"""
        embed = discord.Embed(
            title="🌌 ═══════〔 G E S T I O N   S Y S T È M E 〕═══════ 🌌",
            description="```\n◆ Administration système avancée ◆\n```",
            color=BotConfig.RARITY_COLORS['Secret']
        )
        
        embed.add_field(
            name="🔧 Actions Système",
            value=(
                "```\n"
                "🔄 Sync Commands - Synchroniser Discord\n"
                "📊 Database Stats - Statistiques DB\n"
                "🧹 Cleanup - Nettoyage système\n"
                "📋 Bot Info - Informations bot\n"
                "```"
            ),
            inline=False
        )
        
        return embed
    
    @discord.ui.button(label="🔄 Sync Commands", style=discord.ButtonStyle.primary, row=0)
    async def sync_commands(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Synchroniser les commandes slash"""
        await interaction.response.defer()
        try:
            synced = await self.bot.tree.sync()
            await interaction.followup.send(f"✅ {len(synced)} commandes synchronisées avec Discord", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la synchronisation: {e}", ephemeral=True)
    
    @discord.ui.button(label="📊 Database Stats", style=discord.ButtonStyle.secondary, row=0)
    async def database_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Statistiques de la base de données"""
        await interaction.response.defer()
        try:
            stats_embed = discord.Embed(title="📊 Statistiques Base de Données", color=0x00ff00)
            
            # Tables principales
            tables = ['players', 'characters', 'inventory', 'achievements', 'series']
            for table in tables:
                cursor = await self.bot.db.db.execute(f"SELECT COUNT(*) FROM {table}")
                count = (await cursor.fetchone())[0]
                stats_embed.add_field(name=table.title(), value=f"{count} entrées", inline=True)
            
            await interaction.followup.send(embed=stats_embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}", ephemeral=True)
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class StatsManagementView(discord.ui.View):
    """Gestion des statistiques"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_stats_embed(self) -> discord.Embed:
        """Créer l'embed de statistiques"""
        embed = discord.Embed(
            title="🌌 ═══════〔 S T A T I S T I Q U E S   D É T A I L L É E S 〕═══════ 🌌",
            description="```\n◆ Rapports et analyses avancées ◆\n```",
            color=BotConfig.RARITY_COLORS['Mythic']
        )
        
        try:
            # Statistiques globales
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT SUM(total_rerolls) FROM players")
            total_rolls = (await cursor.fetchone())[0] or 0
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(DISTINCT character_id) FROM inventory")
            unique_collected = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            total_characters = (await cursor.fetchone())[0]
            
            embed.add_field(
                name="📊 Activité Globale",
                value=(
                    f"```\n"
                    f"Joueurs Total: {total_players}\n"
                    f"Invocations Total: {format_number(total_rolls)}\n"
                    f"Personnages Collectés: {unique_collected}/{total_characters}\n"
                    f"Taux Collection: {(unique_collected/total_characters*100):.1f}%\n"
                    f"```"
                ),
                inline=False
            )
            
        except Exception as e:
            embed.add_field(name="❌ Erreur", value="Impossible de charger les statistiques", inline=False)
        
        return embed
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=0)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class QuickActionsView(discord.ui.View):
    """Actions rapides pour les admins"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id and BotConfig.is_admin(interaction.user.id)
    
    async def create_quick_actions_embed(self) -> discord.Embed:
        """Créer l'embed d'actions rapides"""
        embed = discord.Embed(
            title="🌌 ═══════〔 A C T I O N S   R A P I D E S 〕═══════ 🌌",
            description="```\n◆ Outils d'administration express ◆\n```",
            color=BotConfig.RARITY_COLORS['Fusion']
        )
        
        embed.add_field(
            name="🚀 Actions Disponibles",
            value=(
                "```\n"
                "⚡ Action Express - Commande rapide\n"
                "🔍 Recherche - Trouver joueur/personnage\n"
                "🛠️ Réparation - Fix problèmes courants\n"
                "📋 Logs - Voir activité récente\n"
                "```"
            ),
            inline=False
        )
        
        return embed
    
    @discord.ui.button(label="⚡ Action Express", style=discord.ButtonStyle.primary, row=0)
    async def express_action(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Action express avec modal"""
        modal = ExpressActionModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔍 Recherche Globale", style=discord.ButtonStyle.secondary, row=0)
    async def global_search(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Recherche globale"""
        modal = GlobalSearchModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Admin", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au panneau admin"""
        await interaction.response.defer()
        view = ShadowAdminView(self.bot, self.user_id)
        embed = await view.create_main_admin_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class ExpressActionModal(discord.ui.Modal, title='⚡ Action Express'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    command_input = discord.ui.TextInput(
        label='Commande',
        placeholder='givecoins user 1000, ban user, createchar name...',
        required=True,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        command = self.command_input.value.strip().lower()
        parts = command.split()
        
        try:
            if not parts:
                await interaction.followup.send("❌ Commande vide", ephemeral=True)
                return
            
            action = parts[0]
            
            if action == "givecoins" and len(parts) >= 3:
                user_id = parts[1]
                amount = int(parts[2])
                
                cursor = await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET coins = coins + ? WHERE user_id = ? OR username LIKE ?",
                    (amount, user_id if user_id.isdigit() else 0, f"%{user_id}%")
                )
                await self.parent_view.bot.db.db.commit()
                
                await interaction.followup.send(f"✅ {amount} coins donnés à {user_id}", ephemeral=True)
                
            elif action == "ban" and len(parts) >= 2:
                user_id = parts[1]
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET is_banned = TRUE WHERE user_id = ? OR username LIKE ?",
                    (user_id if user_id.isdigit() else 0, f"%{user_id}%")
                )
                await self.parent_view.bot.db.db.commit()
                
                await interaction.followup.send(f"✅ Utilisateur {user_id} banni", ephemeral=True)
                
            elif action == "unban" and len(parts) >= 2:
                user_id = parts[1]
                await self.parent_view.bot.db.db.execute(
                    "UPDATE players SET is_banned = FALSE WHERE user_id = ? OR username LIKE ?",
                    (user_id if user_id.isdigit() else 0, f"%{user_id}%")
                )
                await self.parent_view.bot.db.db.commit()
                
                await interaction.followup.send(f"✅ Utilisateur {user_id} débanni", ephemeral=True)
                
            else:
                await interaction.followup.send(
                    "❌ Commande non reconnue. Utilisez:\n"
                    "• `givecoins user amount`\n"
                    "• `ban user`\n"
                    "• `unban user`",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class GlobalSearchModal(discord.ui.Modal, title='🔍 Recherche Globale'):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    search_input = discord.ui.TextInput(
        label='Terme de recherche',
        placeholder='Nom utilisateur, personnage, ID...',
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        search_term = self.search_input.value.strip()
        
        try:
            results_embed = discord.Embed(
                title=f"🔍 Résultats pour: {search_term}",
                color=0x0099ff
            )
            
            # Recherche dans les joueurs
            cursor = await self.parent_view.bot.db.db.execute(
                "SELECT user_id, username, coins FROM players WHERE username LIKE ? OR user_id = ? LIMIT 5",
                (f"%{search_term}%", search_term if search_term.isdigit() else 0)
            )
            players = await cursor.fetchall()
            
            if players:
                player_text = ""
                for user_id, username, coins in players:
                    player_text += f"• {username} ({user_id}) - {format_number(coins)} SC\n"
                results_embed.add_field(name="👥 Joueurs", value=player_text, inline=False)
            
            # Recherche dans les personnages
            cursor = await self.parent_view.bot.db.db.execute(
                "SELECT name, anime, rarity FROM characters WHERE name LIKE ? OR anime LIKE ? LIMIT 5",
                (f"%{search_term}%", f"%{search_term}%")
            )
            characters = await cursor.fetchall()
            
            if characters:
                char_text = ""
                for name, anime, rarity in characters:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                    char_text += f"• {emoji} {name} ({anime})\n"
                results_embed.add_field(name="🎴 Personnages", value=char_text, inline=False)
            
            if not players and not characters:
                results_embed.add_field(name="❌ Aucun résultat", value="Aucune correspondance trouvée", inline=False)
            
            await interaction.followup.send(embed=results_embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la recherche: {str(e)}", ephemeral=True)


async def setup_new_admin_system(bot):
    """Configurer le nouveau système d'administration"""
    
    @bot.command(name='admin')
    async def admin_command(ctx):
        """Ouvrir le panneau d'administration Shadow Roll"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé - Vous n'êtes pas administrateur")
            return
        
        try:
            view = ShadowAdminView(bot, ctx.author.id)
            embed = await view.create_main_admin_embed()
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Erreur dans la commande admin: {e}")
            await ctx.send("❌ Erreur lors de l'ouverture du panneau admin")
    
    # Commandes rapides pour compatibilité
    @bot.command(name='givecoins')
    async def give_coins_cmd(ctx, user: Optional[discord.Member] = None, amount: Optional[int] = None):
        """Donner des coins à un utilisateur"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé")
            return
        
        if user is None or amount is None:
            await ctx.send("❌ Usage: !givecoins @user amount")
            return
        
        try:
            player = await bot.db.get_or_create_player(user.id, get_display_name(user))
            await bot.db.db.execute(
                "UPDATE players SET coins = coins + ? WHERE user_id = ?", (amount, user.id)
            )
            await bot.db.db.commit()
            
            await ctx.send(f"✅ {format_number(amount)} Shadow Coins donnés à {user.mention}")
            
        except Exception as e:
            logger.error(f"Erreur give coins: {e}")
            await ctx.send("❌ Erreur lors du don de coins")
    
    @bot.command(name='banuser')
    async def ban_user_cmd(ctx, user: discord.Member = None):
        """Bannir un utilisateur"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé")
            return
        
        if not user:
            await ctx.send("❌ Usage: !banuser @user")
            return
        
        try:
            await bot.db.db.execute(
                "UPDATE players SET is_banned = TRUE WHERE user_id = ?", (user.id,)
            )
            await bot.db.db.commit()
            
            await ctx.send(f"✅ {user.mention} a été banni du bot")
            
        except Exception as e:
            logger.error(f"Erreur ban user: {e}")
            await ctx.send("❌ Erreur lors du bannissement")
    
    @bot.command(name='unbanuser')
    async def unban_user_cmd(ctx, user: discord.Member = None):
        """Débannir un utilisateur"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé")
            return
        
        if not user:
            await ctx.send("❌ Usage: !unbanuser @user")
            return
        
        try:
            await bot.db.db.execute(
                "UPDATE players SET is_banned = FALSE WHERE user_id = ?", (user.id,)
            )
            await bot.db.db.commit()
            
            await ctx.send(f"✅ {user.mention} a été débanni du bot")
            
        except Exception as e:
            logger.error(f"Erreur unban user: {e}")
            await ctx.send("❌ Erreur lors du débannissement")
    
    @bot.command(name='createchar')
    async def create_char_cmd(ctx, name: str = None, rarity: str = None, anime: str = None, value: int = None, *, image_url: str = None):
        """Créer un nouveau personnage"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé")
            return
        
        if not all([name, rarity, anime, value]):
            await ctx.send("❌ Usage: !createchar nom rareté anime valeur [url_image]")
            return
        
        if rarity not in BotConfig.RARITY_WEIGHTS:
            await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
            return
        
        try:
            # Vérifier si existe déjà
            cursor = await bot.db.db.execute(
                "SELECT COUNT(*) FROM characters WHERE name = ? AND anime = ?", (name, anime)
            )
            if (await cursor.fetchone())[0] > 0:
                await ctx.send(f"❌ Le personnage {name} de {anime} existe déjà")
                return
            
            # Créer le personnage
            await bot.db.db.execute("""
                INSERT INTO characters (name, anime, rarity, value, image_url)
                VALUES (?, ?, ?, ?, ?)
            """, (name, anime, rarity, value, image_url))
            
            await bot.db.db.commit()
            
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
            await ctx.send(
                f"✅ Personnage créé avec succès!\n"
                f"{rarity_emoji} **{name}** ({anime})\n"
                f"💎 {rarity} | 🪙 {format_number(value)} SC"
            )
            
        except Exception as e:
            logger.error(f"Erreur create char: {e}")
            await ctx.send("❌ Erreur lors de la création du personnage")
    
    @bot.command(name='synccommands')
    async def sync_commands_cmd(ctx):
        """Synchroniser les commandes slash"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Accès refusé")
            return
        
        try:
            synced = await bot.tree.sync()
            await ctx.send(f"✅ {len(synced)} commandes slash synchronisées avec Discord")
            
        except Exception as e:
            logger.error(f"Erreur sync commands: {e}")
            await ctx.send("❌ Erreur lors de la synchronisation")
    
    logger.info("Nouveau système d'administration configuré")