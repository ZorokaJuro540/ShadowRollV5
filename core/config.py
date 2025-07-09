"""
Configuration settings for Shadow Roll Bot
Centralized configuration with French messages and Shadow theme
"""
import os
from typing import Dict, List


class BotConfig:
    """Configuration class for Shadow Roll Bot"""

    # Bot settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = '!'
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'bot.log'
    VERSION = 'v4.6.1'

    # Admin settings
    ADMIN_IDS = [
        921428727307567115,
        1019676314405458051,
        1355686690290663507,
        947515705463570433,  # Ajouté automatiquement
        564068933045583873,  # Ajouté automatiquement  
        1363650623441993739,  # Ajouté automatiquement
    ]

    # Game settings
    REROLL_COST = 100
    REROLL_COOLDOWN = 0.5  # seconds (normal rarities)
    REROLL_COOLDOWN_RARE = 0.5  # seconds (Mythic, Titan, Fusion, Secret)
    DAILY_REWARD_MIN = 150
    DAILY_REWARD_MAX = 300
    MAX_REROLLS_PER_COMMAND = 10
    STARTING_COINS = 1000

    # Display settings
    CURRENCY_EMOJI = "🪙"
    INVENTORY_ITEMS_PER_PAGE = 10
    LEADERBOARD_ITEMS_PER_PAGE = 10

    # Rarity settings
    RARITY_WEIGHTS = {
        'Common': 60,  # légèrement réduit
        'Rare': 25,  # inchangé
        'Epic': 10,  # un peu augmenté
        'Legendary': 4,  # plus fréquent
        'Mythic': 1,  # 10 fois plus fréquent qu'avant
        'Titan': 0.3,  # plus rare que Mythic
        'Fusion': 0.1,  # rareté très élevée
        'Secret': 0.01,  # la rareté ultime
        'Ultimate': 0.001,  # encore plus rare que Secret
        'Evolve': 0  # Rareté non invocable, craft seulement
    }

    RARITY_COLORS = {
        'Common': 0x808080,  # Gris
        'Rare': 0x0070dd,  # Bleu
        'Epic': 0xa335ee,  # Violet
        'Legendary': 0xffa500,  # Jaune
        'Mythic': 0xff0000,  # Rouge
        'Titan': 0xffffff,  # Blanc
        'Fusion': 0xff1493,  # Rose
        'Secret': 0x000000,  # Noir
        'Ultimate': 0xff6600,  # Orange
        'Evolve': 0x00ff00  # Vert
    }

    RARITY_EMOJIS = {
        'Common': '◆',
        'Rare': '◇',
        'Epic': '◈',
        'Legendary': '◉',
        'Mythic': '⬢',
        'Titan': '🔱',  # Trident pour Titan
        'Fusion': '⭐',  # Étoile pour Fusion
        'Secret': '🌑',  # Lune noire pour Secret
        'Ultimate': '🔥',  # Feu pour Ultimate
        'Evolve': '🔮'  # Cristal d'évolution
    }

    # French messages
    MESSAGES = {
        'welcome': "Bienvenue dans les ténèbres, {username}!",
        'insufficient_coins':
        "Fonds insuffisants! Il vous faut {cost} pièces.",
        'on_cooldown':
        "Invocation en recharge! Réessayez dans {time} secondes.",
        'daily_claimed': "Bénédiction déjà récupérée aujourd'hui!",
        'banned': "Vous êtes banni du bot.",
        'admin_only': "Commande réservée aux administrateurs.",
        'character_obtained': "Vous avez obtenu {character}!",
        'achievement_unlocked': "Succès débloqué: {achievement}!"
    }

    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        if not cls.DISCORD_TOKEN:
            return False
        if not cls.ADMIN_IDS:
            return False
        return True

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in cls.ADMIN_IDS
