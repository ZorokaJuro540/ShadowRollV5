# Shadow Roll Bot - Guide Administrateur

## Configuration Accès Admin

Pour devenir administrateur, ajoutez votre ID Discord dans `ADMIN_IDS` dans `core/config.py`:

```python
ADMIN_IDS = [
    921428727307567115,  # Remplacez par votre vrai ID Discord
    # Ajoutez plus d'IDs admin ici
]
```

## Référence Complète des Commandes Admin

### 💥 Gestion des Joueurs
- `!wipeall @user` - Supprimer toutes les données d'un joueur
- `!viewprofile @user` - Voir le profil complet d'un joueur
- `!setstatus @user ban/unban` - Bannir ou débannir un joueur
- `!resetuser @user` - Réinitialiser complètement le profil d'un joueur

### 🪙 Gestion de l'Économie
- `!givecoins @user amount` - Donner des pièces à un joueur
- `!removecoins @user amount` - Retirer des pièces à un joueur
- `!giveallcoins amount` - Donner des pièces à tous les joueurs

### 🎴 Gestion des Personnages & Pulls
- `!forcepull @user rarity` - Forcer un pull de rareté spécifique
- `!createchar nom rareté anime valeur [url]` - Créer un nouveau personnage
- `!deletechar @user nom` - Supprimer un personnage de l'inventaire
- `!setnextpull @user rareté` - Programmer le prochain pull d'un joueur
- `!clearnextpull @user` - Annuler le pull programmé
- `!givechar @user nom_personnage` - **NOUVEAU** Donner un personnage spécifique à un utilisateur
- `!givecharid @user ID` - **NOUVEAU** Donner un personnage par son ID à un utilisateur

### 🏆 Succès & Statistiques
- `!addachievement @user id` - Accorder un succès à un joueur
- `!marketstats` - Afficher les statistiques du marketplace
- `!playerstats` - Afficher les statistiques générales des joueurs

### 🖼️ Gestion des Images
- `!updateimages` - Valider et mettre à jour toutes les images
- `!searchimage nom anime` - Rechercher une image spécifique
- `!addimage nom_personnage url` - **NOUVEAU** Ajouter une image manuellement
- `!suggest` - Interface interactive pour ajouter des images manquantes

### ℹ️ Aide
- `!adminhelp` - Afficher cette aide complète dans Discord

## Exemples d'Usage

### Gestion Économique
```
!givecoins @Player123 5000
!removecoins @Spammer 1000
!giveallcoins 500
```

### Gestion des Personnages
```
!createchar "Goku Ultra Instinct" Mythical "Dragon Ball Super" 8000 https://example.com/goku_ui.png
!deletechar @Player123 "Naruto Uzumaki"
!forcepull @Player123 Legendary
!givechar @Player123 "Naruto Uzumaki"
!givechar @Player123 "Goku"
!givecharid @Player123 45
```

### Gestion des Images
```
!addimage "Naruto Uzumaki" https://example.com/naruto.png
!addimage Goku https://imgur.com/goku_image.jpg
!suggest
```

### Gestion des Joueurs
```
!resetuser @Player123
!setstatus @Troublemaker ban
!setstatus @GoodPlayer unban
!viewprofile @Player123
```

## Raretés Disponibles

- **Common** - Gris - 1,000-2,000 pièces
- **Rare** - Bleu - 3,000-5,000 pièces  
- **Epic** - Violet - 6,000-10,000 pièces
- **Legendary** - Orange - 15,000-25,000 pièces
- **Mythical** - Rouge - 30,000-45,000 pièces
- **Titan** - Violet foncé - 50,000-65,000 pièces
- **Duo** - Or brillant - 100,000+ pièces

## Notes Importantes

⚠️ **Sécurité**: Utilisez ces commandes avec précaution, certaines actions sont irréversibles.

🔄 **Redémarrage**: Certaines commandes peuvent nécessiter un redémarrage du bot.

📊 **Logs**: Toutes les actions admin sont enregistrées dans les logs du bot.

🎯 **Images**: La commande `!addimage` valide automatiquement les URLs avant ajout.

## Security Features

- All admin commands check for proper permissions
- Banned users cannot use any bot commands
- Admin status can be granted/revoked dynamically
- All admin actions are logged

## Database Tables

### banned_users
- `user_id` - Discord user ID
- `banned_by` - Admin who issued the ban
- `banned_at` - Timestamp of ban
- `reason` - Optional ban reason

## Notes

- Admin privileges are checked against the `ADMIN_IDS` list in config.py
- Bans are persistent across bot restarts
- Admin commands have proper error handling and validation
- All monetary operations use the bot's coin system