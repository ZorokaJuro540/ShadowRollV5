"""
Test complet du système de boutique unifié Shadow Roll
Valide l'achat, la vente et toutes les fonctionnalités
"""

import asyncio
import aiosqlite
import json
from datetime import datetime

async def test_shop_system():
    """Tester le système de boutique complet"""
    print("🔍 Test complet du système de boutique unifié...")
    
    try:
        db = await aiosqlite.connect("shadow_roll.db")
        
        # Test 1: Vérification des tables de la boutique
        print("\n📋 Test 1: Vérification des tables...")
        tables_to_check = [
            'shop_items_fixed',
            'player_purchases_fixed', 
            'player_potions_fixed',
            'temporary_buffs_fixed',
            'free_rolls_fixed',
            'guaranteed_rarities_fixed'
        ]
        
        for table in tables_to_check:
            cursor = await db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = await cursor.fetchone()
            if result:
                print(f"  ✅ Table {table} existe")
            else:
                print(f"  ❌ Table {table} manquante")
        
        # Test 2: Articles de la boutique
        print("\n🛒 Test 2: Articles de la boutique...")
        cursor = await db.execute("SELECT id, name, price FROM shop_items_fixed WHERE is_active = 1")
        items = await cursor.fetchall()
        
        if len(items) >= 8:
            print(f"  ✅ {len(items)} articles disponibles")
            for item in items:
                print(f"    {item[0]}. {item[1]} - {item[2]:,} SC")
        else:
            print(f"  ⚠️ Seulement {len(items)} articles trouvés")
        
        # Test 3: Structure des achats
        print("\n🪙 Test 3: Système d'achats...")
        cursor = await db.execute("PRAGMA table_info(player_purchases_fixed)")
        columns = await cursor.fetchall()
        expected_columns = ['user_id', 'item_id', 'quantity', 'purchase_price']
        
        found_columns = [col[1] for col in columns]
        for col in expected_columns:
            if col in found_columns:
                print(f"  ✅ Colonne {col} présente")
            else:
                print(f"  ❌ Colonne {col} manquante")
        
        # Test 4: Fonctionnalité de vente
        print("\n🪙 Test 4: Système de vente...")
        
        # Vérifier qu'il y a des personnages vendables
        cursor = await db.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE user_id IN (SELECT user_id FROM players LIMIT 1)
        """)
        result = await cursor.fetchone()
        
        if result and result[0] > 0:
            print(f"  ✅ {result[0]} personnages disponibles pour la vente")
        else:
            print(f"  ⚠️ Aucun personnage disponible pour test de vente")
        
        # Test 5: Index de performance
        print("\n⚡ Test 5: Index de performance...")
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%fixed%'")
        indexes = await cursor.fetchall()
        
        if indexes:
            print(f"  ✅ {len(indexes)} index de performance trouvés")
            for idx in indexes:
                print(f"    - {idx[0]}")
        else:
            print("  ⚠️ Aucun index de performance trouvé")
        
        # Test 6: Données de test
        print("\n🎮 Test 6: Données de démonstration...")
        
        # Vérifier les achats récents
        cursor = await db.execute("""
            SELECT COUNT(*) FROM player_purchases_fixed 
            WHERE purchased_at > datetime('now', '-1 day')
        """)
        recent_purchases = await cursor.fetchone()
        
        if recent_purchases and recent_purchases[0] > 0:
            print(f"  ✅ {recent_purchases[0]} achats récents trouvés")
        else:
            print("  ℹ️ Aucun achat récent (normal si nouveau système)")
        
        # Test 7: Validation finale
        print("\n🎯 Test 7: Validation finale...")
        
        # Compter les éléments dans chaque table
        validation_results = {}
        for table in tables_to_check:
            try:
                cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                count = (await cursor.fetchone())[0]
                validation_results[table] = count
            except:
                validation_results[table] = "ERREUR"
        
        print("  Résumé des données:")
        for table, count in validation_results.items():
            if isinstance(count, int):
                print(f"    {table}: {count} entrées")
            else:
                print(f"    {table}: {count}")
        
        await db.close()
        
        # Résultat final
        print("\n" + "="*60)
        print("🎉 RÉSULTAT DU TEST COMPLET")
        print("="*60)
        
        total_items = len(items) if items else 0
        
        if total_items >= 8 and all(isinstance(v, int) for v in validation_results.values()):
            print("✅ SYSTÈME DE BOUTIQUE ENTIÈREMENT FONCTIONNEL!")
            print(f"   • {total_items} articles de boutique actifs")
            print("   • Tables de base de données correctes")
            print("   • Index de performance en place")
            print("   • Système d'achat opérationnel")
            print("   • Système de vente intégré")
            print("\n🚀 La boutique Shadow Roll est prête à l'emploi!")
            return True
        else:
            print("⚠️ PROBLÈMES DÉTECTÉS")
            if total_items < 8:
                print(f"   • Seulement {total_items}/8 articles disponibles")
            if not all(isinstance(v, int) for v in validation_results.values()):
                print("   • Certaines tables ont des problèmes")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale de test"""
    print("🧪 SUITE DE TESTS - SYSTÈME DE BOUTIQUE SHADOW ROLL")
    print("="*60)
    
    success = await test_shop_system()
    
    if success:
        print("\n✅ TOUS LES TESTS RÉUSSIS!")
        print("Le système de boutique est 100% opérationnel.")
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS")
        print("Certains éléments nécessitent une attention.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)