"""
Script pour modifier un personnage existant dans Shadow Roll Bot
Permet de changer le nom, la rareté, la valeur, l'anime ou l'image d'un personnage
"""

import asyncio
import aiosqlite
import json
from datetime import datetime
from character_manager import CharacterManager

async def modify_character():
    """Interface interactive pour modifier un personnage"""
    
    print("🌌 Shadow Roll - Modification de Personnage")
    print("=" * 50)
    
    # Initialiser le gestionnaire
    manager = CharacterManager()
    await manager.initialize()
    
    # Rechercher le personnage à modifier
    search_term = input("Nom du personnage à modifier: ").strip()
    characters = await manager.search_characters(search_term)
    
    if not characters:
        print(f"❌ Aucun personnage trouvé pour '{search_term}'")
        return
    
    if len(characters) > 1:
        print(f"\n🔍 {len(characters)} personnages trouvés:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char['name']} ({char['anime']}) - {char['rarity']}")
        
        try:
            choice = int(input("Choisissez le numéro du personnage: ")) - 1
            if 0 <= choice < len(characters):
                character = characters[choice]
            else:
                print("❌ Choix invalide")
                return
        except ValueError:
            print("❌ Veuillez entrer un numéro valide")
            return
    else:
        character = characters[0]
    
    print(f"\n📋 Personnage sélectionné:")
    print(f"   Nom: {character['name']}")
    print(f"   Anime: {character['anime']}")
    print(f"   Rareté: {character['rarity']}")
    print(f"   Valeur: {character['value']} SC")
    print(f"   Image: {'Oui' if character.get('image_url') else 'Non'}")
    
    # Menu de modification
    print(f"\n🔧 Que voulez-vous modifier?")
    print("1. Nom")
    print("2. Anime")
    print("3. Rareté")
    print("4. Valeur")
    print("5. Image URL")
    print("6. Tout modifier")
    print("0. Annuler")
    
    try:
        choice = int(input("Votre choix: "))
    except ValueError:
        print("❌ Choix invalide")
        return
    
    if choice == 0:
        print("Modification annulée")
        return
    
    # Collecter les nouvelles valeurs
    new_values = {}
    
    if choice in [1, 6]:  # Nom
        new_name = input(f"Nouveau nom [{character['name']}]: ").strip()
        if new_name:
            new_values['name'] = new_name
    
    if choice in [2, 6]:  # Anime
        new_anime = input(f"Nouvel anime [{character['anime']}]: ").strip()
        if new_anime:
            new_values['anime'] = new_anime
    
    if choice in [3, 6]:  # Rareté
        rarities = ['Common', 'Rare', 'Epic', 'Legendary', 'Mythical', 'Titan', 'Duo', 'Secret', 'Evolve']
        print(f"Raretés disponibles: {', '.join(rarities)}")
        new_rarity = input(f"Nouvelle rareté [{character['rarity']}]: ").strip()
        if new_rarity and new_rarity in rarities:
            new_values['rarity'] = new_rarity
        elif new_rarity:
            print(f"❌ Rareté invalide. Utilisez: {', '.join(rarities)}")
            return
    
    if choice in [4, 6]:  # Valeur
        try:
            new_value_input = input(f"Nouvelle valeur [{character['value']}]: ").strip()
            if new_value_input:
                new_values['value'] = int(new_value_input)
        except ValueError:
            print("❌ La valeur doit être un nombre entier")
            return
    
    if choice in [5, 6]:  # Image
        new_image = input(f"Nouvelle URL d'image [{character.get('image_url', 'Aucune')}]: ").strip()
        if new_image:
            new_values['image_url'] = new_image
    
    if not new_values:
        print("Aucune modification spécifiée")
        return
    
    # Confirmation
    print(f"\n✅ Modifications à appliquer:")
    for key, value in new_values.items():
        print(f"   {key}: {character.get(key, 'N/A')} → {value}")
    
    confirm = input("Confirmer les modifications? (o/N): ").strip().lower()
    if confirm not in ['o', 'oui', 'y', 'yes']:
        print("Modification annulée")
        return
    
    # Appliquer les modifications
    success = await apply_modifications(character['id'], new_values, manager)
    
    if success:
        print("✅ Personnage modifié avec succès!")
        print("📁 Modifications sauvegardées de manière permanente")
    else:
        print("❌ Erreur lors de la modification")

async def apply_modifications(character_id: int, new_values: dict, manager: CharacterManager):
    """Appliquer les modifications à un personnage"""
    try:
        # Construire la requête SQL
        set_clauses = []
        values = []
        
        for key, value in new_values.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)
        
        values.append(character_id)
        
        # Mettre à jour en base de données
        async with aiosqlite.connect(manager.db_path) as db:
            await db.execute(
                f"UPDATE characters SET {', '.join(set_clauses)} WHERE id = ?",
                values
            )
            await db.commit()
        
        # Mettre à jour le fichier JSON
        try:
            with open(manager.characters_file, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
            
            # Trouver et modifier le personnage dans le JSON
            for char in characters_data["characters"]:
                if char["id"] == character_id:
                    for key, value in new_values.items():
                        char[key] = value
                    char["last_updated"] = datetime.now().isoformat()
                    char["modified_by"] = "admin_script"
                    break
            
            characters_data["last_sync"] = datetime.now().isoformat()
            
            # Sauvegarder
            with open(manager.characters_file, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Base de données et fichier JSON mis à jour")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du JSON: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la modification: {e}")
        return False

async def quick_modify(character_name: str, **modifications):
    """Modification rapide via paramètres"""
    manager = CharacterManager()
    await manager.initialize()
    
    characters = await manager.search_characters(character_name)
    
    if not characters:
        print(f"❌ Personnage '{character_name}' non trouvé")
        return False
    
    if len(characters) > 1:
        print(f"❌ Plusieurs personnages trouvés pour '{character_name}'. Soyez plus spécifique.")
        return False
    
    character = characters[0]
    success = await apply_modifications(character['id'], modifications, manager)
    
    if success:
        print(f"✅ {character['name']} modifié avec succès")
        for key, value in modifications.items():
            print(f"   {key}: {value}")
    
    return success

# Exemples d'utilisation directe
async def examples():
    """Exemples de modifications rapides"""
    
    # Changer la rareté d'un personnage
    # await quick_modify("Naruto", rarity="Mythical")
    
    # Changer le nom et la valeur
    # await quick_modify("Goku", name="Son Goku", value=2000)
    
    # Changer l'anime d'appartenance
    # await quick_modify("Luffy", anime="One Piece Updated")
    
    # Ajouter une image
    # await quick_modify("Sasuke", image_url="https://nouvelle-image.jpg")
    
    pass

if __name__ == "__main__":
    asyncio.run(modify_character())