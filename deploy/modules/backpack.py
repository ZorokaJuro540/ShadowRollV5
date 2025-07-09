"""
Backpack System for Shadow Roll Bot
Unified inventory system combining Collections, Potions, Titles, Equipment, and Effects
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.equipment_fix import fix_equipment_before_operation

logger = logging.getLogger(__name__)

class BackpackView(discord.ui.View):
    """Unified Backpack system combining all player items and collections"""

    def __init__(self, bot, user_id: int, category: str = 'characters', page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_category = category
        self.current_page = page
        self.items_per_page = self.get_items_per_page()

    def get_items_per_page(self) -> int:
        """Get items per page based on category"""
        return {
            'characters': 8,
            'potions': 6,
            'titles': 5,
            'equipment': 3,
            'effects': 6
        }.get(self.current_category, 6)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def get_category_color(self, category: str) -> int:
        """Get color based on backpack category"""
        colors = {
            'characters': 0xe74c3c,    # Red for character collections
            'potions': 0x9b59b6,       # Purple for potions
            'titles': 0xf39c12,        # Orange for titles
            'equipment': 0x2ecc71,     # Green for equipment
            'effects': 0x3498db        # Blue for active effects
        }
        return colors.get(category, 0x34495e)

    async def create_backpack_embed(self) -> discord.Embed:
        """Create backpack embed based on current category"""
        try:
            if self.current_category == 'characters':
                return await self.create_characters_embed()
            elif self.current_category == 'potions':
                return await self.create_potions_embed()
            elif self.current_category == 'titles':
                return await self.create_titles_embed()
            elif self.current_category == 'equipment':
                return await self.create_equipment_embed()
            elif self.current_category == 'effects':
                return await self.create_effects_embed()
            else:
                return await self.create_characters_embed()
                
        except Exception as e:
            logger.error(f"Error creating backpack embed: {e}")
            return discord.Embed(
                title="❌ Erreur Backpack",
                description="```\n⚠️  Impossible de charger le backpack\nVeuillez réessayer plus tard\n```",
                color=0xff0000)

    async def create_characters_embed(self) -> discord.Embed:
        """Create characters section of backpack"""
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        inventory = await self.bot.db.get_player_inventory(
            self.user_id, 
            page=self.current_page, 
            limit=self.items_per_page
        )
        
        stats = await self.bot.db.get_inventory_stats(self.user_id)
        total_pages = max(1, (stats.get('total_characters', 0) + self.items_per_page - 1) // self.items_per_page)

        embed = discord.Embed(
            title="🎒 ═══════〔 B A C K P A C K   •   P E R S O N N A G E S 〕═══════ 🎒",
            color=self.get_category_color('characters'))

        # Stats header
        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)}\n"
            f"🎴 Personnages: {stats.get('total_characters', 0)}\n"
            f"💎 Valeur totale: {format_number(stats.get('total_value', 0))}\n"
            f"```"
        )

        if not inventory:
            embed.add_field(
                name="📭 ═══〔 Aucun Personnage 〕═══ 📭",
                value="```\nUtilisez /roll pour commencer\nvotre collection!\n```",
                inline=False)
        else:
            # Group by rarity for organized display
            rarity_groups = {}
            for item in inventory:
                rarity = item.get('rarity', 'Common')
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(item)

            # Display by rarity order
            rarity_order = ['Secret', 'Fusion', 'Titan', 'Evolve', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']
            for rarity in rarity_order:
                if rarity in rarity_groups:
                    characters = rarity_groups[rarity]
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    
                    char_list = []
                    for char in characters[:5]:  # Show 5 per rarity
                        count_text = f" x{char['count']}" if char.get('count', 1) > 1 else ""
                        char_list.append(f"{emoji} {char['character_name']} ({char['anime']}){count_text}")
                    
                    if len(characters) > 5:
                        char_list.append(f"... et {len(characters) - 5} autres")
                    
                    embed.add_field(
                        name=f"{emoji} ═══〔 {rarity} 〕═══ {emoji} ({len(characters)})",
                        value="```\n" + "\n".join(char_list) + "\n```",
                        inline=True)

        embed.set_footer(text=f"Shadow Roll • Page {self.current_page}/{total_pages}")
        return embed

    async def create_potions_embed(self) -> discord.Embed:
        """Create potions section of backpack"""
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        
        # Get player's shop items (potions)
        if hasattr(self.bot.db, 'get_player_shop_items'):
            shop_items = await self.bot.db.get_player_shop_items(self.user_id)
            potions = await self.convert_shop_items_to_potions(shop_items)
        else:
            potions = await self.bot.db.get_player_items(self.user_id)
        
        # Calculate pagination
        total_pages = max(1, (len(potions) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(potions))
        page_potions = potions[start_idx:end_idx]

        embed = discord.Embed(
            title="🎒 ═══════〔 B A C K P A C K   •   P O T I O N S 〕═══════ 🎒",
            color=self.get_category_color('potions'))

        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)}\n"
            f"🧪 Potions: {len(potions)}\n"
            f"```"
        )

        if not page_potions:
            embed.add_field(
                name="📭 ═══〔 Aucune Potion 〕═══ 📭",
                value="```\nVisitez la boutique pour acheter\ndes potions utiles!\n```",
                inline=False)
        else:
            # Display potions with details
            for i, potion in enumerate(page_potions, start_idx + 1):
                duration_text = ""
                if potion.get('duration_minutes', 0) > 0:
                    hours = potion['duration_minutes'] // 60
                    minutes = potion['duration_minutes'] % 60
                    duration_text = f"Durée: {hours}h{minutes:02d}m" if hours > 0 else f"Durée: {minutes}m"
                
                embed.add_field(
                    name=f"{potion.get('icon', '🧪')} ═══〔 {potion['name']} 〕═══",
                    value=(
                        f"```\n"
                        f"Quantité: {potion.get('quantity', 1)}\n"
                        f"{duration_text}\n"
                        f"ID: {i}\n"
                        f"```"
                    ),
                    inline=True)

        if page_potions:
            embed.add_field(
                name="💡 ═══〔 Utilisation 〕═══ 💡",
                value="```\nCliquez 🧪 Utiliser pour activer\nune potion par son ID\n```",
                inline=False)

        embed.set_footer(text=f"Shadow Roll • Page {self.current_page}/{total_pages}")
        return embed

    async def create_titles_embed(self) -> discord.Embed:
        """Create titles section of backpack"""
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        
        # Check for new title unlocks
        newly_unlocked = await self.bot.db.check_and_unlock_titles(self.user_id)
        
        # Get all titles for player
        all_titles = await self.bot.db.get_player_titles(self.user_id)
        
        # Calculate pagination
        total_pages = max(1, (len(all_titles) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(all_titles))
        page_titles = all_titles[start_idx:end_idx]

        # Count unlocked titles
        unlocked_count = sum(1 for title in all_titles if title['is_unlocked'])
        total_count = len(all_titles)

        embed = discord.Embed(
            title="🎒 ═══════〔 B A C K P A C K   •   T I T R E S 〕═══════ 🎒",
            color=self.get_category_color('titles'))

        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)}\n"
            f"🏆 Titres: {unlocked_count}/{total_count} débloqués\n"
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
                name="📭 ═══〔 Aucun Titre 〕═══ 📭",
                value="```\nComplétez des objectifs pour\ndébloquer des titres!\n```",
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

        embed.set_footer(text=f"Shadow Roll • Page {self.current_page}/{total_pages}")
        return embed

    async def create_equipment_embed(self) -> discord.Embed:
        """Create equipment section of backpack"""
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        
        # Fix equipment before displaying
        await fix_equipment_before_operation(self.bot.db, self.user_id)
        
        equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
        available_chars = await self.bot.db.get_equippable_characters(self.user_id)
        
        embed = discord.Embed(
            title="🎒 ═══════〔 B A C K P A C K   •   É Q U I P E M E N T 〕═══════ 🎒",
            color=self.get_category_color('equipment'))

        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)}\n"
            f"⚔️ Équipés: {len(equipped_chars)}/3\n"
            f"🎴 Disponibles: {len(available_chars)}\n"
            f"```"
        )

        # Show equipped characters
        if equipped_chars:
            equipped_text = ""
            for char in equipped_chars:
                emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                bonus_text = self._format_character_bonus(char)
                char_name = char.get('character_name', char.get('name', 'Inconnu'))
                anime_name = char.get('anime', 'Série Inconnue')
                equipped_text += f"{emoji} **{char_name}** ({anime_name})\n"
                equipped_text += f"   💫 {bonus_text}\n\n"
            
            embed.add_field(
                name="⚔️ ═══〔 Personnages Équipés 〕═══ ⚔️",
                value=equipped_text[:1020] + "..." if len(equipped_text) > 1020 else equipped_text,
                inline=False)
        else:
            embed.add_field(
                name="⚔️ ═══〔 Aucun Équipement 〕═══ ⚔️",
                value="```\nÉquipez des personnages Titan/Fusion/Secret\npour des bonus passifs globaux!\n```",
                inline=False)

        # Show available characters for equipment
        if available_chars:
            available_text = ""
            for char in available_chars[:5]:  # Show first 5
                emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                bonus_text = self._format_character_bonus(char)
                char_name = char.get('character_name', char.get('name', 'Inconnu'))
                available_text += f"{emoji} {char_name} - {bonus_text}\n"
            
            if len(available_chars) > 5:
                available_text += f"... et {len(available_chars) - 5} autres"
            
            embed.add_field(
                name="🎯 ═══〔 Disponibles pour Équipement 〕═══ 🎯",
                value=available_text[:1020] + "..." if len(available_text) > 1020 else available_text,
                inline=False)

        embed.set_footer(text=f"Shadow Roll • Équipement {len(equipped_chars)}/3")
        return embed

    async def create_effects_embed(self) -> discord.Embed:
        """Create effects section of backpack"""
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        effects = await self.bot.db.get_active_effects(self.user_id)

        embed = discord.Embed(
            title="🎒 ═══════〔 B A C K P A C K   •   E F F E T S 〕═══════ 🎒",
            color=self.get_category_color('effects'))

        embed.description = (
            f"```\n"
            f"◆ {player.username} ◆\n"
            f"🪙 Shadow Coins: {format_number(player.coins)}\n"
            f"✨ Effets actifs: {len(effects)}\n"
            f"```"
        )

        if not effects:
            embed.add_field(
                name="✨ ═══〔 Aucun Effet Actif 〕═══ ✨",
                value="```\nUtilisez des potions pour activer\ndes bonus temporaires!\n```",
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
                    name="🎯 ═══〔 Effets Combinés 〕═══ 🎯",
                    value=(
                        f"```\n"
                        f"🍀 Bonus Total: +{combined_bonuses['total']}%\n"
                        f"◇ Rare: +{combined_bonuses['rare']}%\n"
                        f"◈ Epic: +{combined_bonuses['epic']}%\n"
                        f"◉ Legendary: +{combined_bonuses['legendary']}%\n"
                        f"⬢ Mythic: +{combined_bonuses['mythical']}%\n"
                        f"🔱 Titan: +{combined_bonuses['titan']}%\n"
                        f"⭐ Fusion: +{combined_bonuses['duo']}%\n"
                        f"```"
                    ),
                    inline=False
                )

            # Show individual effects with time remaining
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
                        
                        # Effect value formatting
                        if 'boost' in effect['effect_type']:
                            multiplier = effect['effect_value'] + 1
                            value_text = f"x{multiplier:.1f} chances"
                        else:
                            value_text = f"x{effect['effect_value']}"
                        
                        embed.add_field(
                            name=f"{effect_name} ⏱️ {time_text}",
                            value=f"```\n🎯 Effet: {value_text}\n```",
                            inline=True)
                except:
                    continue

        embed.set_footer(text=f"Shadow Roll • Effets Actifs")
        return embed

    def _format_character_bonus(self, char: Dict) -> str:
        """Format character bonus text"""
        rarity = char['rarity']
        if rarity == 'Titan':
            return "+2% chances toutes raretés"
        elif rarity == 'Fusion':
            return "+5% Shadow Coins partout"
        elif rarity == 'Secret':
            return "+3% chances + 3% coins"
        elif rarity == 'Evolve':
            return "+1% chances + 2% coins"
        return "Bonus inconnu"

    async def convert_shop_items_to_potions(self, shop_items: List[Dict]) -> List[Dict]:
        """Convert shop items to potion display format"""
        from modules.shop_new import ModernShopView
        shop_view = ModernShopView(self.bot, self.user_id)
        all_shop_items = shop_view.get_shop_items()
        
        potions = []
        for player_item in shop_items:
            # Find item details
            shop_item = next((item for item in all_shop_items if item['id'] == player_item['item_id']), None)
            if shop_item:
                potions.append({
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
        return potions

    # Category navigation buttons - Row 0 (Main categories - 3 buttons max per row for visibility)
    @discord.ui.button(label='🎴 Personnages', style=discord.ButtonStyle.primary, row=0)
    async def view_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'characters'
        self.current_page = 1
        self.items_per_page = self.get_items_per_page()
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🧪 Potions', style=discord.ButtonStyle.secondary, row=0)
    async def view_potions(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'potions'
        self.current_page = 1
        self.items_per_page = self.get_items_per_page()
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏆 Titres', style=discord.ButtonStyle.secondary, row=0)
    async def view_titles(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'titles'
        self.current_page = 1
        self.items_per_page = self.get_items_per_page()
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    # Row 1 - Additional categories
    @discord.ui.button(label='⚔️ Équipement', style=discord.ButtonStyle.danger, row=1)
    async def view_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'equipment'
        self.current_page = 1
        self.items_per_page = self.get_items_per_page()
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='✨ Effets', style=discord.ButtonStyle.success, row=1)
    async def view_effects(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = 'effects'
        self.current_page = 1
        self.items_per_page = self.get_items_per_page()
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    # Navigation buttons (Row 2)
    @discord.ui.button(label='◀️ Précédent', style=discord.ButtonStyle.secondary, row=2)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_backpack_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='▶️ Suivant', style=discord.ButtonStyle.secondary, row=2)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Calculate total pages based on current category
        if self.current_category == 'characters':
            stats = await self.bot.db.get_inventory_stats(self.user_id)
            total_items = stats.get('total_characters', 0)
        elif self.current_category == 'potions':
            if hasattr(self.bot.db, 'get_player_shop_items'):
                shop_items = await self.bot.db.get_player_shop_items(self.user_id)
                total_items = len(shop_items)
            else:
                items = await self.bot.db.get_player_items(self.user_id)
                total_items = len(items)
        elif self.current_category == 'titles':
            all_titles = await self.bot.db.get_player_titles(self.user_id)
            total_items = len(all_titles)
        elif self.current_category == 'equipment':
            available_chars = await self.bot.db.get_equippable_characters(self.user_id)
            total_items = len(available_chars)
        elif self.current_category == 'effects':
            effects = await self.bot.db.get_active_effects(self.user_id)
            total_items = len(effects)
        else:
            total_items = 0
            
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_backpack_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Déjà à la dernière page!", ephemeral=True)

    # Action buttons (Row 3) - Limited to 3 buttons for visibility
    @discord.ui.button(label='🧪 Utiliser Potion', style=discord.ButtonStyle.success, row=3)
    async def use_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_category != 'potions':
            await interaction.response.send_message("Naviguez vers les potions pour utiliser cet bouton!", ephemeral=True)
            return
        
        await interaction.response.send_modal(UsePotionModal(self.bot, self.user_id, self))

    @discord.ui.button(label='🎯 Sélectionner Titre', style=discord.ButtonStyle.primary, row=3)
    async def select_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_category != 'titles':
            await interaction.response.send_message("Naviguez vers les titres pour utiliser cet bouton!", ephemeral=True)
            return
        
        await interaction.response.send_modal(SelectTitleModal(self.bot, self.user_id, self))

    @discord.ui.button(label='⚔️ Équiper/Déséquiper', style=discord.ButtonStyle.danger, row=3)
    async def manage_equipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_category != 'equipment':
            await interaction.response.send_message("Naviguez vers l'équipement pour utiliser cet bouton!", ephemeral=True)
            return
        
        # Check if user has any equippable characters first
        available_chars = await self.bot.db.get_equippable_characters(self.user_id)
        equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
        
        if len(available_chars) == 0 and len(equipped_chars) == 0:
            # User has no equipment-eligible characters
            embed = discord.Embed(
                title="⚔️ Gestion d'Équipement",
                description="Vous n'avez aucun personnage éligible à l'équipement.\n\nSeuls les personnages **Titan**, **Fusion** et **Secret** peuvent être équipés.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create the equipment management view with populated dropdowns
        view = ManageEquipmentView(self.bot, self.user_id, self)
        
        # Populate the dropdowns with actual data
        await self.populate_equipment_dropdowns(view)
        
        embed = discord.Embed(
            title="⚔️ Gestion d'Équipement",
            description="Sélectionnez un personnage dans les listes déroulantes ci-dessous:",
            color=0xe74c3c
        )
        
        # Show current status
        equipped_count = len(equipped_chars)
        available_count = len(available_chars)
        
        embed.add_field(
            name="📊 Statut Actuel",
            value=f"Équipés: {equipped_count}/3\nDisponibles: {available_count}",
            inline=False
        )
        
        if available_count > 0:
            embed.add_field(
                name="🔧 Équiper un Personnage",
                value="Choisissez un personnage non équipé à équiper (max 3)",
                inline=False
            )
        
        if equipped_count > 0:
            embed.add_field(
                name="🔧 Déséquiper un Personnage", 
                value="Choisissez un personnage équipé à déséquiper",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def populate_equipment_dropdowns(self, view: 'ManageEquipmentView'):
        """Populate the dropdown options with actual character data"""
        try:
            # Get characters available for equipping (not already equipped)
            available_chars = await self.bot.db.get_equippable_characters(self.user_id)
            
            # Get currently equipped characters
            equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
            
            # Populate equip dropdown with unique values
            equip_options = []
            seen_values = set()
            
            for char in available_chars[:20]:  # Limit to 20 for Discord dropdown limit
                # Use proper field names from database
                char_name = char.get('name') or char.get('character_name', 'Personnage Inconnu')
                char_rarity = char.get('rarity', 'Common')
                char_value = char.get('value', 0)
                char_id = char.get('inventory_id') or char.get('id', 0)
                
                # Skip invalid IDs and duplicates
                if char_id == 0 or str(char_id) in seen_values:
                    continue
                seen_values.add(str(char_id))
                
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(char_rarity, '◆')
                
                # Create safe label and description
                label = f"{char_name} ({char_rarity})"[:100]
                description = f"{rarity_emoji} Valeur: {format_number(char_value)} SC"[:100]
                
                equip_options.append(
                    discord.SelectOption(
                        label=label,
                        description=description,
                        value=str(char_id)
                    )
                )
            
            # Always add at least one option
            if not equip_options:
                equip_options.append(
                    discord.SelectOption(
                        label="Aucun personnage disponible",
                        description="Tous vos personnages sont équipés ou vous n'avez pas de personnages rares",
                        value="none_available"
                    )
                )
            
            # Update equip dropdown
            for item in view.children:
                if isinstance(item, EquipCharacterSelect):
                    item.options = equip_options
                    # Disable if no real options
                    if len(equip_options) == 1 and equip_options[0].value == "none_available":
                        item.disabled = True
            
            # Populate unequip dropdown with unique values
            unequip_options = []
            seen_unequip_values = set()
            
            for char in equipped_chars:
                # Use proper field names from database
                char_name = char.get('name') or char.get('character_name', 'Personnage Inconnu')
                char_rarity = char.get('rarity', 'Common')
                char_value = char.get('value', 0)
                # Use inventory_id for unequip, not character_id
                char_id = char.get('inventory_id') or char.get('id', 0)
                slot_number = char.get('slot_number', '?')
                
                # Skip invalid IDs and duplicates
                if char_id == 0 or str(char_id) in seen_unequip_values:
                    continue
                seen_unequip_values.add(str(char_id))
                
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(char_rarity, '◆')
                
                # Create safe label and description
                label = f"{char_name} ({char_rarity})"[:100]
                description = f"{rarity_emoji} Slot {slot_number} • Valeur: {format_number(char_value)} SC"[:100]
                
                unequip_options.append(
                    discord.SelectOption(
                        label=label,
                        description=description,
                        value=str(char_id)
                    )
                )
            
            # Always add at least one option
            if not unequip_options:
                unequip_options.append(
                    discord.SelectOption(
                        label="Aucun équipement actuel",
                        description="Vous n'avez aucun personnage équipé",
                        value="none_equipped"
                    )
                )
            
            # Update unequip dropdown  
            for item in view.children:
                if isinstance(item, UnequipCharacterSelect):
                    item.options = unequip_options
                    # Disable if no real options
                    if len(unequip_options) == 1 and unequip_options[0].value == "none_equipped":
                        item.disabled = True
                        
        except Exception as e:
            logger.error(f"Error populating equipment dropdowns: {e}")
            # In case of error, create safe fallback options
            fallback_equip = [discord.SelectOption(label="Erreur de chargement", description="Réessayez plus tard", value="error")]
            fallback_unequip = [discord.SelectOption(label="Erreur de chargement", description="Réessayez plus tard", value="error")]
            
            for item in view.children:
                if isinstance(item, EquipCharacterSelect):
                    item.options = fallback_equip
                    item.disabled = True
                elif isinstance(item, UnequipCharacterSelect):
                    item.options = fallback_unequip
                    item.disabled = True

    # Utility buttons (Row 4) - Keep essential buttons separate
    @discord.ui.button(label='🔄 Actualiser', style=discord.ButtonStyle.secondary, row=4)
    async def refresh_backpack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = await self.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=4)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class UsePotionModal(discord.ui.Modal):
    """Modal for using potions"""
    def __init__(self, bot, user_id: int, backpack_view: BackpackView):
        super().__init__(title="🧪 Utiliser Potion")
        self.bot = bot
        self.user_id = user_id
        self.backpack_view = backpack_view

    potion_id = discord.ui.TextInput(
        label="ID de la Potion",
        placeholder="Entrez l'ID de la potion à utiliser...",
        max_length=10,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            potion_id = int(self.potion_id.value)
            
            # Get player's potions
            if hasattr(self.bot.db, 'get_player_shop_items'):
                shop_items = await self.bot.db.get_player_shop_items(self.user_id)
                potions = await self.backpack_view.convert_shop_items_to_potions(shop_items)
            else:
                potions = await self.bot.db.get_player_items(self.user_id)
            
            if potion_id < 1 or potion_id > len(potions):
                await interaction.response.send_message("❌ ID de potion invalide!", ephemeral=True)
                return
            
            selected_potion = potions[potion_id - 1]
            
            # Use the potion (implement potion usage logic here)
            success = await self.use_potion_logic(selected_potion)
            
            if success:
                await interaction.response.send_message(
                    f"✅ Potion **{selected_potion['name']}** utilisée avec succès!",
                    ephemeral=True
                )
                # Refresh backpack
                embed = await self.backpack_view.create_backpack_embed()
                await interaction.edit_original_response(embed=embed, view=self.backpack_view)
            else:
                await interaction.response.send_message("❌ Erreur lors de l'utilisation de la potion!", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un numéro valide!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error using potion: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'utilisation de la potion!", ephemeral=True)

    async def use_potion_logic(self, potion: Dict) -> bool:
        """Implement potion usage logic"""
        try:
            # This would integrate with the shop system's potion usage
            # For now, return True as placeholder
            return True
        except Exception as e:
            logger.error(f"Error in potion usage logic: {e}")
            return False


class SelectTitleModal(discord.ui.Modal):
    """Modal for selecting titles"""
    def __init__(self, bot, user_id: int, backpack_view: BackpackView):
        super().__init__(title="🏆 Sélectionner Titre")
        self.bot = bot
        self.user_id = user_id
        self.backpack_view = backpack_view

    title_name = discord.ui.TextInput(
        label="Nom du Titre",
        placeholder="Entrez le nom du titre à équiper...",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            title_name = self.title_name.value.strip()
            
            # Get player's titles
            all_titles = await self.bot.db.get_player_titles(self.user_id)
            unlocked_titles = [title for title in all_titles if title['is_unlocked']]
            
            # Find matching title
            matching_title = None
            for title in unlocked_titles:
                if title_name.lower() in title['display_name'].lower():
                    matching_title = title
                    break
            
            if not matching_title:
                await interaction.response.send_message("❌ Titre non trouvé ou non débloqué!", ephemeral=True)
                return
            
            # Select the title
            success = await self.bot.db.set_selected_title(self.user_id, matching_title['id'])
            
            if success:
                await interaction.response.send_message(
                    f"✅ Titre **{matching_title['display_name']}** équipé avec succès!",
                    ephemeral=True
                )
                # Refresh backpack
                embed = await self.backpack_view.create_backpack_embed()
                await interaction.edit_original_response(embed=embed, view=self.backpack_view)
            else:
                await interaction.response.send_message("❌ Erreur lors de l'équipement du titre!", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error selecting title: {e}")
            await interaction.response.send_message("❌ Erreur lors de la sélection du titre!", ephemeral=True)


class ManageEquipmentView(discord.ui.View):
    """View for managing equipment with dropdown selection"""
    def __init__(self, bot, user_id: int, backpack_view: BackpackView):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.backpack_view = backpack_view
        self.add_equipment_dropdown()
    
    def add_equipment_dropdown(self):
        # Add both dropdowns conditionally
        self.add_item(EquipCharacterSelect(self.bot, self.user_id, self.backpack_view))
        self.add_item(UnequipCharacterSelect(self.bot, self.user_id, self.backpack_view))

class EquipCharacterSelect(discord.ui.Select):
    """Dropdown for selecting characters to equip"""
    def __init__(self, bot, user_id: int, backpack_view: BackpackView):
        self.bot = bot
        self.user_id = user_id
        self.backpack_view = backpack_view
        
        # Temporary options - will be populated in view creation
        options = [
            discord.SelectOption(
                label="Chargement...",
                description="Récupération de vos personnages",
                value="loading"
            )
        ]
        
        super().__init__(
            placeholder="🔧 Sélectionnez un personnage à équiper",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if self.values[0] in ["loading", "none", "none_available", "error"]:
                await interaction.response.send_message("❌ Aucun personnage disponible pour l'équipement!", ephemeral=True)
                return
                
            inventory_id = int(self.values[0])
            
            # Check if user has room for more equipment
            equipped_count = await self.bot.db.get_equipped_count(self.user_id)
            if equipped_count >= 3:
                await interaction.response.send_message("❌ Vous avez déjà 3 personnages équipés (limite maximale)!", ephemeral=True)
                return
            
            # Equip the character
            success = await self.bot.db.equip_character(self.user_id, inventory_id)
            
            if success:
                # Get character name for feedback
                char_info = await self.bot.db.get_character_from_inventory(inventory_id)
                char_name = char_info.get('name', 'Personnage') if char_info else 'Personnage'
                
                await interaction.response.send_message(
                    f"✅ **{char_name}** équipé avec succès!",
                    ephemeral=True
                )
                
                # Refresh the equipment view
                await self.refresh_view(interaction)
            else:
                await interaction.response.send_message("❌ Erreur lors de l'équipement!", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error equipping character: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'équipement!", ephemeral=True)
    
    async def refresh_view(self, interaction: discord.Interaction):
        """Refresh the equipment view"""
        embed = await self.backpack_view.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self.backpack_view)

class UnequipCharacterSelect(discord.ui.Select):
    """Dropdown for selecting characters to unequip"""
    def __init__(self, bot, user_id: int, backpack_view: BackpackView):
        self.bot = bot
        self.user_id = user_id
        self.backpack_view = backpack_view
        
        # Temporary options - will be populated in view creation
        options = [
            discord.SelectOption(
                label="Chargement...",
                description="Récupération de vos équipements",
                value="loading"
            )
        ]
        
        super().__init__(
            placeholder="🔧 Sélectionnez un personnage à déséquiper",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            if self.values[0] in ["loading", "none", "none_equipped", "error"]:
                await interaction.response.send_message("❌ Aucun personnage équipé à déséquiper!", ephemeral=True)
                return
                
            inventory_id = int(self.values[0])
            
            # Unequip the character using inventory_id
            success = await self.bot.db.unequip_character(self.user_id, inventory_id)
            
            if success:
                # Get character name for feedback
                char_info = await self.bot.db.get_character_from_inventory(inventory_id)
                char_name = char_info.get('name', 'Personnage') if char_info else 'Personnage'
                
                await interaction.response.send_message(
                    f"✅ **{char_name}** déséquipé avec succès!",
                    ephemeral=True
                )
                
                # Refresh the equipment view
                await self.refresh_view(interaction)
            else:
                await interaction.response.send_message("❌ Erreur lors du déséquipement!", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error unequipping character: {e}")
            await interaction.response.send_message("❌ Erreur lors du déséquipement!", ephemeral=True)
    
    async def refresh_view(self, interaction: discord.Interaction):
        """Refresh the equipment view"""
        embed = await self.backpack_view.create_backpack_embed()
        await interaction.edit_original_response(embed=embed, view=self.backpack_view)