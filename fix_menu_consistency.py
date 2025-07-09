"""
Script de correction de la cohérence des menus
Assure que tous les boutons "Retour au menu" affichent le même menu de base
"""

import asyncio
import aiosqlite
import logging
from pathlib import Path
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_menu_consistency():
    """Corriger la cohérence des menus dans tous les modules"""
    
    # Patron standard pour le bouton "Retour au menu"
    standard_menu_button = '''    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)'''
    
    # Modules à corriger
    modules_to_fix = [
        'modules/unified_shop.py',
        'modules/backpack.py',
        'modules/craft_system.py',
        'modules/equipment.py',
        'modules/trade.py',
        'modules/sets.py',
        'modules/achievements.py',
        'modules/guide.py',
        'modules/character_viewer.py',
        'modules/patch_notes.py',
        'modules/shop_new.py',
        'modules/shop_system_fixed.py'
    ]
    
    corrections_made = 0
    
    for module_path in modules_to_fix:
        try:
            if Path(module_path).exists():
                logger.info(f"Correction du module: {module_path}")
                
                # Lire le contenu actuel
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Rechercher les différents patterns de boutons "Retour au menu"
                patterns = [
                    r'@discord\.ui\.button\(label=\'🏠 Menu.*?\n.*?async def back_to_menu.*?\n.*?await interaction\.response\.defer\(\).*?\n.*?from modules\.menu import.*?\n.*?view = .*?\n.*?embed = .*?\n.*?await interaction\.edit_original_response\(embed=embed, view=view\)',
                    r'@discord\.ui\.button\(label=\'🏠 Menu Principal\'.*?\n.*?async def back_to_menu.*?\n.*?await interaction\.response\.defer\(\).*?\n.*?try:.*?\n.*?from modules\.menu import.*?\n.*?embed = .*?\n.*?await interaction\.edit_original_response\(embed=embed, view=menu_view\)',
                    r'@discord\.ui\.button\(label=\'🏠 Menu Principal\'.*?\n.*?async def back_to_menu.*?\n.*?await interaction\.response\.defer\(\).*?\n.*?from modules\.menu import.*?\n.*?view = .*?\n.*?embed = await create.*?\n.*?await interaction\.edit_original_response\(embed=embed, view=view\)'
                ]
                
                # Remplacer tous les patterns par le pattern standard
                content_modified = False
                for pattern in patterns:
                    if re.search(pattern, content, re.DOTALL):
                        content = re.sub(pattern, standard_menu_button, content, flags=re.DOTALL)
                        content_modified = True
                
                # Rechercher et remplacer les implémentations spécifiques problématiques
                if 'unified_shop.py' in module_path:
                    # Correction spécifique pour unified_shop.py
                    unified_shop_pattern = r'@discord\.ui\.button\(label=\'🏠 Menu Principal\'.*?\n.*?async def back_to_menu.*?\n.*?await interaction\.response\.defer\(\).*?\n.*?try:.*?\n.*?from modules\.menu import ShadowMenuView.*?\n.*?menu_view = ShadowMenuView\(self\.bot, self\.user_id\).*?\n.*?embed = discord\.Embed\(.*?\n.*?title=.*?\n.*?description=.*?\n.*?color=.*?\n.*?\).*?\n.*?await interaction\.edit_original_response\(embed=embed, view=menu_view\).*?\n.*?except Exception as e:.*?\n.*?print\(f"Error returning to main menu: \{e\}"\).*?\n.*?# Fallback simple.*?\n.*?embed = discord\.Embed\(.*?\n.*?title=.*?\n.*?description=.*?\n.*?color=.*?\n.*?\).*?\n.*?await interaction\.edit_original_response\(embed=embed\)'
                    
                    if re.search(unified_shop_pattern, content, re.DOTALL):
                        content = re.sub(unified_shop_pattern, standard_menu_button, content, flags=re.DOTALL)
                        content_modified = True
                
                # Sauvegarder les modifications
                if content_modified:
                    with open(module_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    corrections_made += 1
                    logger.info(f"✅ Module {module_path} corrigé")
                else:
                    logger.info(f"⚪ Module {module_path} - Aucune correction nécessaire")
                    
        except Exception as e:
            logger.error(f"❌ Erreur lors de la correction de {module_path}: {e}")
    
    logger.info(f"🎯 Corrections terminées: {corrections_made} modules modifiés")


async def add_missing_menu_buttons():
    """Ajouter les boutons de menu manquants dans certains modules"""
    
    modules_needing_buttons = [
        'modules/backpack.py',
        'modules/craft_system.py',
        'modules/equipment.py'
    ]
    
    standard_menu_button = '''
    @discord.ui.button(label='🏠 Menu Principal', style=discord.ButtonStyle.primary, row=2)
    async def back_to_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        from modules.menu import ShadowMenuView, create_main_menu_embed
        view = ShadowMenuView(self.bot, self.user_id)
        embed = await create_main_menu_embed(self.bot, self.user_id)
        await interaction.edit_original_response(embed=embed, view=view)
'''
    
    for module_path in modules_needing_buttons:
        try:
            if Path(module_path).exists():
                with open(module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifier si le bouton existe déjà
                if 'back_to_menu' not in content and '🏠 Menu' not in content:
                    # Trouver la fin de la dernière classe View
                    view_classes = re.findall(r'class \w+View\(discord\.ui\.View\):.*?(?=class|\Z)', content, re.DOTALL)
                    
                    if view_classes:
                        # Ajouter le bouton à la fin de la première classe View
                        last_view_end = content.rfind('class')
                        if last_view_end > 0:
                            # Trouver la fin de la classe
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'class' in line and 'View' in line:
                                    # Trouver la fin de cette classe
                                    for j in range(i + 1, len(lines)):
                                        if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                                            # Insérer le bouton avant cette ligne
                                            lines.insert(j, standard_menu_button)
                                            break
                                    break
                            
                            content = '\n'.join(lines)
                            
                            with open(module_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            logger.info(f"✅ Bouton de menu ajouté à {module_path}")
                        
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout du bouton dans {module_path}: {e}")


async def main():
    """Fonction principale de correction"""
    print("🔧 Correction de la cohérence des menus Shadow Roll")
    print("=" * 50)
    
    await fix_menu_consistency()
    await add_missing_menu_buttons()
    
    print("\n✅ Correction terminée!")
    print("📋 Résumé des corrections:")
    print("  - Standardisation des boutons 'Retour au menu'")
    print("  - Utilisation uniforme de ShadowMenuView")
    print("  - Utilisation uniforme de create_main_menu_embed")
    print("  - Ajout des boutons manquants")


if __name__ == "__main__":
    asyncio.run(main())