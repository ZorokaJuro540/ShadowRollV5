# Shadow Roll Discord Bot

Un bot Discord sophistiqué offrant un jeu de collection de personnages d'anime avec système de gacha, raretés dynamiques et mécaniques de collection interactives.

## Fonctionnalités Principales

- **Système de Gacha** : Collection de personnages avec 8 niveaux de rareté
- **Interface French** : Interface complète en français avec thème "Shadow"
- **Gestion Persistante** : Sauvegarde automatique des personnages admin
- **Système d'Équipement** : Bonus passifs avec personnages ultra-rares
- **Économie Complexe** : Shadow Coins, bonus de séries, marketplace
- **Administration Avancée** : Interface moderne + commandes rapides

## Structure du Projet

```
├── core/                   # Composants principaux
├── modules/               # Modules fonctionnels
├── scripts/               # Scripts utilitaires
│   ├── admin/            # Scripts d'administration
│   ├── maintenance/      # Scripts de maintenance
│   └── utilities/        # Utilitaires généraux
├── docs/                 # Documentation
├── backups/              # Sauvegardes
└── assets/               # Ressources
```

## Installation

1. Installer les dépendances :
```bash
pip install discord.py aiosqlite
```

2. Configurer le token Discord dans les variables d'environnement :
```bash
export DISCORD_TOKEN="votre_token_ici"
```

3. Lancer le bot :
```bash
python main.py
```

## Utilisation

### Commandes Utilisateur
- `!menu` ou `/menu` : Menu principal interactif
- `!help` : Guide d'utilisation
- Navigation par boutons Discord

### Commandes Admin
- `!admin` : Interface d'administration graphique
- `!modifychar "nom" field valeur` : Modifier un personnage
- `!createcharpersistent` : Créer personnage avec persistance
- `!syncchars` : Synchroniser tous les personnages

## Configuration

### Variables d'Environnement
- `DISCORD_TOKEN` : Token du bot Discord (requis)

### Configuration Admin
Modifier `ADMIN_IDS` dans `core/config.py` :
```python
ADMIN_IDS = [
    123456789,  # Votre ID Discord
]
```

## Modification des Personnages

Pour modifier directement les personnages, éditer `core/database.py` dans la section des personnages :

```python
(1, "Nom", "Anime", "Rareté", valeur, "url_image"),
```

Puis redémarrer le bot.

## Système de Rareté

- **Common** (60%) : Personnages de base
- **Rare** (25%) : Personnages peu communs  
- **Epic** (10%) : Personnages épiques
- **Legendary** (4%) : Personnages légendaires
- **Mythical** (1%) : Personnages mythiques
- **Titan** (0.3%) : Personnages titans
- **Duo** (0.1%) : Personnages duo
- **Secret** (0.001%) : Rareté ultime
- **Evolve** (craft) : Personnages d'évolution

## Scripts Utiles

### Administration
- `scripts/admin/modify_character.py` : Interface de modification
- `scripts/admin/sync_all_characters.py` : Synchronisation

### Maintenance  
- `scripts/maintenance/batch_resize.py` : Redimensionnement images
- `scripts/maintenance/fix_achievements.py` : Réparation succès

## Documentation

- `docs/ADMIN_GUIDE.md` : Guide complet administrateur
- `docs/CHARACTER_PERSISTENCE_GUIDE.md` : Guide persistance
- `PROJECT_STRUCTURE.md` : Structure détaillée du projet

## Support

Pour toute question ou problème :
1. Consulter la documentation dans `docs/`
2. Vérifier les logs dans `logs/bot.log`
3. Utiliser les commandes de diagnostic admin

## Version

Version actuelle : v5.2.0
- Système de persistance des personnages
- 161 personnages synchronisés
- Interface d'administration complète