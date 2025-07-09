# 🎯 Guide de Gestion des Personnages Personnalisés

## Comment modifier vos personnages facilement

Tous vos personnages personnalisés sont maintenant définis dans le fichier `core/database.py` dans la section **VOS PERSONNAGES PERSONNALISÉS**.

### 📍 Emplacement
Fichier: `core/database.py`
Section: Ligne ~570 - Cherchez le commentaire "VOS PERSONNAGES PERSONNALISÉS"

### 🛠️ Format des personnages
```python
("Nom du Personnage", "Nom de l'Anime", "Rareté", Valeur, "URL_Image"),
```

### 🎭 Raretés disponibles
- `Common` - 60% de chance
- `Rare` - 25% de chance  
- `Epic` - 10% de chance
- `Legendary` - 4% de chance
- `Mythical` - 1% de chance
- `Titan` - 0.3% de chance
- `Duo` - 0.1% de chance
- `Secret` - 0.001% de chance (ultra rare)

### 🪙 Valeurs suggérées par rareté
- **Common**: 50-200 SC
- **Rare**: 250-500 SC
- **Epic**: 600-1000 SC
- **Legendary**: 1200-2000 SC
- **Mythical**: 3000-5000 SC
- **Titan**: 40000-60000 SC
- **Duo**: 80000-120000 SC
- **Secret**: 150000-300000 SC

### ✏️ Exemples de modifications

#### Ajouter un nouveau personnage
```python
("Saitama", "One Punch Man", "Secret", 250000, "https://example.com/saitama.gif"),
```

#### Modifier un personnage existant
Changez simplement les valeurs dans la ligne correspondante:
```python
# Avant
("Goku and Vegeta", "Dragon Ball Z", "Duo", 100000, "https://..."),

# Après - Nouvelle valeur et nouvelle image
("Goku and Vegeta", "Dragon Ball Z", "Duo", 150000, "https://nouvelle-image.gif"),
```

#### Supprimer un personnage
Supprimez ou commentez la ligne:
```python
# ("Personnage à supprimer", "Anime", "Rareté", Valeur, "URL"),
```

### 🔄 Appliquer les changements
1. Modifiez le fichier `core/database.py`
2. Sauvegardez les changements
3. Le bot se redémarre automatiquement
4. Vos modifications sont appliquées instantanément

### 🎬 URLs d'images/GIFs
- Utilisez des URLs directes vers des images (jpg, png, gif)
- Les GIFs animés rendent les personnages plus vivants
- Préférez des images de bonne qualité (1920x1080 recommandé)

### ⚠️ Important
- Respectez la syntaxe Python (virgules, guillemets)
- Chaque ligne se termine par une virgule
- Les noms de personnages doivent être uniques
- Redémarrez le bot après modification

### 🚀 Avantages de cette méthode
- ✅ Modification facile et rapide
- ✅ Pas besoin de commandes Discord
- ✅ Contrôle total sur vos personnages
- ✅ Sauvegarde automatique
- ✅ Synchronisation instantanée