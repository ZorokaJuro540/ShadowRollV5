"""
Enhanced Visual Menu System for Shadow Roll Bot
Dramatically improved aesthetics with images, animations, and visual effects
"""

import discord
from discord.ext import commands
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime
from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.utils import get_display_name

logger = logging.getLogger(__name__)

class EnhancedMenuView(discord.ui.View):
    """Menu principal avec esthétique améliorée et éléments visuels"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_enhanced_main_menu_embed(self) -> discord.Embed:
        """Créer un menu principal avec esthétique dramatiquement améliorée"""
        try:
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"
            player = await self.bot.db.get_or_create_player(self.user_id, username)

            # Bannières animées rotatives
            animated_banners = [
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGJ2d2p5azBxbWFxY3B4dGN4cGNvNjFtcmpvMTlyZ3d6ejhsaGw5bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26BRBKqUiq586bRVm/giphy.gif",
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHlvNXN4YmJmNGdkeDNvZGhqMWh5bmF5YzVvNXN5cnU3dHB6NnRjeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgzoKnwFNmISR8I/giphy.gif",
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWN1c3FjYTJvcnIydjVocTRpdGwxNHB0MG5jNWhvNWZkZWRtaDJyMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41lGvinEgARjB2HC/giphy.gif",
                "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHd4bHN4ams5NDNhM3NrcDRmOG5zOXYxZzg1OWN4aHJqaDdzc3VmbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3q2XhfQ8oCkm1Ts4/giphy.gif"
            ]

            # Créer un embed sans titre pour utiliser la description
            embed = discord.Embed(
                description=f"""```ansi
\u001b[1;35m╔════════════════════════════════════════════════════════════╗\u001b[0m
\u001b[1;36m║                    🌌 SHADOW ROLL SYSTEM 🌌                ║\u001b[0m
\u001b[1;35m╚════════════════════════════════════════════════════════════╝\u001b[0m

\u001b[1;33m✦ Bienvenue dans les ténèbres, {username} ✦\u001b[0m
\u001b[1;32m🪙 Fortune des Ombres: {format_number(player.coins)} Shadow Coins\u001b[0m
\u001b[1;34m🎭 Système de jeu anime et mystique activé\u001b[0m
\u001b[1;31m⚡ Dernière connexion: {datetime.now().strftime('%H:%M')}\u001b[0m
```""",
                color=0x7b2cbf
            )

            # Navigation stylisée avec couleurs ANSI
            navigation_text = """```ansi
\u001b[1;31m┌─────────────────────────────────────────────────────────────┐\u001b[0m
\u001b[1;31m│                    ⭐ NAVIGATION SYSTEM ⭐                   │\u001b[0m
\u001b[1;31m└─────────────────────────────────────────────────────────────┘\u001b[0m

\u001b[1;36m👤 PROFIL\u001b[0m        ▸ \u001b[0;37mVos statistiques et achievements\u001b[0m
\u001b[1;33m🎲 INVOCATION\u001b[0m    ▸ \u001b[0;37mInvoquer des personnages légendaires\u001b[0m
\u001b[1;35m🧪 RECHERCHE\u001b[0m     ▸ \u001b[0;37mTraquer un personnage spécifique\u001b[0m
\u001b[1;32m🎒 COLLECTION\u001b[0m    ▸ \u001b[0;37mExplorer vos trésors collectés\u001b[0m
\u001b[1;34m🔮 CRAFT\u001b[0m         ▸ \u001b[0;37mÉvolution et fusion mystique\u001b[0m
\u001b[1;93m🎁 BÉNÉDICTION\u001b[0m   ▸ \u001b[0;37mRécompense quotidienne des ombres\u001b[0m
\u001b[1;32m🛒 BOUTIQUE\u001b[0m      ▸ \u001b[0;37mObjets magiques et potions\u001b[0m
\u001b[1;91m🪙 VENTE\u001b[0m         ▸ \u001b[0;37mRevendre vos personnages\u001b[0m
\u001b[1;33m🎖️ SUCCÈS\u001b[0m        ▸ \u001b[0;37mExploits et récompenses épiques\u001b[0m
\u001b[1;35m🏆 CLASSEMENT\u001b[0m    ▸ \u001b[0;37mTableau des maîtres légendaires\u001b[0m
\u001b[1;34m❓ GUIDE\u001b[0m         ▸ \u001b[0;37mAide et informations détaillées\u001b[0m
```"""

            embed.add_field(name="", value=navigation_text, inline=False)
            
            # Vérifier les effets actifs
            try:
                active_effects = []
                if hasattr(self.bot.db, 'db'):
                    cursor = await self.bot.db.db.execute(
                        "SELECT buff_type, expires_at FROM temporary_buffs WHERE user_id = ? AND expires_at > ?",
                        (self.user_id, int(datetime.now().timestamp()))
                    )
                    buffs = await cursor.fetchall()
                    for buff in buffs:
                        remaining_time = buff[1] - int(datetime.now().timestamp())
                        if remaining_time > 0:
                            hours = remaining_time // 3600
                            minutes = (remaining_time % 3600) // 60
                            time_str = f"{hours}h{minutes:02d}m" if hours > 0 else f"{minutes}m"
                            effect_name = buff[0].replace('_', ' ').title()
                            active_effects.append(f"✨ {effect_name} ({time_str})")
                
                if active_effects:
                    effects_text = "```ansi\n\u001b[1;32m🪙 EFFETS MAGIQUES ACTIFS:\u001b[0m\n"
                    for effect in active_effects[:3]:  # Limiter à 3 effets
                        effects_text += f"\u001b[1;33m{effect}\u001b[0m\n"
                    effects_text += "```"
                    embed.add_field(name="", value=effects_text, inline=False)
            except Exception as e:
                logger.debug(f"Could not fetch active effects: {e}")
            
            # Section statistiques rapides
            try:
                stats = await self.bot.db.get_inventory_stats(self.user_id)
                quick_stats = f"""```ansi
\u001b[1;94m📊 STATISTIQUES RAPIDES:\u001b[0m
\u001b[1;37m🎴 Personnages Uniques: {stats.get('unique_characters', 0)}\u001b[0m
\u001b[1;37m📦 Collection Totale: {stats.get('total_characters', 0)}\u001b[0m
\u001b[1;37m🎲 Invocations Totales: {player.total_rerolls}\u001b[0m
```"""
                embed.add_field(name="", value=quick_stats, inline=False)
            except:
                pass
            
            # Bannière aléatoire
            embed.set_image(url=random.choice(animated_banners))
            
            # Thumbnail mystique
            embed.set_thumbnail(url="https://i.imgur.com/8bDdvxM.png")
            
            # Footer avec le pseudo du joueur (pas "I am atomic")
            embed.set_footer(
                text=f"🌌 Shadow Roll • Plongez dans les ténèbres • {username}",
                icon_url=user.avatar.url if user and user.avatar else None
            )

            return embed

        except Exception as e:
            pass
            logger.error(f"Error creating enhanced main menu embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger le menu principal",
                color=0xff0000)

    # Boutons avec couleurs améliorées (style drapeau français)
    @discord.ui.button(label='👤 Profil', style=discord.ButtonStyle.primary, row=0)
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ProfileView
        view = ProfileView(self.bot, self.user_id)
        embed = await view.create_profile_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎲 Invocation', style=discord.ButtonStyle.secondary, row=0)
    async def summon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import RollView
        view = RollView(self.bot, self.user_id)
        embed, _ = await view.perform_roll()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🧪 Recherche', style=discord.ButtonStyle.danger, row=0)
    async def hunt_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.hunt_system import CharacterHuntView
        view = CharacterHuntView(self.user_id, self.bot.db)
        embed = await view.create_hunt_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎒 Collection', style=discord.ButtonStyle.secondary, row=1)
    async def collection_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.inventory import EnhancedInventoryView
        view = EnhancedInventoryView(self.bot, self.user_id)
        embed = await view.create_inventory_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🔮 Craft', style=discord.ButtonStyle.secondary, row=1)
    async def craft_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.craft_system import CraftView
        view = CraftView(self.bot, self.user_id)
        embed = await view.create_craft_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎁 Bénédiction', style=discord.ButtonStyle.secondary, row=1)
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import DailyView
        view = DailyView(self.bot, self.user_id)
        embed = await view.claim_daily_reward()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🛒 Boutique', style=discord.ButtonStyle.success, row=2)
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.shop_new import ModernShopView
        view = ModernShopView(self.bot, self.user_id)
        embed = await view.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🪙 Vendre', style=discord.ButtonStyle.secondary, row=2)
    async def sell_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.sell import SellView
        view = SellView(self.bot, self.user_id)
        embed = await view.create_sell_embed()
        await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(label='🎖️ Succès', style=discord.ButtonStyle.secondary, row=2)
    async def achievements_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import AchievementsView
        view = AchievementsView(self.bot, self.user_id)
        embed = await view.create_achievements_embed()
        await interaction.edit_original_response(embed=embed, view=view)


# Fonction pour créer un embed de menu amélioré
async def create_enhanced_main_menu_embed(bot, user_id: int) -> discord.Embed:
    """Créer un embed de menu principal avec esthétique améliorée"""
    view = EnhancedMenuView(bot, user_id)
    return await create_main_menu_embed(self.bot, self.user_id)


# Intégration avec le système de commandes existant
async def setup_enhanced_menu_commands(bot):
    """Configurer les commandes pour le menu amélioré"""
    
    @bot.command(name='newmenu', aliases=['nmenu', 'enhanced'])
    async def enhanced_menu_command(ctx):
        """Commande pour le nouveau menu amélioré"""
        try:
            view = EnhancedMenuView(bot, ctx.author.id)
            embed = await create_main_menu_embed(self.bot, self.user_id)
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            pass
            logger.error(f"Error in enhanced menu command: {e}")
            await ctx.send("❌ Erreur lors de l'affichage du menu amélioré.")
    
    logger.info("Enhanced menu commands setup completed")