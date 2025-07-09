"""
Jeu "Tu préfères" pour Shadow Roll Bot
Système de vote interactif avec images et timing automatique
"""
import discord
import logging
import asyncio
from typing import Set, TYPE_CHECKING, Dict, List, Tuple
import random
from discord import ui

if TYPE_CHECKING:
    from .game_manager import GameManager

from .game_stats import GameStatsManager

class GameConfigModal(ui.Modal, title="Configuration de la partie"):
    """Modal pour configurer une partie personnalisée"""
    
    def __init__(self):
        super().__init__()
        
    rounds = ui.TextInput(
        label="Nombre de manches",
        placeholder="Entrez le nombre de manches (1-20)",
        default="5",
        min_length=1,
        max_length=2
    )
    
    voting_time = ui.TextInput(
        label="Temps de vote par manche (secondes)",
        placeholder="Entrez le temps de vote (5-60 secondes)",
        default="10",
        min_length=1,
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traiter la configuration soumise"""
        try:
            rounds_count = int(self.rounds.value)
            vote_time = int(self.voting_time.value)
            
            # Validation des valeurs
            if not (1 <= rounds_count <= 20):
                await interaction.response.send_message(
                    "❌ Le nombre de manches doit être entre 1 et 20 !",
                    ephemeral=True
                )
                return
                
            if not (5 <= vote_time <= 60):
                await interaction.response.send_message(
                    "❌ Le temps de vote doit être entre 5 et 60 secondes !",
                    ephemeral=True
                )
                return
            
            # Stockage temporaire dans l'interaction pour récupération
            interaction.client.temp_game_config = {
                'rounds': rounds_count,
                'voting_time': vote_time,
                'user': interaction.user,
                'channel': interaction.channel
            }
            
            await interaction.response.send_message(
                f"✅ **Configuration sauvegardée !**\n"
                f"🎯 **Manches:** {rounds_count}\n"
                f"⏱️ **Temps de vote:** {vote_time}s\n"
                f"🎮 **Lancez maintenant la partie avec le bouton ci-dessous !**",
                view=StartGameView(),
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer des nombres valides !",
                ephemeral=True
            )

class StartGameView(ui.View):
    """Vue pour démarrer le jeu après configuration"""
    
    def __init__(self):
        super().__init__(timeout=300)  # 5 minutes pour démarrer
        
    @ui.button(label="🎮 Lancer la partie", style=discord.ButtonStyle.success)
    async def start_configured_game(self, interaction: discord.Interaction, button: ui.Button):
        """Démarrer la partie avec la configuration personnalisée"""
        config = getattr(interaction.client, 'temp_game_config', None)
        
        if not config or config['user'] != interaction.user:
            await interaction.response.send_message(
                "❌ Configuration expirée ou non trouvée ! Reconfigurer la partie.",
                ephemeral=True
            )
            return
            
        # Nettoyer la config temporaire
        delattr(interaction.client, 'temp_game_config')
        
        # Démarrer le jeu avec la config personnalisée
        from .game_manager import GameManager
        game_manager = GameManager(interaction.client)
        
        # Créer une instance personnalisée du jeu
        game = WouldYouRatherGame(
            game_manager=game_manager,
            channel=interaction.channel,
            host=interaction.user,
            theme="anime_girl",
            custom_rounds=config['rounds'],
            custom_voting_time=config['voting_time']
        )
        
        # Stocker le jeu
        game_manager.active_games[interaction.channel.id] = game
        
        await game.start_game(interaction)
        
    @ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_game(self, interaction: discord.Interaction, button: ui.Button):
        """Annuler la création de partie"""
        # Nettoyer la config temporaire si elle existe
        if hasattr(interaction.client, 'temp_game_config'):
            delattr(interaction.client, 'temp_game_config')
            
        await interaction.response.edit_message(
            content="❌ **Création de partie annulée.**",
            view=None
        )

logger = logging.getLogger(__name__)

class GameConfigModal(ui.Modal, title="Configuration de la partie"):
    """Modal pour configurer une partie personnalisée"""
    
    def __init__(self):
        super().__init__()
        self.configured_rounds = None
        self.configured_voting_time = None
    
    rounds = ui.TextInput(
        label="Nombre de manches",
        placeholder="Entrez le nombre de manches (1-20)",
        default="5",
        min_length=1,
        max_length=2
    )
    
    voting_time = ui.TextInput(
        label="Temps de vote par manche (secondes)",
        placeholder="Entrez le temps de vote (5-60 secondes)",
        default="10",
        min_length=1,
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traiter la configuration soumise"""
        try:
            # Valider le nombre de manches
            rounds_count = int(self.rounds.value)
            if not 1 <= rounds_count <= 20:
                await interaction.response.send_message(
                    "❌ Le nombre de manches doit être entre 1 et 20.",
                    ephemeral=True
                )
                return
            
            # Valider le temps de vote
            vote_time = int(self.voting_time.value)
            if not 5 <= vote_time <= 60:
                await interaction.response.send_message(
                    "❌ Le temps de vote doit être entre 5 et 60 secondes.",
                    ephemeral=True
                )
                return
            
            # Stocker la configuration
            self.configured_rounds = rounds_count
            self.configured_voting_time = vote_time
            
            # Créer la vue pour démarrer le jeu
            view = StartGameView()
            view.configured_rounds = self.configured_rounds
            view.configured_voting_time = self.configured_voting_time
            view.user = interaction.user
            
            embed = discord.Embed(
                title="🎮 Configuration de la partie",
                description=(
                    f"✅ **Configuration validée !**\n\n"
                    f"🎯 **Manches:** {self.configured_rounds}\n"
                    f"⏱️ **Temps de vote:** {self.configured_voting_time}s par manche\n\n"
                    f"Voulez-vous démarrer la partie avec ces paramètres ?"
                ),
                color=0x27ae60
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer des valeurs numériques valides.",
                ephemeral=True
            )

class StartGameView(ui.View):
    """Vue pour démarrer le jeu après configuration"""
    
    def __init__(self):
        super().__init__(timeout=300)
        self.configured_rounds = None
        self.configured_voting_time = None
        self.user = None
    
    @ui.button(label="🚀 Démarrer la partie", style=discord.ButtonStyle.green)
    async def start_configured_game(self, interaction: discord.Interaction, button: ui.Button):
        """Démarrer la partie avec la configuration personnalisée"""
        # Vérifier que c'est le bon utilisateur
        if interaction.user != self.user:
            await interaction.response.send_message(
                "❌ Seul celui qui a configuré la partie peut la démarrer.",
                ephemeral=True
            )
            return
        
        # Récupérer le game manager depuis le bot
        game_manager = getattr(interaction.client, 'game_manager', None)
        if game_manager is None:
            from .game_manager import GameManager
            game_manager = GameManager(interaction.client)
        
        # Créer le jeu avec la configuration personnalisée
        game = WouldYouRatherGame(
            interaction.channel, 
            interaction.user.id, 
            game_manager,
            max_rounds=self.configured_rounds,
            voting_time=self.configured_voting_time,
            theme="anime_girl"
        )
        
        # Ajouter le jeu à la liste des jeux actifs
        game_manager.active_games[interaction.channel.id] = game
        
        # Démarrer le jeu
        await game.start_game(interaction)
        
        # Désactiver les boutons
        self.clear_items()
        
    @ui.button(label="❌ Annuler", style=discord.ButtonStyle.red)
    async def cancel_game(self, interaction: discord.Interaction, button: ui.Button):
        """Annuler la création de partie"""
        if interaction.user != self.user:
            await interaction.response.send_message(
                "❌ Seul celui qui a configuré la partie peut l'annuler.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="❌ Partie annulée",
            description="La configuration de la partie a été annulée.",
            color=0xe74c3c
        )
        
        # Désactiver les boutons
        self.clear_items()
        
        await interaction.response.edit_message(embed=embed, view=self)


class ThemeConfigModal(ui.Modal, title="Configuration du thème Anime Girl"):
    """Modal pour configurer les paramètres du thème anime girl"""
    
    def __init__(self):
        super().__init__()
        
    rounds = ui.TextInput(
        label="Nombre de manches",
        placeholder="Entrez le nombre de manches (1-20)",
        default="5",
        min_length=1,
        max_length=2
    )
    
    voting_time = ui.TextInput(
        label="Temps de vote par manche (secondes)",
        placeholder="Entrez le temps de vote (5-60 secondes)",
        default="10",
        min_length=1,
        max_length=2
    )
    
    banned_animes = ui.TextInput(
        label="Animes à bannir (optionnel)",
        placeholder="Ex: Naruto, One Piece, Dragon Ball (séparés par des virgules)",
        default="",
        min_length=0,
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traiter la configuration du thème soumise"""
        try:
            # Valider le nombre de manches
            rounds_count = int(self.rounds.value)
            if not 1 <= rounds_count <= 20:
                await interaction.response.send_message(
                    "❌ Le nombre de manches doit être entre 1 et 20.",
                    ephemeral=True
                )
                return
            
            # Valider le temps de vote
            vote_time = int(self.voting_time.value)
            if not 5 <= vote_time <= 60:
                await interaction.response.send_message(
                    "❌ Le temps de vote doit être entre 5 et 60 secondes.",
                    ephemeral=True
                )
                return
            
            # Traiter les animes bannis
            banned_list = []
            if self.banned_animes.value.strip():
                banned_list = [anime.strip() for anime in self.banned_animes.value.split(',') if anime.strip()]
            
            # Créer la vue pour démarrer le jeu avec configuration du thème
            view = ThemeStartGameView()
            view.configured_rounds = rounds_count
            view.configured_voting_time = vote_time
            view.banned_animes = banned_list
            view.user = interaction.user
            
            embed = discord.Embed(
                title="🎮 Configuration du thème Anime Girl",
                description=(
                    f"✅ **Configuration validée !**\n\n"
                    f"🎯 **Manches:** {rounds_count}\n"
                    f"⏱️ **Temps de vote:** {vote_time}s par manche\n"
                    f"🚫 **Animes bannis:** {', '.join(banned_list) if banned_list else 'Aucun'}\n\n"
                    f"Voulez-vous démarrer la partie avec ces paramètres ?"
                ),
                color=0x9b59b6
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                "❌ Veuillez entrer des valeurs numériques valides.",
                ephemeral=True
            )


class ThemeStartGameView(ui.View):
    """Vue pour démarrer le jeu après configuration du thème"""
    
    def __init__(self):
        super().__init__(timeout=300)
        self.configured_rounds = None
        self.configured_voting_time = None
        self.banned_animes = []
        self.user = None
    
    @ui.button(label="🚀 Démarrer avec ces paramètres", style=discord.ButtonStyle.green)
    async def start_themed_game(self, interaction: discord.Interaction, button: ui.Button):
        """Démarrer la partie avec la configuration du thème"""
        # Vérifier que c'est le bon utilisateur
        if interaction.user != self.user:
            await interaction.response.send_message(
                "❌ Seul celui qui a configuré la partie peut la démarrer.",
                ephemeral=True
            )
            return
        
        # Récupérer le game manager depuis le bot
        game_manager = getattr(interaction.client, 'game_manager', None)
        if game_manager is None:
            from .game_manager import GameManager
            game_manager = GameManager(interaction.client)
        
        # Créer le jeu avec la configuration personnalisée du thème
        game = WouldYouRatherGame(
            interaction.channel, 
            interaction.user.id, 
            game_manager,
            max_rounds=self.configured_rounds,
            voting_time=self.configured_voting_time,
            theme="anime_girl",
            banned_animes=self.banned_animes
        )
        
        # Ajouter le jeu à la liste des jeux actifs
        game_manager.active_games[interaction.channel.id] = game
        
        # Démarrer le jeu
        await game.start_game(interaction)
        
        # Désactiver les boutons
        self.clear_items()
        
    @ui.button(label="❌ Annuler", style=discord.ButtonStyle.red)
    async def cancel_themed_game(self, interaction: discord.Interaction, button: ui.Button):
        """Annuler la création de partie"""
        if interaction.user != self.user:
            await interaction.response.send_message(
                "❌ Seul celui qui a configuré la partie peut l'annuler.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="❌ Partie annulée",
            description="La configuration de la partie a été annulée.",
            color=0xe74c3c
        )
        
        # Désactiver les boutons
        self.clear_items()
        
        await interaction.response.edit_message(embed=embed, view=self)

class WouldYouRatherGame:
    """Jeu Tu préfères avec système de votes et scoring"""
    
    # Base de données des questions par thème avec métadonnées
    THEMES = {
        "anime_girl": {
            "name": "👧 Anime Girl",
            "questions": [
                # ========================================
                # PERSONNAGES FÉMININS - SYNCHRONISATION FINALE
                # Images récupérées depuis la base de données Shadow Roll
                # 23 matchups de haute qualité
                # 22 animes représentés
                # ========================================
                # Question 1: Oshi no Ko vs Blue Lock
                ("Ai Hoshino", "Anri Teieri", "https://cdn.discordapp.com/attachments/1391191728261824552/1391207429835985008/Carte_-_Shadow_Roll7.png?ex=686b0e62&is=6869bce2&hm=4acca556fc88e3a5040e785bac82ac75ea423d890e810266ed4ffbf31516febb&", "https://media.discordapp.net/attachments/1389028777195212922/1389068911324037261/Carte_-_Shadow_Roll20.png?ex=6867e3fc&is=6866927c&hm=2b636ca95fb7908458f3690f342fab20283546a34d7070cd5a42a36265779eea&=&format=webp&quality=lossless&width=910&height=512"),
                # Question 2: My Deer Friend Nekotan vs Death Note
                ("Torako Koshi", "Misa Amane", "https://cdn.discordapp.com/attachments/1391191728261824552/1391204482163150868/Carte_-_Shadow_Roll5.png?ex=686b0ba3&is=6869ba23&hm=0e2e4f09b536186cbc5ab3d9def8242d2aa19a476d74a9370bf6dff4713f2480&", "https://cdn.discordapp.com/attachments/1390081153226113124/1390413761910800604/Carte_-_Shadow_Roll_43.png?ex=6868d3f9&is=68678279&hm=a464006119c585dad5a9328195a4e9b9715235d182192ab6a95eb2472696bc51&"),
                # Question 3: Chainsaw Man vs Fairy Tail
                ("Makima", "Erza Scarlet", "https://cdn.discordapp.com/attachments/1390074934142828574/1390417188556374057/Carte_-_Shadow_Roll_36.gif?ex=6868d72a&is=686785aa&hm=4807807c19c727aea13bb38493a748978ae54367a482f3f57054df4ace9f361f&", "https://cdn.discordapp.com/attachments/1390082622134292551/1390409355928666172/Carte_-_Shadow_Roll_38.png?ex=6868cfdf&is=68677e5f&hm=29e1e9a58043e46aedc7228b5877b550f1307a0c288e84056cf53003a243e0fb&"),
                # Question 4: My Deer Friend Nekotan vs Re Zero
                ("Anko Koshi", "Emilia", "https://cdn.discordapp.com/attachments/1391191728261824552/1391204797037936661/Carte_-_Shadow_Roll6.png?ex=686b0bee&is=6869ba6e&hm=39c2ea2bb514401d9d2fa130a86c159edd480489052182b28609f353620c7300&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391570243863838871/Carte_-_Shadow_Roll9.png?ex=686d0908&is=686bb788&hm=f83db4d274e717d5625960617f58e3609c81cf605286096be031bb16d4a0799d&"),
                # Question 5: JoJo's Bizarre Adventure vs My Deer Friend Nekotan
                ("Jolyne Cujoh", "Noko Shikanoko", "https://media.discordapp.net/attachments/1389008376385634425/1389018314054832138/Carte_-_Shadow_Roll_3.png?ex=6863179c&is=6861c61c&hm=55ae8e942a760d9289bb9a66f47955a167c1987a67a7b7aafdf251a7eae73cc4&=&format=webp&quality=lossless&width=1635&height=920", "https://cdn.discordapp.com/attachments/1391191728261824552/1391204199294959780/Carte_-_Shadow_Roll4.png?ex=686b0b60&is=6869b9e0&hm=d999007ba54088f26a8132c495de87d7cb04f6c9af596f23b9d22339215117b6&"),
                # Question 6: Black Clover vs Demon Slayer
                ("Noelle Silva", "Shinobu Kocho", "https://cdn.discordapp.com/attachments/1390074451290493099/1390422774471725166/Carte_-_Shadow_Roll_50.png?ex=6868dc5e&is=68678ade&hm=1c7694db4423e130e18c6f0c400a2c2144f9371f869283d2d4b5cae0561e0f15&", "https://cdn.discordapp.com/attachments/1389031039879610408/1391137505901809824/Carte_-_Shadow_Roll_72.png?ex=686acd43&is=68697bc3&hm=520584e8257d991ed5f26f9fd809770ab2c98603a8dd1b1f722aadd541c29427&"),
                # Question 7: Sword Art Online vs Demon Slayer
                ("Sinon", "Mitsuri Kanroji", "https://cdn.discordapp.com/attachments/1389030937710563358/1389073763798224958/Carte_-_Shadow_Roll25.png?ex=68669701&is=68654581&hm=f6264fb0ebccdfc293913bd45d453455b737310c5271687aba00edeb62d56974&", "https://cdn.discordapp.com/attachments/1389031039879610408/1391135731547635856/Carte_-_Shadow_Roll_70.png?ex=686acb9c&is=68697a1c&hm=7e1f8fe35736b17e5671a0e717b2c5f8a1571b2b969491df94af1fe7e35286af&"),
                # Question 8: Chainsaw Man vs Sword Art Online
                ("Power", "Asuna", "https://cdn.discordapp.com/attachments/1390074934142828574/1390416599466508390/Carte_-_Shadow_Roll_45.png?ex=6868d69e&is=6867851e&hm=50ffcd134719790f261b8d89dae067ee4faeef670c30db3b150b2867b1491432&", "Asuna"),
                # Question 9: Naruto vs Demon Slayer
                ("Sakura Haruno", "Nezuko Kamado", "https://cdn.discordapp.com/attachments/1389031204539465846/1390805413921820732/Carte_-_Shadow_Roll6.png?ex=686a40ba&is=6868ef3a&hm=899804f1e77aee58b2d35d998c14bd62730328780bb6a780452d5196a3adc589&", "https://cdn.discordapp.com/attachments/1389031039879610408/1391137359973711872/Carte_-_Shadow_Roll_71.png?ex=686acd20&is=68697ba0&hm=9e6c95394384c1dbb04d779ddb8d3a5b63bdac78de3a0983654afef26c0b9ed5&"),
                # Question 10: Oshi no Ko vs One Punch Man
                ("Ruby Hoshino", "Fubuki", "https://cdn.discordapp.com/attachments/1391191728261824552/1391208352138133704/Carte_-_Shadow_Roll14.gif?ex=686b0f3e&is=6869bdbe&hm=3b6c59cfba47288c952209de95742c1744408086ab08cdf6ce2dee00dd3e5ab4&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391193994205335605/Carte_-_Shadow_Roll2.png?ex=686b01df&is=6869b05f&hm=dc174c1c4fe1440f839ea6943a2b8cc56ed9f6a1ae5680b8914bdbb58c90be32&"),
                # Question 11: The Eminence in Shadow vs Call Of The Night
                ("Alexia Midgar", "Midori Kohakobe", "https://cdn.discordapp.com/attachments/1389124349189161071/1391132961591791667/Carte_-_Shadow_Roll_66.png?ex=686ac908&is=68697788&hm=e3eb2415c5293ac8380de26e055b09cdc3ff52a8ce989f246e7b120d3e195e2b&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391574918692339842/Carte_-_Shadow_Roll15.png?ex=686d0d62&is=686bbbe2&hm=0dbb461d616bd71f7c1230cb57438b95ea09dc753328c89c04090e02b97fe6d1&"),
                # Question 12: The Eminence in Shadow vs Spy x Family
                ("Iris Midgar", "Anya Forger", "https://cdn.discordapp.com/attachments/1389124349189161071/1391126498856927272/Carte_-_Shadow_Roll_61.png?ex=686ac303&is=68697183&hm=d09abe1034463f0492e2019722851b659c14027135361974d6ab6c0f4a8aa882&", "https://media.discordapp.net/attachments/1390074865280876615/1390298557789114378/Carte_-_Shadow_Roll_30.png?ex=6867bfee&is=68666e6e&hm=3993a5c8e35c23ca8bc9d0731d6e29e158dde1927a899ba907d4918f0fec6a38&=&format=webp&quality=lossless&width=910&height=512"),
                # Question 13: Naruto vs Zenless Zone Zero
                ("Hinata Hyuga", "Ellen Joe", "https://cdn.discordapp.com/attachments/1389031204539465846/1390758741921497249/image.png?ex=686a1543&is=6868c3c3&hm=a0855131f81b5d72b7716399aba47b4a42185c13c1474a635c80262703111085&", "https://cdn.discordapp.com/attachments/1389125558893412513/1390403280600830185/Carte_-_Shadow_Roll.gif?ex=68682176&is=6866cff6&hm=5f89e09e1559973942e8c32c56f9f625512486d101693cb41dd7c85921527532&"),
                # Question 14: Re Zero vs Oshi no Ko
                ("Rem", "Akane Kurokawa", "https://cdn.discordapp.com/attachments/1391191728261824552/1391569162589044859/Carte_-_Shadow_Roll19.gif?ex=686d0806&is=686bb686&hm=900c4690f8d522519d6d6e2f12c84b3e33b130c17c4e3a99b8fb0f6d42d7acee&", "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbXd1YW41MWNzY3R0MjZrZHV5MWdnN3FqbTdqeXhyeGRwM2Y3dmN0NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/sHCifHTVkCqLmuMsww/giphy.gif"),
                # Question 15: One Piece vs Konosuba
                ("Boa Hancock", "Megumin", "https://cdn.discordapp.com/attachments/1390081108347191336/1391526713124454520/Carte_-_Shadow_Roll.png?ex=686c37bd&is=686ae63d&hm=dfb4cc30a521f6ab0ad7d287032634cc42a988df6620a27cb88c7d30108927e0&", "https://media.discordapp.net/attachments/1390072193463091200/1390297023806177301/Carte_-_Shadow_Roll_26.png?ex=6867be80&is=68666d00&hm=beb04c1b885daa5a60a1df0de484e1b19ae83f972d46724c03d31034dc51a92a&=&format=webp&quality=lossless&width=910&height=512"),
                # Question 16: My Hero Academia vs Re Zero
                ("Momo Yaoyorozu", "Ram", "https://cdn.discordapp.com/attachments/1389124669029875782/1390084533495398520/Carte_-_Shadow_Roll_24.png?ex=6866f89b&is=6865a71b&hm=7fe34120343ff96254795b595b7c476de98023cd0792be8a94366ebe8a3fc59e&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391569269220839514/Carte_-_Shadow_Roll20.gif?ex=686d081f&is=686bb69f&hm=3f7b4f493538d576dbff84ec50bcdb345a133990c08ce9c442352b7c3f550ba9&"),
                # Question 17: Call Of The Night vs Naruto
                ("Seri Kikyo", "Tsunade", "https://cdn.discordapp.com/attachments/1391191728261824552/1391574574302232607/Carte_-_Shadow_Roll14.png?ex=686d0d10&is=686bbb90&hm=a2877d4a4712d0550c6729526c94e569bbfc6008ffaafaa20c5ad3e921f5a498&", "https://cdn.discordapp.com/attachments/1389031204539465846/1390806629666001036/Carte_-_Shadow_Roll9.png?ex=686a41dc&is=6868f05c&hm=7b1f73416591fcf051c1659bc576c13978d340658011b2502e340bc5f46b3696&"),
                # Question 18: Call Of The Night vs One Piece
                ("Nazuna Nanakusa", "Nami", "https://cdn.discordapp.com/attachments/1391191728261824552/1391205728601116742/Carte_-_Shadow_Roll12.gif?ex=686b0ccd&is=6869bb4d&hm=88e2396b0bb7ef0b8f01d5072132c1457f3aea5c381417550398a97898a981af&", "https://cdn.discordapp.com/attachments/1390081108347191336/1391146834407194624/Carte_-_Shadow_Roll_86.png?ex=686ad5f3&is=68698473&hm=c35e5bdff40bc8b537e21acee59faa1c3d1a2ab70443bdd503a877011a64b864&"),
                # Question 19: My Hero Academia vs Fairy Tail
                ("Tsuyu Asui", "Lucy Heartfilia", "https://cdn.discordapp.com/attachments/1389124669029875782/1390084613417865338/Carte_-_Shadow_Roll_25.png?ex=6866f8ae&is=6865a72e&hm=db7182258c9f84a8b2c8e92ba794501a2eaeec863f332c6105db516eb3c1e1f2&", "https://cdn.discordapp.com/attachments/1390082622134292551/1390409540767453284/Carte_-_Shadow_Roll_40.png?ex=6868d00b&is=68677e8b&hm=e185b34ee2ab4c48526ce22c31387b53462b46f77700c6cf60062e8ee158cbf9&"),
                # Question 20: My Hero Academia vs Jujutsu Kaisen
                ("Ochaco Uraraka", "Kasumi Miwa", "https://cdn.discordapp.com/attachments/1389124669029875782/1389151313408954439/Carte_-_Shadow_Roll_8.png?ex=6866367a&is=6864e4fa&hm=099b6299db0362b74cec390f12810a4c686d250ddd4bf09621c2dfbc75c014e1&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391194913470943322/Carte_-_Shadow_Roll3.png?ex=686b02ba&is=6869b13a&hm=a5d9ce0ebb549ad9ccf057a6696772a9aaba671be637bc2ee3cbb97d73491e68&"),
                # Question 21: Jujutsu Kaisen vs Attack on Titan
                ("Nobara Kugisaki", "Historia Reiss", "https://cdn.discordapp.com/attachments/1390071426467500174/1390401699876700190/Carte_-_Shadow_Roll_36.png?ex=6868c8bd&is=6867773d&hm=b21a01f36516249629cf9c301f6fd3dbfcb591953a4e461c16a6e079c351b29f&", "https://cdn.discordapp.com/attachments/1389030758609584350/1389040743510704288/Carte_-_Shadow_Roll7.png?ex=68667840&is=686526c0&hm=105e409657055978515860dde7b65cdb10c8ee8b39a797490d668571b4800ce4&"),
                # Question 22: Attack on Titan vs One Punch Man
                ("Mikasa Ackerman", "Tatsumaki", "https://cdn.discordapp.com/attachments/1389030758609584350/1389035072937791528/Carte_-_Shadow_Roll2.png?ex=686672f8&is=68652178&hm=a5590e63d6c3a7d8ef9dd2649eed0c2798b14ad4015cc14fa4148739dd5ac293&", "https://cdn.discordapp.com/attachments/1391191728261824552/1391193591371792504/Carte_-_Shadow_Roll3.gif?ex=686b017f&is=6869afff&hm=8ad3fa91bd93af7e7ef820c97d72c3ae371af38d46eb6901a1bfa405f228d821&"),
                # Question 23: Attack on Titan vs Spy x Family
                ("Sasha Blouse", "Yor Forger", "https://cdn.discordapp.com/attachments/1389030758609584350/1389041311423795260/Carte_-_Shadow_Roll8.png?ex=686678c7&is=68652747&hm=08ca53f68faabdb5fa8cf8bdb0658cb02ddf55815a81f63603f8bd359e39d61e&", "https://media.discordapp.net/attachments/1390074865280876615/1390298568501235792/Carte_-_Shadow_Roll_31.png?ex=6867bff1&is=68666e71&hm=87101bee7469b1aa73186d0b3793fb73cdafcd9c2e4907e001463cde540f9c06&=&format=webp&quality=lossless&width=910&height=512"),
            ]
        }
    }
    
    def __init__(self, game_manager: 'GameManager', channel: discord.TextChannel, host: discord.User, theme: str, custom_rounds=None, custom_voting_time=None, banned_animes=None):
        self.game_manager = game_manager
        self.channel = channel
        self.host = host
        self.theme = theme
        self.current_question = None
        self.votes_left: Set[int] = set()
        self.votes_right: Set[int] = set()
        self.is_active = False
        self.round_number = 1
        self.max_rounds = custom_rounds if custom_rounds else 5
        self.voting_time = custom_voting_time if custom_voting_time else 10
        self.banned_animes = banned_animes if banned_animes else []
        self.filtered_questions = self._filter_questions()
        self.is_game_stopped = False  # Flag pour arrêt complet du jeu
        
        # Initialize stats manager and related attributes
        self.stats_manager = GameStatsManager()
        self.session_id = None
        self.player_scores = {}  # user_id -> {"username": str, "correct_votes": int, "total_votes": int}
        self.round_results = []  # Liste des résultats de chaque manche
        self.votes = {}  # user_id -> "A" or "B"
        self.current_matchup = None
        self.cleanup_callback = None
        self.main_message = None  # Message principal qui sera mis à jour
        
    def _filter_questions(self):
        """Filtrer les questions selon les animes bannis"""
        if not self.banned_animes:
            return self.THEMES[self.theme]['questions']
        
        # Normaliser les noms d'animes bannis (minuscules, pas d'espaces)
        banned_normalized = [anime.lower().strip() for anime in self.banned_animes]
        
        filtered = []
        for question in self.THEMES[self.theme]['questions']:
            # Pour chaque question, vérifier si un des animes est banni
            if len(question) >= 6:  # Questions avec métadonnées d'anime
                anime1 = question[4].lower().strip()
                anime2 = question[5].lower().strip()
                
                # Vérifier si aucun des animes n'est banni
                if not any(banned in anime1 or anime1 in banned for banned in banned_normalized) and \
                   not any(banned in anime2 or anime2 in banned for banned in banned_normalized):
                    filtered.append(question)
            else:
                # Questions sans métadonnées - les garder par défaut
                filtered.append(question)
        
        return filtered if filtered else self.THEMES[self.theme]['questions']  # Fallback si tout est banni
        
    async def start_game(self, interaction: discord.Interaction):
        """Démarrer le jeu avec initialisation des statistiques"""
        # Initialiser la base de données des statistiques
        await self.stats_manager.initialize_database()
        
        # Créer une session de jeu
        self.session_id = await self.stats_manager.start_game_session(
            channel_id=self.channel.id,
            game_type="Tu préfères",
            theme=self.theme,
            max_rounds=self.max_rounds,
            voting_time=self.voting_time
        )
        
        # Obtenir l'hôte du jeu
        self.host = interaction.user
        
        # Filtrer les questions selon les animes bannis
        self.filtered_questions = self._filter_questions()
        
        banned_info = f"\n🚫 **Animes bannis:** {', '.join(self.banned_animes)}" if self.banned_animes else ""
        available_questions = f"\n📊 **Questions disponibles:** {len(self.filtered_questions)}"
        
        # Set game as active
        self.is_active = True
        
        # Créer le message principal
        embed = discord.Embed(
            title="🎮 JEU TU PRÉFÈRES",
            description=(
                f"**Lancé par:** {self.host.mention}\n"
                f"**Thème:** {self.THEMES[self.theme]['name']}\n"
                f"**Manches:** {self.max_rounds}\n"
                f"**Temps de vote:** {self.voting_time}s par manche{banned_info}{available_questions}"
            ),
            color=0x3498db
        )
        
        embed.add_field(
            name="⏳ Statut",
            value="⏰ **Le jeu commence dans 15 secondes...**",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        self.main_message = await interaction.original_response()
        # print(f"DEBUG: Message principal créé avec ID: {self.main_message.id if self.main_message else 'None'}")
        
        # Attendre 15 secondes avec vérification d'arrêt
        for _ in range(15):
            if self.is_game_stopped:
                return
            await asyncio.sleep(1)
        
        # Démarrer la première manche
        await self.start_round()
    
    async def start_round(self):
        """Démarrer une nouvelle manche"""
        # Vérifier si le jeu a été arrêté
        if self.is_game_stopped:
            return
            
        if self.round_number > self.max_rounds:
            await self.end_game()
            return
        
        # Sélectionner une question aléatoire parmi les questions filtrées
        if not self.filtered_questions:
            # Mettre à jour le message principal avec l'erreur
            error_embed = discord.Embed(
                title="⚠️ ERREUR - AUCUNE QUESTION DISPONIBLE",
                description="**Aucune question disponible avec les animes bannis !**",
                color=0xe74c3c
            )
            if self.main_message:
                await self.main_message.edit(embed=error_embed, view=None)
            await self.end_game()
            return
            
        self.current_question = random.choice(self.filtered_questions)
        
        # Réinitialiser les votes
        if not hasattr(self, 'votes_left'):
            self.votes_left = set()
        if not hasattr(self, 'votes_right'):
            self.votes_right = set()
        
        self.votes_left.clear()
        self.votes_right.clear()
        self.votes.clear()
        self.is_active = True
        
        # Créer l'embed de la question avec images
        embed = discord.Embed(
            title=f"🤔 TU PRÉFÈRES - MANCHE {self.round_number}/{self.max_rounds}",
            description=f"**Thème:** {self.THEMES[self.theme]['name']}\n\n**Tu préfères quel personnage ?**",
            color=0xf39c12
        )
        
        # Ajouter les options avec images si disponibles
        if len(self.current_question) >= 4:  # Avec images
            # Récupérer les noms des animes si disponibles
            anime_a = self.current_question[4] if len(self.current_question) > 4 else ""
            anime_b = self.current_question[5] if len(self.current_question) > 5 else ""
            
            # Afficher l'option A avec l'anime directement dans le nom
            if anime_a:
                option_a_text = f"*{anime_a}*\n**{self.current_question[0]}**"
            else:
                option_a_text = f"**{self.current_question[0]}**"
                
            embed.add_field(
                name="⬅️ OPTION A",
                value=option_a_text,
                inline=True
            )
            
            # Afficher l'option B avec l'anime directement dans le nom
            if anime_b:
                option_b_text = f"*{anime_b}*\n**{self.current_question[1]}**"
            else:
                option_b_text = f"**{self.current_question[1]}**"
            
            embed.add_field(
                name="➡️ OPTION B", 
                value=option_b_text,
                inline=True
            )
            
            embed.add_field(
                name="⏰ Temps de vote",
                value=f"**{self.voting_time} secondes pour voter !**",
                inline=False
            )
            
            # Ajouter l'image principale (option A)
            embed.set_image(url=self.current_question[2])
            
            # Ajouter l'image de l'option B en thumbnail
            embed.set_thumbnail(url=self.current_question[3])
        else:  # Sans images (fallback)
            # Récupérer les noms des animes si disponibles
            anime_a = self.current_question[4] if len(self.current_question) > 4 else ""
            anime_b = self.current_question[5] if len(self.current_question) > 5 else ""
            
            # Afficher l'option A avec l'anime directement dans le nom
            if anime_a:
                option_a_text = f"*{anime_a}*\n**{self.current_question[0]}**"
            else:
                option_a_text = f"**{self.current_question[0]}**"
            
            embed.add_field(
                name="⬅️ OPTION A",
                value=option_a_text,
                inline=True
            )
            
            # Afficher l'option B avec l'anime directement dans le nom
            if anime_b:
                option_b_text = f"*{anime_b}*\n**{self.current_question[1]}**"
            else:
                option_b_text = f"**{self.current_question[1]}**"
            
            embed.add_field(
                name="➡️ OPTION B", 
                value=option_b_text,
                inline=True
            )
            
            embed.add_field(
                name="⏰ Temps de vote",
                value=f"**{self.voting_time} secondes pour voter !**",
                inline=False
            )
        
        # Vue avec boutons de vote et bouton d'arrêt
        view = VotingView(self)
        
        # Éditer le message principal au lieu d'en créer un nouveau
        # print(f"DEBUG: Tentative d'édition du message principal (ID: {self.main_message.id if self.main_message else 'None'})")
        if self.main_message:
            try:
                await self.main_message.edit(embed=embed, view=view)
                # print(f"DEBUG: Message principal édité avec succès pour la manche {self.round_number}")
            except discord.NotFound:
                print("DEBUG: Message principal supprimé")
                return
            except Exception as e:
                print(f"Erreur lors de l'édition du message de round: {e}")
                return
        else:
            print("ERREUR: Message principal non trouvé lors du round")
            return
        
        # Attendre le temps de vote configuré avec vérification d'arrêt
        try:
            for _ in range(self.voting_time):
                if self.is_game_stopped:  # Le jeu a été arrêté
                    return
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            return
        
        # Vérifier à nouveau si le jeu n'a pas été arrêté
        if self.is_game_stopped:
            return
            
        # Arrêter les votes pour cette manche et afficher les résultats
        view.stop()
        
        await self.show_results()
    
    async def show_results(self):
        """Afficher les résultats de la manche avec système de score"""
        total_votes = len(self.votes_left) + len(self.votes_right)
        
        if total_votes == 0:
            # Créer embed pour aucun vote
            embed = discord.Embed(
                title=f"😴 MANCHE {self.round_number}/{self.max_rounds} - AUCUN VOTE",
                description="**Aucun vote reçu pour cette manche !**",
                color=0x95a5a6
            )
            
            embed.add_field(
                name="⏳ Prochaine manche",
                value="**Prochaine manche dans 3 secondes...**" if self.round_number < self.max_rounds else "**Fin du jeu...**",
                inline=False
            )
            
            # Mettre à jour le message principal
            if self.main_message:
                await self.main_message.edit(embed=embed, view=None)
        else:
            left_percentage = (len(self.votes_left) / total_votes) * 100
            right_percentage = (len(self.votes_right) / total_votes) * 100
            
            # Déterminer l'option majoritaire
            if len(self.votes_left) > len(self.votes_right):
                majority_option = "A"
                winner_text = f"⬅️ **{self.current_question[0]}** remporte cette manche !"
                majority_voters = self.votes_left
            elif len(self.votes_right) > len(self.votes_left):
                majority_option = "B"
                winner_text = f"➡️ **{self.current_question[1]}** remporte cette manche !"
                majority_voters = self.votes_right
            else:
                majority_option = "TIE"
                winner_text = "🤝 **Égalité parfaite !**"
                majority_voters = self.votes_left.union(self.votes_right)  # Tous gagnent en cas d'égalité
            
            # Calculer les scores pour cette manche
            players_who_scored = []
            for user_id in majority_voters:
                if user_id in self.votes:
                    user = self.channel.guild.get_member(user_id)
                    if user:
                        username = user.display_name
                        # Initialiser le score du joueur s'il n'existe pas
                        if user_id not in self.player_scores:
                            self.player_scores[user_id] = {
                                "username": username,
                                "correct_votes": 0,
                                "total_votes": 0
                            }
                        
                        # Attribuer le point si le joueur a voté majoritaire
                        self.player_scores[user_id]["correct_votes"] += 1
                        players_who_scored.append(username)
            
            # Compter les votes totaux pour tous les joueurs
            for user_id in self.votes:
                if user_id not in self.player_scores:
                    user = self.channel.guild.get_member(user_id)
                    if user:
                        self.player_scores[user_id] = {
                            "username": user.display_name,
                            "correct_votes": 0,
                            "total_votes": 0
                        }
                
                if user_id in self.player_scores:
                    self.player_scores[user_id]["total_votes"] += 1
            
            # Enregistrer les résultats de la manche dans les statistiques
            await self.stats_manager.record_round_result(
                self.session_id, self.round_number,
                self.current_question[0], self.current_question[1],
                len(self.votes_left), len(self.votes_right)
            )
            
            # Enregistrer chaque vote individuel
            for user_id, option in self.votes.items():
                user = self.channel.guild.get_member(user_id)
                username = user.display_name if user else f"User_{user_id}"
                
                was_majority = (option == "A" and majority_option == "A") or \
                              (option == "B" and majority_option == "B") or \
                              (majority_option == "TIE")
                
                await self.stats_manager.record_player_vote(
                    self.session_id, self.round_number,
                    user_id, username, option, was_majority
                )
            
            # Créer l'embed des résultats
            embed = discord.Embed(
                title=f"📊 RÉSULTATS - MANCHE {self.round_number}",
                color=0x3498db
            )
            
            embed.add_field(
                name="⬅️ OPTION A",
                value=f"**{self.current_question[0]}**\n"
                      f"🗳️ {len(self.votes_left)} votes ({left_percentage:.1f}%)",
                inline=True
            )
            
            embed.add_field(
                name="➡️ OPTION B",
                value=f"**{self.current_question[1]}**\n"
                      f"🗳️ {len(self.votes_right)} votes ({right_percentage:.1f}%)",
                inline=True
            )
            
            embed.add_field(
                name="🏆 Gagnant",
                value=winner_text,
                inline=False
            )
            
            # Afficher les joueurs qui ont gagné des points
            if players_who_scored:
                embed.add_field(
                    name="✅ Joueurs qui marquent (+1 point)",
                    value=f"**{len(players_who_scored)} joueurs:** {', '.join(players_who_scored)}",
                    inline=False
                )
            
            # Afficher le score actuel
            if self.player_scores:
                current_scores = sorted(
                    self.player_scores.items(),
                    key=lambda x: x[1]["correct_votes"],
                    reverse=True
                )
                
                score_text = ""
                for i, (user_id, data) in enumerate(current_scores[:5]):  # Top 5
                    score_text += f"{i+1}. {data['username']}: {data['correct_votes']}/{data['total_votes']} pts\n"
                
                embed.add_field(
                    name="📈 Score actuel (Top 5)",
                    value=score_text,
                    inline=False
                )
            
            # Ajouter info sur la prochaine manche ou fin
            if self.round_number < self.max_rounds:
                embed.add_field(
                    name="⏳ Prochaine manche",
                    value="**Prochaine manche dans 3 secondes...**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🏁 Fin du jeu",
                    value="**Calcul du classement final...**",
                    inline=False
                )
            
            # Mettre à jour le message principal
            if self.main_message:
                await self.main_message.edit(embed=embed, view=None)
        
        # Attendre 3 secondes avant la prochaine manche avec vérification d'arrêt
        try:
            for _ in range(3):
                if self.is_game_stopped:  # Le jeu a été arrêté
                    return
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            return
        
        # Vérifier à nouveau si le jeu n'a pas été arrêté
        if self.is_game_stopped:
            return
            
        self.round_number += 1
        await self.start_round()
    
    async def end_game(self, stopped_by_user=False):
        """Terminer le jeu avec classement final et statistiques"""
        self.is_game_stopped = True
        
        # Calculer le classement final
        if self.player_scores:
            final_ranking = await self.stats_manager.calculate_session_scores(self.session_id)
            
            # Mettre à jour les statistiques globales des joueurs
            for user_id, data in self.player_scores.items():
                await self.stats_manager.update_player_global_stats(
                    user_id=user_id,
                    username=data["username"],
                    wins_gained=data["correct_votes"],
                    games_played=1,
                    rounds_played=data["total_votes"]
                )
            
            # Déterminer le gagnant
            winner_id = None
            if final_ranking:
                winner_id = final_ranking[0][0]  # user_id du premier
            
            # Finaliser la session
            await self.stats_manager.end_game_session(
                self.session_id, 
                winner_id=winner_id,
                total_participants=len(self.player_scores)
            )
        
        # Créer l'embed de fin de jeu
        if stopped_by_user:
            embed = discord.Embed(
                title="🛑 JEU ARRÊTÉ !",
                description=f"Le jeu **Tu préfères** a été arrêté par {self.host.mention}.\n"
                           f"🎨 **Thème:** {self.THEMES[self.theme]['name']}\n"
                           f"📊 **Manches jouées:** {self.round_number - 1}/{self.max_rounds}",
                color=0xe74c3c
            )
        else:
            embed = discord.Embed(
                title="🎉 JEU TERMINÉ !",
                description=f"Merci d'avoir joué au **Tu préfères** !\n"
                           f"🎨 **Thème:** {self.THEMES[self.theme]['name']}\n"
                           f"📊 **Manches jouées:** {self.max_rounds}",
                color=0x2ecc71
            )
        
        # Afficher le classement final si il y a des joueurs
        if self.player_scores:
            # Calculer le classement trié
            sorted_players = sorted(
                self.player_scores.items(),
                key=lambda x: (x[1]["correct_votes"], x[1]["total_votes"]),
                reverse=True
            )
            
            # Affichage du podium
            if len(sorted_players) >= 1:
                winner_data = sorted_players[0][1]
                embed.add_field(
                    name="🥇 VAINQUEUR",
                    value=f"**{winner_data['username']}**\n"
                          f"✅ {winner_data['correct_votes']}/{winner_data['total_votes']} votes majoritaires\n"
                          f"📊 Ratio: {(winner_data['correct_votes']/winner_data['total_votes']*100):.1f}%",
                    inline=False
                )
            
            # Classement complet
            ranking_text = ""
            for i, (user_id, data) in enumerate(sorted_players):
                if i == 0:
                    emoji = "🥇"
                elif i == 1:
                    emoji = "🥈"
                elif i == 2:
                    emoji = "🥉"
                else:
                    emoji = f"{i+1}."
                
                ratio = (data['correct_votes']/data['total_votes']*100) if data['total_votes'] > 0 else 0
                ranking_text += f"{emoji} **{data['username']}** - {data['correct_votes']}/{data['total_votes']} ({ratio:.1f}%)\n"
            
            embed.add_field(
                name="📊 CLASSEMENT COMPLET",
                value=ranking_text,
                inline=False
            )
            
            # Statistiques de la partie
            total_players = len(self.player_scores)
            total_votes_cast = sum(data['total_votes'] for data in self.player_scores.values())
            embed.add_field(
                name="📈 STATISTIQUES",
                value=f"👥 {total_players} joueurs\n"
                      f"🗳️ {total_votes_cast} votes au total\n"
                      f"⭐ Basé sur les votes majoritaires",
                inline=False
            )
        
        embed.set_footer(text="Tapez !game pour rejouer • Utilisez !mystats pour voir vos statistiques globales !")
        
        # Mettre à jour le message principal avec le classement final
        if self.main_message:
            try:
                await self.main_message.edit(embed=embed, view=None)
            except discord.NotFound:
                # Le message a été supprimé, on ne fait rien
                pass
            except Exception as e:
                # En cas d'erreur, log mais ne pas créer de nouveau message
                print(f"Erreur lors de l'édition du message final: {e}")
        # Note: Pas de fallback pour éviter de créer plusieurs messages
        
        # Retirer le jeu de la liste des jeux actifs
        if self.channel.id in self.game_manager.active_games:
            del self.game_manager.active_games[self.channel.id]
    
    async def stop_game(self, user: discord.User):
        """Arrêter le jeu prématurément et complètement"""
        if user.id != self.host.id:
            return False
        
        # Arrêter complètement le jeu avec les deux flags
        self.is_active = False
        self.is_game_stopped = True
        
        # Retirer immédiatement le jeu de la liste des jeux actifs
        if self.channel.id in self.game_manager.active_games:
            del self.game_manager.active_games[self.channel.id]
        
        # Afficher le message d'arrêt
        await self.end_game(stopped_by_user=True)
        return True
    
    async def vote(self, user: discord.User, side: str):
        """Enregistrer un vote"""
        if not self.is_active:
            return False
        
        user_id = user.id
        
        # Retirer l'utilisateur des deux côtés au cas où il change d'avis
        self.votes_left.discard(user_id)
        self.votes_right.discard(user_id)
        
        # Ajouter le vote du bon côté et l'enregistrer dans le dictionnaire principal
        if side == "left":
            self.votes_left.add(user_id)
            self.votes[user_id] = "A"
        else:
            self.votes_right.add(user_id)
            self.votes[user_id] = "B"
        
        return True

class VotingView(discord.ui.View):
    """Vue avec boutons de vote et bouton d'arrêt"""
    
    def __init__(self, game: WouldYouRatherGame):
        super().__init__(timeout=10)
        self.game = game
    
    @discord.ui.button(label="⬅️ OPTION A", style=discord.ButtonStyle.primary, row=0)
    async def vote_left(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vote pour l'option de gauche"""
        success = await self.game.vote(interaction.user, "left")
        if success:
            await interaction.response.send_message(
                f"✅ Vote enregistré pour **{self.game.current_question[0]}** !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Les votes sont fermés pour cette manche !",
                ephemeral=True
            )
    
    @discord.ui.button(label="➡️ OPTION B", style=discord.ButtonStyle.secondary, row=0)
    async def vote_right(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vote pour l'option de droite"""
        success = await self.game.vote(interaction.user, "right")
        if success:
            await interaction.response.send_message(
                f"✅ Vote enregistré pour **{self.game.current_question[1]}** !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Les votes sont fermés pour cette manche !",
                ephemeral=True
            )
    
    @discord.ui.button(label="🛑 Arrêter le jeu", style=discord.ButtonStyle.danger, row=1)
    async def stop_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Arrêter le jeu (uniquement pour l'hôte)"""
        success = await self.game.stop_game(interaction.user)
        if success:
            await interaction.response.send_message(
                "🛑 Jeu arrêté avec succès !",
                ephemeral=True
            )
            self.stop()
        else:
            await interaction.response.send_message(
                "❌ Seul l'hôte du jeu peut l'arrêter !",
                ephemeral=True
            )