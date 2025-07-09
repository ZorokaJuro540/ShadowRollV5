"""
Vérification des corrections de cohérence des menus
Vérifie que tous les modules utilisent la même implémentation de retour au menu
"""

import os
import re
from pathlib import Path

def verify_menu_consistency():
    """Vérifier la cohérence des menus dans tous les modules"""
    
    # Pattern standard attendu
    standard_patterns = [
        r'from modules\.menu import ShadowMenuView, create_main_menu_embed',
        r'view = ShadowMenuView\(self\.bot, self\.user_id\)',
        r'embed = await create_main_menu_embed\(self\.bot, self\.user_id\)',
        r'await interaction\.edit_original_response\(embed=embed, view=view\)'
    ]
    
    # Modules clés à vérifier
    key_modules = [
        'modules/unified_shop.py',
        'modules/shop_system_fixed.py', 
        'modules/backpack.py',
        'modules/equipment.py',
        'modules/patch_notes.py',
        'modules/guide.py',
        'modules/trade.py',
        'modules/craft_system.py'
    ]
    
    results = {}
    
    for module_path in key_modules:
        if Path(module_path).exists():
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier si le module a un bouton de retour au menu
            has_menu_button = 'Menu Principal' in content or 'back_to_menu' in content
            
            if has_menu_button:
                # Vérifier la conformité avec le pattern standard
                patterns_found = []
                for pattern in standard_patterns:
                    if re.search(pattern, content):
                        patterns_found.append(True)
                    else:
                        patterns_found.append(False)
                
                conformity_score = sum(patterns_found) / len(patterns_found) * 100
                results[module_path] = {
                    'has_menu_button': True,
                    'conformity_score': conformity_score,
                    'patterns_found': patterns_found,
                    'is_compliant': conformity_score >= 75  # Au moins 3/4 patterns
                }
            else:
                results[module_path] = {
                    'has_menu_button': False,
                    'conformity_score': 0,
                    'patterns_found': [],
                    'is_compliant': True  # Pas de bouton = pas de problème
                }
    
    return results

def print_verification_results():
    """Afficher les résultats de vérification"""
    print("🔍 VÉRIFICATION DE LA COHÉRENCE DES MENUS")
    print("=" * 50)
    
    results = verify_menu_consistency()
    
    compliant_modules = 0
    total_modules_with_buttons = 0
    
    for module_path, result in results.items():
        module_name = module_path.split('/')[-1]
        
        if result['has_menu_button']:
            total_modules_with_buttons += 1
            status = "✅ CONFORME" if result['is_compliant'] else "❌ NON CONFORME"
            conformity = f"{result['conformity_score']:.0f}%"
            
            print(f"{module_name:<25} | {status:<12} | {conformity}")
            
            if result['is_compliant']:
                compliant_modules += 1
            else:
                print(f"  ⚠️ Patterns manquants dans {module_name}")
        else:
            print(f"{module_name:<25} | ⚪ PAS DE BOUTON |  N/A")
    
    print("=" * 50)
    print(f"📊 RÉSUMÉ:")
    print(f"  Modules avec boutons de menu: {total_modules_with_buttons}")
    print(f"  Modules conformes: {compliant_modules}")
    print(f"  Taux de conformité: {(compliant_modules/total_modules_with_buttons)*100:.0f}%" if total_modules_with_buttons > 0 else "  Taux de conformité: N/A")
    
    if compliant_modules == total_modules_with_buttons:
        print("✅ TOUS LES MODULES SONT CONFORMES!")
    else:
        print(f"⚠️ {total_modules_with_buttons - compliant_modules} module(s) nécessitent des corrections")

if __name__ == "__main__":
    print_verification_results()