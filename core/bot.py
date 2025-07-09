"""
Main bot class for Shadow Roll Discord Bot
Handles Discord events, command setup, and core functionality
"""
import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional

from core.config import BotConfig
from core.database import DatabaseManager
from core.performance import initialize_performance_optimizer
from modules.utils import get_display_name

logger = logging.getLogger(__name__)

class ShadowRollBot(commands.Bot):
    """Main Shadow Roll Bot class with all functionality"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=BotConfig.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.db = None
        
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Initializing Shadow Roll Bot...")
        
        # Initialize database
        self.db = DatabaseManager()
        await self.db.initialize()
        logger.info("Database initialized successfully")
        
        # Initialize performance optimizer
        await initialize_performance_optimizer(self.db)
        logger.info("Performance optimizer initialized successfully")
        
        # Character images are now managed manually via !addimage command
        # No automatic overwriting of custom images
        
        # Setup admin commands
        await self.setup_admin_commands()
        
        # Setup series admin commands
        from modules.admin_series import setup_series_admin_commands
        from modules.admin_legacy_series import setup_legacy_series_commands
        await setup_series_admin_commands(self)
        await setup_legacy_series_commands(self)
        
        # Setup lookcard command specifically
        try:
            from modules.admin_legacy_commands import LookcardSelectionView
            from modules.utils import format_number, get_display_name
            
            @self.command(name='lookcard', aliases=['previewcard', 'cardpreview'])
            async def look_card(ctx, *, character_name: str):
                """Afficher la carte d'un personnage - Disponible pour tous"""
                try:
                    # Recherche du personnage - exact match first, then partial
                    cursor = await self.db.db.execute(
                        "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) = LOWER(?) ORDER BY name",
                        (character_name,)
                    )
                    char_rows = await cursor.fetchall()
                    
                    # If no exact match, try partial match
                    if not char_rows:
                        cursor = await self.db.db.execute(
                            "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) LIKE LOWER(?) ORDER BY name",
                            (f"%{character_name}%",)
                        )
                        char_rows = await cursor.fetchall()
                    
                    if not char_rows:
                        await ctx.send(f"❌ Aucun personnage trouvé pour '{character_name}'")
                        return
                    
                    if len(char_rows) > 1:
                        # Multiple characters found - use button selection
                        embed = discord.Embed(
                            title="🔍 Plusieurs personnages trouvés",
                            description="Cliquez sur le bouton correspondant au personnage que vous voulez voir:",
                            color=0x3498db
                        )
                        
                        # Add character list to embed for reference
                        char_list = "\n".join([f"**{i+1}.** {char[1]} ({char[2]}) - {char[3]}" for i, char in enumerate(char_rows[:10])])
                        embed.add_field(name="Personnages disponibles:", value=char_list, inline=False)
                        
                        view = LookcardSelectionView(char_rows, ctx.author.id, self)
                        await ctx.send(embed=embed, view=view)
                        return
                    
                    # Un seul résultat
                    row = char_rows[0]
                    from core.models import Character
                    character = Character(
                        id=row[0],
                        name=row[1], 
                        anime=row[2],
                        rarity=row[3],
                        value=row[4],
                        image_url=row[5]
                    )
                    
                    # Obtenir les informations utilisateur pour un affichage personnalisé
                    username = get_display_name(ctx.author)
                    
                    # Créer la carte avec le style Shadow amélioré
                    embed = discord.Embed(
                        title="🌌 ═══════〔 C A R T E   P E R S O N N A G E 〕═══════ 🌌",
                        description=f"```\n◆ Consultation par: {username} ◆\n```",
                        color=character.get_rarity_color()
                    )
                    
                    embed.add_field(
                        name=f"🌑 ═══〔 {character.get_rarity_emoji()} {character.name} 〕═══ 🌑",
                        value=(f"```\n"
                               f"Anime: {character.anime}\n"
                               f"Rareté: {character.rarity}\n"
                               f"Valeur: {format_number(character.value)} Shadow Coins\n"
                               f"```"),
                        inline=False
                    )
                    
                    # Ajouter les chances d'obtention
                    from core.config import BotConfig
                    rarity_chance = BotConfig.RARITY_WEIGHTS.get(character.rarity, 0)
                    embed.add_field(
                        name="📊 Informations d'Invocation",
                        value=(f"```\n"
                               f"Invocation: Disponible\n"
                               f"Fréquence: {rarity_chance}%\n"
                               f"Roll Standard: Oui\n"
                               f"```"),
                        inline=True
                    )
                    
                    if character.image_url and not character.image_url.startswith('https://i.imgur.com/example'):
                        embed.set_image(url=character.image_url)
                    
                    embed.set_footer(
                        text="Shadow Roll • Consultation de Personnage • ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ",
                        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
                    )
                    
                    await ctx.send(embed=embed)
                    
                except Exception as e:
                    logger.error(f"Error in lookcard command: {e}")
                    await ctx.send("❌ Erreur lors de l'affichage de la carte.")
            
            logger.info("Lookcard command setup completed")
        except Exception as e:
            logger.error(f"Error setting up lookcard command: {e}")
        logger.info("Admin commands setup completed")
        
        # Setup prefix commands
        await self.setup_prefix_commands()
        logger.info("Prefix commands setup completed")
        
        # Setup slash commands
        await self.setup_slash_commands()
        logger.info("Slash commands setup completed")
        
        # Setup craft system
        from modules.craft_system import setup_craft_commands
        await setup_craft_commands(self)
        logger.info("Craft system setup completed")
        
        # Setup hunt system
        try:
            from modules.hunt_system import setup_hunt_system
            self.hunt_system = await setup_hunt_system(self, self.db)
            logger.info("Hunt system setup completed")
        except Exception as e:
            logger.error(f"Error setting up hunt system: {e}")
        
        # Setup persistent character management
        from modules.admin_character_persistent import setup_persistent_admin_commands
        await setup_persistent_admin_commands(self)
        logger.info("Persistent character management setup completed")
        
        # Setup trade system
        try:
            from modules.trade import setup_trade_commands
            await setup_trade_commands(self)
            logger.info("Trade system setup completed")
        except Exception as e:
            logger.error(f"Error setting up trade system: {e}")
        
        # Setup modern shop system
        try:
            from modules.shop_new import setup_shop_database
            await setup_shop_database(self)
            logger.info("Modern shop system setup completed")
        except Exception as e:
            logger.error(f"Error setting up modern shop system: {e}")
        
        # Setup enhanced visual menu system
        try:
            from modules.enhanced_menu import setup_enhanced_menu_commands
            await setup_enhanced_menu_commands(self)
            logger.info("Enhanced visual menu system setup completed")
        except Exception as e:
            logger.error(f"Error setting up enhanced menu system: {e}")
        
        # Setup system optimizer
        try:
            from modules.system_optimizer import setup_system_optimizer
            await setup_system_optimizer(self)
            logger.info("System optimizer setup completed")
        except Exception as e:
            logger.error(f"Error setting up system optimizer: {e}")
        
        # Setup comprehensive fixes
        try:
            from modules.comprehensive_fixes import setup_comprehensive_fixes
            await setup_comprehensive_fixes(self)
            logger.info("Comprehensive fixes setup completed")
        except Exception as e:
            logger.error(f"Error setting up comprehensive fixes: {e}")

        # Setup rarity value management system
        try:
            from rarity_value_updater import setup_rarity_commands
            await setup_rarity_commands(self)
            logger.info("Rarity value management system setup completed")
        except Exception as e:
            logger.error(f"Error setting up rarity value management: {e}")
        
        # Setup game system
        try:
            from modules.games.game_manager import setup_game_manager
            await setup_game_manager(self)
            logger.info("Game system setup completed")
        except Exception as e:
            logger.error(f"Error setting up game system: {e}")
        
        logger.info("Shadow Roll Bot initialization complete")
    
    async def setup_admin_commands(self):
        """Setup new administrative system"""
        from modules.admin_new import setup_new_admin_system
        await setup_new_admin_system(self)
    
    async def setup_prefix_commands(self):
        """Setup prefix commands"""
        @self.command(name='menu')
        async def menu_command(ctx):
            """Main menu command"""
            try:
                from modules.menu import ShadowMenuView, create_main_menu_embed
                view = ShadowMenuView(self, ctx.author.id)
                embed = await create_main_menu_embed(self, ctx.author.id)
                await ctx.send(embed=embed, view=view)
            except Exception as e:
                logger.error(f"Error in menu command: {e}")
                await ctx.send("❌ Erreur lors de la création du menu Shadow Roll.")
        
        @self.command(name='help')
        async def help_command(ctx):
            """Help command"""
            try:
                from modules.menu import HelpView
                view = HelpView(self, ctx.author.id)
                embed = await view.create_help_embed()
                await ctx.send(embed=embed, view=view)
            except Exception as e:
                logger.error(f"Error in help command: {e}")
                await ctx.send("❌ Erreur lors de l'affichage de l'aide.")
    
    async def setup_slash_commands(self):
        """Setup slash commands"""
        try:
            from modules.commands import setup_slash_commands
            await setup_slash_commands(self)
            logger.info("Slash commands setup completed")
        except Exception as e:
            logger.error(f"Error setting up slash commands: {e}")
            # Continue without slash commands if there's an error
    
    async def on_ready(self):
        """Called when bot is ready"""
        username = self.user.name if self.user else "Unknown"
        user_id = self.user.id if self.user else "Unknown"
        logger.info(f"Shadow Roll Bot logged in as {username} (ID: {user_id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name="Shadow Roll | !menu"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Argument requis manquant pour cette commande.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide fourni.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Commande en cooldown. Réessayez dans {error.retry_after:.1f} secondes.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
        else:
            logger.error(f"Unexpected error in command {ctx.command}: {error}")
            await ctx.send("❌ Une erreur inattendue s'est produite.")
    
    async def on_application_command_error(self, interaction: discord.Interaction, error):
        """Handle slash command errors"""
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"⏰ Commande en cooldown. Réessayez dans {error.retry_after:.1f} secondes.",
                ephemeral=True
            )
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Vous n'avez pas les permissions nécessaires.",
                ephemeral=True
            )
        else:
            logger.error(f"Unexpected error in slash command: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur inattendue s'est produite.",
                    ephemeral=True
                )
    
    async def close(self):
        """Cleanup when bot is shutting down"""
        if self.db:
            await self.db.close()
        await super().close()