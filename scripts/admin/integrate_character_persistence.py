"""
Script d'intégration pour la persistance des personnages admin
Modifie les commandes admin existantes pour utiliser le gestionnaire centralisé
"""

import asyncio
import logging
from character_manager import CharacterManager

logger = logging.getLogger(__name__)

async def update_admin_commands():
    """Met à jour les commandes admin pour utiliser la persistance"""
    
    # Initialiser le gestionnaire
    manager = CharacterManager()
    await manager.initialize()
    
    print("🔄 Synchronisation initiale des personnages...")
    characters = await manager.sync_all_characters()
    print(f"✅ {len(characters)} personnages synchronisés")
    
    # Afficher les statistiques
    stats = await manager.get_statistics()
    print("\n📊 Statistiques des personnages:")
    print(f"   Total: {stats['total_characters']}")
    print(f"   Avec images: {stats['with_images']}")
    print(f"   Sans images: {stats['without_images']}")
    print(f"   Créés par admin: {stats['by_source']['admin']}")
    print(f"   Base de données: {stats['by_source']['database']}")
    
    print("\n🎯 Par rareté:")
    for rarity, count in stats['by_rarity'].items():
        print(f"   {rarity}: {count}")
    
    print("\n📺 Top 10 animes (par nombre de personnages):")
    sorted_anime = sorted(stats['by_anime'].items(), key=lambda x: x[1], reverse=True)
    for anime, count in sorted_anime[:10]:
        print(f"   {anime}: {count}")
    
    # Créer une sauvegarde
    backup_file = await manager.backup_characters()
    if backup_file:
        print(f"\n💾 Sauvegarde créée: {backup_file}")
    
    return manager

async def main():
    """Fonction principale"""
    print("🌌 Shadow Roll - Intégration Persistance Personnages")
    print("=" * 60)
    
    try:
        manager = await update_admin_commands()
        print("\n✅ Intégration terminée avec succès!")
        print("\nLes commandes admin suivantes utiliseront maintenant la persistance:")
        print("• !createchar - Personnages sauvegardés automatiquement")
        print("• !addimage - Images mises à jour dans le stockage")
        print("• Tous les nouveaux personnages seront persistants")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'intégration: {e}")
        logger.error(f"Erreur d'intégration: {e}")

if __name__ == "__main__":
    asyncio.run(main())