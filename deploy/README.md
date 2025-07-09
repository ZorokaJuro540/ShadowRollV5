# Shadow Roll Bot - Déploiement

## Déploiement rapide

### Variables d'environnement requises
```
DISCORD_TOKEN=votre_token_discord
DISCORD_CLIENT_ID=votre_client_id_discord
```

### Plateformes supportées

#### Heroku
```bash
heroku create votre-app-name
heroku config:set DISCORD_TOKEN=votre_token
heroku config:set DISCORD_CLIENT_ID=votre_client_id
git push heroku main
```

#### Railway
1. Connectez votre repo GitHub
2. Configurez les variables d'environnement
3. Déployez automatiquement

#### Render
1. Connectez votre repo GitHub
2. Utilisez le fichier render.yaml
3. Configurez les variables d'environnement

#### Fly.io
```bash
fly launch
fly secrets set DISCORD_TOKEN=votre_token
fly secrets set DISCORD_CLIENT_ID=votre_client_id
fly deploy
```

#### Docker
```bash
docker build -t shadow-roll-bot .
docker run -e DISCORD_TOKEN=votre_token -e DISCORD_CLIENT_ID=votre_client_id shadow-roll-bot
```

## Fonctionnalités
- 161 personnages d'anime
- Système de gacha complet
- Jeu "Tu préfères" avec 47 personnages féminins
- Interface française
- Multi-serveurs

## Support
Consultez DEPLOYMENT_GUIDE.md pour plus de détails.
