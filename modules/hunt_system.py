"""
Système de Recherche de Personnages - Shadow Roll Bot
Permet aux joueurs de cibler un personnage spécifique et de progresser vers son obtention
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging
from core.config import BotConfig
from core.database import DatabaseManager
from modules.utils import format_number

logger = logging.getLogger(__name__)

class CharacterHuntView(discord.ui.View):
    """Interface pour le système de recherche de personnages"""
    
    def __init__(self, user_id: int, db: DatabaseManager):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.db = db
        self.current_page = 0
        self.characters_per_page = 8
        self.selected_rarity = None
        self.search_term = ""
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def create_hunt_embed(self) -> discord.Embed:
        """Créer l'embed principal du système de recherche"""
        try:
            # Obtenir la recherche active du joueur
            hunt_data = await self.db.get_player_hunt(self.user_id)
            
            embed = discord.Embed(
                title="🧪 ═══════〔 S Y S T È M E   D E   R E C H E R C H E 〕═══════ 🧪",
                description="```\n◆ Traquez vos personnages favoris... ◆\n```",
                color=0x9d4edd
            )
            
            if hunt_data:
                # Recherche active
                character_name = hunt_data.get('character_name', 'Inconnu')
                current_progress = hunt_data.get('progress', 0)
                required_progress = hunt_data.get('required_progress', 100)
                rarity = hunt_data.get('rarity', 'Common')
                
                progress_percentage = (current_progress / required_progress) * 100
                progress_bar = "█" * int(progress_percentage // 10) + "░" * (10 - int(progress_percentage // 10))
                
                rarity_emoji = BotConfig.RARITY_EMOJIS.get(rarity, '◆')
                
                embed.add_field(
                    name="🎯 Recherche Active",
                    value=(f"```\n"
                          f"Cible: {character_name}\n"
                          f"Rareté: {rarity_emoji} {rarity}\n"
                          f"Progression: {current_progress}/{required_progress}\n"
                          f"[{progress_bar}] {progress_percentage:.1f}%\n"
                          f"```"),
                    inline=False
                )
            else:
                # Aucune recherche active
                embed.add_field(
                    name="🎯 Aucune Recherche Active",
                    value="```\nChoisissez un personnage à traquer ci-dessous!\n```",
                    inline=False
                )
            
            # Instructions
            embed.add_field(
                name="📖 Comment ça fonctionne",
                value=("```\n"
                      "• Sélectionnez un personnage à traquer\n"
                      "• Invoquez des personnages normalement\n"
                      "• Votre progression augmente à chaque invocation\n"
                      "• Obtenez automatiquement le personnage une fois la barre pleine\n"
                      "```"),
                inline=False
            )
            
            embed.set_footer(text="Shadow Roll • Système de Recherche Avancé")
            return embed
            
        except Exception as e:
            pass
            logger.error(f"Erreur création embed hunt: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger le système de recherche.",
                color=0xff0000
            )
    
    @discord.ui.select(
        placeholder="Filtrer par rareté...",
        options=[
            discord.SelectOption(label="Toutes", value="all", emoji="🪙"),
            discord.SelectOption(label="Rare", value="Rare"),
            discord.SelectOption(label="Epic", value="Epic"),
            discord.SelectOption(label="Legendary", value="Legendary"),
            discord.SelectOption(label="Mythic", value="Mythic"),
            discord.SelectOption(label="Titan", value="Titan", emoji="🔱"),
            discord.SelectOption(label="Fusion", value="Fusion", emoji="⭐"),
            discord.SelectOption(label="Secret", value="Secret", emoji="🌑"),
        ]
    )
    async def rarity_filter(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_rarity = None if select.values[0] == "all" else select.values[0]
        self.current_page = 0
        await self.update_hunt_display(interaction)
    
    @discord.ui.button(label="Rechercher", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def search_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Modal pour recherche par nom
        modal = CharacterSearchModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_hunt_display(interaction)
    
    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        characters = await self.get_filtered_characters()
        max_pages = (len(characters) - 1) // self.characters_per_page
        if self.current_page < max_pages:
            self.current_page += 1
            await self.update_hunt_display(interaction)
    
    @discord.ui.button(label="🎯 Ma Recherche Actuelle", style=discord.ButtonStyle.primary)
    async def view_current_hunt(self, interaction: discord.Interaction, button: discord.ui.Button):
        hunt_data = await self.db.get_player_hunt(self.user_id)
        if not hunt_data:
            embed = discord.Embed(
                title="🧪 Système de Recherche",
                description="Aucune recherche active.\nSélectionnez un personnage pour commencer une traque!",
                color=0x2f3136
            )
        else:
            # Récupérer les infos du personnage depuis la base
            try:
                async with self.db.db.execute(
                    "SELECT name, anime, rarity, value FROM characters WHERE id = ?", 
                    (hunt_data['character_id'],)
                ) as cursor:
                    char_row = await cursor.fetchone()
                if char_row:
                    character = {
                        'name': char_row[0],
                        'anime': char_row[1], 
                        'rarity': char_row[2],
                        'value': char_row[3]
                    }
                else:
                    character = {'name': 'Personnage inconnu', 'anime': '', 'rarity': 'Common', 'value': 0}
            except:
                character = {'name': 'Personnage inconnu', 'anime': '', 'rarity': 'Common', 'value': 0}
            
            progress_bar = self.create_progress_bar(hunt_data['progress'], hunt_data['target_progress'])
            
            embed = discord.Embed(
                title="🎯 Recherche Active",
                color=BotConfig.RARITY_COLORS.get(character['rarity'], 0x2f3136)
            )
            
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], '◆')
            embed.add_field(
                name="Personnage Ciblé",
                value=f"{rarity_emoji} **{character['name']}**\n📺 {character['anime']}",
                inline=False
            )
            
            embed.add_field(
                name="Progression",
                value=f"{progress_bar}\n`{hunt_data['progress']}/{hunt_data['target_progress']}` invocations",
                inline=False
            )
            
            if hunt_data['progress'] >= hunt_data['target_progress']:
                embed.add_field(
                    name="🎉 Prêt!",
                    value="Votre prochaine invocation garantira ce personnage!",
                    inline=False
                )
            else:
                remaining = hunt_data['target_progress'] - hunt_data['progress']
                embed.add_field(
                    name="Restant",
                    value=f"**{remaining}** invocations avant garantie",
                    inline=False
                )
            
            # Bonus de progression
            bonus_text = ""
            if hunt_data.get('daily_bonus_used', False):
                bonus_text += "✅ Bonus quotidien utilisé (+2 progression)\n"
            else:
                bonus_text += "💎 Bonus quotidien disponible (+2 progression)\n"
            
            embed.add_field(name="Bonus", value=bonus_text, inline=False)
            
            if character.get('image_url'):
                embed.set_thumbnail(url=character['image_url'])
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="❌ Arrêter Recherche", style=discord.ButtonStyle.danger)
    async def stop_hunt(self, interaction: discord.Interaction, button: discord.ui.Button):
        hunt_data = await self.db.get_player_hunt(self.user_id)
        if not hunt_data:
            embed = discord.Embed(
                title="Aucune Recherche",
                description="Vous n'avez pas de recherche active à arrêter.",
                color=0xff6b6b
            )
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)
            return
        
        # Confirmation
        confirm_view = HuntStopConfirmView(self.user_id, self.db, self)
        embed = discord.Embed(
            title="⚠️ Confirmer l'Arrêt",
            description="Êtes-vous sûr de vouloir arrêter votre recherche actuelle?\n**Toute progression sera perdue!**",
            color=0xff6b6b
        )
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=confirm_view)
        else:
            await interaction.response.edit_message(embed=embed, view=confirm_view)
    
    @discord.ui.button(label="🏠 Menu Principal", style=discord.ButtonStyle.secondary)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        from modules.menu import ShadowMenuView, create_main_menu_embed
        bot = interaction.client
        menu_view = ShadowMenuView(bot, self.user_id)
        embed = await create_main_menu_embed(bot, self.user_id)
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=menu_view)
        else:
            await interaction.response.edit_message(embed=embed, view=menu_view)
    
    async def get_filtered_characters(self) -> List[Dict]:
        """Obtenir la liste filtrée des personnages"""
        if self.search_term:
            characters = await self.db.search_characters_by_name(self.search_term)
        else:
            characters = await self.db.get_all_characters()
        
        # Convertir les objets Character en dictionnaires si nécessaire
        char_list = []
        for c in characters:
            if hasattr(c, 'id'):
                # C'est un objet Character
                char_dict = {
                    'id': getattr(c, 'id', 0),
                    'name': getattr(c, 'name', ''),
                    'anime': getattr(c, 'anime', ''),
                    'rarity': getattr(c, 'rarity', 'Common'),
                    'value': getattr(c, 'value', 0),
                    'image_url': getattr(c, 'image_url', '')
                }
            else:
                # C'est déjà un dictionnaire
                char_dict = c
            char_list.append(char_dict)
        
        # Filtrer par rareté
        if self.selected_rarity:
            char_list = [c for c in char_list if c['rarity'] == self.selected_rarity]
        
        # Exclure les raretés non chassables
        char_list = [c for c in char_list if c['rarity'] != 'Evolve']
        
        return sorted(char_list, key=lambda x: (x['rarity'], x['name']))
    
    async def update_hunt_display(self, interaction: discord.Interaction):
        """Mettre à jour l'affichage des personnages chassables"""
        characters = await self.get_filtered_characters()
        
        if not characters:
            embed = discord.Embed(
                title="🧪 Système de Recherche",
                description="Aucun personnage trouvé avec ces critères.",
                color=0x2f3136
            )
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)
            return
        
        # Pagination
        start_idx = self.current_page * self.characters_per_page
        end_idx = start_idx + self.characters_per_page
        page_characters = characters[start_idx:end_idx]
        
        embed = discord.Embed(
            title="🧪 Système de Recherche de Personnages",
            description="Choisissez un personnage à traquer. Plus vous invoquez, plus vous vous rapprochez de l'obtenir!",
            color=0x9d4edd
        )
        
        # Afficher les personnages de la page
        for i, char in enumerate(page_characters):
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(char['rarity'], '◆')
            embed.add_field(
                name=f"{i+1}. {rarity_emoji} {char['name']}",
                value=f"📺 {char['anime']}\n💎 {char['value']:,} SC",
                inline=True
            )
        
        # Informations de pagination
        total_pages = (len(characters) - 1) // self.characters_per_page + 1
        embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages} • {len(characters)} personnages")
        
        # Ajouter les boutons de sélection
        select_view = CharacterSelectView(self.user_id, self.db, page_characters, self)
        
        # Combiner les vues
        combined_view = discord.ui.View(timeout=300)
        for item in select_view.children:
            combined_view.add_item(item)
        for item in self.children:
            combined_view.add_item(item)
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=combined_view)
        else:
            await interaction.response.edit_message(embed=embed, view=combined_view)
    
    def create_progress_bar(self, current: int, target: int, length: int = 10) -> str:
        """Créer une barre de progression visuelle"""
        filled = int((current / target) * length)
        bar = "█" * filled + "░" * (length - filled)
        percentage = int((current / target) * 100)
        return f"[{bar}] {percentage}%"

class CharacterSelectView(discord.ui.View):
    """Vue pour sélectionner un personnage à chasser"""
    
    def __init__(self, user_id: int, db: DatabaseManager, characters: List[Dict], parent_view):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.db = db
        self.characters = characters
        self.parent_view = parent_view
        
        # Créer les boutons de sélection
        for i, char in enumerate(characters[:8]):  # Max 8 boutons
            button = discord.ui.Button(
                label=f"{i+1}",
                style=discord.ButtonStyle.primary,
                custom_id=f"select_{char['id']}"
            )
            button.callback = self.create_select_callback(char)
            self.add_item(button)
    
    def create_select_callback(self, character: Dict):
        async def callback(interaction: discord.Interaction):
            await self.select_character_for_hunt(interaction, character)
        return callback
    
    async def select_character_for_hunt(self, interaction: discord.Interaction, character: Dict):
        """Commencer la traque d'un personnage"""
        # Vérifier si le joueur a déjà ce personnage
        player_chars = await self.db.get_player_characters(self.user_id)
        has_character = any(pc['character_id'] == character['id'] for pc in player_chars)
        
        if has_character:
            embed = discord.Embed(
                title="❌ Personnage Déjà Possédé",
                description=f"Vous possédez déjà **{character['name']}**!\nChoisissez un personnage que vous n'avez pas.",
                color=0xff6b6b
            )
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self.parent_view)
            else:
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            return
        
        # Calculer la progression cible basée sur la rareté (beaucoup plus difficile)
        rarity_targets = {
            'Common': 50,
            'Rare': 100,
            'Epic': 200,
            'Legendary': 350,
            'Mythic': 600,
            'Titan': 1000,
            'Fusion': 1500,
            'Secret': 999  # Impossible car c'est un secret... eheh
        }
        
        target_progress = rarity_targets.get(character['rarity'], 20)
        
        # Vérification spéciale pour les personnages Secret
        if character['rarity'] == 'Secret':
            embed = discord.Embed(
                title="🌑 Secret Impossible à Traquer",
                description=f"**{character['name']}** est un personnage Secret!\n\n🤫 *Impossible car c'est un secret... eheh*",
                color=BotConfig.RARITY_COLORS.get('Secret', 0x000000)
            )
            embed.add_field(
                name="💀 Mystère des Ténèbres",
                value="Les secrets ne peuvent pas être traqués.\nIls apparaissent quand ils le décident... ou jamais.",
                inline=False
            )
            embed.add_field(
                name="🎲 Comment les obtenir?",
                value="Seule la chance pure peut révéler un Secret.\nContinuez vos invocations et espérez...",
                inline=False
            )
            if character.get('image_url'):
                embed.set_thumbnail(url=character['image_url'])
                
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self.parent_view)
            else:
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            return
        
        # Créer ou remplacer la recherche active
        success = await self.db.start_character_hunt(
            self.user_id,
            character['id'],
            target_progress
        )
        
        if success:
            rarity_emoji = BotConfig.RARITY_EMOJIS.get(character['rarity'], '◆')
            embed = discord.Embed(
                title="🎯 Recherche Commencée!",
                description=f"Vous traquez maintenant **{character['name']}**!",
                color=BotConfig.RARITY_COLORS.get(character['rarity'], 0x9d4edd)
            )
            
            embed.add_field(
                name="Personnage Ciblé",
                value=f"{rarity_emoji} **{character['name']}**\n📺 {character['anime']}",
                inline=False
            )
            
            embed.add_field(
                name="Progression Requise",
                value=f"**{target_progress}** invocations pour garantie",
                inline=False
            )
            
            embed.add_field(
                name="Comment ça marche?",
                value="• Chaque invocation augmente votre progression (+1)\n• Bonus quotidien disponible (+2 progression supplémentaire)\n• Une fois la barre pleine, votre prochaine invocation garantit ce personnage!\n• *Note: Les personnages Secret ne peuvent pas être traqués*",
                inline=False
            )
            
            if character.get('image_url'):
                embed.set_thumbnail(url=character['image_url'])
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de commencer la recherche. Réessayez plus tard.",
                color=0xff6b6b
            )
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
        else:
            await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CharacterSearchModal(discord.ui.Modal):
    """Modal pour rechercher un personnage par nom"""
    
    def __init__(self, parent_view):
        super().__init__(title="Rechercher un Personnage")
        self.parent_view = parent_view
        
        self.search_input = discord.ui.TextInput(
            label="Nom du personnage",
            placeholder="Entrez le nom du personnage à rechercher...",
            max_length=50
        )
        self.add_item(self.search_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.search_term = self.search_input.value
        self.parent_view.current_page = 0
        await self.parent_view.update_hunt_display(interaction)

class HuntStopConfirmView(discord.ui.View):
    """Vue de confirmation pour arrêter une recherche"""
    
    def __init__(self, user_id: int, db: DatabaseManager, parent_view):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.db = db
        self.parent_view = parent_view
    
    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await self.db.stop_character_hunt(self.user_id)
        
        if success:
            embed = discord.Embed(
                title="🛑 Recherche Arrêtée",
                description="Votre recherche active a été annulée.\nVous pouvez en commencer une nouvelle à tout moment.",
                color=0x2f3136
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible d'arrêter la recherche.",
                color=0xff6b6b
            )
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self.parent_view)
        else:
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel_stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Go back to hunt display
        await self.parent_view.update_hunt_display(interaction)

class HuntSystem:
    """Gestionnaire principal du système de recherche"""
    
    def __init__(self, bot, db: DatabaseManager):
        self.bot = bot
        self.db = db
    
    async def process_hunt_progress(self, user_id: int, is_daily_bonus: bool = False) -> Optional[Dict]:
        """Traiter la progression de recherche lors d'une invocation"""
        hunt_data = await self.db.get_player_hunt(user_id)
        if not hunt_data:
            return None
        
        # Calculer la progression à ajouter
        progress_gain = 1
        if is_daily_bonus and not hunt_data.get('daily_bonus_used', False):
            progress_gain = 3  # Bonus quotidien
            await self.db.mark_hunt_daily_bonus_used(user_id)
        
        # Mettre à jour la progression
        new_progress = hunt_data['progress'] + progress_gain
        await self.db.update_hunt_progress(user_id, new_progress)
        
        # Vérifier si la recherche est complète
        if new_progress >= hunt_data['target_progress']:
            return {
                'completed': True,
                'character_id': hunt_data['target_character_id'],
                'progress': new_progress,
                'target': hunt_data['target_progress']
            }
        
        return {
            'completed': False,
            'progress': new_progress,
            'target': hunt_data['target_progress'],
            'gained': progress_gain
        }
    
    async def get_hunt_bonus_character(self, user_id: int) -> Optional[Dict]:
        """Obtenir le personnage de recherche si la progression est complète"""
        hunt_data = await self.db.get_player_hunt(user_id)
        if not hunt_data or hunt_data['progress'] < hunt_data['target_progress']:
            return None
        
        character = await self.db.get_character_by_id(hunt_data['target_character_id'])
        return character
    
    async def complete_hunt(self, user_id: int) -> bool:
        """Compléter une recherche et donner le personnage"""
        hunt_data = await self.db.get_player_hunt(user_id)
        if not hunt_data:
            return False
        
        # Ajouter le personnage à l'inventaire
        await self.db.add_character_to_player(user_id, hunt_data['target_character_id'])
        
        # Supprimer la recherche active
        await self.db.stop_character_hunt(user_id)
        
        return True

async def setup_hunt_system(bot, db: DatabaseManager):
    """Configurer le système de recherche de personnages"""
    hunt_system = HuntSystem(bot, db)
    return hunt_system