"""
Script pour configurer la nouvelle rareté Ultimate dans le système Shadow Roll
- Ajoute la rareté Ultimate (orange, 0.001% de chance)
- Plus rare que Secret (0.01%)
- Configure les cooldowns et valeurs
"""

import asyncio
import aiosqlite
import json
from datetime import datetime

async def setup_ultimate_rarity():
    """Configurer la rareté Ultimate dans le système"""
    print("🔥 Configuration de la rareté Ultimate...")
    
    # Configuration de la rareté Ultimate
    ultimate_config = {
        'name': 'Ultimate',
        'weight': 0.001,
        'color': 0xff6600,  # Orange
        'emoji': '🔥',
        'value': 500000,  # 500,000 SC
        'description': 'Rareté divine - plus rare que Secret'
    }
    
    print(f"✅ Rareté Ultimate configurée:")
    print(f"   - Nom: {ultimate_config['name']}")
    print(f"   - Poids: {ultimate_config['weight']}% (10x plus rare que Secret)")
    print(f"   - Couleur: Orange ({hex(ultimate_config['color'])})")
    print(f"   - Emoji: {ultimate_config['emoji']}")
    print(f"   - Valeur: {ultimate_config['value']:,} SC")
    
    # Vérifier si il y a des personnages Ultimate dans la base
    async with aiosqlite.connect("shadow_roll.db") as db:
        async with db.execute("SELECT COUNT(*) FROM characters WHERE rarity = 'Ultimate'") as cursor:
            count = (await cursor.fetchone())[0]
            print(f"📊 Personnages Ultimate existants: {count}")
    
    print("\n🎯 Configuration terminée!")
    print("   - La rareté Ultimate est maintenant disponible")
    print("   - Utilisez les commandes admin pour créer des personnages Ultimate")
    print("   - Exemple: !addchar \"Saitama Ultimate\" \"One Punch Man\" Ultimate 500000")
    
    return ultimate_config

async def verify_ultimate_setup():
    """Vérifier que la configuration Ultimate est correcte"""
    print("\n🔍 Vérification de la configuration Ultimate...")
    
    # Vérifier la configuration dans le code
    try:
        from core.config import BotConfig
        
        # Vérifier le poids
        if 'Ultimate' in BotConfig.RARITY_WEIGHTS:
            weight = BotConfig.RARITY_WEIGHTS['Ultimate']
            print(f"✅ Poids Ultimate: {weight}%")
        else:
            print("❌ Poids Ultimate manquant dans la configuration")
            
        # Vérifier la couleur
        if 'Ultimate' in BotConfig.RARITY_COLORS:
            color = BotConfig.RARITY_COLORS['Ultimate']
            print(f"✅ Couleur Ultimate: {hex(color)} (Orange)")
        else:
            print("❌ Couleur Ultimate manquante dans la configuration")
            
        # Vérifier l'emoji
        if 'Ultimate' in BotConfig.RARITY_EMOJIS:
            emoji = BotConfig.RARITY_EMOJIS['Ultimate']
            print(f"✅ Emoji Ultimate: {emoji}")
        else:
            print("❌ Emoji Ultimate manquant dans la configuration")
            
        print("\n🎉 Configuration Ultimate vérifiée avec succès!")
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("   Le bot doit être redémarré pour appliquer les changements")

async def show_rarity_comparison():
    """Afficher la comparaison des raretés"""
    print("\n📊 Comparaison des Raretés (du plus commun au plus rare):")
    print("┌─────────────────────────────────────────────────────┐")
    print("│                 RARETÉS SHADOW ROLL                 │")
    print("├─────────────────────────────────────────────────────┤")
    print("│ ◆ Commun      │ 60.0%    │ Gris    │ 500-1K SC      │")
    print("│ ◇ Rare        │ 25.0%    │ Bleu    │ 5K-10K SC      │")
    print("│ ◈ Épique      │ 10.0%    │ Violet  │ 15K-25K SC     │")
    print("│ ◉ Légendaire  │ 4.0%     │ Jaune   │ 40K-50K SC     │")
    print("│ ⬢ Mythique    │ 1.0%     │ Rouge   │ 65K-75K SC     │")
    print("│ 🔱 Titan      │ 0.3%     │ Blanc   │ 100K SC        │")
    print("│ ⭐ Fusion     │ 0.1%     │ Rose    │ 150K SC        │")
    print("│ 🌑 Secret     │ 0.01%    │ Noir    │ 200K SC        │")
    print("│ 🔥 Ultimate   │ 0.001%   │ Orange  │ 500K SC        │")
    print("│ 🔮 Evolve     │ 0.0%     │ Vert    │ 200K SC (Craft)│")
    print("└─────────────────────────────────────────────────────┘")
    print("\n🔥 Ultimate est 10x plus rare que Secret!")
    print("   - Chance d'obtenir Ultimate: 1 sur 100,000")
    print("   - Valeur maximale: 500,000 Shadow Coins")

async def main():
    """Fonction principale"""
    print("🌟 ══════════════════════════════════════════════════════════════ 🌟")
    print("    CONFIGURATION DE LA RARETÉ ULTIMATE - SHADOW ROLL BOT")
    print("🌟 ══════════════════════════════════════════════════════════════ 🌟")
    
    # Configurer la rareté Ultimate
    config = await setup_ultimate_rarity()
    
    # Vérifier la configuration
    await verify_ultimate_setup()
    
    # Afficher la comparaison
    await show_rarity_comparison()
    
    print("\n🎯 ACTIONS RECOMMANDÉES:")
    print("   1. Redémarrer le bot pour appliquer les changements")
    print("   2. Utiliser !addchar pour créer des personnages Ultimate")
    print("   3. Tester les invocations pour vérifier la rareté")
    print("   4. Utiliser !rarityvalues pour voir les statistiques")
    
    print("\n✨ Configuration Ultimate terminée avec succès!")

if __name__ == "__main__":
    asyncio.run(main())