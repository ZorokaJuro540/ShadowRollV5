import discord
import logging
from core.config import BotConfig

logger = logging.getLogger(__name__)

def format_number(number):
    """Format number with K/M suffixes"""
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

class RankingsView(discord.ui.View):
    """Rankings/leaderboard view with multiple categories"""

    def __init__(self, bot, user_id: int, category: str = 'coins'):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_category = category

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
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
                footer_text = "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ • Classement par Shadow Coins"
            elif self.current_category == 'collection_value':
                title = "🌌 ═══════〔 C L A S S E M E N T   C O L L E C T I O N S 〕═══════ 🌌"
                description = "```\n◆ Les collections les plus précieuses ◆\n```"
                field_name = "💎 Top Collections"
                footer_text = "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ • Classement par valeur totale de collection"
            else:
                title = "🌌 ═══════〔 C L A S S E M E N T   I N V O C A T I O N S 〕═══════ 🌌"
                description = "```\n◆ Les maîtres des invocations ◆\n```"
                field_name = "🎲 Top Invocations"
                footer_text = "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ • Classement par nombre d'invocations"

            embed = discord.Embed(
                title=title,
                description=description,
                color=BotConfig.RARITY_COLORS['Mythical'])

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
            logger.error(f"Error creating rankings embed: {e}")
            return discord.Embed(title="❌ Erreur",
                                 description="Impossible de charger le classement",
                                 color=0xff0000)

    @discord.ui.button(label='🪙 Richesses', style=discord.ButtonStyle.primary, row=0)
    async def coins_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'coins'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='💎 Collections', style=discord.ButtonStyle.primary, row=0)
    async def collection_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'collection_value'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🎲 Invocations', style=discord.ButtonStyle.primary, row=0)
    async def rerolls_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'rerolls'
        await interaction.response.defer()
        embed = await self.create_rankings_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.secondary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await ProfileView(self.bot, self.user_id).create_main_menu_embed()
        await interaction.edit_original_response(embed=embed, view=view)