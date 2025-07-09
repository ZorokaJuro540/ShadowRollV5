"""
Shop system for Shadow Roll Bot
Comprehensive shop interface with luck potions and item management
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from core.config import BotConfig
from modules.utils import format_number

logger = logging.getLogger(__name__)

class ShopView(discord.ui.View):
    """Enhanced shop interface with item categories and purchase system"""

    def __init__(self, bot, user_id: int, category: str = 'all', page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_category = category
        self.current_page = page
        self.items_per_page = 4

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def get_category_color(self, category: str) -> int:
        """Get color based on shop category"""
        colors = {
            'luck_potion': 0x9b59b6,  # Purple
            'utility': 0x3498db,      # Blue
            'all': 0xf39c12           # Orange
        }
        return colors.get(category, 0xf39c12)

    def get_category_icon(self, item_type: str) -> str:
        """Get icon for item type"""
        icons = {
            'luck_potion': '🧪',
            'utility': '🪙',
            'special': '🔮',
            'consumable': '💊'
        }
        return icons.get(item_type, '🛒')

    def filter_items_by_category(self, items: list) -> list:
        """Filter items by selected category"""
        if self.current_category == 'all':
            return items
        return [item for item in items if item['item_type'] == self.current_category]

    async def create_shop_embed(self) -> discord.Embed:
        """Create shop embed with items and purchase options"""
        try:
            # Get all shop items
            all_items = await self.bot.db.get_shop_items()
            
            if not all_items:
                embed = discord.Embed(
                    title="🛒 ═══════〔 B O U T I Q U E 〕═══════ 🛒",
                    description="```\n⚠️  Boutique temporairement fermée\n```",
                    color=self.get_category_color('all'))
                return embed

            # Filter by category
            items = self.filter_items_by_category(all_items)
            
            # Calculate pagination
            total_pages = max(1, (len(items) + self.items_per_page - 1) // self.items_per_page)
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(items))
            page_items = items[start_idx:end_idx]

            # Get player coins
            player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")

            # Create category title
            category_names = {
                'all': 'TOUTE LA BOUTIQUE',
                'luck_potion': 'POTIONS DE CHANCE',
                'utility': 'OBJETS UTILITAIRES'
            }
            category_title = category_names.get(self.current_category, 'BOUTIQUE')

            embed = discord.Embed(
                title=f"🛒 ═══════〔 {category_title} 〕═══════ 🛒",
                color=self.get_category_color(self.current_category))

            # Player status
            embed.description = f"```\n🪙 Votre Fortune: {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}\n📦 Articles disponibles: {len(items)}\n```"

            # Add items to embed with cleaner formatting
            if not page_items:
                embed.add_field(
                    name="📭 Aucun article disponible",
                    value="```\nChangez de catégorie pour voir d'autres articles\n```",
                    inline=False)
            else:
                # Create a clean item list format
                items_text = "```\n"
                for i, item in enumerate(page_items, 1):
                    icon = item['icon']
                    price_status = "✅" if player.coins >= item['price'] else "❌"
                    
                    # Effect summary
                    effect_summary = ""
                    if item['effect_type'] and 'boost' in item['effect_type']:
                        boost_pct = int(item['effect_value'] * 100)
                        effect_summary = f" (+{boost_pct}%)"
                    elif item['effect_type'] == 'guaranteed_rare':
                        effect_summary = " (Rare garanti)"
                    elif item['effect_type'] == 'guaranteed_epic':
                        effect_summary = " (Epic garanti)"
                    elif item['effect_type'] == 'coin_boost':
                        multiplier = int(item['effect_value'])
                        effect_summary = f" (x{multiplier} coins)"
                    
                    # Duration
                    duration = ""
                    if item['duration_minutes'] > 0:
                        hours = item['duration_minutes'] // 60
                        minutes = item['duration_minutes'] % 60
                        duration = f" - {hours}h{minutes:02d}m" if hours > 0 else f" - {minutes}m"
                    
                    items_text += f"{i}. {icon} {item['name']}{effect_summary}{duration}\n"
                    items_text += f"    Prix: {format_number(item['price'])} {BotConfig.CURRENCY_EMOJI} {price_status}\n\n"
                
                items_text += "```"
                
                embed.add_field(
                    name=f"🛒 Articles disponibles ({len(page_items)})",
                    value=items_text,
                    inline=False)
                
                # Add purchase instructions
                embed.add_field(
                    name="💡 Comment acheter",
                    value="```\nCliquez sur 🛒 Acheter puis entrez le numéro de l'article\n✅ = Vous pouvez l'acheter  |  ❌ = Fonds insuffisants\n```",
                    inline=False)

            # Enhanced footer
            footer_text = f"Shadow Roll • Page {self.current_page}/{total_pages} • Boutique"
            if self.current_category != 'all':
                footer_text += f" • {category_title}"
            embed.set_footer(text=footer_text)
            
            return embed

        except Exception as e:
            logger.error(f"Error creating shop embed: {e}")
            return discord.Embed(
                title="❌ Erreur Boutique",
                description="```\n⚠️  Impossible de charger la boutique\nVeuillez réessayer plus tard\n```",
                color=0xff0000)

    # Category filter buttons (Row 0)
    @discord.ui.button(label='🛒 Tous', style=discord.ButtonStyle.secondary, row=0)
    async def filter_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'all'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🧪 Potions', style=discord.ButtonStyle.secondary, row=0)
    async def filter_potions(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'luck_potion'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🪙 Économie', style=discord.ButtonStyle.secondary, row=0)
    async def filter_utility(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'utility'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🔮 Spéciaux', style=discord.ButtonStyle.secondary, row=0)
    async def filter_special(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'special'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    # Navigation and purchase buttons (Row 1)
    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.primary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='🛒 Acheter', style=discord.ButtonStyle.success, row=1)
    async def purchase_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PurchaseModal(self.bot, self.user_id, self))

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.primary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        all_items = await self.bot.db.get_shop_items()
        items = self.filter_items_by_category(all_items)
        total_pages = max(1, (len(items) + self.items_per_page - 1) // self.items_per_page)

        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🎒 Inventaire', style=discord.ButtonStyle.secondary, row=1)
    async def view_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.inventory import EnhancedInventoryView
        view = EnhancedInventoryView(self.bot, self.user_id)
        embed = await view.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🏠 Menu', style=discord.ButtonStyle.danger, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, ProfileView
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await ProfileView(self.bot, self.user_id).create_main_menu_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class PurchaseModal(discord.ui.Modal):
    """Modal for purchasing items from the shop"""

    def __init__(self, bot, user_id: int, shop_view: ShopView):
        super().__init__(title="🛒 Acheter un Article")
        self.bot = bot
        self.user_id = user_id
        self.shop_view = shop_view

    item_number = discord.ui.TextInput(
        label='Numéro de l\'article à acheter',
        placeholder='Entrez le numéro affiché (ex: 1, 2, 3...)',
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate input
            try:
                selection = int(self.item_number.value)
            except ValueError:
                await interaction.response.send_message(
                    "❌ Veuillez entrer un numéro valide!", ephemeral=True)
                return

            # Get current page items
            all_items = await self.bot.db.get_shop_items()
            items = self.shop_view.filter_items_by_category(all_items)
            
            start_idx = (self.shop_view.current_page - 1) * self.shop_view.items_per_page
            end_idx = min(start_idx + self.shop_view.items_per_page, len(items))
            page_items = items[start_idx:end_idx]

            if selection < 1 or selection > len(page_items):
                await interaction.response.send_message(
                    f"❌ Numéro invalide! Choisissez entre 1 et {len(page_items)}", ephemeral=True)
                return

            selected_item = page_items[selection - 1]
            
            # Check if player can afford it
            player = await self.bot.db.get_or_create_player(self.user_id, interaction.user.display_name)
            if player.coins < selected_item['price']:
                needed = selected_item['price'] - player.coins
                await interaction.response.send_message(
                    f"❌ Fonds insuffisants!\n🪙 Prix: {format_number(selected_item['price'])} {BotConfig.CURRENCY_EMOJI}\n🪙 Il vous manque: {format_number(needed)} {BotConfig.CURRENCY_EMOJI}", 
                    ephemeral=True)
                return

            # Purchase the item
            success = await self.bot.db.purchase_item(self.user_id, selected_item['id'])
            
            if success:
                # Update shop display
                embed = await self.shop_view.create_shop_embed()
                await interaction.response.edit_message(embed=embed, view=self.shop_view)
                
                # Send success message
                await interaction.followup.send(
                    f"🎉 **Achat réussi!**\n{selected_item['icon']} **{selected_item['name']}** ajouté à votre inventaire!\n🪙 Nouveau solde: {format_number(player.coins - selected_item['price'])} {BotConfig.CURRENCY_EMOJI}",
                    ephemeral=True)
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors de l'achat. Veuillez réessayer.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in purchase modal: {e}")
            await interaction.response.send_message(
                "❌ Une erreur est survenue lors de l'achat.", ephemeral=True)