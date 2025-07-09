"""
Trade system for Shadow Roll Bot
Allows players to safely trade characters with each other
"""

import discord
from discord.ext import commands
from core.config import BotConfig
from typing import Dict, List, Optional
import asyncio
import logging
import time

logger = logging.getLogger(__name__)

class TradeOffer:
    """Represents a trade offer between two players"""
    
    def __init__(self, initiator_id: int, target_id: int):
        self.initiator_id = initiator_id
        self.target_id = target_id
        self.initiator_characters = []  # List of character IDs
        self.target_characters = []
        self.initiator_confirmed = False
        self.target_confirmed = False
        self.created_at = time.time()
        self.confirmation_timestamp = None
        self.status = "pending"  # pending, confirmed, completed, cancelled, expired
        
    def is_expired(self) -> bool:
        """Check if trade offer has expired (5 minutes)"""
        return time.time() - self.created_at > 300
        
    def can_confirm(self) -> bool:
        """Check if trade can be confirmed (both sides have items)"""
        return len(self.initiator_characters) > 0 and len(self.target_characters) > 0
        
    def both_confirmed(self) -> bool:
        """Check if both parties have confirmed"""
        return self.initiator_confirmed and self.target_confirmed
        
    def set_confirmation_timer(self):
        """Set the 10-second confirmation timer"""
        if self.both_confirmed() and not self.confirmation_timestamp:
            self.confirmation_timestamp = time.time()
            
    def is_ready_to_execute(self) -> bool:
        """Check if trade is ready to execute (10 seconds after both confirmed)"""
        if not self.confirmation_timestamp:
            return False
        return time.time() - self.confirmation_timestamp >= 10


class TradeManager:
    """Manages all active trades"""
    
    def __init__(self):
        self.active_trades = {}  # trade_id -> TradeOffer
        self.user_trades = {}    # user_id -> trade_id
        
    def create_trade(self, initiator_id: int, target_id: int) -> str:
        """Create a new trade offer"""
        trade_id = f"{initiator_id}_{target_id}_{int(time.time())}"
        trade = TradeOffer(initiator_id, target_id)
        
        self.active_trades[trade_id] = trade
        self.user_trades[initiator_id] = trade_id
        self.user_trades[target_id] = trade_id
        
        return trade_id
        
    def get_trade(self, trade_id: str) -> Optional[TradeOffer]:
        """Get a trade by ID"""
        return self.active_trades.get(trade_id)
        
    def get_user_trade(self, user_id: int) -> Optional[TradeOffer]:
        """Get active trade for a user"""
        trade_id = self.user_trades.get(user_id)
        if trade_id:
            return self.active_trades.get(trade_id)
        return None
        
    def cancel_trade(self, trade_id: str):
        """Cancel a trade"""
        if trade_id in self.active_trades:
            trade = self.active_trades[trade_id]
            # Remove from user mappings
            self.user_trades.pop(trade.initiator_id, None)
            self.user_trades.pop(trade.target_id, None)
            # Remove trade
            del self.active_trades[trade_id]
            
    def cleanup_expired_trades(self):
        """Remove expired trades"""
        expired_trades = []
        for trade_id, trade in self.active_trades.items():
            if trade.is_expired():
                expired_trades.append(trade_id)
                
        for trade_id in expired_trades:
            self.cancel_trade(trade_id)


# Global trade manager
trade_manager = TradeManager()


class TradeMenuView(discord.ui.View):
    """Trade menu interface for selecting trade options"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact with this view"""
        return interaction.user.id == self.user_id
    
    async def create_trade_menu_embed(self) -> discord.Embed:
        """Create the trade menu embed"""
        user = await self.bot.fetch_user(self.user_id)
        username = user.display_name if user else f"User {self.user_id}"
        
        embed = discord.Embed(
            title="🔄 ═══════〔 S Y S T È M E   D E   T R A D E 〕═══════ 🔄",
            description=f"```\n◆ Échangez vos personnages en toute sécurité, {username} ◆\nSystème de trade sécurisé avec délai anti-arnaque\n```",
            color=0x00BFFF
        )
        
        # Check if user has active trade
        active_trade = trade_manager.get_user_trade(self.user_id)
        
        if active_trade:
            # Show active trade info
            if active_trade.initiator_id == self.user_id:
                other_user_id = active_trade.target_id
            else:
                other_user_id = active_trade.initiator_id
                
            try:
                other_user = await self.bot.fetch_user(other_user_id)
                other_username = other_user.display_name if other_user else f"User {other_user_id}"
            except:
                other_username = f"User {other_user_id}"
            
            embed.add_field(
                name="🔄 Trade Actif",
                value=f"Vous avez un trade en cours avec **{other_username}**",
                inline=False
            )
            
            status = "En attente" if not active_trade.both_confirmed() else "Confirmé"
            embed.add_field(
                name="📊 Statut",
                value=f"**{status}**",
                inline=True
            )
            
            if active_trade.confirmation_timestamp:
                time_left = 10 - (time.time() - active_trade.confirmation_timestamp)
                if time_left > 0:
                    embed.add_field(
                        name="⏱️ Temps Restant",
                        value=f"{time_left:.1f}s",
                        inline=True
                    )
                    
        else:
            embed.add_field(
                name="🌑 ═══〔 Options de Trade 〕═══ 🌑",
                value=("```\n"
                       "🎯 Proposer Trade ◆ Créer une offre d'échange\n"
                       "📋 Mes Trades     ◆ Voir vos trades en cours\n"
                       "📖 Guide Trade    ◆ Comment utiliser le système\n"
                       "🏠 Menu Principal ◆ Retour au menu\n"
                       "```"),
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Sécurité",
                value="• Délai de 10 secondes après confirmation\n• Impossible d'annuler pendant l'exécution\n• Vérifiez bien avant de confirmer",
                inline=False
            )
            
        embed.set_footer(text="🔄 Trade • Échangez en toute sécurité")
        
        return embed
        
    @discord.ui.button(label="🎯 Proposer Trade", style=discord.ButtonStyle.primary, row=0)
    async def propose_trade_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start a new trade"""
        # Check if user already has active trade
        if trade_manager.get_user_trade(self.user_id):
            await interaction.response.send_message("❌ Vous avez déjà un trade en cours!", ephemeral=True)
            return
            
        # Create trade proposal modal
        modal = TradeProposalModal(self.bot, self.user_id)
        await interaction.response.send_modal(modal)
        
    @discord.ui.button(label="📋 Mes Trades", style=discord.ButtonStyle.secondary, row=0)
    async def my_trades_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View active trades"""
        active_trade = trade_manager.get_user_trade(self.user_id)
        
        if not active_trade:
            await interaction.response.send_message("❌ Vous n'avez aucun trade en cours!", ephemeral=True)
            return
            
        # Find trade ID
        trade_id = None
        for tid, trade in trade_manager.active_trades.items():
            if trade == active_trade:
                trade_id = tid
                break
                
        if not trade_id:
            await interaction.response.send_message("❌ Erreur: Trade introuvable!", ephemeral=True)
            return
            
        # Show trade interface
        trade_view = TradeView(self.bot, trade_id, self.user_id)
        embed = await trade_view.create_trade_embed()
        await interaction.response.send_message(embed=embed, view=trade_view, ephemeral=True)
        
    @discord.ui.button(label="📖 Guide Trade", style=discord.ButtonStyle.secondary, row=0)
    async def trade_guide_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show trade guide"""
        embed = discord.Embed(
            title="📖 Guide du Système de Trade",
            description="Comment utiliser le système d'échange sécurisé",
            color=0x00BFFF
        )
        
        embed.add_field(
            name="🎯 Comment proposer un trade",
            value="1. Utilisez `/trade @joueur` ou le bouton **Proposer Trade**\n2. Ajoutez vos personnages à l'échange\n3. Attendez que l'autre joueur ajoute les siens",
            inline=False
        )
        
        embed.add_field(
            name="✅ Confirmer l'échange",
            value="1. Vérifiez les personnages proposés\n2. Cliquez sur **Confirmer** quand vous êtes sûr\n3. Attendez la confirmation de l'autre joueur",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Sécurité anti-arnaque",
            value="• **10 secondes** de délai après les confirmations\n• Impossible d'annuler pendant l'exécution\n• Vérifiez toujours avant de confirmer",
            inline=False
        )
        
        embed.add_field(
            name="🚫 Règles importantes",
            value="• Un seul trade à la fois par joueur\n• Trade expire après 5 minutes d'inactivité\n• Les deux joueurs doivent avoir des personnages",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.danger, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class TradeProposalModal(discord.ui.Modal):
    """Modal for proposing a trade"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(title="🔄 Proposer un Trade")
        self.bot = bot
        self.user_id = user_id
        
        self.target_input = discord.ui.TextInput(
            label="Nom d'utilisateur ou ID Discord",
            placeholder="Exemple: @username ou 123456789012345678",
            required=True,
            max_length=100
        )
        self.add_item(self.target_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        """Handle trade proposal submission"""
        target_input = self.target_input.value.strip()
        
        # Try to find user
        target_user = None
        
        # Remove @ if present
        if target_input.startswith('@'):
            target_input = target_input[1:]
            
        # Try by ID first
        if target_input.isdigit():
            try:
                target_user = await self.bot.fetch_user(int(target_input))
            except:
                pass
                
        # Try by username in guild
        if not target_user:
            for guild in self.bot.guilds:
                member = discord.utils.find(lambda m: m.display_name.lower() == target_input.lower() or m.name.lower() == target_input.lower(), guild.members)
                if member:
                    target_user = member
                    break
                    
        if not target_user:
            await interaction.response.send_message("❌ Utilisateur introuvable! Utilisez un nom d'utilisateur exact ou un ID Discord.", ephemeral=True)
            return
            
        # Check if target is bot or self
        if target_user.bot:
            await interaction.response.send_message("❌ Vous ne pouvez pas faire de trade avec un bot!", ephemeral=True)
            return
            
        if target_user.id == self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas faire de trade avec vous-même!", ephemeral=True)
            return
            
        # Check if either user is banned
        if await self.bot.db.is_banned(self.user_id) or await self.bot.db.is_banned(target_user.id):
            await interaction.response.send_message("❌ Un des joueurs est banni du bot.", ephemeral=True)
            return
            
        # Check if either user already has active trade
        if trade_manager.get_user_trade(self.user_id):
            await interaction.response.send_message("❌ Vous avez déjà un trade en cours!", ephemeral=True)
            return
            
        if trade_manager.get_user_trade(target_user.id):
            await interaction.response.send_message("❌ Ce joueur a déjà un trade en cours!", ephemeral=True)
            return
            
        # Create trade
        trade_id = trade_manager.create_trade(self.user_id, target_user.id)
        
        # Create trade view
        trade_view = TradeView(self.bot, trade_id, self.user_id)
        embed = await trade_view.create_trade_embed()
        
        await interaction.response.send_message(embed=embed, view=trade_view)
        
        # Notify target user
        try:
            user = await self.bot.fetch_user(self.user_id)
            username = user.display_name if user else f"User {self.user_id}"
            
            embed_notif = discord.Embed(
                title="🔄 Proposition de Trade",
                description=f"**{username}** vous propose un échange!",
                color=0x00BFFF
            )
            embed_notif.add_field(
                name="🎯 Action requise",
                value="Rendez-vous dans le serveur pour accepter ou refuser l'échange.",
                inline=False
            )
            
            await target_user.send(embed=embed_notif)
        except:
            pass  # User might have DMs disabled


class TradeView(discord.ui.View):
    """Main trade interface"""
    
    def __init__(self, bot, trade_id: str, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.trade_id = trade_id
        self.user_id = user_id
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact with this view"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            return False
        return interaction.user.id in [trade.initiator_id, trade.target_id]
    
    async def create_trade_embed(self) -> discord.Embed:
        """Create the trade interface embed"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            return discord.Embed(title="❌ Trade Expiré", color=0xFF0000)
            
        # Get user info
        initiator = await self.bot.fetch_user(trade.initiator_id)
        target = await self.bot.fetch_user(trade.target_id)
        
        embed = discord.Embed(
            title="🔄 Interface de Trade",
            description=f"Trade entre **{initiator.display_name}** et **{target.display_name}**",
            color=0x00BFFF
        )
        
        # Initiator's side
        initiator_text = "Aucun personnage sélectionné"
        if trade.initiator_characters:
            chars = []
            for char_id in trade.initiator_characters:
                char = await self.bot.db.get_character_cached(char_id)
                if char:
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    chars.append(f"{rarity_emoji} {char['name']} ({char['anime']})")
            initiator_text = "\n".join(chars)
            
        embed.add_field(
            name=f"👤 {initiator.display_name}" + (" ✅" if trade.initiator_confirmed else ""),
            value=initiator_text,
            inline=True
        )
        
        # Target's side  
        target_text = "Aucun personnage sélectionné"
        if trade.target_characters:
            chars = []
            for char_id in trade.target_characters:
                char = await self.bot.db.get_character_cached(char_id)
                if char:
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                    chars.append(f"{rarity_emoji} {char['name']} ({char['anime']})")
            target_text = "\n".join(chars)
            
        embed.add_field(
            name=f"👤 {target.display_name}" + (" ✅" if trade.target_confirmed else ""),
            value=target_text,
            inline=True
        )
        
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer
        
        # Status information
        if trade.both_confirmed():
            if trade.confirmation_timestamp:
                time_left = 10 - (time.time() - trade.confirmation_timestamp)
                if time_left > 0:
                    embed.add_field(
                        name="⏱️ Confirmation",
                        value=f"Trade en cours d'exécution dans {time_left:.1f}s",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="✅ Prêt",
                        value="Trade prêt à être exécuté!",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="⏱️ Confirmation",
                    value="Lancement du timer de sécurité...",
                    inline=False
                )
        else:
            embed.add_field(
                name="ℹ️ Statut",
                value="En attente des confirmations des deux joueurs",
                inline=False
            )
            
        embed.set_footer(text="⚠️ Sécurité: 10 secondes de délai après confirmation pour éviter les arnaques")
        
        return embed
        
    @discord.ui.button(label="➕ Ajouter Personnage", style=discord.ButtonStyle.secondary, row=0)
    async def add_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add character to trade"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade or trade.both_confirmed():
            await interaction.response.send_message("❌ Impossible de modifier le trade maintenant!", ephemeral=True)
            return
            
        # Show character selection
        select_view = CharacterSelectView(self.bot, self.trade_id, interaction.user.id)
        embed = await select_view.create_selection_embed()
        
        await interaction.response.send_message(embed=embed, view=select_view, ephemeral=True)
        
    @discord.ui.button(label="➖ Retirer Personnage", style=discord.ButtonStyle.secondary, row=0)
    async def remove_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove character from trade"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade or trade.both_confirmed():
            await interaction.response.send_message("❌ Impossible de modifier le trade maintenant!", ephemeral=True)
            return
            
        # Show character removal
        remove_view = CharacterRemoveView(self.bot, self.trade_id, interaction.user.id)
        embed = await remove_view.create_removal_embed()
        
        await interaction.response.send_message(embed=embed, view=remove_view, ephemeral=True)
        
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success, row=1)
    async def confirm_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirm the trade"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            await interaction.response.send_message("❌ Trade introuvable!", ephemeral=True)
            return
            
        if not trade.can_confirm():
            await interaction.response.send_message("❌ Les deux joueurs doivent avoir des personnages à échanger!", ephemeral=True)
            return
            
        # Set confirmation
        if interaction.user.id == trade.initiator_id:
            trade.initiator_confirmed = True
        else:
            trade.target_confirmed = True
            
        # Check if both confirmed
        if trade.both_confirmed():
            trade.set_confirmation_timer()
            
            # Start the execution timer
            await asyncio.sleep(10)
            
            # Execute trade if still valid
            if trade.is_ready_to_execute():
                success = await self.execute_trade()
                if success:
                    embed = discord.Embed(
                        title="✅ Trade Réalisé!",
                        description="L'échange a été effectué avec succès!",
                        color=0x00FF00
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                    trade_manager.cancel_trade(self.trade_id)
                    return
                    
        # Update display
        embed = await self.create_trade_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger, row=1)
    async def cancel_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancel the trade"""
        trade_manager.cancel_trade(self.trade_id)
        
        embed = discord.Embed(
            title="❌ Trade Annulé",
            description="Le trade a été annulé.",
            color=0xFF0000
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        
    async def execute_trade(self) -> bool:
        """Execute the actual trade"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            return False
            
        try:
            # Transfer characters
            for char_id in trade.initiator_characters:
                # Remove from initiator, add to target
                await self.bot.db.transfer_character(trade.initiator_id, trade.target_id, char_id)
                
            for char_id in trade.target_characters:
                # Remove from target, add to initiator  
                await self.bot.db.transfer_character(trade.target_id, trade.initiator_id, char_id)
                
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False


class CharacterSelectView(discord.ui.View):
    """Character selection for trade"""
    
    def __init__(self, bot, trade_id: str, user_id: int, page: int = 1):
        super().__init__(timeout=60)
        self.bot = bot
        self.trade_id = trade_id
        self.user_id = user_id
        self.page = page
        
    async def create_selection_embed(self) -> discord.Embed:
        """Create character selection embed"""
        inventory = await self.bot.db.get_player_inventory(self.user_id, self.page, 10)
        
        embed = discord.Embed(
            title="➕ Sélectionner un Personnage",
            description="Choisissez un personnage à ajouter au trade:",
            color=0x00BFFF
        )
        
        if not inventory:
            embed.add_field(
                name="📭 Inventaire Vide",
                value="Vous n'avez aucun personnage disponible.",
                inline=False
            )
            return embed
            
        # Create character list
        char_list = []
        for i, item in enumerate(inventory[:10], 1):
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(item['rarity'], '◆')
            char_list.append(f"`{i}.` {rarity_emoji} **{item['name']}** ({item['anime']})")
            
        embed.add_field(
            name="📋 Vos Personnages",
            value="\n".join(char_list) if char_list else "Aucun personnage",
            inline=False
        )
        
        # Update select options
        self._update_select_options(inventory)
        
        return embed
        
    def _update_select_options(self, inventory: List[Dict]):
        """Update select menu options"""
        if not inventory:
            return
            
        options = []
        for item in inventory[:10]:
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(item['rarity'], '◆')
            options.append(discord.SelectOption(
                label=f"{item['name']} ({item['anime']})",
                description=f"{rarity_emoji} {item['rarity']} | Valeur: {item['value']:,}",
                value=str(item['character_id'])
            ))
            
        if options:
            self.character_select.options = options[:25]  # Discord limit
        
    @discord.ui.select(placeholder="Choisissez un personnage...", row=0)
    async def character_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle character selection"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            await interaction.response.send_message("❌ Trade introuvable!", ephemeral=True)
            return
            
        char_id = int(select.values[0])
        
        # Add to appropriate list
        if interaction.user.id == trade.initiator_id:
            if char_id not in trade.initiator_characters:
                trade.initiator_characters.append(char_id)
        else:
            if char_id not in trade.target_characters:
                trade.target_characters.append(char_id)
                
        # Reset confirmations
        trade.initiator_confirmed = False
        trade.target_confirmed = False
        trade.confirmation_timestamp = None
        
        await interaction.response.send_message("✅ Personnage ajouté au trade!", ephemeral=True)


class CharacterRemoveView(discord.ui.View):
    """Character removal from trade"""
    
    def __init__(self, bot, trade_id: str, user_id: int):
        super().__init__(timeout=60)
        self.bot = bot
        self.trade_id = trade_id
        self.user_id = user_id
        
    async def create_removal_embed(self) -> discord.Embed:
        """Create character removal embed"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            return discord.Embed(title="❌ Trade Introuvable", color=0xFF0000)
            
        embed = discord.Embed(
            title="➖ Retirer un Personnage",
            description="Choisissez un personnage à retirer du trade:",
            color=0xFF8C00
        )
        
        # Get user's characters in trade
        char_ids = []
        if self.user_id == trade.initiator_id:
            char_ids = trade.initiator_characters
        else:
            char_ids = trade.target_characters
            
        if not char_ids:
            embed.add_field(
                name="📭 Aucun Personnage",
                value="Vous n'avez aucun personnage dans le trade.",
                inline=False
            )
            return embed
            
        # Create character list
        char_list = []
        options = []
        for i, char_id in enumerate(char_ids, 1):
            char = await self.bot.db.get_character_cached(char_id)
            if char:
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
                char_list.append(f"`{i}.` {rarity_emoji} **{char['name']}** ({char['anime']})")
                
                options.append(discord.SelectOption(
                    label=f"{char['name']} ({char['anime']})",
                    description=f"{rarity_emoji} {char['rarity']}",
                    value=str(char_id)
                ))
                
        embed.add_field(
            name="📋 Vos Personnages dans le Trade",
            value="\n".join(char_list) if char_list else "Aucun personnage",
            inline=False
        )
        
        # Update select options
        if options:
            self.character_remove.options = options[:25]
            
        return embed
        
    @discord.ui.select(placeholder="Choisissez un personnage à retirer...", row=0)
    async def character_remove(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle character removal"""
        trade = trade_manager.get_trade(self.trade_id)
        if not trade:
            await interaction.response.send_message("❌ Trade introuvable!", ephemeral=True)
            return
            
        char_id = int(select.values[0])
        
        # Remove from appropriate list
        if interaction.user.id == trade.initiator_id:
            if char_id in trade.initiator_characters:
                trade.initiator_characters.remove(char_id)
        else:
            if char_id in trade.target_characters:
                trade.target_characters.remove(char_id)
                
        # Reset confirmations
        trade.initiator_confirmed = False
        trade.target_confirmed = False
        trade.confirmation_timestamp = None
        
        await interaction.response.send_message("✅ Personnage retiré du trade!", ephemeral=True)


async def setup_trade_commands(bot):
    """Setup trade-related commands"""
    
    @bot.tree.command(name="trade", description="Proposer un échange avec un autre joueur")
    async def trade_slash(interaction: discord.Interaction, joueur: discord.Member):
        """Trade command"""
        try:
            await interaction.response.defer()
            
            # Check if user is banned
            if await bot.db.is_banned(interaction.user.id):
                await interaction.followup.send(BotConfig.MESSAGES['banned'], ephemeral=True)
                return
                
            # Check if target is banned
            if await bot.db.is_banned(joueur.id):
                await interaction.followup.send("❌ Ce joueur est banni du bot.", ephemeral=True)
                return
                
            # Can't trade with yourself
            if interaction.user.id == joueur.id:
                await interaction.followup.send("❌ Vous ne pouvez pas faire de trade avec vous-même!", ephemeral=True)
                return
                
            # Check if either user already has an active trade
            if trade_manager.get_user_trade(interaction.user.id):
                await interaction.followup.send("❌ Vous avez déjà un trade en cours!", ephemeral=True)
                return
                
            if trade_manager.get_user_trade(joueur.id):
                await interaction.followup.send("❌ Ce joueur a déjà un trade en cours!", ephemeral=True)
                return
                
            # Create trade offer
            trade_id = trade_manager.create_trade(interaction.user.id, joueur.id)
            
            # Create trade view
            trade_view = TradeView(bot, trade_id, interaction.user.id)
            embed = await trade_view.create_trade_embed()
            
            await interaction.followup.send(embed=embed, view=trade_view)
            
            # Notify target user
            try:
                embed_notif = discord.Embed(
                    title="🔄 Proposition de Trade",
                    description=f"**{interaction.user.display_name}** vous propose un échange!",
                    color=0x00BFFF
                )
                await joueur.send(embed=embed_notif)
            except:
                pass  # User might have DMs disabled
                
        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            await interaction.followup.send("❌ Erreur lors de la création du trade.", ephemeral=True)
            
    # Cleanup task
    @bot.event
    async def on_ready():
        """Cleanup expired trades on bot ready"""
        async def cleanup_trades():
            while True:
                trade_manager.cleanup_expired_trades()
                await asyncio.sleep(60)  # Cleanup every minute
                
        bot.loop.create_task(cleanup_trades())


async def setup(bot):
    """Setup function for the trade module"""
    await setup_trade_commands(bot)
    logger.info("Trade system setup completed")