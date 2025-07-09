# Structure Organisée du Projet Shadow Roll Bot

## Vue d'ensemble

Le projet Shadow Roll Bot est maintenant organisé dans une structure claire et logique pour faciliter la maintenance et le développement.

## Structure des Dossiers

```
shadow-roll-bot/
├── 📁 core/                    # Composants principaux du bot
│   ├── __init__.py
│   ├── bot.py                  # Classe principale du bot
│   ├── config.py               # Configuration centralisée
│   ├── database.py             # Gestionnaire de base de données
│   └── models.py               # Modèles de données
│
├── 📁 modules/                 # Modules fonctionnels
│   ├── achievements.py         # Système de succès
│   ├── admin*.py              # Modules d'administration
│   ├── commands.py            # Commandes slash
│   ├── craft_system.py        # Système de craft
│   ├── equipment.py           # Système d'équipement
│   ├── guide.py               # Guide interactif
│   ├── inventory.py           # Gestion inventaire
│   ├── menu.py                # Système de navigation
│   ├── patch_notes.py         # Notes de version
│   ├── sell.py                # Système de vente
│   ├── sets.py                # Système de séries
│   ├── shop.py                # Boutique
│   └── utils.py               # Utilitaires
│
├── 📁 scripts/                # Scripts utilitaires
│   ├── 📁 admin/              # Scripts d'administration
│   │   ├── integrate_character_persistence.py
│   │   ├── modify_character.py
│   │   └── sync_all_characters.py
│   │
│   ├── 📁 maintenance/        # Scripts de maintenance
│   │   ├── award_achievement_coins.py
│   │   ├── batch_resize.py
│   │   ├── check_duplicates.py
│   │   ├── clean_database_file.py
│   │   ├── fix_achievements.py
│   │   ├── fix_duplicates_and_organize.py
│   │   ├── image_resizer.py
│   │   └── update_database_images.py
│   │
│   └── 📁 utilities/          # Utilitaires généraux
│       ├── marketplace_cleanup.py
│       └── rankings_update.py
│
├── 📁 docs/                   # Documentation
│   ├── ADMIN_GUIDE.md         # Guide administrateur
│   ├── CHARACTER_PERSISTENCE_GUIDE.md
│   ├── GUIDE_ADMIN_SYNC.md
│   ├── PATCH_NOTES.md         # Notes de version
│   ├── PERSONNAGES_GUIDE.md   # Guide personnages
│   └── README.md              # Documentation principale
│
├── 📁 backups/                # Sauvegardes
│   ├── all_characters.json   # Sauvegarde personnages
│   └── characters_backup_*.json
│
├── 📁 assets/                 # Ressources
│   └── 📁 images/             # Images redimensionnées
│       └── [character_images].jpg
│
├── 📁 logs/                   # Fichiers de logs
│   └── bot.log
│
├── 📁 attached_assets/        # Assets attachés
│
├── main.py                    # Point d'entrée principal
├── character_manager.py       # Gestionnaire de personnages
├── fallback_images.py         # Images de secours
├── replit.md                  # Configuration projet
├── all_characters.json        # Données personnages
├── shadow_roll.db             # Base de données
├── pyproject.toml             # Configuration Python
└── uv.lock                    # Dépendances verrouillées
```

## Description des Dossiers

### 📁 `core/`
Contient les composants essentiels du bot :
- **bot.py** : Classe principale ShadowRollBot
- **config.py** : Toute la configuration (raretés, couleurs, messages)
- **database.py** : Gestionnaire SQLite avec tous les personnages
- **models.py** : Modèles de données (Character, Player, etc.)

### 📁 `modules/`
Modules fonctionnels du bot :
- **admin*** : Système d'administration complet
- **menu.py** : Interface de navigation principale
- **commands.py** : Commandes slash Discord
- **achievements.py** : Système de succès
- **inventory.py** : Gestion des collections
- Autres modules spécialisés

### 📁 `scripts/`
Scripts utilitaires organisés par catégorie :

#### `admin/`
- **modify_character.py** : Modifier personnages existants
- **sync_all_characters.py** : Synchronisation personnages
- **integrate_character_persistence.py** : Intégration persistance

#### `maintenance/`
- **fix_*.py** : Scripts de réparation
- **batch_resize.py** : Redimensionnement images
- **clean_database_file.py** : Nettoyage base
- **award_achievement_coins.py** : Attribution succès

#### `utilities/`
- **marketplace_cleanup.py** : Nettoyage marketplace
- **rankings_update.py** : Mise à jour classements

### 📁 `docs/`
Documentation complète :
- **ADMIN_GUIDE.md** : Guide des commandes admin
- **CHARACTER_PERSISTENCE_GUIDE.md** : Guide persistance
- **PATCH_NOTES.md** : Historique des versions
- **README.md** : Documentation générale

### 📁 `backups/`
Sauvegardes automatiques et manuelles :
- **all_characters.json** : Sauvegarde principale
- **characters_backup_*.json** : Sauvegardes horodatées

### 📁 `assets/`
Ressources du projet :
- **images/** : Images redimensionnées des personnages

## Fichiers Principaux

### `main.py`
Point d'entrée du bot. Lance l'application Shadow Roll.

### `character_manager.py`
Gestionnaire centralisé pour la persistance des personnages.

### `replit.md`
Configuration du projet et préférences utilisateur.

### `shadow_roll.db`
Base de données SQLite principale.

## Avantages de cette Organisation

### 🎯 **Clarté**
- Chaque type de fichier a sa place
- Structure logique et intuitive
- Séparation claire des responsabilités

### 🔧 **Maintenance**
- Scripts de maintenance groupés
- Documentation centralisée
- Sauvegardes organisées

### 📈 **Évolutivité**
- Ajout facile de nouveaux modules
- Scripts facilement catégorisables
- Structure extensible

### 👥 **Collaboration**
- Structure standard reconnue
- Documentation accessible
- Code facile à naviguer

## Utilisation

### Développement
```bash
# Lancer le bot
python main.py

# Modifier un personnage
python scripts/admin/modify_character.py

# Maintenance
python scripts/maintenance/fix_achievements.py
```

### Administration
- Interface graphique : `!admin`
- Commandes rapides : `!modifychar`, `!syncchars`
- Scripts dédiés dans `scripts/admin/`

### Documentation
- Guides complets dans `docs/`
- Configuration dans `replit.md`
- Notes de version dans `docs/PATCH_NOTES.md`

Cette organisation garantit un projet maintenu, évolutif et facile à comprendre.