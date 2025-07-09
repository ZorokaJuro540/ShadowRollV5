"""
Script de correction complète pour Shadow Roll Bot
Corrige toutes les erreurs LSP, optimise la base de données, et améliore les performances
"""

import os
import re
import sqlite3
import logging
from pathlib import Path

def fix_discord_ui_errors():
    """Corriger les erreurs Discord UI dans tous les fichiers"""
    print("🔧 Correction des erreurs Discord UI...")
    
    files_to_fix = [
        "modules/sell.py",
        "modules/enhanced_menu.py", 
        "modules/hunt_system.py",
        "modules/menu.py"
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fixes spécifiques pour les erreurs Discord UI
                fixes = [
                    # Corriger les erreurs de disabled
                    (r'item\.disabled = True', 'if hasattr(item, "disabled"): item.disabled = True'),
                    # Corriger les erreurs de paramètres
                    (r'CharacterHuntView\(self\.bot\.db, self\.user_id\)', 'CharacterHuntView(self.user_id, self.bot.db)'),
                    # Améliorer la gestion d'erreurs
                    (r'except Exception as e:', 'except Exception as e:\n            logger.error(f"Error in {file_path}: {e}")'),
                ]
                
                for pattern, replacement in fixes:
                    content = re.sub(pattern, replacement, content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Corrigé: {file_path}")
                
            except Exception as e:
                print(f"❌ Erreur lors de la correction de {file_path}: {e}")

def optimize_database():
    """Optimiser la base de données SQLite"""
    print("🗄️  Optimisation de la base de données...")
    
    try:
        conn = sqlite3.connect('shadow_roll.db')
        cursor = conn.cursor()
        
        # Optimisations SQLite
        optimizations = [
            "PRAGMA journal_mode = WAL;",
            "PRAGMA synchronous = NORMAL;", 
            "PRAGMA cache_size = 1000;",
            "PRAGMA temp_store = memory;",
            "PRAGMA mmap_size = 268435456;",
            "VACUUM;",
            "ANALYZE;"
        ]
        
        for optimization in optimizations:
            try:
                cursor.execute(optimization)
                print(f"✅ Exécuté: {optimization}")
            except Exception as e:
                print(f"⚠️  Ignoré: {optimization} - {e}")
        
        # Créer des index manquants
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_inventory_user_id ON inventory(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_characters_rarity ON characters(rarity);", 
            "CREATE INDEX IF NOT EXISTS idx_players_coins ON players(coins);",
            "CREATE INDEX IF NOT EXISTS idx_hunts_user_id ON character_hunts(user_id);"
        ]
        
        for index in indexes:
            try:
                cursor.execute(index)
                print(f"✅ Index créé: {index}")
            except Exception as e:
                print(f"⚠️  Index ignoré: {e}")
        
        conn.commit()
        conn.close()
        print("✅ Base de données optimisée")
        
    except Exception as e:
        print(f"❌ Erreur optimisation base de données: {e}")

def fix_embed_length_issues():
    """Corriger les problèmes de longueur d'embed"""
    print("📝 Correction des problèmes d'embed...")
    
    # Créer une fonction utilitaire pour truncate les textes longs
    utility_code = '''
def truncate_field_value(text: str, max_length: int = 1000) -> str:
    """Tronquer un texte pour éviter les erreurs d'embed Discord"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def safe_embed_field(embed, name: str, value: str, inline: bool = False):
    """Ajouter un field à un embed en vérifiant la longueur"""
    if len(value) > 1024:
        value = truncate_field_value(value, 1020)
    if len(name) > 256:
        name = truncate_field_value(name, 252)
    embed.add_field(name=name, value=value, inline=inline)
'''
    
    # Ajouter cette fonction à utils.py
    try:
        with open('modules/utils.py', 'a', encoding='utf-8') as f:
            f.write('\n\n' + utility_code)
        print("✅ Fonctions utilitaires ajoutées")
    except Exception as e:
        print(f"❌ Erreur ajout utilitaires: {e}")

def fix_missing_imports():
    """Corriger les imports manquants"""
    print("📦 Correction des imports...")
    
    files_imports = {
        "modules/sell.py": [
            "from modules.utils import format_number, truncate_field_value, safe_embed_field"
        ],
        "modules/hunt_system.py": [
            "from modules.utils import format_number"
        ],
        "modules/enhanced_menu.py": [
            "from modules.utils import get_display_name, style_section"
        ]
    }
    
    for file_path, imports in files_imports.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ajouter les imports manquants au début du fichier
                lines = content.split('\n')
                import_line = max([i for i, line in enumerate(lines) if line.startswith('import ') or line.startswith('from ')], default=5)
                
                for imp in imports:
                    if imp not in content:
                        lines.insert(import_line + 1, imp)
                        import_line += 1
                
                content = '\n'.join(lines)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ Imports corrigés: {file_path}")
                
            except Exception as e:
                print(f"❌ Erreur imports {file_path}: {e}")

def create_comprehensive_fixes():
    """Créer des corrections complètes pour tous les systèmes"""
    print("🔨 Application des corrections complètes...")
    
    # Corriger le sell.py pour éviter l'erreur embed
    sell_fix = '''
            # Limit character display to prevent embed overflow
            if char_list and len("\\n".join(char_list)) > 900:
                # Reduce the list size
                max_display = min(5, len(char_list))
                char_list = char_list[:max_display]
                char_list.append("...")
                
            embed.add_field(
                name=f"🎭 Vos Personnages (Page {self.current_page})",
                value="\\n".join(char_list) if char_list else "Aucun personnage trouvé",
                inline=False
            )
'''
    
    try:
        # Appliquer la correction à sell.py
        with open('modules/sell.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la section problématique
        old_pattern = r'embed\.add_field\(\s*name=f"🎭 Vos Personnages.*?\n.*?inline=False\s*\)'
        if 'embed.add_field(' in content and 'Vos Personnages' in content:
            content = re.sub(old_pattern, sell_fix.strip(), content, flags=re.DOTALL)
            
            with open('modules/sell.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Sell.py corrigé")
        
    except Exception as e:
        print(f"❌ Erreur correction sell.py: {e}")

def main():
    """Fonction principale d'optimisation"""
    print("🚀 Début de l'optimisation complète du Shadow Roll Bot")
    print("=" * 60)
    
    fix_discord_ui_errors()
    print()
    
    fix_embed_length_issues()
    print()
    
    fix_missing_imports()
    print()
    
    create_comprehensive_fixes()
    print()
    
    optimize_database()
    print()
    
    print("=" * 60)
    print("✅ Optimisation complète terminée!")
    print("🎯 Le bot devrait maintenant fonctionner sans erreurs")

if __name__ == "__main__":
    main()