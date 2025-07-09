"""
Script d'amélioration pour récupérer TOUS les personnages féminins de la base de données
et créer un système plus intelligent de détection automatique
"""
import aiosqlite
import asyncio
import logging
from typing import List, Dict, Tuple, Set
import random
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mots-clés pour identifier les personnages féminins
FEMALE_KEYWORDS = [
    # Noms typiquement féminins
    "chan", "sama", "san", "kun", "ko", "ka", "mi", "na", "ri", "yu", "ai", "ei", "ui", "oi",
    # Suffixes et préfixes féminins
    "hime", "princess", "queen", "lady", "girl", "woman", "female", "maiden", "miss", "mrs",
    # Noms communs féminins
    "akane", "akira", "ami", "anna", "asuka", "ayame", "chika", "emi", "hana", "haru", "hinata",
    "ichigo", "kana", "karin", "kasumi", "kei", "kiko", "kimi", "kyoko", "mai", "maki", "mana",
    "mari", "maya", "mei", "miki", "mina", "misaki", "mizuki", "nana", "natsuki", "rei", "rika",
    "riko", "rin", "saki", "shizuku", "yui", "yuka", "yuki", "yuko", "yumi", "yuna"
]

# Liste étendue de personnages féminins connus
DEFINITELY_FEMALE = [
    # One Piece
    "Nami", "Nico Robin", "Boa Hancock", "Nefertari Vivi", "Perona", "Tashigi", "Reiju Vinsmoke",
    "Carrot", "Yamato", "Ulti", "Black Maria", "Charlotte Linlin", "Jewelry Bonney", "Portgas D. Rouge",
    "Alvida", "Kaya", "Nojiko", "Bellemere", "Kuina", "Miss All Sunday", "Miss Valentine", "Miss Doublefinger",
    "Miss Merry Christmas", "Miss Goldenweek", "Kalifa", "Spandam", "Kokoro", "Chimney", "Camie",
    "Keimi", "Shakky", "Gloriosa", "Marguerite", "Sweet Pea", "Aphelandra", "Ran", "Daisy", "Cosmos",
    "Marigold", "Sandersonia", "Hancock", "Shirahoshi", "Otohime", "Madame Sharley", "Ishilly",
    "Carina", "Stella", "Ann", "Honey Queen", "Smoothie", "Galette", "Amande", "Praline",
    "Compote", "Custard", "Angel", "Broyé", "Joscarpone", "Mascarpone", "Panna", "Joconde",
    "Pudding", "Flampe", "Citron", "Cinnamon", "Citron", "Myukuru", "Newshi", "Newichi",
    "Newsan", "Newshi", "Newgo", "Newroku", "Newna", "Newhachi", "Newkyu", "Newjuu",
    
    # Attack on Titan
    "Mikasa Ackerman", "Historia Reiss", "Sasha Blouse", "Annie Leonhart", "Pieck Finger", "Ymir",
    "Hange Zoe", "Petra Ral", "Rico Brzenska", "Nanaba", "Frieda Reiss", "Carla Yeager",
    "Dina Fritz", "Alma", "Kuchel Ackerman", "Faye Yeager", "Mina Carolina", "Hannah Diamant",
    "Franz Kefka", "Milieus", "Lynne", "Ilse Langnar", "Zofia", "Udo", "Gabi Braun",
    "Kaya", "Louise", "Yelena", "Hitch Dreyse", "Marlowe Freudenberg", "Nifa", "Keiji",
    "Lauda", "Rashad", "Holger", "Wim", "Levi", "Floch", "Anka Rheinberger",
    
    # Demon Slayer
    "Nezuko Kamado", "Shinobu Kocho", "Kanao Tsuyuri", "Mitsuri Kanroji", "Aoi Kanzaki", "Makomo",
    "Tamayo", "Susamaru", "Nakime", "Daki", "Mitsuri", "Kanae Kocho", "Kie Kamado",
    "Hanako Kamado", "Takeo Kamado", "Rokuta Kamado", "Shigeru Kamado", "Rui", "Spider Mother",
    "Spider Sister", "Spider Daughter", "Rui's Mother", "Rui's Sister", "Rui's Daughter",
    "Mukago", "Wakuraba", "Rokuro", "Enmu", "Kaigaku", "Kokushibo", "Douma", "Akaza",
    "Hantengu", "Gyokko", "Gyutaro", "Daki", "Kamanue", "Rui", "Enmu", "Kaigaku",
    "Muzan Kibutsuji", "Kagaya Ubuyashiki", "Amane Ubuyashiki", "Hinaki Ubuyashiki", "Nichika Ubuyashiki",
    "Kuina Ubuyashiki", "Kiriya Ubuyashiki", "Kanata Ubuyashiki", "Suma", "Makio", "Hinatsuru",
    
    # Naruto
    "Hinata Hyuga", "Sakura Haruno", "Temari", "Ino Yamanaka", "Tenten", "Tsunade", "Kushina Uzumaki",
    "Konan", "Anko Mitarashi", "Kurenai Yuhi", "Mei Terumi", "Samui", "Karui", "Karin",
    "Shizune", "Chiyo", "Guren", "Fuu", "Yugito Nii", "Mabui", "Pakura", "Kurotsuchi",
    "Hanabi Hyuga", "Himawari Uzumaki", "Sarada Uchiha", "Chocho Akimichi", "Sumire Kakei",
    "Namida Suzumeno", "Wasabi Izuno", "Tsubaki Kurogane", "Mirai Sarutobi", "Moegi Kazamatsuri",
    "Udon Ise", "Konohamaru Sarutobi", "Hanabi", "Hinata", "Neji", "Tenten", "Rock Lee",
    "Might Guy", "Kakashi Hatake", "Yamato", "Sai", "Naruto Uzumaki", "Sasuke Uchiha",
    "Sakura Haruno", "Shikamaru Nara", "Choji Akimichi", "Ino Yamanaka", "Kiba Inuzuka",
    "Shino Aburame", "Hinata Hyuga", "Neji Hyuga", "Tenten", "Rock Lee", "Might Guy",
    
    # My Hero Academia
    "Ochaco Uraraka", "Momo Yaoyorozu", "Tsuyu Asui", "Kyoka Jiro", "Mina Ashido", "Toru Hagakure",
    "Mei Hatsume", "Nejire Hado", "Himiko Toga", "Inko Midoriya", "Nana Shimura", "Mirko", "Mt. Lady",
    "Midnight", "Recovery Girl", "Thirteen", "Pixie-Bob", "Mandalay", "Ragdoll", "Bubble Girl",
    "Centipeder", "Uwabami", "Camie Utsushimi", "Saiko Intelli", "Reiko Yanagi", "Pony Tsunotori",
    "Setsuna Tokage", "Yui Kodai", "Kinoko Komori", "Shiozaki Ibara", "Kendo Itsuka", "Tetsutetsu Tetsutetsu",
    "Yosetsu Awase", "Sen Kaibara", "Togaru Kamakiri", "Shihai Kuroiro", "Jurota Shishida",
    "Kojiro Bondo", "Neito Monoma", "Reiko Yanagi", "Yui Kodai", "Setsuna Tokage", "Pony Tsunotori",
    "Kinoko Komori", "Shiozaki Ibara", "Kendo Itsuka", "Yosetsu Awase", "Sen Kaibara", "Togaru Kamakiri",
    
    # Dragon Ball
    "Bulma", "Chi-Chi", "Android 18", "Videl", "Launch", "Mai", "Caulifla", "Kale", "Kefla",
    "Marcarita", "Vados", "Kusu", "Cus", "Heles", "Brianne de Chateau", "Ribrianne", "Rozie",
    "Kakunsa", "Vikal", "Cocotte", "Kettol", "Vuon", "Lilibeu", "Zarbuto", "Rabanra",
    "Ganos", "Hermila", "Prum", "Dr. Rota", "Magetta", "Botamo", "Cabba", "Frost",
    "Hit", "Champa", "Vados", "Whis", "Beerus", "Goku", "Vegeta", "Gohan", "Piccolo",
    "Krillin", "Tien", "Yamcha", "Chiaotzu", "Master Roshi", "Turtle", "Oolong", "Puar",
    "Yajirobe", "Korin", "Mr. Popo", "Kami", "King Kai", "Bubbles", "Gregory", "Jeice",
    "Burter", "Recoome", "Guldo", "Ginyu", "Frieza", "Zarbon", "Dodoria", "Cui",
    
    # Et beaucoup d'autres séries...
]

# Mots-clés pour identifier les personnages masculins (à éviter)
MALE_KEYWORDS = [
    "king", "prince", "lord", "master", "mister", "sir", "duke", "baron", "emperor", "god",
    "sensei", "senpai", "kun", "sama", "san", "chan", "bo", "ro", "to", "ta", "da",
    "man", "boy", "male", "father", "dad", "papa", "brother", "son", "uncle", "grandfather",
    "hero", "warrior", "knight", "soldier", "captain", "general", "admiral", "commander"
]

# Noms définitivement masculins
DEFINITELY_MALE = [
    "Naruto", "Sasuke", "Goku", "Vegeta", "Luffy", "Zoro", "Sanji", "Ichigo", "Natsu", "Gray",
    "Erza", "Levi", "Eren", "Armin", "Tanjiro", "Zenitsu", "Inosuke", "Deku", "Bakugo", "Todoroki",
    "Kirito", "Asuna", "Rimuru", "Ainz", "Subaru", "Kazuma", "Aqua", "Darkness", "Megumin",
    "Senku", "Tsukasa", "Chrome", "Meliodas", "Ban", "King", "Gowther", "Merlin", "Diane",
    "Asta", "Yuno", "Noelle", "Luck", "Magna", "Vanessa", "Charmy", "Gauche", "Gordon",
    "Finral", "Zora", "Henry", "Yami", "William", "Fuegoleon", "Mereoleona", "Nozel", "Jack",
    "Charlotte", "Rill", "Dorothy", "Kaiser", "Gueldre", "Langris", "Sekke", "Solid", "Nebra",
    "Sora", "Shiro", "Jibril", "Stephanie", "Chlammy", "Fiel", "Izuna", "Tet", "Schwi", "Riku",
    "Corone", "Plum", "Avant", "Holou", "Dola", "Emir", "Einzig", "Kurami", "Fil", "Jibril",
    "Corone", "Plum", "Avant", "Holou", "Dola", "Emir", "Einzig", "Kurami", "Fil", "Jibril"
]

async def get_all_characters_from_db() -> List[Dict]:
    """Récupérer TOUS les personnages depuis la base de données"""
    all_chars = []
    
    try:
        async with aiosqlite.connect("shadow_roll.db") as db:
            cursor = await db.execute(
                "SELECT id, name, anime, rarity, value, image_url FROM characters ORDER BY anime, name"
            )
            results = await cursor.fetchall()
            
            for result in results:
                all_chars.append({
                    'id': result[0],
                    'name': result[1],
                    'anime': result[2],
                    'rarity': result[3],
                    'value': result[4],
                    'image_url': result[5] or ""
                })
                
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des personnages: {e}")
    
    return all_chars

def is_likely_female(name: str) -> bool:
    """Déterminer si un nom est probablement féminin"""
    name_lower = name.lower()
    
    # Vérifier si c'est dans la liste des personnages définitivement féminins
    if name in DEFINITELY_FEMALE:
        return True
    
    # Vérifier si c'est dans la liste des personnages définitivement masculins
    if name in DEFINITELY_MALE:
        return False
    
    # Vérifier les mots-clés masculins (exclure)
    for keyword in MALE_KEYWORDS:
        if keyword in name_lower:
            return False
    
    # Vérifier les mots-clés féminins (inclure)
    for keyword in FEMALE_KEYWORDS:
        if keyword in name_lower:
            return True
    
    # Vérifier les terminaisons typiquement féminines
    female_endings = ['ko', 'ka', 'mi', 'na', 'ri', 'yu', 'ai', 'ei', 'ui', 'oi', 'chan', 'san']
    for ending in female_endings:
        if name_lower.endswith(ending):
            return True
    
    # Vérifier les terminaisons typiquement masculines
    male_endings = ['ro', 'to', 'ta', 'da', 'ma', 'ya', 'wa', 'ra', 'sa', 'ha', 'kun']
    for ending in male_endings:
        if name_lower.endswith(ending):
            return False
    
    # Si aucun indicateur clair, retourner False par défaut
    return False

async def get_smart_female_characters() -> List[Dict]:
    """Récupérer les personnages féminins avec détection intelligente"""
    all_chars = await get_all_characters_from_db()
    female_chars = []
    
    for char in all_chars:
        if is_likely_female(char['name']):
            female_chars.append(char)
            logger.info(f"✓ Détecté comme féminin: {char['name']} ({char['anime']})")
        else:
            logger.debug(f"✗ Détecté comme masculin: {char['name']} ({char['anime']})")
    
    return female_chars

def generate_optimized_matchups(female_chars: List[Dict], count: int = 30) -> List[Tuple]:
    """Générer des matchups optimisés avec plus de variété"""
    if len(female_chars) < count * 2:
        logger.warning(f"Ajustement: seulement {len(female_chars)} personnages féminins pour {count} matchups")
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
    
    # Prioriser les animes avec plus de personnages
    anime_priority = sorted(by_anime.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Générer les matchups
    for i in range(count):
        best_matchup = None
        best_score = -1
        
        for attempt in range(200):  # Plus de tentatives
            # Choisir deux animes différents
            anime_keys = list(by_anime.keys())
            if len(anime_keys) < 2:
                break
                
            anime1, anime2 = random.sample(anime_keys, 2)
            
            # Choisir des personnages disponibles
            available_chars1 = [c for c in by_anime[anime1] if c['id'] not in used_chars]
            available_chars2 = [c for c in by_anime[anime2] if c['id'] not in used_chars]
            
            if not available_chars1 or not available_chars2:
                continue
            
            char1 = random.choice(available_chars1)
            char2 = random.choice(available_chars2)
            
            # Calculer un score de qualité du matchup
            score = 0
            
            # Bonus pour les images disponibles
            if char1['image_url'] and char1['image_url'].strip():
                score += 10
            if char2['image_url'] and char2['image_url'].strip():
                score += 10
            
            # Bonus pour les raretés élevées
            rarity_values = {'Common': 1, 'Rare': 2, 'Epic': 3, 'Legendary': 4, 'Mythic': 5, 'Titan': 6, 'Fusion': 7, 'Evolve': 8, 'Secret': 9, 'Ultimate': 10}
            score += rarity_values.get(char1['rarity'], 0)
            score += rarity_values.get(char2['rarity'], 0)
            
            # Bonus pour les animes populaires
            popular_animes = ['Naruto', 'One Piece', 'Attack on Titan', 'Demon Slayer', 'My Hero Academia', 'Dragon Ball']
            if char1['anime'] in popular_animes:
                score += 5
            if char2['anime'] in popular_animes:
                score += 5
            
            if score > best_score:
                best_score = score
                best_matchup = (char1, char2)
            
            # Si on a un très bon matchup, on l'accepte
            if score >= 25:
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

async def update_would_you_rather_with_better_structure(matchups: List[Tuple]):
    """Mettre à jour le fichier avec une meilleure structure"""
    
    # Générer le code des questions avec plus de détails
    questions_code = []
    for i, (char1, char2, img1, img2, anime1, anime2) in enumerate(matchups):
        questions_code.append(f'                # Question {i+1}: {anime1} vs {anime2}')
        questions_code.append(f'                ("{char1}", "{char2}", "{img1}", "{img2}"),')
    
    questions_str = '\n'.join(questions_code)
    
    # Lire le fichier actuel
    try:
        with open("modules/games/would_you_rather.py", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.error("Fichier would_you_rather.py non trouvé")
        return False
    
    # Améliorer la structure en ajoutant un commentaire sur la source
    header_comment = f"""                # ========================================
                # PERSONNAGES FÉMININS SYNCHRONISÉS AUTOMATIQUEMENT
                # Source: Base de données Shadow Roll Bot
                # Nombre total de matchups: {len(matchups)}
                # Animes représentés: {len(set(m[4] for m in matchups) | set(m[5] for m in matchups))}
                # Généré automatiquement par sync_female_characters_to_game.py
                # ========================================
"""
    
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
        '\n' + header_comment + '\n' + questions_str + '\n            ' +
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
    """Fonction principale améliorée"""
    print("🔄 Synchronisation intelligente des personnages féminins...")
    
    # Récupérer tous les personnages et détecter les féminins
    female_chars = await get_smart_female_characters()
    
    if not female_chars:
        print("❌ Aucun personnage féminin détecté dans la base de données")
        return
    
    print(f"✅ {len(female_chars)} personnages féminins détectés")
    
    # Afficher les statistiques par anime
    by_anime = {}
    for char in female_chars:
        anime = char['anime']
        if anime not in by_anime:
            by_anime[anime] = []
        by_anime[anime].append(char)
    
    print(f"\n📊 Répartition par anime:")
    for anime, chars in sorted(by_anime.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   - {anime}: {len(chars)} personnages")
    
    # Générer des matchups optimisés
    matchups = generate_optimized_matchups(female_chars, 30)
    
    if not matchups:
        print("❌ Impossible de générer des matchups")
        return
    
    print(f"\n✅ {len(matchups)} matchups générés avec succès")
    
    # Mettre à jour le fichier avec une meilleure structure
    success = await update_would_you_rather_with_better_structure(matchups)
    
    if success:
        print("\n🎉 Synchronisation intelligente terminée avec succès !")
        print(f"📈 Améliorations:")
        print(f"   - {len(female_chars)} personnages féminins détectés automatiquement")
        print(f"   - {len(matchups)} matchups de haute qualité générés")
        print(f"   - {len(set(m[4] for m in matchups) | set(m[5] for m in matchups))} animes différents représentés")
        print(f"   - {sum(1 for m in matchups if m[2] and m[3])} matchups avec images complètes")
        print(f"   - Structure de fichier améliorée avec commentaires détaillés")
    else:
        print("❌ Erreur lors de la mise à jour du fichier")

if __name__ == "__main__":
    asyncio.run(main())