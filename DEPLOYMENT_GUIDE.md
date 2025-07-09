# Guide de Déploiement - Shadow Roll Bot

## Vue d'ensemble
Ce guide vous explique comment héberger le bot Shadow Roll sur différentes plateformes d'hébergement de bots Discord.

## Prérequis
- Token Discord du bot
- Client ID de l'application Discord
- Compte sur une plateforme d'hébergement

## Configuration Discord

### 1. Créer l'application Discord
1. Allez sur https://discord.com/developers/applications
2. Cliquez sur "New Application"
3. Nommez votre application "Shadow Roll Bot"
4. Dans l'onglet "Bot", créez un nouveau bot
5. Copiez le token (gardez-le secret!)
6. Dans l'onglet "General Information", copiez l'Application ID

### 2. Configurer les permissions
Le bot nécessite ces permissions:
- Lire les messages
- Envoyer des messages
- Intégrer des liens
- Joindre des fichiers
- Utiliser les commandes d'application
- Gérer les messages
- Ajouter des réactions

## Plateformes d'hébergement supportées

### 1. Heroku (Recommandé)
```bash
# Déploiement automatique
git clone votre-repo
cd shadow-roll-bot
heroku create votre-app-name
heroku config:set DISCORD_TOKEN=votre_token
heroku config:set DISCORD_CLIENT_ID=votre_client_id
git push heroku main
```

### 2. Railway
```bash
# Connectez votre repo GitHub à Railway
# Configurez les variables d'environnement:
DISCORD_TOKEN=votre_token
DISCORD_CLIENT_ID=votre_client_id
```

### 3. Render
```bash
# Utilisez le fichier render.yaml fourni
# Configurez les variables d'environnement dans l'interface
```

### 4. Fly.io
```bash
fly launch
fly secrets set DISCORD_TOKEN=votre_token
fly secrets set DISCORD_CLIENT_ID=votre_client_id
fly deploy
```

### 5. Docker (Auto-hébergement)
```bash
# Construire l'image
docker build -t shadow-roll-bot .

# Lancer le conteneur
docker run -e DISCORD_TOKEN=votre_token -e DISCORD_CLIENT_ID=votre_client_id shadow-roll-bot
```

### 6. Docker Compose
```bash
# Créer le fichier .env
echo "DISCORD_TOKEN=votre_token" > .env
echo "DISCORD_CLIENT_ID=votre_client_id" >> .env

# Lancer avec Docker Compose
docker-compose up -d
```

## Variables d'environnement

### Obligatoires
- `DISCORD_TOKEN`: Token du bot Discord
- `DISCORD_CLIENT_ID`: ID de l'application Discord

### Optionnelles
- `LOG_LEVEL`: Niveau de log (INFO par défaut)
- `DATABASE_PATH`: Chemin de la base de données (shadow_roll.db par défaut)

## Fichiers de configuration

### Structure des fichiers
```
├── Procfile              # Heroku
├── runtime.txt           # Version Python
├── app.json             # Configuration Heroku
├── railway.toml         # Configuration Railway  
├── render.yaml          # Configuration Render
├── fly.toml             # Configuration Fly.io
├── Dockerfile           # Image Docker
├── docker-compose.yml   # Docker Compose
├── setup_database.py    # Initialisation DB
└── .env.example         # Variables d'env exemple
```

## Fonctionnalités
- 161 personnages d'anime
- Système de gacha avec 9 raretés
- Jeu "Tu préfères" avec 47 personnages féminins
- Système d'équipement et d'évolution
- Boutique et échanges
- Succès et classements
- Interface française complète

## Invite du bot
Générez un lien d'invitation avec:
```
https://discord.com/api/oauth2/authorize?client_id=VOTRE_CLIENT_ID&permissions=414464724032&scope=bot%20applications.commands
```

## Support technique
- Base de données SQLite (créée automatiquement)
- Sauvegarde automatique
- Cache de performances
- Gestion multi-serveurs
- Logging complet

## Monitoring
- Logs détaillés disponibles
- Métriques de performance
- Détection d'erreurs automatique
- Redémarrage automatique en cas d'erreur

## Sécurité
- Token sécurisé par variables d'environnement
- Pas de données sensibles dans le code
- Permissions minimales requises
- Validation des entrées utilisateur

## Coûts estimés
- Heroku: Gratuit (plan hobby) à 7$/mois
- Railway: Gratuit (500h/mois) à 5$/mois
- Render: Gratuit (750h/mois) à 7$/mois
- Fly.io: Gratuit (160h/mois) à 5$/mois

## Troubleshooting

### Problèmes courants
1. **Bot ne démarre pas**: Vérifiez le token Discord
2. **Commandes ne fonctionnent pas**: Vérifiez les permissions
3. **Base de données corrompue**: Supprimez shadow_roll.db et redémarrez
4. **Mémoire insuffisante**: Utilisez un plan payant

### Logs utiles
```bash
# Heroku
heroku logs --tail -a votre-app

# Railway
railway logs

# Docker
docker logs container_name
```

## Mise à jour
```bash
# Git
git pull origin main
git push heroku main

# Docker
docker build -t shadow-roll-bot .
docker-compose up -d --build
```

## Backup
- La base de données SQLite est automatiquement sauvegardée
- Fichiers de backup dans /data/backups/
- Sauvegarde quotidienne recommandée

---

✅ **Le bot Shadow Roll est maintenant prêt pour l'hébergement professionnel!**