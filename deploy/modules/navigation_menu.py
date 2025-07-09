"""
Shadow Roll Bot - Navigation Menu Style Fortnite
Système de navigation horizontale avec flèches
"""

import discord
import asyncio
from typing import Dict, List, Optional
from core.config import BotConfig
from modules.utils import format_number, get_display_name
import logging

logger = logging.getLogger(__name__)

class NavigationMenuView(discord.ui.View):
    """Menu de navigation horizontal style Fortnite"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        
        # Définir toutes les pages du menu
        self.pages = [
            {
                "name": "🏠 Accueil",
                "description": "Menu principal Shadow Roll",
                "buttons": [
                    {"label": "👤 Profil", "action": "profile"},
                    {"label": "🎲 Invocation", "action": "summon"},
                    {"label": "🎁 Bénédiction", "action": "daily"},
                    {"label": "❓ Guide", "action": "guide"}
                ]
            },
            {
                "name": "🎲 Invocation",
                "description": "Invoquer des personnages",
                "buttons": [
                    {"label": "🎲 Invocation Simple", "action": "single_summon"},
                    {"label": "🎲 Invocation x10", "action": "multi_summon"},
                    {"label": "🍀 Avec Potion", "action": "potion_summon"},
                    {"label": "💎 Invocation Premium", "action": "premium_summon"}
                ]
            },
            {
                "name": "🧪 Recherche",
                "description": "Traquer un personnage spécifique",
                "buttons": [
                    {"label": "🔍 Rechercher", "action": "search_character"},
                    {"label": "🎯 Mes Hunts", "action": "my_hunts"},
                    {"label": "📊 Progression", "action": "hunt_progress"},
                    {"label": "⭐ Hunt Premium", "action": "premium_hunt"}
                ]
            },
            {
                "name": "🎒 Collection",
                "description": "Voir vos personnages",
                "buttons": [
                    {"label": "👥 Mes Personnages", "action": "inventory"},
                    {"label": "🏆 Séries", "action": "series"},
                    {"label": "⚡ Équipement", "action": "equipment"},
                    {"label": "📈 Statistiques", "action": "stats"}
                ]
            },
            {
                "name": "🔮 Craft",
                "description": "Évolution des personnages",
                "buttons": [
                    {"label": "🔮 Craft Simple", "action": "craft"},
                    {"label": "⚡ Craft Premium", "action": "premium_craft"},
                    {"label": "📋 Recettes", "action": "recipes"},
                    {"label": "🎯 Craft Automatique", "action": "auto_craft"}
                ]
            },
            {
                "name": "🔄 Trade",
                "description": "Échanger avec d'autres joueurs",
                "buttons": [
                    {"label": "🔄 Nouveau Trade", "action": "new_trade"},
                    {"label": "📋 Mes Trades", "action": "my_trades"},
                    {"label": "🏪 Marketplace", "action": "marketplace"},
                    {"label": "📊 Historique", "action": "trade_history"}
                ]
            },
            {
                "name": "🛒 Boutique",
                "description": "Articles premium rotatifs",
                "buttons": [
                    {"label": "✨ Featured", "action": "featured_shop"},
                    {"label": "🗓️ Daily", "action": "daily_shop"},
                    {"label": "🎁 Packs", "action": "packs_shop"},
                    {"label": "🔄 Rotation", "action": "force_rotation"}
                ]
            },
            {
                "name": "🪙 Vendre",
                "description": "Revendre vos personnages",
                "buttons": [
                    {"label": "🪙 Vente Rapide", "action": "quick_sell"},
                    {"label": "💎 Vente Premium", "action": "premium_sell"},
                    {"label": "📊 Valeurs", "action": "market_values"},
                    {"label": "🔄 Vente Multiple", "action": "bulk_sell"}
                ]
            },
            {
                "name": "🎯 Succès",
                "description": "Récompenses d'exploits",
                "buttons": [
                    {"label": "🏆 Mes Succès", "action": "achievements"},
                    {"label": "📈 Progression", "action": "achievement_progress"},
                    {"label": "🪙 Récompenses", "action": "claim_rewards"},
                    {"label": "🎖️ Badges", "action": "badges"}
                ]
            },
            {
                "name": "🏆 Classement",
                "description": "Tableau des maîtres",
                "buttons": [
                    {"label": "👑 Top Global", "action": "global_leaderboard"},
                    {"label": "🎯 Top Mensuel", "action": "monthly_leaderboard"},
                    {"label": "⚡ Top Équipement", "action": "equipment_leaderboard"},
                    {"label": "📊 Mes Rangs", "action": "my_ranks"}
                ]
            },
            {
                "name": "👑 Titres",
                "description": "Titres personnalisés",
                "buttons": [
                    {"label": "👑 Mes Titres", "action": "my_titles"},
                    {"label": "🔓 Débloquer", "action": "unlock_titles"},
                    {"label": "⚡ Bonus", "action": "title_bonuses"},
                    {"label": "🎨 Personnaliser", "action": "customize_titles"}
                ]
            }
        ]
        
        self.update_buttons()
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    def update_buttons(self):
        """Mettre à jour les boutons selon la page actuelle"""
        self.clear_items()
        
        # Première ligne : Navigation avec flèches
        # Flèche gauche
        if self.current_page > 0:
            left_arrow = discord.ui.Button(
                label="◀️",
                style=discord.ButtonStyle.secondary,
                row=0,
                custom_id="nav_left"
            )
            left_arrow.callback = self.nav_left
            self.add_item(left_arrow)
        
        # Indicateur de page actuelle
        current_page_btn = discord.ui.Button(
            label=f"{self.pages[self.current_page]['name']} ({self.current_page + 1}/{len(self.pages)})",
            style=discord.ButtonStyle.primary,
            row=0,
            disabled=True
        )
        self.add_item(current_page_btn)
        
        # Flèche droite
        if self.current_page < len(self.pages) - 1:
            right_arrow = discord.ui.Button(
                label="▶️",
                style=discord.ButtonStyle.secondary,
                row=0,
                custom_id="nav_right"
            )
            right_arrow.callback = self.nav_right
            self.add_item(right_arrow)
        
        # Boutons de la page actuelle (lignes 2 et 3) - Couleurs drapeau français pour les 3 premiers
        current_page_data = self.pages[self.current_page]
        for i, button_data in enumerate(current_page_data["buttons"]):
            row = 1 if i < 2 else 2  # 2 boutons par ligne
            
            # Appliquer les couleurs du drapeau français pour les 3 premières pages
            if self.current_page == 0 and button_data["action"] == "profile":  # Profil - Bleu
                button_style = discord.ButtonStyle.primary
            elif self.current_page == 1 and button_data["action"] in ["single_summon", "multi_summon"]:  # Invocation - Blanc
                button_style = discord.ButtonStyle.secondary
            elif self.current_page == 2:  # Recherche - Rouge
                button_style = discord.ButtonStyle.danger
            else:
                # Style par défaut pour les autres boutons
                button_style = discord.ButtonStyle.success if button_data["action"] in ["summon", "single_summon"] else discord.ButtonStyle.secondary
            
            btn = discord.ui.Button(
                label=button_data["label"],
                style=button_style,
                row=row,
                custom_id=button_data["action"]
            )
            
            # Assigner le callback dynamiquement
            btn.callback = self.create_button_callback(button_data["action"])
            self.add_item(btn)
        
        # Bouton retour à l'accueil (toujours visible)
        if self.current_page != 0:
            home_btn = discord.ui.Button(
                label="🏠 Accueil",
                style=discord.ButtonStyle.primary,
                row=2,
                custom_id="home"
            )
            home_btn.callback = self.go_home
            self.add_item(home_btn)
    
    def create_button_callback(self, action: str):
        """Créer un callback dynamique pour chaque bouton"""
        async def button_callback(interaction: discord.Interaction):
            await self.handle_action(interaction, action)
        return button_callback
    
    async def nav_left(self, interaction: discord.Interaction):
        """Navigation vers la gauche"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.defer()
            embed = await self.create_navigation_embed()
            await interaction.edit_original_response(embed=embed, view=self)
    
    async def nav_right(self, interaction: discord.Interaction):
        """Navigation vers la droite"""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.defer()
            embed = await self.create_navigation_embed()
            await interaction.edit_original_response(embed=embed, view=self)
    
    async def go_home(self, interaction: discord.Interaction):
        """Retour à l'accueil"""
        self.current_page = 0
        self.update_buttons()
        await interaction.response.defer()
        embed = await self.create_navigation_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    async def handle_action(self, interaction: discord.Interaction, action: str):
        """Gérer les actions des boutons"""
        await interaction.response.defer()
        
        # Utiliser l'ancien menu pour toutes les actions (pour l'instant)
        from modules.menu import ShadowMenuView, create_main_menu_embed
        
        # Actions spécifiques qui redirigent directement
        if action == "profile":
            from modules.menu import ProfileView
            view = ProfileView(self.bot, self.user_id)
            embed = await view.create_profile_embed()
            await interaction.edit_original_response(embed=embed, view=view)
            
        elif action in ["summon", "single_summon"]:
            # Rediriger vers le menu classique puis vers invocation
            view = ShadowMenuView(self.bot, self.user_id)
            embed = await create_main_menu_embed(self.bot, self.user_id)
            await interaction.edit_original_response(embed=embed, view=view)
            await interaction.followup.send("✅ Cliquez sur 🎲 Invocation dans le menu ci-dessous", ephemeral=True)
            
        elif action == "daily":
            from modules.menu import DailyView
            view = DailyView(self.bot, self.user_id)
            embed = await view.claim_daily_reward()
            await interaction.edit_original_response(embed=embed, view=view)
            
        elif action == "guide":
            from modules.guide import GuideView
            view = GuideView(self.bot, self.user_id)
            embed = await view.create_guide_embed()
            await interaction.edit_original_response(embed=embed, view=view)
            
        else:
            # Pour toutes les autres actions, revenir au menu Shadow Roll classique
            view = ShadowMenuView(self.bot, self.user_id)
            embed = await create_main_menu_embed(self.bot, self.user_id)
            await interaction.edit_original_response(embed=embed, view=view)
            
            # Informer l'utilisateur de l'action demandée
            action_names = {
                "search_character": "🧪 Recherche",
                "inventory": "🎒 Collection",
                "craft": "🔮 Craft",
                "new_trade": "🔄 Trade",
                "featured_shop": "🛒 Boutique",
                "daily_shop": "🛒 Boutique",
                "quick_sell": "🪙 Vendre",
                "achievements": "🎯 Succès",
                "global_leaderboard": "🏆 Classement",
                "my_titles": "👑 Titres"
            }
            
            action_name = action_names.get(action, action)
            await interaction.followup.send(f"✅ Cliquez sur {action_name} dans le menu ci-dessous", ephemeral=True)
    
    async def create_navigation_embed(self) -> discord.Embed:
        """Créer l'embed de navigation"""
        try:
            player = await self.bot.db.get_or_create_player(self.user_id, f"User_{self.user_id}")
            username = get_display_name(player)
            
            current_page_data = self.pages[self.current_page]
            
            embed = discord.Embed(
                title=f"{current_page_data['name']} ═══════════════════════",
                description=f"```\n◆ {username} - {format_number(player.coins)} SC ◆\n{current_page_data['description']}\n```",
                color=BotConfig.RARITY_COLORS['Epic']
            )
            
            # Ajouter les options disponibles
            options_text = ""
            for i, button_data in enumerate(current_page_data["buttons"], 1):
                options_text += f"{button_data['label']}\n"
            
            embed.add_field(
                name="🎯 ═══〔 Options Disponibles 〕═══ 🎯",
                value=f"```\n{options_text}```",
                inline=False
            )
            
            # Navigation info
            embed.add_field(
                name="🧭 Navigation",
                value=f"```\n◀️ Précédent  |  Page {self.current_page + 1}/{len(self.pages)}  |  Suivant ▶️\n```",
                inline=False
            )
            
            embed.set_footer(
                text=f"Shadow Roll • Navigation Style Fortnite",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating navigation embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de créer le menu de navigation",
                color=0xff0000
            )


async def create_navigation_menu_embed(bot, user_id: int) -> discord.Embed:
    """Créer l'embed du menu de navigation principal"""
    try:
        player = await bot.db.get_or_create_player(user_id, f"User_{user_id}")
        username = get_display_name(player)
        
        embed = discord.Embed(
            title="🏠 Accueil ═══════════════════════",
            description=f"```\n◆ Bienvenue {username} - {format_number(player.coins)} SC ◆\nMenu principal Shadow Roll\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        embed.add_field(
            name="🎯 ═══〔 Options Disponibles 〕═══ 🎯",
            value="```\n👤 Profil\n🎲 Invocation\n🎁 Bénédiction\n❓ Guide\n```",
            inline=False
        )
        
        embed.add_field(
            name="🧭 Navigation",
            value="```\n◀️ Précédent  |  Page 1/11  |  Suivant ▶️\n```",
            inline=False
        )
        
        embed.set_footer(
            text="Shadow Roll • Navigation Style Fortnite",
            icon_url=bot.user.avatar.url if bot.user.avatar else None
        )
        
        return embed
        
    except Exception as e:
        logger.error(f"Error creating navigation menu embed: {e}")
        return discord.Embed(
            title="❌ Erreur",
            description="Impossible de créer le menu principal",
            color=0xff0000
        )