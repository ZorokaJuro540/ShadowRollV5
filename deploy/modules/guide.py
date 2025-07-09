"""
Enhanced Guide System for Shadow Roll Bot
Complete 4-page guide with working navigation
"""

import discord
from core.config import BotConfig


class GuideView(discord.ui.View):
    """Enhanced guide view with working navigation"""

    def __init__(self, bot, user_id: int, page: int = 1):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def create_guide_embed(self) -> discord.Embed:
        """Create guide embed based on current page"""
        if self.current_page == 1:
            return self.create_basics_embed()
        elif self.current_page == 2:
            return self.create_systems_embed()
        elif self.current_page == 3:
            return self.create_equipment_embed()
        elif self.current_page == 4:
            return self.create_tips_embed()
        else:
            return self.create_basics_embed()

    def create_basics_embed(self) -> discord.Embed:
        """Page 1: Basic commands and navigation"""
        embed = discord.Embed(
            title="🌌 ═══════〔 G U I D E   D E S   O M B R E S 〕═══════ 🌌",
            description="```\n◆ Maîtrisez les pouvoirs des ténèbres... ◆\nPage 1/4 - Bases du Jeu\n```",
            color=BotConfig.RARITY_COLORS['Mythic'])

        embed.add_field(
            name="🌑 ═══〔 Commandes Principales 〕═══ 🌑",
            value=("```\n"
                   "!menu     ◆ Interface principale\n"
                   "/menu     ◆ Interface principale (slash)\n"
                   "/roll     ◆ Invocation rapide\n"
                   "/profile  ◆ Voir votre profil\n"
                   "/daily    ◆ Récupérer la bénédiction\n"
                   "/equipment ◆ Gérer l'équipement\n"
                   "/index    ◆ Index des personnages\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🌑 ═══〔 Navigation 〕═══ 🌑",
            value=("```\n"
                   "👤 Profil      ◆ Vos statistiques\n"
                   "🎲 Invocation  ◆ Invoquer des personnages\n"
                   "🧪 Recherche   ◆ Traquer un personnage\n"
                   "🎒 Collection  ◆ Voir vos personnages\n"
                   "🔮 Craft       ◆ Évolution des personnages\n"
                   "🎁 Bénédiction ◆ Récompense quotidienne\n"
                   "🛒 Vente        ◆ Revendre vos personnages\n"
                   "🎖️ Succès      ◆ Récompenses d'exploits\n"
                   "🏆 Classement  ◆ Tableau des maîtres\n"
                   "❓ Guide       ◆ Aide et informations\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🎖️ ═══〔 Fonctionnalités Avancées 〕═══ 🎖️",
            value=("```\n"
                   "🎯 Succès      ◆ Récompenses d'exploits\n"
                   "🏆 Classement  ◆ Tableau des maîtres\n"
                   "🎖️ Séries      ◆ Bonus de collection\n"
                   "⚔️ Équipement  ◆ Bonus ultra-rares\n"
                   "📜 Patch Notes ◆ Historique des MAJ\n"
                   "🔄 Marketplace ◆ Échanger avec d'autres\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 1/4")
        return embed

    def create_systems_embed(self) -> discord.Embed:
        """Page 2: Rarity system and economy"""
        embed = discord.Embed(
            title="🌌 ═══════〔 S Y S T È M E S   D E   J E U 〕═══════ 🌌",
            description="```\n◆ Comprenez les mécaniques avancées... ◆\nPage 2/4 - Raretés & Économie\n```",
            color=BotConfig.RARITY_COLORS['Legendary'])

        embed.add_field(
            name="⚡ ═══〔 Système de Rareté (10 Niveaux) 〕═══ ⚡",
            value=(f"```\n"
                   f"{BotConfig.RARITY_EMOJIS['Common']} Commun      ◆ 60.0% - Base\n"
                   f"{BotConfig.RARITY_EMOJIS['Rare']} Rare        ◆ 25.0% - Peu commun\n"
                   f"{BotConfig.RARITY_EMOJIS['Epic']} Épique      ◆ 10.0% - Rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Legendary']} Légendaire ◆ 4.0% - Très rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Mythic']} Mythique    ◆ 1.0% - Extrêmement rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Titan']} Titan       ◆ 0.3% - Ultra rare\n"
                   f"{BotConfig.RARITY_EMOJIS['Fusion']} Fusion         ◆ 0.1% - Légendaire ultime\n"
                   f"{BotConfig.RARITY_EMOJIS.get('Secret', '🌑')} Secret      ◆ 0.01% - Rareté ultime\n"
                   f"{BotConfig.RARITY_EMOJIS['Ultimate']} Ultimate    ◆ 0.001% - Rareté divine\n"
                   f"```"),
            inline=False)

        embed.add_field(
            name="🪙 ═══〔 Économie Shadow Coins 〕═══ 🪙",
            value=(f"```\n"
                   f"Coût Invocation: {BotConfig.REROLL_COST} SC\n"
                   f"Bénédiction Quotidienne: {BotConfig.DAILY_REWARD_MIN}-{BotConfig.DAILY_REWARD_MAX} SC\n"
                   f"Temps de Recharge: {BotConfig.REROLL_COOLDOWN}s\n"
                   f"Coins de Départ: {BotConfig.STARTING_COINS} SC\n"
                   f"```"),
            inline=True)

        embed.add_field(
            name="🍀 ═══〔 Système de Potions 〕═══ 🍀",
            value=("```\n"
                   "🧪 Potion Rare: +50% chances Rare\n"
                   "🧪 Potion Epic: +30% chances Epic\n"
                   "🧪 Élixir Légendaire: +20% Legendary\n"
                   "🧪 Sérum Mythique: +15% Mythic\n"
                   "⚠️ N'affectent PAS Titan/Fusion/Secret\n"
                   "Achat via 🛒 Boutique\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="📊 ═══〔 Statistiques de Collection 〕═══ 📊",
            value=("```\n"
                   "📚 Index: Tous les 151 personnages\n"
                   "🎖️ 21 séries d'anime complètes\n"
                   "🏆 Classement par coins/collection\n"
                   "🎯 Système de succès avec récompenses\n"
                   "🔄 Marketplace pour échanger\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 2/4")
        return embed

    def create_equipment_embed(self) -> discord.Embed:
        """Page 3: Equipment and bonus systems"""
        embed = discord.Embed(
            title="⚔️ ═══════〔 S Y S T È M E   É Q U I P E M E N T 〕═══════ ⚔️",
            description="```\n◆ Maîtrisez les bonus ultimes... ◆\nPage 3/4 - Équipement & Bonus\n```",
            color=BotConfig.RARITY_COLORS['Titan'])

        embed.add_field(
            name="⚔️ ═══〔 Équipement Ultra-Rare 〕═══ ⚔️",
            value=("```\n"
                   "🔱 Titan:  +2% chances toutes raretés\n"
                   "⭐ Fusion:    +5% Shadow Coins partout\n"
                   "🌑 Secret: +3% chances + 3% coins\n"
                   "\n"
                   "• Maximum 3 personnages équipés\n"
                   "• Bonus appliqués PARTOUT dans le jeu\n"
                   "• Combinables avec autres bonus\n"
                   "• Gestion via ⚔️ Équipement ou /equipment\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🎖️ ═══〔 Bonus de Séries 〕═══ 🎖️",
            value=("```\n"
                   "Complétez des séries d'anime:\n"
                   "• Akatsuki (Naruto): +1% rareté globale\n"
                   "• Straw Hat Pirates: +15% coins\n"
                   "• Survey Corps: +10% coins\n"
                   "• Demon Slayer Corps: +8% coins\n"
                   "\n"
                   "23 séries complètes disponibles!\n"
                   "Voir via 🎖️ Séries\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🔥 ═══〔 Cumul des Bonus 〕═══ 🔥",
            value=("```\n"
                   "Les bonus se CUMULENT:\n"
                   "⚔️ Équipement (Titan/Fusion/Secret)\n"
                   "+ 🎖️ Séries (collections complètes)\n"
                   "+ 🍀 Potions (temporaires)\n"
                   "= 🔥 Total affiché en temps réel\n"
                   "\n"
                   "Visible à chaque invocation!\n"
                   "Affichage deux colonnes moderne\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🎯 ═══〔 Applications des Bonus 〕═══ 🎯",
            value=("```\n"
                   "Les bonus s'appliquent à:\n"
                   "🎲 Chances d'invocation de personnages\n"
                   "🎁 Bénédictions quotidiennes\n"
                   "🪙 Ventes de personnages au marché\n"
                   "🏆 Récompenses de succès\n"
                   "🔄 Toutes transactions économiques\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 3/4")
        return embed

    def create_tips_embed(self) -> discord.Embed:
        """Page 4: Advanced tips and strategies"""
        embed = discord.Embed(
            title="🪙 ═══════〔 S T R A T É G I E S   A V A N C É E S 〕═══════ 🪙",
            description="```\n◆ Devenez un maître des ombres... ◆\nPage 4/4 - Conseils & Stratégies\n```",
            color=BotConfig.RARITY_COLORS['Mythic'])

        embed.add_field(
            name="🎯 ═══〔 Stratégies d'Invocation 〕═══ 🎯",
            value=("```\n"
                   "• Récupérez votre bénédiction CHAQUE jour\n"
                   "• Équipez des Titans pour +2% de chances\n"
                   "• Complétez des séries pour des bonus\n"
                   "• Utilisez des potions avant les sessions\n"
                   "• Vendez les doublons de Common/Rare\n"
                   "• Gardez au moins 1000 SC de réserve\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="💎 ═══〔 Gestion de Collection 〕═══ 💎",
            value=("```\n"
                   "• Gardez TOUS les ultra-rares (Titan+)\n"
                   "• Équipez les meilleurs pour les bonus\n"
                   "• Complétez les séries d'anime\n"
                   "• Surveillez l'Index pour progression\n"
                   "• Vendez intelligemment les doublons\n"
                   "• Utilisez le Marketplace pour échanger\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="🏆 ═══〔 Optimisation Économique 〕═══ 🏆",
            value=("```\n"
                   "• Équipez des Duos pour +5% coins\n"
                   "• Complétez les succès pour bonus\n"
                   "• Planifiez achats de potions\n"
                   "• Gardez SC de réserve pour occasions\n"
                   "• Utilisez classement comme objectif\n"
                   "• Marketplace = profit à long terme\n"
                   "```"),
            inline=True)

        embed.add_field(
            name="⚡ ═══〔 Fonctionnalités Avancées 〕═══ ⚡",
            value=("```\n"
                   "• Bonus visibles à chaque invocation\n"
                   "• Secret = 0.001% chance seulement\n"
                   "• Séries complètes = bonus permanents\n"
                   "• Potions n'affectent pas ultra-rares\n"
                   "• 151 personnages total disponibles\n"
                   "• Marketplace pour échanges joueurs\n"
                   "```"),
            inline=False)

        embed.add_field(
            name="🌑 ═══〔 Secrets du Système 〕═══ 🌑",
            value=("```\n"
                   "• Layout deux colonnes pour clarté\n"
                   "• Affichage en temps réel des bonus\n"
                   "• Navigation fluide sans spam messages\n"
                   "• Patch notes avec historique complet\n"
                   "• Admin commands pour modération\n"
                   "• Architecture modulaire pour évolution\n"
                   "```"),
            inline=False)

        embed.set_footer(text=f"Shadow Roll Bot {BotConfig.VERSION} • Page 4/4")
        return embed

    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = await self.create_guide_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < 4:
            self.current_page += 1
            embed = await self.create_guide_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='🎯 Bases', style=discord.ButtonStyle.success, row=1)
    async def basics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        embed = await self.create_guide_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='⚡ Systèmes', style=discord.ButtonStyle.success, row=1)
    async def systems_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 2
        embed = await self.create_guide_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='⚔️ Équipement', style=discord.ButtonStyle.success, row=1)
    async def equipment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 3
        embed = await self.create_guide_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🪙 Stratégies', style=discord.ButtonStyle.success, row=1)
    async def tips_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 4
        embed = await self.create_guide_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)