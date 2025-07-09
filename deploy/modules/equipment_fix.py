"""
Correctif automatique pour le système d'équipement
Nettoie les équipements liés à des personnages vendus
"""

import logging
import asyncio

logger = logging.getLogger(__name__)

async def cleanup_invalid_equipment(db_manager):
    """Nettoie tous les équipements liés à des personnages qui n'existent plus dans l'inventaire"""
    try:
        # Trouver tous les équipements qui pointent vers des inventory_id inexistants
        cursor = await db_manager.db.execute("""
            SELECT e.user_id, e.inventory_id, e.slot
            FROM equipment e
            LEFT JOIN inventory i ON e.inventory_id = i.id
            WHERE i.id IS NULL
        """)
        
        invalid_equipment = await cursor.fetchall()
        
        if invalid_equipment:
            # Supprimer tous les équipements invalides
            for user_id, inventory_id, slot in invalid_equipment:
                await db_manager.db.execute(
                    "DELETE FROM equipment WHERE user_id = ? AND inventory_id = ?",
                    (user_id, inventory_id)
                )
            
            await db_manager.db.commit()
            logger.info(f"Nettoyage d'équipement: {len(invalid_equipment)} équipements invalides supprimés")
            return len(invalid_equipment)
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage d'équipement: {e}")
        return 0

async def validate_user_equipment(db_manager, user_id: int):
    """Valide et nettoie l'équipement d'un utilisateur spécifique"""
    try:
        # Vérifier les équipements de l'utilisateur
        cursor = await db_manager.db.execute("""
            SELECT e.inventory_id, c.name
            FROM equipment e
            LEFT JOIN inventory i ON e.inventory_id = i.id
            LEFT JOIN characters c ON i.character_id = c.id
            WHERE e.user_id = ? AND i.id IS NULL
        """, (user_id,))
        
        invalid_equipment = await cursor.fetchall()
        
        if invalid_equipment:
            # Supprimer les équipements invalides pour cet utilisateur
            await db_manager.db.execute(
                "DELETE FROM equipment WHERE user_id = ? AND inventory_id NOT IN (SELECT id FROM inventory WHERE user_id = ?)",
                (user_id, user_id)
            )
            await db_manager.db.commit()
            logger.info(f"Équipement de l'utilisateur {user_id} nettoyé: {len(invalid_equipment)} éléments supprimés")
            return len(invalid_equipment)
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation d'équipement pour l'utilisateur {user_id}: {e}")
        return 0

async def fix_equipment_before_operation(db_manager, user_id: int):
    """Nettoie l'équipement avant toute opération d'équipement"""
    return await validate_user_equipment(db_manager, user_id)