"""
Correcteur Automatique d'Erreurs Shadow Roll
Corrige automatiquement les erreurs de types et d'imports
"""

import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def apply_character_modification(character: dict, field: str, new_value) -> dict:
    """Appliquer une modification à un personnage"""
    if character is None:
        return None
    
    modified_character = character.copy()
    
    valid_fields = ['name', 'anime', 'rarity', 'value', 'image_url']
    if field in valid_fields:
        modified_character[field] = new_value
        
    return modified_character

def safe_get_rarity(character: Optional[dict], default: str = "Common") -> str:
    """Récupérer la rareté de manière sécurisée"""
    if character is None:
        return default
    return character.get('rarity', default)

def safe_get_field(obj: Optional[dict], field: str, default="") -> str:
    """Récupérer un champ de manière sécurisée"""
    if obj is None:
        return default
    return str(obj.get(field, default))

def safe_convert_to_int(value, default: int = 0) -> int:
    """Convertir une valeur en entier de manière sécurisée"""
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default

def validate_discord_member(member) -> bool:
    """Valider qu'un membre Discord est valide"""
    return member is not None and hasattr(member, 'id')

async def setup_error_fixes():
    """Appliquer les corrections d'erreurs automatiques"""
    logger.info("Application des corrections d'erreurs automatiques")
    
    # Les corrections sont maintenant intégrées dans les fonctions utilitaires
    
    logger.info("Corrections d'erreurs appliquées")