"""
Marketplace cleanup script for Shadow Roll Bot
Automatically cleans up expired listings every hour
"""

import asyncio
import logging
from datetime import datetime
from core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketplace_cleanup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MarketplaceCleanup:
    def __init__(self):
        self.db = DatabaseManager()
        self.running = False

    async def start(self):
        """Start the cleanup service"""
        await self.db.initialize()
        self.running = True
        logger.info("Marketplace cleanup service started")
        
        try:
            while self.running:
                await self.cleanup_expired_listings()
                # Wait 1 hour before next cleanup
                await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in cleanup service: {e}")
        finally:
            await self.db.close()

    async def cleanup_expired_listings(self):
        """Clean up expired marketplace listings"""
        try:
            await self.db.cleanup_expired_listings()
            logger.info(f"Marketplace cleanup completed at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error during marketplace cleanup: {e}")

    def stop(self):
        """Stop the cleanup service"""
        self.running = False
        logger.info("Marketplace cleanup service stopped")

async def main():
    """Main function to run marketplace cleanup"""
    cleanup_service = MarketplaceCleanup()
    try:
        await cleanup_service.start()
    except KeyboardInterrupt:
        cleanup_service.stop()
        logger.info("Marketplace cleanup service interrupted by user")

if __name__ == "__main__":
    asyncio.run(main())