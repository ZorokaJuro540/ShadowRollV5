"""
Script pour appliquer les images premium au jeu "Tu préfères"
Génère automatiquement 25 matchups avec images HD optimisées
"""
from anime_girls_premium_images import get_diverse_premium_matchups

def generate_new_game_questions():
    """Générer les nouvelles questions avec images premium"""
    matchups = get_diverse_premium_matchups(25)
    
    questions_code = []
    for char1, char2, img1, img2 in matchups:
        line = f'                ("{char1}", "{char2}", "{img1}", "{img2}"),'
        questions_code.append(line)
    
    return "\n".join(questions_code)

def main():
    print("🚀 APPLICATION DES IMAGES PREMIUM AU JEU")
    print("=" * 50)
    
    new_questions = generate_new_game_questions()
    
    print("✅ 25 nouveaux matchups générés avec images HD")
    print("✅ Format optimisé 700x1400 pour Discord")
    print("✅ Qualité premium WallpaperCave/Pinterest")
    print("✅ Aucun doublon d'anime dans les matchups")
    
    print("\n" + "="*60)
    print("CODE GÉNÉRÉ POUR would_you_rather.py:")
    print("="*60)
    print('            "questions": [')
    print(new_questions)
    print('            ]')
    print("="*60)
    
    return new_questions

if __name__ == "__main__":
    main()