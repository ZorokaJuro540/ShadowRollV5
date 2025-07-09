"""
Test direct du système de sac à dos pour identifier les problèmes
"""
import asyncio
import sys
sys.path.append('.')

from core.database import DatabaseManager
from modules.backpack import BackpackView
import discord
from unittest.mock import Mock

async def test_backpack_creation():
    """Tester la création directe du sac à dos"""
    
    # Initialiser la base de données
    db = DatabaseManager()
    await db.initialize()
    
    # Créer un bot mock simple
    mock_bot = Mock()
    mock_bot.db = db
    
    # ID utilisateur de test
    test_user_id = 123456789
    
    print("🎒 TEST DIRECT DU SAC À DOS")
    print("=" * 50)
    
    # Tester chaque catégorie
    categories = ['characters', 'potions', 'titles', 'equipment', 'effects']
    
    for category in categories:
        print(f"\n🔍 Test de la catégorie: {category}")
        try:
            # Créer le backpack view
            backpack = BackpackView(mock_bot, test_user_id, category)
            
            # Tester la création de l'embed
            embed = await backpack.create_backpack_embed()
            
            print(f"✅ {category}: Embed créé avec succès")
            print(f"   Titre: {embed.title}")
            print(f"   Description: {embed.description[:100] if embed.description else 'Aucune'}...")
            print(f"   Champs: {len(embed.fields)} champs")
            
            # Afficher les premiers champs
            for i, field in enumerate(embed.fields[:2]):
                print(f"   Champ {i+1}: {field.name[:50]}...")
            
        except Exception as e:
            print(f"❌ {category}: Erreur - {e}")
            import traceback
            traceback.print_exc()
    
    # Tester les fonctions de base de données spécifiques
    print(f"\n🔍 Test des fonctions de base de données:")
    try:
        titles = await db.get_player_titles(test_user_id)
        print(f"✅ get_player_titles: {len(titles)} titres")
        
        equipped = await db.get_equipped_characters(test_user_id)
        print(f"✅ get_equipped_characters: {len(equipped)} équipés")
        
        equippable = await db.get_equippable_characters(test_user_id)
        print(f"✅ get_equippable_characters: {len(equippable)} disponibles")
        
    except Exception as e:
        print(f"❌ Fonctions DB: Erreur - {e}")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_backpack_creation())