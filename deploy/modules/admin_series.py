"""
Système de Gestion des Séries pour Admins - Shadow Roll Bot
Permet de créer de nouvelles séries et d'assigner des personnages
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name

logger = logging.getLogger(__name__)

class SeriesManagementView(discord.ui.View):
    """Interface de gestion des séries pour admins"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.mode = "main"  # main, create, assign, edit
        self.selected_series = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_main_embed(self) -> discord.Embed:
        """Créer l'embed principal de gestion des séries"""
        embed = discord.Embed(
            title="🎖️ ═══════〔 G E S T I O N   D E S   S É R I E S 〕═══════ 🎖️",
            description="```\n◆ Administration des Séries d'Anime ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        # Récupérer les séries existantes
        series_data = await self.get_all_series()
        
        embed.add_field(
            name="📊 ═══〔 Statistiques Actuelles 〕═══ 📊",
            value=(f"```\n"
                   f"Séries Totales: {len(series_data)}\n"
                   f"Personnages Assignés: {sum(len(s['characters']) for s in series_data)}\n"
                   f"Bonus Actifs: {len([s for s in series_data if s.get('bonus_type')])}\n"
                   f"```"),
            inline=False
        )
        
        # Afficher les séries existantes
        if series_data:
            series_list = ""
            for i, series in enumerate(series_data[:10]):  # Limiter à 10 pour l'affichage
                bonus_text = ""
                if series.get('bonus_type') and series.get('bonus_value'):
                    bonus_text = f" (+{series['bonus_value']}% {series['bonus_type']})"
                series_list += f"• {series['name']}: {len(series['characters'])} perso{bonus_text}\n"
            
            embed.add_field(
                name="🎭 ═══〔 Séries Existantes 〕═══ 🎭",
                value=f"```\n{series_list}```",
                inline=False
            )
        
        embed.add_field(
            name="🛠️ ═══〔 Actions Disponibles 〕═══ 🛠️",
            value=("```\n"
                   "🆕 Créer Série - Nouvelle série d'anime\n"
                   "📝 Assigner - Ajouter personnages à série\n"
                   "⚙️ Modifier - Éditer série existante\n"
                   "📋 Détails - Voir série complète\n"
                   "🗑️ Supprimer - Retirer une série\n"
                   "```"),
            inline=False
        )
        
        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Gestion Séries Admin")
        return embed
    
    async def get_all_series(self) -> List[Dict]:
        """Récupérer toutes les séries avec leurs personnages"""
        try:
            async with self.bot.db.db.execute("""
                SELECT DISTINCT anime FROM characters 
                WHERE anime IS NOT NULL AND anime != ''
            """) as cursor:
                series_names = [row[0] for row in await cursor.fetchall()]
            
            series_data = []
            for series_name in series_names:
                # Récupérer les personnages de cette série
                async with self.bot.db.db.execute("""
                    SELECT name, rarity FROM characters 
                    WHERE anime = ?
                """, (series_name,)) as cursor:
                    characters = await cursor.fetchall()
                
                # Récupérer les bonus de série s'ils existent
                bonus_data = await self.get_series_bonus(series_name)
                
                series_data.append({
                    'name': series_name,
                    'characters': characters,
                    'bonus_type': bonus_data.get('bonus_type'),
                    'bonus_value': bonus_data.get('bonus_value')
                })
            
            return series_data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des séries: {e}")
            return []
    
    async def get_series_bonus(self, series_name: str) -> Dict:
        """Récupérer les bonus d'une série"""
        # Pour l'instant, utilisons les bonus hardcodés du config
        # Plus tard on pourrait les stocker en base
        series_bonuses = {
            'Naruto': {'bonus_type': 'rarity', 'bonus_value': 1.0},
            'One Piece': {'bonus_type': 'coins', 'bonus_value': 15.0},
            'Attack on Titan': {'bonus_type': 'coins', 'bonus_value': 10.0},
            'Demon Slayer': {'bonus_type': 'coins', 'bonus_value': 8.0},
            'Dragon Ball Z': {'bonus_type': 'coins', 'bonus_value': 12.0},
            'My Hero Academia': {'bonus_type': 'coins', 'bonus_value': 7.0},
            'Death Note': {'bonus_type': 'rarity', 'bonus_value': 0.5},
            'Fullmetal Alchemist': {'bonus_type': 'coins', 'bonus_value': 6.0},
            'Hunter x Hunter': {'bonus_type': 'rarity', 'bonus_value': 0.8},
            'Bleach': {'bonus_type': 'coins', 'bonus_value': 9.0}
        }
        
        return series_bonuses.get(series_name, {})
    
    @discord.ui.button(label="🆕 Créer Série", style=discord.ButtonStyle.success, row=0)
    async def create_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Créer une nouvelle série"""
        modal = CreateSeriesModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📝 Assigner", style=discord.ButtonStyle.primary, row=0)
    async def assign_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Assigner des personnages à une série"""
        view = AssignCharacterView(self.bot, self.user_id, self)
        embed = await view.create_assign_embed()
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="⚙️ Modifier", style=discord.ButtonStyle.secondary, row=0)
    async def edit_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Modifier une série existante"""
        view = EditSeriesView(self.bot, self.user_id, self)
        embed = await view.create_edit_embed()
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="📋 Détails", style=discord.ButtonStyle.secondary, row=1)
    async def details_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Voir les détails d'une série"""
        view = SeriesDetailsView(self.bot, self.user_id, self)
        embed = await view.create_details_embed()
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger, row=1)
    async def delete_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Supprimer une série"""
        view = DeleteSeriesView(self.bot, self.user_id, self)
        embed = await view.create_delete_embed()
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🏠 Menu Admin", style=discord.ButtonStyle.secondary, row=2)
    async def back_to_admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu admin"""
        await interaction.response.defer()
        from modules.admin_complete import AdminCompleteView
        view = AdminCompleteView(self.bot, self.user_id)
        embed = await view.create_main_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class CreateSeriesModal(discord.ui.Modal, title="🆕 Créer Nouvelle Série"):
    """Modal pour créer une nouvelle série"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    series_name = discord.ui.TextInput(
        label="Nom de la Série",
        placeholder="Ex: Jujutsu Kaisen",
        required=True,
        max_length=50
    )
    
    bonus_type = discord.ui.TextInput(
        label="Type de Bonus (coins/rarity)",
        placeholder="coins ou rarity",
        required=False,
        max_length=10
    )
    
    bonus_value = discord.ui.TextInput(
        label="Valeur du Bonus (%)",
        placeholder="Ex: 5.0 pour +5%",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            series_name = self.series_name.value.strip()
            bonus_type = self.bonus_type.value.strip().lower() if self.bonus_type.value else None
            bonus_value = float(self.bonus_value.value) if self.bonus_value.value else 0.0
            
            # Vérifier si la série existe déjà
            async with self.bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (series_name,)) as cursor:
                exists = (await cursor.fetchone())[0] > 0
            
            if exists:
                embed = discord.Embed(
                    title="❌ Série Existante",
                    description=f"La série '{series_name}' existe déjà!",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Validation du type de bonus
            if bonus_type and bonus_type not in ['coins', 'rarity']:
                embed = discord.Embed(
                    title="❌ Type de Bonus Invalide",
                    description="Le type de bonus doit être 'coins' ou 'rarity'",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Créer la série (elle sera créée automatiquement quand on assignera des personnages)
            embed = discord.Embed(
                title="✅ Série Préparée",
                description=(f"Série '{series_name}' préparée!\n"
                           f"Bonus: {bonus_type} +{bonus_value}% (si spécifié)\n\n"
                           f"Utilisez maintenant '📝 Assigner' pour ajouter des personnages."),
                color=0x00ff00
            )
            
            # Sauvegarder temporairement les infos de bonus
            if not hasattr(self.bot, 'temp_series_bonuses'):
                self.bot.temp_series_bonuses = {}
            
            if bonus_type:
                self.bot.temp_series_bonuses[series_name] = {
                    'bonus_type': bonus_type,
                    'bonus_value': bonus_value
                }
            
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Valeur Invalide",
                description="La valeur du bonus doit être un nombre valide",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        except Exception as e:
            logger.error(f"Erreur lors de la création de série: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


class AssignCharacterView(discord.ui.View):
    """Vue pour assigner des personnages à une série"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        self.current_page = 0
        self.characters_per_page = 10
        self.selected_characters = []
        self.target_series = None
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_assign_embed(self) -> discord.Embed:
        """Créer l'embed d'assignation"""
        embed = discord.Embed(
            title="📝 ═══════〔 A S S I G N E R   P E R S O N N A G E S 〕═══════ 📝",
            description="```\n◆ Assignez des personnages à une série ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        if self.target_series:
            embed.add_field(
                name="🎯 Série Cible",
                value=f"```{self.target_series}```",
                inline=False
            )
        
        # Récupérer les personnages sans série ou avec une série différente
        unassigned_chars = await self.get_unassigned_characters()
        
        if unassigned_chars:
            start_idx = self.current_page * self.characters_per_page
            end_idx = start_idx + self.characters_per_page
            chars_page = unassigned_chars[start_idx:end_idx]
            
            char_list = ""
            for i, char in enumerate(chars_page, start_idx + 1):
                current_series = char[2] if char[2] else "Aucune"
                selected = "✅" if char[0] in self.selected_characters else "⬜"
                char_list += f"{selected} {i}. {char[1]} ({char[3]}) - {current_series}\n"
            
            embed.add_field(
                name=f"👥 Personnages Disponibles (Page {self.current_page + 1})",
                value=f"```{char_list}```",
                inline=False
            )
            
            if self.selected_characters:
                embed.add_field(
                    name="✅ Personnages Sélectionnés",
                    value=f"```{len(self.selected_characters)} personnages```",
                    inline=True
                )
        else:
            embed.add_field(
                name="ℹ️ Information",
                value="```Tous les personnages sont déjà assignés```",
                inline=False
            )
        
        embed.set_footer(text="Utilisez les boutons pour naviguer et sélectionner")
        return embed
    
    async def get_unassigned_characters(self) -> List[tuple]:
        """Récupérer les personnages disponibles pour assignation"""
        try:
            async with self.bot.db.db.execute("""
                SELECT id, name, anime, rarity FROM characters 
                ORDER BY name
            """) as cursor:
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur récupération personnages: {e}")
            return []
    
    @discord.ui.button(label="🎯 Choisir Série", style=discord.ButtonStyle.primary, row=0)
    async def choose_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Choisir la série cible"""
        modal = ChooseSeriesModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⬜ Sélectionner", style=discord.ButtonStyle.secondary, row=0)
    async def select_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sélectionner un personnage"""
        modal = SelectCharacterModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="💾 Assigner", style=discord.ButtonStyle.success, row=0)
    async def assign_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Effectuer l'assignation"""
        if not self.target_series:
            embed = discord.Embed(
                title="❌ Série Manquante",
                description="Veuillez d'abord choisir une série cible",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        if not self.selected_characters:
            embed = discord.Embed(
                title="❌ Personnages Manquants",
                description="Veuillez sélectionner au moins un personnage",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        try:
            # Assigner les personnages à la série
            for char_id in self.selected_characters:
                await self.bot.db.db.execute("""
                    UPDATE characters SET anime = ? WHERE id = ?
                """, (self.target_series, char_id))
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Assignation Réussie",
                description=f"{len(self.selected_characters)} personnages assignés à '{self.target_series}'",
                color=0x00ff00
            )
            
            # Retour au menu principal
            main_embed = await self.parent_view.create_main_embed()
            await interaction.response.edit_message(embed=main_embed, view=self.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur assignation: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de l'assignation: {str(e)}",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⬅️ Précédent", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.create_assign_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="➡️ Suivant", style=discord.ButtonStyle.secondary, row=1)
    async def next_page_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        unassigned_chars = await self.get_unassigned_characters()
        max_pages = (len(unassigned_chars) - 1) // self.characters_per_page + 1
        
        if self.current_page < max_pages - 1:
            self.current_page += 1
            embed = await self.create_assign_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.secondary, row=1)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class ChooseSeriesModal(discord.ui.Modal, title="🎯 Choisir Série Cible"):
    """Modal pour choisir la série cible"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    series_name = discord.ui.TextInput(
        label="Nom de la Série",
        placeholder="Ex: Jujutsu Kaisen",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.target_series = self.series_name.value.strip()
        embed = await self.parent_view.create_assign_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class SelectCharacterModal(discord.ui.Modal, title="⬜ Sélectionner Personnage"):
    """Modal pour sélectionner un personnage par ID"""
    
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
        try:
            char_id = int(self.character_id.value.strip())
            
            # Vérifier que le personnage existe
            async with self.bot.db.db.execute("""
                SELECT name FROM characters WHERE id = ?
            """, (char_id,)) as cursor:
                result = await cursor.fetchone()
            
            if not result:
                embed = discord.Embed(
                    title="❌ Personnage Introuvable",
                    description=f"Aucun personnage avec l'ID {char_id}",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Ajouter/retirer de la sélection
            if char_id in self.parent_view.selected_characters:
                self.parent_view.selected_characters.remove(char_id)
            else:
                self.parent_view.selected_characters.append(char_id)
            
            embed = await self.parent_view.create_assign_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ ID Invalide",
                description="L'ID doit être un nombre valide",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        except Exception as e:
            logger.error(f"Erreur sélection personnage: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


class EditSeriesView(discord.ui.View):
    """Vue pour modifier une série existante"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_edit_embed(self) -> discord.Embed:
        """Créer l'embed de modification"""
        embed = discord.Embed(
            title="⚙️ ═══════〔 M O D I F I E R   S É R I E 〕═══════ ⚙️",
            description="```\n◆ Modifiez une série existante ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        embed.add_field(
            name="🛠️ Actions Disponibles",
            value=("```\n"
                   "📝 Renommer - Changer le nom de la série\n"
                   "➕ Ajouter - Ajouter des personnages\n"
                   "➖ Retirer - Retirer des personnages\n"
                   "🪙 Bonus - Modifier les bonus\n"
                   "```"),
            inline=False
        )
        
        return embed
    
    @discord.ui.button(label="📝 Renommer", style=discord.ButtonStyle.primary, row=0)
    async def rename_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Renommer une série"""
        modal = RenameSeriesModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.secondary, row=0)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class RenameSeriesModal(discord.ui.Modal, title="📝 Renommer Série"):
    """Modal pour renommer une série"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    old_name = discord.ui.TextInput(
        label="Ancien Nom",
        placeholder="Ex: One Piece",
        required=True,
        max_length=50
    )
    
    new_name = discord.ui.TextInput(
        label="Nouveau Nom",
        placeholder="Ex: One Piece: New World",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            old_name = self.old_name.value.strip()
            new_name = self.new_name.value.strip()
            
            # Vérifier que l'ancienne série existe
            async with self.bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (old_name,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count == 0:
                embed = discord.Embed(
                    title="❌ Série Introuvable",
                    description=f"Aucune série nommée '{old_name}'",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Vérifier que le nouveau nom n'existe pas déjà
            async with self.bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (new_name,)) as cursor:
                exists = (await cursor.fetchone())[0] > 0
            
            if exists and new_name != old_name:
                embed = discord.Embed(
                    title="❌ Nom Déjà Utilisé",
                    description=f"Une série nommée '{new_name}' existe déjà",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Effectuer le renommage
            await self.bot.db.db.execute("""
                UPDATE characters SET anime = ? WHERE anime = ?
            """, (new_name, old_name))
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Renommage Réussi",
                description=f"'{old_name}' → '{new_name}'\n{count} personnages mis à jour",
                color=0x00ff00
            )
            
            # Retour au menu principal
            main_embed = await self.parent_view.parent_view.create_main_embed()
            await interaction.response.edit_message(embed=main_embed, view=self.parent_view.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur renommage série: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


class SeriesDetailsView(discord.ui.View):
    """Vue pour voir les détails d'une série"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        self.current_series = None
        self.current_page = 0
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_details_embed(self) -> discord.Embed:
        """Créer l'embed de détails"""
        embed = discord.Embed(
            title="📋 ═══════〔 D É T A I L S   S É R I E 〕═══════ 📋",
            description="```\n◆ Détails complets de la série ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary']
        )
        
        if not self.current_series:
            embed.add_field(
                name="🎯 Sélectionner Série",
                value="```Utilisez le bouton ci-dessous pour choisir une série```",
                inline=False
            )
        else:
            # Récupérer les détails de la série
            series_details = await self.get_series_details(self.current_series)
            
            if series_details:
                embed.add_field(
                    name=f"🎭 {self.current_series}",
                    value=f"```{len(series_details['characters'])} personnages```",
                    inline=False
                )
                
                # Afficher les personnages par rareté
                rarity_groups = {}
                for char in series_details['characters']:
                    rarity = char[1]
                    if rarity not in rarity_groups:
                        rarity_groups[rarity] = []
                    rarity_groups[rarity].append(char[0])
                
                for rarity in ['Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                    if rarity in rarity_groups:
                        emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                        chars = ', '.join(rarity_groups[rarity])
                        embed.add_field(
                            name=f"{emoji} {rarity}",
                            value=f"```{chars}```",
                            inline=False
                        )
                
                # Afficher les bonus
                bonus = series_details.get('bonus')
                if bonus and bonus.get('bonus_type'):
                    embed.add_field(
                        name="🪙 Bonus de Série",
                        value=f"```+{bonus['bonus_value']}% {bonus['bonus_type']}```",
                        inline=True
                    )
        
        return embed
    
    async def get_series_details(self, series_name: str) -> Dict:
        """Récupérer les détails complets d'une série"""
        try:
            async with self.bot.db.db.execute("""
                SELECT name, rarity FROM characters 
                WHERE anime = ?
                ORDER BY rarity DESC, name
            """, (series_name,)) as cursor:
                characters = await cursor.fetchall()
            
            bonus_data = await self.parent_view.get_series_bonus(series_name)
            
            return {
                'characters': characters,
                'bonus': bonus_data
            }
        except Exception as e:
            logger.error(f"Erreur détails série: {e}")
            return {}
    
    @discord.ui.button(label="🎯 Choisir Série", style=discord.ButtonStyle.primary, row=0)
    async def choose_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Choisir la série à afficher"""
        modal = ChooseSeriesDetailsModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.secondary, row=0)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class ChooseSeriesDetailsModal(discord.ui.Modal, title="🎯 Choisir Série"):
    """Modal pour choisir la série à afficher"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    series_name = discord.ui.TextInput(
        label="Nom de la Série",
        placeholder="Ex: Naruto",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        series_name = self.series_name.value.strip()
        
        # Vérifier que la série existe
        async with self.bot.db.db.execute("""
            SELECT COUNT(*) FROM characters WHERE anime = ?
        """, (series_name,)) as cursor:
            count = (await cursor.fetchone())[0]
        
        if count == 0:
            embed = discord.Embed(
                title="❌ Série Introuvable",
                description=f"Aucune série nommée '{series_name}'",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            return
        
        self.parent_view.current_series = series_name
        embed = await self.parent_view.create_details_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class DeleteSeriesView(discord.ui.View):
    """Vue pour supprimer une série"""
    
    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=600)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_delete_embed(self) -> discord.Embed:
        """Créer l'embed de suppression"""
        embed = discord.Embed(
            title="🗑️ ═══════〔 S U P P R I M E R   S É R I E 〕═══════ 🗑️",
            description="```\n⚠️ ATTENTION: Action irréversible! ⚠️\n```",
            color=0xff0000
        )
        
        embed.add_field(
            name="🚨 Important",
            value=("```\n"
                   "Supprimer une série retirera la série\n"
                   "de TOUS les personnages concernés.\n"
                   "Les personnages ne seront PAS supprimés,\n"
                   "mais perdront leur assignation de série.\n"
                   "```"),
            inline=False
        )
        
        return embed
    
    @discord.ui.button(label="🗑️ Confirmer Suppression", style=discord.ButtonStyle.danger, row=0)
    async def confirm_delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmer la suppression"""
        modal = DeleteSeriesModal(self.bot, self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.secondary, row=0)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = await self.parent_view.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class DeleteSeriesModal(discord.ui.Modal, title="🗑️ Confirmer Suppression"):
    """Modal pour confirmer la suppression d'une série"""
    
    def __init__(self, bot, parent_view):
        super().__init__()
        self.bot = bot
        self.parent_view = parent_view
    
    series_name = discord.ui.TextInput(
        label="Nom de la Série à Supprimer",
        placeholder="Tapez exactement le nom de la série",
        required=True,
        max_length=50
    )
    
    confirmation = discord.ui.TextInput(
        label="Confirmation (tapez 'SUPPRIMER')",
        placeholder="SUPPRIMER",
        required=True,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        series_name = self.series_name.value.strip()
        confirmation = self.confirmation.value.strip().upper()
        
        if confirmation != "SUPPRIMER":
            embed = discord.Embed(
                title="❌ Confirmation Invalide",
                description="Vous devez taper exactement 'SUPPRIMER'",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            return
        
        try:
            # Vérifier que la série existe et compter les personnages
            async with self.bot.db.db.execute("""
                SELECT COUNT(*) FROM characters WHERE anime = ?
            """, (series_name,)) as cursor:
                count = (await cursor.fetchone())[0]
            
            if count == 0:
                embed = discord.Embed(
                    title="❌ Série Introuvable",
                    description=f"Aucune série nommée '{series_name}'",
                    color=0xff0000
                )
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
                return
            
            # Supprimer la série (mettre anime à NULL)
            await self.bot.db.db.execute("""
                UPDATE characters SET anime = NULL WHERE anime = ?
            """, (series_name,))
            
            await self.bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Série Supprimée",
                description=f"Série '{series_name}' supprimée\n{count} personnages libérés",
                color=0x00ff00
            )
            
            # Retour au menu principal
            main_embed = await self.parent_view.parent_view.create_main_embed()
            await interaction.response.edit_message(embed=main_embed, view=self.parent_view.parent_view)
            
        except Exception as e:
            logger.error(f"Erreur suppression série: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=0xff0000
            )
            await interaction.response.edit_message(embed=embed, view=self.parent_view)


async def setup_series_admin_commands(bot):
    """Configurer les commandes admin pour les séries"""
    
    @bot.command(name='series')
    async def series_admin_command(ctx):
        """Commande admin pour gérer les séries"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send(BotConfig.MESSAGES['admin_only'])
            return
        
        view = SeriesManagementView(bot, ctx.author.id)
        embed = await view.create_main_embed()
        await ctx.send(embed=embed, view=view)
        
    logger.info("Series admin commands setup completed")