"""
Système de Visualisation de Cartes Publique pour Shadow Roll Bot
Permet à tous les utilisateurs de voir les cartes de personnages
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.text_styling import style_section

logger = logging.getLogger(__name__)

class CharacterListView(discord.ui.View):
    """Vue pour afficher la liste paginée des personnages possédés"""
    
    def __init__(self, bot, user_id: int, characters: List[tuple]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.characters = characters
        self.page = 0
        self.items_per_page = 15
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_list_embed(self):
        """Créer l'embed de la liste des personnages"""
        
        if not self.characters:
            return discord.Embed(
                title="📋 Votre Collection",
                description="Vous ne possédez aucun personnage pour le moment.",
                color=0xff0000
            )
        
        start_idx = self.page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_characters = self.characters[start_idx:end_idx]
        
        embed = discord.Embed(
            title=f"📋 ═══════〔 {style_section('VOTRE COLLECTION', '🌌')} 〕═══════ 📋",
            description=f"```\n◆ Total personnages: {len(self.characters)} ◆\n◆ Page: {self.page + 1}/{(len(self.characters) - 1) // self.items_per_page + 1} ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        # Grouper par rareté
        rarity_groups = {}
        for char_id, name, anime, rarity, quantity in page_characters:
            if rarity not in rarity_groups:
                rarity_groups[rarity] = []
            rarity_groups[rarity].append((name, anime, quantity))
        
        # Trier les raretés par ordre de valeur
        rarity_order = ['Secret', 'Evolve', 'Fusion', 'Titan', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']
        
        for rarity in rarity_order:
            if rarity in rarity_groups:
                emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                characters_text = ""
                
                for name, anime, quantity in rarity_groups[rarity]:
                    qty_text = f" (x{quantity})" if quantity > 1 else ""
                    characters_text += f"• {name}{qty_text}\n"
                
                if len(characters_text) > 900:  # Limite Discord
                    characters_text = characters_text[:900] + "..."
                
                embed.add_field(
                    name=f"{emoji} {rarity} ({len(rarity_groups[rarity])})",
                    value=characters_text,
                    inline=True
                )
        
        # Instructions
        embed.set_footer(text="Utilisez 🔍 Rechercher pour voir une carte spécifique")
        
        return embed
    
    @discord.ui.button(label='◀️', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        if self.page > 0:
            self.page -= 1
            embed = await self.create_list_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='▶️', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        max_pages = (len(self.characters) - 1) // self.items_per_page + 1 if self.characters else 1
        if self.page < max_pages - 1:
            self.page += 1
            embed = await self.create_list_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='🔍 Rechercher', style=discord.ButtonStyle.primary, row=0)
    async def search_from_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ouvrir la recherche depuis la liste"""
        await interaction.response.send_modal(CharacterSearchModal(self.bot, interaction.user.id))
    
    @discord.ui.button(label='🎴 Retour au Visualiseur', style=discord.ButtonStyle.success, row=1)
    async def back_to_viewer(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retourner au visualiseur principal"""
        await interaction.response.defer()
        
        view = CharacterViewerView(self.bot, interaction.user.id)
        embed = await create_character_viewer_embed(interaction.user)
        await interaction.edit_original_response(embed=embed, view=view)

class CharacterViewerSelectView(discord.ui.View):
    """Interface de sélection de personnage pour visualisation publique"""
    
    def __init__(self, bot, user_id: int, characters: List[tuple]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.characters = characters
        
        # Créer les options de sélection
        options = []
        for i, (char_id, name, anime, rarity) in enumerate(characters[:25]):  # Discord limit 25            
            options.append(discord.SelectOption(
                label=f"{name}",
                description=f"{anime} • {rarity}",
                value=str(i)
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="🌌 Choisissez un personnage à consulter...",
                options=options,
                min_values=1,
                max_values=1
            )
            select.callback = self.character_selected
            self.add_item(select)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Accessible à tous
    
    async def character_selected(self, interaction: discord.Interaction):
        """Traiter la sélection d'un personnage"""
        if not interaction.data or 'values' not in interaction.data:
            await interaction.response.send_message("❌ Erreur de sélection", ephemeral=True)
            return
            
        character_index = int(interaction.data['values'][0])
        char_id, name, anime, rarity = self.characters[character_index]
        
        # Récupérer les détails complets du personnage
        cursor = await self.bot.db.db.execute(
            "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE id = ?",
            (char_id,)
        )
        char_data = await cursor.fetchone()
        
        if not char_data:
            await interaction.response.send_message("❌ Personnage introuvable", ephemeral=True)
            return
        
        # Créer l'objet Character
        from core.models import Character
        character = Character(
            id=char_data[0],
            name=char_data[1],
            anime=char_data[2],
            rarity=char_data[3],
            value=char_data[4],
            image_url=char_data[5]
        )
        
        # Créer l'embed de la carte
        embed = await self.create_character_card_embed(character, interaction.user)
        
        # Créer une nouvelle vue avec bouton retour
        view = CharacterCardView(self.bot, self.user_id, character)
        
        await interaction.response.edit_message(embed=embed, view=view)

    async def create_character_card_embed(self, character, viewer_user) -> discord.Embed:
        """Créer l'embed de carte de personnage"""
        
        embed = discord.Embed(
            title=f"🌌 ═══════〔 {style_section('CARTE PERSONNAGE', '🎴')} 〕═══════ 🌌",
            description=f"```\n◆ Consultation par: {get_display_name(viewer_user)} ◆\n```",
            color=character.get_rarity_color()
        )
        
        # Informations principales du personnage
        embed.add_field(
            name=f"🌑 ═══〔 {character.get_rarity_emoji()} {character.name} 〕═══ 🌑",
            value=(f"```\n"
                   f"Anime: {character.anime}\n"
                   f"Rareté: {character.rarity}\n"
                   f"Valeur: {format_number(character.value)} Shadow Coins\n"
                   f"```"),
            inline=False
        )
        
        # Informations d'invocation
        rarity_chance = BotConfig.RARITY_WEIGHTS.get(character.rarity, 0)
        if character.rarity == "Evolve":
            invocation_info = "Craft Seulement"
            frequency_info = "Évolution requise"
        else:
            invocation_info = "Disponible"
            frequency_info = f"{rarity_chance}%"
            
        embed.add_field(
            name="📊 Informations d'Invocation",
            value=(f"```\n"
                   f"Invocation: {invocation_info}\n"
                   f"Fréquence: {frequency_info}\n"
                   f"Roll Standard: {'Non' if character.rarity == 'Evolve' else 'Oui'}\n"
                   f"```"),
            inline=True
        )
        
        # Statistiques de rareté
        embed.add_field(
            name="⭐ Statistiques de Rareté",
            value=(f"```\n"
                   f"Niveau: {character.rarity}\n"
                   f"Couleur: {character.get_rarity_emoji()}\n"
                   f"Premium: {'Oui' if character.rarity in ['Mythic', 'Titan', 'Fusion', 'Secret', 'Evolve'] else 'Non'}\n"
                   f"```"),
            inline=True
        )
        
        # Image du personnage si disponible
        if character.image_url and character.image_url.startswith(('http://', 'https://')):
            embed.set_image(url=character.image_url)
        
        embed.set_footer(
            text="Shadow Roll • Consultation Publique",
            icon_url=viewer_user.avatar.url if viewer_user.avatar else None
        )
        
        return embed

class CharacterCardView(discord.ui.View):
    """Vue pour la carte de personnage avec boutons de navigation"""
    
    def __init__(self, bot, user_id: int, character):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.character = character
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Accessible à tous
    
    @discord.ui.button(label='🔍 Autre Personnage', style=discord.ButtonStyle.primary, row=0)
    async def search_another(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rechercher un autre personnage"""
        await interaction.response.send_modal(CharacterSearchModal(self.bot, self.user_id))
    
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.secondary, row=0)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

class CharacterSearchModal(discord.ui.Modal):
    """Modal pour rechercher un personnage"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(title="🔍 Recherche de Personnage")
        self.bot = bot
        self.user_id = user_id
        
        self.search_input = discord.ui.TextInput(
            label="Nom du personnage",
            placeholder="Tapez le nom du personnage (ex: Naruto, Goku, Luffy...)",
            required=True,
            max_length=100
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        search_term = self.search_input.value.strip()
        
        # Rechercher uniquement les personnages possédés par le joueur
        cursor = await self.bot.db.db.execute("""
            SELECT DISTINCT c.id, c.name, c.anime, c.rarity 
            FROM characters c
            INNER JOIN inventory i ON c.id = i.character_id
            WHERE i.user_id = ? AND LOWER(c.name) LIKE LOWER(?) 
            ORDER BY 
                CASE c.rarity 
                    WHEN 'Secret' THEN 1
                    WHEN 'Evolve' THEN 2
                    WHEN 'Fusion' THEN 3
                    WHEN 'Titan' THEN 4
                    WHEN 'Mythic' THEN 5
                    WHEN 'Legendary' THEN 6
                    WHEN 'Epic' THEN 7
                    WHEN 'Rare' THEN 8
                    WHEN 'Common' THEN 9
                END,
                c.name
            LIMIT 25
        """, (self.user_id, f"%{search_term}%",))
        
        results = await cursor.fetchall()
        
        if not results:
            embed = discord.Embed(
                title="❌ Aucun Résultat",
                description=f"Aucun personnage possédé ne correspond à '{search_term}'\n\n*Seuls vos personnages possédés sont affichés pour éviter les spoilers*",
                color=0xff0000
            )
            if interaction.message and hasattr(interaction.message, 'id'):
                await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=None)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Créer la vue de sélection
        select_view = CharacterViewerSelectView(self.bot, self.user_id, results)
        
        embed = discord.Embed(
            title=f"🔍 ═══════〔 {style_section('RÉSULTATS DE RECHERCHE', '🌌')} 〕═══════ 🔍",
            description=f"```\n◆ Recherche: {search_term} ◆\n◆ Résultats trouvés: {len(results)} ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        if interaction.message and hasattr(interaction.message, 'id'):
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=select_view)
        else:
            await interaction.followup.send(embed=embed, view=select_view, ephemeral=True)

class CharacterViewerView(discord.ui.View):
    """Vue principale du système de visualisation de cartes"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True  # Accessible à tous
    
    @discord.ui.button(label='📋 Liste de Mes Personnages', style=discord.ButtonStyle.success, row=0)
    async def list_owned_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher la liste des personnages possédés"""
        await interaction.response.defer()
        
        # Récupérer tous les personnages possédés
        cursor = await self.bot.db.db.execute("""
            SELECT DISTINCT c.id, c.name, c.anime, c.rarity, COUNT(i.id) as quantity
            FROM characters c
            INNER JOIN inventory i ON c.id = i.character_id
            WHERE i.user_id = ?
            GROUP BY c.id, c.name, c.anime, c.rarity
            ORDER BY 
                CASE c.rarity 
                    WHEN 'Secret' THEN 1
                    WHEN 'Evolve' THEN 2
                    WHEN 'Fusion' THEN 3
                    WHEN 'Titan' THEN 4
                    WHEN 'Mythic' THEN 5
                    WHEN 'Legendary' THEN 6
                    WHEN 'Epic' THEN 7
                    WHEN 'Rare' THEN 8
                    WHEN 'Common' THEN 9
                END,
                c.name
        """, (interaction.user.id,))
        
        characters = await cursor.fetchall()
        
        if not characters:
            embed = discord.Embed(
                title="📋 Votre Collection",
                description="Vous ne possédez aucun personnage pour le moment.\n\nUtilisez le menu principal pour invoquer vos premiers personnages !",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed, view=CharacterListView(self.bot, interaction.user.id, []))
            return
        
        # Créer la vue avec pagination
        list_view = CharacterListView(self.bot, interaction.user.id, characters)
        embed = await list_view.create_list_embed()
        await interaction.edit_original_response(embed=embed, view=list_view)
    
    @discord.ui.button(label='🔍 Rechercher Personnage', style=discord.ButtonStyle.primary, row=0)
    async def search_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ouvrir la recherche de personnage"""
        await interaction.response.send_modal(CharacterSearchModal(self.bot, interaction.user.id))
    
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.danger, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

async def create_character_viewer_embed(user) -> discord.Embed:
    """Créer l'embed principal du visualiseur de cartes"""
    
    embed = discord.Embed(
        title=f"🎴 ═══════〔 {style_section('VISUALISEUR DE CARTES', '🌌')} 〕═══════ 🎴",
        description=f"```\n◆ Consulteur: {get_display_name(user)} ◆\n◆ Affichage: Uniquement vos personnages possédés ◆\n```",
        color=BotConfig.RARITY_COLORS['Epic']
    )
    
    embed.add_field(
        name="🔍 Recherche de Personnages",
        value=(f"```\n"
               f"• Recherche par nom\n"
               f"• Seulement vos personnages\n"
               f"• Filtrage automatique\n"
               f"```"),
        inline=True
    )
    
    embed.add_field(
        name="🎴 Cartes Détaillées",
        value=(f"```\n"
               f"• Statistiques complètes\n"
               f"• Images des personnages\n"
               f"• Informations d'invocation\n"
               f"```"),
        inline=True
    )
    
    embed.add_field(
        name="🌌 Navigation",
        value=(f"```\n"
               f"• Interface simple\n"
               f"• Retour au menu\n"
               f"• Accessible à tous\n"
               f"```"),
        inline=False
    )
    
    embed.set_footer(
        text="Shadow Roll • Visualiseur Public",
        icon_url=user.avatar.url if user.avatar else None
    )
    
    return embed

async def setup_character_viewer_commands(bot):
    """Setup character viewer commands"""
    
    @bot.tree.command(name="voir", description="🎴 Visualiser les cartes de personnages (accessible à tous)")
    async def view_character_cards(interaction: discord.Interaction):
        """Commande slash pour visualiser les cartes"""
        view = CharacterViewerView(bot, interaction.user.id)
        embed = await create_character_viewer_embed(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)
    
    logger.info("Character viewer commands setup completed")