"""
Script final pour synchroniser UNIQUEMENT les personnages féminins corrects
avec une liste curée manuellement et des images de la base de données
"""
import aiosqlite
import asyncio
import logging
import random
from typing import List, Dict, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Liste curée manuellement des personnages DÉFINITIVEMENT féminins
CURATED_FEMALE_CHARACTERS = [
    # One Piece
    "Nami", "Boa Hancock",
    
    # Naruto
    "Hinata Hyuga", "Sakura Haruno", "Tsunade",
    
    # Attack on Titan
    "Mikasa Ackerman", "Historia Reiss", "Sasha Blouse", "Annie Leonhart",
    
    # Demon Slayer
    "Nezuko Kamado", "Shinobu Kocho", "Mitsuri Kanroji",
    
    # My Hero Academia
    "Ochaco Uraraka", "Momo Yaoyorozu", "Tsuyu Asui",
    
    # Jujutsu Kaisen
    "Nobara Kugisaki", "Kasumi Miwa",
    
    # Chainsaw Man
    "Makima", "Power",
    
    # Spy x Family
    "Yor Forger", "Anya Forger",
    
    # Oshi no Ko
    "Ai Hoshino", "Ruby Hoshino", "Akane Kurokawa",
    
    # Call of the Night
    "Nazuna Nanakusa", "Seri Kikyo", "Midori Kohakobe",
    
    # My Deer Friend Nekotan
    "Torako Koshi", "Anko Koshi", "Noko Shikanoko",
    
    # Zenless Zone Zero
    "Ellen Joe",
    
    # Re:Zero
    "Emilia", "Rem", "Ram",
    
    # Konosuba
    "Megumin", "Aqua", "Darkness",
    
    # Fairy Tail
    "Lucy Heartfilia", "Erza Scarlet", "Wendy Marvell",
    
    # Black Clover
    "Noelle Silva", "Mimosa Vermillion", "Vanessa Enoteca",
    
    # One Punch Man
    "Tatsumaki", "Fubuki",
    
    # Tokyo Ghoul
    "Touka Kirishima", "Rize Kamishiro",
    
    # Bleach
    "Orihime Inoue", "Rukia Kuchiki", "Yoruichi Shihoin",
    
    # Death Note
    "Misa Amane",
    
    # Overlord
    "Albedo", "Shalltear Bloodfallen",
    
    # Violet Evergarden
    "Violet Evergarden",
    
    # Akame ga Kill
    "Akame", "Esdeath", "Mine",
    
    # Seven Deadly Sins
    "Elizabeth Liones", "Diane", "Merlin",
    
    # Dr. Stone
    "Kohaku", "Yuzuriha Ogawa",
    
    # Fire Force
    "Tamaki Kotatsu", "Iris", "Maki Oze",
    
    # Quintessential Quintuplets
    "Ichika Nakano", "Nino Nakano", "Miku Nakano", "Yotsuba Nakano", "Itsuki Nakano",
    
    # K-On!
    "Yui Hirasawa", "Mio Akiyama", "Ritsu Tainaka", "Tsumugi Kotobuki", "Azusa Nakano",
    
    # Love Live!
    "Honoka Kosaka", "Eli Ayase", "Kotori Minami", "Umi Sonoda", "Rin Hoshizora",
    "Maki Nishikino", "Nozomi Tojo", "Hanayo Koizumi", "Nico Yazawa",
    
    # Steins;Gate
    "Kurisu Makise", "Mayuri Shiina", "Suzuha Amane",
    
    # Fate/Stay Night
    "Saber", "Rin Tohsaka", "Sakura Matou", "Illyasviel von Einzbern",
    
    # Mob Psycho 100
    "Tsubomi Takane",
    
    # Haikyuu!!
    "Kiyoko Shimizu", "Yachi Hitoka",
    
    # Dragon Ball
    "Bulma", "Chi-Chi", "Android 18", "Videl",
    
    # Hunter x Hunter
    "Biscuit Krueger", "Neferpitou", "Alluka Zoldyck",
    
    # JoJo's Bizarre Adventure
    "Jolyne Cujoh", "Trish Una", "Lisa Lisa",
    
    # Fullmetal Alchemist
    "Winry Rockbell", "Riza Hawkeye", "Izumi Curtis",
    
    # Tokyo Revengers
    "Emma Sano", "Hina Tachibana",
    
    # Sword Art Online
    "Asuna", "Sinon", "Silica",
    
    # Blue Lock
    "Anri Teieri",
    
    # The Eminence in Shadow
    "Alexia Midgar", "Iris Midgar"
]

async def get_curated_female_characters() -> List[Dict]:
    """Récupérer les personnages féminins curés depuis la base de données"""
    female_chars = []
    
    try:
        async with aiosqlite.connect("shadow_roll.db") as db:
            for female_name in CURATED_FEMALE_CHARACTERS:
                cursor = await db.execute(
                    "SELECT id, name, anime, rarity, value, image_url FROM characters WHERE name = ?",
                    (female_name,)
                )
                result = await cursor.fetchone()
                
                if result:
                    female_chars.append({
                        'id': result[0],
                        'name': result[1],
                        'anime': result[2],
                        'rarity': result[3],
                        'value': result[4],
                        'image_url': result[5] or ""
                    })
                    logger.info(f"✓ Trouvé: {result[1]} ({result[2]})")
                else:
                    logger.warning(f"✗ Personnage non trouvé: {female_name}")
                    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des personnages: {e}")
    
    return female_chars

def generate_perfect_matchups(female_chars: List[Dict], count: int = 25) -> List[Tuple]:
    """Générer des matchups parfaits avec diversité maximale"""
    if len(female_chars) < count * 2:
        logger.warning(f"Ajustement: {len(female_chars)} personnages pour {count} matchups")
        count = len(female_chars) // 2
    
    matchups = []
    used_chars = set()
    
    # Grouper par anime
    by_anime = {}
    for char in female_chars:
        anime = char['anime']
        if anime not in by_anime:
            by_anime[anime] = []
        by_anime[anime].append(char)
    
    # Prioriser les animes avec des images
    animes_with_images = {}
    for anime, chars in by_anime.items():
        chars_with_images = [c for c in chars if c['image_url'] and c['image_url'].strip()]
        if chars_with_images:
            animes_with_images[anime] = chars_with_images
    
    # Générer des matchups de haute qualité
    for i in range(count):
        best_matchup = None
        best_score = -1
        
        for attempt in range(500):  # Beaucoup de tentatives pour trouver le meilleur
            # Choisir deux animes différents avec des images
            anime_keys = list(animes_with_images.keys())
            if len(anime_keys) < 2:
                # Fallback vers tous les animes
                anime_keys = list(by_anime.keys())
                if len(anime_keys) < 2:
                    break
                    
            anime1, anime2 = random.sample(anime_keys, 2)
            
            # Choisir des personnages disponibles
            if anime1 in animes_with_images and anime2 in animes_with_images:
                available_chars1 = [c for c in animes_with_images[anime1] if c['id'] not in used_chars]
                available_chars2 = [c for c in animes_with_images[anime2] if c['id'] not in used_chars]
            else:
                available_chars1 = [c for c in by_anime[anime1] if c['id'] not in used_chars]
                available_chars2 = [c for c in by_anime[anime2] if c['id'] not in used_chars]
            
            if not available_chars1 or not available_chars2:
                continue
            
            char1 = random.choice(available_chars1)
            char2 = random.choice(available_chars2)
            
            # Calculer un score de qualité
            score = 0
            
            # Bonus majeur pour les images
            if char1['image_url'] and char1['image_url'].strip():
                score += 15
            if char2['image_url'] and char2['image_url'].strip():
                score += 15
            
            # Bonus pour les raretés
            rarity_values = {
                'Common': 1, 'Rare': 2, 'Epic': 3, 'Legendary': 4, 'Mythic': 5,
                'Titan': 6, 'Fusion': 7, 'Evolve': 8, 'Secret': 9, 'Ultimate': 10
            }
            score += rarity_values.get(char1['rarity'], 0)
            score += rarity_values.get(char2['rarity'], 0)
            
            # Bonus pour les animes populaires
            popular_animes = [
                'Naruto', 'One Piece', 'Attack on Titan', 'Demon Slayer', 'My Hero Academia',
                'Dragon Ball', 'Jujutsu Kaisen', 'Chainsaw Man', 'Spy x Family', 'Oshi no Ko'
            ]
            if char1['anime'] in popular_animes:
                score += 8
            if char2['anime'] in popular_animes:
                score += 8
            
            # Bonus pour éviter les animes sous-représentés
            underrepresented = ['Call Of The Night', 'My Deer Friend Nekotan', 'Zenless Zone Zero']
            if char1['anime'] in underrepresented or char2['anime'] in underrepresented:
                score += 5
            
            if score > best_score:
                best_score = score
                best_matchup = (char1, char2)
            
            # Si on a un excellent matchup, on l'accepte
            if score >= 40:
                break
        
        if best_matchup:
            char1, char2 = best_matchup
            matchups.append((
                char1['name'],
                char2['name'],
                char1['image_url'],
                char2['image_url'],
                char1['anime'],
                char2['anime']
            ))
            
            used_chars.add(char1['id'])
            used_chars.add(char2['id'])
            
            logger.info(f"✓ Matchup {i+1}: {char1['name']} ({char1['anime']}) vs {char2['name']} ({char2['anime']}) - Score: {best_score}")
        else:
            logger.warning(f"✗ Impossible de créer le matchup {i+1}")
    
    return matchups

async def update_would_you_rather_final(matchups: List[Tuple]):
    """Mise à jour finale du fichier avec structure optimisée"""
    
    # Générer le code avec structure propre
    questions_code = []
    questions_code.append("                # ========================================")
    questions_code.append("                # PERSONNAGES FÉMININS - SYNCHRONISATION FINALE")
    questions_code.append("                # Images récupérées depuis la base de données Shadow Roll")
    questions_code.append(f"                # {len(matchups)} matchups de haute qualité")
    questions_code.append(f"                # {len(set(m[4] for m in matchups) | set(m[5] for m in matchups))} animes représentés")
    questions_code.append("                # ========================================")
    
    for i, (char1, char2, img1, img2, anime1, anime2) in enumerate(matchups):
        questions_code.append(f"                # Question {i+1}: {anime1} vs {anime2}")
        questions_code.append(f'                ("{char1}", "{char2}", "{img1}", "{img2}"),')
    
    questions_str = '\n'.join(questions_code)
    
    # Lire le fichier actuel
    try:
        with open("modules/games/would_you_rather.py", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error("Fichier would_you_rather.py non trouvé")
        return False
    
    # Trouver et remplacer la section des questions
    start_marker = '"questions": ['
    end_marker = ']'
    
    start_idx = content.find(start_marker)
    if start_idx == -1:
        logger.error("Marqueur de début des questions non trouvé")
        return False
    
    # Trouver la fin de la section questions
    bracket_count = 0
    end_idx = start_idx + len(start_marker)
    found_end = False
    
    for i in range(end_idx, len(content)):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            if bracket_count == 0:
                end_idx = i
                found_end = True
                break
            bracket_count -= 1
    
    if not found_end:
        logger.error("Marqueur de fin des questions non trouvé")
        return False
    
    # Construire le nouveau contenu
    new_content = (
        content[:start_idx + len(start_marker)] +
        '\n' + questions_str + '\n            ' +
        content[end_idx:]
    )
    
    # Écrire le fichier mis à jour
    try:
        with open("modules/games/would_you_rather.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        logger.info("✅ Fichier would_you_rather.py mis à jour avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier: {e}")
        return False

async def main():
    """Fonction principale finale"""
    print("🎯 Synchronisation FINALE des personnages féminins curés...")
    
    # Récupérer les personnages féminins curés
    female_chars = await get_curated_female_characters()
    
    if not female_chars:
        print("❌ Aucun personnage féminin trouvé dans la base de données")
        return
    
    print(f"✅ {len(female_chars)} personnages féminins trouvés")
    
    # Afficher les statistiques
    by_anime = {}
    with_images = 0
    
    for char in female_chars:
        anime = char['anime']
        if anime not in by_anime:
            by_anime[anime] = []
        by_anime[anime].append(char)
        
        if char['image_url'] and char['image_url'].strip():
            with_images += 1
    
    print(f"\n📊 Statistiques:")
    print(f"   - {len(female_chars)} personnages féminins au total")
    print(f"   - {with_images} personnages avec images ({with_images/len(female_chars)*100:.1f}%)")
    print(f"   - {len(by_anime)} animes représentés")
    
    print(f"\n🎮 Top animes par nombre de personnages:")
    for anime, chars in sorted(by_anime.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        chars_with_img = sum(1 for c in chars if c['image_url'] and c['image_url'].strip())
        print(f"   - {anime}: {len(chars)} personnages ({chars_with_img} avec images)")
    
    # Générer des matchups parfaits
    matchups = generate_perfect_matchups(female_chars, 25)
    
    if not matchups:
        print("❌ Impossible de générer des matchups")
        return
    
    print(f"\n✅ {len(matchups)} matchups générés")
    
    # Mettre à jour le fichier
    success = await update_would_you_rather_final(matchups)
    
    if success:
        # Calculer les statistiques finales
        total_with_images = sum(1 for m in matchups if m[2] and m[3])
        unique_animes = len(set(m[4] for m in matchups) | set(m[5] for m in matchups))
        
        print(f"\n🎉 SYNCHRONISATION FINALE TERMINÉE !")
        print(f"📈 Résultats:")
        print(f"   ✓ {len(matchups)} matchups de haute qualité")
        print(f"   ✓ {total_with_images} matchups avec images complètes")
        print(f"   ✓ {unique_animes} animes différents représentés")
        print(f"   ✓ {len(female_chars)} personnages féminins utilisés")
        print(f"   ✓ Synchronisation avec la base de données Shadow Roll")
        print(f"   ✓ Images authentiques récupérées automatiquement")
        
        print(f"\n🎯 Le jeu 'Tu préfères' anime girls est maintenant synchronisé !")
    else:
        print("❌ Erreur lors de la mise à jour du fichier")

if __name__ == "__main__":
    asyncio.run(main())