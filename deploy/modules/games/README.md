# Games Module - Shadow Roll Bot

## Structure du Module

Le module `games` organise tous les systèmes de jeu interactifs du bot Shadow Roll.

### Fichiers

- **`__init__.py`** - Initialisation du module et exports
- **`game_manager.py`** - Gestionnaire principal des jeux et interface Discord
- **`would_you_rather.py`** - Jeu "Tu préfères" avec système de votes
- **`README.md`** - Documentation du module

### Architecture

```
modules/games/
├── __init__.py          # Exports du module
├── game_manager.py      # Gestionnaire principal
├── would_you_rather.py  # Jeu "Tu préfères"
└── README.md           # Documentation
```

### Utilisation

Le système de jeu est intégré automatiquement au bot via `game_manager.py` et est accessible par:
- Commande: `!game` ou `!jeu` ou `!games`
- Interface: Menu avec boutons pour sélectionner les jeux

### Jeux Disponibles

1. **Tu préfères** - Jeu de votes interactif avec thème Anime Girl
   - 20 questions avec images
   - Système de votes en temps réel
   - 5 manches par partie
   - Bouton d'arrêt pour l'hôte

### Extensibilité

Pour ajouter un nouveau jeu:
1. Créer un nouveau fichier dans `modules/games/`
2. Implémenter la classe du jeu
3. Ajouter le jeu au `GameManager`
4. Mettre à jour `__init__.py`