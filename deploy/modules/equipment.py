"""
Equipment System for Shadow Roll Bot
Ultra-rare characters (Titan/Fusion/Secret) can be equipped for global passive bonuses
"""
import discord
from discord.ext import commands
import logging
from typing import List, Dict, Optional
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.equipment_fix import fix_equipment_before_operation

logger = logging.getLogger(__name__)


class EquipmentView(discord.ui.View):
    """Equipment management view"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 1
        self.items_per_page = 5

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command user can interact"""
        return interaction.user.id == self.user_id

    async def create_equipment_embed(self) -> discord.Embed:
        """Create equipment management embed"""
        try:
            # Nettoyer l'équipement avant l'affichage
            await fix_equipment_before_operation(self.bot.db, self.user_id)
            
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"

            # Get equipped characters
            equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
            
            # Calculate total bonuses
            total_bonuses = await self.bot.db.calculate_equipment_bonuses(self.user_id)

            embed = discord.Embed(
                title="⚔️ ═══════〔 É Q U I P E M E N T   D E S   O M B R E S 〕═══════ ⚔️",
                description=f"```\n🪙 Maître des Ténèbres : {username} 🪙\n\nSeuls les personnages Titan, Fusion et Secret\npeuvent être équipés (3 maximum)\n```",
                color=BotConfig.RARITY_COLORS['Titan']
            )

            # Show equipped characters
            if equipped_chars:
                equipped_text = ""
                for i, char in enumerate(equipped_chars, 1):
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    bonus_text = self._format_character_bonus(char)
                    equipped_text += f"{i}. {rarity_emoji} **{char['name']}** ({char['anime']})\n   {bonus_text}\n"
                
                embed.add_field(
                    name="⚡ ═══〔 Personnages Équipés 〕═══ ⚡",
                    value=equipped_text or "```\nAucun personnage équipé\n```",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚡ ═══〔 Personnages Équipés 〕═══ ⚡",
                    value="```\nAucun personnage équipé\n```",
                    inline=False
                )

            # Show total active bonuses
            bonus_text = ""
            if total_bonuses.get('rarity_boost', 0) > 0:
                bonus_text += f"🎲 +{total_bonuses['rarity_boost']:.1f}% chances toutes raretés\n"
            else:
                bonus_text += f"🎲 +0% chances toutes raretés\n"
            
            if total_bonuses.get('coin_boost', 0) > 0:
                bonus_text += f"🪙 +{total_bonuses['coin_boost']:.1f}% Shadow Coins partout\n"
            else:
                bonus_text += f"🪙 +0% Shadow Coins partout\n"

            embed.add_field(
                name="🔥 ═══〔 Bonus Actifs Globaux 〕═══ 🔥",
                value=bonus_text,
                inline=False
            )

            embed.add_field(
                name="🎯 ═══〔 Instructions 〕═══ 🎯",
                value="```\n• Équiper : Sélectionnez un personnage ultra-rare\n• Déséquiper : Retirez un personnage équipé\n• Maximum 3 personnages équipés simultanément\n• Bonus appliqués automatiquement partout\n```",
                inline=False
            )

            embed.set_footer(
                text=f"Shadow Roll • Équipement {len(equipped_chars)}/3",
                icon_url=user.avatar.url if user and user.avatar else None
            )

            return embed

        except Exception as e:
            logger.error(f"Error creating equipment embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger l'équipement",
                color=0xff0000
            )

    def _format_character_bonus(self, char: Dict) -> str:
        """Format character bonus text"""
        rarity = char['rarity']
        if rarity == 'Titan':
            return "🎲 +2% chances toutes raretés"
        elif rarity == 'Fusion':
            return "🪙 +5% Shadow Coins partout"
        elif rarity == 'Secret':
            return "🔥 +3% chances + 3% coins"
        elif rarity == 'Evolve':
            return "🔮 +1% chances + 2% coins"
        return "Bonus inconnu"

    @discord.ui.button(label='⚔️ Équiper', style=discord.ButtonStyle.success, row=0)
    async def equip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user has room for more equipment
        equipped_count = await self.bot.db.get_equipped_count(self.user_id)
        if equipped_count >= 3:
            error_embed = discord.Embed(
                title="❌ Équipement Complet",
                description="```\nVous avez déjà 3 personnages équipés.\nDéséquipez d'abord un personnage.\n```",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=error_embed, view=self)
            return

        # Show equippable characters
        view = EquipSelectionView(self.bot, self.user_id, self)
        embed = await view.create_selection_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🗡️ Déséquiper', style=discord.ButtonStyle.danger, row=0)
    async def unequip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user has equipped characters
        equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)
        if not equipped_chars:
            error_embed = discord.Embed(
                title="❌ Aucun Équipement",
                description="```\nVous n'avez aucun personnage équipé.\n```",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=error_embed, view=self)
            return

        # Show equipped characters for unequipping
        view = UnequipSelectionView(self.bot, self.user_id, self)
        embed = await view.create_unequip_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class EquipSelectionView(discord.ui.View):
    """Character selection for equipping"""

    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view
        self.current_page = 1
        self.items_per_page = 5

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_selection_embed(self) -> discord.Embed:
        """Create character selection embed"""
        try:
            # Get equippable characters (Titan/Fusion/Secret not already equipped)
            equippable_chars = await self.bot.db.get_equippable_characters(self.user_id)
            
            total_pages = (len(equippable_chars) + self.items_per_page - 1) // self.items_per_page if equippable_chars else 1
            
            if self.current_page > total_pages:
                self.current_page = total_pages
            if self.current_page < 1:
                self.current_page = 1

            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(equippable_chars))

            embed = discord.Embed(
                title="⚔️ ═══════〔 S É L E C T I O N   É Q U I P E M E N T 〕═══════ ⚔️",
                description=f"```\nPage {self.current_page}/{total_pages} • Personnages équipables\n\nSeuls Evolve, Titan, Fusion et Secret peuvent être équipés\n```",
                color=BotConfig.RARITY_COLORS['Legendary']
            )

            if equippable_chars:
                chars_text = ""
                for i in range(start_idx, end_idx):
                    char = equippable_chars[i]
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    bonus = self.parent_view._format_character_bonus(char)
                    chars_text += f"{i+1}. {rarity_emoji} **{char['name']}** ({char['anime']})\n   {bonus}\n"

                embed.add_field(
                    name="🪙 ═══〔 Personnages Disponibles 〕═══ 🪙",
                    value=chars_text,
                    inline=False
                )

                # Add selection buttons
                self.clear_items()
                for i in range(start_idx, min(end_idx, start_idx + 5)):
                    char = equippable_chars[i]
                    button = discord.ui.Button(
                        label=f"{i+1}. {char['name'][:15]}",
                        style=discord.ButtonStyle.secondary,
                        custom_id=f"equip_{char['inventory_id']}"
                    )
                    button.callback = self.create_equip_callback(char)
                    self.add_item(button)

                # Navigation buttons
                if total_pages > 1:
                    if self.current_page > 1:
                        prev_btn = discord.ui.Button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=2)
                        prev_btn.callback = self.previous_page
                        self.add_item(prev_btn)
                    
                    if self.current_page < total_pages:
                        next_btn = discord.ui.Button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=2)
                        next_btn.callback = self.next_page
                        self.add_item(next_btn)

            else:
                embed.add_field(
                    name="❌ ═══〔 Aucun Personnage Équipable 〕═══ ❌",
                    value="```\nVous n'avez aucun personnage Titan, Fusion ou Secret\ndisponible pour l'équipement.\n```",
                    inline=False
                )

            # Back button
            back_btn = discord.ui.Button(label='🔙 Retour', style=discord.ButtonStyle.primary, row=3)
            back_btn.callback = self.back_to_equipment
            self.add_item(back_btn)

            return embed

        except Exception as e:
            logger.error(f"Error creating selection embed: {e}")
            return discord.Embed(title="❌ Erreur", description="Impossible de charger la sélection", color=0xff0000)

    def create_equip_callback(self, char):
        async def callback(interaction: discord.Interaction):
            try:
                await interaction.response.defer()
                
                # Equip the character
                success = await self.bot.db.equip_character(self.user_id, char['inventory_id'])
                
                if success:
                    success_embed = discord.Embed(
                        title="✅ Personnage Équipé",
                        description=f"```\n{char['name']} a été équipé avec succès!\n\nBonus actif: {self.parent_view._format_character_bonus(char)}\n```",
                        color=BotConfig.RARITY_COLORS.get(char['rarity'], 0x00ff00)
                    )
                    await interaction.edit_original_response(embed=success_embed, view=None)
                    await asyncio.sleep(2)
                else:
                    error_embed = discord.Embed(
                        title="❌ Erreur d'Équipement",
                        description="```\nImpossible d'équiper ce personnage.\n```",
                        color=0xff0000
                    )
                    await interaction.edit_original_response(embed=error_embed, view=None)
                    await asyncio.sleep(2)
                
                # Return to equipment view
                embed = await self.parent_view.create_equipment_embed()
                await interaction.edit_original_response(embed=embed, view=self.parent_view)

            except Exception as e:
                logger.error(f"Error equipping character: {e}")
                
        return callback

    async def previous_page(self, interaction: discord.Interaction):
        self.current_page -= 1
        embed = await self.create_selection_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction):
        self.current_page += 1
        embed = await self.create_selection_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    async def back_to_equipment(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.parent_view.create_equipment_embed()
        await interaction.edit_original_response(embed=embed, view=self.parent_view)


class UnequipSelectionView(discord.ui.View):
    """Character selection for unequipping"""

    def __init__(self, bot, user_id: int, parent_view):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.parent_view = parent_view

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_unequip_embed(self) -> discord.Embed:
        """Create unequip selection embed"""
        try:
            equipped_chars = await self.bot.db.get_equipped_characters(self.user_id)

            embed = discord.Embed(
                title="🗡️ ═══════〔 D É S É Q U I P E R   P E R S O N N A G E 〕═══════ 🗡️",
                description="```\nSélectionnez le personnage à déséquiper\n```",
                color=BotConfig.RARITY_COLORS['Epic']
            )

            if equipped_chars:
                chars_text = ""
                for i, char in enumerate(equipped_chars, 1):
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    bonus = self.parent_view._format_character_bonus(char)
                    chars_text += f"{i}. {rarity_emoji} **{char['name']}** ({char['anime']})\n   {bonus}\n"

                embed.add_field(
                    name="⚡ ═══〔 Personnages Équipés 〕═══ ⚡",
                    value=chars_text,
                    inline=False
                )

                # Add unequip buttons
                self.clear_items()
                for i, char in enumerate(equipped_chars):
                    button = discord.ui.Button(
                        label=f"{i+1}. {char['name'][:15]}",
                        style=discord.ButtonStyle.danger,
                        custom_id=f"unequip_{char['inventory_id']}"
                    )
                    button.callback = self.create_unequip_callback(char)
                    self.add_item(button)

            # Back button
            back_btn = discord.ui.Button(label='🔙 Retour', style=discord.ButtonStyle.primary, row=2)
            back_btn.callback = self.back_to_equipment
            self.add_item(back_btn)

            return embed

        except Exception as e:
            logger.error(f"Error creating unequip embed: {e}")
            return discord.Embed(title="❌ Erreur", description="Impossible de charger la sélection", color=0xff0000)

    def create_unequip_callback(self, char):
        async def callback(interaction: discord.Interaction):
            try:
                await interaction.response.defer()
                
                # Unequip the character
                success = await self.bot.db.unequip_character(self.user_id, char['inventory_id'])
                
                if success:
                    success_embed = discord.Embed(
                        title="✅ Personnage Déséquipé",
                        description=f"```\n{char['name']} a été déséquipé avec succès!\n\nBonus retiré: {self.parent_view._format_character_bonus(char)}\n```",
                        color=BotConfig.RARITY_COLORS.get(char['rarity'], 0x00ff00)
                    )
                    await interaction.edit_original_response(embed=success_embed, view=None)
                    await asyncio.sleep(2)
                else:
                    error_embed = discord.Embed(
                        title="❌ Erreur de Déséquipement",
                        description="```\nImpossible de déséquiper ce personnage.\n```",
                        color=0xff0000
                    )
                    await interaction.edit_original_response(embed=error_embed, view=None)
                    await asyncio.sleep(2)
                
                # Return to equipment view
                embed = await self.parent_view.create_equipment_embed()
                await interaction.edit_original_response(embed=embed, view=self.parent_view)

            except Exception as e:
                logger.error(f"Error unequipping character: {e}")
                
        return callback

    async def back_to_equipment(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.parent_view.create_equipment_embed()
        await interaction.edit_original_response(embed=embed, view=self.parent_view)