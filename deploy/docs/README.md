# Shadow Roll Discord Bot v2.0

Un bot Discord de gacha inspiré de "The Eminence in Shadow" avec système de collection de personnages d'anime, économie et interface française élégante.

## Fonctionnalités

### 🎲 Système d'Invocation
- Invocation de personnages d'anime aléatoires
- Système de rareté pondéré (Commun → Mythique)
- Cooldown et coût par invocation
- Interface interactive avec boutons Discord

### 🎒 Collection & Inventaire
- Système de collection avec personnages uniques
- Pagination et organisation par rareté
- Statistiques détaillées de collection
- Valeurs économiques des personnages

### 🪙 Économie Shadow Coins
- Monnaie virtuelle "Shadow Coins"
- Récompenses quotidiennes
- Système de progression économique
- Valeurs basées sur la rareté

### 🏆 Système de Succès
- Succès de progression (invocations, collection)
- Récompenses automatiques en pièces
- Suivi des jalons de progression
- Interface de visualisation

### 👑 Système d'Administration
- Commandes administrateur sécurisées
- Création/suppression de personnages
- Gestion des utilisateurs (ban/unban)
- Manipulation d'économie

## Architecture du Projet

```
shadow_roll_bot/
├── main.py                 # Point d'entrée principal
├── core/                   # Composants principaux
│   ├── __init__.py
│   ├── bot.py             # Classe bot principale
│   ├── config.py          # Configuration centralisée
│   ├── database.py        # Gestionnaire base de données
│   └── models.py          # Modèles de données
├── modules/               # Modules fonctionnels
│   ├── __init__.py
│   ├── admin.py          # Commandes administrateur
│   ├── achievements.py   # Système de succès
│   ├── commands.py       # Commandes slash
│   ├── menu.py          # Système de menus
│   └── utils.py         # Utilitaires
├── ADMIN_GUIDE.md        # Guide administrateur
└── README.md            # Documentation
```

## Installation & Configuration

### Prérequis
- Python 3.11+
- Discord.py 2.5.2+
- aiosqlite 0.21.0+

### Configuration
1. Créer une application Discord et obtenir un token bot
2. Définir la variable d'environnement `DISCORD_TOKEN`
3. Configurer les IDs administrateur dans `core/config.py`

### Lancement
```bash
python main.py
```

## Utilisation

### Commandes Principales
- `!menu` - Interface principale avec navigation par boutons
- `!help` - Guide d'utilisation complet
- `/menu` - Commande slash pour l'interface
- `/roll [amount]` - Invocation rapide de personnages
- `/profile [user]` - Affichage de profil
- `/daily` - Récupération de récompense quotidienne

### Navigation Interface
L'interface utilise un système de boutons Discord pour une navigation fluide :
- 👤 **Profil** - Statistiques personnelles et collection
- 🎲 **Invocation** - Système d'invocation de personnages
- 🎒 **Collection** - Visualisation de l'inventaire avec pagination
- 🎁 **Bénédiction** - Récompenses quotidiennes
- 🏆 **Classement** - Tableaux des meilleurs joueurs
- ❓ **Guide** - Aide et informations détaillées

### Système de Rareté
- ◆ **Commun** (60% chance) - 100 pièces
- ◇ **Rare** (25% chance) - 250 pièces
- ◈ **Épique** (10% chance) - 500 pièces
- ◉ **Légendaire** (4% chance) - 1000 pièces
- ⬢ **Mythique** (1% chance) - 2500 pièces

## Fonctionnalités Techniques

### Gestion de Base de Données
- SQLite asynchrone avec aiosqlite
- Tables optimisées pour joueurs, personnages, inventaires
- Système de synchronisation et intégrité des données
- Migrations automatiques et population initiale

### Gestion des Utilisateurs
- Correction du bug "User: Unknown" avec gestion centralisée des noms
- Système de bannissement intégré
- Cooldowns et limitations de taux
- Persistance des données utilisateur

### Interface Utilisateur
- Thème sombre futuriste "Shadow"
- Messages en français avec codes ANSI
- Navigation par boutons Discord
- Édition de messages unique pour fluidité

### Sécurité & Administration
- Vérification des permissions administrateur
- Validation des entrées utilisateur
- Gestion des erreurs robuste
- Logging complet pour débogage

## Personnages Disponibles

Le bot inclut 40+ personnages de séries populaires :
- **Naruto** - Naruto, Sasuke, Kakashi, Itachi, Madara...
- **One Piece** - Luffy, Zoro, Sanji, Ace, Shanks...
- **Dragon Ball Z** - Goku, Vegeta, Gohan, Frieza...
- **Attack on Titan** - Eren, Mikasa, Levi, Armin...

## Support & Maintenance

### Logs & Débogage
- Logs centralisés dans `bot.log`
- Niveaux de log configurables
- Gestion d'erreurs avec contexte
- Monitoring des performances

### Évolutivité
- Architecture modulaire pour extensions
- Système de configuration flexible
- Base de données extensible
- API Discord moderne

---

**Shadow Roll Bot v2.0** - "ɪ ᴀᴍ ᴀᴛᴏᴍɪᴄ"

*Créé avec passion pour les fans d'anime et l'univers de "The Eminence in Shadow"*