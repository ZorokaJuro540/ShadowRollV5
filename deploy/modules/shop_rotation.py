"""
Shadow Roll Bot - Boutique Rotatif (Style Fortnite)
Système de boutique avec rotation quotidienne et offres spéciales
"""

import discord
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from core.config import BotConfig
from modules.utils import format_number, get_display_name
from modules.text_styling import style_section, style_character
import logging

logger = logging.getLogger(__name__)

class ShopRotationSystem:
    """Système de boutique avec rotation comme Fortnite"""
    
    def __init__(self, bot):
        self.bot = bot
        self.current_rotation = None
        self.rotation_end_time = None
        
    async def generate_daily_rotation(self) -> Dict:
        """Générer une rotation quotidienne d'articles"""
        
        # Articles Featured (Style Fortnite - Prix x5)
        featured_items = [
            {
                "name": "🪙 PACK LÉGENDE ULTIME",
                "description": "MEGA PACK • 15 invocations + 75% bonus rareté + 5000 SC",
                "price": 12500,  # 2500 x 5
                "original_price": 15000,
                "discount": "-17%",
                "type": "pack",
                "rarity": "Secret",
                "icon": "🎁",
                "value": "15 rolls + 75% + 5K SC",
                "category": "featured",
                "tier": "LEGENDARY"
            },
            {
                "name": "💎 POTION MYTHIQUE TITAN", 
                "description": "ULTRA RARE • Triple les chances Mythic+ pendant 2h",
                "price": 9000,  # 1800 x 5
                "original_price": 10000,
                "discount": "-10%",
                "type": "potion",
                "rarity": "Titan",
                "icon": "🧪",
                "value": "x3 Mythic+ 2h",
                "category": "featured",
                "tier": "EPIC"
            },

            {
                "name": "🔮 ORACLE DES OMBRES",
                "description": "ÉDITION LIMITÉE • Révèle la prochaine invocation garantie",
                "price": 15000,
                "original_price": 18000,
                "discount": "-17%",
                "type": "oracle",
                "rarity": "Secret",
                "icon": "🔮",
                "value": "Next roll preview",
                "category": "featured",
                "tier": "LEGENDARY"
            }
        ]
        
        # Articles Daily (Style Fortnite Daily Shop - Prix x5)
        daily_items = [
            {
                "name": "🍀 POTION CHANCE PRO",
                "description": "COMMUN • Augmente toutes les raretés de 15% pendant 1h",
                "price": 4000,  # 800 x 5
                "type": "potion",
                "rarity": "Epic",
                "icon": "🍀",
                "value": "+15% rarities 1h",
                "category": "daily",
                "tier": "UNCOMMON"
            },
            {
                "name": "🪙 MULTIPLICATEUR COINS PLUS",
                "description": "POPULAIRE • Triple les gains de coins pendant 45min",
                "price": 3000,  # 600 x 5
                "type": "boost",
                "rarity": "Rare", 
                "icon": "🪙",
                "value": "x3 coins 45min",
                "category": "daily",
                "tier": "COMMON"
            },
            {
                "name": "🔮 CRAFT GARANTI ULTRA",
                "description": "RARE • Garantit 3 crafts + matériaux bonus",
                "price": 6000,  # 1200 x 5
                "type": "boost",
                "rarity": "Mythic",
                "icon": "🔮", 
                "value": "3 guaranteed crafts",
                "category": "daily",
                "tier": "RARE"
            },
            {
                "name": "🎯 VISION OMEGA",
                "description": "COMMUN • Révèle tous hunts + 3 indices gratuits",
                "price": 1500,  # 300 x 5
                "type": "utility",
                "rarity": "Epic",
                "icon": "🎯",
                "value": "Hunt vision + 3 hints",
                "category": "daily",
                "tier": "COMMON"
            },
            {
                "name": "⭐ BOOST XP CHAMPION",
                "description": "NOUVEAU • Double l'expérience de toutes actions",
                "price": 3500,
                "type": "boost",
                "rarity": "Legendary",
                "icon": "⭐",
                "value": "x2 XP all actions",
                "category": "daily",
                "tier": "UNCOMMON"
            }
        ]
        
        # Sélectionner aléatoirement les articles du jour (style Fortnite)
        selected_featured = random.sample(featured_items, min(3, len(featured_items)))  # Plus d'articles featured
        selected_daily = random.sample(daily_items, min(5, len(daily_items)))  # Plus d'articles daily
        
        # Calculer le temps de fin de rotation (24h)
        end_time = datetime.now() + timedelta(hours=24)
        
        return {
            "featured": selected_featured,
            "daily": selected_daily,
            "rotation_end": end_time,
            "generated_at": datetime.now()
        }
    
    async def get_current_rotation(self) -> Dict:
        """Obtenir la rotation actuelle ou en générer une nouvelle"""
        now = datetime.now()
        
        # Vérifier si une nouvelle rotation est nécessaire
        if (self.current_rotation is None or 
            self.rotation_end_time is None or 
            now >= self.rotation_end_time):
            
            self.current_rotation = await self.generate_daily_rotation()
            self.rotation_end_time = self.current_rotation["rotation_end"]
            
        return self.current_rotation
    
    async def get_time_remaining(self) -> str:
        """Obtenir le temps restant avant la prochaine rotation"""
        if self.rotation_end_time is None:
            return "Calcul en cours..."
            
        now = datetime.now()
        remaining = self.rotation_end_time - now
        
        if remaining.total_seconds() <= 0:
            return "Rotation en cours..."
            
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"


class ShopRotationView(discord.ui.View):
    """Interface de la boutique rotatif style Fortnite"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.shop_system = ShopRotationSystem(bot)
        self.current_category = "featured"
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_shop_embed(self) -> discord.Embed:
        """Créer l'embed de la boutique style Fortnite moderne"""
        try:
            rotation = await self.shop_system.get_current_rotation()
            time_remaining = await self.shop_system.get_time_remaining()
            
            # Obtenir les pièces du joueur
            player = await self.bot.db.get_or_create_player(self.user_id, f"User_{self.user_id}")
            
            # Couleurs spéciales selon la catégorie
            if self.current_category == "featured":
                embed_color = 0xFF6B35  # Orange Fortnite Featured
                title_emoji = "⭐"
                title_text = "FEATURED ITEMS"
            else:
                embed_color = 0x00D4FF  # Bleu Fortnite Daily
                title_emoji = "🛒"
                title_text = "DAILY ITEMS"
            
            embed = discord.Embed(
                title=f"{title_emoji} ═══════〔 {style_section(title_text)} 〕═══════ {title_emoji}",
                description=(f"```ansi\n"
                           f"\u001b[1;33m⏰ NEXT ROTATION: {time_remaining}\u001b[0m\n"
                           f"\u001b[1;32m🪙 YOUR SHADOW COINS: {format_number(player.coins)} SC\u001b[0m\n"
                           f"\u001b[1;37m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m\n"
                           f"```"),
                color=embed_color
            )
            
            # Articles selon la catégorie actuelle
            if self.current_category == "featured":
                items = rotation["featured"]
                header = "🪙 **FEATURED ITEMS** 🪙\n*Premium items with limited availability*"
            else:
                items = rotation["daily"]
                header = "🛒 **DAILY ITEMS** 🛒\n*Fresh rotation every 24 hours*"
                
            embed.add_field(
                name="╔═══════════════════════════════════════════╗",
                value=f"{header}\n╚═══════════════════════════════════════════╝",
                inline=False
            )
            
            # Afficher les articles avec style Fortnite
            for i, item in enumerate(items, 1):
                # Tier colors style Fortnite
                if item.get('tier') == "LEGENDARY":
                    tier_color = "🟠"  # Orange
                    tier_border = "▰▰▰▰▰"
                elif item.get('tier') == "EPIC":
                    tier_color = "🟣"  # Violet
                    tier_border = "▰▰▰▰"
                elif item.get('tier') == "RARE":
                    tier_color = "🔵"  # Bleu
                    tier_border = "▰▰▰"
                elif item.get('tier') == "UNCOMMON":
                    tier_color = "🟢"  # Vert
                    tier_border = "▰▰"
                else:
                    tier_color = "⚪"  # Blanc
                    tier_border = "▰"
                
                # Prix avec réduction si applicable
                price_text = f"**{format_number(item['price'])} SC**"
                if 'original_price' in item and 'discount' in item:
                    price_text += f"\n~~{format_number(item['original_price'])} SC~~ `{item['discount']}`"
                
                # Vérifier si affordable
                can_afford = player.coins >= item['price']
                affordability = "✅ **AFFORDABLE**" if can_afford else "❌ **INSUFFICIENT FUNDS**"
                
                # Rarity emoji
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(item['rarity'], '◆')
                
                embed.add_field(
                    name=f"╭─ {item['icon']} **{style_character(item['name'])}** ─╮",
                    value=(f"```ansi\n"
                          f"\u001b[1;37m{item['description']}\u001b[0m\n"
                          f"```\n"
                          f"{tier_color} **{item.get('tier', 'COMMON')}** {tier_border}\n"
                          f"{rarity_emoji} *{item['rarity']}* • 📦 `{item['value']}`\n"
                          f"🪙 {price_text}\n"
                          f"{affordability}\n"
                          f"╰───────────────────────╯"),
                    inline=True
                )
            
            # Footer avec style cohérent
            embed.set_footer(
                text=f"🎮 {style_character('SHADOW ROLL SHOP')} • Daily rotation at 00:00 UTC",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            return embed
            
        except Exception as e:
            logger.error(f"Error creating shop embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger la boutique rotatif",
                color=0xff0000
            )
    
    # Style Fortnite buttons with proper colors
    @discord.ui.button(label='⭐ FEATURED ITEMS', style=discord.ButtonStyle.danger, row=0)
    async def featured_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "featured"
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🛒 DAILY ITEMS', style=discord.ButtonStyle.primary, row=0)
    async def daily_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_category = "daily"
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🪙 PURCHASE', style=discord.ButtonStyle.success, row=0)
    async def purchase_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PurchaseModal(self.shop_system, self.current_category, self.bot, self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label='🔄 NEW ROTATION', style=discord.ButtonStyle.secondary, row=0)
    async def force_rotation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Force new rotation (admin only)"""
        if not BotConfig.is_admin(self.user_id):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
            
        self.shop_system.current_rotation = None
        self.shop_system.rotation_end_time = None
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
        await interaction.followup.send("✅ Fresh rotation loaded!", ephemeral=True)
    
    @discord.ui.button(label='🏠 LOBBY', style=discord.ButtonStyle.secondary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class PurchaseModal(discord.ui.Modal, title="🪙 FORTNITE SHOP PURCHASE"):
    """Modal pour acheter des articles de la boutique"""
    
    def __init__(self, shop_system: ShopRotationSystem, category: str, bot, user_id: int):
        super().__init__()
        self.shop_system = shop_system
        self.category = category
        self.bot = bot
        self.user_id = user_id

    item_number = discord.ui.TextInput(
        label="Numéro de l'article à acheter",
        placeholder="Entrez le numéro de l'article (1, 2, 3...)",
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            item_index = int(self.item_number.value) - 1
            
            # Obtenir la rotation actuelle
            rotation = await self.shop_system.get_current_rotation()
            items = rotation[self.category]
            
            if item_index < 0 or item_index >= len(items):
                await interaction.response.send_message(
                    f"❌ Numéro invalide! Choisissez entre 1 et {len(items)}", ephemeral=True)
                return
            
            selected_item = items[item_index]
            
            # Vérifier les fonds du joueur
            player = await self.bot.db.get_or_create_player(self.user_id, f"User_{self.user_id}")
            
            if player.coins < selected_item['price']:
                await interaction.response.send_message(
                    f"❌ Fonds insuffisants! Il vous faut {format_number(selected_item['price'])} SC mais vous n'avez que {format_number(player.coins)} SC.",
                    ephemeral=True)
                return
            
            # Traiter l'achat
            success = await self.process_purchase(selected_item, player)
            
            if success:
                # Déduire le coût
                new_coins = player.coins - selected_item['price']
                await self.bot.db.update_player_coins(self.user_id, new_coins)
                
                await interaction.response.send_message(
                    f"✅ **{selected_item['name']}** acheté avec succès!\n"
                    f"🪙 Coût: {format_number(selected_item['price'])} SC\n"
                    f"🪙 Nouveau solde: {format_number(new_coins)} SC",
                    ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"❌ Erreur lors de l'achat de **{selected_item['name']}**", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un numéro valide!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error in shop purchase: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'achat.", ephemeral=True)
    
    async def process_purchase(self, item: Dict, player) -> bool:
        """Traiter l'achat d'un article selon son type"""
        try:
            item_type = item['type']
            
            if item_type == "pack":
                # Ajouter des invocations gratuites ou des packs
                if "10 rolls" in item['value']:
                    # Donner 10 invocations gratuites
                    return True
                elif "5 free rolls" in item['value']:
                    # Donner 5 invocations gratuites
                    return True
                    
            elif item_type == "potion":
                # Ajouter des potions temporaires
                # Ici on pourrait implémenter un système de buffs temporaires
                return True
                
            elif item_type == "boost":
                # Appliquer des bonus temporaires
                return True
                
            elif item_type == "utility":
                # Utilitaires divers
                if "Remove cooldowns" in item['value']:
                    # Reset tous les cooldowns
                    current_time = "1970-01-01T00:00:00"
                    await self.bot.db.db.execute(
                        "UPDATE players SET last_reroll = ? WHERE user_id = ?",
                        (current_time, self.user_id)
                    )
                    await self.bot.db.db.commit()
                    return True
                    
            return True
            
        except Exception as e:
            logger.error(f"Error processing purchase: {e}")
            return False