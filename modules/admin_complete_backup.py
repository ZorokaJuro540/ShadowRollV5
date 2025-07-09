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
        self.mode = "economy"
        embed = await self.create_economy_embed()
        view = EconomyManagementView(self.bot, self.user_id, self)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="⚙️ Système", style=discord.ButtonStyle.danger, row=0)
    async def system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Administration système"""
        self.mode = "system"
        embed = await self.create_system_embed()
        view = SystemManagementView(self.bot, self.user_id, self)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, row=1)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Statistiques détaillées"""
        embed = await self.create_detailed_stats_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔄 Actualiser", style=discord.ButtonStyle.secondary, row=1)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Actualiser l'affichage"""
        embed = await self.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
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
        modal = EditCharacterModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
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
            
            # Retour à l'embed personnages
            char_embed = await self.parent_view.parent_view.create_characters_embed()
            await interaction.response.edit_message(embed=char_embed, view=self.parent_view)
            
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


class EditCharacterModal(discord.ui.Modal, title="📝 Modifier Personnage"):
    """Modal pour modifier un personnage"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    character_id = discord.ui.TextInput(
        label="ID du Personnage",
        placeholder="Ex: 25",
        required=True,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "💡 **Modification de Personnage:**\n"
            "Utilisez les commandes legacy pour modifier:\n"
            "• `!editchar [ID] name [nouveau_nom]`\n"
            "• `!editchar [ID] rarity [nouvelle_rareté]`\n"
            "• `!editchar [ID] value [nouvelle_valeur]`\n"
            "• `!editchar [ID] anime [nouvelle_série]`",
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


# Placeholder pour les autres classes admin si nécessaire
class PlayerManagementView(discord.ui.View):
    """Vue de gestion des joueurs - placeholder"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id


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

            active_today = (await cursor.fetchone())[0]
            
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*) FROM players WHERE DATE(last_daily) = ?",
                (today,)
            )
            daily_today = (await cursor.fetchone())[0]
            
            embed.add_field(
                name="📅 Activité Aujourd'hui",
                value=f"```yaml\nRerolls actifs: {active_today:,}\nDaily réclamés: {daily_today:,}```",
                inline=True
            )
            
        except Exception as e:
            logger.error(f"Erreur stats détaillées: {e}")
            embed.description = "❌ Erreur lors du chargement des statistiques"
        
        return embed
    
    async def create_players_embed(self) -> discord.Embed:
        """Liste des joueurs avec pagination"""
        embed = discord.Embed(
            title="👥 ═══════〔 G E S T I O N   J O U E U R S 〕═══════ 👥",
            color=0x3498db
        )
        
        try:
            # Compter le total
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players")
            total_players = (await cursor.fetchone())[0]
            
            # Récupérer la page actuelle
            offset = self.current_page * self.items_per_page
            cursor = await self.bot.db.db.execute(
                "SELECT user_id, username, coins, total_rerolls, is_banned FROM players ORDER BY coins DESC LIMIT ? OFFSET ?",
                (self.items_per_page, offset)
            )
            players = await cursor.fetchall()
            
            if players:
                player_list = []
                for i, (user_id, username, coins, rerolls, is_banned) in enumerate(players, 1):
                    status = "🚫" if is_banned else "✅"
                    rank = offset + i
                    player_list.append(f"`{rank:2}.` {status} **{username}** • {format_number(coins)} pièces • {rerolls:,} rerolls")
                
                embed.description = f"```\n◆ Joueurs {offset + 1}-{min(offset + len(players), total_players)} sur {total_players} ◆\n```"
                embed.add_field(
                    name="📋 Liste des Joueurs",
                    value="\n".join(player_list),
                    inline=False
                )
            else:
                embed.description = "Aucun joueur trouvé"
            
        except Exception as e:
            logger.error(f"Erreur liste joueurs: {e}")
            embed.description = "❌ Erreur lors du chargement"
        
        return embed
    
    async def create_characters_embed(self) -> discord.Embed:
        """Liste des personnages avec pagination"""
        embed = discord.Embed(
            title="🎴 ═══════〔 G E S T I O N   P E R S O N N A G E S 〕═══════ 🎴",
            color=0x9370DB
        )
        
        try:
            # Compter le total
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM characters")
            total_chars = (await cursor.fetchone())[0]
            
            # Récupérer la page actuelle
            offset = self.current_page * self.items_per_page
            cursor = await self.bot.db.db.execute(
                "SELECT id, name, anime, rarity, value FROM characters ORDER BY value DESC LIMIT ? OFFSET ?",
                (self.items_per_page, offset)
            )
            characters = await cursor.fetchall()
            
            if characters:
                char_list = []
                for i, (char_id, name, anime, rarity, value) in enumerate(characters, 1):
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                    rank = offset + i
                    char_list.append(f"`{rank:2}.` {emoji} **{name}** ({anime}) • {format_number(value)} pièces")
                
                embed.description = f"```\n◆ Personnages {offset + 1}-{min(offset + len(characters), total_chars)} sur {total_chars} ◆\n```"
                embed.add_field(
                    name="📋 Liste des Personnages",
                    value="\n".join(char_list),
                    inline=False
                )
            else:
                embed.description = "Aucun personnage trouvé"
            
        except Exception as e:
            logger.error(f"Erreur liste personnages: {e}")
            embed.description = "❌ Erreur lors du chargement"
        
        return embed
    
    async def create_economy_embed(self) -> discord.Embed:
        """Statistiques économiques"""
        embed = discord.Embed(
            title="🪙 ═══════〔 G E S T I O N   É C O N O M I E 〕═══════ 🪙",
            color=0x27ae60
        )
        
        try:
            # Statistiques économiques globales
            cursor = await self.bot.db.db.execute("""
                SELECT 
                    SUM(coins) as total_coins,
                    AVG(coins) as avg_coins,
                    COUNT(*) as player_count
                FROM players
            """)
            eco_stats = await cursor.fetchone()
            
            total_coins, avg_coins, player_count = eco_stats
            
            embed.add_field(
                name="📊 Vue d'ensemble économique",
                value=f"```yaml\nPièces en circulation: {format_number(total_coins or 0)}\nMoyenne par joueur: {format_number(int(avg_coins or 0))}\nJoueurs actifs: {player_count:,}```",
                inline=False
            )
            
            # Distribution des richesses
            ranges = [
                ("💎 Millionnaires", 1000000),
                ("🏆 Riches (100K+)", 100000), 
                ("🪙 Aisés (50K+)", 50000),
                ("🪙 Moyens (10K+)", 10000),
                ("📉 Modestes (<10K)", 0)
            ]
            
            distribution = []
            for name, min_coins in ranges:
                if min_coins == 0:
                    cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players WHERE coins < 10000")
                else:
                    cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players WHERE coins >= ?", (min_coins,))
                count = (await cursor.fetchone())[0]
                percentage = (count / player_count * 100) if player_count > 0 else 0
                distribution.append(f"{name}: {count:,} ({percentage:.1f}%)")
            
            embed.add_field(
                name="📈 Distribution des Richesses",
                value="```\n" + "\n".join(distribution) + "```",
                inline=False
            )
            
        except Exception as e:
            logger.error(f"Erreur stats économie: {e}")
            embed.description = "❌ Erreur lors du chargement"
        
        return embed
    
    async def create_system_embed(self) -> discord.Embed:
        """Informations système"""
        embed = discord.Embed(
            title="⚙️ ═══════〔 A D M I N I S T R A T I O N   S Y S T È M E 〕═══════ ⚙️",
            color=0xe74c3c
        )
        
        try:
            # Informations du bot
            guilds = len(self.bot.guilds)
            total_members = sum(guild.member_count for guild in self.bot.guilds)
            
            embed.add_field(
                name="🤖 Informations Bot",
                value=f"```yaml\nVersion: {BotConfig.VERSION}\nServeurs: {guilds:,}\nMembres total: {total_members:,}\nLatence: {round(self.bot.latency * 1000)}ms```",
                inline=False
            )
            
            # Statistiques des tables
            tables_info = []
            tables = ['players', 'characters', 'inventory', 'achievements', 'player_achievements']
            
            for table in tables:
                try:
                    cursor = await self.bot.db.db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = (await cursor.fetchone())[0]
                    tables_info.append(f"{table}: {count:,} entrées")
                except:
                    tables_info.append(f"{table}: Erreur")
            
            embed.add_field(
                name="🗃️ Base de Données",
                value="```\n" + "\n".join(tables_info) + "```",
                inline=True
            )
            
            # Configuration
            config_info = [
                f"Prefix: {BotConfig.COMMAND_PREFIX}",
                f"Coût reroll: {BotConfig.REROLL_COST}",
                f"Cooldown: {BotConfig.REROLL_COOLDOWN}s",
                f"Pièces de départ: {BotConfig.STARTING_COINS}",
                f"Daily min-max: {BotConfig.DAILY_REWARD_MIN}-{BotConfig.DAILY_REWARD_MAX}"
            ]
            
            embed.add_field(
                name="⚙️ Configuration",
                value="```\n" + "\n".join(config_info) + "```",
                inline=True
            )
            
        except Exception as e:
            logger.error(f"Erreur info système: {e}")
            embed.description = "❌ Erreur lors du chargement"
        
        return embed


# ═══════════════════ VUES DE GESTION SPÉCIALISÉES ═══════════════════

class PlayerManagementView(discord.ui.View):
    """Vue de gestion des joueurs"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    @discord.ui.button(label="🔍 Rechercher", style=discord.ButtonStyle.secondary, row=0)
    async def search_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un joueur"""
        modal = PlayerSearchModal(self.bot, self.parent_view)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🪙 Donner Pièces", style=discord.ButtonStyle.success, row=0)
    async def give_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner des pièces"""
        modal = GiveCoinsModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🚫 Ban/Unban", style=discord.ButtonStyle.danger, row=0)
    async def ban_unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ban/Unban un joueur"""
        modal = BanPlayerModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🔄 Reset Joueur", style=discord.ButtonStyle.danger, row=0)
    async def reset_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Reset un joueur"""
        modal = ResetPlayerModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.parent_view.current_page > 0:
            self.parent_view.current_page -= 1
            embed = await self.parent_view.create_players_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="▶️ Suivant", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        self.parent_view.current_page += 1
        embed = await self.parent_view.create_players_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.primary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class CharacterManagementView(discord.ui.View):
    """Vue de gestion des personnages"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    @discord.ui.button(label="➕ Créer Personnage", style=discord.ButtonStyle.success, row=0)
    async def create_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer un nouveau personnage"""
        modal = CreateCharacterModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🖼️ Modifier Image", style=discord.ButtonStyle.secondary, row=0)
    async def edit_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modifier l'image d'un personnage"""
        modal = EditImageModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎯 Forcer Pull", style=discord.ButtonStyle.primary, row=0)
    async def force_pull(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Forcer un pull pour un joueur"""
        modal = ForcePullModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, row=0)
    async def delete_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer un personnage"""
        modal = DeleteCharacterModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.parent_view.current_page > 0:
            self.parent_view.current_page -= 1
            embed = await self.parent_view.create_characters_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="▶️ Suivant", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        self.parent_view.current_page += 1
        embed = await self.parent_view.create_characters_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.primary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class EconomyManagementView(discord.ui.View):
    """Vue de gestion économique"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    @discord.ui.button(label="🪙 Donner à Tous", style=discord.ButtonStyle.success, row=0)
    async def give_all_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Donner des pièces à tous les joueurs"""
        modal = GiveAllCoinsModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🎁 Event Pièces", style=discord.ButtonStyle.primary, row=0)
    async def event_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Event spécial de pièces"""
        modal = EventCoinsModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📊 Analyse Économie", style=discord.ButtonStyle.secondary, row=0)
    async def economy_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Analyse économique détaillée"""
        embed = await self.create_economy_analysis()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⚖️ Rééquilibrage", style=discord.ButtonStyle.danger, row=0)
    async def rebalance_economy(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rééquilibrage économique"""
        modal = RebalanceEconomyModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.primary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
    
    async def create_economy_analysis(self) -> discord.Embed:
        """Analyse économique approfondie"""
        embed = discord.Embed(
            title="📊 ═══════〔 A N A L Y S E   É C O N O M I Q U E 〕═══════ 📊",
            color=0x27ae60
        )
        
        try:
            # Analyse des tendances
            cursor = await self.bot.db.db.execute("""
                SELECT 
                    COUNT(*) as players,
                    AVG(coins) as avg_coins,
                    MEDIAN(coins) as median_coins,
                    MAX(coins) as max_coins,
                    MIN(coins) as min_coins
                FROM players
            """)
            stats = await cursor.fetchone()
            
            # Calcul de la médiane manuellement car SQLite n'a pas MEDIAN
            cursor = await self.bot.db.db.execute("SELECT coins FROM players ORDER BY coins")
            all_coins = [row[0] for row in await cursor.fetchall()]
            n = len(all_coins)
            median_coins = all_coins[n//2] if n > 0 else 0
            
            embed.add_field(
                name="📈 Tendances Économiques",
                value=f"```yaml\nJoueurs: {stats[0]:,}\nMoyenne: {format_number(int(stats[1] or 0))}\nMédiane: {format_number(median_coins)}\nMax: {format_number(stats[3] or 0)}\nMin: {format_number(stats[4] or 0)}```",
                inline=False
            )
            
            # Analyse des inégalités (coefficient de Gini approximatif)
            if all_coins:
                sorted_coins = sorted(all_coins)
                n = len(sorted_coins)
                cumsum = [sum(sorted_coins[:i+1]) for i in range(n)]
                total_sum = sum(sorted_coins)
                
                # Calcul approximatif du coefficient de Gini
                if total_sum > 0:
                    gini_sum = sum((2 * (i + 1) - n - 1) * coin for i, coin in enumerate(sorted_coins))
                    gini = gini_sum / (n * total_sum)
                    
                    inequality_level = "Très élevée" if gini > 0.7 else "Élevée" if gini > 0.5 else "Modérée" if gini > 0.3 else "Faible"
                    
                    embed.add_field(
                        name="⚖️ Inégalités Économiques",
                        value=f"```yaml\nCoefficient Gini: {gini:.3f}\nNiveau: {inequality_level}\nTop 10%: {format_number(sum(sorted_coins[-n//10:]) if n >= 10 else sum(sorted_coins))} pièces```",
                        inline=True
                    )
            
        except Exception as e:
            logger.error(f"Erreur analyse économique: {e}")
            embed.description = "❌ Erreur lors de l'analyse"
        
        return embed


class SystemManagementView(discord.ui.View):
    """Vue d'administration système"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    @discord.ui.button(label="🔄 Sync Commands", style=discord.ButtonStyle.primary, row=0)
    async def sync_commands(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Synchroniser les commandes slash"""
        await interaction.response.defer()
        try:
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                title="✅ Synchronisation Réussie",
                description=f"**{len(synced)} commandes** slash synchronisées avec Discord.",
                color=0x27ae60
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur de Synchronisation",
                description=f"Impossible de synchroniser les commandes: {e}",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🗃️ Backup DB", style=discord.ButtonStyle.secondary, row=0)
    async def backup_database(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer une sauvegarde de la base de données"""
        await interaction.response.defer()
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"shadow_roll_backup_{timestamp}.db"
            shutil.copy2("shadow_roll.db", backup_path)
            
            embed = discord.Embed(
                title="✅ Sauvegarde Créée",
                description=f"Base de données sauvegardée: `{backup_path}`",
                color=0x27ae60
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur de Sauvegarde",
                description=f"Impossible de créer la sauvegarde: {e}",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🧹 Nettoyage", style=discord.ButtonStyle.danger, row=0)
    async def cleanup_system(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Nettoyage du système"""
        modal = SystemCleanupModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Logs", style=discord.ButtonStyle.secondary, row=0)
    async def view_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Voir les logs système"""
        try:
            with open("bot.log", "r", encoding="utf-8") as f:
                logs = f.readlines()[-20:]  # Dernières 20 lignes
            
            embed = discord.Embed(
                title="📋 Logs Système (20 dernières lignes)",
                description="```\n" + "".join(logs) + "```",
                color=0x95a5a6
            )
            await interaction.response.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur Logs",
                description=f"Impossible de lire les logs: {e}",
                color=0xe74c3c
            )
            await interaction.response.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.primary, row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


# ═══════════════════ MODALS POUR LES ACTIONS ═══════════════════

class PlayerSearchModal(discord.ui.Modal):
    """Modal pour rechercher un joueur"""
    
    def __init__(self, bot, parent_view):
        super().__init__(title="🔍 Rechercher un Joueur")
        self.bot = bot
        self.parent_view = parent_view
        
        self.search_input = discord.ui.TextInput(
            label="Nom du joueur ou ID Discord",
            placeholder="Tapez le nom ou l'ID du joueur à rechercher...",
            max_length=100
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        search_term = self.search_input.value.strip()
        
        try:
            # Recherche par ID si c'est un nombre
            if search_term.isdigit():
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, coins, total_rerolls, is_banned FROM players WHERE user_id = ?",
                    (int(search_term),)
                )
            else:
                # Recherche par nom
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, coins, total_rerolls, is_banned FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{search_term}%",)
                )
            
            results = await cursor.fetchall()
            
            if not results:
                embed = discord.Embed(
                    title="❌ Aucun Résultat",
                    description=f"Aucun joueur trouvé pour: `{search_term}`",
                    color=0xe74c3c
                )
                await interaction.response.send(embed=embed, ephemeral=True)
                return
            
            if len(results) == 1:
                # Un seul résultat - afficher le profil
                user_id, username, coins, rerolls, is_banned = results[0]
                embed = await self.create_player_profile(user_id, username, coins, rerolls, is_banned)
                await interaction.response.send(embed=embed, ephemeral=True)
            else:
                # Multiples résultats - afficher la liste
                embed = discord.Embed(
                    title="🔍 Résultats de Recherche",
                    color=0x3498db
                )
                
                result_list = []
                for user_id, username, coins, rerolls, is_banned in results[:10]:  # Limiter à 10
                    status = "🚫" if is_banned else "✅"
                    result_list.append(f"{status} **{username}** (ID: {user_id}) • {format_number(coins)} pièces")
                
                embed.add_field(
                    name=f"Joueurs trouvés ({len(results)})",
                    value="\n".join(result_list),
                    inline=False
                )
                
                await interaction.response.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Erreur recherche joueur: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de la recherche",
                color=0xe74c3c
            )
            await interaction.response.send(embed=embed, ephemeral=True)
    
    async def create_player_profile(self, user_id: int, username: str, coins: int, rerolls: int, is_banned: bool) -> discord.Embed:
        """Créer un profil détaillé du joueur"""
        embed = discord.Embed(
            title=f"👤 Profil de {username}",
            color=0xe74c3c if is_banned else 0x27ae60
        )
        
        try:
            # Informations de base
            status = "🚫 Banni" if is_banned else "✅ Actif"
            embed.add_field(
                name="📊 Informations Générales",
                value=f"**ID Discord:** {user_id}\n**Statut:** {status}\n**Pièces:** {format_number(coins)}\n**Rerolls:** {rerolls:,}",
                inline=False
            )
            
            # Statistiques de collection
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*), COUNT(DISTINCT character_id) FROM inventory WHERE user_id = ?",
                (user_id,)
            )
            inv_stats = await cursor.fetchone()
            total_items, unique_chars = inv_stats
            
            # Raretés possédées
            cursor = await self.bot.db.db.execute("""
                SELECT c.rarity, COUNT(*) as count
                FROM inventory i
                JOIN characters c ON i.character_id = c.id
                WHERE i.user_id = ?
                GROUP BY c.rarity
                ORDER BY count DESC
            """, (user_id,))
            rarity_stats = await cursor.fetchall()
            
            collection_info = f"**Total objets:** {total_items:,}\n**Personnages uniques:** {unique_chars:,}\n"
            if rarity_stats:
                rarity_list = []
                for rarity, count in rarity_stats[:5]:  # Top 5
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                    rarity_list.append(f"{emoji} {rarity}: {count:,}")
                collection_info += "**Raretés:**\n" + "\n".join(rarity_list)
            
            embed.add_field(
                name="🎴 Collection",
                value=collection_info,
                inline=True
            )
            
            # Dernière activité
            cursor = await self.bot.db.db.execute(
                "SELECT last_reroll, last_daily FROM players WHERE user_id = ?",
                (user_id,)
            )
            activity = await cursor.fetchone()
            if activity:
                last_reroll, last_daily = activity
                activity_info = f"**Dernier reroll:** {last_reroll or 'Jamais'}\n**Dernier daily:** {last_daily or 'Jamais'}"
                embed.add_field(
                    name="⏰ Activité",
                    value=activity_info,
                    inline=True
                )
        
        except Exception as e:
            logger.error(f"Erreur profil joueur: {e}")
            embed.add_field(
                name="❌ Erreur",
                value="Impossible de charger les détails",
                inline=False
            )
        
        return embed


class GiveCoinsModal(discord.ui.Modal):
    """Modal pour donner des pièces à un joueur"""
    
    def __init__(self, bot):
        super().__init__(title="🪙 Donner des Pièces")
        self.bot = bot
        
        self.player_input = discord.ui.TextInput(
            label="Joueur (nom ou ID Discord)",
            placeholder="Nom du joueur ou ID Discord...",
            max_length=100
        )
        
        self.amount_input = discord.ui.TextInput(
            label="Montant",
            placeholder="Nombre de pièces à donner...",
            max_length=20
        )
        
        self.reason_input = discord.ui.TextInput(
            label="Raison (optionnel)",
            placeholder="Raison de l'attribution...",
            required=False,
            max_length=200
        )
        
        self.add_item(self.player_input)
        self.add_item(self.amount_input)
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            player_term = self.player_input.value.strip()
            amount = int(self.amount_input.value.strip())
            reason = self.reason_input.value.strip() or "Attribution admin"
            
            # Trouver le joueur
            if player_term.isdigit():
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE user_id = ?",
                    (int(player_term),)
                )
            else:
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, coins FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{player_term}%",)
                )
            
            results = await cursor.fetchall()
            
            if not results:
                embed = discord.Embed(
                    title="❌ Joueur Introuvable",
                    description=f"Aucun joueur trouvé pour: `{player_term}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if len(results) > 1:
                embed = discord.Embed(
                    title="❌ Plusieurs Joueurs",
                    description="Plusieurs joueurs trouvés. Soyez plus précis.",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            user_id, username, current_coins = results[0]
            new_coins = current_coins + amount
            
            # Mettre à jour les pièces
            await self.bot.db.db.execute(
                "UPDATE players SET coins = ? WHERE user_id = ?",
                (new_coins, user_id)
            )
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Pièces Attribuées",
                description=f"**{format_number(amount)} pièces** données à **{username}**",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Avant:** {format_number(current_coins)} pièces\n**Après:** {format_number(new_coins)} pièces\n**Raison:** {reason}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Montant Invalide",
                description="Veuillez entrer un nombre valide",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur donner pièces: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de l'attribution des pièces",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class GiveAllCoinsModal(discord.ui.Modal):
    """Modal pour donner des pièces à tous les joueurs"""
    
    def __init__(self, bot):
        super().__init__(title="🪙 Donner des Pièces à Tous")
        self.bot = bot
        
        self.amount_input = discord.ui.TextInput(
            label="Montant par joueur",
            placeholder="Nombre de pièces à donner à chaque joueur...",
            max_length=20
        )
        
        self.reason_input = discord.ui.TextInput(
            label="Raison",
            placeholder="Raison de l'événement (ex: Event spécial, compensation...)...",
            max_length=200
        )
        
        self.add_item(self.amount_input)
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            amount = int(self.amount_input.value.strip())
            reason = self.reason_input.value.strip()
            
            # Compter les joueurs actifs (non bannis)
            cursor = await self.bot.db.db.execute("SELECT COUNT(*) FROM players WHERE is_banned = 0")
            player_count = (await cursor.fetchone())[0]
            
            if player_count == 0:
                embed = discord.Embed(
                    title="❌ Aucun Joueur",
                    description="Aucun joueur actif trouvé",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            total_cost = amount * player_count
            
            # Confirmation
            embed = discord.Embed(
                title="⚠️ Confirmation Required",
                description=f"Vous allez donner **{format_number(amount)} pièces** à **{player_count:,} joueurs**",
                color=0xf39c12
            )
            embed.add_field(
                name="📊 Résumé",
                value=f"**Coût total:** {format_number(total_cost)} pièces\n**Raison:** {reason}",
                inline=False
            )
            
            view = ConfirmGiveAllView(self.bot, amount, reason, player_count)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Montant Invalide",
                description="Veuillez entrer un nombre valide",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur distribution pièces: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de la préparation de la distribution",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class ConfirmGiveAllView(discord.ui.View):
    """Vue de confirmation pour la distribution de pièces"""
    
    def __init__(self, bot, amount: int, reason: str, player_count: int):
        super().__init__(timeout=60)
        self.bot = bot
        self.amount = amount
        self.reason = reason
        self.player_count = player_count
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmer la distribution"""
        await interaction.response.defer()
        
        try:
            # Distribuer les pièces
            await self.bot.db.db.execute(
                "UPDATE players SET coins = coins + ? WHERE is_banned = 0",
                (self.amount,)
            )
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Distribution Réussie",
                description=f"**{format_number(self.amount)} pièces** distribuées à **{self.player_count:,} joueurs**",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Total distribué:** {format_number(self.amount * self.player_count)} pièces\n**Raison:** {self.reason}",
                inline=False
            )
            
            await interaction.followup.edit_message(
                interaction.message.id,
                embed=embed,
                view=None
            )
            
        except Exception as e:
            logger.error(f"Erreur distribution finale: {e}")
            embed = discord.Embed(
                title="❌ Erreur de Distribution",
                description="Erreur lors de la distribution des pièces",
                color=0xe74c3c
            )
            await interaction.followup.edit_message(
                interaction.message.id,
                embed=embed,
                view=None
            )
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annuler la distribution"""
        embed = discord.Embed(
            title="❌ Distribution Annulée",
            description="La distribution de pièces a été annulée",
            color=0x95a5a6
        )
        await interaction.response.edit_message(embed=embed, view=None)


class BanPlayerModal(discord.ui.Modal):
    """Modal pour ban/unban un joueur"""
    
    def __init__(self, bot):
        super().__init__(title="🚫 Ban/Unban Joueur")
        self.bot = bot
        
        self.player_input = discord.ui.TextInput(
            label="Joueur (nom ou ID Discord)",
            placeholder="Nom du joueur ou ID Discord...",
            max_length=100
        )
        
        self.action_input = discord.ui.TextInput(
            label="Action (ban/unban)",
            placeholder="Tapez 'ban' pour bannir ou 'unban' pour débannir...",
            max_length=10
        )
        
        self.reason_input = discord.ui.TextInput(
            label="Raison",
            placeholder="Raison du ban/unban...",
            max_length=200
        )
        
        self.add_item(self.player_input)
        self.add_item(self.action_input)
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            player_term = self.player_input.value.strip()
            action = self.action_input.value.strip().lower()
            reason = self.reason_input.value.strip()
            
            if action not in ['ban', 'unban']:
                embed = discord.Embed(
                    title="❌ Action Invalide",
                    description="L'action doit être 'ban' ou 'unban'",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Trouver le joueur
            if player_term.isdigit():
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, banned FROM players WHERE user_id = ?",
                    (int(player_term),)
                )
            else:
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username, banned FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{player_term}%",)
                )
            
            results = await cursor.fetchall()
            
            if not results:
                embed = discord.Embed(
                    title="❌ Joueur Introuvable",
                    description=f"Aucun joueur trouvé pour: `{player_term}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if len(results) > 1:
                embed = discord.Embed(
                    title="❌ Plusieurs Joueurs",
                    description="Plusieurs joueurs trouvés. Soyez plus précis.",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            user_id, username, currently_banned = results[0]
            new_ban_status = 1 if action == 'ban' else 0
            
            if (currently_banned and action == 'ban') or (not currently_banned and action == 'unban'):
                status_text = "déjà banni" if action == 'ban' else "pas banni"
                embed = discord.Embed(
                    title="⚠️ Aucun Changement",
                    description=f"**{username}** est {status_text}",
                    color=0xf39c12
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Mettre à jour le statut
            await self.bot.db.db.execute(
                "UPDATE players SET banned = ? WHERE user_id = ?",
                (new_ban_status, user_id)
            )
            await self.bot.db.db.commit()
            
            action_text = "banni" if action == 'ban' else "débanni"
            color = 0xe74c3c if action == 'ban' else 0x27ae60
            
            embed = discord.Embed(
                title=f"✅ Joueur {action_text.title()}",
                description=f"**{username}** a été {action_text}",
                color=color
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Joueur:** {username} (ID: {user_id})\n**Action:** {action_text.title()}\n**Raison:** {reason}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur ban/unban: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors du ban/unban",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class CreateCharacterModal(discord.ui.Modal):
    """Modal pour créer un nouveau personnage"""
    
    def __init__(self, bot):
        super().__init__(title="➕ Créer un Personnage")
        self.bot = bot
        
        self.name_input = discord.ui.TextInput(
            label="Nom du personnage",
            placeholder="Nom du personnage...",
            max_length=100
        )
        
        self.anime_input = discord.ui.TextInput(
            label="Anime/Série",
            placeholder="Nom de l'anime ou série...",
            max_length=100
        )
        
        self.rarity_input = discord.ui.TextInput(
            label="Rareté",
            placeholder="Common, Rare, Epic, Legendary, Mythic, Titan, Fusion, Secret",
            max_length=20
        )
        
        self.value_input = discord.ui.TextInput(
            label="Valeur (pièces)",
            placeholder="Valeur en pièces...",
            max_length=20
        )
        
        self.image_input = discord.ui.TextInput(
            label="URL de l'image (optionnel)",
            placeholder="URL de l'image du personnage...",
            required=False,
            max_length=500
        )
        
        self.add_item(self.name_input)
        self.add_item(self.anime_input)
        self.add_item(self.rarity_input)
        self.add_item(self.value_input)
        self.add_item(self.image_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            name = self.name_input.value.strip()
            anime = self.anime_input.value.strip()
            rarity = self.rarity_input.value.strip()
            value = int(self.value_input.value.strip())
            image_url = self.image_input.value.strip() or None
            
            # Vérifier que la rareté est valide
            valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']
            if rarity not in valid_rarities:
                embed = discord.Embed(
                    title="❌ Rareté Invalide",
                    description=f"Raretés valides: {', '.join(valid_rarities)}",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Vérifier si le personnage existe déjà
            cursor = await self.bot.db.db.execute(
                "SELECT id FROM characters WHERE LOWER(name) = LOWER(?)",
                (name,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                embed = discord.Embed(
                    title="❌ Personnage Existant",
                    description=f"Un personnage nommé **{name}** existe déjà",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Créer le personnage
            await self.bot.db.db.execute(
                "INSERT INTO characters (name, anime, rarity, value, image_url) VALUES (?, ?, ?, ?, ?)",
                (name, anime, rarity, value, image_url)
            )
            await self.bot.db.db.commit()
            
            # Récupérer l'ID du nouveau personnage
            cursor = await self.bot.db.db.execute(
                "SELECT id FROM characters WHERE name = ? AND anime = ?",
                (name, anime)
            )
            char_id = (await cursor.fetchone())[0]
            
            embed = discord.Embed(
                title="✅ Personnage Créé",
                description=f"**{name}** a été créé avec succès",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**ID:** {char_id}\n**Anime:** {anime}\n**Rareté:** {rarity}\n**Valeur:** {format_number(value)} pièces",
                inline=False
            )
            
            if image_url:
                embed.set_thumbnail(url=image_url)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Valeur Invalide",
                description="Veuillez entrer un nombre valide pour la valeur",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur création personnage: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de la création du personnage",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class ForcePullModal(discord.ui.Modal):
    """Modal pour forcer un pull pour un joueur"""
    
    def __init__(self, bot):
        super().__init__(title="🎯 Forcer un Pull")
        self.bot = bot
        
        self.player_input = discord.ui.TextInput(
            label="Joueur (nom ou ID Discord)",
            placeholder="Nom du joueur ou ID Discord...",
            max_length=100
        )
        
        self.character_input = discord.ui.TextInput(
            label="Personnage ou Rareté",
            placeholder="Nom exact du personnage OU rareté (Common, Rare, etc.)...",
            max_length=100
        )
        
        self.add_item(self.player_input)
        self.add_item(self.character_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            player_term = self.player_input.value.strip()
            char_term = self.character_input.value.strip()
            
            # Trouver le joueur
            if player_term.isdigit():
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE user_id = ?",
                    (int(player_term),)
                )
            else:
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{player_term}%",)
                )
            
            player_results = await cursor.fetchall()
            
            if not player_results:
                embed = discord.Embed(
                    title="❌ Joueur Introuvable",
                    description=f"Aucun joueur trouvé pour: `{player_term}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if len(player_results) > 1:
                embed = discord.Embed(
                    title="❌ Plusieurs Joueurs",
                    description="Plusieurs joueurs trouvés. Soyez plus précis.",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            user_id, username = player_results[0]
            
            # Déterminer si c'est un personnage ou une rareté
            character = None
            valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']
            
            if char_term in valid_rarities:
                # Forcer une rareté
                character = await self.bot.db.get_character_by_rarity_weight(user_id, self.bot)
                # Ici on devrait modifier la méthode pour forcer une rareté spécifique
                # Pour l'instant, on tire aléatoirement dans la rareté
                cursor = await self.bot.db.db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE rarity = ? ORDER BY RANDOM() LIMIT 1",
                    (char_term,)
                )
                char_data = await cursor.fetchone()
                
                if not char_data:
                    embed = discord.Embed(
                        title="❌ Aucun Personnage",
                        description=f"Aucun personnage de rareté **{char_term}** trouvé",
                        color=0xe74c3c
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                from core.models import Character
                character = Character(
                    id=char_data[0],
                    name=char_data[1],
                    anime=char_data[2],
                    rarity=char_data[3],
                    value=char_data[4],
                    image_url=char_data[5]
                )
            else:
                # Rechercher le personnage par nom
                cursor = await self.bot.db.db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) LIKE LOWER(?)",
                    (f"%{char_term}%",)
                )
                char_results = await cursor.fetchall()
                
                if not char_results:
                    embed = discord.Embed(
                        title="❌ Personnage Introuvable",
                        description=f"Aucun personnage trouvé pour: `{char_term}`",
                        color=0xe74c3c
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                if len(char_results) > 1:
                    char_list = []
                    for char_data in char_results[:10]:
                        char_list.append(f"**{char_data[1]}** ({char_data[2]}) - {char_data[3]}")
                    
                    embed = discord.Embed(
                        title="❌ Plusieurs Personnages",
                        description="Plusieurs personnages trouvés:\n" + "\n".join(char_list),
                        color=0xe74c3c
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                
                char_data = char_results[0]
                from core.models import Character
                character = Character(
                    id=char_data[0],
                    name=char_data[1],
                    anime=char_data[2],
                    rarity=char_data[3],
                    value=char_data[4],
                    image_url=char_data[5]
                )
            
            # Ajouter le personnage à l'inventaire
            await self.bot.db.add_character_to_inventory(user_id, character.id)
            
            embed = discord.Embed(
                title="✅ Pull Forcé Réussi",
                description=f"**{character.name}** a été ajouté à l'inventaire de **{username}**",
                color=character.get_rarity_color()
            )
            embed.add_field(
                name=f"{character.get_rarity_emoji()} {character.name}",
                value=f"**Anime:** {character.anime}\n**Rareté:** {character.rarity}\n**Valeur:** {format_number(character.value)} pièces",
                inline=False
            )
            
            if character.image_url:
                embed.set_thumbnail(url=character.image_url)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur pull forcé: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors du pull forcé",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


# Autres modals pour les fonctionnalités restantes...
class ResetPlayerModal(discord.ui.Modal):
    """Modal pour reset un joueur"""
    
    def __init__(self, bot):
        super().__init__(title="🔄 Reset Joueur")
        self.bot = bot
        
        self.player_input = discord.ui.TextInput(
            label="Joueur (nom ou ID Discord)",
            placeholder="Nom du joueur ou ID Discord...",
            max_length=100
        )
        
        self.confirm_input = discord.ui.TextInput(
            label="Confirmation (tapez RESET)",
            placeholder="Tapez RESET pour confirmer...",
            max_length=10
        )
        
        self.add_item(self.player_input)
        self.add_item(self.confirm_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.confirm_input.value.strip().upper() != "RESET":
            embed = discord.Embed(
                title="❌ Confirmation Échouée",
                description="Vous devez taper 'RESET' pour confirmer",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            player_term = self.player_input.value.strip()
            
            # Trouver le joueur
            if player_term.isdigit():
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE user_id = ?",
                    (int(player_term),)
                )
            else:
                cursor = await self.bot.db.db.execute(
                    "SELECT user_id, username FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{player_term}%",)
                )
            
            results = await cursor.fetchall()
            
            if not results:
                embed = discord.Embed(
                    title="❌ Joueur Introuvable",
                    description=f"Aucun joueur trouvé pour: `{player_term}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if len(results) > 1:
                embed = discord.Embed(
                    title="❌ Plusieurs Joueurs",
                    description="Plusieurs joueurs trouvés. Soyez plus précis.",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            user_id, username = results[0]
            
            # Reset du joueur
            await self.bot.db.db.execute(
                "UPDATE players SET coins = ?, reroll_count = 0, last_reroll = NULL, last_daily = NULL WHERE user_id = ?",
                (BotConfig.STARTING_COINS, user_id)
            )
            
            # Supprimer l'inventaire
            await self.bot.db.db.execute(
                "DELETE FROM inventory WHERE user_id = ?",
                (user_id,)
            )
            
            # Supprimer les achievements
            await self.bot.db.db.execute(
                "DELETE FROM player_achievements WHERE user_id = ?",
                (user_id,)
            )
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Joueur Reset",
                description=f"**{username}** a été complètement reset",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Actions Effectuées",
                value=f"• Pièces remises à {BotConfig.STARTING_COINS:,}\n• Reroll count reset\n• Inventaire vidé\n• Achievements supprimés\n• Cooldowns reset",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur reset joueur: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors du reset du joueur",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class EditImageModal(discord.ui.Modal):
    """Modal pour modifier l'image d'un personnage"""
    
    def __init__(self, bot):
        super().__init__(title="🖼️ Modifier Image")
        self.bot = bot
        
        self.character_input = discord.ui.TextInput(
            label="Personnage",
            placeholder="Nom du personnage...",
            max_length=100
        )
        
        self.image_input = discord.ui.TextInput(
            label="Nouvelle URL d'image",
            placeholder="URL de la nouvelle image...",
            max_length=500
        )
        
        self.add_item(self.character_input)
        self.add_item(self.image_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            char_name = self.character_input.value.strip()
            image_url = self.image_input.value.strip()
            
            # Trouver le personnage
            cursor = await self.bot.db.db.execute(
                "SELECT id, name, anime FROM characters WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{char_name}%",)
            )
            results = await cursor.fetchall()
            
            if not results:
                embed = discord.Embed(
                    title="❌ Personnage Introuvable",
                    description=f"Aucun personnage trouvé pour: `{char_name}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            if len(results) > 1:
                char_list = []
                for char_id, name, anime in results[:10]:
                    char_list.append(f"**{name}** ({anime})")
                
                embed = discord.Embed(
                    title="❌ Plusieurs Personnages",
                    description="Plusieurs personnages trouvés:\n" + "\n".join(char_list),
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            char_id, name, anime = results[0]
            
            # Mettre à jour l'image
            await self.bot.db.db.execute(
                "UPDATE characters SET image_url = ? WHERE id = ?",
                (image_url, char_id)
            )
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Image Mise à Jour",
                description=f"L'image de **{name}** a été mise à jour",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Personnage:** {name} ({anime})\n**Nouvelle URL:** [Lien]({image_url})",
                inline=False
            )
            embed.set_thumbnail(url=image_url)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur modification image: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de la modification de l'image",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class DeleteCharacterModal(discord.ui.Modal):
    """Modal pour supprimer un personnage"""
    
    def __init__(self, bot):
        super().__init__(title="🗑️ Supprimer Personnage")
        self.bot = bot
        
        self.character_input = discord.ui.TextInput(
            label="Personnage",
            placeholder="Nom exact du personnage...",
            max_length=100
        )
        
        self.confirm_input = discord.ui.TextInput(
            label="Confirmation (tapez DELETE)",
            placeholder="Tapez DELETE pour confirmer...",
            max_length=10
        )
        
        self.add_item(self.character_input)
        self.add_item(self.confirm_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.confirm_input.value.strip().upper() != "DELETE":
            embed = discord.Embed(
                title="❌ Confirmation Échouée",
                description="Vous devez taper 'DELETE' pour confirmer",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        try:
            char_name = self.character_input.value.strip()
            
            # Trouver le personnage
            cursor = await self.bot.db.db.execute(
                "SELECT id, name, anime FROM characters WHERE LOWER(name) = LOWER(?)",
                (char_name,)
            )
            result = await cursor.fetchone()
            
            if not result:
                embed = discord.Embed(
                    title="❌ Personnage Introuvable",
                    description=f"Aucun personnage trouvé avec le nom exact: `{char_name}`",
                    color=0xe74c3c
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            char_id, name, anime = result
            
            # Compter combien de joueurs ont ce personnage
            cursor = await self.bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE character_id = ?",
                (char_id,)
            )
            owned_count = (await cursor.fetchone())[0]
            
            # Supprimer de l'inventaire des joueurs
            await self.bot.db.db.execute(
                "DELETE FROM inventory WHERE character_id = ?",
                (char_id,)
            )
            
            # Supprimer le personnage
            await self.bot.db.db.execute(
                "DELETE FROM characters WHERE id = ?",
                (char_id,)
            )
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Personnage Supprimé",
                description=f"**{name}** a été supprimé du système",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Impact",
                value=f"**Personnage:** {name} ({anime})\n**Retiré de {owned_count:,} inventaires**",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur suppression personnage: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Erreur lors de la suppression du personnage",
                color=0xe74c3c
            )
            await interaction.followup.send(embed=embed, ephemeral=True)


class EventCoinsModal(discord.ui.Modal):
    """Modal pour event de pièces spécial"""
    pass  # À implémenter si nécessaire


class RebalanceEconomyModal(discord.ui.Modal):
    """Modal pour rééquilibrage économique"""
    pass  # À implémenter si nécessaire


class SystemCleanupModal(discord.ui.Modal):
    """Modal pour nettoyage système"""
    pass  # À implémenter si nécessaire


# ═══════════════════ FONCTION DE CONFIGURATION ═══════════════════

async def setup_complete_admin_commands(bot):
    """Configuration du système d'administration complet"""
    
    # Importer et configurer les commandes legacy
    from modules.admin_legacy_commands import setup_legacy_admin_commands
    await setup_legacy_admin_commands(bot)
    
    @bot.command(name='admin', aliases=['adminpanel', 'administration'])
    async def complete_admin_command(ctx):
        """Interface d'administration complète"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas les permissions d'administrateur.")
            return
        
        try:
            view = AdminCompleteView(bot, ctx.author.id)
            embed = await view.create_main_embed()
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Erreur admin complet: {e}")
            await ctx.send("❌ Erreur lors du chargement de l'interface admin.")
    
    logger.info("Complete admin system setup completed")