"""
Shadow Roll Bot - Modern Shop System
Redesigned shop with working purchase system and modern UI
"""

import discord
from discord.ext import commands
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from core.config import BotConfig
from modules.utils import format_number

logger = logging.getLogger(__name__)

class ModernShopView(discord.ui.View):
    """Nouvelle boutique moderne avec système d'achat fonctionnel"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 1
        self.items_per_page = 6

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    def get_shop_items(self) -> List[Dict]:
        """Définir les articles de la boutique"""
        return [
            {
                'id': 1,
                'name': '🧪 Potion de Chance',
                'description': 'Améliore les chances de raretés élevées',
                'price': 500,
                'category': 'potion',
                'effect': 'luck_boost',
                'duration': 3600,  # 1 heure
                'icon': '🧪'
            },
            {
                'id': 2,
                'name': '🪙 Multiplicateur de Pièces',
                'description': 'Double les gains de pièces pendant 1h',
                'price': 750,
                'category': 'boost',
                'effect': 'coin_multiplier',
                'duration': 3600,
                'icon': '🪙'
            },
            {
                'id': 3,
                'name': '⚡ Reset Cooldown',
                'description': 'Supprime tous les cooldowns actuels',
                'price': 300,
                'category': 'utility',
                'effect': 'reset_cooldown',
                'icon': '⚡'
            },
            {
                'id': 4,
                'name': '🎲 Pack 5 Invocations',
                'description': 'Accorde 5 invocations gratuites',
                'price': 1000,
                'category': 'pack',
                'effect': 'free_rolls',
                'amount': 5,
                'icon': '🎲'
            },
            {
                'id': 5,
                'name': '🔮 Potion Épique',
                'description': 'Garantit minimum Epic sur la prochaine invocation',
                'price': 1500,
                'category': 'potion',
                'effect': 'epic_guarantee',
                'icon': '🔮'
            },
            {
                'id': 6,
                'name': '🪙 Mega Pack',
                'description': 'Pack ultime: 10 invocations + chance bonus',
                'price': 2500,
                'category': 'pack',
                'effect': 'mega_pack',
                'amount': 10,
                'icon': '🪙'
            },
            {
                'id': 7,
                'name': '💎 Potion Légendaire',
                'description': 'Garantit minimum Legendary sur la prochaine invocation',
                'price': 3000,
                'category': 'potion',
                'effect': 'legendary_guarantee',
                'icon': '💎'
            },
            {
                'id': 8,
                'name': '🔥 Boost Craft',
                'description': 'Réduit les exigences de craft de 50%',
                'price': 2000,
                'category': 'boost',
                'effect': 'craft_discount',
                'duration': 7200,  # 2 heures
                'icon': '🔥'
            }
        ]

    async def create_shop_embed(self) -> discord.Embed:
        """Créer l'embed de la boutique moderne"""
        # Obtenir les articles et les informations du joueur
        all_items = self.get_shop_items()
        player = await self.bot.db.get_or_create_player(self.user_id, "Unknown")
        
        # Pagination
        total_pages = max(1, (len(all_items) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(all_items))
        page_items = all_items[start_idx:end_idx]

        # Créer l'embed principal avec design amélioré
        embed = discord.Embed(
            description=f"""```ansi
\u001b[1;35m╔════════════════════════════════════════════════════════════╗\u001b[0m
\u001b[1;36m║                  🛒 SHADOW MYSTICAL SHOP 🛒                ║\u001b[0m
\u001b[1;35m╚════════════════════════════════════════════════════════════╝\u001b[0m

\u001b[1;32m🪙 Fortune des Ombres: {format_number(player.coins)} {BotConfig.CURRENCY_EMOJI}\u001b[0m
\u001b[1;33m📦 Articles Mystiques: {len(all_items)} disponibles\u001b[0m
\u001b[1;34m📄 Page {self.current_page}/{total_pages} • Objets magiques et potions\u001b[0m
```""",
            color=0x7b2cbf
        )

        # Ajouter les articles de la page actuelle
        for i, item in enumerate(page_items, 1):
            # Déterminer la couleur selon la catégorie
            category_colors = {
                'potion': '🟣',
                'boost': '🟢', 
                'utility': '🔵',
                'pack': '🟡'
            }
            color_indicator = category_colors.get(item['category'], '⚪')
            
            # Créer le nom et la description
            item_name = f"{color_indicator} **{item['name']}**"
            item_desc = f"```\n{item['description']}\n🪙 Prix: {format_number(item['price'])} {BotConfig.CURRENCY_EMOJI}\n```"
            
            # Ajouter l'effet spécial si applicable
            if 'duration' in item:
                hours = item['duration'] // 3600
                minutes = (item['duration'] % 3600) // 60
                if hours > 0:
                    item_desc += f"`⏱️ Durée: {hours}h{minutes:02d}m`\n"
                else:
                    item_desc += f"`⏱️ Durée: {minutes}m`\n"
            
            if 'amount' in item:
                item_desc += f"`🎯 Quantité: {item['amount']}`\n"

            embed.add_field(
                name=f"**{start_idx + i}.** {item_name}",
                value=item_desc,
                inline=True
            )

        # Ajouter les instructions d'achat
        embed.add_field(
            name="🛒 Comment acheter",
            value="```\n1. Cliquez sur '🛒 Acheter'\n2. Entrez le numéro de l'article\n3. Confirmez votre achat\n```",
            inline=False
        )

        # Ajouter des images visuelles pour la boutique
        shop_banners = [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXU2ODU1YTl6M3d4N3N6dnVqeW5vNHV3ejNtZXlqM2FseTN3dWV4eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPjM1lNsCrwEJfq/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmlkZjB1dTRwbnJmYmN3OGZwZTM4a21iYzI4OHZmZnV1cnF1ODFpdCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abKhOpu0NwenH3O/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGlqaTF2bzJpdnhvdzZvYzB4c2V4c2FwOWY1b2NyYXlhanl2OWZ3bCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7abwbzFqNgHlYyAo/giphy.gif"
        ]
        import random
        embed.set_image(url=random.choice(shop_banners))
        embed.set_thumbnail(url="https://i.imgur.com/kGz9R3m.png")
        
        embed.set_footer(
            text="🛒 Shadow Mystical Shop • Objets magiques des ténèbres",
            icon_url="https://i.imgur.com/8bDdvxM.png"
        )

        return embed

    async def process_purchase(self, item: Dict, player) -> bool:
        """Traiter l'achat d'un article"""
        try:
            # D'abord, ajouter l'objet à l'inventaire du joueur
            await self.bot.db.add_item_to_inventory(player.user_id, item['id'], 1)
            
            effect = item['effect']
            
            # Ensuite, appliquer l'effet selon le type d'objet
            if effect == 'luck_boost':
                # Ajouter buff de chance temporaire
                await self.add_temporary_buff(player.user_id, 'luck', item['duration'])
                
            elif effect == 'coin_multiplier':
                # Ajouter multiplicateur de pièces
                await self.add_temporary_buff(player.user_id, 'coin_multiplier', item['duration'])
                
            elif effect == 'reset_cooldown':
                # Supprimer tous les cooldowns (effet instantané)
                await self.bot.db.reset_all_cooldowns(player.user_id)
                
            elif effect == 'free_rolls':
                # Ajouter des invocations gratuites
                await self.bot.db.add_free_rolls(player.user_id, item['amount'])
                
            elif effect == 'epic_guarantee':
                # Garantir epic sur la prochaine invocation
                await self.bot.db.add_guaranteed_rarity(player.user_id, 'Epic')
                
            elif effect == 'legendary_guarantee':
                # Garantir legendary sur la prochaine invocation
                await self.bot.db.add_guaranteed_rarity(player.user_id, 'Legendary')
                
            elif effect == 'mega_pack':
                # Combo pack avec bonus
                await self.bot.db.add_free_rolls(player.user_id, item['amount'])
                await self.add_temporary_buff(player.user_id, 'luck', 1800)  # 30 min
                
            elif effect == 'craft_discount':
                # Réduction sur les crafts
                await self.add_temporary_buff(player.user_id, 'craft_discount', item['duration'])
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing purchase: {e}")
            return False

    async def add_temporary_buff(self, user_id: int, buff_type: str, duration: int):
        """Ajouter un buff temporaire"""
        try:
            # Créer la table des buffs si elle n'existe pas
            await self.bot.db.db.execute("""
                CREATE TABLE IF NOT EXISTS temporary_buffs (
                    user_id INTEGER,
                    buff_type TEXT,
                    expires_at INTEGER,
                    PRIMARY KEY (user_id, buff_type)
                )
            """)
            
            # Ajouter le buff
            expires_at = int(datetime.now().timestamp()) + duration
            await self.bot.db.db.execute(
                "INSERT OR REPLACE INTO temporary_buffs (user_id, buff_type, expires_at) VALUES (?, ?, ?)",
                (user_id, buff_type, expires_at)
            )
            await self.bot.db.db.commit()
            
        except Exception as e:
            logger.error(f"Error adding temporary buff: {e}")

    # Boutons de navigation
    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la première page!", ephemeral=True)

    @discord.ui.button(label='🛒 Acheter', style=discord.ButtonStyle.success, row=0)
    async def purchase_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PurchaseModal(self.bot, self.user_id, self))

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        all_items = self.get_shop_items()
        total_pages = max(1, (len(all_items) + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page < total_pages:
            self.current_page += 1
            await interaction.response.defer()
            embed = await self.create_shop_embed()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.send_message("Vous êtes déjà à la dernière page!", ephemeral=True)

    @discord.ui.button(label='🔄 Actualiser', style=discord.ButtonStyle.primary, row=0)
    async def refresh_shop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        embed = await self.create_shop_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.danger, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)


class PurchaseModal(discord.ui.Modal, title="🛒 Acheter un Article"):
    """Modal pour acheter des articles"""

    def __init__(self, bot, user_id: int, shop_view: ModernShopView):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.shop_view = shop_view

    item_number = discord.ui.TextInput(
        label='Numéro de l\'article à acheter',
        placeholder='Entrez le numéro affiché (ex: 1, 2, 3...)',
        required=True,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Valider l'entrée
            try:
                selection = int(self.item_number.value)
            except ValueError:
                await interaction.response.send_message("❌ Veuillez entrer un numéro valide!", ephemeral=True)
                return

            # Obtenir les articles de la page actuelle
            all_items = self.shop_view.get_shop_items()
            start_idx = (self.shop_view.current_page - 1) * self.shop_view.items_per_page
            end_idx = min(start_idx + self.shop_view.items_per_page, len(all_items))
            page_items = all_items[start_idx:end_idx]

            if selection < 1 or selection > len(page_items):
                await interaction.response.send_message(
                    f"❌ Numéro invalide! Choisissez entre 1 et {len(page_items)}", ephemeral=True)
                return

            selected_item = page_items[selection - 1]
            
            # Vérifier si le joueur peut se le permettre
            player = await self.bot.db.get_or_create_player(self.user_id, interaction.user.display_name)
            if player.coins < selected_item['price']:
                needed = selected_item['price'] - player.coins
                await interaction.response.send_message(
                    f"❌ **Fonds insuffisants!**\n"
                    f"🪙 Prix: {format_number(selected_item['price'])} {BotConfig.CURRENCY_EMOJI}\n"
                    f"🪙 Il vous manque: {format_number(needed)} {BotConfig.CURRENCY_EMOJI}", 
                    ephemeral=True)
                return

            # Traiter l'achat
            success = await self.shop_view.process_purchase(selected_item, player)
            
            if success:
                # Déduire le coût
                new_coins = player.coins - selected_item['price']
                await self.bot.db.update_player_coins(self.user_id, new_coins)
                
                # Mettre à jour l'affichage de la boutique
                embed = await self.shop_view.create_shop_embed()
                await interaction.response.edit_message(embed=embed, view=self.shop_view)
                
                # Envoyer le message de succès
                await interaction.followup.send(
                    f"🎉 **Achat réussi!**\n"
                    f"{selected_item['icon']} **{selected_item['name']}** ajouté à votre inventaire!\n"
                    f"🪙 Nouveau solde: {format_number(new_coins)} {BotConfig.CURRENCY_EMOJI}\n"
                    f"✨ Effet appliqué avec succès!", 
                    ephemeral=True)
            else:
                await interaction.response.send_message(
                    f"❌ Erreur lors de l'achat de **{selected_item['name']}**. Veuillez réessayer.", 
                    ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in purchase modal: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'achat. Veuillez réessayer.", ephemeral=True)


# Fonctions utilitaires pour les méthodes de base de données
async def setup_shop_database(bot):
    """Configurer les tables nécessaires pour la boutique"""
    try:
        # Table pour les invocations gratuites
        await bot.db.db.execute("""
            CREATE TABLE IF NOT EXISTS free_rolls (
                user_id INTEGER PRIMARY KEY,
                amount INTEGER DEFAULT 0
            )
        """)
        
        # Table pour les raretés garanties
        await bot.db.db.execute("""
            CREATE TABLE IF NOT EXISTS guaranteed_rarities (
                user_id INTEGER PRIMARY KEY,
                rarity TEXT,
                expires_at INTEGER
            )
        """)
        
        # Ajouter les méthodes à la classe Database
        async def add_free_rolls(self, user_id: int, amount: int):
            """Ajouter des invocations gratuites"""
            await self.db.execute(
                "INSERT OR REPLACE INTO free_rolls (user_id, amount) VALUES (?, COALESCE((SELECT amount FROM free_rolls WHERE user_id = ?), 0) + ?)",
                (user_id, user_id, amount)
            )
            await self.db.commit()
        
        async def get_free_rolls(self, user_id: int) -> int:
            """Obtenir le nombre d'invocations gratuites"""
            cursor = await self.db.execute("SELECT amount FROM free_rolls WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            return result[0] if result else 0
        
        async def use_free_roll(self, user_id: int) -> bool:
            """Utiliser une invocation gratuite"""
            current = await self.get_free_rolls(user_id)
            if current > 0:
                await self.db.execute(
                    "UPDATE free_rolls SET amount = amount - 1 WHERE user_id = ?",
                    (user_id,)
                )
                await self.db.commit()
                return True
            return False
        
        async def reset_all_cooldowns(self, user_id: int):
            """Supprimer tous les cooldowns"""
            await self.db.execute("DELETE FROM cooldowns WHERE user_id = ?", (user_id,))
            await self.db.commit()
        
        async def add_guaranteed_rarity(self, user_id: int, rarity: str):
            """Ajouter une rareté garantie pour la prochaine invocation"""
            expires_at = int(datetime.now().timestamp()) + 3600  # 1 heure
            await self.db.execute(
                "INSERT OR REPLACE INTO guaranteed_rarities (user_id, rarity, expires_at) VALUES (?, ?, ?)",
                (user_id, rarity, expires_at)
            )
            await self.db.commit()
        
        async def add_item_to_inventory(self, user_id: int, item_id: int, quantity: int):
            """Ajouter un objet à l'inventaire du joueur"""
            try:
                # Créer la table des objets du joueur si elle n'existe pas
                await self.db.execute("""
                    CREATE TABLE IF NOT EXISTS player_shop_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        item_id INTEGER,
                        quantity INTEGER DEFAULT 1,
                        purchased_at INTEGER,
                        UNIQUE(user_id, item_id)
                    )
                """)
                
                # Ajouter ou mettre à jour l'objet
                current_time = int(datetime.now().timestamp())
                await self.db.execute("""
                    INSERT INTO player_shop_items (user_id, item_id, quantity, purchased_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, item_id) 
                    DO UPDATE SET quantity = quantity + ?, purchased_at = ?
                """, (user_id, item_id, quantity, current_time, quantity, current_time))
                
                await self.db.commit()
                
            except Exception as e:
                logger.error(f"Error adding item to inventory: {e}")
        
        async def get_player_shop_items(self, user_id: int):
            """Obtenir les objets du joueur"""
            try:
                cursor = await self.db.execute("""
                    SELECT psi.item_id, psi.quantity, psi.purchased_at
                    FROM player_shop_items psi
                    WHERE psi.user_id = ? AND psi.quantity > 0
                    ORDER BY psi.purchased_at DESC
                """, (user_id,))
                
                items = []
                for row in await cursor.fetchall():
                    items.append({
                        'item_id': row[0],
                        'quantity': row[1],
                        'purchased_at': row[2]
                    })
                return items
                
            except Exception as e:
                logger.error(f"Error getting player shop items: {e}")
                return []

        # Attacher les méthodes à la classe Database
        bot.db.add_free_rolls = add_free_rolls.__get__(bot.db, bot.db.__class__)
        bot.db.get_free_rolls = get_free_rolls.__get__(bot.db, bot.db.__class__)
        bot.db.use_free_roll = use_free_roll.__get__(bot.db, bot.db.__class__)
        bot.db.reset_all_cooldowns = reset_all_cooldowns.__get__(bot.db, bot.db.__class__)
        bot.db.add_guaranteed_rarity = add_guaranteed_rarity.__get__(bot.db, bot.db.__class__)
        bot.db.add_item_to_inventory = add_item_to_inventory.__get__(bot.db, bot.db.__class__)
        bot.db.get_player_shop_items = get_player_shop_items.__get__(bot.db, bot.db.__class__)
        
        await bot.db.db.commit()
        logger.info("Modern shop database setup completed")
        
    except Exception as e:
        logger.error(f"Error setting up shop database: {e}")