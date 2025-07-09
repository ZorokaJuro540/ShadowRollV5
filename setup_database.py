"""
Script d'initialisation de la base de données pour l'hébergement externe
Crée automatiquement toutes les tables nécessaires au démarrage
"""
import asyncio
import sqlite3
import os
from core.database import DatabaseManager

async def setup_database():
    """Initialiser la base de données pour l'hébergement externe"""
    
    print("🔧 Initialisation de la base de données...")
    
    # Créer le gestionnaire de base de données
    db_manager = DatabaseManager()
    
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        print("✅ Base de données initialisée avec succès")
        
        # Vérifier que toutes les tables sont créées
        tables = await db_manager.get_all_tables()
        print(f"📊 Tables créées: {len(tables)}")
        
        # Synchroniser les personnages
        await db_manager.sync_characters()
        print("✅ Personnages synchronisés")
        
        # Fermer la connexion
        await db_manager.close()
        print("✅ Configuration terminée")
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(setup_database())