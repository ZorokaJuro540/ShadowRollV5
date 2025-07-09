"""
Module d'administration pour la gestion persistante des personnages
Intègre le gestionnaire centralisé avec les commandes admin existantes
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name
from character_manager import CharacterManager, add_character_with_persistence

logger = logging.getLogger(__name__)

async def setup_persistent_admin_commands(bot):
    """Configure les commandes admin avec persistance des personnages"""
    
    # Initialiser le gestionnaire au démarrage
    global character_manager
    character_manager = CharacterManager()
    await character_manager.initialize()
    
    @bot.command(name='createcharpersistent', aliases=['createcharp', 'ccp'])
    async def create_character_persistent(ctx, name: str, anime: str, rarity: str, value: int, *, image_url: str = ""):
        """Créer un personnage avec persistance garantie - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            # Valider la rareté
            if rarity not in BotConfig.RARITY_WEIGHTS:
                await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
                return
            
            # Vérifier si le personnage existe déjà
            existing = await character_manager.search_characters(name)
            for char in existing:
                if char['name'].lower() == name.lower() and char['anime'].lower() == anime.lower():
                    await ctx.send(f"❌ Le personnage {name} de {anime} existe déjà")
                    return
            
            # Créer le personnage avec persistance
            success = await add_character_with_persistence(
                name, anime, rarity, value, image_url, ctx.author.id
            )
            
            if success:
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                embed = discord.Embed(
                    title="✅ Personnage Créé et Sauvegardé",
                    description=f"{rarity_emoji} **{name}** ({anime})",
                    color=BotConfig.RARITY_COLORS.get(rarity, 0x808080)
                )
                embed.add_field(name="💎 Rareté", value=rarity, inline=True)
                embed.add_field(name="🪙 Valeur", value=f"{format_number(value)} SC", inline=True)
                embed.add_field(name="📁 Statut", value="Stocké de manière permanente", inline=False)
                
                if image_url:
                    embed.set_thumbnail(url=image_url)
                
                await ctx.send(embed=embed)
                logger.info(f"Admin {ctx.author.id} created persistent character: {name} ({anime})")
            else:
                await ctx.send(f"❌ Erreur lors de la création du personnage {name}")
                
        except ValueError:
            await ctx.send("❌ La valeur doit être un nombre entier")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
            logger.error(f"Erreur lors de la création du personnage persistant: {e}")
    
    @bot.command(name='syncchars', aliases=['sync'])
    async def sync_characters(ctx):
        """Synchroniser tous les personnages vers le stockage persistant - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            await ctx.send("🔄 Synchronisation en cours...")
            
            characters = await character_manager.sync_all_characters()
            stats = await character_manager.get_statistics()
            
            embed = discord.Embed(
                title="✅ Synchronisation Terminée",
                description=f"**{len(characters)} personnages synchronisés**",
                color=0x00ff00
            )
            
            embed.add_field(
                name="📊 Statistiques",
                value=(f"Total: {stats['total_characters']}\n"
                       f"Avec images: {stats['with_images']}\n"
                       f"Sans images: {stats['without_images']}"),
                inline=True
            )
            
            # Top 3 raretés
            top_rarities = sorted(stats['by_rarity'].items(), key=lambda x: x[1], reverse=True)[:3]
            rarity_text = "\n".join([f"{rarity}: {count}" for rarity, count in top_rarities])
            embed.add_field(name="🎯 Top Raretés", value=rarity_text, inline=True)
            
            # Top 3 animes
            top_animes = sorted(stats['by_anime'].items(), key=lambda x: x[1], reverse=True)[:3]
            anime_text = "\n".join([f"{anime}: {count}" for anime, count in top_animes])
            embed.add_field(name="📺 Top Animes", value=anime_text, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"Admin {ctx.author.id} synchronized characters")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la synchronisation: {e}")
            logger.error(f"Erreur de synchronisation: {e}")
    
    @bot.command(name='charstats', aliases=['cs'])
    async def character_statistics(ctx):
        """Afficher les statistiques détaillées des personnages - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            stats = await character_manager.get_statistics()
            
            embed = discord.Embed(
                title="📊 Statistiques Détaillées des Personnages",
                description=f"**Total: {stats['total_characters']} personnages**",
                color=BotConfig.RARITY_COLORS['Secret']
            )
            
            # Statistiques par rareté
            rarity_stats = []
            for rarity in ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret', 'Evolve']:
                count = stats['by_rarity'].get(rarity, 0)
                emoji = BotConfig.RARITY_EMOJIS.get(rarity, "◆")
                if count > 0:
                    rarity_stats.append(f"{emoji} {rarity}: {count}")
            
            embed.add_field(
                name="🎯 Par Rareté",
                value="\n".join(rarity_stats) if rarity_stats else "Aucune donnée",
                inline=True
            )
            
            # Top 5 animes
            top_animes = sorted(stats['by_anime'].items(), key=lambda x: x[1], reverse=True)[:5]
            anime_text = "\n".join([f"📺 {anime}: {count}" for anime, count in top_animes])
            embed.add_field(
                name="📺 Top 5 Animes",
                value=anime_text if anime_text else "Aucune donnée",
                inline=True
            )
            
            # Statistiques d'images
            embed.add_field(
                name="🖼️ Images",
                value=(f"Avec image: {stats['with_images']}\n"
                       f"Sans image: {stats['without_images']}\n"
                       f"Pourcentage: {(stats['with_images']/stats['total_characters']*100):.1f}%"),
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des statistiques: {e}")
            logger.error(f"Erreur de statistiques: {e}")
    
    @bot.command(name='backupchars', aliases=['backup'])
    async def backup_characters(ctx, backup_name: Optional[str] = None):
        """Créer une sauvegarde des personnages - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            await ctx.send("💾 Création de la sauvegarde...")
            
            backup_file = await character_manager.backup_characters(backup_name)
            
            if backup_file:
                embed = discord.Embed(
                    title="✅ Sauvegarde Créée",
                    description=f"**Fichier:** `{backup_file}`",
                    color=0x00ff00
                )
                
                stats = await character_manager.get_statistics()
                embed.add_field(
                    name="📊 Contenu",
                    value=f"{stats['total_characters']} personnages sauvegardés",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                logger.info(f"Admin {ctx.author.id} created backup: {backup_file}")
            else:
                await ctx.send("❌ Erreur lors de la création de la sauvegarde")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
            logger.error(f"Erreur de sauvegarde: {e}")
    
    @bot.command(name='findchar', aliases=['fc'])
    async def find_character(ctx, *, search_term: str):
        """Rechercher un personnage dans le système persistant - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            results = await character_manager.search_characters(search_term)
            
            if not results:
                await ctx.send(f"❌ Aucun personnage trouvé pour '{search_term}'")
                return
            
            if len(results) == 1:
                char = results[0]
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], "◆")
                
                embed = discord.Embed(
                    title=f"{rarity_emoji} {char['name']}",
                    description=f"**Anime:** {char['anime']}",
                    color=BotConfig.RARITY_COLORS.get(char['rarity'], 0x808080)
                )
                
                embed.add_field(name="💎 Rareté", value=char['rarity'], inline=True)
                embed.add_field(name="🪙 Valeur", value=f"{format_number(char['value'])} SC", inline=True)
                embed.add_field(name="🆔 ID", value=char['id'], inline=True)
                embed.add_field(name="📁 Source", value=char.get('source', 'database'), inline=True)
                
                if char.get('image_url'):
                    embed.set_thumbnail(url=char['image_url'])
                
                await ctx.send(embed=embed)
            else:
                # Plusieurs résultats
                embed = discord.Embed(
                    title=f"🔍 {len(results)} résultats pour '{search_term}'",
                    color=0x3498db
                )
                
                results_text = ""
                for char in results[:10]:  # Limiter à 10 résultats
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], "◆")
                    results_text += f"{rarity_emoji} **{char['name']}** ({char['anime']}) - {char['rarity']}\n"
                
                if len(results) > 10:
                    results_text += f"\n... et {len(results) - 10} autres résultats"
                
                embed.description = results_text
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la recherche: {e}")
            logger.error(f"Erreur de recherche: {e}")

    @bot.command(name='modifychar', aliases=['modchar', 'mc'])
    async def modify_character_command(ctx, character_input: str, field: str, *, new_value: str):
        """Modifier un personnage existant par nom ou ID - Admin seulement
        Usage: !modifychar "nom ou ID" field nouvelle_valeur
        Fields: name, anime, rarity, value, image_url
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            # Valider le champ
            valid_fields = ['name', 'anime', 'rarity', 'value', 'image_url']
            if field not in valid_fields:
                await ctx.send(f"❌ Champ invalide. Utilisez: {', '.join(valid_fields)}")
                return
            
            # Déterminer si l'input est un ID ou un nom
            character = None
            search_type = ""
            
            if character_input.isdigit():
                # Recherche par ID
                char_id = int(character_input)
                character = await character_manager.get_character_by_id(char_id)
                search_type = f"ID {char_id}"
                
                if not character:
                    await ctx.send(f"❌ Aucun personnage trouvé avec l'ID {char_id}")
                    return
            else:
                # Recherche par nom
                characters = await character_manager.search_characters(character_input)
                search_type = f"nom '{character_input}'"
                
                if not characters:
                    await ctx.send(f"❌ Aucun personnage trouvé pour '{character_input}'")
                    return
                
                if len(characters) > 1:
                    # Multiple characters found
                    embed = discord.Embed(
                        title="🔍 Plusieurs personnages trouvés",
                        description="Soyez plus spécifique ou utilisez l'ID du personnage:",
                        color=0x3498db
                    )
                    
                    char_list = ""
                    for char in characters[:5]:  # Limit to 5 results
                        char_list += f"ID {char['id']}: **{char['name']}** ({char['anime']}) - {char['rarity']}\n"
                    
                    embed.add_field(name="Résultats", value=char_list, inline=False)
                    embed.add_field(name="Usage", value=f"!modifychar {characters[0]['id']} {field} {new_value}", inline=False)
                    await ctx.send(embed=embed)
                    return
                
                character = characters[0]
            old_value = character.get(field, 'N/A')
            
            # Valider les valeurs spéciales
            if field == 'rarity':
                if new_value not in BotConfig.RARITY_WEIGHTS:
                    await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
                    return
            elif field == 'value':
                try:
                    new_value = int(new_value)
                except ValueError:
                    await ctx.send("❌ La valeur doit être un nombre entier")
                    return
            
            # Appliquer la modification
            success = await character_manager.update_character_field(character['id'], field, new_value)
            
            if success:
                # Créer l'embed de confirmation
                from modules.error_fixer import safe_get_field
                rarity_color = BotConfig.RARITY_COLORS.get(safe_get_field(character, 'rarity', 'Common'), 0x808080)
                embed = discord.Embed(
                    title="✅ Personnage Modifié",
                    description=f"**{character['name']}** ({character['anime']})",
                    color=rarity_color
                )
                
                embed.add_field(name="🆔 ID", value=str(character['id']), inline=True)
                embed.add_field(name="🔍 Trouvé par", value=search_type, inline=True)
                embed.add_field(name="📝 Champ", value=field.capitalize(), inline=True)
                embed.add_field(name="📋 Ancienne valeur", value=str(old_value), inline=True)
                embed.add_field(name="✨ Nouvelle valeur", value=str(new_value), inline=True)
                embed.add_field(name="💾 Statut", value="✅ Sauvegardé de manière permanente", inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"Admin {ctx.author.id} modified character {character['id']} via {search_type}: {field} = {new_value}")
            else:
                await ctx.send(f"❌ Erreur lors de la modification du personnage trouvé par {search_type}")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
            logger.error(f"Erreur lors de la modification du personnage: {e}")
    
    @bot.command(name='modifycharid', aliases=['mcid'])
    async def modify_character_by_id(ctx, character_id: int, field: str, *, new_value: str):
        """Modifier un personnage par son ID - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            # Valider le champ
            valid_fields = ['name', 'anime', 'rarity', 'value', 'image_url']
            if field not in valid_fields:
                await ctx.send(f"❌ Champ invalide. Utilisez: {', '.join(valid_fields)}")
                return
            
            # Récupérer le personnage par ID
            character = await character_manager.get_character_by_id(character_id)
            
            if not character:
                await ctx.send(f"❌ Aucun personnage trouvé avec l'ID {character_id}")
                return
            
            old_value = character.get(field, 'N/A')
            
            # Valider les valeurs spéciales
            if field == 'rarity':
                if new_value not in BotConfig.RARITY_WEIGHTS:
                    await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(BotConfig.RARITY_WEIGHTS.keys())}")
                    return
            elif field == 'value':
                try:
                    new_value = int(new_value)
                except ValueError:
                    await ctx.send("❌ La valeur doit être un nombre entier")
                    return
            
            # Appliquer la modification
            success = await apply_character_modification(character_id, field, new_value)
            
            if success:
                rarity_color = BotConfig.RARITY_COLORS.get(character.get('rarity'), 0x808080)
                embed = discord.Embed(
                    title="✅ Personnage Modifié",
                    description=f"**{character['name']}** ({character['anime']}) - ID: {character_id}",
                    color=rarity_color
                )
                
                embed.add_field(name="Champ modifié", value=field.capitalize(), inline=True)
                embed.add_field(name="Ancienne valeur", value=str(old_value), inline=True)
                embed.add_field(name="Nouvelle valeur", value=str(new_value), inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"Admin {ctx.author.id} modified character {character_id}: {field} = {new_value}")
            else:
                await ctx.send(f"❌ Erreur lors de la modification")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
            logger.error(f"Erreur lors de la modification par ID: {e}")

    @bot.command(name='givechar', aliases=['gc', 'givecharacter'])
    async def give_character_to_user(ctx, user: discord.Member, *, character_name: str):
        """Donner un personnage spécifique à un utilisateur - Admin seulement
        Usage: !givechar @utilisateur nom_du_personnage
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            # Rechercher le personnage
            characters = await character_manager.search_characters(character_name)
            
            if not characters:
                await ctx.send(f"❌ Aucun personnage trouvé pour '{character_name}'")
                return
            
            if len(characters) > 1:
                # Multiple characters found - let admin choose
                embed = discord.Embed(
                    title="🔍 Plusieurs personnages trouvés",
                    description=f"Plusieurs personnages correspondent à '{character_name}'. Soyez plus spécifique:",
                    color=0x3498db
                )
                
                char_list = ""
                for i, char in enumerate(characters[:5], 1):  # Limit to 5 results
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], "◆")
                    char_list += f"{i}. {rarity_emoji} **{char['name']}** ({char['anime']}) - {char['rarity']}\n"
                
                embed.add_field(name="Résultats", value=char_list, inline=False)
                embed.add_field(name="💡 Conseil", value=f"Utilisez le nom exact: `!givechar @{user.display_name} \"nom exact\"`", inline=False)
                await ctx.send(embed=embed)
                return
            
            # Found exactly one character
            character = characters[0]
            
            # Ensure the target user exists in database
            target_player = await bot.db.get_or_create_player(user.id, get_display_name(user))
            
            # Add character to user's inventory
            await bot.db.add_character_to_inventory(user.id, character['id'])
            
            # Create confirmation embed
            rarity_color = BotConfig.RARITY_COLORS.get(character['rarity'], 0x808080)
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], "◆")
            
            embed = discord.Embed(
                title="✅ Personnage Donné",
                description=f"**{character['name']}** a été donné à {user.mention}",
                color=rarity_color
            )
            
            embed.add_field(
                name="📋 Détails du personnage",
                value=(f"{rarity_emoji} **{character['name']}**\n"
                       f"📺 {character['anime']}\n"
                       f"⭐ {character['rarity']}\n"
                       f"🪙 {format_number(character['value'])} SC"),
                inline=True
            )
            
            embed.add_field(
                name="🎯 Destinataire",
                value=(f"👤 {user.display_name}\n"
                       f"🆔 {user.id}\n"
                       f"📊 Ajouté à l'inventaire"),
                inline=True
            )
            
            embed.add_field(
                name="👨‍💼 Administrateur",
                value=f"{ctx.author.mention}",
                inline=False
            )
            
            if character.get('image_url'):
                embed.set_thumbnail(url=character['image_url'])
            
            embed.set_footer(text=f"Shadow Roll • Admin Command • {character['id']}")
            
            await ctx.send(embed=embed)
            
            # Send notification to the target user
            try:
                user_embed = discord.Embed(
                    title="🎁 Vous avez reçu un personnage !",
                    description=f"Un administrateur vous a donné **{character['name']}**",
                    color=rarity_color
                )
                
                user_embed.add_field(
                    name=f"{rarity_emoji} {character['name']}",
                    value=f"📺 {character['anime']}\n⭐ {character['rarity']}\n🪙 {format_number(character['value'])} SC",
                    inline=False
                )
                
                if character.get('image_url'):
                    user_embed.set_thumbnail(url=character['image_url'])
                
                user_embed.set_footer(text="Utilisez !menu pour voir votre collection")
                
                await user.send(embed=user_embed)
            except discord.Forbidden:
                await ctx.send(f"⚠️ Impossible d'envoyer un MP à {user.display_name} (MPs fermés)")
            
            logger.info(f"Admin {ctx.author.id} gave character {character['id']} ({character['name']}) to user {user.id}")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du don du personnage: {e}")
            logger.error(f"Erreur lors du don de personnage: {e}")

    @bot.command(name='givecharid', aliases=['gcid'])
    async def give_character_by_id(ctx, user: discord.Member, character_id: int):
        """Donner un personnage par son ID à un utilisateur - Admin seulement
        Usage: !givecharid @utilisateur 123
        """
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
            
        try:
            # Get character by ID
            character = await character_manager.get_character_by_id(character_id)
            
            if not character:
                await ctx.send(f"❌ Aucun personnage trouvé avec l'ID {character_id}")
                return
            
            # Ensure the target user exists in database
            target_player = await bot.db.get_or_create_player(user.id, get_display_name(user))
            
            # Add character to user's inventory
            await bot.db.add_character_to_inventory(user.id, character_id)
            
            # Create confirmation embed (same as above)
            rarity_color = BotConfig.RARITY_COLORS.get(character['rarity'], 0x808080)
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], "◆")
            
            embed = discord.Embed(
                title="✅ Personnage Donné (par ID)",
                description=f"**{character['name']}** a été donné à {user.mention}",
                color=rarity_color
            )
            
            embed.add_field(
                name="📋 Détails du personnage",
                value=(f"{rarity_emoji} **{character['name']}**\n"
                       f"📺 {character['anime']}\n"
                       f"⭐ {character['rarity']}\n"
                       f"🪙 {format_number(character['value'])} SC\n"
                       f"🆔 ID: {character_id}"),
                inline=True
            )
            
            embed.add_field(
                name="🎯 Destinataire",
                value=(f"👤 {user.display_name}\n"
                       f"🆔 {user.id}\n"
                       f"📊 Ajouté à l'inventaire"),
                inline=True
            )
            
            embed.add_field(
                name="👨‍💼 Administrateur",
                value=f"{ctx.author.mention}",
                inline=False
            )
            
            if character.get('image_url'):
                embed.set_thumbnail(url=character['image_url'])
            
            embed.set_footer(text=f"Shadow Roll • Admin Command • ID: {character_id}")
            
            await ctx.send(embed=embed)
            
            # Send notification to the target user
            try:
                user_embed = discord.Embed(
                    title="🎁 Vous avez reçu un personnage !",
                    description=f"Un administrateur vous a donné **{character['name']}**",
                    color=rarity_color
                )
                
                user_embed.add_field(
                    name=f"{rarity_emoji} {character['name']}",
                    value=f"📺 {character['anime']}\n⭐ {character['rarity']}\n🪙 {format_number(character['value'])} SC",
                    inline=False
                )
                
                if character.get('image_url'):
                    user_embed.set_thumbnail(url=character['image_url'])
                
                user_embed.set_footer(text="Utilisez !menu pour voir votre collection")
                
                await user.send(embed=user_embed)
            except discord.Forbidden:
                await ctx.send(f"⚠️ Impossible d'envoyer un MP à {user.display_name} (MPs fermés)")
            
            logger.info(f"Admin {ctx.author.id} gave character ID {character_id} ({character['name']}) to user {user.id}")
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du don du personnage: {e}")
            logger.error(f"Erreur lors du don de personnage par ID: {e}")

    logger.info("Commandes d'administration persistante configurées")


# ═══════════════════ FONCTIONS AUTONOMES POUR INTERFACE ADMIN ═══════════════════

async def give_character_to_user(bot, admin_id: int, user_identifier: str, character_name: str):
    """Fonction autonome pour donner un personnage à un utilisateur par nom"""
    try:
        # Rechercher le personnage
        characters = await character_manager.search_characters(character_name)
        
        if not characters:
            return False, f"Aucun personnage trouvé pour '{character_name}'"
        
        if len(characters) > 1:
            char_list = ""
            for i, char in enumerate(characters[:5], 1):
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], "◆")
                char_list += f"{i}. {rarity_emoji} **{char['name']}** ({char['anime']}) - {char['rarity']}\n"
            
            return False, f"Plusieurs personnages trouvés:\n{char_list}\nSoyez plus spécifique."
        
        # Found exactly one character
        character = characters[0]
        
        # Trouver l'utilisateur cible
        target_user = None
        if user_identifier.isdigit():
            target_user = bot.get_user(int(user_identifier))
        else:
            # Rechercher par nom dans les joueurs
            cursor = await bot.db.db.execute(
                "SELECT user_id FROM players WHERE username LIKE ?", (f"%{user_identifier}%",)
            )
            result = await cursor.fetchone()
            if result:
                target_user = bot.get_user(result[0])
        
        if not target_user:
            return False, f"Utilisateur '{user_identifier}' non trouvé"
        
        # Ensure the target user exists in database
        await bot.db.get_or_create_player(target_user.id, get_display_name(target_user))
        
        # Add character to user's inventory
        await bot.db.add_character_to_inventory(target_user.id, character['id'])
        
        # Log the action
        logger.info(f"Admin {admin_id} gave character ID {character['id']} ({character['name']}) to user {target_user.id} via interface")
        
        # Send notification to the target user
        try:
            rarity_color = BotConfig.RARITY_COLORS.get(character['rarity'], 0x808080)
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], "◆")
            
            user_embed = discord.Embed(
                title="🎁 Vous avez reçu un personnage !",
                description=f"Un administrateur vous a donné **{character['name']}**",
                color=rarity_color
            )
            
            user_embed.add_field(
                name=f"{rarity_emoji} {character['name']}",
                value=f"📺 {character['anime']}\n⭐ {character['rarity']}\n🪙 {format_number(character['value'])} SC",
                inline=False
            )
            
            if character.get('image_url'):
                user_embed.set_thumbnail(url=character['image_url'])
            
            user_embed.set_footer(text="Shadow Roll • Cadeau Admin")
            
            await target_user.send(embed=user_embed)
        except discord.Forbidden:
            pass  # MPs fermés, ce n'est pas grave
        
        return True, f"Personnage **{character['name']}** ({character['rarity']}) donné à {target_user.display_name}"
        
    except Exception as e:
        logger.error(f"Erreur lors du don de personnage: {e}")
        return False, f"Erreur: {str(e)}"


async def give_character_by_id_to_user(bot, admin_id: int, user_identifier: str, character_id: int):
    """Fonction autonome pour donner un personnage à un utilisateur par ID"""
    try:
        # Récupérer le personnage par ID
        character = await character_manager.get_character_by_id(character_id)
        
        if not character:
            return False, f"Aucun personnage trouvé avec l'ID {character_id}"
        
        # Trouver l'utilisateur cible
        target_user = None
        if user_identifier.isdigit():
            target_user = bot.get_user(int(user_identifier))
        else:
            # Rechercher par nom dans les joueurs
            cursor = await bot.db.db.execute(
                "SELECT user_id FROM players WHERE username LIKE ?", (f"%{user_identifier}%",)
            )
            result = await cursor.fetchone()
            if result:
                target_user = bot.get_user(result[0])
        
        if not target_user:
            return False, f"Utilisateur '{user_identifier}' non trouvé"
        
        # Ensure the target user exists in database
        await bot.db.get_or_create_player(target_user.id, get_display_name(target_user))
        
        # Add character to user's inventory
        await bot.db.add_character_to_inventory(target_user.id, character['id'])
        
        # Log the action
        logger.info(f"Admin {admin_id} gave character ID {character_id} ({character['name']}) to user {target_user.id} via interface")
        
        # Send notification to the target user
        try:
            rarity_color = BotConfig.RARITY_COLORS.get(character['rarity'], 0x808080)
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], "◆")
            
            user_embed = discord.Embed(
                title="🎁 Vous avez reçu un personnage !",
                description=f"Un administrateur vous a donné **{character['name']}**",
                color=rarity_color
            )
            
            user_embed.add_field(
                name=f"{rarity_emoji} {character['name']}",
                value=f"📺 {character['anime']}\n⭐ {character['rarity']}\n🪙 {format_number(character['value'])} SC\n🆔 ID: {character_id}",
                inline=False
            )
            
            if character.get('image_url'):
                user_embed.set_thumbnail(url=character['image_url'])
            
            user_embed.set_footer(text="Shadow Roll • Cadeau Admin")
            
            await target_user.send(embed=user_embed)
        except discord.Forbidden:
            pass  # MPs fermés, ce n'est pas grave
        
        return True, f"Personnage **{character['name']}** (ID: {character_id}, {character['rarity']}) donné à {target_user.display_name}"
        
    except Exception as e:
        logger.error(f"Erreur lors du don de personnage par ID: {e}")
        return False, f"Erreur: {str(e)}"