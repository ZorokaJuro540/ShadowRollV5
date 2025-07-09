"""
Visual Assets and Styling for Shadow Roll Bot
Enhanced visual elements, images, and aesthetic improvements
"""

import discord
import random
from typing import Dict, List

class VisualAssets:
    """Classe pour gérer tous les éléments visuels du bot"""
    
    # Bannières et images principales
    MAIN_BANNERS = [
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGJ2d2p5azBxbWFxY3B4dGN4cGNvNjFtcmpvMTlyZ3d6ejhsaGw5bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26BRBKqUiq586bRVm/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHlvNXN4YmJmNGdkeDNvZGhqMWh5bmF5YzVvNXN5cnU3dHB6NnRjeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgzoKnwFNmISR8I/giphy.gif",
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWN1c3FjYTJvcnIydjVocTRpdGwxNHB0MG5jNWhvNWZkZWRtaDJyMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l41lGvinEgARjB2HC/giphy.gif"
    ]
    
    # Images pour différentes sections
    SECTION_IMAGES = {
        'profile': [
            "https://i.imgur.com/ZQYjKbO.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnJ6cWN2Mzd5bjJjaDJxMGw2cXBneHdzazBpMGNlNTZtbWNjOWNxaiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPnAiaMCws8nOsE/giphy.gif"
        ],
        'summon': [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaHd4bHN4ams5NDNhM3NrcDRmOG5zOXYxZzg1OWN4aHJqaDdzc3VmbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3q2XhfQ8oCkm1Ts4/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYm9sYzUweGJzd2RpcDV3eTFmaDc5dGFxazl0bzl6aGRxanYwMGJwZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26BRzozg4TCBXv6QU/giphy.gif"
        ],
        'shop': [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXU2ODU1YTl6M3d4N3N6dnVqeW5vNHV3ejNtZXlqM2FseTN3dWV4eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPjM1lNsCrwEJfq/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmlkZjB1dTRwbnJmYmN3OGZwZTM4a21iYzI4OHZmZnV1cnF1ODFpdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abKhOpu0NwenH3O/giphy.gif"
        ],
        'collection': [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGo4dGZrZm1xMHJ2bjZqMW01MHQ2Z3J0aDhsdXl3a2F5Y3J0a3prbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xT9IgG50Fb7Mi0prBC/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWNnMmY2cnduZ3hkdnB1a20xdjltbm91NnV5M2w1eGNzOWxhb3E2bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26FLgGTPUDH6UGAbm/giphy.gif"
        ],
        'craft': [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGlqaTF2bzJpdnhvdzZvYzB4c2V4c2FwOWY1b2NyYXlhanl2OWZ3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abwbzFqNgHlYyAo/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcnFlbmFuNHFwbDZhYXZ3eTlvYW14aThpYWlqZGQ5bmN5aGZzd3h1NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlPystfePnYjImA/giphy.gif"
        ]
    }
    
    # Thumbnails pour les sections
    SECTION_THUMBNAILS = {
        'main_menu': "https://i.imgur.com/8bDdvxM.png",
        'profile': "https://i.imgur.com/VKm5eo8.png", 
        'summon': "https://i.imgur.com/nY8t2Kw.png",
        'shop': "https://i.imgur.com/kGz9R3m.png",
        'collection': "https://i.imgur.com/LpX8n4R.png",
        'craft': "https://i.imgur.com/mR2Hy5S.png"
    }
    
    # Bannières spéciales pour les raretés
    RARITY_BANNERS = {
        'Secret': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWI2a3FqdzRsZnB0cDJpbXRmcXNreG90cTJndjd3ZGN6M2lzd3Q5ZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26BRrSvJUa0crqw4E/giphy.gif",
        'Titan': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZGN4dXpsMzJ6Z3R1eWt1N2kzeDh0a3UyMGN5anpwZGNtbGcxNjJjdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HlHZ4sjiWWXqo2k/giphy.gif",
        'Mythic': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGY4dmlmcGgwZnJhcWJxdjU3bzJ0MXZpNDMzY2lwajFwczE4bjBjdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPkg10L7C2M0GxW/giphy.gif"
    }
    
    # Icônes améliorées pour les boutons
    ENHANCED_ICONS = {
        'profile': '👤',
        'summon': '🎲',
        'search': '🧪',
        'collection': '🎒',
        'craft': '🔮',
        'daily': '🎁',
        'shop': '🛒',
        'sell': '🪙',
        'achievements': '🎖️',
        'leaderboard': '🏆',
        'guide': '❓'
    }
    
    @classmethod
    def get_random_banner(cls, category: str = 'main') -> str:
        """Obtenir une bannière aléatoire pour une catégorie"""
        if category == 'main':
            return random.choice(cls.MAIN_BANNERS)
        elif category in cls.SECTION_IMAGES:
            return random.choice(cls.SECTION_IMAGES[category])
        return cls.MAIN_BANNERS[0]
    
    @classmethod
    def get_thumbnail(cls, section: str) -> str:
        """Obtenir la thumbnail pour une section"""
        return cls.SECTION_THUMBNAILS.get(section, cls.SECTION_THUMBNAILS['main_menu'])
    
    @classmethod
    def get_rarity_banner(cls, rarity: str) -> str:
        """Obtenir une bannière spéciale pour une rareté"""
        return cls.RARITY_BANNERS.get(rarity)
    
    @classmethod
    def create_enhanced_description(cls, base_text: str, effects: List[str] = None) -> str:
        """Créer une description enrichie avec des effets visuels"""
        enhanced = f"```ansi\n\u001b[1;35m╔══════════════════════════════════════╗\u001b[0m\n"
        enhanced += f"\u001b[1;36m║     ⭐ SHADOW ROLL SYSTEM ⭐      ║\u001b[0m\n"
        enhanced += f"\u001b[1;35m╚══════════════════════════════════════╝\u001b[0m\n\n"
        enhanced += f"\u001b[1;33m{base_text}\u001b[0m\n"
        
        if effects:
            enhanced += f"\n\u001b[1;32m✨ Effets actifs:\u001b[0m\n"
            for effect in effects:
                enhanced += f"\u001b[0;36m  ▸ {effect}\u001b[0m\n"
        
        enhanced += "```"
        return enhanced
    
    @classmethod
    def create_stylized_field_name(cls, text: str, icon: str = "🪙") -> str:
        """Créer un nom de champ stylisé"""
        return f"{icon} ═══════〔 {text.upper()} 〕═══════ {icon}"
    
    @classmethod
    def create_border_text(cls, text: str, style: str = "double") -> str:
        """Créer du texte avec bordures"""
        if style == "double":
            return f"```\n╔{'═' * (len(text) + 2)}╗\n║ {text} ║\n╚{'═' * (len(text) + 2)}╝\n```"
        elif style == "single":
            return f"```\n┌{'─' * (len(text) + 2)}┐\n│ {text} │\n└{'─' * (len(text) + 2)}┘\n```"
        elif style == "stars":
            return f"```\n✦{'━' * (len(text) + 2)}✦\n  {text}  \n✦{'━' * (len(text) + 2)}✦\n```"
        return f"```\n{text}\n```"


class AnimatedEmbeds:
    """Classe pour créer des embeds avec animations et effets visuels"""
    
    @staticmethod
    def create_loading_embed(title: str, step: int = 1, total_steps: int = 3) -> discord.Embed:
        """Créer un embed de chargement animé"""
        loading_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        frame = loading_frames[step % len(loading_frames)]
        
        progress_bar = "█" * step + "░" * (total_steps - step)
        
        embed = discord.Embed(
            title=f"{frame} {title}",
            description=f"```ansi\n\u001b[1;36m╔══════════════════════════════════════╗\u001b[0m\n\u001b[1;36m║           CHARGEMENT...              ║\u001b[0m\n\u001b[1;36m╚══════════════════════════════════════╝\u001b[0m\n\n\u001b[1;33mProgress: [{progress_bar}] {step}/{total_steps}\u001b[0m\n```",
            color=0x9b59b6
        )
        
        embed.set_image(url=VisualAssets.get_random_banner('main'))
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str, image_category: str = 'main') -> discord.Embed:
        """Créer un embed de succès avec effets visuels"""
        enhanced_desc = VisualAssets.create_enhanced_description(
            description,
            ["✨ Opération réussie", "🎯 Données synchronisées", "🔮 Magie des ténèbres activée"]
        )
        
        embed = discord.Embed(
            title=f"✅ {title}",
            description=enhanced_desc,
            color=0x00ff00
        )
        
        embed.set_image(url=VisualAssets.get_random_banner(image_category))
        embed.set_thumbnail(url=VisualAssets.get_thumbnail('main_menu'))
        
        return embed
    
    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Créer un embed d'erreur stylisé"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=f"```ansi\n\u001b[1;31m╔══════════════════════════════════════╗\u001b[0m\n\u001b[1;31m║              ERREUR                  ║\u001b[0m\n\u001b[1;31m╚══════════════════════════════════════╝\u001b[0m\n\n\u001b[1;33m{description}\u001b[0m\n```",
            color=0xff0000
        )
        
        return embed


class InteractiveElements:
    """Éléments interactifs pour améliorer l'expérience utilisateur"""
    
    @staticmethod
    def create_hover_effects() -> Dict[str, str]:
        """Créer des effets de survol pour les boutons"""
        return {
            'primary': "🪙 Cliquez pour accéder",
            'secondary': "⚡ Action disponible",
            'success': "✅ Prêt à utiliser",
            'danger': "⚠️ Action importante"
        }
    
    @staticmethod
    def get_dynamic_footer(section: str) -> str:
        """Obtenir un footer dynamique selon la section"""
        footers = {
            'main': "🌌 Shadow Roll • Plongez dans les ténèbres",
            'profile': "👤 Profil Shadow • Vos statistiques dans l'ombre",
            'shop': "🛒 Boutique Shadow • Objets mystiques disponibles",
            'summon': "🎲 Invocation • Les ténèbres vous répondent",
            'collection': "🎒 Collection • Vos trophées des ténèbres"
        }
        return footers.get(section, footers['main'])