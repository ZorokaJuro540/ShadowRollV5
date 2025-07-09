"""
Patch Notes System for Shadow Roll Bot
Displays comprehensive version history and updates
"""
import discord
from discord.ext import commands
import logging
from typing import List, Dict
import re
from pathlib import Path

from core.config import BotConfig
from modules.utils import get_display_name

logger = logging.getLogger(__name__)


class PatchNotesView(discord.ui.View):
    """Patch Notes display view with navigation"""

    def __init__(self, bot, user_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 1
        self.versions_per_page = 3
        self.versions = self._load_patch_notes()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command user can interact"""
        return interaction.user.id == self.user_id

    def _load_patch_notes(self) -> List[Dict]:
        """Load and parse patch notes from markdown file"""
        try:
            patch_file = Path("docs/PATCH_NOTES.md")
            if not patch_file.exists():
                return []

            with open(patch_file, "r", encoding="utf-8") as f:
                content = f.read()

            versions = []
            current_version = None
            current_content = []
            
            lines = content.split('\n')
            
            for line in lines:
                # Check for version header (## v...)
                version_match = re.match(r'^## (v[\d\.]+.*?) - (.*?) \((.*?)\)$', line)
                if version_match:
                    # Save previous version if exists
                    if current_version:
                        versions.append({
                            'version': current_version['version'],
                            'title': current_version['title'],
                            'date': current_version['date'],
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # Start new version
                    current_version = {
                        'version': version_match.group(1),
                        'title': version_match.group(2),
                        'date': version_match.group(3)
                    }
                    current_content = []
                elif current_version and line.strip():
                    # Add content to current version (skip architecture section)
                    if not line.startswith('## Architecture'):
                        current_content.append(line)
            
            # Add the last version
            if current_version:
                versions.append({
                    'version': current_version['version'],
                    'title': current_version['title'],
                    'date': current_version['date'],
                    'content': '\n'.join(current_content).strip()
                })

            return versions

        except Exception as e:
            logger.error(f"Error loading patch notes: {e}")
            return []

    async def create_patch_notes_embed(self) -> discord.Embed:
        """Create patch notes embed with current page"""
        try:
            if not self.versions:
                embed = discord.Embed(
                    title="📜 ═══════〔 N O T E S   D E   V E R S I O N 〕═══════ 📜",
                    description="```\nAucune note de version disponible\n```",
                    color=BotConfig.RARITY_COLORS['Mythic']
                )
                return embed

            total_pages = (len(self.versions) + self.versions_per_page - 1) // self.versions_per_page
            
            # Ensure current_page is within bounds
            if self.current_page > total_pages:
                self.current_page = total_pages
            if self.current_page < 1:
                self.current_page = 1

            start_idx = (self.current_page - 1) * self.versions_per_page
            end_idx = min(start_idx + self.versions_per_page, len(self.versions))
            
            embed = discord.Embed(
                title="📜 ═══════〔 N O T E S   D E   V E R S I O N 〕═══════ 📜",
                description=f"```\n🌌 Shadow Roll - Historique des Mises à Jour 🌌\nPage {self.current_page}/{total_pages}\n```",
                color=BotConfig.RARITY_COLORS['Mythic']
            )

            # Add versions for current page
            for i in range(start_idx, end_idx):
                version = self.versions[i]
                
                # Format version content
                content = version['content']
                
                # Limit content length for Discord embed
                if len(content) > 1000:
                    content = content[:997] + "..."
                
                # Clean up markdown formatting for Discord
                content = content.replace('###', '**').replace('**', '**')
                content = re.sub(r'\*\*(.*?)\*\*:', r'**\1:**', content)
                
                embed.add_field(
                    name=f"🎯 {version['version']} - {version['title']}",
                    value=f"```\n📅 {version['date']}\n```\n{content}",
                    inline=False
                )

            # Add navigation info
            if total_pages > 1:
                embed.set_footer(
                    text=f"Shadow Roll • Page {self.current_page}/{total_pages} • {len(self.versions)} versions total"
                )
            else:
                embed.set_footer(text="Shadow Roll • Notes de Version")

            return embed

        except Exception as e:
            logger.error(f"Error creating patch notes embed: {e}")
            return discord.Embed(
                title="❌ Erreur",
                description="Impossible de charger les notes de version",
                color=0xff0000
            )

    @discord.ui.button(label='⬅️ Précédent', style=discord.ButtonStyle.secondary, row=0)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = await self.create_patch_notes_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='➡️ Suivant', style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        total_pages = (len(self.versions) + self.versions_per_page - 1) // self.versions_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            embed = await self.create_patch_notes_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label='🔄 Actualiser', style=discord.ButtonStyle.success, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh patch notes from file"""
        self.versions = self._load_patch_notes()
        embed = await self.create_patch_notes_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=1)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)