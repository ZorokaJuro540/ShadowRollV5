"""
Système de Craft pour Shadow Roll Bot
Permet d'évoluer des personnages en combinant plusieurs exemplaires
"""

import discord
from discord.ext import commands
import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio

from core.config import BotConfig
from modules.utils import format_number, get_display_name

logger = logging.getLogger(__name__)

class CraftView(discord.ui.View):
    """Interface de craft avec sélection et évolution"""
    
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.recipes_per_page = 5
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_craft_embed(self) -> discord.Embed:
        """Créer l'embed du système de craft avec le style Shadow"""
        recipes = await self.get_craft_recipes()
        
        # Obtenir les informations utilisateur pour l'affichage
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"User {self.user_id}"
        player = await self.bot.db.get_or_create_player(self.user_id, username)
        
        embed = discord.Embed(
            title="🌌 ═══════〔 A T E L I E R   D ' É V O L U T I O N 〕═══════ 🌌",
            description=f"```\n◆ Maître des Évolutions: {username} ◆\n🪙 Shadow Coins: {format_number(player.coins)}\n```",
            color=BotConfig.RARITY_COLORS['Evolve']
        )
        
        if not recipes:
            embed.add_field(
                name="🌑 ═══〔 Aucune Évolution Disponible 〕═══ 🌑",
                value=("```\n"
                       "◆ Aucune recette d'évolution détectée\n"
                       "◆ Collectez des personnages Evolve d'abord\n"
                       "◆ Les recettes se génèrent automatiquement\n"
                       "```"),
                inline=False
            )
        else:
            start_idx = self.current_page * self.recipes_per_page
            end_idx = start_idx + self.recipes_per_page
            page_recipes = recipes[start_idx:end_idx]
            
            recipe_sections = []
            craftable_count = 0
            
            for recipe in page_recipes:
                base_name, evolved_name, count, user_count = recipe
                can_craft = user_count >= count
                if can_craft:
                    craftable_count += 1
                
                status_icon = "🔮" if can_craft else "⚫"
                progress_bar = self.create_progress_bar(user_count, count)
                
                recipe_section = (
                    f"{status_icon} **{base_name}** ➤ **{evolved_name}**\n"
                    f"   {progress_bar} **{user_count}/{count}** exemplaires\n"
                    f"   {'✨ Prêt à évoluer!' if can_craft else '🔸 Collectez encore'}"
                )
                recipe_sections.append(recipe_section)
            
            embed.add_field(
                name=f"🌑 ═══〔 Recettes d'Évolution 〕═══ 🌑",
                value="```\n" + f"◆ Évolutions disponibles: {craftable_count}/{len(page_recipes)}\n" + "```\n\n" + "\n\n".join(recipe_sections),
                inline=False
            )
            
            # Statistiques et navigation
            total_pages = (len(recipes) + self.recipes_per_page - 1) // self.recipes_per_page
            total_craftable = sum(1 for r in recipes if r[3] >= r[2])
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"```\nÉvolutions prêtes: {total_craftable}\nRecettes totales: {len(recipes)}\nPage: {self.current_page + 1}/{total_pages}\n```",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Instructions",
                value="```\n⚡ Craft - Évoluer\n◀️▶️ - Navigation\n🏠 - Menu principal\n```",
                inline=True
            )
        
        embed.set_footer(
            text="Shadow Roll • Atelier d'Évolution",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        return embed
    
    def create_progress_bar(self, current: int, required: int, length: int = 8) -> str:
        """Créer une barre de progression stylée"""
        if required == 0:
            return "▓" * length
        
        progress = min(current / required, 1.0)
        filled = int(progress * length)
        
        if progress >= 1.0:
            return "🟣" * length  # Couleur Evolve quand complet
        else:
            return "🟣" * filled + "⚫" * (length - filled)
    
    def get_custom_craft_requirements(self) -> Dict[str, int]:
        """Configuration des quantités personnalisées pour le craft"""
        return {
            "Garou Cosmic": 500,  # Garou Cosmic nécessite 500 Garou normaux
            "Mahoraga": 100,      # Mahoraga nécessite 100 Megumi Fushiguro
            # Ajouter d'autres personnages Evolve avec des exigences spéciales ici
        }
    
    def get_custom_base_names(self) -> Dict[str, str]:
        """Configuration des noms de base personnalisés pour certains personnages Evolve"""
        return {
            "Mahoraga": "Megumi Fushiguro",  # Mahoraga utilise Megumi Fushiguro comme base
            # Ajouter d'autres mappages spéciaux ici
        }

    async def get_craft_recipes(self) -> List[Tuple[str, str, int, int]]:
        """Récupérer les recettes de craft avec le nombre possédé par l'utilisateur"""
        # Configuration des quantités personnalisées
        custom_requirements = self.get_custom_craft_requirements()
        
        # Récupérer automatiquement toutes les recettes basées sur les personnages Evolve existants
        cursor = await self.bot.db.db.execute("""
            SELECT name, anime FROM characters 
            WHERE rarity = 'Evolve'
            ORDER BY name
        """)
        evolve_characters = await cursor.fetchall()
        
        recipes_with_count = []
        
        for evolved_name, anime in evolve_characters:
            # Configuration des noms de base personnalisés
            custom_base_names = self.get_custom_base_names()
            
            # Utiliser le nom de base personnalisé s'il existe, sinon déduire automatiquement
            if evolved_name in custom_base_names:
                base_name = custom_base_names[evolved_name]
            else:
                # Déduire le nom de base en enlevant " Evolve"
                base_name = evolved_name.replace(" Evolve", "")
            
            # Déterminer la quantité requise (personnalisée ou par défaut)
            required_count = custom_requirements.get(evolved_name, 10)
            
            # Vérifier si le personnage de base existe, sinon essayer d'autres variations
            cursor = await self.bot.db.db.execute("""
                SELECT COUNT(*) FROM characters 
                WHERE name = ? AND anime = ? AND rarity != 'Evolve'
            """, (base_name, anime))
            base_exists = (await cursor.fetchone())[0] > 0
            
            # Si pas trouvé, essayer des variations du nom
            if not base_exists:
                # Pour "Cell Perfect Evolve" -> essayer "Cell"
                if " " in base_name:
                    first_word = base_name.split()[0]
                    cursor = await self.bot.db.db.execute("""
                        SELECT COUNT(*) FROM characters 
                        WHERE name = ? AND anime = ? AND rarity != 'Evolve'
                    """, (first_word, anime))
                    if (await cursor.fetchone())[0] > 0:
                        base_name = first_word
                        base_exists = True
            
            if base_exists:
                # Vérifier combien l'utilisateur possède du personnage de base
                cursor = await self.bot.db.db.execute("""
                    SELECT COALESCE(SUM(i.count), 0)
                    FROM inventory i
                    JOIN characters c ON i.character_id = c.id
                    WHERE i.user_id = ? AND c.name = ? AND c.anime = ?
                """, (self.user_id, base_name, anime))
                user_count = (await cursor.fetchone())[0]
                
                recipes_with_count.append((base_name, evolved_name, required_count, user_count))
        
        return recipes_with_count
    
    @discord.ui.button(label="⚡ Craft", style=discord.ButtonStyle.primary, row=0)
    async def craft_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour crafter/évoluer un personnage"""
        await interaction.response.defer()
        
        recipes = await self.get_craft_recipes()
        craftable_recipes = [r for r in recipes if r[3] >= r[2]]  # user_count >= required_count
        
        if not craftable_recipes:
            embed = discord.Embed(
                title="❌ Aucune Évolution Possible",
                description="Vous n'avez pas assez d'exemplaires pour aucune recette.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Créer un menu de sélection stylé pour les recettes disponibles
        select_view = CraftSelectionView(self.bot, self.user_id, craftable_recipes)
        
        # Obtenir les informations utilisateur
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"User {self.user_id}"
        
        embed = discord.Embed(
            title="🌌 ═══════〔 S É L E C T I O N   É V O L U T I O N 〕═══════ 🌌",
            description=f"```\n◆ Maître des Évolutions: {username} ◆\n◆ Évolutions disponibles: {len(craftable_recipes)} ◆\n```",
            color=BotConfig.RARITY_COLORS['Evolve']
        )
        
        # Afficher un aperçu des évolutions disponibles
        preview_text = ""
        for i, (base_name, evolved_name, required_count, user_count) in enumerate(craftable_recipes[:5]):
            possible_crafts = user_count // required_count
            preview_text += f"🔮 **{base_name}** ➤ **{evolved_name}** (x{possible_crafts})\n"
        
        if len(craftable_recipes) > 5:
            preview_text += f"... et {len(craftable_recipes) - 5} autres évolutions"
        
        embed.add_field(
            name="🌑 ═══〔 Évolutions Prêtes 〕═══ 🌑",
            value=preview_text if preview_text else "Aucune évolution disponible",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Instructions",
            value="```\n◆ Utilisez le menu déroulant ci-dessous\n◆ Sélectionnez l'évolution désirée\n◆ Confirmez votre choix\n```",
            inline=False
        )
        
        embed.set_footer(
            text="Shadow Roll • Sélection d'Évolution",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        await interaction.followup.send(embed=embed, view=select_view, ephemeral=True)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, row=1)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page précédente"""
        recipes = await self.get_craft_recipes()
        total_pages = (len(recipes) + self.recipes_per_page - 1) // self.recipes_per_page
        
        if self.current_page > 0:
            self.current_page -= 1
        
        embed = await self.create_craft_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, row=1)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page suivante"""
        recipes = await self.get_craft_recipes()
        total_pages = (len(recipes) + self.recipes_per_page - 1) // self.recipes_per_page
        
        if self.current_page < total_pages - 1:
            self.current_page += 1
        
        embed = await self.create_craft_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Menu", style=discord.ButtonStyle.secondary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)

class CraftSelectionView(discord.ui.View):
    """Vue de sélection pour choisir quelle recette crafter avec le style Shadow"""
    
    def __init__(self, bot, user_id: int, craftable_recipes: List[Tuple[str, str, int, int]]):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.craftable_recipes = craftable_recipes
        
        # Ajouter les options au select menu avec style amélioré
        options = []
        for i, (base_name, evolved_name, required_count, user_count) in enumerate(craftable_recipes[:25]):  # Limite Discord
            # Calculer le nombre d'évolutions possibles
            possible_crafts = user_count // required_count
            emoji = "🔮" if possible_crafts >= 1 else "⚫"
            
            options.append(discord.SelectOption(
                label=f"{emoji} {base_name} ➤ {evolved_name}",
                description=f"Coût: {required_count} exemplaires • Possédés: {user_count} • Évolutions: {possible_crafts}",
                value=str(i),
                emoji="🔮" if possible_crafts >= 1 else None
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="🌌 Choisissez votre évolution Shadow...",
                options=options,
                min_values=1,
                max_values=1
            )
            select.callback = self.recipe_selected
            self.add_item(select)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def recipe_selected(self, interaction: discord.Interaction):
        """Traiter la sélection d'une recette"""
        if not interaction.data or 'values' not in interaction.data:
            await interaction.response.send_message("❌ Erreur de sélection", ephemeral=True)
            return
            
        recipe_index = int(interaction.data['values'][0])
        base_name, evolved_name, required_count, user_count = self.craftable_recipes[recipe_index]
        
        # Créer la vue de confirmation
        confirm_view = CraftConfirmView(self.bot, self.user_id, base_name, evolved_name, required_count)
        
        # Obtenir les informations utilisateur pour l'affichage
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"User {self.user_id}"
        
        # Calculer le nombre d'évolutions possibles
        possible_crafts = user_count // required_count
        
        embed = discord.Embed(
            title="🌌 ═══════〔 C O N F I R M A T I O N   É V O L U T I O N 〕═══════ 🌌",
            description=f"```\n◆ Maître des Évolutions: {username} ◆\n```",
            color=BotConfig.RARITY_COLORS['Evolve']
        )
        
        embed.add_field(
            name="🌑 ═══〔 Évolution Sélectionnée 〕═══ 🌑",
            value=(f"```\n"
                   f"Personnage Base: {base_name}\n"
                   f"Évolution Cible: {evolved_name}\n"
                   f"Coût Requis: {required_count} exemplaires\n"
                   f"Possédés: {user_count}\n"
                   f"Évolutions possibles: {possible_crafts}\n"
                   f"```\n"
                   f"🔮 **{base_name}** ➤ **{evolved_name}**\n"
                   f"✨ Cette évolution consommera {required_count} exemplaires"),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Avertissement",
            value="```\n◆ Action irréversible\n◆ Les exemplaires seront consommés\n◆ L'évolution sera ajoutée à votre collection\n```",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Instructions",
            value="```\n✅ Confirmer - Évoluer\n❌ Annuler - Retour\n```",
            inline=True
        )
        
        embed.set_footer(
            text="Shadow Roll • Confirmation d'Évolution",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        await interaction.response.edit_message(embed=embed, view=confirm_view)

class CraftConfirmView(discord.ui.View):
    """Vue de confirmation pour l'évolution"""
    
    def __init__(self, bot, user_id: int, base_name: str, evolved_name: str, required_count: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.base_name = base_name
        self.evolved_name = evolved_name
        self.required_count = required_count
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success)
    async def confirm_craft(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmer et effectuer l'évolution"""
        await interaction.response.defer()
        
        try:
            # Vérifier encore une fois que l'utilisateur a assez de personnages
            cursor = await self.bot.db.db.execute("""
                SELECT i.id, c.id as char_id, i.count
                FROM inventory i
                JOIN characters c ON i.character_id = c.id
                WHERE i.user_id = ? AND c.name = ?
            """, (self.user_id, self.base_name))
            
            inventory_items = await cursor.fetchall()
            total_count = sum(item[2] for item in inventory_items) if inventory_items else 0
            
            if total_count < self.required_count:
                # Obtenir les informations utilisateur
                user = self.bot.get_user(self.user_id)
                username = get_display_name(user) if user else f"User {self.user_id}"
                
                embed = discord.Embed(
                    title="🌌 ═══════〔 É V O L U T I O N   I M P O S S I B L E 〕═══════ 🌌",
                    description=f"```\n◆ Maître: {username} ◆\n```",
                    color=0xff0000
                )
                embed.add_field(
                    name="❌ Ressources Insuffisantes",
                    value=(f"```\n"
                           f"Personnage: {self.base_name}\n"
                           f"Requis: {self.required_count} exemplaires\n"
                           f"Possédés: {total_count} exemplaires\n"
                           f"Manquant: {self.required_count - total_count}\n"
                           f"```\n"
                           f"🔸 Collectez plus d'exemplaires de **{self.base_name}** pour continuer l'évolution"),
                    inline=False
                )
                embed.set_footer(
                    text="Shadow Roll • Évolution Échouée",
                    icon_url=user.avatar.url if user and user.avatar else None
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Vérifier si le personnage évolué existe, sinon le créer
            cursor = await self.bot.db.db.execute(
                "SELECT id FROM characters WHERE name = ?",
                (self.evolved_name,)
            )
            evolved_char = await cursor.fetchone()
            
            if not evolved_char:
                # Créer le personnage évolué basé sur l'original
                cursor = await self.bot.db.db.execute(
                    "SELECT anime, value, image_url FROM characters WHERE name = ?",
                    (self.base_name,)
                )
                base_char_info = await cursor.fetchone()
                
                if base_char_info:
                    anime, base_value, image_url = base_char_info
                    # Valeur évoluée = valeur de base * 15 (pour compenser le coût)
                    evolved_value = base_value * 15
                    
                    await self.bot.db.db.execute("""
                        INSERT INTO characters (name, anime, rarity, value, image_url)
                        VALUES (?, ?, 'Evolve', ?, ?)
                    """, (self.evolved_name, anime, evolved_value, image_url))
                    
                    await self.bot.db.db.commit()
                    
                    # Récupérer l'ID du nouveau personnage
                    cursor = await self.bot.db.db.execute(
                        "SELECT id FROM characters WHERE name = ?",
                        (self.evolved_name,)
                    )
                    evolved_char = await cursor.fetchone()
            
            # Déduire les personnages de base de l'inventaire en gérant les counts
            characters_to_remove = self.required_count
            equipped_items = []
            
            for inventory_item in inventory_items:
                inv_id, char_id, current_count = inventory_item
                
                if characters_to_remove <= 0:
                    break
                
                # Vérifier si ce personnage est équipé
                cursor = await self.bot.db.db.execute(
                    "SELECT slot_number FROM equipment WHERE user_id = ? AND inventory_id = ?",
                    (self.user_id, inv_id)
                )
                equipped = await cursor.fetchone()
                if equipped:
                    equipped_items.append((inv_id, equipped[0]))
                    # Déséquiper le personnage
                    await self.bot.db.db.execute(
                        "DELETE FROM equipment WHERE user_id = ? AND inventory_id = ?",
                        (self.user_id, inv_id)
                    )
                
                # Calculer combien de personnages retirer de cette entrée
                to_remove_from_this = min(characters_to_remove, current_count)
                new_count = current_count - to_remove_from_this
                characters_to_remove -= to_remove_from_this
                
                if new_count <= 0:
                    # Supprimer complètement cette entrée d'inventaire
                    await self.bot.db.db.execute(
                        "DELETE FROM inventory WHERE id = ?",
                        (inv_id,)
                    )
                else:
                    # Mettre à jour le count
                    await self.bot.db.db.execute(
                        "UPDATE inventory SET count = ? WHERE id = ?",
                        (new_count, inv_id)
                    )
            
            # Ajouter le personnage évolué à l'inventaire
            await self.bot.db.db.execute("""
                INSERT INTO inventory (user_id, character_id, obtained_at)
                VALUES (?, ?, datetime('now'))
            """, (self.user_id, evolved_char[0]))
            
            await self.bot.db.db.commit()
            
            # Obtenir les informations utilisateur pour l'affichage de succès
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"
            player = await self.bot.db.get_or_create_player(self.user_id, username)
            
            # Embed de succès avec style Shadow
            embed = discord.Embed(
                title="🌌 ═══════〔 É V O L U T I O N   R É U S S I E 〕═══════ 🌌",
                description=f"```\n◆ Maître des Évolutions: {username} ◆\n🪙 Shadow Coins: {format_number(player.coins)}\n```",
                color=BotConfig.RARITY_COLORS['Evolve']
            )
            
            embed.add_field(
                name="🌑 ═══〔 Transformation Accomplie 〕═══ 🌑",
                value=(f"```\n"
                       f"Personnage Base: {self.base_name}\n"
                       f"Nouvelle Forme: {self.evolved_name}\n"
                       f"Exemplaires Consommés: {self.required_count}\n"
                       f"Rareté Obtenue: Evolve 🔮\n"
                       f"```\n"
                       f"✨ **{self.base_name}** ➤ **{self.evolved_name}**\n"
                       f"🔮 L'énergie des ténèbres a fusionné {self.required_count} âmes en une entité supérieure!"),
                inline=False
            )
            
            if equipped_items:
                embed.add_field(
                    name="⚔️ Équipement Modifié",
                    value=f"```\n◆ {len(equipped_items)} personnage(s) automatiquement déséquipés\n◆ Personnages consommés retirés des slots\n◆ Équipement disponible pour réassignation\n```",
                    inline=True
                )
            
            embed.add_field(
                name="🎯 Évolution Complete",
                value="```\n◆ Personnage ajouté à la collection\n◆ Évolution disponible immédiatement\n◆ Nouvelle puissance Shadow débloquée\n```",
                inline=True
            )
            
            embed.set_footer(
                text="Shadow Roll • Évolution Réussie",
                icon_url=user.avatar.url if user and user.avatar else None
            )
            
            # Créer une nouvelle vue vide pour désactiver les interactions
            empty_view = discord.ui.View()
            empty_view.timeout = 1
            
            await interaction.edit_original_response(embed=embed, view=empty_view)
            
        except Exception as e:
            logger.error(f"Erreur lors du craft: {e}")
            
            # Obtenir les informations utilisateur pour l'affichage d'erreur
            user = self.bot.get_user(self.user_id)
            username = get_display_name(user) if user else f"User {self.user_id}"
            
            embed = discord.Embed(
                title="🌌 ═══════〔 E R R E U R   É V O L U T I O N 〕═══════ 🌌",
                description=f"```\n◆ Maître: {username} ◆\n```",
                color=0xff0000
            )
            embed.add_field(
                name="❌ Échec de la Transformation",
                value=(f"```\n"
                       f"Personnage: {self.base_name}\n"
                       f"Évolution Cible: {self.evolved_name}\n"
                       f"Statut: Échec technique\n"
                       f"```\n"
                       f"🔸 Une erreur inattendue s'est produite lors de l'évolution\n"
                       f"⚡ Réessayez dans quelques instants\n"
                       f"🛠️ Contactez un administrateur si le problème persiste"),
                inline=False
            )
            embed.set_footer(
                text="Shadow Roll • Erreur d'Évolution",
                icon_url=user.avatar.url if user and user.avatar else None
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel_craft(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Annuler l'évolution avec style Shadow"""
        # Obtenir les informations utilisateur
        user = self.bot.get_user(self.user_id)
        username = get_display_name(user) if user else f"User {self.user_id}"
        
        embed = discord.Embed(
            title="🌌 ═══════〔 É V O L U T I O N   A N N U L É E 〕═══════ 🌌",
            description=f"```\n◆ Maître: {username} ◆\n```",
            color=0xff9900
        )
        
        embed.add_field(
            name="🌑 ═══〔 Évolution Interrompue 〕═══ 🌑",
            value=(f"```\n"
                   f"Personnage: {self.base_name}\n"
                   f"Évolution Cible: {self.evolved_name}\n"
                   f"Statut: Annulée par l'utilisateur\n"
                   f"```\n"
                   f"🔸 L'évolution de **{self.base_name}** a été annulée\n"
                   f"⚡ Vos personnages restent intacts\n"
                   f"🔮 Vous pouvez réessayer à tout moment"),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Retour",
            value="```\n◆ Évolution annulée avec succès\n◆ Aucun personnage consommé\n◆ Retour au menu d'évolution\n```",
            inline=False
        )
        
        embed.set_footer(
            text="Shadow Roll • Évolution Annulée",
            icon_url=user.avatar.url if user and user.avatar else None
        )
        
        # Créer une nouvelle vue vide pour désactiver les interactions
        empty_view = discord.ui.View()
        empty_view.timeout = 1
        
        await interaction.response.edit_message(embed=embed, view=empty_view)

async def setup_craft_commands(bot):
    """Configuration des commandes de craft"""
    
    @bot.tree.command(name="craft", description="Ouvrir l'atelier d'évolution")
    async def craft_command(interaction: discord.Interaction):
        """Commande slash pour ouvrir le système de craft"""
        try:
            username = get_display_name(interaction.user)
            player = await bot.db.get_or_create_player(interaction.user.id, username)
            
            if player.is_banned:
                await interaction.response.send_message(BotConfig.MESSAGES['banned'], ephemeral=True)
                return
            
            view = CraftView(bot, interaction.user.id)
            embed = await view.create_craft_embed()
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in craft command: {e}")
            await interaction.response.send_message("❌ Erreur lors de l'ouverture de l'atelier.", ephemeral=True)
    
    logger.info("Craft system commands setup completed")