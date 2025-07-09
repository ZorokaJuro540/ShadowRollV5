"""
Script de synchronisation complète des personnages Shadow Roll
Initialise le système de persistance et synchronise tous les personnages
"""

import asyncio
import logging
from character_manager import CharacterManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Synchronise tous les personnages vers le système de persistance"""
    print("🌌 Shadow Roll - Synchronisation Complète des Personnages")
    print("=" * 60)
    
    try:
        # Initialiser le gestionnaire
        manager = CharacterManager()
        await manager.initialize()
        
        print("✅ Gestionnaire de personnages initialisé")
        
        # Synchroniser tous les personnages
        print("\n🔄 Synchronisation en cours...")
        characters = await manager.sync_all_characters()
        
        if characters:
            print(f"✅ {len(characters)} personnages synchronisés avec succès")
            
            # Afficher les statistiques
            stats = await manager.get_statistics()
            print(f"\n📊 Statistiques:")
            print(f"   Total: {stats['total_characters']}")
            print(f"   Avec images: {stats['with_images']}")
            print(f"   Sans images: {stats['without_images']}")
            
            print(f"\n🎯 Par rareté:")
            for rarity, count in sorted(stats['by_rarity'].items()):
                print(f"   {rarity}: {count}")
            
            print(f"\n📺 Top 5 animes:")
            sorted_anime = sorted(stats['by_anime'].items(), key=lambda x: x[1], reverse=True)
            for anime, count in sorted_anime[:5]:
                print(f"   {anime}: {count}")
            
            # Créer une sauvegarde
            backup_file = await manager.backup_characters()
            if backup_file:
                print(f"\n💾 Sauvegarde créée: {backup_file}")
            
            print(f"\n✅ Synchronisation terminée!")
            print(f"📁 Fichier principal: all_characters.json")
            print(f"📁 Sauvegarde: {backup_file}")
            
        else:
            print("❌ Aucun personnage trouvé à synchroniser")
            
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {e}")
        logger.error(f"Erreur de synchronisation: {e}")

if __name__ == "__main__":
    asyncio.run(main())