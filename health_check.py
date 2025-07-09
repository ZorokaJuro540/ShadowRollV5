"""
Health check endpoint pour l'hébergement externe
Permet aux plateformes de vérifier que le bot fonctionne
"""
import asyncio
import aiohttp
from aiohttp import web
import logging
import os
from datetime import datetime
import json

logger = logging.getLogger('health_check')

class HealthCheckServer:
    """Serveur de health check pour l'hébergement externe"""
    
    def __init__(self, port=8080):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.start_time = datetime.now()
        self.bot_status = "starting"
        self.last_heartbeat = None
    
    def setup_routes(self):
        """Configurer les routes du serveur"""
        self.app.router.add_get('/', self.health_check)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.detailed_status)
        self.app.router.add_post('/heartbeat', self.heartbeat)
    
    async def health_check(self, request):
        """Endpoint de health check basique"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "bot_status": self.bot_status
        })
    
    async def detailed_status(self, request):
        """Endpoint de statut détaillé"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "start_time": self.start_time.isoformat(),
            "uptime": str(datetime.now() - self.start_time),
            "bot_status": self.bot_status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "environment": {
                "python_version": os.sys.version,
                "discord_token_set": bool(os.getenv('DISCORD_TOKEN')),
                "client_id_set": bool(os.getenv('DISCORD_CLIENT_ID')),
                "log_level": os.getenv('LOG_LEVEL', 'INFO')
            }
        })
    
    async def heartbeat(self, request):
        """Endpoint pour recevoir les heartbeats du bot"""
        try:
            data = await request.json()
            self.bot_status = data.get('status', 'unknown')
            self.last_heartbeat = datetime.now()
            
            return web.json_response({
                "status": "heartbeat_received",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Erreur heartbeat: {e}")
            return web.json_response({
                "status": "error",
                "error": str(e)
            }, status=400)
    
    async def start_server(self):
        """Démarrer le serveur de health check"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        logger.info(f"✅ Serveur health check démarré sur le port {self.port}")
        return runner

async def send_heartbeat(status="running"):
    """Envoyer un heartbeat au serveur de health check"""
    try:
        async with aiohttp.ClientSession() as session:
            await session.post('http://localhost:8080/heartbeat', json={
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.debug(f"Erreur envoi heartbeat: {e}")

async def main():
    """Démarrer le serveur health check en standalone"""
    logging.basicConfig(level=logging.INFO)
    
    port = int(os.getenv('PORT', 8080))
    server = HealthCheckServer(port)
    
    runner = await server.start_server()
    
    try:
        print(f"🏥 Serveur health check actif sur le port {port}")
        print("Endpoints disponibles:")
        print(f"  - http://localhost:{port}/")
        print(f"  - http://localhost:{port}/health")
        print(f"  - http://localhost:{port}/status")
        
        # Garder le serveur en marche
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("⏹️ Arrêt du serveur health check")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())