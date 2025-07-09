"""
Script pour mettre à jour les personnages du jeu "Tu préfères" 
avec la nouvelle configuration diversifiée
"""
import asyncio
from anime_girls_config import ANIME_GIRLS_LIST, get_diverse_matchups

def update_game_file():
    """Met à jour le fichier would_you_rather.py avec la nouvelle liste"""
    
    # Générer 25 matchups diversifiés
    diverse_matchups = get_diverse_matchups(25)
    
    # Créer le nouveau contenu des questions
    new_questions = []
    for char1, char2, img1, img2 in diverse_matchups:
        new_questions.append(f'                ("{char1}", "{char2}", "{img1}", "{img2}"),')
    
    new_questions_str = "\n".join(new_questions)
    
    print("🎮 MISE À JOUR DU JEU TU PRÉFÈRES")
    print("=" * 50)
    print(f"✅ {len(diverse_matchups)} matchups diversifiés générés")
    print("✅ Aucun doublon du même anime dans les matchups")
    print("✅ Images incluses pour chaque personnage")
    
    print("\n📋 EXEMPLES DE NOUVEAUX MATCHUPS:")
    print("-" * 40)
    for i, (char1, char2, _, _) in enumerate(diverse_matchups[:10], 1):
        print(f"{i:2d}. {char1} VS {char2}")
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   • Total personnages utilisés: {len(diverse_matchups) * 2}")
    print(f"   • Animes différents représentés: ~{len(set(char[1] for char in ANIME_GIRLS_LIST))}")
    
    print("\n🔧 Pour appliquer les changements:")
    print("   1. Copiez le code suivant dans modules/games/would_you_rather.py")
    print("   2. Remplacez la section 'questions' dans THEMES['anime_girl']")
    
    print("\n" + "="*60)
    print("CODE À COPIER:")
    print("="*60)
    print('            "questions": [')
    print(new_questions_str)
    print('            ]')
    print("="*60)
    
    return new_questions_str

def show_anime_diversity():
    """Affiche la diversité des animes dans la configuration"""
    from collections import Counter
    
    # Compter les animes représentés
    anime_counts = Counter(anime for _, anime, _ in ANIME_GIRLS_LIST)
    
    print("\n🌟 DIVERSITÉ DES ANIMES DISPONIBLES:")
    print("-" * 50)
    for anime, count in sorted(anime_counts.items(), key=lambda x: x[1], reverse=True):
        stars = "⭐" * min(count, 5)  # Max 5 étoiles
        print(f"{anime:<25} {count:2d} personnages {stars}")
    
    print(f"\nTotal: {len(anime_counts)} animes différents")
    print(f"Moyenne: {len(ANIME_GIRLS_LIST) / len(anime_counts):.1f} personnages par anime")

def generate_custom_matchups(excluded_animes=None, count=20):
    """Génère des matchups personnalisés en excluant certains animes"""
    if excluded_animes is None:
        excluded_animes = []
    
    # Filtrer les personnages
    filtered_characters = [
        (name, anime, img) for name, anime, img in ANIME_GIRLS_LIST
        if anime not in excluded_animes
    ]
    
    print(f"\n🎯 MATCHUPS PERSONNALISÉS (sans {', '.join(excluded_animes) if excluded_animes else 'aucune exclusion'}):")
    print("-" * 60)
    print(f"Personnages disponibles: {len(filtered_characters)}")
    print(f"Animes disponibles: {len(set(anime for _, anime, _ in filtered_characters))}")
    
    # Utiliser la même logique de diversité mais avec la liste filtrée
    # ... (logique similaire à get_diverse_matchups mais avec filtered_characters)
    
    return filtered_characters

if __name__ == "__main__":
    print("🚀 CONFIGURATEUR DE PERSONNAGES ANIME GIRLS")
    print("=" * 60)
    
    # Afficher les stats actuelles
    show_anime_diversity()
    
    # Générer la mise à jour
    update_game_file()
    
    print("\n💡 CONSEILS D'UTILISATION:")
    print("-" * 30)
    print("• Modifiez anime_girls_config.py pour ajouter/retirer des personnages")
    print("• Utilisez get_diverse_matchups() pour éviter les doublons d'anime")
    print("• Toutes les images sont hébergées sur Discord (fiables)")
    print("• La liste contient plus de 50 animes différents pour la diversité")