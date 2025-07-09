"""
Système d'Administration Complet pour Shadow Roll Bot
Interface moderne avec toutes les commandes admin
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any
import asyncio
import json
from datetime import datetime, timedelta

from core.config import BotConfig
from modules.utils import format_number, get_display_name

logger = logging.getLogger(__name__)

class AdminCompleteView(discord.ui.View):
    """Interface admin complète avec navigation avancée"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.items_per_page = 8
        self.mode = "main"  # main, players, characters, economy, system, logs
        self.selected_player = None
        self.selected_character = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    # ═══════════════════ BOUTONS PRINCIPAUX ═══════════════════
    
    @discord.ui.button(label="👥 Joueurs", style=discord.ButtonStyle.primary, row=0)
    async def players_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des joueurs"""
        self.mode = "players"
        self.current_page = 0
        embed = await self.create_players_embed()
        view = PlayerManagementView(self.bot, self.user_id, self)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🎴 Personnages", style=discord.ButtonStyle.secondary, row=0)
    async def characters_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des personnages"""
        self.mode = "characters"
        self.current_page = 0
        embed = await self.create_characters_embed()
        view = CharacterManagementView(self.bot, self.user_id, self)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🎖️ Séries", style=discord.ButtonStyle.success, row=0)
    async def series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion des séries"""
        await interaction.response.defer()
        from modules.admin_series import SeriesManagementView
        view = SeriesManagementView(self.bot, self.user_id)
        embed = await view.create_main_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label="🪙 Économie", style=discord.ButtonStyle.success, row=0)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion économique"""
        await interaction.response.send_message(
            "💡 **Gestion Économique:**\n"
            "• `!givecoins [user] [amount]` - Donner des pièces\n"
            "• `!removecoins [user] [amount]` - Retirer des pièces\n"
            "• `!setcoins [user] [amount]` - Définir montant exact\n"
            "• `!economystats` - Statistiques économiques\n"
            "• `!resetdaily [user]` - Reset cooldown daily",
            ephemeral=True
        )
    
    @discord.ui.button(label="🔧 Système", style=discord.ButtonStyle.danger, row=1)
    async def system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Administration système"""
        await interaction.response.send_message(
            "💡 **Administration Système:**\n"
            "• `!synccommands` - Synchroniser commandes slash\n"
            "• `!restart` - Redémarrer le bot (si configuré)\n"
            "• `!backup` - Sauvegarder la base de données\n"
            "• `!logs` - Voir les logs récents\n"
            "• `!maintenance [on/off]` - Mode maintenance",
            ephemeral=True
        )
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, ProfileView
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await ProfileView(self.bot, self.user_id).create_main_menu_embed()
        await interaction.edit_original_response(embed=embed, view=view)
    
    # ═══════════════════ EMBEDS PRINCIPAUX ═══════════════════
    
    async def create_main_embed(self) -> discord.Embed:
        """Créer l'embed principal d'administration"""
        embed = discord.Embed(
            title="🔧 ═══════〔 A D M I N I S T R A T I O N 〕═══════ 🔧",
            description="```\n◆ Panneau de Contrôle Shadow Roll ◆\n```",
            color=BotConfig.RARITY_COLORS['Mythic']
        )
        
        embed.add_field(
            name="👥 ═══〔 Gestion Joueurs 〕═══ 👥",
            value=("```\n"
                   "• Voir la liste des joueurs\n"
                   "• Bannir/débannir des utilisateurs\n"
                   "• Gérer les coins et statistiques\n"
                   "• Modérer les comptes\n"
                   "```"),
            inline=True
        )
        
        embed.add_field(
            name="🎴 ═══〔 Gestion Personnages 〕═══ 🎴",
            value=("```\n"
                   "• Créer de nouveaux personnages\n"
                   "• Modifier les caractéristiques\n"
                   "• Gérer les images\n"
                   "• Ajuster les raretés\n"
                   "```"),
            inline=True
        )
        
        embed.add_field(
            name="🎖️ ═══〔 Gestion Séries 〕═══ 🎖️",
            value=("```\n"
                   "• Créer nouvelles séries d'anime\n"
                   "• Assigner personnages aux séries\n"
                   "• Modifier bonus de collections\n"
                   "• Renommer/supprimer séries\n"
                   "```"),
            inline=True
        )
        
        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Administration Complète")
        return embed
    
    async def create_characters_embed(self) -> discord.Embed:
        """Créer l'embed de gestion des personnages"""
        embed = discord.Embed(
            title="🎴 ═══════〔 G E S T I O N   P E R S O N N A G E S 〕═══════ 🎴",
            description="```\n◆ Administration des Personnages ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        try:
            # Stats des personnages
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            total_chars = (await cursor.fetchone())[0]
            
            # Stats par rareté
            cursor = await self.bot.db.db.execute("""
                SELECT rarity, COUNT(*) FROM characters 
                GROUP BY rarity 
                ORDER BY 
                    CASE rarity
                        WHEN 'Secret' THEN 8
                        WHEN 'Fusion' THEN 7
                        WHEN 'Titan' THEN 6
                        WHEN 'Mythic' THEN 5
                        WHEN 'Legendary' THEN 4
                        WHEN 'Epic' THEN 3
                        WHEN 'Rare' THEN 2
                        WHEN 'Common' THEN 1
                    END DESC
            """)
            rarity_stats = await cursor.fetchall()
            
            embed.add_field(
                name="📊 ═══〔 Statistiques 〕═══ 📊",
                value=f"```\nTotal: {total_chars} personnages\n```",
                inline=False
            )
            
            # Afficher les raretés
            if rarity_stats:
                rarity_text = ""
                for rarity, count in rarity_stats:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    rarity_text += f"{emoji} {rarity}: {count}\n"
                
                embed.add_field(
                    name="🎯 Répartition par Rareté",
                    value=f"```{rarity_text}```",
                    inline=True
                )
            
            # Stats par série
            cursor = await self.bot.db.db.execute("""
                SELECT anime, COUNT(*) FROM characters 
                WHERE anime IS NOT NULL 
                GROUP BY anime 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            """)
            series_stats = await cursor.fetchall()
            
            if series_stats:
                series_text = ""
                for anime, count in series_stats:
                    series_text += f"• {anime}: {count}\n"
                
                embed.add_field(
                    name="🎭 Top 5 Séries",
                    value=f"```{series_text}```",
                    inline=True
                )
            
            embed.add_field(
                name="🛠️ ═══〔 Actions Disponibles 〕═══ 🛠️",
                value=("```\n"
                       "🆕 Créer - Nouveau personnage\n"
                       "📝 Modifier - Éditer personnage\n"
                       "🖼️ Images - Gérer les images\n"
                       "🔍 Rechercher - Trouver personnage\n"
                       "📋 Lister - Voir tous les personnages\n"
                       "🗑️ Supprimer - Retirer personnage\n"
                       "```"),
                inline=False
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur création embed personnages: {e}")
            embed.add_field(
                name="❌ Erreur",
                value=f"```{str(e)}```",
                inline=False
            )
            return embed
    
    async def create_players_embed(self) -> discord.Embed:
        """Créer l'embed de gestion des joueurs"""
        embed = discord.Embed(
            title="👥 ═══════〔 G E S T I O N   J O U E U R S 〕═══════ 👥",
            description="```\n◆ Administration des Joueurs ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        try:
            # Stats des joueurs
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute("SELECT SUM(coins) FROM players")
            total_coins = (await cursor.fetchone())[0] or 0
            
            embed.add_field(
                name="📊 ═══〔 Statistiques 〕═══ 📊",
                value=f"```\nTotal Joueurs: {total_players}\nÉconomie Totale: {format_number(total_coins)} SC\n```",
                inline=False
            )
            
            # Top joueurs
            cursor = await self.bot.db.db.execute("""
                SELECT username, coins FROM players 
                ORDER BY coins DESC 
                LIMIT 5
            """)
            top_players = await cursor.fetchall()
            
            if top_players:
                top_text = ""
                for i, (username, coins) in enumerate(top_players, 1):
                    top_text += f"{i}. {username}: {format_number(coins)} SC\n"
                
                embed.add_field(
                    name="🏆 Top 5 Joueurs",
                    value=f"```{top_text}```",
                    inline=True
                )
            
            embed.add_field(
                name="🛠️ ═══〔 Actions Disponibles 〕═══ 🛠️",
                value=("```\n"
                       "👥 Lister - Voir tous les joueurs\n"
                       "🔍 Rechercher - Trouver un joueur\n"
                       "🪙 Coins - Gérer l'économie\n"
                       "🚫 Bannir - Modérer un compte\n"
                       "📊 Stats - Statistiques détaillées\n"
                       "```"),
                inline=False
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur création embed joueurs: {e}")
            embed.add_field(
                name="❌ Erreur",
                value=f"```{str(e)}```",
                inline=False
            )
            return embed


class CharacterManagementView(discord.ui.View):
    """Vue de gestion des personnages"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        self.current_page = 0
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    @discord.ui.button(label="🆕 Créer", style=discord.ButtonStyle.success, row=0)
    async def create_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un nouveau personnage"""
        modal = CreateCharacterModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📝 Modifier", style=discord.ButtonStyle.primary, row=0)
    async def edit_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modifier un personnage existant"""
        await interaction.response.send_message(
            "💡 **Modification de Personnage:**\n"
            "Utilisez les commandes legacy pour modifier:\n"
            "• `!editchar [ID] name [nouveau_nom]`\n"
            "• `!editchar [ID] rarity [nouvelle_rareté]`\n"
            "• `!editchar [ID] value [nouvelle_valeur]`\n"
            "• `!editchar [ID] anime [nouvelle_série]`",
            ephemeral=True
        )
    
    @discord.ui.button(label="🖼️ Images", style=discord.ButtonStyle.secondary, row=0)
    async def manage_images_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gérer les images des personnages"""
        await interaction.response.send_message(
            "💡 **Gestion des Images:**\n"
            "• Utilisez `!addimage [nom]` pour ajouter une image\n"
            "• Utilisez `!suggest` pour l'interface interactive\n"
            "• Utilisez `!searchimage [nom]` pour rechercher automatiquement",
            ephemeral=True
        )
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.secondary, row=1)
    async def search_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un personnage"""
        modal = SearchCharacterModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Lister", style=discord.ButtonStyle.secondary, row=1)
    async def list_characters_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Lister tous les personnages"""
        embed = await self.create_character_list_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Retour Admin", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu admin"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
    
    async def create_character_list_embed(self) -> discord.Embed:
        """Créer l'embed de liste des personnages"""
        embed = discord.Embed(
            title="📋 ═══════〔 L I S T E   P E R S O N N A G E S 〕═══════ 📋",
            description="```\n◆ Tous les personnages du jeu ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        try:
            # Récupérer les personnages par page
            offset = self.current_page * 15
            cursor = await self.bot.db.db.execute("""
                SELECT id, name, anime, rarity, value FROM characters 
                ORDER BY 
                    CASE rarity
                        WHEN 'Secret' THEN 8
                        WHEN 'Fusion' THEN 7
                        WHEN 'Titan' THEN 6
                        WHEN 'Mythic' THEN 5
                        WHEN 'Legendary' THEN 4
                        WHEN 'Epic' THEN 3
                        WHEN 'Rare' THEN 2
                        WHEN 'Common' THEN 1
                    END DESC, name
                LIMIT 15 OFFSET ?
            """, (offset,))
            
            characters = await cursor.fetchall()
            
            if characters:
                char_list = ""
                for char_id, name, anime, rarity, value in characters:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    series = anime if anime else "Aucune"
                    char_list += f"{emoji} {char_id:3d}. {name} ({series}) - {value:,} SC\n"
                
                embed.add_field(
                    name=f"🎴 Page {self.current_page + 1}",
                    value=f"```{char_list}```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ Information",
                    value="```Aucun personnage sur cette page```",
                    inline=False
                )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur liste personnages: {e}")
            embed.add_field(name="❌ Erreur", value=f"```{str(e)}```", inline=False)
            return embed


class CreateCharacterModal(discord.ui.Modal, title="🆕 Créer Nouveau Personnage"):
    """Modal pour créer un nouveau personnage"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    name = discord.ui.TextInput(
        label="Nom du Personnage",
        placeholder="Ex: Goku",
        required=True,
        max_length=50
    )
    
    anime = discord.ui.TextInput(
        label="Série Anime",
        placeholder="Ex: Dragon Ball Z",
        required=True,
        max_length=50
    )
    
    rarity = discord.ui.TextInput(
        label="Rareté",
        placeholder="Common/Rare/Epic/Legendary/Mythic/Titan/Fusion/Secret",
        required=True,
        max_length=20
    )
    
    value = discord.ui.TextInput(
        label="Valeur (Shadow Coins)",
        placeholder="Ex: 1000",
        required=True,
        max_length=10
    )
    
    image_url = discord.ui.TextInput(
        label="URL Image (optionnel)",
        placeholder="https://...",
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            name = self.name.value.strip()
            anime = self.anime.value.strip()
            rarity = self.rarity.value.strip()
            value = int(self.value.value.strip())
            image_url = self.image_url.value.strip() if self.image_url.value else None
            
            # Validation de la rareté
            valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']
            if rarity not in valid_rarities:
                await interaction.response.send_message(
                    f"❌ Rareté invalide. Utilisez: {', '.join(valid_rarities)}",
                    ephemeral=True
                )
                return
            
            # Vérifier si le personnage existe déjà
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*) FROM characters WHERE name = ? AND anime = ?",
                (name, anime)
            )
            exists = (await cursor.fetchone())[0] > 0
            
            if exists:
                await interaction.response.send_message(
                    f"❌ Le personnage '{name}' de '{anime}' existe déjà!",
                    ephemeral=True
                )
                return
            
            # Créer le personnage
            await self.bot.db.db.execute("""
                INSERT INTO characters (name, anime, rarity, value, image_url)
                VALUES (?, ?, ?, ?, ?)
            """, (name, anime, rarity, value, image_url))
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Personnage Créé",
                description=f"**{name}** de '{anime}' créé avec succès!\nRareté: {rarity} | Valeur: {value:,} SC",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ La valeur doit être un nombre valide",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Erreur création personnage: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )


class SearchCharacterModal(discord.ui.Modal, title="🔍 Rechercher Personnage"):
    """Modal pour rechercher un personnage"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    search_term = discord.ui.TextInput(
        label="Nom ou Série",
        placeholder="Ex: Naruto ou Dragon Ball",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            search = f"%{self.search_term.value.strip()}%"
            
            cursor = await self.bot.db.db.execute("""
                SELECT id, name, anime, rarity, value FROM characters 
                WHERE name LIKE ? OR anime LIKE ?
                ORDER BY name
                LIMIT 10
            """, (search, search))
            
            results = await cursor.fetchall()
            
            if results:
                result_text = ""
                for char_id, name, anime, rarity, value in results:
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    series = anime if anime else "Aucune"
                    result_text += f"{emoji} {char_id:3d}. {name} ({series}) - {value:,} SC\n"
                
                embed = discord.Embed(
                    title="🔍 Résultats de Recherche",
                    description=f"```{result_text}```",
                    color=BotConfig.RARITY_COLORS['Epic']
                )
            else:
                embed = discord.Embed(
                    title="🔍 Aucun Résultat",
                    description="Aucun personnage trouvé pour cette recherche",
                    color=0xff0000
                )
            
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur recherche personnage: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )


class PlayerManagementView(discord.ui.View):
    """Vue de gestion des joueurs"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    @discord.ui.button(label="👥 Lister", style=discord.ButtonStyle.primary, row=0)
    async def list_players_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Lister tous les joueurs"""
        await interaction.response.send_message(
            "💡 **Liste des Joueurs:**\n"
            "Utilisez `!players` pour voir la liste complète des joueurs avec pagination",
            ephemeral=True
        )
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.secondary, row=0)
    async def search_player_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un joueur"""
        await interaction.response.send_message(
            "💡 **Recherche de Joueur:**\n"
            "Utilisez `!playerinfo [nom/ID]` pour obtenir les informations d'un joueur",
            ephemeral=True
        )
    
    @discord.ui.button(label="🪙 Économie", style=discord.ButtonStyle.success, row=0)
    async def economy_management_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Gestion économique"""
        await interaction.response.send_message(
            "💡 **Gestion Économique:**\n"
            "• `!givecoins [user] [amount]` - Donner des pièces\n"
            "• `!removecoins [user] [amount]` - Retirer des pièces\n"
            "• `!setcoins [user] [amount]` - Définir montant exact\n"
            "• `!economystats` - Statistiques économiques",
            ephemeral=True
        )
    
    @discord.ui.button(label="🚫 Modération", style=discord.ButtonStyle.danger, row=1)
    async def moderation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modération des joueurs"""
        await interaction.response.send_message(
            "💡 **Modération:**\n"
            "• `!banuser [user]` - Bannir un utilisateur\n"
            "• `!unbanuser [user]` - Débannir un utilisateur\n"
            "• `!bannedlist` - Liste des utilisateurs bannis\n"
            "• `!resetdaily [user]` - Reset cooldown daily",
            ephemeral=True
        )
    
    @discord.ui.button(label="🏠 Retour Admin", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu admin"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


async def setup_complete_admin_commands(bot):
    """Setup des commandes admin complètes"""
    
    @bot.command(name='admin')
    async def admin_command(ctx):
        """Interface d'administration complète"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        view = AdminCompleteView(bot, ctx.author.id)
        embed = await view.create_main_embed()
        await ctx.send(embed=embed, view=view)
    
    logger.info("Complete admin system setup completed")