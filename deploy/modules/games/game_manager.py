"""
Gestionnaire Principal des Jeux pour Shadow Roll Bot
Coordonne tous les systèmes de jeu et leur interface Discord
"""
import discord
from discord.ext import commands
import logging
from typing import Dict, Optional

from .would_you_rather import WouldYouRatherGame
from .game_stats import GameStatsManager

logger = logging.getLogger(__name__)

class GameManager:
    """Gestionnaire principal pour tous les systèmes de jeu"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, WouldYouRatherGame] = {}  # channel_id -> game
        self.stats_manager = GameStatsManager()
        
    async def setup_commands(self):
        """Configuration des commandes de jeu"""
        
        @self.bot.command(name='game', aliases=['jeu', 'games'])
        async def game_command(ctx):
            """Ouvre le menu des jeux disponibles"""
            try:
                view = GameMenuView(self)
                embed = self.create_game_menu_embed()
                await ctx.send(embed=embed, view=view)
                
            except Exception as e:
                logger.error(f"Error in game command: {e}")
                await ctx.send("❌ Erreur lors de l'ouverture du menu de jeu.")
        
        @self.bot.command(name='mystats', aliases=['stats', 'statistiques'])
        async def stats_command(ctx):
            """Affiche les statistiques personnelles du joueur"""
            try:
                await self.stats_manager.initialize_database()
                stats = await self.stats_manager.get_player_stats(ctx.author.id)
                
                if not stats:
                    embed = discord.Embed(
                        title="📊 Vos Statistiques",
                        description="Vous n'avez pas encore joué de parties !\n"
                                   "Tapez `!game` pour commencer votre première partie.",
                        color=0x95a5a6
                    )
                else:
                    embed = discord.Embed(
                        title=f"📊 Statistiques de {stats['username']}",
                        color=0x3498db
                    )
                    
                    embed.add_field(
                        name="🏆 Total Wins",
                        value=f"**{stats['total_wins']}** votes majoritaires",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📈 Parties jouées",
                        value=f"**{stats['total_games']}** parties",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🎯 Manches totales",
                        value=f"**{stats['total_rounds']}** manches",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="💯 Ratio de réussite",
                        value=f"**{stats['win_rate']:.1f}%**",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🕒 Dernière partie",
                        value=f"{stats['last_played'][:10]}",
                        inline=True
                    )
                    
                    # Historique récent
                    recent_games = await self.stats_manager.get_session_history(ctx.author.id, 3)
                    if recent_games:
                        history_text = ""
                        for game in recent_games:
                            history_text += f"• **{game['game_type']}** - {game['correct_votes']}/{game['total_votes']} pts (#{game['final_rank']}/{game['total_participants']})\n"
                        
                        embed.add_field(
                            name="📚 Parties récentes",
                            value=history_text,
                            inline=False
                        )
                
                embed.set_footer(text="Tapez !leaderboard pour voir le classement global")
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in stats command: {e}")
                await ctx.send("❌ Erreur lors de la récupération des statistiques.")
        
        @self.bot.command(name='leaderboard', aliases=['classement', 'top'])
        async def leaderboard_command(ctx):
            """Affiche le classement global des joueurs"""
            try:
                await self.stats_manager.initialize_database()
                leaderboard = await self.stats_manager.get_leaderboard(10)
                
                if not leaderboard:
                    embed = discord.Embed(
                        title="🏆 Classement Global",
                        description="Aucune statistique disponible pour le moment.\n"
                                   "Soyez le premier à jouer avec `!game` !",
                        color=0x95a5a6
                    )
                else:
                    embed = discord.Embed(
                        title="🏆 CLASSEMENT GLOBAL",
                        description="Top 10 des meilleurs joueurs",
                        color=0xf1c40f
                    )
                    
                    ranking_text = ""
                    for i, player in enumerate(leaderboard, 1):
                        if i == 1:
                            emoji = "🥇"
                        elif i == 2:
                            emoji = "🥈"
                        elif i == 3:
                            emoji = "🥉"
                        else:
                            emoji = f"{i}."
                        
                        ranking_text += f"{emoji} **{player['username']}**\n"
                        ranking_text += f"   📊 {player['win_rate']:.1f}% • 🏆 {player['total_wins']} wins • 🎮 {player['total_games']} parties\n\n"
                    
                    embed.add_field(
                        name="📈 Classement par ratio de réussite",
                        value=ranking_text,
                        inline=False
                    )
                    
                    embed.set_footer(text="Basé sur le pourcentage de votes majoritaires • Tapez !mystats pour vos stats")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error in leaderboard command: {e}")
                await ctx.send("❌ Erreur lors de la récupération du classement.")
        
        logger.info("Game system commands setup completed")
    
    def create_game_menu_embed(self) -> discord.Embed:
        """Créer l'embed du menu principal des jeux"""
        embed = discord.Embed(
            title="🎮 MENU DES JEUX",
            description="Choisissez un jeu pour commencer à jouer !",
            color=0x7b2cbf
        )
        
        embed.add_field(
            name="🎯 Jeux Disponibles",
            value="🤔 **Tu préfères** - Choisis entre deux options avec tes amis !",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value="• **Tu préfères** - Partie rapide (5 manches, 10s de vote)\n• **Configurer Anime Girl** - Personnaliser le thème avec vos paramètres",
            inline=False
        )
        
        embed.set_footer(text="Shadow Roll Gaming")
        
        return embed
    
    async def start_would_you_rather(self, interaction: discord.Interaction):
        """Démarrer le jeu Tu préfères"""
        channel_id = interaction.channel.id
        
        # Vérifier si un jeu est déjà en cours
        if channel_id in self.active_games:
            await interaction.response.send_message(
                "❌ Un jeu est déjà en cours dans ce salon !",
                ephemeral=True
            )
            return
        
        # Créer le menu de sélection de thème
        view = ThemeSelectionView(self, interaction.user)
        embed = discord.Embed(
            title="🤔 TU PRÉFÈRES",
            description="Choisissez un thème pour commencer le jeu !",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="🎨 Thèmes Disponibles",
            value="👧 **Anime Girl** - Questions sur les personnages féminins d'anime\n⚙️ **Configurer Anime Girl** - Personnalisez les paramètres et bannissez des animes",
            inline=False
        )
        
        embed.add_field(
            name="📝 Règles",
            value="• Le jeu commence dans 15 secondes après sélection du thème\n• 5 manches avec 10 secondes pour voter par manche\n• Choisissez entre l'option de gauche ⬅️ ou de droite ➡️",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view)

class GameMenuView(discord.ui.View):
    """Vue du menu principal des jeux"""
    
    def __init__(self, game_manager: GameManager):
        super().__init__(timeout=300)
        self.game_manager = game_manager
    
    @discord.ui.button(label="🤔 Tu préfères", style=discord.ButtonStyle.primary)
    async def would_you_rather_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour lancer le jeu Tu préfères"""
        await self.game_manager.start_would_you_rather(interaction)

class ThemeSelectionView(discord.ui.View):
    """Vue de sélection du thème"""
    
    def __init__(self, game_manager: GameManager, user: discord.User):
        super().__init__(timeout=60)
        self.game_manager = game_manager
        self.user = user
    
    @discord.ui.button(label="👧 Anime Girl", style=discord.ButtonStyle.success)
    async def anime_girl_theme(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Thème Anime Girl"""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Seule la personne qui a lancé le jeu peut choisir le thème !",
                ephemeral=True
            )
            return
        
        # Créer et démarrer le jeu
        game = WouldYouRatherGame(
            game_manager=self.game_manager,
            channel=interaction.channel,
            host=interaction.user,
            theme="anime_girl"
        )
        
        self.game_manager.active_games[interaction.channel.id] = game
        await game.start_game(interaction)
    
    @discord.ui.button(label="⚙️ Configurer Anime Girl", style=discord.ButtonStyle.secondary)
    async def configure_anime_girl(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les paramètres du thème Anime Girl"""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Seule la personne qui a lancé le jeu peut configurer le thème !",
                ephemeral=True
            )
            return
        
        # Importer et afficher le modal de configuration du thème
        from .would_you_rather import ThemeConfigModal
        
        modal = ThemeConfigModal()
        await interaction.response.send_modal(modal)

async def setup_game_manager(bot):
    """Initialiser le gestionnaire de jeu"""
    game_manager = GameManager(bot)
    await game_manager.setup_commands()
    return game_manager