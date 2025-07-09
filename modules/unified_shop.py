"""
Unified Shop System for Shadow Roll Bot
Combines buying and selling in a modern interface
"""

import discord
import asyncio
from datetime import datetime, timedelta
from core.config import BotConfig
try:
    from modules.text_styling import apply_font_style
except ImportError:
    def apply_font_style(text, style):
        return text

try:
    from modules.utils import truncate_field_value, safe_embed_field
except ImportError:
    def truncate_field_value(text, max_length=1024):
        return text[:max_length]
    def safe_embed_field(embed, name, value, inline=False):
        embed.add_field(name=name, value=value, inline=inline)

class UnifiedShopView(discord.ui.View):
    """Unified shop interface combining buying and selling"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.mode = "buy"  # "buy" or "sell"
        self.page = 1
        self.items_per_page = 6
        
    async def create_shop_embed(self):
        """Create the main shop embed"""
        try:
            # Get user data
            user = self.bot.get_user(self.user_id)
            if not user:
                return self.create_error_embed("Utilisateur non trouvé")
                
            player_data = await self.bot.db.get_player_data(self.user_id)
            if not player_data:
                return self.create_error_embed("Données joueur non trouvées")
                
            if self.mode == "buy":
                return await self.create_buy_embed(player_data)
            else:
                return await self.create_sell_embed(player_data)
                
        except Exception as e:
            print(f"Error creating shop embed: {e}")
            return self.create_error_embed("Erreur lors du chargement du shop")
    
    async def create_buy_embed(self, player_data):
        """Create buying interface embed"""
        embed = discord.Embed(
            title=f"🛒 {apply_font_style('SHADOW ROLL SHOP', 'vaporwave')}",
            description=f"```ansi\n{apply_font_style('MODE ACHAT', 'section')}\n```",
            color=0x2f3136
        )
        
        # User balance
        coins = player_data.get('coins', 0)
        embed.add_field(
            name=f"🪙 {apply_font_style('VOTRE SOLDE', 'bold')}",
            value=f"```ansi\n\u001b[1;33m{coins:,}\u001b[0m Shadow Coins```",
            inline=False
        )
        
        # Shop items
        shop_items = await self.get_shop_items()
        if not shop_items:
            embed.add_field(
                name="❌ Boutique Vide",
                value="Aucun article disponible pour le moment.",
                inline=False
            )
        else:
            items_text = ""
            start_idx = (self.page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            current_items = shop_items[start_idx:end_idx]
            
            for i, item in enumerate(current_items, 1):
                price = item.get('price', 0)
                name = item.get('name', 'Article')
                description = item.get('description', 'Aucune description')
                
                # Color based on price tier
                if price >= 10000:
                    color_code = "\u001b[1;35m"  # Magenta for premium
                elif price >= 5000:
                    color_code = "\u001b[1;33m"  # Yellow for expensive
                elif price >= 2000:
                    color_code = "\u001b[1;32m"  # Green for moderate
                else:
                    color_code = "\u001b[1;36m"  # Cyan for cheap
                
                items_text += f"{color_code}{i}. {name}\u001b[0m\n"
                items_text += f"   🪙 {price:,} SC\n"
                items_text += f"   📝 {description}\n\n"
            
            embed.add_field(
                name=f"🛍️ {apply_font_style('ARTICLES DISPONIBLES', 'section')}",
                value=f"```ansi\n{items_text}```",
                inline=False
            )
            
            # Pagination info
            total_pages = (len(shop_items) + self.items_per_page - 1) // self.items_per_page
            embed.add_field(
                name="📄 Navigation",
                value=f"Page {self.page}/{total_pages}",
                inline=True
            )
        
        # Footer
        embed.set_footer(
            text=f"{apply_font_style('SHADOW ROLL SHOP', 'serif')}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        return embed
    
    async def create_sell_embed(self, player_data):
        """Create selling interface embed"""
        embed = discord.Embed(
            title=f"🪙 {apply_font_style('SHADOW ROLL SHOP', 'vaporwave')}",
            description=f"```ansi\n{apply_font_style('MODE VENTE', 'section')}\n```",
            color=0x2f3136
        )
        
        # Get user inventory
        inventory = await self.bot.db.get_user_inventory(self.user_id, limit=50)
        
        if not inventory:
            embed.add_field(
                name="📦 Inventaire Vide",
                value="Aucun personnage à vendre.",
                inline=False
            )
        else:
            # Group by rarity for better display
            rarity_groups = {}
            for item in inventory:
                rarity = item.get('rarity', 'Common')
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append(item)
            
            # Display grouped inventory
            inventory_text = ""
            for rarity, items in rarity_groups.items():
                rarity_color = BotConfig.RARITY_COLORS.get(rarity, 0x808080)
                color_code = self.get_ansi_color(rarity_color)
                
                inventory_text += f"{color_code}{BotConfig.RARITY_EMOJIS.get(rarity, '◆')} {rarity}\u001b[0m\n"
                
                for item in items[:5]:  # Show max 5 per rarity
                    name = item.get('name', 'Unknown')
                    value = item.get('value', 0)
                    quantity = item.get('quantity', 1)
                    
                    inventory_text += f"   • {name}"
                    if quantity > 1:
                        inventory_text += f" (x{quantity})"
                    inventory_text += f" - {value:,} SC\n"
                
                if len(items) > 5:
                    inventory_text += f"   ... et {len(items) - 5} autres\n"
                inventory_text += "\n"
            
            embed.add_field(
                name=f"🎒 {apply_font_style('VOTRE INVENTAIRE', 'section')}",
                value=f"```ansi\n{inventory_text}```",
                inline=False
            )
        
        # Current balance
        coins = player_data.get('coins', 0)
        embed.add_field(
            name=f"🪙 {apply_font_style('SOLDE ACTUEL', 'bold')}",
            value=f"```ansi\n\u001b[1;33m{coins:,}\u001b[0m Shadow Coins```",
            inline=True
        )
        
        # Footer
        embed.set_footer(
            text=f"{apply_font_style('SHADOW ROLL SHOP', 'serif')}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        return embed
    
    def get_ansi_color(self, color_int):
        """Convert color integer to ANSI code"""
        if color_int == 0xff0000:  # Red
            return "\u001b[1;31m"
        elif color_int == 0xffa500:  # Orange/Yellow
            return "\u001b[1;33m"
        elif color_int == 0xa335ee:  # Purple
            return "\u001b[1;35m"
        elif color_int == 0x0070dd:  # Blue
            return "\u001b[1;34m"
        elif color_int == 0x00ff00:  # Green
            return "\u001b[1;32m"
        elif color_int == 0xffffff:  # White
            return "\u001b[1;37m"
        elif color_int == 0xff1493:  # Pink
            return "\u001b[1;35m"
        elif color_int == 0x000000:  # Black
            return "\u001b[1;30m"
        else:
            return "\u001b[1;36m"  # Cyan default
    
    async def get_shop_items(self):
        """Get available shop items"""
        items = [
            {
                'name': 'Potion de Chance',
                'price': 1500,
                'description': 'Augmente les chances de rareté pendant 1h',
                'type': 'potion',
                'effect': 'luck_boost'
            },
            {
                'name': 'Multiplicateur de Pièces',
                'price': 2000,
                'description': 'Double les gains de pièces pendant 1h',
                'type': 'potion',
                'effect': 'coin_multiplier'
            },
            {
                'name': 'Reset Cooldown',
                'price': 1000,
                'description': 'Supprime tous les cooldowns actifs',
                'type': 'utility',
                'effect': 'cooldown_reset'
            },
            {
                'name': 'Pack Invocation Premium',
                'price': 5000,
                'description': '10 invocations avec bonus de rareté',
                'type': 'pack',
                'effect': 'premium_rolls'
            },
            {
                'name': 'Garanti Légendaire',
                'price': 7500,
                'description': 'Prochaine invocation garantie Légendaire+',
                'type': 'guarantee',
                'effect': 'legendary_guarantee'
            },
            {
                'name': 'Orbe Mystique',
                'price': 12000,
                'description': 'Chance d\'obtenir un personnage Secret',
                'type': 'special',
                'effect': 'secret_chance'
            }
        ]
        return items
    
    def create_error_embed(self, message):
        """Create error embed"""
        return discord.Embed(
            title="❌ Erreur",
            description=message,
            color=0xff0000
        )
    
    # Button handlers
    @discord.ui.button(label='🛍️ Acheter', style=discord.ButtonStyle.success, row=0)
    async def buy_mode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        self.mode = "buy"
        self.page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='🪙 Vendre', style=discord.ButtonStyle.danger, row=0)
    async def sell_mode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        self.mode = "sell"
        self.page = 1
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)
    
    @discord.ui.button(label='◀️', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        if self.page > 1:
            self.page -= 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("❌ Vous êtes déjà sur la première page.", ephemeral=True)
    
    @discord.ui.button(label='▶️', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        if self.mode == "buy":
            items = await self.get_shop_items()
            max_pages = (len(items) + self.items_per_page - 1) // self.items_per_page
            if self.page < max_pages:
                self.page += 1
                await interaction.response.defer()
                embed = await self.create_shop_embed()
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message("❌ Vous êtes déjà sur la dernière page.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Pagination non disponible en mode vente.", ephemeral=True)
    
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=0)
    async def main_menu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(label='🛒 Acheter Article', style=discord.ButtonStyle.success, row=1)
    async def buy_item_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        if self.mode != "buy":
            await interaction.response.send_message("❌ Basculez en mode achat pour acheter des articles.", ephemeral=True)
            return
        
        await interaction.response.send_modal(BuyItemModal(self.bot, self.user_id))
    
    @discord.ui.button(label='🪙 Vendre Personnage', style=discord.ButtonStyle.danger, row=1)
    async def sell_character_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce menu.", ephemeral=True)
            return
        
        if self.mode != "sell":
            await interaction.response.send_message("❌ Basculez en mode vente pour vendre des personnages.", ephemeral=True)
            return
        
        await interaction.response.send_modal(SellCharacterModal(self.bot, self.user_id))
    
    async def create_menu_embed(self):
        """Create menu embed for compatibility"""
        embed = discord.Embed(
            title=f"🌑 {apply_font_style('SHADOW ROLL', 'vaporwave')}",
            description="Bienvenue dans les ténèbres...",
            color=0x2f3136
        )
        return embed

class BuyItemModal(discord.ui.Modal):
    """Modal for buying shop items"""
    
    def __init__(self, bot, user_id):
        super().__init__(title="Acheter un Article")
        self.bot = bot
        self.user_id = user_id
        
        self.item_number = discord.ui.TextInput(
            label="Numéro de l'article",
            placeholder="Entrez le numéro de l'article à acheter (1-6)",
            min_length=1,
            max_length=2,
            required=True
        )
        self.add_item(self.item_number)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            item_num = int(self.item_number.value)
            if item_num < 1 or item_num > 6:
                await interaction.response.send_message("❌ Numéro d'article invalide (1-6).", ephemeral=True)
                return
            
            # Get shop items
            unified_shop = UnifiedShopView(self.bot, self.user_id)
            shop_items = await unified_shop.get_shop_items()
            
            if item_num > len(shop_items):
                await interaction.response.send_message("❌ Article non disponible.", ephemeral=True)
                return
            
            item = shop_items[item_num - 1]
            price = item['price']
            name = item['name']
            
            # Check player balance
            player_data = await self.bot.db.get_player_data(self.user_id)
            if not player_data:
                await interaction.response.send_message("❌ Données joueur non trouvées.", ephemeral=True)
                return
            
            coins = player_data.get('coins', 0)
            if coins < price:
                await interaction.response.send_message(f"❌ Fonds insuffisants! Il vous faut {price:,} SC.", ephemeral=True)
                return
            
            # Process purchase
            await self.bot.db.update_player_coins(self.user_id, -price)
            
            # Apply item effect (simplified)
            await self.apply_item_effect(item)
            
            embed = discord.Embed(
                title="✅ Achat Réussi",
                description=f"Vous avez acheté **{name}** pour {price:,} SC!",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Veuillez entrer un numéro valide.", ephemeral=True)
        except Exception as e:
            print(f"Error in buy item modal: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'achat.", ephemeral=True)
    
    async def apply_item_effect(self, item):
        """Apply purchased item effect"""
        try:
            item_type = item.get('type', 'potion')
            item_name = item.get('name', 'Unknown Item')
            effect_type = item.get('effect', 'unknown')
            
            if item_type == 'potion':
                # Add potion to player inventory
                await self.add_potion_to_inventory(item_name, effect_type, item.get('duration', 30))
            elif item_type == 'pack':
                # Handle pack items (rolls, etc.)
                await self.handle_pack_purchase(item)
            elif item_type == 'utility':
                # Handle utility items
                await self.handle_utility_purchase(item)
            elif item_type == 'guarantee':
                # Handle guaranteed items
                await self.handle_guarantee_purchase(item)
            elif item_type == 'special':
                # Handle special items
                await self.handle_special_purchase(item)
                
        except Exception as e:
            print(f"Error applying item effect: {e}")
    
    async def add_potion_to_inventory(self, potion_name, effect_type, duration):
        """Add potion to player inventory"""
        try:
            # Check if player_potions table exists, create if not
            await self.bot.db.db.execute('''
                CREATE TABLE IF NOT EXISTS player_potions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    potion_name TEXT NOT NULL,
                    effect_type TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            ''')
            
            # Check if user already has this potion
            cursor = await self.bot.db.db.execute(
                "SELECT quantity FROM player_potions WHERE user_id = ? AND potion_name = ?",
                (self.user_id, potion_name)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # Increase quantity
                await self.bot.db.db.execute(
                    "UPDATE player_potions SET quantity = quantity + 1 WHERE user_id = ? AND potion_name = ?",
                    (self.user_id, potion_name)
                )
            else:
                # Add new potion
                await self.bot.db.db.execute(
                    "INSERT INTO player_potions (user_id, potion_name, effect_type, duration_minutes) VALUES (?, ?, ?, ?)",
                    (self.user_id, potion_name, effect_type, duration)
                )
            
            await self.bot.db.db.commit()
            print(f"Added potion {potion_name} to user {self.user_id}")
            
        except Exception as e:
            print(f"Error adding potion to inventory: {e}")
    
    async def handle_pack_purchase(self, item):
        """Handle pack item purchases"""
        # For now, just log the purchase
        print(f"Pack purchased: {item['name']} by user {self.user_id}")
    
    async def handle_utility_purchase(self, item):
        """Handle utility item purchases"""
        # For now, just log the purchase
        print(f"Utility purchased: {item['name']} by user {self.user_id}")
    
    async def handle_guarantee_purchase(self, item):
        """Handle guarantee item purchases"""
        # For now, just log the purchase
        print(f"Guarantee purchased: {item['name']} by user {self.user_id}")
    
    async def handle_special_purchase(self, item):
        """Handle special item purchases"""
        # For now, just log the purchase
        print(f"Special item purchased: {item['name']} by user {self.user_id}")

class SellCharacterModal(discord.ui.Modal):
    """Modal for selling characters"""
    
    def __init__(self, bot, user_id):
        super().__init__(title="Vendre un Personnage")
        self.bot = bot
        self.user_id = user_id
        
        self.character_name = discord.ui.TextInput(
            label="Nom du personnage",
            placeholder="Entrez le nom du personnage à vendre",
            min_length=1,
            max_length=100,
            required=True
        )
        self.add_item(self.character_name)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            character_name = self.character_name.value.strip()
            
            # Get user inventory
            inventory = await self.bot.db.get_user_inventory(self.user_id)
            
            # Find character
            character_found = None
            for item in inventory:
                if item.get('name', '').lower() == character_name.lower():
                    character_found = item
                    break
            
            if not character_found:
                await interaction.response.send_message(f"❌ Personnage '{character_name}' non trouvé dans votre inventaire.", ephemeral=True)
                return
            
            # Get character value
            value = character_found.get('value', 0)
            sell_price = int(value * 0.7)  # 70% of original value
            
            # Confirm sale
            embed = discord.Embed(
                title="🪙 Confirmer la Vente",
                description=f"Vendre **{character_found['name']}** pour {sell_price:,} SC?",
                color=0xffa500
            )
            
            view = ConfirmSellView(self.bot, self.user_id, character_found, sell_price)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"Error in sell character modal: {e}")
            await interaction.response.send_message("❌ Erreur lors de la vente.", ephemeral=True)

class ConfirmSellView(discord.ui.View):
    """Confirmation view for selling characters"""
    
    def __init__(self, bot, user_id, character, sell_price):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.character = character
        self.sell_price = sell_price
    
    @discord.ui.button(label='✅ Confirmer', style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        try:
            # Remove character from inventory
            await self.bot.db.remove_character_from_inventory(self.user_id, self.character['id'])
            
            # Add coins
            await self.bot.db.update_player_coins(self.user_id, self.sell_price)
            
            embed = discord.Embed(
                title="✅ Vente Réussie",
                description=f"Vous avez vendu **{self.character['name']}** pour {self.sell_price:,} SC!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            print(f"Error confirming sell: {e}")
            await interaction.response.send_message("❌ Erreur lors de la vente.", ephemeral=True)
    
    @discord.ui.button(label='❌ Annuler', style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Vous ne pouvez pas utiliser ce bouton.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Vente Annulée",
            description="La vente a été annulée.",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)