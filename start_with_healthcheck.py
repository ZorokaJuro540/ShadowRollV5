"""
Script de démarrage avec health check pour l'hébergement externe
Démarre le bot et un serveur health check en parallèle
"""
import asyncio
import logging
import os
from main import main as bot_main
from health_check import HealthCheckServer, send_heartbeat

logger = logging.getLogger('start_with_healthcheck')

async def main():
    """Démarrer le bot avec health check"""
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Démarrage du bot avec health check...")
    
    # Démarrer le serveur health check
    port = int(os.getenv('PORT', 8080))
    health_server = HealthCheckServer(port)
    runner = await health_server.start_server()
    
    # Mettre à jour le statut
    health_server.bot_status = "starting"
    
    # Fonction pour envoyer des heartbeats périodiques
    async def heartbeat_task():
        while True:
            try:
                await send_heartbeat("running")
                await asyncio.sleep(30)  # Heartbeat toutes les 30 secondes
            except Exception as e:
                logger.debug(f"Erreur heartbeat: {e}")
                await asyncio.sleep(30)
    
    # Démarrer le bot et le heartbeat en parallèle
    try:
        await asyncio.gather(
            bot_main(),
            heartbeat_task()
        )
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur: {e}")
        health_server.bot_status = "error"
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())