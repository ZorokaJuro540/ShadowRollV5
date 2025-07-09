"""
Slash commands for Shadow Roll Bot
Centralized slash command definitions
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from datetime import datetime
from typing import Optional

from core.config import BotConfig
from modules.utils import format_number, get_cooldown_remaining, get_display_name
from modules.achievements import AchievementManager

logger = logging.getLogger(__name__)


async def play_summoning_animation(interaction_or_ctx, character_rarity: str, is_multiple: bool = False):
    """Play dramatic animation for legendary, mythical, titan and duo character summons"""
    if character_rarity == "Legendary":
        # Stage 1
        embed1 = discord.Embed(title="⚡ Invocation Légendaire", 
                              description="L'air devient électrique...", 
                              color=0xFFD700)
        await interaction_or_ctx.followup.send(embed=embed1, ephemeral=False)
        await asyncio.sleep(1.5)
        
        # Stage 2  
        embed2 = discord.Embed(title="🔥 Invocation Légendaire", 
                              description=f"{'Des forces ancestrales approchent' if is_multiple else 'Une force ancestrale approche'}...", 
                              color=0xFFD700)
        await interaction_or_ctx.followup.send(embed=embed2, ephemeral=False)
        await asyncio.sleep(1.5)
        
        # Stage 3
        embed3 = discord.Embed(title="🔶 Invocation Légendaire", 
                              description=f"{'Des héros légendaires surgissent' if is_multiple else 'Un héros légendaire surgit'} des ténèbres !", 
                              color=0xFFD700)
        await interaction_or_ctx.followup.send(embed=embed3, ephemeral=False)
        await asyncio.sleep(1)
    elif character_rarity == "Mythic":
        # Stage 1
        embed1 = discord.Embed(title="🌌 Invocation Mythique", 
                              description="Les dimensions s'effondrent autour de vous...", 
                              color=0x9400D3)
        await interaction_or_ctx.followup.send(embed=embed1, ephemeral=False)
        await asyncio.sleep(1.5)
        
        # Stage 2
        embed2 = discord.Embed(title="✨ Invocation Mythique", 
                              description="Une énergie mythique consume l'espace...", 
                              color=0x9400D3)
        await interaction_or_ctx.followup.send(embed=embed2, ephemeral=False)
        await asyncio.sleep(1.5)
        
        # Stage 3
        embed3 = discord.Embed(title="💥 🌠 Invocation Mythique", 
                              description=f"{'Plusieurs entités' if is_multiple else 'Une entité'} d'un autre monde se matérialise{'nt' if is_multiple else ''} !", 
                              color=0x9400D3)
        await interaction_or_ctx.followup.send(embed=embed3, ephemeral=False)
        await asyncio.sleep(1)
    elif character_rarity == "Titan":
        # Stage 1
        embed1 = discord.Embed(title="🔱 Invocation Titanesque", 
                              description="La réalité tremble sous une force colossale...", 
                              color=0xdc143c)
        await interaction_or_ctx.followup.send(embed=embed1, ephemeral=False)
        await asyncio.sleep(2)
        
        # Stage 2
        embed2 = discord.Embed(title="⚡ Invocation Titanesque", 
                              description="Des énergies titanesques percent les dimensions...", 
                              color=0xdc143c)
        await interaction_or_ctx.followup.send(embed=embed2, ephemeral=False)
        await asyncio.sleep(2)
        
        # Stage 3
        embed3 = discord.Embed(title="🪙 🔱 Invocation Titanesque", 
                              description=f"{'Des titans légendaires' if is_multiple else 'Un titan légendaire'} émerge{'nt' if is_multiple else ''} des abysses du pouvoir !", 
                              color=0xdc143c)
        await interaction_or_ctx.followup.send(embed=embed3, ephemeral=False)
        await asyncio.sleep(1.5)
    elif character_rarity == "Fusion":
        # Stage 1
        embed1 = discord.Embed(title="⭐ Invocation Ultime", 
                              description="L'univers entier s'arrête de respirer...", 
                              color=0xff1493)
        await interaction_or_ctx.followup.send(embed=embed1, ephemeral=False)
        await asyncio.sleep(2.5)
        
        # Stage 2
        embed2 = discord.Embed(title="💫 Invocation Ultime", 
                              description="Une confrontation épique transcende toute existence...", 
                              color=0xff1493)
        await interaction_or_ctx.followup.send(embed=embed2, ephemeral=False)
        await asyncio.sleep(2.5)
        
        # Stage 3
        embed3 = discord.Embed(title="✨ ⭐ Invocation Ultime", 
                              description=f"{'Plusieurs duels' if is_multiple else 'Un duel'} légendaire{'s' if is_multiple else ''} se matérialise{'nt' if is_multiple else ''} dans toute sa gloire !", 
                              color=0xff1493)
        await interaction_or_ctx.followup.send(embed=embed3, ephemeral=False)
        await asyncio.sleep(2)
    elif character_rarity == "Secret":
        # Stage 1
        embed1 = discord.Embed(title="🌑 Invocation Secrète", 
                              description="Le vide absolu avale la réalité elle-même...", 
                              color=0x000000)
        await interaction_or_ctx.followup.send(embed=embed1, ephemeral=False)
        await asyncio.sleep(3)
        
        # Stage 2
        embed2 = discord.Embed(title="🖤 Invocation Secrète", 
                              description="Les secrets oubliés de l'existence se révèlent...", 
                              color=0x000000)
        await interaction_or_ctx.followup.send(embed=embed2, ephemeral=False)
        await asyncio.sleep(3)
        
        # Stage 3
        embed3 = discord.Embed(title="💀 🌑 Invocation Secrète", 
                              description=f"{'Des êtres' if is_multiple else 'Un être'} transcendant{'s' if is_multiple else ''} toute comprehension émerge{'nt' if is_multiple else ''} des ténèbres éternelles !", 
                              color=0x000000)
        await interaction_or_ctx.followup.send(embed=embed3, ephemeral=False)
        await asyncio.sleep(2.5)
    else:
        # Small delay for other rarities to maintain smooth flow
        await asyncio.sleep(0.5)


async def setup_slash_commands(bot):
    """Setup all slash commands for the bot"""

    @bot.tree.command(name="menu",
                      description="Afficher le menu principal Shadow Roll")
    async def menu_slash(interaction: discord.Interaction):
        """Slash command for main menu"""
        try:
            await interaction.response.defer()

            # Utiliser le menu Shadow Roll original
            from modules.menu import ShadowMenuView, create_main_menu_embed
            
            user_id = interaction.user.id
            embed = await create_main_menu_embed(bot, user_id)
            view = ShadowMenuView(bot, user_id)
            
            await interaction.followup.send(embed=embed, view=view)

        except Exception as e:
            logger.error(f"Error in menu slash command: {e}")
            await interaction.followup.send(
                f"❌ Erreur lors de la création du menu Shadow Roll: {str(e)}")
    
    # Fortnite navigation removed - shop functionality preserved in main menu

    @bot.tree.command(name="roll",
                      description="Invoquer un personnage anime aléatoire")
    @app_commands.describe(amount="Nombre de personnages à invoquer (1-10)")
    async def roll_slash(interaction: discord.Interaction,
                         amount: Optional[int] = 1):
        """Slash command for rolling characters"""
        try:
            user_id = interaction.user.id
            username = get_display_name(interaction.user)

            # Validate amount
            if amount is None:
                amount = 1
            if amount < 1 or amount > BotConfig.MAX_REROLLS_PER_COMMAND:
                await interaction.response.send_message(
                    f"❌ Vous pouvez invoquer 1-{BotConfig.MAX_REROLLS_PER_COMMAND} personnages à la fois!",
                    ephemeral=True)
                return

            # Get player
            player = await bot.db.get_or_create_player(user_id, username)

            # Check if user is banned
            if await bot.db.is_banned(user_id):
                await interaction.response.send_message(
                    "❌ Vous êtes banni du bot.", ephemeral=True)
                return

            # Check cooldown - use the last character's rarity if available
            if player.last_reroll:
                from modules.utils import get_rarity_cooldown
                
                # Get the last rolled character's rarity to determine cooldown
                cursor = await bot.db.db.execute("""
                    SELECT c.rarity FROM inventory i
                    JOIN characters c ON i.character_id = c.id
                    WHERE i.user_id = ?
                    ORDER BY i.id DESC LIMIT 1
                """, (user_id,))
                last_char = await cursor.fetchone()
                
                if last_char:
                    last_rarity = last_char[0]
                    cooldown_time = get_rarity_cooldown(last_rarity)
                else:
                    cooldown_time = BotConfig.REROLL_COOLDOWN
                
                cooldown_remaining = get_cooldown_remaining(
                    player.last_reroll, int(cooldown_time))
                if cooldown_remaining > 0:
                    await interaction.response.send_message(
                        f"⏰ Invocation en recharge! Réessayez dans {cooldown_remaining:.1f} secondes.",
                        ephemeral=True)
                    return

            # Check coins
            cost = BotConfig.REROLL_COST * amount
            if player.coins < cost:
                await interaction.response.send_message(
                    f"❌ Fonds insuffisants! Il vous faut {format_number(cost)} {BotConfig.CURRENCY_EMOJI} mais vous n'avez que {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}.",
                    ephemeral=True)
                return

            # Defer response for processing
            await interaction.response.defer()

            # Roll characters
            rolled_characters = []
            for _ in range(amount):
                character = await bot.db.get_character_by_rarity_weight(user_id, bot)
                if character:
                    rolled_characters.append(character)
                    await bot.db.add_character_to_inventory(
                        user_id, character.id)

            if not rolled_characters:
                await interaction.followup.send(
                    "❌ Erreur lors de l'invocation des personnages. Réessayez!"
                )
                return

            # Apply set bonuses to coin rewards
            set_bonuses = await bot.db.get_active_set_bonuses(user_id)
            
            # Update player stats
            new_coins = player.coins - cost
            current_time = datetime.now().isoformat()
            await bot.db.update_player_coins(user_id, new_coins)
            await bot.db.update_player_reroll_stats(user_id, current_time)
            
            # Check for newly completed sets
            newly_completed_sets = await bot.db.check_and_complete_sets(user_id)

            # Achievement system temporarily disabled for stability
            new_achievements = []

            # Create embed response with animation for rare characters
            if len(rolled_characters) == 1:
                character = rolled_characters[0]
                
                # Animation for Legendary and Mythic characters
                await play_summoning_animation(interaction, character.rarity, False)

                embed = discord.Embed(
                    title="🌌 ═══════〔 I N V O C A T I O N 〕═══════ 🌌",
                    description=f"```\n◆ Vous avez invoqué... ◆\n```",
                    color=character.get_rarity_color())

                embed.add_field(
                    name=f"{character.get_rarity_emoji()} {character.name}",
                    value=
                    f"**Anime:** {character.anime}\n**Rareté:** {character.rarity}\n**Valeur:** {format_number(character.value)} pièces",
                    inline=False)

                if character.image_url:
                    embed.set_image(url=character.image_url)

                embed.add_field(
                    name="🪙 Solde Restant",
                    value=
                    f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                    inline=True)
                
                # Add luck bonus display
                luck_bonuses = await bot.db.calculate_luck_bonus(user_id)
                bonus_text = ""
                
                if luck_bonuses['total'] > 0:
                    bonus_text += f"🍀 Bonus Chance: +{luck_bonuses['total']}%"
                    if luck_bonuses['rare'] > 0:
                        bonus_text += f"\n◇ Rare: +{luck_bonuses['rare']}%"
                    if luck_bonuses['epic'] > 0:
                        bonus_text += f"\n◈ Epic: +{luck_bonuses['epic']}%"
                    if luck_bonuses['legendary'] > 0:
                        bonus_text += f"\n◉ Legendary: +{luck_bonuses['legendary']}%"
                    if luck_bonuses['mythical'] > 0:
                        bonus_text += f"\n⬢ Mythic: +{luck_bonuses['mythical']}%"
                    
                # Add set completion notifications
                if newly_completed_sets:
                    for set_info in newly_completed_sets:
                        new_achievements.append(type('SetCompletion', (), {
                            'name': f"Série {set_info['set_name']} Complète!",
                            'reward_coins': 0
                        })())

                if new_achievements:
                    achievement_text = ""
                    for achievement in new_achievements:
                        achievement_text += f"🏆 {achievement.name}"
                        if achievement.reward_coins > 0:
                            achievement_text += f" (+{achievement.reward_coins} coins)"
                        achievement_text += "\n"

                    embed.add_field(name="🎉 Nouveaux Succès!",
                                    value=achievement_text,
                                    inline=False)
            else:
                # Multiple characters - check for rare pulls
                has_legendary = any(char.rarity == "Legendary" for char in rolled_characters)
                has_mythical = any(char.rarity == "Mythic" for char in rolled_characters)
                has_titan = any(char.rarity == "Titan" for char in rolled_characters)
                has_duo = any(char.rarity == "Fusion" for char in rolled_characters)
                
                # Use animation helper for multiple character rolls
                if has_duo:
                    await play_summoning_animation(interaction, "Fusion", True)
                elif has_titan:
                    await play_summoning_animation(interaction, "Titan", True)
                elif has_mythical:
                    await play_summoning_animation(interaction, "Mythic", True)
                elif has_legendary:
                    await play_summoning_animation(interaction, "Legendary", True)
                else:
                    await asyncio.sleep(0.5)

                embed = discord.Embed(
                    title=
                    f"🌌 ═══════〔 I N V O C A T I O N   M U L T I P L E 〕═══════ 🌌",
                    description=f"```\n◆ {amount} personnages invoqués ◆\n```",
                    color=BotConfig.RARITY_COLORS['Epic'])

                results_text = ""
                total_value = 0
                rarity_counts = {}

                for char in rolled_characters:
                    results_text += f"{char.get_rarity_emoji()} **{char.name}** ({char.anime}) - {format_number(char.value)} pièces\n"
                    total_value += char.value
                    rarity_counts[char.rarity] = rarity_counts.get(
                        char.rarity, 0) + 1

                embed.add_field(name="🎭 Personnages Obtenus",
                                value=results_text,
                                inline=False)
                embed.add_field(name="💎 Valeur Totale",
                                value=f"{format_number(total_value)} pièces",
                                inline=True)

                # Rarity breakdown
                rarity_text = ""
                for rarity, count in rarity_counts.items():
                    emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    rarity_text += f"{emoji} {rarity}: {count}\n"

                embed.add_field(name="📊 Répartition",
                                value=rarity_text,
                                inline=True)
                embed.add_field(
                    name="🪙 Solde",
                    value=
                    f"Coût: {format_number(cost)} {BotConfig.CURRENCY_EMOJI}\nRestant: {format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                    inline=True)

            # Add achievement notifications if any were earned
            if new_achievements:
                achievement_text = ""
                for ach in new_achievements[:3]:  # Show max 3
                    achievement_text += f"🏆 **{ach.name}** débloqué!\n"
                    if ach.reward_coins > 0:
                        achievement_text += f"   +{format_number(ach.reward_coins)} pièces bonus!\n"

                embed.add_field(name="🎊 Succès Débloqués",
                                value=achievement_text,
                                inline=False)

            embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in roll slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors de l'invocation.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors de l'invocation.")

    @bot.tree.command(name="profile",
                      description="Afficher votre profil Shadow Roll")
    @app_commands.describe(user="Utilisateur dont voir le profil (optionnel)")
    async def profile_slash(interaction: discord.Interaction,
                            user: Optional[discord.Member] = None):
        """Slash command for viewing profiles"""
        try:
            target_user = user or interaction.user
            target_user_id = target_user.id
            username = get_display_name(target_user)

            await interaction.response.defer()

            # Sync stats and get player data
            await bot.db.sync_player_stats(target_user_id)
            player = await bot.db.get_or_create_player(target_user_id,
                                                       username)
            inventory_stats = await bot.db.get_inventory_stats(target_user_id)

            # Get selected title
            selected_title = await bot.db.get_selected_title(target_user_id)
            title_display = ""
            if selected_title:
                title_display = f"{selected_title['icon']} {selected_title['display_name']}\n"
            else:
                title_display = "◆ Maître des Ténèbres ◆\n"

            embed = discord.Embed(
                title="🌌 ═══════〔 P R O F I L   D E   L ' O M B R E 〕═══════ 🌌",
                description=f"```\n{title_display}{username}\n```",
                color=BotConfig.RARITY_COLORS['Mythic'])

            embed.add_field(
                name="🪙 ═══〔 Richesse des Ombres 〕═══ 🪙",
                value=f"```\n{format_number(player.coins)} Shadow Coins\n```",
                inline=True)

            embed.add_field(
                name="🎲 ═══〔 Invocations 〕═══ 🎲",
                value=f"```\n{format_number(player.total_rerolls)} total\n```",
                inline=True)

            embed.add_field(
                name="🎒 ═══〔 Collection 〕═══ 🎒",
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

            embed.add_field(name="🌫️ ═══〔 Répartition par Rareté 〕═══ 🌫️",
                            value=f"```\n{rarity_text}```",
                            inline=False)

            embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION}",
                             icon_url=target_user.avatar.url
                             if target_user.avatar else None)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error in profile slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement du profil.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement du profil.")

    @bot.tree.command(name="daily",
                      description="Récupérer votre récompense quotidienne")
    async def daily_slash(interaction: discord.Interaction):
        """Slash command for daily rewards"""
        try:
            user_id = interaction.user.id
            username = get_display_name(interaction.user)
            player = await bot.db.get_or_create_player(user_id, username)

            # Check if already claimed today
            if player.last_daily:
                try:
                    last_daily = datetime.fromisoformat(player.last_daily)
                    now = datetime.now()

                    if last_daily.date() == now.date():
                        from datetime import timedelta
                        next_daily = last_daily.replace(
                            hour=0, minute=0, second=0,
                            microsecond=0) + timedelta(days=1)
                        time_until = next_daily - now
                        hours, remainder = divmod(
                            int(time_until.total_seconds()), 3600)
                        minutes, _ = divmod(remainder, 60)

                        await interaction.response.send_message(
                            f"❌ Bénédiction déjà récupérée aujourd'hui! Prochaine bénédiction dans {hours}h {minutes}m",
                            ephemeral=True)
                        return
                except (ValueError, TypeError):
                    pass  # Invalid date format, allow claim

            # Generate reward
            import random
            reward_amount = random.randint(BotConfig.DAILY_REWARD_MIN,
                                           BotConfig.DAILY_REWARD_MAX)
            
            # Apply series and equipment coin bonuses to daily reward
            set_bonuses = await bot.db.get_active_set_bonuses(user_id)
            coin_multiplier = set_bonuses.get('coin_boost', 1.0)
            reward_with_set_bonus = int(reward_amount * coin_multiplier)
            final_reward = await bot.db.apply_equipment_bonuses_to_coins(user_id, reward_with_set_bonus)
            
            new_coins = player.coins + final_reward
            current_time = datetime.now().isoformat()

            # Update database
            await bot.db.update_player_coins(user_id, new_coins)
            await bot.db.update_daily_reward(user_id, current_time)

            embed = discord.Embed(
                title=
                "🌌 ═══════〔 B É N É D I C T I O N   Q U O T I D I E N N E 〕═══════ 🌌",
                description=
                f"```\n◆ Les ténèbres vous accordent leur bénédiction ◆\n```",
                color=BotConfig.RARITY_COLORS['Legendary'])

            embed.add_field(
                name="🎁 Récompense Reçue",
                value=
                f"**+{format_number(final_reward)}** {BotConfig.CURRENCY_EMOJI}" +
                (f"\n(base: {reward_amount}, bonus série: +{int((coin_multiplier-1)*100)}%)" if coin_multiplier > 1.0 else ""),
                inline=True)

            embed.add_field(
                name="🪙 Nouveau Solde",
                value=f"{format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}",
                inline=True)

            embed.add_field(name="⏰ Prochaine Bénédiction",
                            value="Dans 24 heures",
                            inline=False)

            embed.set_footer(text=f"Shadow Roll • {BotConfig.VERSION}")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            logger.error(f"Error in daily slash command: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la récupération de la bénédiction quotidienne.",
                ephemeral=True)



    @bot.tree.command(
        name="index",
        description="Afficher l'index des personnages avec statut de possession et stats par série")
    async def index_slash(interaction: discord.Interaction):
        """Show enhanced character index with ownership tracking"""
        try:
            from modules.menu import IndexView
            view = IndexView(bot, interaction.user.id)
            embed = await view.create_index_embed()
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error in index slash command: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de l'affichage de l'index des personnages.", ephemeral=True)

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
            from modules.sell import SellView
            sell_view = SellView(bot, interaction.user.id)
            embed = await sell_view.create_sell_embed()
            
            await interaction.followup.send(embed=embed, view=sell_view)
            
        except Exception as e:
            logger.error(f"Error in sell command: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de l'ouverture de l'interface de vente!",
                ephemeral=True)

    @bot.tree.command(name="boutique", description="Accéder à la boutique corrigée Shadow Roll")
    async def shop_slash(interaction: discord.Interaction):
        """Fixed shop slash command"""
        try:
            await interaction.response.defer()
            
            # Check if user is banned
            if await bot.db.is_banned(interaction.user.id):
                await interaction.followup.send(
                    BotConfig.MESSAGES['banned'], ephemeral=True)
                return
            
            # Create fixed shop view
            from modules.shop_system_fixed import create_fixed_shop_view
            shop_view = await create_fixed_shop_view(bot, interaction.user.id)
            embed = await shop_view.create_shop_embed()
            
            await interaction.followup.send(embed=embed, view=shop_view)
            
        except Exception as e:
            logger.error(f"Error in fixed shop command: {e}")
            # Fallback to modern shop
            try:
                from modules.shop_new import ModernShopView
                shop_view = ModernShopView(bot, interaction.user.id)
                embed = await shop_view.create_shop_embed()
                await interaction.followup.send(embed=embed, view=shop_view)
            except:
                await interaction.followup.send(
                    "❌ Erreur lors de l'ouverture de la boutique!",
                    ephemeral=True)

    @bot.tree.command(name="patchnotes",
                      description="Afficher les notes de version de Shadow Roll")
    async def patch_notes_slash(interaction: discord.Interaction):
        """Slash command for patch notes"""
        try:
            await interaction.response.defer()
            from modules.patch_notes import PatchNotesView
            view = PatchNotesView(bot, interaction.user.id)
            embed = await view.create_patch_notes_embed()
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in patch notes slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement des notes de version.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement des notes de version.")

    @bot.tree.command(name="equipment",
                      description="Gérer votre équipement de personnages ultra-rares")
    async def equipment_slash(interaction: discord.Interaction):
        """Slash command for equipment management"""
        try:
            await interaction.response.defer()
            from modules.equipment import EquipmentView
            view = EquipmentView(bot, interaction.user.id)
            embed = await view.create_equipment_embed()
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in equipment slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement de l'équipement.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement de l'équipement.")

    @bot.tree.command(name="recherche",
                      description="Système de recherche de personnages")
    async def hunt_slash(interaction: discord.Interaction):
        """Slash command for character hunt system"""
        try:
            await interaction.response.defer()
            from modules.hunt_system import CharacterHuntView
            view = CharacterHuntView(interaction.user.id, bot.db)
            await view.update_hunt_display(interaction)
            
        except Exception as e:
            logger.error(f"Error in hunt slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement du système de recherche.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement du système de recherche.")

    @bot.tree.command(name="titres",
                      description="Gérer vos titres personnalisés et leurs bonus")
    async def titles_slash(interaction: discord.Interaction):
        """Slash command for titles management"""
        try:
            await interaction.response.defer()
            from modules.menu import TitlesView
            view = TitlesView(bot, interaction.user.id)
            embed = await view.create_titles_embed()
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in titles slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement des titres.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement des titres.")

    @bot.tree.command(name="backpack",
                      description="Accéder au backpack unifié (personnages, potions, titres, équipement, effets)")
    async def backpack_slash(interaction: discord.Interaction):
        """Slash command for unified backpack system"""
        try:
            await interaction.response.defer()
            from modules.backpack import BackpackView
            view = BackpackView(bot, interaction.user.id)
            embed = await view.create_backpack_embed()
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in backpack slash command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Erreur lors du chargement du backpack.", ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors du chargement du backpack.")

    # Sync commands to Discord (only if needed)
    # Note: Sync is disabled to avoid rate limiting on startup
    # Use !synccommands admin command to manually sync when needed
    logger.info("Slash commands registered (sync disabled to avoid rate limiting)")
