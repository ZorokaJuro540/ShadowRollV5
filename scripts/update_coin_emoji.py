#!/usr/bin/env python3
"""
Script pour remplacer tous les emojis d'argent par l'emoji personnalisé
"""

import os
import re
from pathlib import Path

def update_coin_emojis():
    """Remplace tous les emojis d'argent par l'emoji personnalisé"""
    
    # L'emoji personnalisé
    custom_coin = "🪙"
    
    # Pattern pour les emojis d'argent
    patterns = [
        (r'🪙', custom_coin),
        (r'🌟', custom_coin),  # Si utilisé pour les pièces
        (r'🪙', custom_coin),  # Emoji argent qui s'envole
        (r'🪙', custom_coin),  # Billets
        (r'🪙', custom_coin),  # Dollar
        (r'🪙', custom_coin),  # Euro
        (r'🪙', custom_coin),  # Livre
    ]
    
    # Fichiers à exclure
    exclude_files = {
        'update_coin_emoji.py',
        '__pycache__',
        '.git',
        'node_modules',
        '.replit',
        'uv.lock'
    }
    
    # Extensions à traiter
    extensions = {'.py', '.md'}
    
    # Compter les remplacements
    total_replacements = 0
    files_modified = 0
    
    # Parcourir tous les fichiers Python
    for root, dirs, files in os.walk('.'):
        # Exclure certains dossiers
        dirs[:] = [d for d in dirs if d not in exclude_files]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions) and file not in exclude_files:
                file_path = Path(root) / file
                
                try:
                    # Lire le fichier
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    file_replacements = 0
                    
                    # Appliquer tous les remplacements
                    for pattern, replacement in patterns:
                        matches = len(re.findall(pattern, content))
                        if matches > 0:
                            content = re.sub(pattern, replacement, content)
                            file_replacements += matches
                    
                    # Sauvegarder si des changements ont été faits
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"✅ {file_path}: {file_replacements} remplacements")
                        files_modified += 1
                        total_replacements += file_replacements
                        
                except Exception as e:
                    print(f"❌ Erreur avec {file_path}: {e}")
    
    print(f"\n🎉 Terminé!")
    print(f"📁 Fichiers modifiés: {files_modified}")
    print(f"🔄 Total remplacements: {total_replacements}")
    
    # Cas spéciaux à vérifier manuellement
    special_cases = [
        "modules/shop_new.py - Vérifier les icônes de catégories",
        "modules/admin*.py - Vérifier les boutons d'administration",
        "modules/enhanced_menu.py - Vérifier l'affichage des coins",
    ]
    
    if special_cases:
        print(f"\n⚠️  Cas spéciaux à vérifier manuellement:")
        for case in special_cases:
            print(f"   • {case}")

if __name__ == "__main__":
    print("🚀 Début du remplacement des emojis d'argent...")
    update_coin_emojis()