"""
Script de validation complète du Shadow Roll Bot
Teste tous les composants critiques du système
"""

import asyncio
import sys
import os
import logging
sys.path.append('.')

# Configuration du logging pour les tests
logging.basicConfig(level=logging.ERROR)

async def validate_complete_system():
    """Validation complète de tous les systèmes"""
    
    print("🔥 VALIDATION COMPLÈTE DU SHADOW ROLL BOT")
    print("=" * 60)
    
    success_count = 0
    total_tests = 8
    
    # Test 1: Structure des fichiers
    print("\n📁 Test 1: Structure des fichiers...")
    try:
        critical_files = [
            'main.py', 'core/bot.py', 'core/database.py', 'core/config.py',
            'modules/menu.py', 'modules/sell.py', 'modules/commands.py',
            'modules/shop_new.py', 'modules/hunt_system.py', 'shadow_roll.db'
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Fichiers manquants: {missing_files}")
        else:
            print("✅ Tous les fichiers critiques présents")
            success_count += 1
            
    except Exception as e:
        print(f"❌ Erreur structure: {e}")
    
    # Test 2: Imports des modules
    print("\n🧩 Test 2: Imports des modules...")
    try:
        from core.bot import ShadowRollBot
        from core.database import DatabaseManager
        from core.config import BotConfig
        from modules.menu import ShadowMenuView
        from modules.sell import SellView, truncate_field_value
        from modules.commands import setup_slash_commands
        print("✅ Tous les imports critiques réussis")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
    
    # Test 3: Configuration
    print("\n⚙️ Test 3: Configuration...")
    try:
        from core.config import BotConfig
        
        # Vérifier les valeurs critiques
        assert BotConfig.VERSION is not None
        assert BotConfig.REROLL_COST > 0
        assert BotConfig.STARTING_COINS > 0
        assert len(BotConfig.RARITY_WEIGHTS) > 0
        assert len(BotConfig.RARITY_COLORS) > 0
        assert len(BotConfig.RARITY_EMOJIS) > 0
        
        print(f"✅ Configuration validée - Version {BotConfig.VERSION}")
        success_count += 1
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
    
    # Test 4: Base de données
    print("\n🗄️ Test 4: Base de données...")
    try:
        from core.database import DatabaseManager
        
        db = DatabaseManager()
        await db.initialize()
        
        # Test requête simple
        async with db.db.execute("SELECT COUNT(*) FROM characters") as cursor:
            char_count = (await cursor.fetchone())[0]
        
        async with db.db.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'") as cursor:
            table_count = (await cursor.fetchone())[0]
        
        await db.close()
        
        print(f"✅ Base de données: {char_count} personnages, {table_count} tables")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
    
    # Test 5: Système de personnages
    print("\n🎭 Test 5: Système de personnages...")
    try:
        from character_manager import CharacterManager
        
        char_manager = CharacterManager()
        await char_manager.initialize()
        
        # Test récupération par rareté
        legendary_chars = await char_manager.get_characters_by_rarity('Legendary')
        mythic_chars = await char_manager.get_characters_by_rarity('Mythic')
        
        print(f"✅ Personnages: {len(legendary_chars)} Legendary, {len(mythic_chars)} Mythic")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Erreur personnages: {e}")
    
    # Test 6: Interfaces Discord
    print("\n🖥️ Test 6: Interfaces Discord...")
    try:
        import discord
        from modules.menu import ShadowMenuView
        from modules.sell import SellView
        
        # Test de création des vues (sans interaction)
        class MockBot:
            def __init__(self):
                self.db = None
        
        mock_bot = MockBot()
        
        # Ces classes doivent pouvoir être instanciées
        menu_view = ShadowMenuView(mock_bot, 123456789)
        sell_view = SellView(mock_bot, 123456789)
        
        print("✅ Interfaces Discord: Menu et Vente validés")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Erreur interfaces: {e}")
    
    # Test 7: Utilitaires
    print("\n🔧 Test 7: Fonctions utilitaires...")
    try:
        from modules.utils import format_number, get_display_name
        from modules.text_styling import style_main_title, style_section
        from modules.sell import truncate_field_value
        
        # Test formatage
        formatted = format_number(1500000)
        assert len(formatted) > 0
        
        # Test styling
        title = style_main_title()
        section = style_section("Test", "🎯")
        assert len(title) > 0
        assert len(section) > 0
        
        # Test troncature
        long_text = "Test " * 500
        truncated = truncate_field_value(long_text, 1000)
        assert len(truncated) <= 1020  # Avec marge pour "..."
        
        print("✅ Utilitaires: Format, style et troncature OK")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Erreur utilitaires: {e}")
    
    # Test 8: Protection anti-overflow
    print("\n🛡️ Test 8: Protection anti-overflow...")
    try:
        from modules.sell import truncate_field_value
        
        # Test avec texte très long
        massive_text = "A" * 2000
        result = truncate_field_value(massive_text, 1000)
        
        if len(result) <= 1020:  # 1000 + marge pour "..."
            print(f"✅ Anti-overflow: {len(massive_text)} chars -> {len(result)} chars")
            success_count += 1
        else:
            print(f"❌ Anti-overflow défaillant: {len(result)} chars (trop long)")
            
    except Exception as e:
        print(f"❌ Erreur anti-overflow: {e}")
    
    # Résultat final
    print(f"\n🏆 RÉSULTAT FINAL: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("✅ SHADOW ROLL BOT ENTIÈREMENT OPÉRATIONNEL")
        print("\n🌟 SYSTÈMES VALIDÉS:")
        print("  • Structure des fichiers complète")
        print("  • Modules Python importables")
        print("  • Configuration validée")
        print("  • Base de données fonctionnelle")
        print("  • Système de personnages opérationnel")
        print("  • Interfaces Discord prêtes")
        print("  • Utilitaires fonctionnels")
        print("  • Protection anti-overflow active")
        return True
    else:
        print(f"❌ {total_tests - success_count} PROBLÈMES DÉTECTÉS")
        return False

if __name__ == "__main__":
    result = asyncio.run(validate_complete_system())
    print(f"\n🎯 STATUT GLOBAL: {'VALIDÉ' if result else 'ERREURS DÉTECTÉES'}")