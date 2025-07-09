"""
Enhanced inventory system for Shadow Roll Bot
Dual-category inventory: Collections (characters) and Items (consumables)
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from core.config import BotConfig
from modules.utils import format_number

logger = logging.getLogger(__name__)

class EnhancedInventoryView(discord.ui.View):
    """Enhanced inventory with Collections and Items categories"""

    def __init__(self, bot, user_id: int, category: str = 'collections', page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_category = category
        self.current_page = page
        self.items_per_page = 8 if category == 'collections' else 6

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def get_category_color(self, category: str) -> int:
        """Get color based on inventory category"""
        colors = {
            'collections': 0xe74c3c,  # Red for character collections
            'items': 0x9b59b6,       # Purple for consumable items
            'effects': 0x27ae60      # Green for active effects
        }
        return colors.get(category, 0x34495e)

    async def create_inventory_embed(self) -> discord.Embed:
        """Create inventory embed based on current category"""
        try:
            player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
            
            if self.current_category == 'collections':
                return await self.create_collections_embed(player)
            elif self.current_category == 'items':
                return await self.create_items_embed(player)
            elif self.current_category == 'effects':
                return await self.create_effects_embed(player)
            else:
                return await self.create_collections_embed(player)
                
        except Exception as e:
            logger.error(f"Error creating inventory embed: {e}")
            return discord.Embed(
                title="❌ Erreur Inventaire",
                description="```\n⚠️  Impossible de charger l'inventaire\nVeuillez réessayer plus tard\n```",
                color=0xff0000)

    async def create_collections_embed(self, player) -> discord.Embed:
        """Create collections embed with consistent Shadow Roll style"""
        inventory = await self.bot.db.get_player_inventory(
            self.user_id, 
            page=self.current_page, 
            limit=self.items_per_page
        )
        
        stats = await self.bot.db.get_inventory_stats(self.user_id)
        total_pages = max(1, (stats.get('total_characters', 0) + self.items_per_page - 1) // self.items_per_page)

        embed = discord.Embed(
            title="🎴 ═══════〔 C O L L E C T I O N 〕═══════ 🎴",
            color=BotConfig.RARITY_COLORS['Mythic'])

        # Stats header like menu style
        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}\n"
            f"🎴 Personnages: {stats.get('total_characters', 0)}\n"
            f"💎 Valeur totale: {format_number(stats.get('total_value', 0))} {BotConfig.CURRENCY_EMOJI}\n"
            f"```"
        )

        if not inventory:
            embed.add_field(
                name="📭 ═══〔 Collection Vide 〕═══ 📭",
                value="```\nUtilisez la commande /roll pour commencer\nvotre collection de personnages!\n```",
                inline=False)
        else:
            # Group by rarity for organized display
            rarity_groups = {}
            for item in inventory:
                rarity = item.get('rarity', 'Common')
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(item)

            # Display by rarity order like menu style
            rarity_order = ['Secret', 'Fusion', 'Titan', 'Evolve', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']
            for rarity in rarity_order:
                if rarity in rarity_groups:
                    characters = rarity_groups[rarity]
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    
                    char_list = []
                    for char in characters[:5]:  # Show 5 per rarity
                        char_list.append(f"{emoji} {char['character_name']} ({char['anime']})")
                    
                    if len(characters) > 5:
                        char_list.append(f"... et {len(characters) - 5} autres")
                    
                    embed.add_field(
                        name=f"{emoji} ═══〔 {rarity} 〕═══ {emoji} ({len(characters)})",
                        value="```\n" + "\n".join(char_list) + "\n```",
                        inline=True)

        # Footer consistent with menu style
        embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION} • Page {self.current_page}/{total_pages}")
        return embed

    async def create_items_embed(self, player) -> discord.Embed:
        """Create items embed with consistent Shadow Roll style"""
        # Obtenir les objets de la boutique du joueur
        if hasattr(self.bot.db, 'get_player_shop_items'):
            shop_items = await self.bot.db.get_player_shop_items(self.user_id)
            items = await self.convert_shop_items_to_display(shop_items)
        else:
            items = await self.bot.db.get_player_items(self.user_id)
        
        # Calculate pagination for items
        total_pages = max(1, (len(items) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(items))
        page_items = items[start_idx:end_idx]

        embed = discord.Embed(
            title="🎒 ═══════〔 O B J E T S 〕═══════ 🎒",
            color=BotConfig.RARITY_COLORS['Epic'])

        # Stats header like menu style
        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}\n"
            f"🎒 Objets: {len(items)}\n"
            f"```"
        )

        if not page_items:
            embed.add_field(
                name="📭 ═══〔 Sac Vide 〕═══ 📭",
                value="```\nVisitez la boutique pour acheter\ndes objets utiles!\n```",
                inline=False)
        else:
            # Display items with menu style formatting
            for i, item in enumerate(page_items, start_idx + 1):
                duration_text = ""
                if item['duration_minutes'] > 0:
                    hours = item['duration_minutes'] // 60
                    minutes = item['duration_minutes'] % 60
                    duration_text = f"Durée: {hours}h{minutes:02d}m" if hours > 0 else f"Durée: {minutes}m"
                
                embed.add_field(
                    name=f"{item['icon']} ═══〔 {item['name']} 〕═══ {item['icon']}",
                    value=(
                        f"```\n"
                        f"Quantité: {item['quantity']}\n"
                        f"{duration_text}\n"
                        f"Numéro: {i}\n"
                        f"```"
                    ),
                    inline=True)

        # Usage info with menu style
        if page_items:
            embed.add_field(
                name="💡 ═══〔 Utilisation 〕═══ 💡",
                value="```\nCliquez 🔥 Utiliser puis entrez\nle numéro de l'objet\n```",
                inline=False)

        embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION} • Page {self.current_page}/{total_pages}")
        return embed
    
    async def convert_shop_items_to_display(self, shop_items: List[Dict]) -> List[Dict]:
        """Convertir les objets de la boutique pour l'affichage"""
        from modules.shop_new import ModernShopView
        shop_view = ModernShopView(self.bot, self.user_id)
        all_shop_items = shop_view.get_shop_items()
        
        display_items = []
        for player_item in shop_items:
            # Trouver les détails de l'objet
            shop_item = next((item for item in all_shop_items if item['id'] == player_item['item_id']), None)
            if shop_item:
                display_items.append({
                    'player_item_id': player_item['item_id'],
                    'quantity': player_item['quantity'],
                    'name': shop_item['name'],
                    'description': shop_item['description'],
                    'item_type': shop_item['category'],
                    'effect_type': shop_item['effect'],
                    'effect_value': shop_item.get('amount', 1),
                    'duration_minutes': shop_item.get('duration', 0) // 60,
                    'icon': shop_item['icon']
                })
        return display_items

    async def create_effects_embed(self, player) -> discord.Embed:
        """Create effects embed showing active effects"""
        effects = await self.bot.db.get_active_effects(self.user_id)

        embed = discord.Embed(
            title="✨ ═══════〔 E F F E T S   A C T I F S 〕═══════ ✨",
            color=self.get_category_color('effects'))

        embed.description = (
            f"```\n"
            f"👤 {player.username}\n"
            f"🪙 Shadow Coins: {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}\n"
            f"✨ Effets actifs: {len(effects)}"
            f"\n```"
        )

        if not effects:
            embed.add_field(
                name="🪙 Aucun effet actif",
                value="Utilisez des potions depuis votre inventaire pour activer des bonus!",
                inline=False)
        else:
            effect_descriptions = {
                'rare_boost': '📈 Bonus Personnages Rares',
                'epic_boost': '📈 Bonus Personnages Épiques', 
                'legendary_boost': '📈 Bonus Personnages Légendaires',
                'mythical_boost': '📈 Bonus Personnages Mythiques',
                'all_boost': '🪙 Bonus Toutes Raretés',
                'mega_boost': '💫 Méga Bonus',
                'coin_boost': '🪙 Multiplicateur Coins',
                'cooldown_skip': '⚡ Ignore Cooldown'
            }

            # Calculate combined effects display
            combined_bonuses = await self.bot.db.calculate_luck_bonus(self.user_id)
            
            # Show combined effects first
            if combined_bonuses['total'] > 0:
                embed.add_field(
                    name="🎯 Effets Actifs",
                    value=(
                        f"🍀 **Bonus Chance:** +{combined_bonuses['total']}%\n"
                        f"◇ **Rare:** +{combined_bonuses['rare']}%\n"
                        f"◈ **Epic:** +{combined_bonuses['epic']}%\n"
                        f"◉ **Legendary:** +{combined_bonuses['legendary']}%\n"
                        f"⬢ **Mythic:** +{combined_bonuses['mythical']}%\n"
                        f"🔱 **Titan:** +{combined_bonuses['titan']}%\n"
                        f"⭐ **Fusion:** +{combined_bonuses['duo']}%"
                    ),
                    inline=False
                )

            # Show individual potions with time remaining
            for effect in effects:
                effect_name = effect_descriptions.get(effect['effect_type'], f"✨ {effect['effect_type']}")
                
                # Calculate remaining time
                try:
                    expires_at = datetime.fromisoformat(effect['expires_at'])
                    remaining = expires_at - datetime.now()
                    
                    if remaining.total_seconds() > 0:
                        hours = int(remaining.total_seconds() // 3600)
                        minutes = int((remaining.total_seconds() % 3600) // 60)
                        time_text = f"{hours}h{minutes:02d}m" if hours > 0 else f"{minutes}m"
                        
                        # Effect value formatting - show multiplier instead of percentage
                        if 'boost' in effect['effect_type']:
                            multiplier = effect['effect_value'] + 1  # Convert to multiplier
                            value_text = f"x{multiplier:.1f} chances"
                        else:
                            value_text = f"x{effect['effect_value']}"
                        
                        embed.add_field(
                            name=f"{effect_name} ⏱️ {time_text}",
                            value=f"🎯 **Effet:** {value_text}",
                            inline=True)
                except:
                    continue

        embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION} • Effets Actifs")
        return embed

    # Category navigation buttons (Row 0)
    @discord.ui.button(label='🎴 Collections', style=discord.ButtonStyle.secondary, row=0)
    async def view_collections(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'collections'
        self.current_page = 1
        self.items_per_page = 8
        await interaction.response.defer()
        embed = await self.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🎒 Objets', style=discord.ButtonStyle.secondary, row=0)
    async def view_items(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'items'
        self.current_page = 1
        self.items_per_page = 6
        await interaction.response.defer()
        embed = await self.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='✨ Effets', style=discord.ButtonStyle.secondary, row=0)
    async def view_effects(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'effects'
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    # Navigation and action buttons (Row 1)
    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.primary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_inventory_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='🔥 Utiliser', style=discord.ButtonStyle.success, row=1)
    async def use_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_category != 'items':
            await interaction.response.send_message(
                "Allez dans la catégorie **Objets** pour utiliser des items!", ephemeral=True)
            return
        
        await interaction.response.send_modal(UseItemModal(self.bot, self.user_id, self))

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.primary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Calculate total pages based on current category
        if self.current_category == 'collections':
            stats = await self.bot.db.get_inventory_stats(self.user_id)
            total_items = stats.get('total_characters', 0)
        elif self.current_category == 'items':
            items = await self.bot.db.get_player_items(self.user_id)
            total_items = len(items)
        else:
            total_items = 0

        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)

        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_inventory_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message(
                "Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🛒 Boutique', style=discord.ButtonStyle.secondary, row=1)
    async def view_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.shop import ShopView
        view = ShopView(self.bot, self.user_id)
        embed = await view.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=view)

        @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class UseItemModal(discord.ui.Modal):
    """Modal for using items from inventory"""

    def __init__(self, bot, user_id: int, inventory_view: EnhancedInventoryView):
        super().__init__(title="🔥 Utiliser un Objet")
        self.bot = bot
        self.user_id = user_id
        self.inventory_view = inventory_view

    item_number = discord.ui.TextInput(
        label='Numéro de l\'objet à utiliser',
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
            items = await self.bot.db.get_player_items(self.user_id)
            start_idx = (self.inventory_view.current_page - 1) * self.inventory_view.items_per_page
            end_idx = min(start_idx + self.inventory_view.items_per_page, len(items))
            page_items = items[start_idx:end_idx]

            if selection < 1 or selection > len(page_items):
                await interaction.response.send_message(
                    f"❌ Numéro invalide! Choisissez entre 1 et {len(page_items)}", ephemeral=True)
                return

            selected_item = page_items[selection - 1]
            
            # Use the item
            success = await self.bot.db.use_item(self.user_id, selected_item['player_item_id'])
            
            if success:
                # Update inventory display
                embed = await self.inventory_view.create_inventory_embed()
                await interaction.response.edit_message(embed=embed, view=self.inventory_view)
                
                # Create effect description
                effect_msg = f"🎉 **{selected_item['name']}** utilisé avec succès!"
                if selected_item['duration_minutes'] > 0:
                    hours = selected_item['duration_minutes'] // 60
                    minutes = selected_item['duration_minutes'] % 60
                    duration_text = f"{hours}h{minutes:02d}m" if hours > 0 else f"{minutes}m"
                    effect_msg += f"\n✨ Effet actif pendant **{duration_text}**!"
                
                if 'boost' in selected_item.get('effect_type', ''):
                    boost_pct = int(selected_item['effect_value'] * 100)
                    effect_msg += f"\n🎯 Vos chances sont augmentées de **+{boost_pct}%**!"
                
                await interaction.followup.send(effect_msg, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors de l'utilisation de l'objet.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error in use item modal: {e}")
            await interaction.response.send_message(
                "❌ Une erreur est survenue lors de l'utilisation.", ephemeral=True)