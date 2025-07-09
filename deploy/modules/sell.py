"""
Sell system for Shadow Roll Bot
Allows players to sell their characters for coins
"""

import discord
from discord.ext import commands
from core.config import BotConfig
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def truncate_field_value(text: str, max_length: int = 1000) -> str:
    """Truncate text to prevent Discord embed field overflow"""
    if len(text) <= max_length:
        return text
    # Find a good break point
    truncated = text[:max_length-20]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length // 2:
        truncated = truncated[:last_newline]
    return truncated + "\n..."

class SellView(discord.ui.View):
    """Sell interface view with character selection"""
    
    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.selected_item = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact with this view"""
        return interaction.user.id == self.user_id
    
    async def on_timeout(self):
        """Called when view times out"""
        for item in self.children:
            item.disabled = True
    
    async def create_sell_embed(self) -> discord.Embed:
        """Create sell interface embed"""
        try:
            # Get player's sellable inventory
            inventory_items = await self.bot.db.get_player_sellable_inventory(
                self.user_id, self.current_page, 10)
            
            # Get player info for coins display
            player = await self.bot.db.get_or_create_player(
                self.user_id, "Unknown")
            
            embed = discord.Embed(
                title="🪙 Vendre des Personnages",
                description="Vendez vos personnages contre des pièces pour financer vos invocations!",
                color=0xFFD700
            )
            
            # Add current coins
            embed.add_field(
                name="🪙 Vos Pièces Actuelles",
                value=f"{BotConfig.CURRENCY_EMOJI} {player.coins:,}",
                inline=True
            )
            
            # Add sell cost info
            embed.add_field(
                name="🎲 Coût d'Invocation",
                value=f"{BotConfig.CURRENCY_EMOJI} {BotConfig.REROLL_COST}",
                inline=True
            )
            
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer
            
            if not inventory_items:
                embed.add_field(
                    name="📭 Inventaire Vide",
                    value="Vous n'avez aucun personnage à vendre.",
                    inline=False
                )
                # Disable sell buttons
                for item in self.children:
                    if isinstance(item, discord.ui.Select):
                        item.disabled = True
            else:
                # Create character list with sell prices
                char_list = []
                select_options = []
                
                for i, item in enumerate(inventory_items[:10]):
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(item['rarity'], '◆')
                    
                    # Calculate actual sell price with bonuses
                    base_price = item['value']
                    set_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
                    coin_multiplier = set_bonuses.get('coin_boost', 1.0)
                    price_with_set_bonus = int(base_price * coin_multiplier)
                    final_price = await self.bot.db.apply_equipment_bonuses_to_coins(self.user_id, price_with_set_bonus)
                    
                    char_info = (f"{rarity_emoji} **{item['character_name']}** "
                               f"({item['anime']})\n"
                               f"   🪙 Prix de vente: {final_price:,} pièces "
                               f"• Quantité: {item['count']}")
                    char_list.append(char_info)
                    
                    # Add to select options (max 25)
                    if len(select_options) < 25:
                        # Use standard emojis instead of custom ones
                        emoji_map = {
                            'Mythic': '🔸',
                            'Legendary': '🔹', 
                            'Epic': '🔷',
                            'Rare': '🔺',
                            'Common': '⚫'
                        }
                        safe_emoji = emoji_map.get(item['rarity'], '⚫')
                        
                        select_options.append(
                            discord.SelectOption(
                                label=f"{item['character_name'][:50]}",
                                description=f"{item['anime'][:50]} - {item['value']:,} pièces",
                                value=str(item['inventory_id']),
                                emoji=safe_emoji
                            )
                        )
                
                # Prevent embed overflow by truncating character list
                char_display = "\n".join(char_list) if char_list else "Aucun personnage trouvé"
                embed.add_field(
                    name=f"🎭 Vos Personnages (Page {self.current_page})",
                    value=truncate_field_value(char_display, 1000),
                    inline=False
                )
                
                # Update select menu
                if hasattr(self, 'character_select'):
                    if select_options:
                        self.character_select.options = select_options
                        self.character_select.disabled = False
                    else:
                        # Provide default option when no characters available
                        self.character_select.options = [
                            discord.SelectOption(
                                label="Aucun personnage disponible",
                                description="Votre inventaire est vide",
                                value="empty",
                                emoji="📭"
                            )
                        ]
                        self.character_select.disabled = True
            
            embed.set_footer(text="Shadow Roll • Sélectionnez un personnage à vendre")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating sell embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger l'interface de vente.",
                color=0xFF0000
            )
    
    @discord.ui.select(
        placeholder="Choisissez un personnage à vendre...",
        min_values=1,
        max_values=1,
        row=0
    )
    async def character_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle character selection"""
        try:
            inventory_id = int(select.values[0])
            
            # Get character details
            inventory_items = await self.bot.db.get_player_sellable_inventory(
                self.user_id, 1, 100)
            
            selected_char = None
            for item in inventory_items:
                if item['inventory_id'] == inventory_id:
                    selected_char = item
                    break
            
            if not selected_char:
                await interaction.response.send_message(
                    "❌ Personnage non trouvé!", ephemeral=True)
                return
            
            # Create confirmation embed with bonus calculation
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(selected_char['rarity'], '◆')
            rarity_color = BotConfig.RARITY_COLORS.get(selected_char['rarity'], 0x808080)
            
            # Calculate actual sell price with bonuses
            base_price = selected_char['value']
            set_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
            coin_multiplier = set_bonuses.get('coin_boost', 1.0)
            price_with_set_bonus = int(base_price * coin_multiplier)
            final_price = await self.bot.db.apply_equipment_bonuses_to_coins(self.user_id, price_with_set_bonus)
            
            bonus_text = ""
            if final_price > base_price:
                bonus_percentage = ((final_price / base_price) - 1) * 100
                bonus_text = f"\n💎 Bonus appliqués: +{bonus_percentage:.1f}%"
            
            confirm_embed = discord.Embed(
                title="⚠️ Confirmation de Vente",
                description=(f"Êtes-vous sûr de vouloir vendre ?\n\n"
                           f"{rarity_emoji} **{selected_char['character_name']}**\n"
                           f"📺 {selected_char['anime']}\n"
                           f"🪙 Prix de base: **{base_price:,}** pièces\n"
                           f"🪙 Prix final: **{final_price:,}** pièces{bonus_text}"),
                color=rarity_color
            )
            
            if selected_char['image_url']:
                confirm_embed.set_thumbnail(url=selected_char['image_url'])
            
            confirm_embed.add_field(
                name="⚠️ Attention",
                value="Cette action est **irréversible** !",
                inline=False
            )
            
            # Create confirmation view
            confirm_view = SellConfirmView(self.bot, self.user_id, inventory_id, selected_char)
            
            await interaction.response.edit_message(embed=confirm_embed, view=confirm_view)
            
        except Exception as e:
            logger.error(f"Error in character selection: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la sélection!", ephemeral=True)
    
    @discord.ui.button(label="◀️ Précédent", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            embed = await self.create_sell_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Suivant ▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next page"""
        self.current_page += 1
        embed = await self.create_sell_embed()
        # Check if page has content
        inventory_items = await self.bot.db.get_player_sellable_inventory(
            self.user_id, self.current_page, 10)
        if not inventory_items:
            self.current_page -= 1  # Go back if no content
            await interaction.response.defer()
        else:
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔙 Retour au Menu", style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Return to main menu"""
        from modules.menu import ShadowMenuView, ProfileView
        menu_view = ShadowMenuView(self.bot, self.user_id)
        profile_view = ProfileView(self.bot, self.user_id)
        embed = await profile_view.create_main_menu_embed()
        await interaction.response.edit_message(embed=embed, view=menu_view)


class SellConfirmView(discord.ui.View):
    """Confirmation view for selling characters"""
    
    def __init__(self, bot, user_id: int, inventory_id: int, character_data: Dict):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.inventory_id = inventory_id
        self.character_data = character_data
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    @discord.ui.button(label="✅ Confirmer la Vente", style=discord.ButtonStyle.success)
    async def confirm_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm the sale"""
        try:
            # Execute the sale
            success, message, coins_earned = await self.bot.db.sell_character(
                self.user_id, self.inventory_id)
            
            if success:
                # Create success embed
                embed = discord.Embed(
                    title="✅ Vente Réussie!",
                    description=message,
                    color=0x00FF00
                )
                
                # Get updated player coins
                player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
                embed.add_field(
                    name="🪙 Nouveau Solde",
                    value=f"{BotConfig.CURRENCY_EMOJI} {player.coins:,}",
                    inline=True
                )
                
                embed.add_field(
                    name="🎲 Invocations Possibles",
                    value=f"{player.coins // BotConfig.REROLL_COST}",
                    inline=True
                )
                
                # Return to sell menu
                sell_view = SellView(self.bot, self.user_id)
                embed_sell = await sell_view.create_sell_embed()
                
                await interaction.response.edit_message(embed=embed, view=None)
                await interaction.followup.send(embed=embed_sell, view=sell_view, ephemeral=False)
                
            else:
                await interaction.response.send_message(f"❌ {message}", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error confirming sell: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la vente!", ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the sale"""
        sell_view = SellView(self.bot, self.user_id)
        embed = await sell_view.create_sell_embed()
        await interaction.response.edit_message(embed=embed, view=sell_view)


async def setup_sell_commands(bot):
    """Setup sell-related commands"""
    
    @bot.tree.command(name="sell", description="Vendre des personnages contre des pièces")
    async def sell_slash(interaction: discord.Interaction):
        """Sell characters slash command"""
        try:
            await interaction.response.defer()
            
            # Check if user is banned
            if await bot.db.is_banned(interaction.user.id):
                await interaction.followup.send(
                    BotConfig.MESSAGES['banned'], ephemeral=True)
                return
            
            # Create sell view
            sell_view = SellView(bot, interaction.user.id)
            embed = await sell_view.create_sell_embed()
            
            await interaction.followup.send(embed=embed, view=sell_view)
            
        except Exception as e:
            logger.error(f"Error in sell command: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de l'ouverture de l'interface de vente!",
                ephemeral=True)