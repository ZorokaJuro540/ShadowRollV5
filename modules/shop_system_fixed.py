"""
Shadow Roll Bot - Shop System Complet et Fonctionnel
Système de boutique entièrement repensé avec gestion d'erreurs robuste
"""

import discord
from discord.ext import commands
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from core.config import BotConfig

logger = logging.getLogger(__name__)

# Fonction de style locale pour éviter les erreurs d'import
def apply_font_style(text, style):
    """Fonction de fallback pour le style de texte"""
    return text

# Fallback pour style_main_title et autres fonctions de style
def style_main_title():
    return "🌑 ═══════〔 S H A D O W   R O L L 〕═══════ 🌑"

def style_section(text, emoji=""):
    return f"{emoji} ═══〔 {text} 〕═══ {emoji}"

def style_bold(text):
    return f"**{text}**"

class ShopDatabase:
    """Gestionnaire de base de données pour la boutique"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db.db
    
    async def initialize_shop_tables(self):
        """Initialiser toutes les tables nécessaires pour la boutique"""
        try:
            # Table des articles de boutique (utilise la table corrigée)
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS shop_items_fixed (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    effect_type TEXT,
                    effect_value TEXT,
                    duration INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des achats de joueurs
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS player_purchases_fixed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    purchase_price INTEGER NOT NULL,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des potions du joueur
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS player_potions_fixed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    potion_name TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    duration_minutes INTEGER DEFAULT 60,
                    quantity INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des buffs temporaires
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS temporary_buffs_fixed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    buff_type TEXT NOT NULL,
                    buff_value REAL DEFAULT 1.0,
                    expires_at INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des invocations gratuites
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS free_rolls_fixed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    rolls_remaining INTEGER DEFAULT 0,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des garanties de rareté
            await self.db.execute('''
                CREATE TABLE IF NOT EXISTS guaranteed_rarities_fixed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    rarity TEXT NOT NULL,
                    uses_remaining INTEGER DEFAULT 1,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await self.db.commit()
            logger.info("Tables de la boutique initialisées avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des tables: {e}")
    
    async def add_default_shop_items(self):
        """Ajouter les articles par défaut à la boutique"""
        try:
            # Vérifier si des articles existent déjà
            cursor = await self.db.execute("SELECT COUNT(*) FROM shop_items_fixed")
            count = (await cursor.fetchone())[0]
            
            if count > 0:
                logger.info("Articles de boutique déjà présents")
                return
            
            # Articles par défaut
            default_items = [
                (1, "🧪 Potion de Chance", "Augmente les chances de rareté pendant 1h", 1500, "potion", "luck_boost", "1.5", 3600),
                (2, "🪙 Multiplicateur Pièces", "Double les gains de pièces pendant 1h", 2000, "boost", "coin_multiplier", "2.0", 3600),
                (3, "⚡ Reset Cooldown", "Supprime tous les cooldowns actifs", 1000, "utility", "cooldown_reset", "instant", 0),
                (4, "🎲 Pack 5 Invocations", "Accorde 5 invocations gratuites", 3000, "pack", "free_rolls", "5", 0),
                (5, "🔮 Garantie Épique", "Prochaine invocation garantie Epic+", 4000, "guarantee", "epic_guarantee", "Epic", 0),
                (6, "💎 Garantie Légendaire", "Prochaine invocation garantie Legendary+", 7500, "guarantee", "legendary_guarantee", "Legendary", 0),
                (7, "🌟 Mega Pack", "10 invocations + bonus chance", 8000, "pack", "mega_pack", "10", 0),
                (8, "🔥 Boost Craft", "Réduit exigences craft de 50%", 5000, "boost", "craft_discount", "0.5", 7200)
            ]
            
            for item in default_items:
                await self.db.execute('''
                    INSERT OR IGNORE INTO shop_items_fixed 
                    (id, name, description, price, category, effect_type, effect_value, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', item)
            
            await self.db.commit()
            logger.info("Articles par défaut ajoutés à la boutique")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des articles par défaut: {e}")
    
    async def get_shop_items(self) -> List[Dict]:
        """Récupérer tous les articles actifs de la boutique"""
        try:
            cursor = await self.db.execute('''
                SELECT id, name, description, price, category, effect_type, effect_value, duration
                FROM shop_items_fixed 
                WHERE is_active = 1 
                ORDER BY price ASC
            ''')
            rows = await cursor.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3],
                    'category': row[4],
                    'effect_type': row[5],
                    'effect_value': row[6],
                    'duration': row[7] or 0
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des articles: {e}")
            return []
    
    async def record_purchase(self, user_id: int, item_id: int, price: int, quantity: int = 1):
        """Enregistrer un achat"""
        try:
            await self.db.execute('''
                INSERT INTO player_purchases_fixed (user_id, item_id, quantity, purchase_price)
                VALUES (?, ?, ?, ?)
            ''', (user_id, item_id, quantity, price))
            await self.db.commit()
            logger.info(f"Achat enregistré: User {user_id}, Item {item_id}, Prix {price}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'achat: {e}")
    
    async def add_potion_to_player(self, user_id: int, potion_name: str, effect_type: str, duration: int):
        """Ajouter une potion à l'inventaire du joueur"""
        try:
            # Vérifier si le joueur a déjà cette potion
            cursor = await self.db.execute('''
                SELECT quantity FROM player_potions_fixed 
                WHERE user_id = ? AND potion_name = ? AND effect_type = ?
            ''', (user_id, potion_name, effect_type))
            existing = await cursor.fetchone()
            
            if existing:
                # Augmenter la quantité
                await self.db.execute('''
                    UPDATE player_potions_fixed 
                    SET quantity = quantity + 1 
                    WHERE user_id = ? AND potion_name = ? AND effect_type = ?
                ''', (user_id, potion_name, effect_type))
            else:
                # Ajouter nouvelle potion
                await self.db.execute('''
                    INSERT INTO player_potions_fixed (user_id, potion_name, effect_type, duration_minutes)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, potion_name, effect_type, duration // 60))
            
            await self.db.commit()
            logger.info(f"Potion ajoutée: {potion_name} pour user {user_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de potion: {e}")
    
    async def add_temporary_buff(self, user_id: int, buff_type: str, buff_value: float, duration: int):
        """Ajouter un buff temporaire"""
        try:
            expires_at = int(datetime.now().timestamp()) + duration
            
            await self.db.execute('''
                INSERT OR REPLACE INTO temporary_buffs_fixed 
                (user_id, buff_type, buff_value, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, buff_type, buff_value, expires_at))
            await self.db.commit()
            logger.info(f"Buff temporaire ajouté: {buff_type} pour user {user_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de buff: {e}")
    
    async def add_free_rolls(self, user_id: int, amount: int):
        """Ajouter des invocations gratuites"""
        try:
            cursor = await self.db.execute('''
                SELECT rolls_remaining FROM free_rolls_fixed WHERE user_id = ?
            ''', (user_id,))
            existing = await cursor.fetchone()
            
            if existing:
                await self.db.execute('''
                    UPDATE free_rolls_fixed 
                    SET rolls_remaining = rolls_remaining + ?
                    WHERE user_id = ?
                ''', (amount, user_id))
            else:
                await self.db.execute('''
                    INSERT INTO free_rolls_fixed (user_id, rolls_remaining)
                    VALUES (?, ?)
                ''', (user_id, amount))
            
            await self.db.commit()
            logger.info(f"Invocations gratuites ajoutées: {amount} pour user {user_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'invocations gratuites: {e}")
    
    async def add_guaranteed_rarity(self, user_id: int, rarity: str):
        """Ajouter une garantie de rareté"""
        try:
            await self.db.execute('''
                INSERT INTO guaranteed_rarities_fixed (user_id, rarity)
                VALUES (?, ?)
            ''', (user_id, rarity))
            await self.db.commit()
            logger.info(f"Garantie de rareté ajoutée: {rarity} pour user {user_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de garantie: {e}")

class FixedShopView(discord.ui.View):
    """Interface de boutique unifiée: achat ET vente"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.shop_db = ShopDatabase(bot)
        self.current_page = 1
        self.items_per_page = 6
        self.mode = "buy"  # "buy" ou "sell"
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_shop_embed(self) -> discord.Embed:
        """Créer l'embed de la boutique unifiée"""
        try:
            # Obtenir les données du joueur
            player_data = await self.bot.db.get_player_data(self.user_id)
            if not player_data:
                player_data = {'coins': 0}
            
            if self.mode == "buy":
                return await self.create_buy_embed(player_data)
            else:
                return await self.create_sell_embed(player_data)
                
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger la boutique.",
                color=0xff0000
            )
    
    async def create_buy_embed(self, player_data) -> discord.Embed:
        """Créer l'embed d'achat"""
        try:
            # Obtenir les articles de la boutique
            all_items = await self.shop_db.get_shop_items()
            
            # Calculer la pagination
            total_pages = max(1, (len(all_items) + self.items_per_page - 1) // self.items_per_page)
            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = min(start_idx + self.items_per_page, len(all_items))
            page_items = all_items[start_idx:end_idx]
            
            # Créer l'embed avec un design moderne et attractif
            embed = discord.Embed(
                title="🛍️ SHADOW ROLL • BOUTIQUE PREMIUM",
                description=f"""╔═══════════════════════════════════════════════════════════╗
║                    ✨ COLLECTION EXCLUSIVE ✨                    ║
╠═══════════════════════════════════════════════════════════╣
║  🌟 Objets Légendaires • Potions Mystiques • Boosts Divins  ║
╚═══════════════════════════════════════════════════════════╝

💎 **Votre Fortune :** `{player_data.get('coins', 0):,}` 🪙 Shadow Coins
🎯 **Mode :** Acquisition d'objets premium
🔮 **Statut :** Boutique ouverte • Articles limités""",
                color=0x7b2cbf
            )
            
            # Afficher les articles avec un design moderne
            if not page_items:
                embed.add_field(
                    name="🚫 Boutique Temporairement Fermée",
                    value="```css\n[Aucun article disponible]\n```",
                    inline=False
                )
            else:
                items_text = ""
                emoji_list = ["🔥", "⚡", "🌟", "💎", "🎭", "🔮", "⭐", "🌈"]
                
                for i, item in enumerate(page_items, 1):
                    price = item['price']
                    emoji = emoji_list[(i-1) % len(emoji_list)]
                    
                    # Créer un affichage stylé pour chaque article
                    items_text += f"╭─ {emoji} **{item['name']}**\n"
                    items_text += f"├ 💰 **{price:,}** 🪙 Shadow Coins\n"
                    items_text += f"├ 📖 {item['description']}\n"
                    
                    # Afficher la durée si applicable
                    if item['duration'] > 0:
                        hours = item['duration'] // 3600
                        minutes = (item['duration'] % 3600) // 60
                        if hours > 0:
                            items_text += f"├ ⏰ Durée: **{hours}h{minutes:02d}m**\n"
                        else:
                            items_text += f"├ ⏰ Durée: **{minutes}m**\n"
                    
                    items_text += f"╰─ 🎯 **Numéro: {i}**\n\n"
                
                embed.add_field(
                    name="🛍️ Articles Disponibles",
                    value=items_text,
                    inline=False
                )
                
                # Information de pagination stylée
                embed.add_field(
                    name="📚 Navigation Boutique",
                    value=f"```ini\n[Page {self.current_page}/{total_pages}]\n[{len(all_items)} Articles Premium]```",
                    inline=True
                )
            
            # Instructions d'achat modernes
            embed.add_field(
                name="🎯 Guide d'Achat",
                value="```css\n┌─ Étape 1: Cliquez sur '🛒 Acheter'\n├─ Étape 2: Entrez le numéro de l'article\n└─ Étape 3: Confirmez votre achat premium```",
                inline=False
            )
            
            # Footer élégant
            embed.set_footer(
                text="✨ Shadow Roll Premium Store",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'embed d'achat: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger les articles.",
                color=0xff0000
            )
    
    async def create_sell_embed(self, player_data) -> discord.Embed:
        """Créer l'embed de vente"""
        try:
            # Créer l'embed avec un design moderne et attractif
            embed = discord.Embed(
                title="💰 SHADOW ROLL • MARCHÉ PREMIUM",
                description=f"""╔═══════════════════════════════════════════════════════════╗
║                    💎 VENTE COLLECTION PREMIUM 💎                    ║
╠═══════════════════════════════════════════════════════════╣
║  🌟 Transformez vos doubles en fortune • Prix garantis  ║
╚═══════════════════════════════════════════════════════════╝

🏦 **Votre Fortune :** `{player_data.get('coins', 0):,}` 🪙 Shadow Coins
🎯 **Mode :** Vente de personnages premium
💵 **Taux :** 70% de la valeur originale garantie""",
                color=0x2ecc71
            )
            
            # Obtenir l'inventaire du joueur
            inventory = await self.bot.db.get_user_inventory(self.user_id, limit=50)
            
            if not inventory:
                embed.add_field(
                    name="📦 Inventaire Vide",
                    value="Aucun personnage à vendre.",
                    inline=False
                )
            else:
                # Grouper par rareté et compter les doublons
                rarity_groups = {}
                character_counts = {}
                total_value = 0
                
                for item in inventory:
                    rarity = item.get('rarity', 'Common')
                    char_name = item.get('name', 'Unknown')
                    
                    # Calculer la valeur de vente (70% de la valeur originale)
                    original_value = item.get('value', 0)
                    sell_value = int(original_value * 0.7)
                    total_value += sell_value
                    
                    # Créer une clé unique pour chaque personnage
                    char_key = f"{char_name}_{rarity}"
                    
                    if char_key not in character_counts:
                        character_counts[char_key] = {
                            'name': char_name,
                            'rarity': rarity,
                            'sell_value': sell_value,
                            'count': 0
                        }
                    
                    character_counts[char_key]['count'] += 1
                
                # Regrouper par rareté avec les comptes
                for char_key, char_data in character_counts.items():
                    rarity = char_data['rarity']
                    if rarity not in rarity_groups:
                        rarity_groups[rarity] = []
                    rarity_groups[rarity].append(char_data)
                
                # Afficher l'inventaire groupé
                inventory_text = ""
                for rarity in ['Secret', 'Fusion', 'Titan', 'Evolve', 'Mythic', 'Legendary', 'Epic', 'Rare', 'Common']:
                    if rarity not in rarity_groups:
                        continue
                        
                    items = rarity_groups[rarity]
                    rarity_color = BotConfig.RARITY_COLORS.get(rarity, 0x808080)
                    
                    if rarity_color == 0xff0000:  # Red
                        color_code = "\u001b[1;31m"
                    elif rarity_color == 0xffa500:  # Orange/Yellow
                        color_code = "\u001b[1;33m"
                    elif rarity_color == 0xa335ee:  # Purple
                        color_code = "\u001b[1;35m"
                    elif rarity_color == 0x0070dd:  # Blue
                        color_code = "\u001b[1;34m"
                    elif rarity_color == 0x00ff00:  # Green
                        color_code = "\u001b[1;32m"
                    elif rarity_color == 0xffffff:  # White
                        color_code = "\u001b[1;37m"
                    elif rarity_color == 0xff1493:  # Pink
                        color_code = "\u001b[1;35m"
                    elif rarity_color == 0x000000:  # Black
                        color_code = "\u001b[1;30m"
                    else:
                        color_code = "\u001b[1;36m"  # Cyan default
                    
                    rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                    inventory_text += f"{color_code}{rarity_emoji} {rarity} ({len(items)})\u001b[0m\n"
                    
                    # Afficher max 3 personnages par rareté avec compteurs
                    for item in items[:3]:
                        name = item.get('name', 'Unknown')
                        sell_value = item.get('sell_value', 0)
                        count = item.get('count', 1)
                        
                        if count > 1:
                            inventory_text += f"   • {name} x{count} - {sell_value:,} SC chacun\n"
                        else:
                            inventory_text += f"   • {name} - {sell_value:,} SC\n"
                    
                    if len(items) > 3:
                        inventory_text += f"   ... et {len(items) - 3} autres\n"
                    inventory_text += "\n"
                
                embed.add_field(
                    name=f"🎒 {apply_font_style('VOTRE INVENTAIRE', 'section')}",
                    value=f"```ansi\n{inventory_text}```",
                    inline=False
                )
                
                # Valeur totale potentielle
                embed.add_field(
                    name="💎 Valeur Totale de l'Inventaire",
                    value=f"```ansi\n\u001b[1;32m{total_value:,}\u001b[0m Shadow Coins (prix de vente)```",
                    inline=False
                )
            
            # Instructions de vente
            embed.add_field(
                name="🪙 Comment Vendre",
                value="```\n1. Cliquez sur '🪙 Vendre'\n2. Entrez le nom du personnage\n3. Confirmez la vente\n```",
                inline=False
            )
            
            embed.set_footer(
                text=f"{apply_font_style('SHADOW ROLL SHOP', 'serif')}",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'embed de vente: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger l'inventaire.",
                color=0xff0000
            )
    
    async def process_purchase(self, item: Dict, user_id: int) -> bool:
        """Traiter l'achat d'un article"""
        try:
            # Enregistrer l'achat
            await self.shop_db.record_purchase(user_id, item['id'], item['price'])
            
            # Appliquer l'effet selon le type
            effect_type = item['effect_type']
            effect_value = item['effect_value']
            duration = item.get('duration', 0)
            
            if effect_type == 'luck_boost':
                # Ajouter buff de chance
                await self.shop_db.add_temporary_buff(user_id, 'luck_boost', float(effect_value), duration)
                await self.shop_db.add_potion_to_player(user_id, item['name'], effect_type, duration)
                
            elif effect_type == 'coin_multiplier':
                # Ajouter multiplicateur de pièces
                await self.shop_db.add_temporary_buff(user_id, 'coin_multiplier', float(effect_value), duration)
                await self.shop_db.add_potion_to_player(user_id, item['name'], effect_type, duration)
                
            elif effect_type == 'cooldown_reset':
                # Reset cooldowns (effet instantané)
                try:
                    await self.bot.db.reset_all_cooldowns(user_id)
                except:
                    # Si la méthode n'existe pas, ignorer silencieusement
                    pass
                
            elif effect_type == 'free_rolls':
                # Ajouter invocations gratuites
                await self.shop_db.add_free_rolls(user_id, int(effect_value))
                
            elif effect_type == 'epic_guarantee' or effect_type == 'legendary_guarantee':
                # Ajouter garantie de rareté
                rarity = effect_value  # 'Epic' ou 'Legendary'
                await self.shop_db.add_guaranteed_rarity(user_id, rarity)
                
            elif effect_type == 'mega_pack':
                # Combo pack
                await self.shop_db.add_free_rolls(user_id, int(effect_value))
                await self.shop_db.add_temporary_buff(user_id, 'luck_boost', 1.5, 1800)  # 30 min
                
            elif effect_type == 'craft_discount':
                # Réduction craft
                await self.shop_db.add_temporary_buff(user_id, 'craft_discount', float(effect_value), duration)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'achat: {e}")
            return False
    
    # Boutons de mode
    @discord.ui.button(label='🛒 Mode Achat', style=discord.ButtonStyle.success, row=0)
    async def buy_mode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mode = "buy"
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🪙 Mode Vente', style=discord.ButtonStyle.danger, row=0)
    async def sell_mode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mode = "sell"
        self.current_page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='◀️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("❌ Vous êtes déjà sur la première page.", ephemeral=True)
    
    @discord.ui.button(label='▶️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode == "buy":
            all_items = await self.shop_db.get_shop_items()
            total_pages = max(1, (len(all_items) + self.items_per_page - 1) // self.items_per_page)
            
            if self.current_page < total_pages:
                self.current_page += 1
                await interaction.response.defer()
                embed = await self.create_shop_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Vous êtes déjà sur la dernière page.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Pagination non disponible en mode vente.", ephemeral=True)
    
    @discord.ui.button(label='🔄 Actualiser', style=discord.ButtonStyle.primary, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    # Boutons d'action
    @discord.ui.button(label='🛍️ Acheter Article', style=discord.ButtonStyle.success, row=1)
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode != "buy":
            await interaction.response.send_message("❌ Basculez en mode achat pour acheter des articles.", ephemeral=True)
            return
        await interaction.response.send_modal(PurchaseModal(self.bot, self.user_id, self))
    
    @discord.ui.button(label='🪙 Vendre Personnage', style=discord.ButtonStyle.danger, row=1)
    async def sell_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.mode != "sell":
            await interaction.response.send_message("❌ Basculez en mode vente pour vendre des personnages.", ephemeral=True)
            return
        await interaction.response.send_modal(SellCharacterModal(self.bot, self.user_id, self))
    
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.danger, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

class PurchaseModal(discord.ui.Modal):
    """Modal d'achat d'articles"""
    
    def __init__(self, bot, user_id: int, shop_view: FixedShopView):
        super().__init__(title="🛒 Acheter un Article")
        self.bot = bot
        self.user_id = user_id
        self.shop_view = shop_view
        
        self.item_number = discord.ui.TextInput(
            label="Numéro de l'article",
            placeholder="Entrez le numéro affiché (ex: 1, 2, 3...)",
            min_length=1,
            max_length=2,
            required=True
        )
        self.add_item(self.item_number)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Valider l'entrée
            try:
                selection = int(self.item_number.value)
            except ValueError:
                await interaction.response.send_message(
                    "❌ Veuillez entrer un numéro valide!", 
                    ephemeral=True
                )
                return
            
            # Obtenir les articles de la page actuelle
            all_items = await self.shop_view.shop_db.get_shop_items()
            start_idx = (self.shop_view.current_page - 1) * self.shop_view.items_per_page
            end_idx = min(start_idx + self.shop_view.items_per_page, len(all_items))
            page_items = all_items[start_idx:end_idx]
            
            if selection < 1 or selection > len(page_items):
                await interaction.response.send_message(
                    f"❌ Numéro invalide! Choisissez entre 1 et {len(page_items)}", 
                    ephemeral=True
                )
                return
            
            selected_item = page_items[selection - 1]
            
            # Vérifier le solde du joueur
            player_data = await self.bot.db.get_player_data(self.user_id)
            if not player_data:
                await interaction.response.send_message(
                    "❌ Impossible de récupérer vos données!", 
                    ephemeral=True
                )
                return
            
            player_coins = player_data.get('coins', 0)
            item_price = selected_item['price']
            
            if player_coins < item_price:
                deficit = item_price - player_coins
                await interaction.response.send_message(
                    f"❌ **Fonds insuffisants!**\n"
                    f"🪙 Prix: {item_price:,} SC\n"
                    f"🪙 Votre solde: {player_coins:,} SC\n"
                    f"🪙 Il vous manque: {deficit:,} SC",
                    ephemeral=True
                )
                return
            
            # Traiter l'achat
            purchase_success = await self.shop_view.process_purchase(selected_item, self.user_id)
            
            if purchase_success:
                # Déduire le coût
                new_balance = player_coins - item_price
                await self.bot.db.update_player_coins(self.user_id, new_balance)
                
                # Confirmation d'achat
                embed = discord.Embed(
                    title="✅ Achat Réussi!",
                    description=f"**{selected_item['name']}** acheté avec succès!",
                    color=0x00ff00
                )
                embed.add_field(
                    name="🪙 Transaction",
                    value=f"Prix: {item_price:,} SC\nNouveau solde: {new_balance:,} SC",
                    inline=False
                )
                embed.add_field(
                    name="📦 Article",
                    value=selected_item['description'],
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Mettre à jour l'affichage de la boutique
                try:
                    updated_embed = await self.shop_view.create_shop_embed()
                    await interaction.edit_original_response(embed=updated_embed, view=self.shop_view)
                except:
                    pass  # Ignorer si l'édition échoue
                
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors du traitement de l'achat. Veuillez réessayer.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erreur dans le modal d'achat: {e}")
            await interaction.response.send_message(
                "❌ Une erreur inattendue s'est produite.",
                ephemeral=True
            )

class SellCharacterModal(discord.ui.Modal):
    """Modal pour vendre des personnages"""
    
    def __init__(self, bot, user_id: int, shop_view):
        super().__init__(title="🪙 Vendre un Personnage")
        self.bot = bot
        self.user_id = user_id
        self.shop_view = shop_view
        
        self.character_name = discord.ui.TextInput(
            label="Nom du personnage",
            placeholder="Entrez le nom exact du personnage à vendre",
            min_length=1,
            max_length=100,
            required=True
        )
        self.add_item(self.character_name)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            character_name = self.character_name.value.strip()
            
            # Obtenir l'inventaire du joueur
            inventory = await self.bot.db.get_user_inventory(self.user_id)
            
            if not inventory:
                await interaction.response.send_message(
                    "❌ Votre inventaire est vide!",
                    ephemeral=True
                )
                return
            
            # Chercher le personnage (recherche exacte puis partielle)
            character_found = None
            for item in inventory:
                if item.get('name', '').lower() == character_name.lower():
                    character_found = item
                    break
            
            # Si pas trouvé, recherche partielle
            if not character_found:
                for item in inventory:
                    if character_name.lower() in item.get('name', '').lower():
                        character_found = item
                        break
            
            if not character_found:
                await interaction.response.send_message(
                    f"❌ Personnage '{character_name}' non trouvé dans votre inventaire.",
                    ephemeral=True
                )
                return
            
            # Calculer le prix de vente (70% de la valeur originale)
            original_value = character_found.get('value', 0)
            sell_price = int(original_value * 0.7)
            
            if sell_price <= 0:
                await interaction.response.send_message(
                    f"❌ Ce personnage n'a aucune valeur de vente.",
                    ephemeral=True
                )
                return
            
            # Créer l'embed de confirmation
            rarity = character_found.get('rarity', 'Common')
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
            rarity_color = BotConfig.RARITY_COLORS.get(rarity, 0x808080)
            
            embed = discord.Embed(
                title="🪙 Confirmer la Vente",
                description=f"Voulez-vous vraiment vendre ce personnage?",
                color=rarity_color
            )
            
            embed.add_field(
                name=f"{rarity_emoji} Personnage",
                value=f"**{character_found['name']}**\nRareté: {rarity}",
                inline=True
            )
            
            embed.add_field(
                name="🪙 Prix de Vente",
                value=f"**{sell_price:,}** Shadow Coins",
                inline=True
            )
            
            embed.add_field(
                name="📊 Détails",
                value=f"Valeur originale: {original_value:,} SC\nPourcentage de vente: 70%",
                inline=False
            )
            
            # Créer les boutons de confirmation
            view = SellConfirmationView(self.bot, self.user_id, character_found, sell_price, self.shop_view)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans le modal de vente: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la préparation de la vente.",
                ephemeral=True
            )

class SellConfirmationView(discord.ui.View):
    """Vue de confirmation pour la vente de personnages"""
    
    def __init__(self, bot, user_id: int, character: dict, sell_price: int, shop_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.character = character
        self.sell_price = sell_price
        self.shop_view = shop_view
    
    @discord.ui.button(label='✅ Confirmer la Vente', style=discord.ButtonStyle.success)
    async def confirm_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Vérifier que le joueur possède toujours le personnage
            inventory = await self.bot.db.get_user_inventory(self.user_id)
            character_still_owned = False
            
            for item in inventory:
                if (item.get('name') == self.character.get('name') and 
                    item.get('rarity') == self.character.get('rarity')):
                    character_still_owned = True
                    break
            
            if not character_still_owned:
                await interaction.response.send_message(
                    "❌ Vous ne possédez plus ce personnage!",
                    ephemeral=True
                )
                return
            
            # Trouver l'ID d'inventaire du personnage à vendre
            inventory = await self.bot.db.get_user_inventory(self.user_id)
            inventory_item_id = None
            
            for item in inventory:
                if (item.get('name') == self.character.get('name') and 
                    item.get('rarity') == self.character.get('rarity')):
                    inventory_item_id = item.get('inventory_id')
                    break
            
            if not inventory_item_id:
                await interaction.response.send_message(
                    "❌ Impossible de trouver ce personnage dans votre inventaire!",
                    ephemeral=True
                )
                return
            
            # Effectuer la vente avec les bons paramètres
            success, message, actual_sell_price = await self.bot.db.sell_character(
                self.user_id, 
                inventory_item_id
            )
            
            if success:
                # Créer l'embed de succès
                embed = discord.Embed(
                    title="✅ Vente Réussie!",
                    description=f"**{self.character['name']}** vendu avec succès!",
                    color=0x00ff00
                )
                embed.add_field(
                    name="🪙 Gains",
                    value=f"{actual_sell_price:,} Shadow Coins ajoutés à votre solde",
                    inline=False
                )
                embed.add_field(
                    name="📋 Message",
                    value=message,
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
                # Mettre à jour l'affichage de la boutique
                try:
                    self.shop_view.mode = "sell"  # Rester en mode vente
                    updated_embed = await self.shop_view.create_shop_embed()
                    await interaction.edit_original_response(embed=updated_embed, view=self.shop_view)
                except:
                    pass  # Ignorer si l'édition échoue
                
            else:
                await interaction.response.send_message(
                    f"❌ Erreur lors de la vente: {message}",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la confirmation de vente: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite lors de la vente.",
                ephemeral=True
            )
    
    @discord.ui.button(label='❌ Annuler', style=discord.ButtonStyle.secondary)
    async def cancel_sell(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Vente Annulée",
            description="La vente a été annulée.",
            color=0x808080
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Fonction d'initialisation
async def setup_fixed_shop_system(bot):
    """Initialiser le système de boutique corrigé"""
    try:
        shop_db = ShopDatabase(bot)
        await shop_db.initialize_shop_tables()
        await shop_db.add_default_shop_items()
        
        logger.info("Système de boutique corrigé initialisé avec succès")
        return shop_db
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du shop corrigé: {e}")
        return None

# Fonction pour créer la vue de boutique
async def create_fixed_shop_view(bot, user_id: int) -> FixedShopView:
    """Créer une vue de boutique corrigée"""
    shop_view = FixedShopView(bot, user_id)
    # Initialiser la base de données si nécessaire
    await shop_view.shop_db.initialize_shop_tables()
    await shop_view.shop_db.add_default_shop_items()
    return shop_view