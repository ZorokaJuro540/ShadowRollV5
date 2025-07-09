# Guide de Persistance des Personnages - Shadow Roll Bot

## Vue d'ensemble

Le système de persistance des personnages garantit que tous les personnages créés par les administrateurs sont automatiquement sauvegardés de manière permanente, sans affecter les inventaires des joueurs existants.

## Architecture du Système

### Composants Principaux

1. **CharacterManager** (`character_manager.py`)
   - Gestionnaire centralisé pour tous les personnages
   - Synchronisation automatique base de données ↔ fichier JSON
   - Sauvegarde persistante garantie

2. **Stockage Dual**
   - **Base de données SQLite** : Stockage principal pour le bot
   - **Fichier JSON** : Sauvegarde persistante (`all_characters.json`)
   - **Sauvegardes automatiques** : Fichiers horodatés

3. **Intégration Admin** (`modules/admin_character_persistent.py`)
   - Commandes spécialisées pour la persistance
   - Interface moderne via `!admin`
   - Commandes rapides en ligne de commande

## Nouvelles Commandes Administratives

### Commandes de Persistance

| Commande | Alias | Description |
|----------|-------|-------------|
| `!createcharpersistent` | `!createcharp`, `!ccp` | Créer un personnage avec persistance garantie |
| `!syncchars` | `!sync` | Synchroniser tous les personnages |
| `!charstats` | `!cs` | Statistiques détaillées des personnages |
| `!backupchars` | `!backup` | Créer une sauvegarde manuelle |
| `!findchar` | `!fc` | Rechercher un personnage |

### Exemples d'Utilisation

```bash
# Créer un personnage persistant
!createcharpersistent "Goku Ultra" "Dragon Ball" Mythical 5000 https://image.url

# Synchroniser tous les personnages
!syncchars

# Voir les statistiques
!charstats

# Créer une sauvegarde
!backupchars "sauvegarde_importante"

# Rechercher un personnage
!findchar Naruto
```

## Fonctionnalités Clés

### 1. Persistance Automatique
- Tous les personnages créés via admin sont automatiquement sauvegardés
- Aucune perte de données lors des redémarrages
- Synchronisation en temps réel

### 2. Interface Moderne
- Boutons Discord intuitifs via `!admin`
- Création de personnages par modal
- Persistance transparente pour l'utilisateur

### 3. Sauvegardes Multiples
- Fichier principal : `all_characters.json`
- Sauvegardes horodatées automatiques
- Sauvegardes manuelles nommées

### 4. Statistiques Avancées
- Répartition par rareté
- Top animes par nombre de personnages
- Taux de personnages avec/sans images
- Suivi des sources (base/admin)

## Structure des Données

### Fichier JSON Principal
```json
{
  "last_sync": "2025-06-28T11:10:15.146800",
  "total_characters": 161,
  "characters": [
    {
      "id": 1,
      "name": "Nom du Personnage",
      "anime": "Nom de l'Anime",
      "rarity": "Legendary",
      "value": 1500,
      "image_url": "https://...",
      "source": "admin",
      "created_at": "2025-06-28T...",
      "created_by": 123456789
    }
  ],
  "sync_info": {
    "database_characters": 155,
    "admin_created": 6,
    "base_characters": 155
  }
}
```

## Intégration avec l'Interface Admin

### Via Interface Graphique (`!admin`)
1. Cliquer sur "🎴 Personnages"
2. Utiliser "➕ Créer" pour ouvrir le modal
3. Remplir les informations
4. La persistance est automatique

### Via Commandes Directes
- Plus rapide pour les administrateurs expérimentés
- Syntaxe simple et mémorisable
- Feedback immédiat

## Avantages du Système

### Pour les Administrateurs
- **Sécurité** : Aucune perte de personnages créés
- **Simplicité** : Interface intuitive et commandes faciles
- **Contrôle** : Statistiques et sauvegardes à la demande
- **Flexibilité** : Interface moderne + commandes legacy

### Pour le Système
- **Robustesse** : Double stockage (DB + JSON)
- **Performance** : Synchronisation optimisée
- **Maintenabilité** : Code modulaire et documenté
- **Évolutivité** : Architecture extensible

## Surveillance et Maintenance

### Logs Automatiques
- Toutes les créations de personnages sont loggées
- Synchronisations tracées avec timestamps
- Erreurs documentées pour debugging

### Fichiers Générés
- `all_characters.json` : Fichier principal
- `characters_backup_YYYYMMDD_HHMMSS.json` : Sauvegardes
- Logs dans `bot.log`

### Commandes de Maintenance
```bash
# Vérifier l'état du système
!charstats

# Synchronisation manuelle
!syncchars

# Créer une sauvegarde
!backupchars "maintenance_$(date)"

# Rechercher des problèmes
!findchar "terme_recherche"
```

## Compatibilité

### Rétrocompatibilité
- Tous les personnages existants sont préservés
- Les inventaires des joueurs restent intacts
- Interface admin classique toujours fonctionnelle

### Migration Automatique
- Synchronisation initiale au démarrage
- Aucune intervention manuelle requise
- Détection automatique des nouveaux personnages

## Sécurité

### Accès Restreint
- Commandes admin uniquement
- Vérification des permissions à chaque action
- Logs de toutes les modifications

### Intégrité des Données
- Validation des raretés
- Vérification des doublons
- Sauvegarde avant modifications importantes

## Support et Dépannage

### Problèmes Courants
1. **Personnage non sauvegardé** → Utiliser `!syncchars`
2. **Fichier JSON corrompu** → Restaurer depuis sauvegarde
3. **Statistiques incorrectes** → Re-synchroniser

### Commandes de Diagnostic
```bash
!charstats          # Voir l'état général
!syncchars          # Forcer la synchronisation
!backupchars        # Créer une sauvegarde de sécurité
```

Ce système garantit une gestion robuste et persistante de tous les personnages du bot Shadow Roll.