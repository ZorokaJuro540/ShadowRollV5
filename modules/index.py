"""
Index System for Shadow Roll Bot
Comprehensive character database browser for all users
"""
import discord
import logging
from typing import List, Dict, Optional
from core.config import BotConfig
from modules.utils import get_display_name, format_number

logger = logging.getLogger(__name__)


class IndexView(discord.ui.View):
    """Main index view for browsing all characters and series"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 1
        self.view_mode = "series"  # series, characters, rarity
        self.search_query = ""
        self.selected_anime = ""
        self.selected_rarity = ""
        self.items_per_page = 10
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_index_embed(self) -> discord.Embed:
        """Create the main index embed"""
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"User {self.user_id}"
        
        if self.view_mode == "series":
            return await self.create_series_index_embed(username)
        elif self.view_mode == "characters":
            return await self.create_characters_index_embed(username)
        elif self.view_mode == "rarity":
            return await self.create_rarity_index_embed(username)
        else:
            return await self.create_main_index_embed(username)
    
    async def create_main_index_embed(self, username: str) -> discord.Embed:
        """Create main index overview"""
        embed = discord.Embed(
            description=f"""🌌 ═══════〔 I N D E X   S H A D O W   R O L L 〕═══════ 🌌
◆ Base de données complète • {username} ◆

〔 Exploration 〕═══ 📚
📖 Liste Complète  ◆ Tous les personnages
🎭 Par Séries      ◆ Groupés par anime
💎 Par Rareté      ◆ Classés par niveau
🔍 Recherche       ◆ Trouver un personnage""",
            color=0x9932cc
        )
        
        # Get statistics
        async with self.bot.db.db.execute("SELECT COUNT(*) FROM characters") as cursor:
            total_chars = (await cursor.fetchone())[0]
            
        async with self.bot.db.db.execute("SELECT COUNT(DISTINCT anime) FROM characters WHERE anime IS NOT NULL") as cursor:
            total_series = (await cursor.fetchone())[0]
            
        async with self.bot.db.db.execute("SELECT COUNT(DISTINCT rarity) FROM characters") as cursor:
            total_rarities = (await cursor.fetchone())[0]
        
        embed.add_field(
            name="📊 ═══〔 Statistiques Globales 〕═══ 📊",
            value=f"{total_chars} personnages total\n{total_series} séries d'anime\n{total_rarities} niveaux de rareté",
            inline=False
        )
        
        embed.set_footer(text=f"Shadow Roll Index • {username}")
        return embed
    
    async def create_series_index_embed(self, username: str) -> discord.Embed:
        """Create series index embed"""
        embed = discord.Embed(
            description=f"""🌌 ═══════〔 I N D E X   D E S   S É R I E S 〕═══════ 🌌
◆ Toutes les séries d'anime • Page {self.current_page} ◆

〔 Collections par Anime 〕═══ 🎭""",
            color=0x9932cc
        )
        
        # Get series data with character counts
        async with self.bot.db.db.execute("""
            SELECT anime, COUNT(*) as count 
            FROM characters 
            WHERE anime IS NOT NULL AND anime != ''
            GROUP BY anime 
            ORDER BY count DESC, anime
        """) as cursor:
            all_series = await cursor.fetchall()
        
        # Pagination
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_series = all_series[start_idx:end_idx]
        total_pages = max(1, (len(all_series) + self.items_per_page - 1) // self.items_per_page)
        
        if page_series:
            series_list = ""
            for i, (anime, count) in enumerate(page_series, start_idx + 1):
                series_list += f"{i:2d}. **{anime}**: {count} personnages\n"
            
            embed.add_field(
                name=f"🎭 ═══〔 Séries {start_idx + 1}-{min(end_idx, len(all_series))} sur {len(all_series)} 〕═══ 🎭",
                value=series_list,
                inline=False
            )
        else:
            embed.add_field(
                name="❌ Aucune série",
                value="Aucune série trouvée",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page}/{total_pages} • Shadow Roll Index • {username}")
        return embed
    
    async def create_characters_index_embed(self, username: str) -> discord.Embed:
        """Create characters index embed"""
        title_suffix = ""
        where_clause = "WHERE 1=1"
        params = []
        
        if self.selected_anime:
            title_suffix = f" - {self.selected_anime}"
            where_clause += " AND anime = ?"
            params.append(self.selected_anime)
            
        if self.selected_rarity:
            title_suffix += f" ({self.selected_rarity})"
            where_clause += " AND rarity = ?"
            params.append(self.selected_rarity)
            
        if self.search_query:
            title_suffix += f" - Recherche: {self.search_query}"
            where_clause += " AND (name LIKE ? OR anime LIKE ?)"
            params.extend([f"%{self.search_query}%", f"%{self.search_query}%"])
        
        embed = discord.Embed(
            description=f"""🌌 ═══════〔 I N D E X   P E R S O N N A G E S{title_suffix} 〕═══════ 🌌
◆ Base de données complète • Page {self.current_page} ◆

〔 Personnages par Rareté et Prix 〕═══ 👥""",
            color=0x9932cc
        )
        
        # Get characters data with custom rarity ordering
        query = f"""
            SELECT name, anime, rarity, value 
            FROM characters 
            {where_clause}
            ORDER BY 
                CASE rarity 
                    WHEN 'Secret' THEN 1
                    WHEN 'Evolve' THEN 2
                    WHEN 'Fusion' THEN 3
                    WHEN 'Titan' THEN 4
                    WHEN 'Mythic' THEN 5
                    WHEN 'Legendary' THEN 6
                    WHEN 'Epic' THEN 7
                    WHEN 'Rare' THEN 8
                    WHEN 'Common' THEN 9
                    ELSE 10
                END,
                value DESC, 
                name
        """
        
        async with self.bot.db.db.execute(query, params) as cursor:
            all_characters = await cursor.fetchall()
        
        # Pagination
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_characters = all_characters[start_idx:end_idx]
        total_pages = max(1, (len(all_characters) + self.items_per_page - 1) // self.items_per_page)
        
        if page_characters:
            char_list = ""
            for name, anime, rarity, value in page_characters:
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                char_list += f"{rarity_emoji} **{name}** ({anime})\n  💰 {format_number(value)} SC • **{rarity}**\n"
            
            embed.add_field(
                name=f"🎭 ═══〔 Personnages {start_idx + 1}-{min(end_idx, len(all_characters))} sur {len(all_characters)} 〕═══ 🎭",
                value=char_list,
                inline=False
            )
        else:
            embed.add_field(
                name="❌ Aucun personnage",
                value="Aucun personnage trouvé avec ces critères",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page}/{total_pages} • Shadow Roll Index • {username}")
        return embed
    
    async def create_rarity_index_embed(self, username: str) -> discord.Embed:
        """Create rarity index embed"""
        embed = discord.Embed(
            description=f"""🌌 ═══════〔 I N D E X   D E S   R A R E T É S 〕═══════ 🌌
◆ Classification par rareté • Page {self.current_page} ◆

〔 Répartition par Niveau 〕═══ 💎""",
            color=0x9932cc
        )
        
        # Get rarity statistics
        async with self.bot.db.db.execute("""
            SELECT rarity, COUNT(*) as count, AVG(value) as avg_value, MIN(value) as min_value, MAX(value) as max_value
            FROM characters 
            GROUP BY rarity 
            ORDER BY AVG(value) DESC
        """) as cursor:
            rarity_stats = await cursor.fetchall()
        
        if rarity_stats:
            rarity_list = ""
            for rarity, count, avg_value, min_value, max_value in rarity_stats:
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                rarity_list += f"{rarity_emoji} **{rarity}**: {count} personnages\n"
                rarity_list += f"  💰 {format_number(int(avg_value))} SC (moyenne)\n"
                rarity_list += f"  📊 {format_number(min_value)} - {format_number(max_value)} SC\n\n"
            
            embed.add_field(
                name="🏆 ═══〔 Statistiques par Rareté 〕═══ 🏆",
                value=rarity_list,
                inline=False
            )
        
        embed.set_footer(text=f"Shadow Roll Index • {username}")
        return embed
    
    # Navigation buttons
    @discord.ui.button(label='📺 Séries', style=discord.ButtonStyle.primary, row=0)
    async def series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "series"
        self.current_page = 1
        self.selected_anime = ""
        self.selected_rarity = ""
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='👥 Personnages', style=discord.ButtonStyle.primary, row=0)
    async def characters_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "characters"
        self.current_page = 1
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='💎 Raretés', style=discord.ButtonStyle.primary, row=0)
    async def rarity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "rarity"
        self.current_page = 1
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🔍 Recherche', style=discord.ButtonStyle.secondary, row=0)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = IndexSearchModal(self)
        await interaction.response.send_modal(modal)
    
    # Page navigation
    @discord.ui.button(label='◀️', style=discord.ButtonStyle.secondary, row=1)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='▶️', style=discord.ButtonStyle.secondary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if there's a next page
        if self.view_mode == "series":
            async with self.bot.db.db.execute("SELECT COUNT(DISTINCT anime) FROM characters WHERE anime IS NOT NULL") as cursor:
                total_items = (await cursor.fetchone())[0]
        elif self.view_mode == "characters":
            where_clause = "WHERE 1=1"
            params = []
            if self.selected_anime:
                where_clause += " AND anime = ?"
                params.append(self.selected_anime)
            if self.selected_rarity:
                where_clause += " AND rarity = ?"
                params.append(self.selected_rarity)
            if self.search_query:
                where_clause += " AND (name LIKE ? OR anime LIKE ?)"
                params.extend([f"%{self.search_query}%", f"%{self.search_query}%"])
            
            async with self.bot.db.db.execute(f"SELECT COUNT(*) FROM characters {where_clause}", params) as cursor:
                total_items = (await cursor.fetchone())[0]
        else:
            total_items = 0
        
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label='🎯 Sélectionner Série', style=discord.ButtonStyle.success, row=1)
    async def select_series_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SelectSeriesModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='💎 Sélectionner Rareté', style=discord.ButtonStyle.success, row=1)
    async def select_rarity_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = SelectRarityModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='🔄 Réinitialiser', style=discord.ButtonStyle.secondary, row=2)
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.search_query = ""
        self.selected_anime = ""
        self.selected_rarity = ""
        self.current_page = 1
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class IndexSearchModal(discord.ui.Modal, title='🔍 Rechercher dans l\'Index'):
    """Modal for searching characters"""
    
    def __init__(self, index_view):
        super().__init__()
        self.index_view = index_view
    
    search_input = discord.ui.TextInput(
        label='Nom du personnage ou anime',
        placeholder='Tapez le nom du personnage ou de l\'anime...',
        required=True,
        max_length=100
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.index_view.search_query = self.search_input.value.strip()
        self.index_view.current_page = 1
        self.index_view.view_mode = "characters"
        await interaction.response.defer()
        embed = await self.index_view.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self.index_view)


class SelectSeriesModal(discord.ui.Modal, title='🎯 Sélectionner une Série'):
    """Modal for selecting anime series"""
    
    def __init__(self, index_view):
        super().__init__()
        self.index_view = index_view
    
    series_input = discord.ui.TextInput(
        label='Nom de la série anime',
        placeholder='Ex: Naruto, One Piece, Dragon Ball...',
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        series_name = self.series_input.value.strip()
        
        # Verify series exists
        async with self.index_view.bot.db.db.execute(
            "SELECT COUNT(*) FROM characters WHERE anime = ?", (series_name,)
        ) as cursor:
            count = (await cursor.fetchone())[0]
        
        if count > 0:
            self.index_view.selected_anime = series_name
            self.index_view.current_page = 1
            self.index_view.view_mode = "characters"
            await interaction.response.defer()
            embed = await self.index_view.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self.index_view)
        else:
            await interaction.response.send_message(
                f"❌ Aucune série trouvée pour '{series_name}'", ephemeral=True
            )


class SelectRarityModal(discord.ui.Modal, title='💎 Sélectionner une Rareté'):
    """Modal for selecting rarity"""
    
    def __init__(self, index_view):
        super().__init__()
        self.index_view = index_view
    
    rarity_input = discord.ui.TextInput(
        label='Niveau de rareté',
        placeholder='Ex: Mythic, Legendary, Epic...',
        required=True,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        rarity_name = self.rarity_input.value.strip()
        
        # Verify rarity exists
        async with self.index_view.bot.db.db.execute(
            "SELECT COUNT(*) FROM characters WHERE rarity = ?", (rarity_name,)
        ) as cursor:
            count = (await cursor.fetchone())[0]
        
        if count > 0:
            self.index_view.selected_rarity = rarity_name
            self.index_view.current_page = 1
            self.index_view.view_mode = "characters"
            await interaction.response.defer()
            embed = await self.index_view.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self.index_view)
        else:
            await interaction.response.send_message(
                f"❌ Aucune rareté trouvée pour '{rarity_name}'", ephemeral=True
            )