"""
Shadow Roll Menu System - Button-based navigation
Complete menu system with Shadow theme and French interface
"""
import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import random

from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.achievements import AchievementManager
from modules.text_styling import style_main_title, style_section, style_username, style_character, style_anime, style_rarity

logger = logging.getLogger(__name__)


async def create_main_menu_embed(bot, user_id: int) -> discord.Embed:
    """Create main menu embed for Shadow Roll bot - standalone function"""
    try:
        user = bot.get_user(user_id)
        username = get_display_name(user) if user else f"User {user_id}"
        player = await bot.db.get_or_create_player(user_id, username)

        # Créer le nouveau style de menu élégant
        embed = discord.Embed(
            description=f"""🌌 ═══════〔 S H A D O W   R O L L 〕═══════ 🌌
◆ Bienvenue dans les ténèbres, {username} ◆
🪙 {format_number(player.coins)} Shadow Coins disponibles

〔 Navigation 〕═══ 🌑
👤 Profil      ◆ Vos statistiques
🎲 Invocation  ◆ Invoquer des personnages
🎒 Collection  ◆ Voir vos personnages
🔮 Craft       ◆ Évolution des personnages
🔄 Trade       ◆ Échanger avec d'autres joueurs
🎁 Bénédiction ◆ Récompense quotidienne
🛒 Vente       ◆ Revendre vos personnages
🎖️ Succès      ◆ Récompenses d'exploits
🏆 Classement  ◆ Tableau des maîtres
🎯 Séries      ◆ Collections par anime
❓ Guide       ◆ Aide et informations
📚 Index       ◆ Base de données complète
🎴 Voir Carte  ◆ Explorer les personnages""",
            color=0x9932cc
        )
        
        # Footer avec seulement le nom du joueur
        embed.set_footer(
            text=f"Shadow Roll • {username}",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        return embed

    except Exception as e:
        logger.error(f"Error creating main menu embed: {e}")
        # Embed de fallback simple mais stylé
        return discord.Embed(
            title="🌑 SHADOW ROLL",
            description="```ansi\n\u001b[1;36mBienvenue dans les ténèbres...\u001b[0m\n```",
            color=0x9932cc
        )


class SearchModal(discord.ui.Modal, title='🔍 Rechercher un Personnage'):
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
        self.index_view.view_mode = "characters"  # Switch to characters view when searching
        await interaction.response.defer()
        embed = await self.index_view.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self.index_view)


class AnimeFilterModal(discord.ui.Modal, title='🎭 Filtrer par Série'):
    def __init__(self, index_view):
        super().__init__()
        self.index_view = index_view

    anime_input = discord.ui.TextInput(
        label='Nom de la série anime',
        placeholder='Ex: Naruto, One Piece, Dragon Ball Z...',
        required=True,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.index_view.anime_filter = self.anime_input.value.strip()
        self.index_view.current_page = 1
        self.index_view.view_mode = "characters"  # Switch to characters view when filtering
        await interaction.response.defer()
        embed = await self.index_view.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self.index_view)


class RarityFilterView(discord.ui.View):
    """View for selecting rarity filter"""
    
    def __init__(self, index_view):
        super().__init__(timeout=60)
        self.index_view = index_view
        
        # Add buttons for each rarity
        rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Evolve', 'Titan', 'Fusion', 'Secret']
        for rarity in rarities:
            emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
            button = discord.ui.Button(
                label=f"{emoji} {rarity}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"rarity_{rarity}"
            )
            button.callback = self.create_rarity_callback(rarity)
            self.add_item(button)

    def create_rarity_callback(self, rarity):
        async def callback(interaction: discord.Interaction):
            self.index_view.rarity_filter = rarity
            self.index_view.current_page = 1
            self.index_view.view_mode = "characters"  # Switch to characters view when filtering
            await interaction.response.defer()
            embed = await self.index_view.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self.index_view)
        return callback


class ShadowMenuView(discord.ui.View):
    """Main Shadow Roll menu with button navigation"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)  # 5 minute timeout
        self.bot = bot
        self.user_id = user_id

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        """Ensure only the command user can interact"""
        return interaction.user.id == self.user_id

    # All buttons in green (success style) with icons only
    @discord.ui.button(label='👤 Profil',
                       style=discord.ButtonStyle.success,
                       row=0)
    async def profile_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        await interaction.response.defer()
        view = ProfileView(self.bot, self.user_id)
        embed = await view.create_profile_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎲 Invocation',
                       style=discord.ButtonStyle.success,
                       row=0)
    async def roll_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        view = RollView(self.bot, self.user_id)
        embed, success = await view.perform_roll()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎒 Backpack',
                       style=discord.ButtonStyle.success,
                       row=0)
    async def inventory_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        await interaction.response.defer()
        from modules.backpack import BackpackView
        view = BackpackView(self.bot, self.user_id)
        embed = await view.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🔮 Craft',
                       style=discord.ButtonStyle.success,
                       row=1)
    async def craft_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.craft_system import CraftView
        view = CraftView(self.bot, self.user_id)
        embed = await view.create_craft_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🔄 Trade',
                       style=discord.ButtonStyle.success,
                       row=1)
    async def trade_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.trade import TradeMenuView
        view = TradeMenuView(self.bot, self.user_id)
        embed = await view.create_trade_menu_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎁 Bénédiction',
                       style=discord.ButtonStyle.success,
                       row=1)
    async def daily_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        view = DailyView(self.bot, self.user_id)
        embed = await view.claim_daily_reward()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🛒 Shop',
                       style=discord.ButtonStyle.success,
                       row=1)
    async def shop_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        try:
            from modules.shop_system_fixed import create_fixed_shop_view
            view = await create_fixed_shop_view(self.bot, self.user_id)
            embed = await view.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error opening fixed shop: {e}")
            # Fallback to unified shop
            from modules.unified_shop import UnifiedShopView
            view = UnifiedShopView(self.bot, self.user_id)
            embed = await view.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎖️ Succès',
                       style=discord.ButtonStyle.success,
                       row=2)
    async def achievements_button(self, interaction: discord.Interaction,
                                  button: discord.ui.Button):
        await interaction.response.defer()
        view = AchievementsView(self.bot, self.user_id)
        embed = await view.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🏆 Classement',
                       style=discord.ButtonStyle.success,
                       row=2)
    async def rankings_button(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        await interaction.response.defer()
        view = RankingsView(self.bot, self.user_id)
        embed = await view.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎯 Séries',
                       style=discord.ButtonStyle.success,
                       row=2)
    async def sets_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        from modules.sets import SetsView
        view = SetsView(self.bot, self.user_id)
        embed = await view.create_sets_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='❓ Guide',
                       style=discord.ButtonStyle.success,
                       row=2)
    async def help_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        from modules.guide import GuideView
        view = GuideView(self.bot, self.user_id, page=1)
        embed = await view.create_guide_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='📚 Index',
                       style=discord.ButtonStyle.success,
                       row=3)
    async def index_button(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        await interaction.response.defer()
        from modules.index import IndexView
        view = IndexView(self.bot, interaction.user.id)
        embed = await view.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎴 Voir Carte',
                       style=discord.ButtonStyle.success,
                       row=3)
    async def view_character_button(self, interaction: discord.Interaction,
                                    button: discord.ui.Button):
        await interaction.response.defer()
        from modules.character_viewer import CharacterViewerView, create_character_viewer_embed
        view = CharacterViewerView(self.bot, interaction.user.id)
        embed = await create_character_viewer_embed(interaction.user)
        await interaction.edit_original_response(embed=embed, view=view)




class ProfileView(discord.ui.View):
    """Profile display view"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_profile_embed(self) -> discord.Embed:
        """Create profile embed with Shadow theme"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(
                user) if user else f"User {self.user_id}"

            await self.bot.db.sync_player_stats(self.user_id)
            player = await self.bot.db.get_or_create_player(
                self.user_id, username)
            inventory_stats = await self.bot.db.get_inventory_stats(
                self.user_id)

            # Get selected title
            selected_title = await self.bot.db.get_selected_title(self.user_id)
            title_display = ""
            if selected_title:
                title_display = f"{selected_title['icon']} {selected_title['display_name']}\n"
            else:
                title_display = "◆ Maître des Ténèbres ◆\n"

            embed = discord.Embed(
                title=style_section("PROFIL DE L'OMBRE", "🌌"),
                description=f"```\n{title_display}{style_username(username)}\n```",
                color=BotConfig.RARITY_COLORS['Epic'])

            embed.add_field(
                name=style_section("RICHESSE DES OMBRES", "🪙"),
                value=f"```\n{format_number(player.coins)} Shadow Coins\n```",
                inline=True)

            embed.add_field(
                name=style_section("INVOCATIONS", "🎲"),
                value=f"```\n{format_number(player.total_rerolls)} total\n```",
                inline=True)

            embed.add_field(
                name=style_section("COLLECTION", "🎒"),
                value=
                f"```\n{inventory_stats.get('unique_characters', 0)} uniques\n{inventory_stats.get('total_characters', 0)} total\n```",
                inline=True)

            # Rarity breakdown
            rarity_counts = inventory_stats.get('rarity_counts', {})
            rarity_text = ""
            for rarity in ['Secret', 'Fusion', 'Titan', 'Evolve', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                count = rarity_counts.get(rarity, 0)
                emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                if count > 0:
                    rarity_text += f"{emoji} {rarity}: {count}\n"

            if not rarity_text:
                rarity_text = "Aucun personnage"

            embed.add_field(name=style_section("RÉPARTITION PAR RARETÉ", "🌫️"),
                            value=f"```\n{rarity_text}```",
                            inline=False)

            # Show equipped characters and bonuses
            equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
            if equipped_chars:
                equipped_text = ""
                for char in equipped_chars[:3]:  # Show max 3
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    equipped_text += f"{rarity_emoji} {char['name']}\n"
                
                # Calculate total bonuses
                bonuses = await self.bot.db.calculate_equipment_bonuses(self.user_id)
                bonus_text = ""
                if bonuses.get('rarity_boost', 0) > 0:
                    bonus_text += f"🎲 +{bonuses['rarity_boost']:.0f}% chances\n"
                if bonuses.get('coin_boost', 0) > 0:
                    bonus_text += f"🪙 +{bonuses['coin_boost']:.0f}% coins\n"

                embed.add_field(
                    name=style_section("ÉQUIPEMENT ACTIF", "⚔️"),
                    value=f"```\n{equipped_text}```\n{bonus_text}",
                    inline=False
                )

            embed.set_footer(
                text=f"Shadow Roll • {username}",
                icon_url=user.avatar.url if user and user.avatar else None)

            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating profile embed: {e}")
            return discord.Embed(title="❌ Erreur",
                                 description="Impossible de charger le profil",
                                 color=0xff0000)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.primary,
                       row=0)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

    async def create_main_menu_embed(self) -> discord.Embed:
        """Create main menu embed"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(
                user) if user else f"User {self.user_id}"
            player = await self.bot.db.get_or_create_player(
                self.user_id, username)

            embed = discord.Embed(
                title="🌌 ═══════〔 S H A D O W   R O L L 〕═══════ 🌌",
                description=
                f"```\n◆ Bienvenue dans les ténèbres, {username} ◆\n{format_number(player.coins)} Shadow Coins disponibles\n```",
                color=BotConfig.RARITY_COLORS['Epic'])

            embed.add_field(
                name="🌑 ═══〔 Navigation 〕═══ 🌑",
                value=("```\n"
                       "👤 Profil      ◆ Vos statistiques\n"
                       "🎲 Invocation  ◆ Invoquer des personnages\n"
                       "🧪 Recherche   ◆ Traquer un personnage\n"
                       "🎒 Collection  ◆ Voir vos personnages\n"
                       "🔮 Craft       ◆ Évolution des personnages\n"
                       "🎁 Bénédiction ◆ Récompense quotidienne\n"
                       "🛒 Vente        ◆ Revendre vos personnages\n"
                       "🎖️ Succès      ◆ Récompenses d’exploits\n"
                       "🏆 Classement  ◆ Tableau des maîtres\n"
                       "❓ Guide       ◆ Aide et informations\n"
                       "```"),
                inline=False)

            embed.set_footer(
                text=f"Shadow Roll • Utilisez les boutons pour naviguer • {username}",
                icon_url=user.avatar.url if user and user.avatar else None)

            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating main menu embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger le menu principal",
                color=0xff0000)


class RollView(discord.ui.View):
    """Character rolling view"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def perform_roll(self) -> tuple[discord.Embed, bool]:
        """Perform a character roll"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(
                user) if user else f"User {self.user_id}"
            player = await self.bot.db.get_or_create_player(
                self.user_id, username)

            # Check if user is banned
            if await self.bot.db.is_banned(self.user_id):
                return discord.Embed(title="❌ Accès Refusé",
                                     description="Vous êtes banni du bot.",
                                     color=0xff0000), False

            # Check cooldown - use the last character's rarity if available
            from modules.utils import get_cooldown_remaining, get_rarity_cooldown
            if player.last_reroll:
                # Get the last rolled character's rarity to determine cooldown
                cursor = await self.bot.db.db.execute("""
                    SELECT c.rarity FROM inventory i
                    JOIN characters c ON i.character_id = c.id
                    WHERE i.user_id = ?
                    ORDER BY i.id DESC LIMIT 1
                """, (self.user_id,))
                last_char = await cursor.fetchone()
                
                if last_char:
                    last_rarity = last_char[0]
                    cooldown_time = get_rarity_cooldown(last_rarity)
                else:
                    cooldown_time = BotConfig.REROLL_COOLDOWN
                
                cooldown_remaining = get_cooldown_remaining(
                    player.last_reroll, int(cooldown_time))
                if cooldown_remaining > 0:
                    return discord.Embed(
                        title="⏰ Invocation en Recharge",
                        description=
                        f"Réessayez dans {cooldown_remaining:.1f} secondes",
                        color=0xff9900), False

            # Check coins
            if player.coins < BotConfig.REROLL_COST:
                return discord.Embed(
                    title="❌ Fonds Insuffisants",
                    description=
                    f"Il vous faut {BotConfig.REROLL_COST} {BotConfig.CURRENCY_EMOJI} mais vous n'avez que {player.coins}",
                    color=0xff0000), False

            # Check for active hunt and priority target
            hunt_system = getattr(self.bot, 'hunt_system', None)
            hunt_character = None
            hunt_completed = False
            
            if hunt_system:
                # Check if hunt progress grants the target character
                hunt_target = await hunt_system.get_hunt_bonus_character(self.user_id)
                if hunt_target:
                    hunt_character = hunt_target
                    hunt_completed = True
                    await hunt_system.complete_hunt(self.user_id)
            
            # Determine which character to award
            if hunt_character and hunt_completed:
                # Award the hunt target character
                character = hunt_character
            else:
                # Normal roll with luck potion effects
                character = await self.bot.db.get_character_by_rarity_weight(self.user_id, self.bot)
                if not character:
                    return discord.Embed(
                        title="❌ Erreur d'Invocation",
                        description="Impossible d'invoquer un personnage",
                        color=0xff0000), False

            # Ensure character is a proper Character object
            if isinstance(character, dict):
                from core.models import Character
                character = Character(
                    id=character['id'],
                    name=character['name'],
                    anime=character['anime'],
                    rarity=character['rarity'],
                    value=character['value'],
                    image_url=character.get('image_url', '')
                )
            
            # Add to inventory and subtract roll cost
            await self.bot.db.add_character_to_inventory(
                self.user_id, character.id)
            await self.bot.db.subtract_player_coins(self.user_id, BotConfig.REROLL_COST)
            new_coins = player.coins - BotConfig.REROLL_COST
            
            # Process hunt progress (if not completed)
            hunt_progress_info = None
            if hunt_system and not hunt_completed:
                hunt_progress_info = await hunt_system.process_hunt_progress(self.user_id)
            
            # Use rarity-based cooldown
            from modules.utils import get_rarity_cooldown
            cooldown_duration = get_rarity_cooldown(character.rarity)
            current_time = datetime.now().isoformat()
            await self.bot.db.update_player_reroll_stats(
                self.user_id, current_time)
            
            # Check for newly completed sets
            await self.bot.db.check_and_complete_sets(self.user_id)

            # Achievement system temporarily disabled for stability
            new_achievements = []

            # Create result embed with styled titles
            if character.rarity in ["Legendary", "Mythic"]:
                # Special title for rare pulls
                if character.rarity == "Legendary":
                    title = style_section("INVOCATION LÉGENDAIRE", "🔶⚡")
                else:  # Mythic
                    title = style_section("INVOCATION MYTHIQUE", "🌠💥")
            else:
                title = style_section("INVOCATION", "🌌")
                
            embed = discord.Embed(
                title=title,
                description=f"```\n◆ Vous avez invoqué... ◆\n```",
                color=character.get_rarity_color())

            # Left column: Character info with styled text and colored rarity
            rarity_colored = f"```ansi\n{style_rarity(character.rarity)}\n```"
            embed.add_field(
                name=f"{character.get_rarity_emoji()} {style_character(character.name)}",
                value=f"**Anime:** {style_anime(character.anime)}\n**Rareté:** {rarity_colored}**Valeur:** {format_number(character.value)} pièces",
                inline=True)

            # Get ALL possible bonuses for complete display
            luck_bonuses = await self.bot.db.calculate_luck_bonus(self.user_id)
            set_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
            equipment_bonuses = await self.bot.db.calculate_equipment_bonuses(self.user_id)
            title_bonuses = await self.bot.db.get_title_bonuses(self.user_id)
            
            # Calculate bonus values
            rarity_bonus = equipment_bonuses.get('rarity_boost', 0)
            coin_bonus = equipment_bonuses.get('coin_boost', 0)
            series_rarity = 0
            series_coin = 0
            if set_bonuses:
                if set_bonuses.get('rarity_boost', 0) > 0:
                    series_rarity = set_bonuses['rarity_boost'] * 100
                if set_bonuses.get('coin_boost', 0) > 0:
                    series_coin = (set_bonuses['coin_boost'] - 1) * 100
            potion_total = luck_bonuses.get('total', 0)
            
            # Calculate title bonuses
            title_rarity = title_bonuses.get('rarity_boost', 0) * 100 if title_bonuses.get('rarity_boost', 0) > 0 else 0
            title_coin = (title_bonuses.get('coin_boost', 1.0) - 1) * 100 if title_bonuses.get('coin_boost', 1.0) > 1 else 0
            
            total_rarity_bonus = rarity_bonus + series_rarity + potion_total + title_rarity
            total_coin_bonus = coin_bonus + series_coin + title_coin

            # Right column: Bonus info (compact)
            bonus_text = (f"⚔️ **ÉQUIP:** 🎲+{rarity_bonus:.1f}% 🪙+{coin_bonus:.1f}%\n"
                         f"🎖️ **SÉRIES:** 🎲+{series_rarity:.1f}% 🪙+{series_coin:.1f}%\n"
                         f"👑 **TITRES:** 🎲+{title_rarity:.1f}% 🪙+{title_coin:.1f}%\n"
                         f"🍀 **POTIONS:** 🎯+{potion_total}%\n"
                         f"🔥 **TOTAL:** 🎲+{total_rarity_bonus:.1f}% 🪙+{total_coin_bonus:.1f}%")
            
            embed.add_field(
                name=style_section("BONUS ACTIFS", "🎯"),
                value=bonus_text,
                inline=True)

            # Full width row: Coins remaining
            embed.add_field(
                name="🪙 Solde Restant",
                value=f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                inline=False)

            if character.image_url and character.image_url.startswith(('http://', 'https://')):
                embed.set_image(url=character.image_url)

            if new_achievements:
                achievement_text = ""
                for ach in new_achievements[:3]:
                    achievement_text += f"🏆 **{ach.name}** débloqué!\n"
                    if ach.reward_coins > 0:
                        achievement_text += f"   +{ach.reward_coins} pièces bonus!\n"

                embed.add_field(name="🎊 Succès Débloqués",
                                value=achievement_text,
                                inline=False)

            embed.set_footer(text="Shadow Roll • Shadow Roll Bot")

            return embed, True

        except Exception as e:
            pass
            logger.error(f"Error performing roll: {e}")
            return discord.Embed(
                title="❌ Erreur d'Invocation",
                description="Une erreur s'est produite lors de l'invocation",
                color=0xff0000), False

    @discord.ui.button(label='🎲 Invoquer Encore',
                       style=discord.ButtonStyle.primary,
                       row=0)
    async def roll_again(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        await interaction.response.defer()
        embed, success = await self.perform_roll()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class CollectionView(discord.ui.View):
    """Character collection view with pagination"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_collection_embed(self) -> discord.Embed:
        """Create collection embed with pagination"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(
                user) if user else f"User {self.user_id}"

            inventory = await self.bot.db.get_player_inventory(
                self.user_id,
                page=self.current_page,
                limit=BotConfig.INVENTORY_ITEMS_PER_PAGE)
            inventory_stats = await self.bot.db.get_inventory_stats(
                self.user_id)

            embed = discord.Embed(
                title=
                "🌌 ═══════〔 C O L L E C T I O N   D E S   O M B R E S 〕═══════ 🌌",
                description=f"```\n◆ Collection de {username} ◆\n```",
                color=BotConfig.RARITY_COLORS['Epic'])

            if not inventory:
                embed.add_field(
                    name="📦 Collection Vide",
                    value=
                    "Utilisez le bouton 🎲 Invocation pour obtenir vos premiers personnages!",
                    inline=False)
            else:
                collection_text = ""
                for item in inventory:
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(
                        item['rarity'], '◆')
                    count_text = f" x{item['count']}" if item[
                        'count'] > 1 else ""
                    collection_text += f"{rarity_emoji} **{item['character_name']}** ({item['anime']}){count_text}\n"
                    collection_text += f"   🪙 {format_number(item['value'])} pièces\n\n"

                embed.add_field(
                    name=f"🎭 Personnages (Page {self.current_page})",
                    value=collection_text,
                    inline=False)

            embed.add_field(
                name="📊 Statistiques",
                value=
                f"**Uniques:** {inventory_stats.get('unique_characters', 0)}\n**Total:** {inventory_stats.get('total_characters', 0)}\n**Valeur:** {format_number(inventory_stats.get('total_value', 0))} pièces",
                inline=True)

            embed.set_footer(text=f"Shadow Roll • Page {self.current_page}")

            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating collection embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger la collection",
                color=0xff0000)

    @discord.ui.button(label='⬅️ Précédent',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def previous_page(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_collection_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def next_page(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        # Check if there are more items
        next_inventory = await self.bot.db.get_player_inventory(
            self.user_id,
            page=self.current_page + 1,
            limit=BotConfig.INVENTORY_ITEMS_PER_PAGE)

        if next_inventory:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_collection_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.primary,
                       row=0)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class IndexView(discord.ui.View):
    """Enhanced character index with ownership tracking and collection stats"""

    def __init__(self, bot, user_id: int, page: int = 1, view_mode: str = "characters", anime_filter: Optional[str] = None, rarity_filter: Optional[str] = None, search_query: Optional[str] = None):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.view_mode = view_mode  # "characters" or "series"
        self.anime_filter = anime_filter
        self.rarity_filter = rarity_filter
        self.search_query = search_query
        self.characters_per_page = 8

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_index_embed(self) -> discord.Embed:
        """Create character index with ownership tracking"""
        try:
            if self.view_mode == "series":
                return await self.create_series_stats_embed()
            else:
                return await self.create_characters_embed()
        except Exception as e:
            pass
            logger.error(f"Error creating index embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger l'index des personnages",
                color=0xff0000)

    async def create_characters_embed(self) -> discord.Embed:
        """Create character list with ownership status"""
        characters = await self.get_filtered_characters_with_ownership()
        total_characters = len(characters)
        
        # Pagination
        start_idx = (self.current_page - 1) * self.characters_per_page
        end_idx = start_idx + self.characters_per_page
        page_characters = characters[start_idx:end_idx]
        total_pages = max(1, (total_characters + self.characters_per_page - 1) // self.characters_per_page)

        # Dynamic title
        title_parts = ["📚 ═══════〔 I N D E X   D E S   P E R S O N N A G E S 〕═══════ 📚"]
        
        # Ownership stats
        owned_count = sum(1 for char in characters if char['owned'])
        completion_percentage = (owned_count / total_characters * 100) if total_characters > 0 else 0
        
        embed = discord.Embed(
            title=" ".join(title_parts),
            description=f"```\n◆ Collection Mondiale: {owned_count}/{total_characters} ({completion_percentage:.1f}%) ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic'])

        if not page_characters:
            embed.add_field(
                name="🔍 Aucun résultat",
                value="Aucun personnage ne correspond à vos critères.",
                inline=False)
            return embed

        # Character entries with ownership status
        for i, char in enumerate(page_characters):
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
            
            # Ownership status
            if char['owned']:
                status_icon = "✅"
                status_text = f"Possédé (x{char['count']})"
                name_format = f"**{char['name']}**"
            else:
                status_icon = "❌"
                status_text = "Non possédé"
                name_format = f"~~{char['name']}~~"
            
            # Get drop rate
            total_weight = sum(BotConfig.RARITY_WEIGHTS.values())
            drop_rate = (BotConfig.RARITY_WEIGHTS.get(char['rarity'], 0) / total_weight) * 100
            
            card_content = (
                f"{status_icon} {name_format}\n"
                f"{rarity_emoji} {char['rarity']} • {char['anime']}\n"
                f"💎 {format_number(char['value'])} coins • {drop_rate:.2f}%\n"
                f"📊 {status_text}"
            )
            
            embed.add_field(
                name=f"#{start_idx + i + 1:03d}",
                value=card_content,
                inline=True)

        # Add filters info
        filter_info = []
        if self.anime_filter:
            filter_info.append(f"🎭 Série: {self.anime_filter}")
        if self.rarity_filter:
            filter_info.append(f"{BotConfig.RARITY_EMOJIS.get(self.rarity_filter, '◆')} Rareté: {self.rarity_filter}")
        if self.search_query:
            filter_info.append(f"🔍 Recherche: '{self.search_query}'")
            
        if filter_info:
            embed.add_field(
                name="🎯 Filtres Actifs",
                value=" • ".join(filter_info),
                inline=False)

        # Footer
        embed.set_footer(text=f"Shadow Roll • Page {self.current_page}/{total_pages} • Mode: Personnages")
        return embed

    async def create_series_stats_embed(self) -> discord.Embed:
        """Create series completion statistics"""
        stats = await self.bot.db.get_collection_stats_by_anime(self.user_id)
        
        embed = discord.Embed(
            title="📊 ═══════〔 S T A T I S T I Q U E S   P A R   S É R I E 〕═══════ 📊",
            description="```\n◆ Progression de collection par anime ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary'])

        if not stats:
            embed.add_field(
                name="📋 Aucune donnée",
                value="Commencez à collectionner des personnages!",
                inline=False)
            return embed

        # Calculate overall stats
        total_chars_all = sum(s['total_characters'] for s in stats.values())
        owned_chars_all = sum(s['owned_characters'] for s in stats.values())
        overall_completion = (owned_chars_all / total_chars_all * 100) if total_chars_all > 0 else 0

        embed.add_field(
            name="🪙 Progression Globale",
            value=f"**{owned_chars_all}/{total_chars_all}** personnages ({overall_completion:.1f}%)",
            inline=False)

        # Series stats
        for anime, data in list(stats.items())[:10]:  # Limit to 10 series
            completion = data['completion_percentage']
            
            # Progress bar
            filled_blocks = int(completion / 10)
            progress_bar = "█" * filled_blocks + "░" * (10 - filled_blocks)
            
            # Completion tier
            if completion == 100:
                tier_emoji = "🏆"
                tier_text = "COMPLÈTE"
            elif completion >= 80:
                tier_emoji = "🥇"
                tier_text = "AVANCÉE"
            elif completion >= 50:
                tier_emoji = "🥈"
                tier_text = "INTERMÉDIAIRE"
            elif completion >= 20:
                tier_emoji = "🥉"
                tier_text = "DÉBUTANT"
            else:
                tier_emoji = "📝"
                tier_text = "NOUVEAU"

            value_text = (
                f"{tier_emoji} **{tier_text}**\n"
                f"Progress: [{progress_bar}] {completion:.1f}%\n"
                f"Personnages: {data['owned_characters']}/{data['total_characters']}\n"
                f"Valeur: {format_number(data['owned_value'])}/{format_number(data['total_value'])}"
            )
            
            embed.add_field(
                name=f"🎭 {anime}",
                value=value_text,
                inline=True)

        embed.set_footer(text="Shadow Roll • Mode: Statistiques par Série")
        return embed

    async def get_filtered_characters_with_ownership(self):
        """Get characters with ownership status based on current filters"""
        all_characters = await self.bot.db.get_all_characters_with_ownership(self.user_id)
        
        # Apply anime filter
        if self.anime_filter:
            all_characters = [char for char in all_characters if char['anime'] == self.anime_filter]
        
        # Apply rarity filter
        if self.rarity_filter:
            all_characters = [char for char in all_characters if char['rarity'] == self.rarity_filter]
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            all_characters = [
                char for char in all_characters 
                if query_lower in char['name'].lower() or query_lower in char['anime'].lower()
            ]
        
        return all_characters

    # Navigation buttons for IndexView
    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.view_mode == "characters":
            characters = await self.get_filtered_characters_with_ownership()
            total_pages = max(1, (len(characters) + self.characters_per_page - 1) // self.characters_per_page)
        else:
            total_pages = 1  # Series view has only one page
            
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_index_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='📊 Statistiques', style=discord.ButtonStyle.primary, row=0)
    async def toggle_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.view_mode == "characters":
            self.view_mode = "series"
            button.label = '📚 Personnages'
        else:
            self.view_mode = "characters"
            button.label = '📊 Statistiques'
        
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🎭 Série', style=discord.ButtonStyle.success, row=0)
    async def filter_anime(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AnimeFilterModal(self))

    @discord.ui.button(label='💎 Rareté', style=discord.ButtonStyle.success, row=0)
    async def filter_rarity(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RarityFilterView(self)
        embed = discord.Embed(
            title="🔍 Filtrer par Rareté",
            description="Sélectionnez une rareté pour filtrer l'index:",
            color=BotConfig.RARITY_COLORS['Epic'])
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label='🔍 Recherche', style=discord.ButtonStyle.success, row=1)
    async def search_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SearchModal(self))

    @discord.ui.button(label='🗑️ Effacer', style=discord.ButtonStyle.danger, row=1)
    async def clear_filters(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.anime_filter = None
        self.rarity_filter = None
        self.search_query = None
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_index_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)






class DailyView(discord.ui.View):
    """Daily reward view"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def claim_daily_reward(self) -> discord.Embed:
        """Claim daily reward"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(
                user) if user else f"User {self.user_id}"
            player = await self.bot.db.get_or_create_player(
                self.user_id, username)

            # Check if already claimed today
            if player.last_daily:
                try:
                    last_daily = datetime.fromisoformat(player.last_daily)
                    now = datetime.now()

                    if last_daily.date() == now.date():
                        next_daily = last_daily.replace(
                            hour=0, minute=0, second=0,
                            microsecond=0) + timedelta(days=1)
                        time_until = next_daily - now
                        hours, remainder = divmod(
                            int(time_until.total_seconds()), 3600)
                        minutes, _ = divmod(remainder, 60)

                        return discord.Embed(
                            title="❌ Bénédiction Déjà Récupérée",
                            description=
                            f"Prochaine bénédiction dans {hours}h {minutes}m",
                            color=0xff9900)
                except (ValueError, TypeError):
                    pass  # Invalid date format, allow claim

            # Generate reward
            base_reward = random.randint(BotConfig.DAILY_REWARD_MIN,
                                           BotConfig.DAILY_REWARD_MAX)
            
            # Apply series and equipment coin bonuses to daily reward
            set_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
            coin_multiplier = set_bonuses.get('coin_boost', 1.0)
            reward_with_set_bonus = int(base_reward * coin_multiplier)
            reward_amount = await self.bot.db.apply_equipment_bonuses_to_coins(self.user_id, reward_with_set_bonus)
            current_time = datetime.now().isoformat()

            # Update database - add reward coins to current total
            await self.bot.db.add_player_coins(self.user_id, reward_amount)
            new_coins = player.coins + reward_amount
            await self.bot.db.update_daily_reward(self.user_id, current_time)

            embed = discord.Embed(
                title=
                "🌌 ═══════〔 B É N É D I C T I O N   Q U O T I D I E N N E 〕═══════ 🌌",
                description=
                f"```\n◆ Les ténèbres vous accordent leur bénédiction ◆\n```",
                color=BotConfig.RARITY_COLORS['Legendary'])

            embed.add_field(
                name="🎁 Récompense Reçue",
                value=
                f"**+{format_number(reward_amount)}** {BotConfig.CURRENCY_EMOJI}",
                inline=True)

            embed.add_field(
                name="🪙 Nouveau Solde",
                value=f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                inline=True)

            embed.add_field(name="⏰ Prochaine Bénédiction",
                            value="Dans 24 heures",
                            inline=False)

            embed.set_footer(
                text=
                "Shadow Roll • Revenez demain pour une nouvelle bénédiction")

            return embed

        except Exception as e:
            pass
            logger.error(f"Error claiming daily reward: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description=
                "Impossible de récupérer la bénédiction quotidienne",
                color=0xff0000)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.primary)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class RankingsView(discord.ui.View):
    """Rankings/leaderboard view with multiple categories"""

    def __init__(self, bot, user_id: int, category: str = 'coins'):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_category = category

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_rankings_embed(self) -> discord.Embed:
        """Create rankings embed"""
        try:
            leaderboard = await self.bot.db.get_leaderboard(
                self.current_category, BotConfig.LEADERBOARD_ITEMS_PER_PAGE)

            # Configure embed based on category
            if self.current_category == 'coins':
                title = "🌌 ═══════〔 C L A S S E M E N T   R I C H E S S E S 〕═══════ 🌌"
                description = "```\n◆ Les maîtres des Shadow Coins ◆\n```"
                field_name = "🏆 Top Richesses"
                footer_text = "Shadow Roll • Classement par Shadow Coins"
            elif self.current_category == 'collection_value':
                title = "🌌 ═══════〔 C L A S S E M E N T   C O L L E C T I O N S 〕═══════ 🌌"
                description = "```\n◆ Les collections les plus précieuses ◆\n```"
                field_name = "💎 Top Collections"
                footer_text = "Shadow Roll • Classement par valeur totale de collection"
            else:
                title = "🌌 ═══════〔 C L A S S E M E N T   I N V O C A T I O N S 〕═══════ 🌌"
                description = "```\n◆ Les maîtres des invocations ◆\n```"
                field_name = "🎲 Top Invocations"
                footer_text = "Shadow Roll • Classement par nombre d'invocations"

            embed = discord.Embed(title=title,
                                  description=description,
                                  color=BotConfig.RARITY_COLORS['Epic'])

            if not leaderboard:
                embed.add_field(name="📊 Classement Vide",
                                value="Aucun joueur trouvé",
                                inline=False)
            else:
                rankings_text = ""
                medal_emojis = ["🥇", "🥈", "🥉"]

                for entry in leaderboard:
                    rank = entry['rank']
                    username = entry['username']

                    if self.current_category == 'coins':
                        value = entry['coins']
                        value_text = f"{format_number(value)} {BotConfig.CURRENCY_EMOJI}"
                    elif self.current_category == 'collection_value':
                        value = entry['collection_value']
                        value_text = f"{format_number(value)} pièces"
                    else:
                        value = entry['rerolls']
                        value_text = f"{format_number(value)} invocations"

                    if rank <= 3:
                        medal = medal_emojis[rank - 1]
                        rankings_text += f"{medal} **{username}** - {value_text}\n"
                    else:
                        rankings_text += f"`{rank}.` **{username}** - {value_text}\n"

                embed.add_field(name=field_name,
                                value=rankings_text,
                                inline=False)

            embed.set_footer(text=footer_text)
            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating rankings embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger le classement",
                color=0xff0000)

    @discord.ui.button(label='🪙 Richesses',
                       style=discord.ButtonStyle.primary,
                       row=0)
    async def coins_button(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        self.current_category = 'coins'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='💎 Collections',
                       style=discord.ButtonStyle.success,
                       row=0)
    async def collection_button(self, interaction: discord.Interaction,
                                button: discord.ui.Button):
        self.current_category = 'collection_value'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🎲 Invocations',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def rerolls_button(self, interaction: discord.Interaction,
                             button: discord.ui.Button):
        self.current_category = 'rerolls'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.primary,
                       row=1)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class AchievementsView(discord.ui.View):
    """Enhanced achievements view with modern design and categorization"""

    def __init__(self, bot, user_id: int, category: str = 'all', page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.current_category = 'all'  # Always show all achievements
        self.achievements_per_page = 6  # More achievements per page

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def get_achievement_icon(self, achievement_type: str, is_earned: bool) -> str:
        """Get appropriate icon for achievement type"""
        icons = {
            'rerolls': '🎲',
            'characters': '🎴',
            'rarity': '✨',
            'coins': '🪙'
        }
        base_icon = icons.get(achievement_type, '🏆')
        return f"{base_icon}✅" if is_earned else f"{base_icon}⏳"

    def get_progress_bar(self, progress: int, requirement: int, length: int = 10) -> str:
        """Create a visual progress bar"""
        if progress >= requirement:
            return "█" * length + " COMPLET!"
        
        filled = int((progress / requirement) * length)
        empty = length - filled
        percentage = int((progress / requirement) * 100)
        return "█" * filled + "░" * empty + f" {percentage}%"

    def get_category_color(self, category: str) -> int:
        """Get color based on category"""
        colors = {
            'rerolls': 0x3498db,    # Blue
            'characters': 0xe74c3c,  # Red
            'rarity': 0xf39c12,     # Orange
            'coins': 0xf1c40f,      # Yellow
            'all': BotConfig.RARITY_COLORS['Mythic']
        }
        return colors.get(category, BotConfig.RARITY_COLORS['Mythic'])

    def filter_achievements_by_category(self, achievements: list) -> list:
        """Filter achievements by selected category"""
        if self.current_category == 'all':
            return achievements
        return [ach for ach in achievements if ach['requirement_type'] == self.current_category]

    async def create_achievements_embed(self) -> discord.Embed:
        """Create achievements embed with consistent Shadow Roll style"""
        try:
            # Get all achievements with status
            all_achievements = await self.bot.db.get_all_achievements_with_status(self.user_id)
            
            if not all_achievements:
                embed = discord.Embed(
                    title="🏆 ═══════〔 S U C C È S 〕═══════ 🏆",
                    description="```\nAucun succès disponible\n```",
                    color=BotConfig.RARITY_COLORS['Epic'])
                return embed

            # Filter by category
            achievements = self.filter_achievements_by_category(all_achievements)
            
            # Calculate pagination
            total_pages = max(1, (len(achievements) + self.achievements_per_page - 1) // self.achievements_per_page)
            start_idx = (self.current_page - 1) * self.achievements_per_page
            end_idx = min(start_idx + self.achievements_per_page, len(achievements))
            page_achievements = achievements[start_idx:end_idx]

            # Count earned achievements
            earned_count = sum(1 for ach in all_achievements if ach['is_earned'])
            total_count = len(all_achievements)

            embed = discord.Embed(
                title="🏆 ═══════〔 S U C C È S 〕═══════ 🏆",
                color=BotConfig.RARITY_COLORS['Epic'])

            # Progress header like menu style
            embed.description = (
                f"```\n"
                f"◆ Progression: {earned_count}/{total_count} succès débloqués ◆\n"
                f"```"
            )

            if not page_achievements:
                embed.add_field(
                    name="📭 ═══〔 Aucun Succès 〕═══ 📭",
                    value="```\nUtilisez les boutons pour naviguer\nentre les catégories\n```",
                    inline=False)
            else:
                # Display achievements like menu style
                for achievement in page_achievements:
                    if achievement['is_earned']:
                        # Completed achievement
                        status = "✅ Débloqué"
                        reward_text = f"🪙 {achievement['reward_coins']} Shadow Coins récupérées"
                    else:
                        # Incomplete achievement
                        progress = achievement.get('progress', 0)
                        requirement = achievement.get('requirement_value', 1)
                        
                        if isinstance(requirement, str):
                            # Rarity-based achievement
                            status = f"⏳ Objectif: {requirement}"
                        else:
                            # Numeric achievement
                            requirement = int(requirement)
                            status = f"⏳ Progression: {progress}/{requirement}"
                        
                        reward_text = f"🎁 {achievement['reward_coins']} Shadow Coins à gagner"
                    
                    # Achievement field with menu-style formatting
                    embed.add_field(
                        name=f"🏆 ═══〔 {achievement['name']} 〕═══ 🏆",
                        value=(
                            f"```\n"
                            f"{achievement['description']}\n"
                            f"{status}\n"
                            f"{reward_text}\n"
                            f"```"
                        ),
                        inline=False
                    )

            # Footer consistent with menu style
            embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION} • Page {self.current_page}/{total_pages}")
            
            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating achievements embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="```\nImpossible de charger les succès\n```",
                color=0xff0000)

    # Navigation simplifiée
    @discord.ui.button(label='◀', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
        await interaction.response.defer()
        embed = await self.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.secondary, row=0)
    async def next_page_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        all_achievements = await self.bot.db.get_all_achievements_with_status(self.user_id)
        achievements = self.filter_achievements_by_category(all_achievements)
        total_pages = max(1, (len(achievements) + self.achievements_per_page - 1) // self.achievements_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
        await interaction.response.defer()
        embed = await self.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🎴 Collection', style=discord.ButtonStyle.secondary, row=0)
    async def filter_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'characters'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='✨ Raretés', style=discord.ButtonStyle.secondary, row=0)
    async def filter_rarity(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'rarity'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🪙 Richesse', style=discord.ButtonStyle.secondary, row=0)
    async def filter_coins(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'coins'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    # Navigation buttons (Row 1)
    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.primary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_achievements_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.primary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        all_achievements = await self.bot.db.get_all_achievements_with_status(self.user_id)
        achievements = self.filter_achievements_by_category(all_achievements)
        total_pages = max(1, (len(achievements) + self.achievements_per_page - 1) // self.achievements_per_page)

        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_achievements_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.success, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class MarketplaceView(discord.ui.View):
    """Marketplace view for buying and selling characters"""

    def __init__(self,
                 bot,
                 user_id: int,
                 page: int = 1,
                 view_mode: str = "browse"):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.view_mode = view_mode  # "browse" or "my_listings"
        self.listings_per_page = 5

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_marketplace_embed(self) -> discord.Embed:
        """Create marketplace embed based on view mode"""
        try:
            if self.view_mode == "my_listings":
                return await self.create_my_listings_embed()
            else:
                return await self.create_browse_embed()
        except Exception as e:
            pass
            logger.error(f"Error creating marketplace embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger l'Hôtel des Ventes",
                color=0xff0000)

    async def create_browse_embed(self) -> discord.Embed:
        """Create browse marketplace embed"""
        listings = await self.bot.db.get_marketplace_listings(
            self.current_page, self.listings_per_page)
        stats = await self.bot.db.get_marketplace_stats()

        embed = discord.Embed(
            title="🏪 ═══════〔 H Ô T E L   D E S   V E N T E S 〕═══════ 🏪",
            description=
            f"```\n◆ {stats['active_listings']} annonces actives ◆\n◆ {stats['total_transactions']} transactions totales ◆\n```",
            color=BotConfig.RARITY_COLORS['Legendary'])

        if not listings:
            embed.add_field(
                name="🔍 Aucune annonce",
                value=
                "L'Hôtel des Ventes est actuellement vide.\nRevenez plus tard ou créez votre propre annonce!",
                inline=False)
        else:
            for i, listing in enumerate(listings):
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(
                    listing['rarity'], '◆')
                rarity_color = BotConfig.RARITY_COLORS.get(
                    listing['rarity'], 0x808080)

                # Calculate days remaining
                from datetime import datetime
                listed_date = datetime.fromisoformat(listing['listed_at'])
                days_ago = (datetime.now() - listed_date).days

                field_value = (
                    f"**{listing['anime']}** • {rarity_emoji} {listing['rarity']}\n"
                    f"🪙 Prix: **{format_number(listing['price'])}** {BotConfig.CURRENCY_EMOJI}\n"
                    f"📦 Vendeur: {listing['seller_name']}\n"
                    f"📅 Mis en vente il y a {days_ago} jour(s)\n"
                    f"🔢 Sélection: `{i + 1}`")

                embed.add_field(name=f"🃏 {listing['character_name']}",
                                value=field_value,
                                inline=False)

        # Calculate pagination info
        total_listings = stats['active_listings']
        total_pages = (total_listings + self.listings_per_page - 1
                       ) // self.listings_per_page if total_listings > 0 else 1

        embed.set_footer(
            text=f"Shadow Roll • Page {self.current_page}/{total_pages}")
        return embed

    async def create_my_listings_embed(self) -> discord.Embed:
        """Create my listings embed"""
        listings = await self.bot.db.get_player_marketplace_listings(
            self.user_id)

        embed = discord.Embed(
            title="🏷️ ═══════〔 M E S   A N N O N C E S 〕═══════ 🏷️",
            description=f"```\n◆ {len(listings)}/3 annonces actives ◆\n```",
            color=BotConfig.RARITY_COLORS['Epic'])

        if not listings:
            embed.add_field(
                name="📋 Aucune annonce",
                value=
                "Vous n'avez actuellement aucune annonce active.\nUtilisez 'Vendre une Carte' pour créer une annonce!",
                inline=False)
        else:
            for i, listing in enumerate(listings):
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(
                    listing['rarity'], '◆')

                # Calculate expiration
                from datetime import datetime
                expires_date = datetime.fromisoformat(listing['expires_at'])
                days_left = (expires_date - datetime.now()).days

                field_value = (
                    f"**{listing['anime']}** • {rarity_emoji} {listing['rarity']}\n"
                    f"🪙 Prix: **{format_number(listing['price'])}** {BotConfig.CURRENCY_EMOJI}\n"
                    f"⏰ Expire dans {days_left} jour(s)\n"
                    f"🔢 Annuler: `{i + 1}`")

                embed.add_field(name=f"🃏 {listing['character_name']}",
                                value=field_value,
                                inline=False)

        embed.set_footer(text="Shadow Roll • Vos annonces actives")
        return embed

    @discord.ui.button(label='⬅️ Précédent',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def previous_page(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_marketplace_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def next_page(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        stats = await self.bot.db.get_marketplace_stats()
        total_pages = (stats['active_listings'] + self.listings_per_page -
                       1) // self.listings_per_page

        if total_pages == 0:
            total_pages = 1

        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_marketplace_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='1️⃣', style=discord.ButtonStyle.primary, row=1)
    async def select_1(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 1)

    @discord.ui.button(label='2️⃣', style=discord.ButtonStyle.primary, row=1)
    async def select_2(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 2)

    @discord.ui.button(label='3️⃣', style=discord.ButtonStyle.primary, row=1)
    async def select_3(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 3)

    @discord.ui.button(label='4️⃣', style=discord.ButtonStyle.primary, row=1)
    async def select_4(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 4)

    @discord.ui.button(label='5️⃣', style=discord.ButtonStyle.primary, row=1)
    async def select_5(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 5)

    @discord.ui.button(label='🛒 Mes Annonces',
                       style=discord.ButtonStyle.secondary,
                       row=2)
    async def my_listings_button(self, interaction: discord.Interaction,
                                 button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "my_listings"
        self.current_page = 1
        embed = await self.create_marketplace_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏪 Parcourir',
                       style=discord.ButtonStyle.secondary,
                       row=2)
    async def browse_button(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        await interaction.response.defer()
        self.view_mode = "browse"
        self.current_page = 1
        embed = await self.create_marketplace_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🪙 Vendre une Carte',
                       style=discord.ButtonStyle.success,
                       row=2)
    async def sell_item_button(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        await interaction.response.defer()
        view = SellItemView(self.bot, self.user_id)
        embed = await view.create_sell_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🏠 Menu Principal',
                       style=discord.ButtonStyle.primary,
                       row=2)
    async def back_to_menu(self, interaction: discord.Interaction,
                           button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

    async def handle_item_selection(self, interaction: discord.Interaction,
                                    selection_number: int):
        """Handle item selection for buying or canceling"""
        await interaction.response.defer()

        try:
            if self.view_mode == "browse":
                # Buying mode
                listings = await self.bot.db.get_marketplace_listings(
                    self.current_page, self.listings_per_page)

                if selection_number > len(listings):
                    await interaction.followup.send("Sélection invalide!",
                                                    ephemeral=True)
                    return

                selected_listing = listings[selection_number - 1]

                # Prevent self-purchase
                if selected_listing['seller_id'] == self.user_id:
                    await interaction.followup.send(
                        "Vous ne pouvez pas acheter votre propre annonce!",
                        ephemeral=True)
                    return

                # Check if player has enough coins
                player = await self.bot.db.get_or_create_player(
                    self.user_id, interaction.user.display_name)
                if player.coins < selected_listing['price']:
                    needed = selected_listing['price'] - player.coins
                    await interaction.followup.send(
                        f"Fonds insuffisants! Il vous manque {format_number(needed)} {BotConfig.CURRENCY_EMOJI}",
                        ephemeral=True)
                    return

                # Attempt purchase
                if await self.bot.db.purchase_marketplace_item(
                        self.user_id, selected_listing['id']):
                    embed = await self.create_marketplace_embed()
                    await interaction.edit_original_response(embed=embed,
                                                             view=self)
                    await interaction.followup.send(
                        f"🎉 Achat réussi! Vous avez acheté **{selected_listing['character_name']}** pour {format_number(selected_listing['price'])} {BotConfig.CURRENCY_EMOJI}",
                        ephemeral=True)
                else:
                    await interaction.followup.send(
                        "Erreur lors de l'achat. L'annonce n'est peut-être plus disponible.",
                        ephemeral=True)

            else:
                # Cancel listing mode
                listings = await self.bot.db.get_player_marketplace_listings(
                    self.user_id)

                if selection_number > len(listings):
                    await interaction.followup.send("Sélection invalide!",
                                                    ephemeral=True)
                    return

                selected_listing = listings[selection_number - 1]

                # Cancel listing
                if await self.bot.db.cancel_marketplace_listing(
                        self.user_id, selected_listing['id']):
                    embed = await self.create_marketplace_embed()
                    await interaction.edit_original_response(embed=embed,
                                                             view=self)
                    await interaction.followup.send(
                        f"✅ Annonce annulée! **{selected_listing['character_name']}** a été retourné à votre collection.",
                        ephemeral=True)
                else:
                    await interaction.followup.send(
                        "Erreur lors de l'annulation de l'annonce.",
                        ephemeral=True)

        except Exception as e:
            pass
            logger.error(f"Error handling item selection: {e}")
            await interaction.followup.send(
                "Erreur lors du traitement de votre sélection.",
                ephemeral=True)


class SellItemView(discord.ui.View):
    """View for selling items on the marketplace"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.items_per_page = 5
        self.selected_item = None

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_sell_embed(self) -> discord.Embed:
        """Create sell item selection embed"""
        try:
            inventory = await self.bot.db.get_player_inventory(
                self.user_id, self.current_page, self.items_per_page)

            embed = discord.Embed(
                title="🪙 ═══════〔 V E N D R E   U N E   C A R T E 〕═══════ 🪙",
                description=
                "```\nChoisissez une carte de votre collection à vendre\n```",
                color=BotConfig.RARITY_COLORS['Epic'])

            if not inventory:
                embed.add_field(
                    name="📦 Collection vide",
                    value=
                    "Vous n'avez aucune carte à vendre.\nInvoquez des personnages d'abord!",
                    inline=False)
            else:
                for i, item in enumerate(inventory):
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(
                        item['rarity'], '◆')
                    suggested_price = max(
                        item['value'] // 2,
                        50)  # Suggest half character value, minimum 50

                    field_value = (
                        f"**{item['anime']}** • {rarity_emoji} {item['rarity']}\n"
                        f"📊 Quantité: {item['count']}\n"
                        f"💡 Prix suggéré: {format_number(suggested_price)} {BotConfig.CURRENCY_EMOJI}\n"
                        f"🔢 Sélection: `{i + 1}`")

                    embed.add_field(name=f"🃏 {item['character_name']}",
                                    value=field_value,
                                    inline=False)

            # Check current listings count
            current_listings = await self.bot.db.get_player_marketplace_listings(
                self.user_id)
            embed.set_footer(
                text=
                f"Shadow Roll • Annonces actives: {len(current_listings)}/3")
            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating sell embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger votre collection",
                color=0xff0000)

    @discord.ui.button(label='⬅️ Précédent',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def previous_page(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_sell_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant',
                       style=discord.ButtonStyle.secondary,
                       row=0)
    async def next_page(self, interaction: discord.Interaction,
                        button: discord.ui.Button):
        inventory_stats = await self.bot.db.get_inventory_stats(self.user_id)
        total_items = inventory_stats.get('unique_characters', 0)
        total_pages = (total_items + self.items_per_page -
                       1) // self.items_per_page

        if total_pages == 0:
            total_pages = 1

        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_sell_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='1️⃣', style=discord.ButtonStyle.success, row=1)
    async def select_1(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 1)

    @discord.ui.button(label='2️⃣', style=discord.ButtonStyle.success, row=1)
    async def select_2(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 2)

    @discord.ui.button(label='3️⃣', style=discord.ButtonStyle.success, row=1)
    async def select_3(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 3)

    @discord.ui.button(label='4️⃣', style=discord.ButtonStyle.success, row=1)
    async def select_4(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 4)

    @discord.ui.button(label='5️⃣', style=discord.ButtonStyle.success, row=1)
    async def select_5(self, interaction: discord.Interaction,
                       button: discord.ui.Button):
        await self.handle_item_selection(interaction, 5)

    @discord.ui.button(label='🏪 Retour Vente',
                       style=discord.ButtonStyle.secondary,
                       row=2)
    async def back_to_marketplace(self, interaction: discord.Interaction,
                                  button: discord.ui.Button):
        await interaction.response.defer()
        view = MarketplaceView(self.bot, self.user_id)
        embed = await view.create_marketplace_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    async def handle_item_selection(self, interaction: discord.Interaction,
                                    selection_number: int):
        """Handle item selection for selling"""
        await interaction.response.send_modal(
            PriceModal(self.bot, self.user_id, self.current_page,
                       selection_number))


class PriceModal(discord.ui.Modal):
    """Modal for setting price when selling an item"""

    def __init__(self, bot, user_id: int, page: int, selection_number: int):
        super().__init__(title="Définir le prix de vente")
        self.bot = bot
        self.user_id = user_id
        self.page = page
        self.selection_number = selection_number

        self.price_input = discord.ui.TextInput(
            label="Prix en Shadow Coins",
            placeholder="Entrez le prix de vente (ex: 1000)",
            min_length=1,
            max_length=10,
            required=True)
        self.add_item(self.price_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price_input.value)

            if price < 1:
                await interaction.response.send_message(
                    "Le prix doit être supérieur à 0!", ephemeral=True)
                return

            if price > 999999:
                await interaction.response.send_message(
                    "Le prix ne peut pas dépasser 999,999 Shadow Coins!",
                    ephemeral=True)
                return

            # Check if player has max listings
            current_listings = await self.bot.db.get_player_marketplace_listings(
                self.user_id)
            if len(current_listings) >= 3:
                await interaction.response.send_message(
                    "Vous avez déjà 3 annonces actives! Annulez-en une avant d'en créer une nouvelle.",
                    ephemeral=True)
                return

            # Get the selected inventory item
            inventory = await self.bot.db.get_player_inventory(
                self.user_id, self.page, 5)

            if self.selection_number > len(inventory):
                await interaction.response.send_message("Sélection invalide!",
                                                        ephemeral=True)
                return

            selected_item = inventory[self.selection_number - 1]
            inventory_item_id = selected_item['inventory_id']

            # Create listing
            if await self.bot.db.create_marketplace_listing(
                    self.user_id, inventory_item_id, price):
                await interaction.response.send_message(
                    f"✅ Annonce créée! **{selected_item['character_name']}** est maintenant en vente pour {format_number(price)} {BotConfig.CURRENCY_EMOJI}",
                    ephemeral=True)

                # Return to marketplace view
                view = MarketplaceView(self.bot,
                                       self.user_id,
                                       view_mode="my_listings")
                embed = await view.create_marketplace_embed()
                await interaction.edit_original_response(embed=embed,
                                                         view=view)
            else:
                await interaction.response.send_message(
                    "Erreur lors de la création de l'annonce. Vérifiez que vous possédez encore cette carte.",
                    ephemeral=True)

        except ValueError:
            await interaction.response.send_message(
                "Veuillez entrer un nombre valide!", ephemeral=True)
        except Exception as e:
            pass
            logger.error(f"Error in price modal: {e}")
            await interaction.response.send_message(
                "Erreur lors de la création de l'annonce.", ephemeral=True)


class TitlesView(discord.ui.View):
    """Titles management view with unlock status and selection"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.titles_per_page = 6

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_titles_embed(self) -> discord.Embed:
        """Create titles embed with unlock status and selection"""
        try:
            # Check for new title unlocks
            newly_unlocked = await self.bot.db.check_and_unlock_titles(self.user_id)
            
            # Get all titles for player
            all_titles = await self.bot.db.get_player_titles(self.user_id)
            
            if not all_titles:
                return discord.Embed(
                    title="🏆 ═══════〔 T I T R E S 〕═══════ 🏆",
                    description="```\nAucun titre disponible\n```",
                    color=BotConfig.RARITY_COLORS['Epic'])

            # Calculate pagination
            total_pages = max(1, (len(all_titles) + self.titles_per_page - 1) // self.titles_per_page)
            start_idx = (self.current_page - 1) * self.titles_per_page
            end_idx = min(start_idx + self.titles_per_page, len(all_titles))
            page_titles = all_titles[start_idx:end_idx]

            # Count unlocked titles
            unlocked_count = sum(1 for title in all_titles if title['is_unlocked'])
            total_count = len(all_titles)

            embed = discord.Embed(
                title="🏆 ═══════〔 T I T R E S 〕═══════ 🏆",
                color=BotConfig.RARITY_COLORS['Epic'])

            # Progress header
            embed.description = (
                f"```\n"
                f"◆ Collection: {unlocked_count}/{total_count} titres débloqués ◆\n"
                f"Page {self.current_page}/{total_pages}\n"
                f"```"
            )

            # Show newly unlocked titles
            if newly_unlocked:
                unlock_text = ""
                for title in newly_unlocked[:2]:  # Show max 2
                    unlock_text += f"✨ **{title['display_name']}** débloqué!\n"
                
                embed.add_field(
                    name="🎊 Nouveaux Titres Débloqués",
                    value=unlock_text,
                    inline=False
                )

            if not page_titles:
                embed.add_field(
                    name="📭 ═══〔 Titres 〕═══ 📭",
                    value="```\nUtilisez les boutons pour naviguer\n```",
                    inline=False)
            else:
                # Display titles with formatting
                for title in page_titles:
                    if title['is_unlocked']:
                        # Unlocked title
                        status = "✅ Débloqué"
                        if title['is_selected']:
                            status += " | 🪙 **ÉQUIPÉ**"
                        
                        bonus_text = ""
                        if title['bonus_description']:
                            bonus_text = f"\n💫 {title['bonus_description']}"
                    else:
                        # Locked title
                        status = "🔒 Verrouillé"
                        bonus_text = ""

                    embed.add_field(
                        name=f"{title['icon']} {title['display_name']}",
                        value=f"```\n{title['description']}\n```\n{status}{bonus_text}",
                        inline=True
                    )

            embed.set_footer(
                text=f"Shadow Roll • Page {self.current_page}/{total_pages}"
            )

            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating titles embed: {e}")
            return discord.Embed(title="❌ Erreur",
                                 description="Impossible de charger les titres",
                                 color=0xff0000)

    @discord.ui.button(label='◀️ Page Précédente', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_titles_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='▶️ Page Suivante', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        all_titles = await self.bot.db.get_player_titles(self.user_id)
        total_pages = max(1, (len(all_titles) + self.titles_per_page - 1) // self.titles_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_titles_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🎯 Sélectionner Titre', style=discord.ButtonStyle.primary, row=1)
    async def select_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show modal to select a title"""
        modal = TitleSelectionModal(self.bot, self.user_id, self.current_page)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='❌ Retirer Titre', style=discord.ButtonStyle.danger, row=1)
    async def remove_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove selected title"""
        try:
            if await self.bot.db.unselect_title(self.user_id):
                await interaction.response.send_message("✅ Titre retiré avec succès!", ephemeral=True)
                # Refresh the view
                embed = await self.create_titles_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Erreur lors de la suppression du titre.", ephemeral=True)
        except Exception as e:
            pass
            logger.error(f"Error removing title: {e}")
            await interaction.response.send_message("❌ Erreur lors de la suppression du titre.", ephemeral=True)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class TitleSelectionModal(discord.ui.Modal, title="🎯 Sélection de Titre"):
    """Modal for selecting a title by number"""
    
    def __init__(self, bot, user_id: int, current_page: int):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.current_page = current_page

    title_number = discord.ui.TextInput(
        label="Numéro du titre à équiper (1-6)",
        placeholder="Entrez le numéro du titre que vous voulez équiper...",
        max_length=1,
        required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            title_index = int(self.title_number.value) - 1
            
            if title_index < 0 or title_index > 5:
                await interaction.response.send_message(
                    "Veuillez entrer un numéro entre 1 et 6!", ephemeral=True)
                return

            # Get titles for current page
            all_titles = await self.bot.db.get_player_titles(self.user_id)
            titles_per_page = 6
            start_idx = (self.current_page - 1) * titles_per_page
            end_idx = min(start_idx + titles_per_page, len(all_titles))
            page_titles = all_titles[start_idx:end_idx]

            if title_index >= len(page_titles):
                await interaction.response.send_message(
                    "Numéro invalide! Vérifiez le nombre de titres affichés.", ephemeral=True)
                return

            selected_title = page_titles[title_index]
            
            if not selected_title['is_unlocked']:
                await interaction.response.send_message(
                    f"❌ Le titre **{selected_title['display_name']}** n'est pas encore débloqué!", 
                    ephemeral=True)
                return

            if selected_title['is_selected']:
                await interaction.response.send_message(
                    f"✅ Le titre **{selected_title['display_name']}** est déjà équipé!", 
                    ephemeral=True)
                return

            # Select the title
            if await self.bot.db.select_title(self.user_id, selected_title['id']):
                bonus_msg = ""
                if selected_title['bonus_description']:
                    bonus_msg = f"\n💫 {selected_title['bonus_description']}"
                
                await interaction.response.send_message(
                    f"🪙 Titre **{selected_title['display_name']}** équipé avec succès!{bonus_msg}", 
                    ephemeral=True)
                
                # Refresh the titles view
                view = TitlesView(self.bot, self.user_id, self.current_page)
                embed = await view.create_titles_embed()
                await interaction.edit_original_response(embed=embed, view=view)
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors de l'équipement du titre.", ephemeral=True)

        except ValueError:
            await interaction.response.send_message(
                "Veuillez entrer un nombre valide!", ephemeral=True)
        except Exception as e:
            pass
            logger.error(f"Error in title selection: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la sélection du titre.", ephemeral=True)


class HelpView(discord.ui.View):
    """Enhanced help and information view with navigation"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_help_embed(self) -> discord.Embed:
        """Create comprehensive help embed with multiple pages"""
        if self.current_page == 1:
            return await self.create_basics_embed()
        elif self.current_page == 2:
            return await self.create_systems_embed()
        elif self.current_page == 3:
            return await self.create_equipment_embed()
        elif self.current_page == 4:
            return await self.create_tips_embed()
        else:
            return await self.create_basics_embed()

    async def create_basics_embed(self) -> discord.Embed:
        """Page 1: Basic commands and navigation"""
        embed = discord.Embed(
            title="🌌 ═══════〔 G U I D E   D E S   O M B R E S 〕═══════ 🌌",
            description="```\n◆ Maîtrisez les pouvoirs des ténèbres... ◆\nPage 1/4 - Bases du Jeu\n```",
            color=BotConfig.RARITY_COLORS['Epic'])

        embed.add_field(name="🌑 ═══〔 Commandes Principales 〕═══ 🌑",
                        value=("```\n"
                               "!menu     ◆ Interface principale\n"
                               "!help     ◆ Affiche ce guide\n"
                               "```"),
                        inline=False)

        embed.add_field(name="🌫️ ═══〔 Navigation Interface 〕═══ 🌫️",
                        value=("```\n"
                               "👤 Profil      ◆ Statistiques personnelles\n"
                               "🎲 Invocation  ◆ Invoquer des personnages\n"
                               "🧪 Recherche   ◆ Traquer un personnage\n"
                               "🎒 Collection  ◆ Voir vos personnages obtenus\n"
                               "🔮 Craft       ◆ Évolution des personnages\n"
                               "🎁 Bénédiction ◆ Récompense quotidienne\n"
                               "🛒 Vente        ◆ Revendre vos personnages\n"
                               "🎖️ Succès      ◆ Récompenses d’exploits\n"
                               "🏆 Classement  ◆ Tableau des maîtres\n"
                               "❓ Guide       ◆ Informations détaillées\n"
                               "```"),
                        inline=False)

        embed.add_field(
            name="⚡ ═══〔 Système de Rareté 〕═══ ⚡",
            value=
            (f"```\n"
             f"{BotConfig.RARITY_EMOJIS['Common']} Commun      ◆ Base\n"
             f"{BotConfig.RARITY_EMOJIS['Rare']} Rare        ◆ Peu commun\n"
             f"{BotConfig.RARITY_EMOJIS['Epic']} Épique      ◆ Rare\n"
             f"{BotConfig.RARITY_EMOJIS['Legendary']} Légendaire ◆ Très rare\n"
             f"{BotConfig.RARITY_EMOJIS['Mythic']} Mythique    ◆ Extrêmement rare\n"
             f"{BotConfig.RARITY_EMOJIS['Titan']} Titan       ◆ Ultra rare\n"
             f"{BotConfig.RARITY_EMOJIS['Fusion']} Fusion      ◆ Légendaire ultime\n"
             f"```"),
            inline=False)

        embed.add_field(
            name="🪙 ═══〔 Économie 〕═══ 🪙",
            value=
            (f"```\n"
             f"Coût Invocation: {BotConfig.REROLL_COST} Shadow Coins\n"
             f"Récompense Quotidienne: {BotConfig.DAILY_REWARD_MIN}-{BotConfig.DAILY_REWARD_MAX} Shadow Coins\n"
             f"Temps de Recharge: {BotConfig.REROLL_COOLDOWN} secondes\n"
             f"```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 1/4")
        return embed

    async def create_systems_embed(self) -> discord.Embed:
        """Page 2: Rarity system and economy"""
        embed = discord.Embed(
            title="🌌 ═══════〔 S Y S T È M E S   D E   J E U 〕═══════ 🌌",
            description="```\n◆ Comprenez les mécaniques avancées... ◆\nPage 2/4 - Raretés & Économie\n```",
            color=BotConfig.RARITY_COLORS['Legendary'])

        embed.add_field(
            name="⚡ ═══〔 Système de Rareté (9 Niveaux) 〕═══ ⚡",
            value=(f"```\n"
                   f"{BotConfig.RARITY_EMOJIS['Common']} Commun      ◆ 60.0% - Base\n"
                   f"{BotConfig.RARITY_EMOJIS['Rare']} Rare        ◆ 25.0% - Peu commun\n"
                   f"{BotConfig.RARITY_EMOJIS['Epic']} Épique      ◆ 10.0% - Rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Legendary']} Légendaire ◆ 4.0% - Très rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Mythic']} Mythique    ◆ 1.0% - Extrêmement rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Evolve']} Evolve      ◆ CRAFT - Évolution ultime\n"
                   f"{BotConfig.RARITY_EMOJIS['Titan']} Titan       ◆ 0.3% - Ultra rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Fusion']} Fusion      ◆ 0.1% - Légendaire ultime\n"
                   f"{BotConfig.RARITY_EMOJIS.get('Secret', '🌑')} Secret      ◆ 0.001% - Rareté ultime\n"
                   f"```"),
            inline=False)

        embed.add_field(
            name="🪙 ═══〔 Économie Shadow Coins 〕═══ 🪙",
            value=(f"```\n"
                   f"Coût Invocation: {BotConfig.REROLL_COST} SC\n"
                   f"Bénédiction Quotidienne: {BotConfig.DAILY_REWARD_MIN}-{BotConfig.DAILY_REWARD_MAX} SC\n"
                   f"Temps de Recharge: {BotConfig.REROLL_COOLDOWN}s\n"
                   f"Coins de Départ: {BotConfig.STARTING_COINS} SC\n"
                   f"```"),
            inline=True)

        embed.add_field(
            name="🍀 ═══〔 Système de Potions 〕═══ 🍀",
            value=("```\n"
                   "🧪 Potion Rare: +50% chances Rare\n"
                   "🧪 Potion Epic: +30% chances Epic\n"
                   "🧪 Élixir Légendaire: +20% Legendary\n"
                   "🧪 Sérum Mythique: +15% Mythic\n"
                   "⚠️ N'affectent PAS Titan/Fusion/Secret\n"
                   "Achat via 🛒 Boutique\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="📊 ═══〔 Statistiques de Collection 〕═══ 📊",
            value=("```\n"
                   "📚 Index: Tous les 151 personnages\n"
                   "🎖️ 21 séries d'anime complètes\n"
                   "🏆 Classement par coins/collection\n"
                   "🎯 Système de succès avec récompenses\n"
                   "🔄 Marketplace pour échanger\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 2/4")
        return embed

    async def create_equipment_embed(self) -> discord.Embed:
        """Page 3: Equipment and bonus systems"""
        embed = discord.Embed(
            title="⚔️ ═══════〔 S Y S T È M E   É Q U I P E M E N T 〕═══════ ⚔️",
            description="```\n◆ Maîtrisez les bonus ultimes... ◆\nPage 3/4 - Équipement & Bonus\n```",
            color=BotConfig.RARITY_COLORS['Titan'])

        embed.add_field(
            name="⚔️ ═══〔 Équipement Ultra-Rare 〕═══ ⚔️",
            value=("```\n"
                   "🔱 Titan:  +2% chances toutes raretés\n"
                   "⭐ Fusion:    +5% Shadow Coins partout\n"
                   "🌑 Secret: +3% chances + 3% coins\n"
                   "\n"
                   "• Maximum 3 personnages équipés\n"
                   "• Bonus appliqués PARTOUT dans le jeu\n"
                   "• Combinables avec autres bonus\n"
                   "• Gestion via ⚔️ Équipement ou /equipment\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🎖️ ═══〔 Bonus de Séries 〕═══ 🎖️",
            value=("```\n"
                   "Complétez des séries d'anime:\n"
                   "• Akatsuki (Naruto): +1% rareté globale\n"
                   "• Straw Hat Pirates: +15% coins\n"
                   "• Survey Corps: +10% coins\n"
                   "• Demon Slayer Corps: +8% coins\n"
                   "\n"
                   "23 séries complètes disponibles!\n"
                   "Voir via 🎖️ Séries\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🔥 ═══〔 Cumul des Bonus 〕═══ 🔥",
            value=("```\n"
                   "Les bonus se CUMULENT:\n"
                   "⚔️ Équipement (Titan/Fusion/Secret)\n"
                   "+ 🎖️ Séries (collections complètes)\n"
                   "+ 🍀 Potions (temporaires)\n"
                   "= 🔥 Total affiché en temps réel\n"
                   "\n"
                   "Visible à chaque invocation!\n"
                   "Affichage deux colonnes moderne\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🎯 ═══〔 Applications des Bonus 〕═══ 🎯",
            value=("```\n"
                   "Les bonus s'appliquent à:\n"
                   "🎲 Chances d'invocation de personnages\n"
                   "🎁 Bénédictions quotidiennes\n"
                   "🪙 Ventes de personnages au marché\n"
                   "🏆 Récompenses de succès\n"
                   "🔄 Toutes transactions économiques\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 3/4")
        return embed

    async def create_tips_embed(self) -> discord.Embed:
        """Page 4: Advanced tips and strategies"""
        embed = discord.Embed(
            title="🪙 ═══════〔 S T R A T É G I E S   A V A N C É E S 〕═══════ 🪙",
            description="```\n◆ Devenez un maître des ombres... ◆\nPage 4/4 - Conseils & Stratégies\n```",
            color=BotConfig.RARITY_COLORS['Epic'])

        embed.add_field(
            name="🎯 ═══〔 Stratégies d'Invocation 〕═══ 🎯",
            value=("```\n"
                   "• Récupérez votre bénédiction CHAQUE jour\n"
                   "• Équipez des Titans pour +2% de chances\n"
                   "• Complétez des séries pour des bonus\n"
                   "• Utilisez des potions avant les sessions\n"
                   "• Vendez les doublons de Common/Rare\n"
                   "• Gardez au moins 1000 SC de réserve\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="💎 ═══〔 Gestion de Collection 〕═══ 💎",
            value=("```\n"
                   "• Gardez TOUS les ultra-rares (Titan+)\n"
                   "• Équipez les meilleurs pour les bonus\n"
                   "• Complétez les séries d'anime\n"
                   "• Surveillez l'Index pour progression\n"
                   "• Vendez intelligemment les doublons\n"
                   "• Utilisez le Marketplace pour échanger\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🏆 ═══〔 Optimisation Économique 〕═══ 🏆",
            value=("```\n"
                   "• Équipez des Duos pour +5% coins\n"
                   "• Complétez les succès pour bonus\n"
                   "• Planifiez achats de potions\n"
                   "• Gardez SC de réserve pour occasions\n"
                   "• Utilisez classement comme objectif\n"
                   "• Marketplace = profit à long terme\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="⚡ ═══〔 Fonctionnalités Avancées 〕═══ ⚡",
            value=("```\n"
                   "• Bonus visibles à chaque invocation\n"
                   "• Secret = 0.001% chance seulement\n"
                   "• Séries complètes = bonus permanents\n"
                   "• Potions n'affectent pas ultra-rares\n"
                   "• 151 personnages total disponibles\n"
                   "• Marketplace pour échanges joueurs\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🌑 ═══〔 Secrets du Système 〕═══ 🌑",
            value=("```\n"
                   "• Layout deux colonnes pour clarté\n"
                   "• Affichage en temps réel des bonus\n"
                   "• Navigation fluide sans spam messages\n"
                   "• Patch notes avec historique complet\n"
                   "• Admin commands pour modération\n"
                   "• Architecture modulaire pour évolution\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 4/4")
        return embed

    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = await self.create_help_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < 4:
            self.current_page += 1
            embed = await self.create_help_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='🎯 Bases', style=discord.ButtonStyle.success, row=1)
    async def basics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        embed = await self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='⚡ Systèmes', style=discord.ButtonStyle.success, row=1)
    async def systems_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 2
        embed = await self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='⚔️ Équipement', style=discord.ButtonStyle.success, row=1)
    async def equipment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 3
        embed = await self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🪙 Stratégies', style=discord.ButtonStyle.success, row=1)
    async def tips_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 4
        embed = await self.create_help_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class ShadowMenuManager:
    """Manager for Shadow Roll menu system"""

    def __init__(self, bot):
        self.bot = bot

    async def create_main_menu(self, ctx):
        """Create the main Shadow Roll menu"""
        try:
            user_id = ctx.author.id
            username = get_display_name(ctx.author)
            player = await self.bot.db.get_or_create_player(user_id, username)

            embed = discord.Embed(
                title="🌌 ═══════〔 S H A D O W   R O L L 〕═══════ 🌌",
                description=
                f"```\n◆ Bienvenue dans les ténèbres, {username} ◆\n{format_number(player.coins)} Shadow Coins disponibles\n```",
                color=BotConfig.RARITY_COLORS['Epic'])

            embed.add_field(
                name="🌑 ═══〔 Navigation 〕═══ 🌑",
                value=("```\n"
                       "👤 Profil      ◆ Vos statistiques\n"
                       "🎲 Invocation  ◆ Invoquer des personnages\n"
                       "🧪 Recherche   ◆ Traquer un personnage\n"
                       "🎒 Collection  ◆ Voir vos personnages\n"
                       "🔮 Craft       ◆ Évolution des personnages\n"
                       "🎁 Bénédiction ◆ Récompense quotidienne\n"
                       "🛒 Vente        ◆ Revendre vos personnages\n"
                       "🎖️ Succès      ◆ Récompenses d’exploits\n"
                       "🏆 Classement  ◆ Tableau des maîtres\n"
                       "❓ Guide       ◆ Aide et informations\n"
                       "```"),
                inline=False)

            embed.set_footer(
                text="Shadow Roll • Utilisez les boutons pour naviguer",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

            view = ShadowMenuView(self.bot, user_id)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            pass
            logger.error(f"Error creating main menu: {e}")
            await ctx.send("❌ Erreur lors de la création du menu Shadow Roll.")
