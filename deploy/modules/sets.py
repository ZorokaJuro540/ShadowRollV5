"""
Character Sets System for Shadow Roll Bot
Manages collection sets with bonus rewards for completing entire series
"""
import discord
import logging
from typing import Dict, List, Optional
from modules.utils import format_number, get_display_name
from core.config import BotConfig

logger = logging.getLogger(__name__)


class AllSeriesDetailsView(discord.ui.View):
    """Vue détaillée de toutes les séries avec leurs bonus"""
    
    def __init__(self, bot, user_id: int, sets_data: List[Dict]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.sets_data = sets_data
        self.current_page = 1
        self.series_per_page = 6
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_all_series_embed(self) -> discord.Embed:
        """Créer l'embed avec toutes les séries et leurs bonus"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"
            
            # Pagination
            start_idx = (self.current_page - 1) * self.series_per_page
            end_idx = start_idx + self.series_per_page
            page_series = self.sets_data[start_idx:end_idx]
            total_pages = max(1, (len(self.sets_data) + self.series_per_page - 1) // self.series_per_page)
            
            embed = discord.Embed(
                title="📋 ═══════〔 T O U T E S   L E S   S É R I E S 〕═══════ 📋",
                description=f"```\n◆ Guide complet des séries ◆\n◆ Page {self.current_page}/{total_pages} ◆\n```",
                color=BotConfig.RARITY_COLORS['Fusion']
            )
            
            # Afficher chaque série avec ses informations complètes
            for series in page_series:
                status_icon = "✅" if series['is_completed'] else "⏳"
                
                # Informations de base
                series_info = (
                    f"{status_icon} **{series['anime_series']}**\n"
                    f"📊 **{series['owned_characters']}/{series['total_characters']}** personnages\n"
                    f"🎁 **Bonus:** {series['bonus_description']}\n"
                )
                
                # Ajouter le statut de récompense si complète
                if series['is_completed']:
                    series_info += "🏆 **SÉRIE COMPLÉTÉE!**\n"
                else:
                    progress_pct = series['completion_percentage']
                    series_info += f"📈 **Progression:** {progress_pct:.1f}%\n"
                
                embed.add_field(
                    name=f"{series['icon']} {series['set_name']}",
                    value=series_info,
                    inline=True
                )
            
            # Ajouter un résumé des bonus actifs
            active_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
            if active_bonuses:
                bonus_summary = ""
                for bonus_type, bonus_value in active_bonuses.items():
                    if bonus_type == "rarity_boost":
                        bonus_summary += f"🍀 Rareté: +{bonus_value*100:.1f}%\n"
                    elif bonus_type == "coin_boost":
                        bonus_summary += f"🪙 Coins: +{(bonus_value-1)*100:.1f}%\n"
                
                if bonus_summary:
                    embed.add_field(
                        name="✨ ═══〔 Vos Bonus Actifs 〕═══ ✨",
                        value=f"```\n{bonus_summary}```",
                        inline=False
                    )
            
            embed.set_footer(text=f"Shadow Roll • {len(self.sets_data)} séries totales • Explorez toutes les collections")
            return embed
            
        except Exception as e:
            logger.error(f"Error creating all series embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger les détails des séries",
                color=0xff0000
            )
    
    @discord.ui.button(label='⬅️', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_all_series_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Première page!", ephemeral=True)
    
    @discord.ui.button(label='➡️', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = max(1, (len(self.sets_data) + self.series_per_page - 1) // self.series_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_all_series_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Dernière page!", ephemeral=True)
    
    @discord.ui.button(label='🔍 Série Spécifique', style=discord.ButtonStyle.primary, row=0)
    async def view_specific_series(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les détails d'une série spécifique avec personnages"""
        await interaction.response.send_modal(SeriesSearchModal(self.bot, self.user_id, self.sets_data, self))
    
    @discord.ui.button(label='🔙 Retour aux Séries', style=discord.ButtonStyle.success, row=1)
    async def back_to_sets(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        view = SetsView(self.bot, self.user_id)
        embed = await view.create_sets_embed()
        await interaction.edit_original_response(embed=embed, view=view)


class SeriesSearchModal(discord.ui.Modal, title='🔍 Choisir une Série'):
    """Modal pour sélectionner une série spécifique"""
    
    def __init__(self, bot, user_id: int, sets_data: List[Dict], parent_view):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.sets_data = sets_data
        self.parent_view = parent_view
    
    series_input = discord.ui.TextInput(
        label='Nom de la série anime',
        placeholder='Ex: Naruto, One Piece, Dragon Ball Z...',
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        search_term = self.series_input.value.strip().lower()
        
        # Trouver la série correspondante
        matching_series = None
        for series in self.sets_data:
            if search_term in series['anime_series'].lower() or search_term in series['set_name'].lower():
                matching_series = series
                break
        
        if not matching_series:
            await interaction.response.send_message(
                f"❌ Aucune série trouvée pour '{self.series_input.value}'\n"
                f"Séries disponibles: {', '.join([s['anime_series'] for s in self.sets_data[:5]])}...",
                ephemeral=True
            )
            return
        
        # Créer l'embed détaillé pour cette série
        embed = discord.Embed(
            title=f"{matching_series['icon']} ═══════〔 {matching_series['set_name']} 〕═══════ {matching_series['icon']}",
            description=f"**{matching_series['anime_series']}**\n{matching_series.get('description', 'Collection de personnages emblématiques')}",
            color=BotConfig.RARITY_COLORS['Epic']
        )
        
        # Personnages possédés
        owned_names = [char['name'] for char in matching_series.get('owned_characters_list', [])]
        if owned_names:
            # Limiter l'affichage pour éviter les erreurs Discord
            display_owned = owned_names[:15]  # Max 15 personnages
            owned_text = "\n".join(display_owned)
            if len(owned_names) > 15:
                owned_text += f"\n... et {len(owned_names) - 15} autres"
            
            embed.add_field(
                name=f"✅ Personnages Possédés ({len(owned_names)})",
                value=f"```\n{owned_text}\n```",
                inline=True
            )
        
        # Personnages manquants
        all_names = [char['name'] for char in matching_series.get('all_characters', [])]
        missing_names = [name for name in all_names if name not in owned_names]
        if missing_names:
            # Limiter l'affichage
            display_missing = missing_names[:15]  # Max 15 personnages
            missing_text = "\n".join(display_missing)
            if len(missing_names) > 15:
                missing_text += f"\n... et {len(missing_names) - 15} autres"
            
            embed.add_field(
                name=f"❌ Personnages Manquants ({len(missing_names)})",
                value=f"```\n{missing_text}\n```",
                inline=True
            )
        
        # Bonus et statut
        embed.add_field(
            name="🎁 Bonus de Série",
            value=f"```\n{matching_series['bonus_description']}\n```",
            inline=False
        )
        
        # Progression
        if matching_series['is_completed']:
            embed.add_field(
                name="🏆 Statut",
                value="```\n✅ SÉRIE COMPLÉTÉE!\n🎁 Bonus actif\n```",
                inline=True
            )
        else:
            progress_bar = "█" * int(matching_series['completion_percentage'] / 10) + "░" * (10 - int(matching_series['completion_percentage'] / 10))
            embed.add_field(
                name="📊 Progression",
                value=f"```\n[{progress_bar}] {matching_series['completion_percentage']:.1f}%\n```",
                inline=True
            )
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class SetsView(discord.ui.View):
    """Character sets view with completion tracking and bonus management"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.sets_per_page = 3

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_sets_embed(self) -> discord.Embed:
        """Create character sets embed with completion status"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"

            # Get sets data with progress
            sets_data = await self.bot.db.get_character_sets_with_progress(self.user_id)
            
            # Pagination
            start_idx = (self.current_page - 1) * self.sets_per_page
            end_idx = start_idx + self.sets_per_page
            page_sets = sets_data[start_idx:end_idx]
            total_pages = max(1, (len(sets_data) + self.sets_per_page - 1) // self.sets_per_page)

            # Count completed sets
            completed_sets = sum(1 for s in sets_data if s['is_completed'])
            
            embed = discord.Embed(
                title="🎖️ ═══════〔 C O L L E C T I O N   D E   S É R I E S 〕═══════ 🎖️",
                description=f"```\n◆ {username} ◆\n{completed_sets}/{len(sets_data)} séries complètes\n```",
                color=BotConfig.RARITY_COLORS['Legendary'])

            if not page_sets:
                embed.add_field(
                    name="📋 Aucune série",
                    value="Les séries de personnages seront bientôt disponibles!",
                    inline=False)
                return embed

            # Display each set
            for set_info in page_sets:
                # Status indicator
                if set_info['is_completed']:
                    status_icon = "✅"
                    status_text = "COMPLÈTE"
                    name_format = f"**{set_info['set_name']}**"
                    color_indicator = "🟢"
                else:
                    status_icon = "⏳"
                    status_text = "EN COURS"
                    name_format = set_info['set_name']
                    color_indicator = "🟡" if set_info['completion_percentage'] > 50 else "🔴"

                # Progress bar
                progress = int(set_info['completion_percentage'] / 10)
                progress_bar = "█" * progress + "░" * (10 - progress)
                
                # Character details
                missing_count = set_info['total_characters'] - set_info['owned_characters']
                
                set_content = (
                    f"{status_icon} {name_format}\n"
                    f"🎭 **{set_info['anime_series']}**\n"
                    f"📊 Progress: [{progress_bar}] {set_info['completion_percentage']:.1f}%\n"
                    f"🎒 Possédés: {set_info['owned_characters']}/{set_info['total_characters']}\n"
                )
                
                if set_info['is_completed']:
                    set_content += f"🎁 **{set_info['bonus_description']}**\n"
                else:
                    set_content += f"❌ Manque: {missing_count} personnages\n"
                    set_content += f"🎁 Bonus: {set_info['bonus_description']}\n"

                embed.add_field(
                    name=f"{set_info['icon']} ═══〔 {status_text} 〕═══ {set_info['icon']}",
                    value=set_content,
                    inline=False)

            # Active bonuses summary
            active_bonuses = await self.bot.db.get_active_set_bonuses(self.user_id)
            if active_bonuses:
                bonus_text = ""
                for bonus_type, bonus_value in active_bonuses.items():
                    if bonus_type == "rarity_boost":
                        bonus_text += f"🍀 Bonus Rareté: +{bonus_value*100:.1f}%\n"
                    elif bonus_type == "coin_boost":
                        bonus_text += f"🪙 Bonus Coins: +{(bonus_value-1)*100:.1f}%\n"
                
                if bonus_text:
                    embed.add_field(
                        name="✨ ═══〔 Bonus Actifs 〕═══ ✨",
                        value=f"```\n{bonus_text}```",
                        inline=False)

            # Footer
            embed.set_footer(text=f"Shadow Roll • Page {self.current_page}/{total_pages} • Séries de Personnages")
            return embed

        except Exception as e:
            logger.error(f"Error creating sets embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger les séries de personnages",
                color=0xff0000)

    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_sets_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        sets_data = await self.bot.db.get_character_sets_with_progress(self.user_id)
        total_pages = max(1, (len(sets_data) + self.sets_per_page - 1) // self.sets_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_sets_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🔄 Vérifier Progression', style=discord.ButtonStyle.primary, row=0)
    async def check_progress(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check for newly completed sets with persistent rewards
        newly_completed = await self.bot.db.check_and_complete_sets(self.user_id)
        
        if newly_completed:
            # Process each completed set with persistent reward claiming
            completion_text = ""
            total_coins_awarded = 0
            
            for set_info in newly_completed:
                anime_series = set_info['anime_series']
                
                # Check if reward already claimed (persistent check)
                already_claimed = await self.bot.db.is_series_reward_claimed(self.user_id, anime_series)
                
                if not already_claimed:
                    # Calculate reward amount based on bonus type
                    reward_amount = 1000  # Base reward for series completion
                    if set_info.get('bonus_type') == 'coins':
                        reward_amount = int(1000 * (1 + set_info.get('bonus_value', 0) / 100))
                    
                    # Claim reward with persistence
                    success = await self.bot.db.claim_series_completion_reward(
                        self.user_id, anime_series, "coins", reward_amount
                    )
                    
                    if success:
                        completion_text += f"🎉 **{set_info['set_name']}** complète!\n"
                        completion_text += f"🎁 {set_info['bonus_description']}\n"
                        completion_text += f"🪙 +{reward_amount:,} Shadow Coins!\n\n"
                        total_coins_awarded += reward_amount
                    else:
                        completion_text += f"🎉 **{set_info['set_name']}** complète!\n"
                        completion_text += f"⚠️ Récompense déjà réclamée\n\n"
                else:
                    completion_text += f"🎉 **{set_info['set_name']}** complète!\n"
                    completion_text += f"✅ Récompense déjà réclamée précédemment\n\n"
            
            embed = discord.Embed(
                title="🎊 ═══════〔 S É R I E   C O M P L È T E ! 〕═══════ 🎊",
                description=f"```\n◆ Félicitations! ◆\n```\n{completion_text}",
                color=BotConfig.RARITY_COLORS['Legendary'])
            
            if total_coins_awarded > 0:
                embed.set_footer(text=f"Total gagné: {total_coins_awarded:,} Shadow Coins • Récompenses sauvegardées définitivement")
            
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            # Just refresh the normal view
            embed = await self.create_sets_embed()
            await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='📋 Toutes les Séries', style=discord.ButtonStyle.success, row=0)
    async def show_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Récupérer toutes les séries avec leurs bonus
        sets_data = await self.bot.db.get_character_sets_with_progress(self.user_id)
        if not sets_data:
            await interaction.followup.send("Aucune série disponible.", ephemeral=True)
            return
        
        # Créer la vue détaillée de toutes les séries
        view = AllSeriesDetailsView(self.bot, self.user_id, sets_data)
        embed = await view.create_all_series_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)