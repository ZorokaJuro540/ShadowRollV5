"""
Script pour synchroniser les personnages féminins depuis la base de données principale
vers le jeu "Tu préfères" avec leurs images existantes
"""
import aiosqlite
import asyncio
import logging
from typing import List, Dict, Tuple
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Liste des personnages féminins connus dans la base de données
FEMALE_CHARACTERS = [
    # One Piece
    "Nami", "Nico Robin", "Boa Hancock", "Nefertari Vivi", "Perona", "Tashigi", "Reiju Vinsmoke",
    "Carrot", "Yamato", "Ulti", "Black Maria", "Charlotte Linlin", "Jewelry Bonney", "Portgas D. Rouge",
    
    # Naruto
    "Hinata Hyuga", "Sakura Haruno", "Temari", "Ino Yamanaka", "Tenten", "Tsunade", "Kushina Uzumaki",
    "Konan", "Anko Mitarashi", "Kurenai Yuhi", "Mei Terumi", "Samui", "Karui", "Karin",
    
    # Attack on Titan
    "Mikasa Ackerman", "Historia Reiss", "Sasha Blouse", "Annie Leonhart", "Pieck Finger", "Ymir",
    "Hange Zoe", "Petra Ral", "Rico Brzenska", "Nanaba",
    
    # Demon Slayer
    "Nezuko Kamado", "Shinobu Kocho", "Kanao Tsuyuri", "Mitsuri Kanroji", "Aoi Kanzaki", "Makomo",
    "Tamayo", "Susamaru", "Nakime", "Daki",
    
    # My Hero Academia
    "Ochaco Uraraka", "Momo Yaoyorozu", "Tsuyu Asui", "Kyoka Jiro", "Mina Ashido", "Toru Hagakure",
    "Mei Hatsume", "Nejire Hado", "Himiko Toga", "Inko Midoriya", "Nana Shimura", "Mirko", "Mt. Lady",
    
    # Dragon Ball
    "Bulma", "Chi-Chi", "Android 18", "Videl", "Launch", "Mai", "Caulifla", "Kale", "Kefla",
    "Marcarita", "Vados",
    
    # Konosuba
    "Aqua", "Megumin", "Darkness", "Eris", "Yunyun", "Wiz", "Sylvia", "Komekko", "Luna",
    
    # JoJo's Bizarre Adventure
    "Jolyne Cujoh", "Trish Una", "Lisa Lisa", "Yukako Yamagishi", "Reimi Sugimoto", "Tomoko Higashikata",
    
    # Death Note
    "Misa Amane", "Naomi Misora", "Rem", "Takada Kiyomi", "Sayu Yagami",
    
    # Chainsaw Man
    "Makima", "Power", "Himeno", "Kobeni Higashiyama", "Reze", "Quanxi", "Aki Hayakawa",
    
    # Spy x Family
    "Yor Forger", "Anya Forger", "Fiona Frost", "Becky Blackbell", "Camilla", "Millie",
    
    # Hunter x Hunter
    "Kurapika", "Alluka Zoldyck", "Biscuit Krueger", "Neferpitou", "Pakunoda", "Machi Komacine",
    "Shizuku Murasaki", "Melody",
    
    # Bleach
    "Orihime Inoue", "Rukia Kuchiki", "Rangiku Matsumoto", "Neliel Tu Odelschwanck", "Yoruichi Shihoin",
    "Unohana Retsu", "Soifon", "Isane Kotetsu", "Nemu Kurotsuchi", "Mashiro Kuna",
    
    # One Punch Man
    "Tatsumaki", "Fubuki", "Mosquito Girl", "Speed-o'-Sound Sonic", "Do-S", "Psykos",
    
    # Tokyo Ghoul
    "Touka Kirishima", "Rize Kamishiro", "Hinami Fueguchi", "Akira Mado", "Eto Yoshimura",
    "Saiko Yonebayashi", "Mutsuki Tooru", "Rize Kamishiro",
    
    # Fullmetal Alchemist
    "Winry Rockbell", "Riza Hawkeye", "Izumi Curtis", "Lust", "Olivier Mira Armstrong", "May Chang",
    "Lan Fan", "Maria Ross", "Sheska", "Trisha Elric",
    
    # Fairy Tail
    "Lucy Heartfilia", "Erza Scarlet", "Wendy Marvell", "Juvia Lockser", "Levy McGarden", "Mirajane Strauss",
    "Cana Alberona", "Lisanna Strauss", "Minerva Orland", "Kagura Mikazuchi",
    
    # Fire Force
    "Tamaki Kotatsu", "Iris", "Maki Oze", "Hibana", "Princess Hibana", "Karim Flam",
    
    # Dr. Stone
    "Kohaku", "Yuzuriha Ogawa", "Ruri", "Suika", "Lillian Weinberg", "Homura Momiji",
    
    # Akame ga Kill
    "Akame", "Esdeath", "Mine", "Leone", "Sheele", "Najenda", "Chelsea",
    
    # Seven Deadly Sins
    "Elizabeth Liones", "Diane", "Merlin", "Elaine", "Jericho", "Guila", "Veronica Liones",
    
    # Black Clover
    "Noelle Silva", "Mimosa Vermillion", "Vanessa Enoteca", "Charlotte Roselei", "Mereoleona Vermillion",
    "Dorothy Unsworth",
    
    # Quintessential Quintuplets
    "Ichika Nakano", "Nino Nakano", "Miku Nakano", "Yotsuba Nakano", "Itsuki Nakano",
    
    # K-On!
    "Yui Hirasawa", "Mio Akiyama", "Ritsu Tainaka", "Tsumugi Kotobuki", "Azusa Nakano",
    
    # Love Live!
    "Honoka Kosaka", "Eli Ayase", "Kotori Minami", "Umi Sonoda", "Rin Hoshizora", "Maki Nishikino",
    "Nozomi Tojo", "Hanayo Koizumi", "Nico Yazawa",
    
    # Steins;Gate
    "Kurisu Makise", "Mayuri Shiina", "Suzuha Amane", "Faris NyanNyan", "Moeka Kiryu", "Luka Urushibara",
    
    # Re:Zero
    "Emilia", "Rem", "Ram", "Beatrice", "Felt", "Priscilla Barielle", "Crusch Karsten", "Anastasia Hoshin",
    
    # Overlord
    "Albedo", "Shalltear Bloodfallen", "Aura Bella Fiora", "Narberal Gamma", "Enri Emmot", "Renner Theiere Chardelon Ryle Vaiself",
    
    # Fate/Stay Night
    "Saber", "Rin Tohsaka", "Sakura Matou", "Illyasviel von Einzbern", "Rider", "Caster", "Taiga Fujimura",
    
    # Mob Psycho 100
    "Tsubomi Takane", "Emi", "Mezato Ichi", "Tome Kurata", "Minori Asagiri",
    
    # Violet Evergarden
    "Violet Evergarden", "Cattleya Baudelaire", "Iris Cannary", "Erica Brown", "Luculia Marlborough",
    
    # Jujutsu Kaisen
    "Nobara Kugisaki", "Maki Zenin", "Mai Zenin", "Miwa Kasumi", "Momo Nishimiya", "Utahime Iori",
    
    # Haikyuu!!
    "Kiyoko Shimizu", "Yachi Hitoka", "Saeko Tanaka", "Alisa Haiba", "Akane Yamamoto",
    
    # Oshi no Ko
    "Ai Hoshino", "Ruby Hoshino", "Kana Arima", "Akane Kurokawa", "Mem-Cho", "Miyako Saitou",
    
    # Solo Leveling
    "Cha Hae-In", "Yoo Jin-Ho", "Lee Ju-Hee", "Sung Jin-Ah",
    
    # Call of the Night
    "Nazuna Nanakusa", "Akira Asai", "Seri Kikyou", "Midori Kohakuhara",
    
    # My Deer Friend Nokotan
    "Nokotan", "Torako Koshi", "Anko Koshi", "Bashame",
    
    # Zenless Zone Zero
    "Ellen Joe", "Zhu Yuan", "Nicole Demara", "Anby Demara", "Nekomiya Mana", "Corin Wickes"
]

async def get_female_characters_from_db() -> List[Dict]:
    """Récupérer tous les personnages féminins depuis la base de données"""
    female_chars = []
    
    try:
        async with aiosqlite.connect("shadow_roll.db") as db:
            for female_name in FEMALE_CHARACTERS:
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

def generate_diverse_matchups(female_chars: List[Dict], count: int = 25) -> List[Tuple]:
    """Générer des matchups diversifiés en évitant les doublons d'anime"""
    if len(female_chars) < count * 2:
        logger.warning(f"Pas assez de personnages féminins ({len(female_chars)}) pour générer {count} matchups")
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
    
    # Générer les matchups
    anime_list = list(by_anime.keys())
    
    for i in range(count):
        attempt = 0
        while attempt < 100:  # Éviter les boucles infinies
            # Choisir deux animes différents
            anime1, anime2 = random.sample(anime_list, 2)
            
            # Choisir un personnage de chaque anime
            available_chars1 = [c for c in by_anime[anime1] if c['id'] not in used_chars]
            available_chars2 = [c for c in by_anime[anime2] if c['id'] not in used_chars]
            
            if available_chars1 and available_chars2:
                char1 = random.choice(available_chars1)
                char2 = random.choice(available_chars2)
                
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
                break
            
            attempt += 1
        
        if attempt >= 100:
            logger.warning(f"Impossible de trouver un matchup unique pour la question {i+1}")
    
    return matchups

async def update_would_you_rather_file(matchups: List[Tuple]):
    """Mettre à jour le fichier would_you_rather.py avec les nouveaux matchups"""
    
    # Générer le code des questions
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
    """Fonction principale"""
    print("🔄 Synchronisation des personnages féminins vers le jeu...")
    
    # Récupérer les personnages féminins depuis la DB
    female_chars = await get_female_characters_from_db()
    
    if not female_chars:
        print("❌ Aucun personnage féminin trouvé dans la base de données")
        return
    
    print(f"✅ {len(female_chars)} personnages féminins trouvés")
    
    # Générer les matchups
    matchups = generate_diverse_matchups(female_chars, 25)
    
    if not matchups:
        print("❌ Impossible de générer des matchups")
        return
    
    print(f"✅ {len(matchups)} matchups générés")
    
    # Mettre à jour le fichier
    success = await update_would_you_rather_file(matchups)
    
    if success:
        print("🎉 Synchronisation terminée avec succès !")
        print(f"📊 Statistiques:")
        print(f"   - {len(female_chars)} personnages féminins disponibles")
        print(f"   - {len(matchups)} matchups générés")
        print(f"   - {len(set(m[4] for m in matchups) | set(m[5] for m in matchups))} animes différents")
    else:
        print("❌ Erreur lors de la mise à jour du fichier")

if __name__ == "__main__":
    asyncio.run(main())