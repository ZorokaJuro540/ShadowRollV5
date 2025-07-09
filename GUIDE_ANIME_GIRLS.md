# Guide de Configuration des Anime Girls - Jeu "Tu préfères"

## 📋 Résumé des Changements

J'ai créé un système complet pour gérer facilement les personnages d'anime girls dans ton jeu "Tu préfères". Voici ce qui a été amélioré :

### ✅ Problèmes Résolus
- **Plus de doublons du même anime** : Maintenant les matchups mélangent toujours des animes différents
- **Meilleure diversité** : 41 animes différents au lieu de quelques-uns répétés
- **Images pour tous** : Chaque personnage a son image (Discord ou Wikia)
- **Plus de choix** : 123 personnages disponibles au total

### 🎯 Anciens Problèmes
Avant, tu avais des matchups comme :
- Nami (One Piece) vs Robin (One Piece) ❌
- Hinata (Naruto) vs Sakura (Naruto) ❌
- Rem (Re:Zero) vs Emilia (Re:Zero) ❌

### ✨ Nouveaux Matchups
Maintenant tu as des choix diversifiés :
- Mikasa (Attack on Titan) vs Nezuko (Demon Slayer) ✅
- Hinata (Naruto) vs Power (Chainsaw Man) ✅
- Rem (Re:Zero) vs Miku (Quintuplets) ✅

## 📁 Fichiers Créés

### 1. `anime_girls_config.py`
**C'est ton fichier principal de configuration !**

```python
# Ajouter un nouveau personnage :
("Nom du Personnage", "Nom de l'Anime", "URL_de_l'image"),

# Exemple :
("Nezuko Kamado", "Demon Slayer", "https://cdn.discord..."),
```

### 2. `update_game_characters.py`  
Script pour générer automatiquement des matchups diversifiés et voir les statistiques.

### 3. `GUIDE_ANIME_GIRLS.md` (ce fichier)
Documentation complète du système.

## 🔧 Comment Modifier la Liste

### Ajouter des Personnages
1. Ouvre `anime_girls_config.py`
2. Trouve la section `ANIME_GIRLS_LIST = [`
3. Ajoute tes nouveaux personnages :
```python
# Nouvel anime
("Personnage 1", "Nouvel Anime", "https://image1.png"),
("Personnage 2", "Nouvel Anime", "https://image2.png"),
```

### Retirer des Personnages
Supprime simplement la ligne du personnage que tu ne veux plus.

### Changer les Images
Remplace l'URL dans la configuration :
```python
("Nom", "Anime", "nouvelle_url_image"),
```

### Générer de Nouveaux Matchups
1. Lance le script : `python update_game_characters.py`
2. Copie le code généré
3. Remplace dans `modules/games/would_you_rather.py`

## 📊 Statistiques Actuelles

- **123 personnages** au total
- **41 animes** différents représentés
- **25 matchups** dans le jeu
- **0 doublon** du même anime dans les matchups

### Top Animes (par nombre de personnages)
1. Naruto (6 personnages)
2. Quintuplets (5 personnages) 
3. My Hero Academia (5 personnages)
4. K-On! (5 personnages)
5. Re:Zero (4 personnages)
6. Et 36 autres animes...

## 🎮 Utilisation dans le Bot

Le jeu est accessible via :
- `!game` dans Discord
- Sélectionner "👧 Anime Girl"

### Format des Questions
Chaque question suit ce format :
```python
("Personnage A", "Personnage B", "Image_A", "Image_B")
```

Les images s'affichent automatiquement :
- **Image principale** : Option A (grande image)
- **Thumbnail** : Option B (petite image en coin)

## 🔄 Régénération Automatique

Pour créer de nouveaux matchups aléatoirement :

```python
from anime_girls_config import get_diverse_matchups

# Générer 20 nouveaux matchups
nouveaux_matchups = get_diverse_matchups(20)
```

## 🌟 Avantages du Nouveau Système

1. **Diversité Garantie** : Jamais 2 personnages du même anime dans un matchup
2. **Images Fiables** : URLs Discord et Wikia stables
3. **Facilité de Modification** : Un seul fichier à éditer
4. **Statistiques Claires** : Scripts pour voir la répartition
5. **Extensibilité** : Facile d'ajouter de nouveaux animes

## 💡 Conseils

- **Ajouter des animes populaires** pour plus d'engagement
- **Équilibrer le nombre de personnages** par anime (3-5 idéalement)
- **Vérifier les images** avant d'ajouter (URL valides)
- **Tester les matchups** avec le script de génération

## 🚀 Prochaines Améliorations Possibles

- Système de votes par rareté de personnage
- Thèmes par genre d'anime (shonen, seinen, etc.)
- Intégration avec la base de données du bot Shadow Roll
- Statistiques de votes des utilisateurs

---

**Maintenant tu peux facilement modifier la liste sans chercher dans le code compliqué !**