"""
Shadow Roll Discord Bot - Main Entry Point
Optimized for external hosting platforms
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from core.bot import ShadowRollBot
from core.config import BotConfig

def setup_logging():
    """Configure logging for external hosting"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Créer le dossier de logs s'il n'existe pas
    Path('logs').mkdir(exist_ok=True)
    
    # Configuration du logging optimisée
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger('shadow_roll_main')

def validate_environment():
    """Valide les variables d'environnement requises"""
    logger = logging.getLogger('shadow_roll_main')
    
    required_vars = ['DISCORD_TOKEN']
    optional_vars = ['DISCORD_CLIENT_ID', 'LOG_LEVEL', 'DATABASE_PATH']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")
        logger.error("Consultez le fichier .env.example pour la configuration")
        sys.exit(1)
    
    logger.info("✅ Variables d'environnement validées")
    
    # Afficher les variables optionnelles configurées
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"  {var}: {value}")

async def main():
    """Main function to run the Shadow Roll bot"""
    
    # Configuration du logging
    logger = setup_logging()
    
    logger.info("🚀 Démarrage du Shadow Roll Bot v2.0...")
    logger.info("🌟 Bot optimisé pour l'hébergement externe")
    
    # Validation de l'environnement
    validate_environment()
    
    # Validation de la configuration
    if not BotConfig.validate_config():
        logger.error("Configuration validation failed!")
        sys.exit(1)
    
    # Récupération du token
    token = BotConfig.DISCORD_TOKEN
    
    # Créer et configurer le bot
    bot = ShadowRollBot()
    
    try:
        logger.info("🔌 Connexion au gateway Discord...")
        async with bot:
            await bot.start(token)
    except KeyboardInterrupt:
        logger.info("⏹️ Bot arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur critique: {e}")
        logger.error("📋 Redémarrage automatique en cours...")
        # Pour l'hébergement externe, on re-lance le bot après une pause
        await asyncio.sleep(5)
        await main()  # Relancer le bot
    finally:
        if bot:
            logger.info("🔐 Connexion fermée proprement")

if __name__ == "__main__":
    # Gestion des signaux pour l'hébergement externe
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger('shadow_roll_main').info("⏹️ Arrêt du bot")
    except Exception as e:
        logging.getLogger('shadow_roll_main').error(f"💥 Erreur fatale: {e}")
        sys.exit(1)