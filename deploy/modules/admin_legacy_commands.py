"""
Legacy Admin Commands for Shadow Roll Bot
All traditional admin commands with proper error handling
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
import asyncio
from datetime import datetime

from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.admin_character_sync import sync_admin_characters

logger = logging.getLogger(__name__)

# Character selection view for lookcard command
class LookcardSelectionView(discord.ui.View):
    def __init__(self, characters, user_id, bot):
        super().__init__(timeout=60)
        self.characters = characters
        self.user_id = user_id
        self.bot = bot
        
        # Add buttons for each character (max 10)
        for i, char in enumerate(characters[:10]):
            button = discord.ui.Button(
                label=f"{i+1}. {char[1]} ({char[2]})",
                style=discord.ButtonStyle.secondary,
                custom_id=f"lookcard_char_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, index):
        async def callback(interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette sélection.", ephemeral=True)
                return
            
            row = self.characters[index]
            from core.models import Character
            character = Character(
                id=row[0],
                name=row[1],
                anime=row[2],
                rarity=row[3],
                value=row[4],
                image_url=row[5]
            )
            
            username = get_display_name(interaction.user)
            
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
                text="Shadow Roll • Consultation de Personnage",
                icon_url=interaction.user.avatar.url if interaction.user.avatar else None
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
        
        return callback
    
    async def on_timeout(self):
        # Disable all buttons when timeout
        for item in self.children:
            item.disabled = True

async def setup_legacy_admin_commands(bot):
    """Setup all legacy admin commands"""
    logger.info("Setting up legacy admin commands...")
    
    # ═══════════════════ COMMANDES DE BASE ═══════════════════
    
    @bot.command(name='syncchars', aliases=['syncpersonnages'])
    async def sync_characters_to_code(ctx):
        """Synchroniser tous les personnages vers le code - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            await ctx.send("🔄 Synchronisation en cours...")
            
            # Synchroniser les personnages avec le code
            synced_count = await sync_admin_characters(bot.db)
            
            # Vérifier les séries manquantes
            cursor = await bot.db.db.execute("SELECT DISTINCT anime FROM characters")
            all_animes = [row[0] for row in await cursor.fetchall()]
            
            series_created = 0
            for anime in all_animes:
                # Vérifier si la série existe
                cursor = await bot.db.db.execute(
                    "SELECT id FROM series WHERE LOWER(series_name) = LOWER(?)",
                    (anime,)
                )
                if not await cursor.fetchone():
                    await bot.db.auto_create_series(anime)
                    series_created += 1
            
            embed = discord.Embed(
                title="✅ Synchronisation Terminée",
                description="Tous les personnages ont été synchronisés avec le code",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Résultats",
                value=f"**Personnages synchronisés:** {synced_count}\n**Séries créées:** {series_created}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in syncchars: {e}")
            await ctx.send("❌ Erreur lors de la synchronisation.")
    
    @bot.command(name='fixbluelock', aliases=['addbluelock'])
    async def fix_bluelock_characters(ctx):
        """Ajouter tous les personnages Blue Lock manquants - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            await ctx.send("🔄 Ajout des personnages Blue Lock manquants...")
            
            # Définir tous les personnages Blue Lock avec leurs vraies informations
            bluelock_characters = [
                ("Rin Itoshi", "Blue Lock", "Legendary", 1500, "https://static.wikia.nocookie.net/bluelock/images/d/d1/Rin_Itoshi_Anime_Profile.png"),
                ("Sae Itoshi", "Blue Lock", "Legendary", 1400, "https://static.wikia.nocookie.net/bluelock/images/5/5c/Sae_Itoshi_Anime_Profile.png"),
                ("Michael Kaiser", "Blue Lock", "Mythic", 3000, "https://static.wikia.nocookie.net/bluelock/images/4/4c/Michael_Kaiser_Anime_Profile.png"),
                ("Alexis Ness", "Blue Lock", "Epic", 800, "https://static.wikia.nocookie.net/bluelock/images/b/b9/Alexis_Ness_Anime_Profile.png"),
                ("Yukimiya Kenyu", "Blue Lock", "Epic", 750, "https://static.wikia.nocookie.net/bluelock/images/e/e5/Yukimiya_Kenyu_Anime_Profile.png"),
                ("Otoya Eita", "Blue Lock", "Rare", 400, "https://static.wikia.nocookie.net/bluelock/images/a/a6/Otoya_Eita_Anime_Profile.png"),
                ("Karasu Tabito", "Blue Lock", "Rare", 450, "https://static.wikia.nocookie.net/bluelock/images/7/7f/Karasu_Tabito_Anime_Profile.png"),
                ("Hiori Yo", "Blue Lock", "Rare", 350, "https://static.wikia.nocookie.net/bluelock/images/2/2a/Hiori_Yo_Anime_Profile.png"),
                ("Zantetsu Tsurugi", "Blue Lock", "Common", 150, "https://static.wikia.nocookie.net/bluelock/images/1/1e/Zantetsu_Tsurugi_Anime_Profile.png"),
                ("Ikki Niko", "Blue Lock", "Common", 120, "https://static.wikia.nocookie.net/bluelock/images/c/c8/Ikki_Niko_Anime_Profile.png"),
                ("Anri Teieri", "Blue Lock", "Rare", 300, "https://static.wikia.nocookie.net/bluelock/images/8/8c/Anri_Teieri_Anime_Profile.png"),
            ]
            
            added_count = 0
            updated_count = 0
            
            for name, anime, rarity, value, image_url in bluelock_characters:
                # Vérifier si le personnage existe déjà
                cursor = await bot.db.db.execute(
                    "SELECT id FROM characters WHERE LOWER(name) = LOWER(?)",
                    (name,)
                )
                existing = await cursor.fetchone()
                
                if existing:
                    # Mettre à jour le personnage existant
                    await bot.db.db.execute(
                        "UPDATE characters SET anime=?, rarity=?, value=?, image_url=? WHERE LOWER(name) = LOWER(?)",
                        (anime, rarity, value, image_url, name)
                    )
                    updated_count += 1
                else:
                    # Créer le nouveau personnage
                    await bot.db.db.execute(
                        "INSERT INTO characters (name, anime, rarity, value, image_url) VALUES (?, ?, ?, ?, ?)",
                        (name, anime, rarity, value, image_url)
                    )
                    added_count += 1
            
            await bot.db.db.commit()
            
            # Créer automatiquement la série Blue Lock
            await bot.db.auto_create_series("Blue Lock")
            
            # Synchroniser avec le code
            synced_count = await sync_admin_characters(bot.db)
            
            embed = discord.Embed(
                title="✅ Personnages Blue Lock Ajoutés",
                description="Tous les personnages Blue Lock ont été ajoutés avec succès",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Résultats",
                value=f"**Nouveaux:** {added_count}\n**Mis à jour:** {updated_count}\n**Synchronisés:** {synced_count}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in fixbluelock: {e}")
            await ctx.send("❌ Erreur lors de l'ajout des personnages Blue Lock.")
    
    @bot.command(name='createevolve', aliases=['addevolve'])
    async def create_evolve_character(ctx, base_character_name: str, *, anime_name: str = None):
        """Créer automatiquement un personnage Evolve - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            await ctx.send("🔮 Création du personnage Evolve en cours...")
            
            # Chercher le personnage de base
            cursor = await bot.db.db.execute(
                "SELECT name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) = LOWER(?)",
                (base_character_name,)
            )
            base_char = await cursor.fetchone()
            
            if not base_char:
                await ctx.send(f"❌ Personnage de base '{base_character_name}' introuvable.")
                return
            
            base_name, base_anime, base_rarity, base_value, base_image = base_char
            evolved_name = f"{base_name} Evolve"
            
            # Utiliser l'anime fourni ou celui du personnage de base
            final_anime = anime_name if anime_name else base_anime
            
            # Calculer la valeur évoluée (valeur de base * 15)
            evolved_value = base_value * 15
            
            # Vérifier si le personnage Evolve existe déjà
            cursor = await bot.db.db.execute(
                "SELECT id FROM characters WHERE LOWER(name) = LOWER(?)",
                (evolved_name,)
            )
            if await cursor.fetchone():
                await ctx.send(f"❌ Le personnage **{evolved_name}** existe déjà.")
                return
            
            # Créer le personnage Evolve
            await bot.db.db.execute(
                "INSERT INTO characters (name, anime, rarity, value, image_url) VALUES (?, ?, 'Evolve', ?, ?)",
                (evolved_name, final_anime, evolved_value, base_image)
            )
            await bot.db.db.commit()
            
            # Créer automatiquement la série
            await bot.db.auto_create_series(final_anime)
            
            # Synchroniser avec le code
            synced_count = await sync_admin_characters(bot.db)
            
            embed = discord.Embed(
                title="✅ Personnage Evolve Créé",
                description=f"**{evolved_name}** a été créé avec succès",
                color=BotConfig.RARITY_COLORS['Evolve']
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Personnage de base:** {base_name}\n**Anime:** {final_anime}\n**Valeur:** {format_number(evolved_value)} pièces",
                inline=False
            )
            embed.add_field(
                name="🔮 Craft",
                value=f"**Recette créée:** {base_name} x10 → {evolved_name}\n**Synchronisés:** {synced_count} personnages",
                inline=False
            )
            
            if base_image:
                embed.set_thumbnail(url=base_image)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in createevolve: {e}")
            await ctx.send("❌ Erreur lors de la création du personnage Evolve.")
    

    @bot.command(name='lookcard', aliases=['previewcard', 'cardpreview'])
    async def look_card(ctx, *, character_name: str):
        """Afficher la carte d'un personnage - Disponible pour tous"""
        # Commande accessible à tous les utilisateurs
        
        try:
            # Recherche du personnage - exact match first, then partial
            cursor = await bot.db.db.execute(
                "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) = LOWER(?) ORDER BY name",
                (character_name,)
            )
            char_rows = await cursor.fetchall()
            
            # If no exact match, try partial match
            if not char_rows:
                cursor = await bot.db.db.execute(
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
                
                view = LookcardSelectionView(char_rows, ctx.author.id, bot)
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
                       f"Valeur: {format_number(character.value)} SC\n"
                       f"```\n"
                       f"🎭 **Série:** {character.anime}\n"
                       f"💎 **Rareté:** {character.rarity} {character.get_rarity_emoji()}\n"
                       f"🪙 **Valeur:** {format_number(character.value)} Shadow Coins"),
                inline=False
            )
            
            # Ajouter les statistiques d'invocation
            rarity_chance = BotConfig.RARITY_WEIGHTS.get(character.rarity, 0)
            embed.add_field(
                name="📊 Statistiques d'Invocation",
                value=(f"```\n"
                       f"Chance: {rarity_chance}%\n"
                       f"ID Système: {character.id}\n"
                       f"```"),
                inline=True
            )
            
            # Ajouter informations sur la rareté
            if character.rarity == 'Evolve':
                embed.add_field(
                    name="🔮 Rareté Spéciale",
                    value=(f"```\n"
                           f"Type: Craft exclusif\n"
                           f"Obtention: Évolution uniquement\n"
                           f"Invocation: Impossible\n"
                           f"```"),
                    inline=True
                )
            else:
                embed.add_field(
                    name="🎲 Disponibilité",
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
                text="Shadow Roll • Consultation de Personnage",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in lookcard command: {e}")
            await ctx.send("❌ Erreur lors de l'affichage de la carte.")
    
    @bot.command(name='testcard')
    async def test_card(ctx, *, character_name: str = "Naruto"):
        """Test simple pour vérifier les commandes admin"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'êtes pas admin.")
            return
        
        try:
            cursor = await bot.db.db.execute(
                "SELECT id, name, anime, rarity, value FROM characters WHERE LOWER(name) LIKE LOWER(?) LIMIT 1",
                (f"%{character_name}%",)
            )
            result = await cursor.fetchone()
            
            if result:
                await ctx.send(f"✅ Trouvé: **{result[1]}** ({result[2]}) - {result[3]} - {result[4]} SC")
            else:
                await ctx.send(f"❌ Aucun personnage trouvé pour '{character_name}'")
                
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")
    
    # ═══════════════════ GESTION DES JOUEURS ═══════════════════
    
    @bot.command(name='givecoins', aliases=['addcoins', 'coins'])
    async def give_coins(ctx, target, amount: int, *, reason="Attribution admin"):
        """Donner des pièces à un joueur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Trouver le joueur
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                # Recherche par nom
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Obtenir ou créer le joueur
            player = await bot.db.get_or_create_player(user_id, target)
            new_coins = player.coins + amount
            
            # Mettre à jour les pièces
            await bot.db.update_player_coins(user_id, new_coins)
            
            embed = discord.Embed(
                title="✅ Pièces Attribuées",
                description=f"**{format_number(amount)} pièces** données à **{player.username}**",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Avant:** {format_number(player.coins)} pièces\n**Après:** {format_number(new_coins)} pièces\n**Raison:** {reason}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Montant invalide. Utilisez un nombre.")
        except Exception as e:
            logger.error(f"Error in givecoins: {e}")
            await ctx.send("❌ Erreur lors de l'attribution des pièces.")
    
    @bot.command(name='removecoins', aliases=['takecoins'])
    async def remove_coins(ctx, target, amount: int, *, reason="Retrait admin"):
        """Retirer des pièces à un joueur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Logique similaire à givecoins mais en soustrayant
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            player = await bot.db.get_or_create_player(user_id, target)
            new_coins = max(0, player.coins - amount)  # Ne pas aller en négatif
            
            await bot.db.update_player_coins(user_id, new_coins)
            
            embed = discord.Embed(
                title="✅ Pièces Retirées",
                description=f"**{format_number(amount)} pièces** retirées à **{player.username}**",
                color=0xe74c3c
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Avant:** {format_number(player.coins)} pièces\n**Après:** {format_number(new_coins)} pièces\n**Raison:** {reason}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Montant invalide. Utilisez un nombre.")
        except Exception as e:
            logger.error(f"Error in removecoins: {e}")
            await ctx.send("❌ Erreur lors du retrait des pièces.")
    
    @bot.command(name='giveallcoins', aliases=['distributecoins'])
    async def give_all_coins(ctx, amount: int, *, reason="Event admin"):
        """Donner des pièces à tous les joueurs - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Compter les joueurs actifs
            cursor = await bot.db.db.execute("SELECT COUNT(*) FROM players WHERE is_banned = 0")
            player_count = (await cursor.fetchone())[0]
            
            if player_count == 0:
                await ctx.send("❌ Aucun joueur actif trouvé.")
                return
            
            # Distribuer les pièces
            await bot.db.db.execute(
                "UPDATE players SET coins = coins + ? WHERE is_banned = 0",
                (amount,)
            )
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Distribution Réussie",
                description=f"**{format_number(amount)} pièces** distribuées à **{player_count:,} joueurs**",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Total distribué:** {format_number(amount * player_count)} pièces\n**Raison:** {reason}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Montant invalide. Utilisez un nombre.")
        except Exception as e:
            logger.error(f"Error in giveallcoins: {e}")
            await ctx.send("❌ Erreur lors de la distribution.")
    
    @bot.command(name='banuser', aliases=['ban'])
    async def ban_user(ctx, target, *, reason="Ban admin"):
        """Bannir un utilisateur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Bannir l'utilisateur
            await bot.db.ban_user(user_id, target)
            
            embed = discord.Embed(
                title="✅ Utilisateur Banni",
                description=f"**{target}** a été banni du système",
                color=0xe74c3c
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Utilisateur:** {target}\n**Raison:** {reason}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in banuser: {e}")
            await ctx.send("❌ Erreur lors du bannissement.")
    
    @bot.command(name='unbanuser', aliases=['unban'])
    async def unban_user(ctx, target, *, reason="Unban admin"):
        """Débannir un utilisateur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Débannir l'utilisateur
            await bot.db.unban_user(user_id)
            
            embed = discord.Embed(
                title="✅ Utilisateur Débanni",
                description=f"**{target}** a été débanni du système",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Utilisateur:** {target}\n**Raison:** {reason}",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in unbanuser: {e}")
            await ctx.send("❌ Erreur lors du débannissement.")
    
    # ═══════════════════ GESTION DES PERSONNAGES ═══════════════════
    
    @bot.command(name='createchar', aliases=['addchar', 'newchar'])
    async def create_character(ctx, name: str, rarity: str, anime: str, value: int, image_url: str = ""):
        """Créer un nouveau personnage - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Vérifier la rareté
            valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']
            if rarity not in valid_rarities:
                await ctx.send(f"❌ Rareté invalide. Utilisez: {', '.join(valid_rarities)}")
                return
            
            # Vérifier si le personnage existe
            cursor = await bot.db.db.execute(
                "SELECT id FROM characters WHERE LOWER(name) = LOWER(?)",
                (name,)
            )
            if await cursor.fetchone():
                await ctx.send(f"❌ Le personnage **{name}** existe déjà.")
                return
            
            # Créer le personnage
            final_image_url = image_url if image_url else None
            await bot.db.db.execute(
                "INSERT INTO characters (name, anime, rarity, value, image_url) VALUES (?, ?, ?, ?, ?)",
                (name, anime, rarity, value, final_image_url)
            )
            await bot.db.db.commit()
            
            # Créer automatiquement la série si elle n'existe pas
            await bot.db.auto_create_series(anime)
            
            # Si c'est un personnage Evolve, vérifier que le personnage de base existe
            craft_msg = ""
            if rarity == "Evolve":
                base_name = name.replace(" Evolve", "")
                cursor = await bot.db.db.execute(
                    "SELECT COUNT(*) FROM characters WHERE name = ? AND anime = ? AND rarity != 'Evolve'",
                    (base_name, anime)
                )
                base_exists = (await cursor.fetchone())[0] > 0
                
                if base_exists:
                    craft_msg = f"\n🔮 Recette de craft automatiquement créée: {base_name} x10 → {name}"
                else:
                    craft_msg = f"\n⚠️ Attention: Personnage de base '{base_name}' introuvable pour le craft"
            
            # Synchroniser avec le code pour persistence
            try:
                synced_count = await sync_admin_characters(bot.db)
                sync_msg = f"\n🔄 {synced_count} personnages synchronisés avec le code"
            except Exception as sync_error:
                logger.error(f"Erreur de synchronisation: {sync_error}")
                sync_msg = "\n⚠️ Synchronisation avec le code échouée"
            
            embed = discord.Embed(
                title="✅ Personnage Créé",
                description=f"**{name}** a été créé avec succès{sync_msg}{craft_msg}",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Détails",
                value=f"**Anime:** {anime}\n**Rareté:** {rarity}\n**Valeur:** {format_number(value)} pièces",
                inline=False
            )
            
            if final_image_url:
                embed.set_thumbnail(url=final_image_url)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Valeur invalide. Utilisez un nombre pour la valeur.")
        except Exception as e:
            logger.error(f"Error in createchar: {e}")
            await ctx.send("❌ Erreur lors de la création du personnage.")
    
    @bot.command(name='deletechar', aliases=['removechar'])
    async def delete_character(ctx, *, character_input: str):
        """Supprimer un personnage par nom ou ID - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Vérifier si l'input est un ID numérique
            result = None
            search_type = ""
            
            if character_input.isdigit():
                # Recherche par ID
                char_id = int(character_input)
                cursor = await bot.db.db.execute(
                    "SELECT id, name, anime FROM characters WHERE id = ?",
                    (char_id,)
                )
                result = await cursor.fetchone()
                search_type = f"ID {char_id}"
            else:
                # Recherche par nom (exacte d'abord)
                cursor = await bot.db.db.execute(
                    "SELECT id, name, anime FROM characters WHERE LOWER(name) = LOWER(?)",
                    (character_input,)
                )
                result = await cursor.fetchone()
                
                if not result:
                    # Si pas trouvé exactement, recherche partielle
                    cursor = await bot.db.db.execute(
                        "SELECT id, name, anime FROM characters WHERE name LIKE ?",
                        (f"%{character_input}%",)
                    )
                    result = await cursor.fetchone()
                search_type = f"nom '{character_input}'"
            
            if not result:
                await ctx.send(f"❌ Personnage avec {search_type} introuvable.")
                return
            
            char_id, name, anime = result
            
            # Compter les possessions
            cursor = await bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE character_id = ?",
                (char_id,)
            )
            owned_count = (await cursor.fetchone())[0]
            
            # Supprimer de l'inventaire
            await bot.db.db.execute("DELETE FROM inventory WHERE character_id = ?", (char_id,))
            
            # Supprimer le personnage
            await bot.db.db.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Personnage Supprimé",
                description=f"**{name}** (ID: {char_id}) a été supprimé du système",
                color=0xe74c3c
            )
            embed.add_field(
                name="📊 Impact",
                value=f"**Anime:** {anime}\n**Retiré de {owned_count:,} inventaires**",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in deletechar: {e}")
            await ctx.send("❌ Erreur lors de la suppression.")
    
    @bot.command(name='deletecharid', aliases=['removecharid'])
    async def delete_character_by_id(ctx, character_id: int):
        """Supprimer un personnage par ID uniquement - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Trouver le personnage par ID
            cursor = await bot.db.db.execute(
                "SELECT id, name, anime FROM characters WHERE id = ?",
                (character_id,)
            )
            result = await cursor.fetchone()
            
            if not result:
                await ctx.send(f"❌ Aucun personnage trouvé avec l'ID {character_id}.")
                return
            
            char_id, name, anime = result
            
            # Compter les possessions
            cursor = await bot.db.db.execute(
                "SELECT COUNT(*) FROM inventory WHERE character_id = ?",
                (char_id,)
            )
            owned_count = (await cursor.fetchone())[0]
            
            # Supprimer de l'inventaire
            await bot.db.db.execute("DELETE FROM inventory WHERE character_id = ?", (char_id,))
            
            # Supprimer le personnage
            await bot.db.db.execute("DELETE FROM characters WHERE id = ?", (char_id,))
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Personnage Supprimé par ID",
                description=f"**{name}** (ID: {char_id}) a été supprimé du système",
                color=0xe74c3c
            )
            embed.add_field(
                name="📊 Impact",
                value=f"**Anime:** {anime}\n**Retiré de {owned_count:,} inventaires**",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ L'ID doit être un nombre valide.")
        except Exception as e:
            logger.error(f"Error in deletecharid: {e}")
            await ctx.send("❌ Erreur lors de la suppression.")
    
    @bot.command(name='forcepull', aliases=['givepull'])
    async def force_pull(ctx, target, *, character_or_rarity: str):
        """Forcer un pull pour un joueur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Trouver le joueur
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Déterminer si c'est un personnage ou une rareté
            character = None
            valid_rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Titan', 'Fusion', 'Secret']
            
            if character_or_rarity in valid_rarities:
                # Tirer dans la rareté
                cursor = await bot.db.db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE rarity = ? ORDER BY RANDOM() LIMIT 1",
                    (character_or_rarity,)
                )
                char_data = await cursor.fetchone()
                
                if not char_data:
                    await ctx.send(f"❌ Aucun personnage de rareté **{character_or_rarity}** trouvé.")
                    return
            else:
                # Rechercher le personnage
                cursor = await bot.db.db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE LOWER(name) LIKE LOWER(?)",
                    (f"%{character_or_rarity}%",)
                )
                char_results = await cursor.fetchall()
                
                if not char_results:
                    await ctx.send(f"❌ Personnage '{character_or_rarity}' introuvable.")
                    return
                
                if len(char_results) > 1:
                    char_list = [f"**{row[1]}** ({row[2]}) - {row[3]}" for row in char_results[:5]]
                    await ctx.send(f"❌ Plusieurs personnages trouvés:\n" + "\n".join(char_list))
                    return
                
                char_data = char_results[0]
            
            # Créer l'objet Character
            from core.models import Character
            character = Character(
                id=char_data[0],
                name=char_data[1],
                anime=char_data[2],
                rarity=char_data[3],
                value=char_data[4],
                image_url=char_data[5]
            )
            
            # Ajouter à l'inventaire
            await bot.db.add_character_to_inventory(user_id, character.id)
            
            embed = discord.Embed(
                title="✅ Pull Forcé Réussi",
                description=f"**{character.name}** a été ajouté à l'inventaire de **{target}**",
                color=character.get_rarity_color()
            )
            embed.add_field(
                name=f"{character.get_rarity_emoji()} {character.name}",
                value=f"**Anime:** {character.anime}\n**Rareté:** {character.rarity}\n**Valeur:** {format_number(character.value)} pièces",
                inline=False
            )
            
            if character.image_url:
                embed.set_thumbnail(url=character.image_url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in forcepull: {e}")
            await ctx.send("❌ Erreur lors du pull forcé.")
    
    # ═══════════════════ STATISTIQUES ET INFORMATIONS ═══════════════════
    
    @bot.command(name='playerstats', aliases=['stats'])
    async def player_stats(ctx):
        """Afficher les statistiques des joueurs - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Statistiques générales
            cursor = await bot.db.db.execute("""
                SELECT 
                    COUNT(*) as total_players,
                    SUM(coins) as total_coins,
                    AVG(coins) as avg_coins,
                    MAX(coins) as max_coins,
                    SUM(total_rerolls) as total_rerolls
                FROM players
            """)
            stats = await cursor.fetchone()
            
            embed = discord.Embed(
                title="📊 Statistiques des Joueurs",
                color=0x3498db
            )
            
            embed.add_field(
                name="👥 Joueurs",
                value=f"**Total:** {stats[0]:,}\n**Actifs:** {stats[0]:,}",
                inline=True
            )
            
            embed.add_field(
                name="🪙 Économie",
                value=f"**Total:** {format_number(stats[1] or 0)} pièces\n**Moyenne:** {format_number(int(stats[2] or 0))} pièces\n**Record:** {format_number(stats[3] or 0)} pièces",
                inline=True
            )
            
            embed.add_field(
                name="🎲 Activité",
                value=f"**Total rerolls:** {stats[4] or 0:,}",
                inline=True
            )
            
            # Top 5 joueurs
            cursor = await bot.db.db.execute(
                "SELECT username, coins FROM players ORDER BY coins DESC LIMIT 5"
            )
            top_players = await cursor.fetchall()
            
            if top_players:
                top_list = []
                medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                for i, (username, coins) in enumerate(top_players):
                    top_list.append(f"{medals[i]} {username}: {format_number(coins)} pièces")
                
                embed.add_field(
                    name="🏆 Top 5 Joueurs",
                    value="\n".join(top_list),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in playerstats: {e}")
            await ctx.send("❌ Erreur lors de l'affichage des statistiques.")
    
    @bot.command(name='systeminfo', aliases=['sysinfo'])
    async def system_info(ctx):
        """Informations système - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            embed = discord.Embed(
                title="⚙️ Informations Système",
                color=0x9370DB
            )
            
            # Informations bot
            guilds = len(bot.guilds)
            total_members = sum(guild.member_count for guild in bot.guilds)
            
            embed.add_field(
                name="🤖 Bot",
                value=f"**Version:** {BotConfig.VERSION}\n**Serveurs:** {guilds:,}\n**Membres:** {total_members:,}\n**Latence:** {round(bot.latency * 1000)}ms",
                inline=True
            )
            
            # Statistiques DB
            cursor = await bot.db.db.execute("SELECT COUNT(*) FROM characters")
            char_count = (await cursor.fetchone())[0]
            
            cursor = await bot.db.db.execute("SELECT COUNT(*) FROM players")
            player_count = (await cursor.fetchone())[0]
            
            cursor = await bot.db.db.execute("SELECT COUNT(*) FROM inventory")
            inv_count = (await cursor.fetchone())[0]
            
            embed.add_field(
                name="🗃️ Base de Données",
                value=f"**Personnages:** {char_count:,}\n**Joueurs:** {player_count:,}\n**Inventaires:** {inv_count:,}",
                inline=True
            )
            
            # Configuration
            embed.add_field(
                name="⚙️ Configuration",
                value=f"**Préfixe:** {BotConfig.COMMAND_PREFIX}\n**Coût reroll:** {BotConfig.REROLL_COST}\n**Cooldown:** {BotConfig.REROLL_COOLDOWN}s",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in systeminfo: {e}")
            await ctx.send("❌ Erreur lors de l'affichage des informations système.")
    
    # ═══════════════════ UTILITAIRES ═══════════════════
    
    @bot.command(name='resetplayer', aliases=['resetuser'])
    async def reset_player(ctx, target, confirm: str = None):
        """Reset complet d'un joueur - Admin seulement - DANGER"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        if confirm != "CONFIRM":
            await ctx.send("❌ Pour confirmer, utilisez: `!resetplayer <joueur> CONFIRM`")
            return
        
        try:
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Reset complet
            await bot.db.db.execute(
                "UPDATE players SET coins = ?, total_rerolls = 0, last_reroll = NULL, last_daily = NULL WHERE user_id = ?",
                (BotConfig.STARTING_COINS, user_id)
            )
            
            await bot.db.db.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
            await bot.db.db.execute("DELETE FROM player_achievements WHERE user_id = ?", (user_id,))
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Joueur Reset",
                description=f"**{target}** a été complètement reset",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Actions",
                value=f"• Pièces: {BotConfig.STARTING_COINS:,}\n• Inventaire vidé\n• Achievements supprimés\n• Statistiques reset",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in resetplayer: {e}")
            await ctx.send("❌ Erreur lors du reset.")
    
    @bot.command(name='viewprofile', aliases=['profile'])
    async def view_profile(ctx, target):
        """Voir le profil détaillé d'un joueur - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            user_id = None
            if target.startswith('<@') and target.endswith('>'):
                user_id = int(target[2:-1].replace('!', ''))
            elif target.isdigit():
                user_id = int(target)
            else:
                cursor = await bot.db.db.execute(
                    "SELECT user_id FROM players WHERE LOWER(username) LIKE LOWER(?)",
                    (f"%{target}%",)
                )
                result = await cursor.fetchone()
                if result:
                    user_id = result[0]
            
            if not user_id:
                await ctx.send(f"❌ Joueur '{target}' introuvable.")
                return
            
            # Récupérer les infos du joueur
            cursor = await bot.db.db.execute(
                "SELECT user_id, username, coins, total_rerolls, last_reroll, last_daily, is_banned FROM players WHERE user_id = ?",
                (user_id,)
            )
            player_data = await cursor.fetchone()
            
            if not player_data:
                await ctx.send(f"❌ Aucune donnée trouvée pour '{target}'.")
                return
            
            user_id, username, coins, rerolls, last_reroll, last_daily, is_banned = player_data
            
            embed = discord.Embed(
                title=f"👤 Profil de {username}",
                color=0xe74c3c if is_banned else 0x27ae60
            )
            
            # Informations de base
            status = "🚫 Banni" if is_banned else "✅ Actif"
            embed.add_field(
                name="📊 Informations",
                value=f"**ID:** {user_id}\n**Statut:** {status}\n**Pièces:** {format_number(coins)}\n**Rerolls:** {rerolls:,}",
                inline=False
            )
            
            # Statistiques de collection
            cursor = await bot.db.db.execute(
                "SELECT COUNT(*), COUNT(DISTINCT character_id) FROM inventory WHERE user_id = ?",
                (user_id,)
            )
            inv_stats = await cursor.fetchone()
            total_items, unique_chars = inv_stats
            
            embed.add_field(
                name="🎴 Collection",
                value=f"**Total objets:** {total_items:,}\n**Personnages uniques:** {unique_chars:,}",
                inline=True
            )
            
            # Activité
            embed.add_field(
                name="⏰ Activité",
                value=f"**Dernier reroll:** {last_reroll or 'Jamais'}\n**Dernier daily:** {last_daily or 'Jamais'}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in viewprofile: {e}")
            await ctx.send("❌ Erreur lors de l'affichage du profil.")
    
    # Character selection view for addimage command
    class CharacterSelectionView(discord.ui.View):
        def __init__(self, characters, image_url, user_id):
            super().__init__(timeout=60)
            self.characters = characters
            self.image_url = image_url
            self.user_id = user_id
            
            # Add buttons for each character (max 10)
            for i, char in enumerate(characters[:10]):
                button = discord.ui.Button(
                    label=f"{i+1}. {char[1]} ({char[2]})",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"select_char_{i}"
                )
                button.callback = self.create_callback(i)
                self.add_item(button)
        
        def create_callback(self, index):
            async def callback(interaction):
                if interaction.user.id != self.user_id:
                    await interaction.response.send_message("❌ Vous ne pouvez pas utiliser cette sélection.", ephemeral=True)
                    return
                
                char_id, name, anime = self.characters[index]
                
                try:
                    # Update the image
                    await bot.db.db.execute(
                        "UPDATE characters SET image_url = ? WHERE id = ?",
                        (self.image_url, char_id)
                    )
                    await bot.db.db.commit()
                    
                    # Confirmation
                    embed = discord.Embed(
                        title="✅ Image Mise à Jour",
                        description=f"L'image de **{name}** ({anime}) a été mise à jour avec succès!",
                        color=0x27ae60
                    )
                    embed.set_thumbnail(url=self.image_url)
                    
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                except Exception as e:
                    logger.error(f"Error updating image: {e}")
                    await interaction.response.send_message("❌ Erreur lors de la mise à jour de l'image.", ephemeral=True)
            
            return callback
        
        async def on_timeout(self):
            # Disable all buttons when timeout
            for item in self.children:
                item.disabled = True

    @bot.command(name='addimage', aliases=['setimage'])
    async def add_image(ctx, character_name: str, image_url: str):
        """Ajouter/modifier l'image d'un personnage - Admin seulement"""
        if not BotConfig.is_admin(ctx.author.id):
            await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
            return
        
        try:
            # Rechercher le personnage
            cursor = await bot.db.db.execute(
                "SELECT id, name, anime FROM characters WHERE LOWER(name) LIKE LOWER(?)",
                (f"%{character_name}%",)
            )
            results = await cursor.fetchall()
            
            if not results:
                await ctx.send(f"❌ Personnage '{character_name}' introuvable.")
                return
            
            if len(results) > 1:
                # Multiple characters found - use button selection
                embed = discord.Embed(
                    title="🔍 Plusieurs personnages trouvés",
                    description="Cliquez sur le bouton correspondant au personnage que vous voulez modifier:",
                    color=0x3498db
                )
                
                # Add character list to embed for reference
                char_list = "\n".join([f"**{i+1}.** {char[1]} ({char[2]})" for i, char in enumerate(results[:10])])
                embed.add_field(name="Personnages disponibles:", value=char_list, inline=False)
                
                view = CharacterSelectionView(results, image_url, ctx.author.id)
                await ctx.send(embed=embed, view=view)
                return
            
            # Single character found
            char_id, name, anime = results[0]
            
            # Update the image
            await bot.db.db.execute(
                "UPDATE characters SET image_url = ? WHERE id = ?",
                (image_url, char_id)
            )
            await bot.db.db.commit()
            
            embed = discord.Embed(
                title="✅ Image Mise à Jour",
                description=f"L'image de **{name}** a été mise à jour",
                color=0x27ae60
            )
            embed.add_field(
                name="📊 Info",
                value=f"**Personnage:** {name} ({anime})",
                inline=False
            )
            embed.set_thumbnail(url=image_url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in addimage: {e}")
            await ctx.send("❌ Erreur lors de la mise à jour de l'image.")
    
    logger.info("Legacy admin commands setup completed")