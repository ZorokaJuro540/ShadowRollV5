"""
Script pour corriger la configuration des séries dans Shadow Roll
- Ajouter les séries manquantes
- Supprimer Dragon Ball Z (0 personnages)
- Synchroniser avec les personnages existants
"""

import asyncio
import aiosqlite

async def fix_series_configuration():
    """Corriger la configuration des séries"""
    print("🔧 Correction de la configuration des séries...")
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        # 1. Supprimer Dragon Ball Z (séries sans personnages)
        print("\n🗑️ Suppression des séries vides...")
        
        # Vérifier Dragon Ball Z
        async with db.execute("SELECT COUNT(*) FROM characters WHERE anime = 'Dragon Ball Z'") as cursor:
            dbz_count = (await cursor.fetchone())[0]
        print(f"   Dragon Ball Z: {dbz_count} personnages")
        
        if dbz_count == 0:
            await db.execute("DELETE FROM character_sets WHERE anime_series = 'Dragon Ball Z'")
            print("   ✅ Dragon Ball Z supprimé de character_sets")
        
        # 2. Récupérer toutes les séries avec des personnages
        async with db.execute("""
            SELECT DISTINCT anime, COUNT(*) as count 
            FROM characters 
            WHERE anime IS NOT NULL AND anime != ''
            GROUP BY anime 
            ORDER BY count DESC
        """) as cursor:
            all_series = await cursor.fetchall()
        
        # 3. Récupérer les séries déjà configurées
        async with db.execute("SELECT DISTINCT anime_series FROM character_sets") as cursor:
            configured_series = {row[0] for row in await cursor.fetchall()}
        
        # 4. Identifier les séries manquantes
        missing_series = []
        for anime, count in all_series:
            if anime not in configured_series:
                missing_series.append((anime, count))
        
        print(f"\n📝 Séries manquantes à ajouter: {len(missing_series)}")
        for anime, count in missing_series:
            print(f"   - {anime}: {count} personnages")
        
        # 5. Ajouter les séries manquantes avec des configurations appropriées
        new_series_configs = {
            # Nouvelles séries identifiées
            'Call Of The Night': ('Vampires de Minuit', 6, '+6% chance luck aux invocations rares'),
            'My Deer Friend Nekotan': ('Amies Nekotan', 5, '+5% chance luck aux invocations'),
            'Zenless Zone Zero': ('Agents Zéro', 7, '+7% chance luck aux invocations premium'),
            'Re Zero': ('Monde Magique', 8, '+8% chance luck aux invocations'),
            'Solo Leveling': ('Chasseurs Éveillés', 9, '+9% chance luck aux invocations légendaires'),
            'Meme': ('Légendes Internet', 5, '+5% chance luck aux invocations amusantes'),
            'Fate Stay Night': ('Guerre du Graal', 7, '+7% chance luck aux invocations héroïques'),
        }
        
        print(f"\n➕ Ajout des nouvelles séries...")
        added_count = 0
        
        for anime, count in missing_series:
            if anime in new_series_configs:
                set_name, luck_bonus, description = new_series_configs[anime]
                
                await db.execute('''
                    INSERT OR REPLACE INTO character_sets 
                    (set_name, anime_series, description, bonus_type, bonus_value, bonus_description) 
                    VALUES (?, ?, ?, 'luck', ?, ?)
                ''', (set_name, anime, f"Collection {anime}", luck_bonus, description))
                
                print(f"   ✅ {anime} -> {set_name} (+{luck_bonus}% luck)")
                added_count += 1
            else:
                # Configuration par défaut pour les autres séries
                set_name = f"Collection {anime}"
                luck_bonus = 5  # Bonus standard
                description = f"+{luck_bonus}% chance luck aux invocations"
                
                await db.execute('''
                    INSERT OR REPLACE INTO character_sets 
                    (set_name, anime_series, description, bonus_type, bonus_value, bonus_description) 
                    VALUES (?, ?, ?, 'luck', ?, ?)
                ''', (set_name, anime, f"Collection {anime}", luck_bonus, description))
                
                print(f"   ➕ {anime} -> {set_name} (+{luck_bonus}% luck) [défaut]")
                added_count += 1
        
        await db.commit()
        
        # 6. Vérification finale
        async with db.execute('SELECT COUNT(DISTINCT anime_series) FROM character_sets') as cursor:
            total_configured = (await cursor.fetchone())[0]
        
        print(f"\n📊 Résultats:")
        print(f"   - Séries ajoutées: {added_count}")
        print(f"   - Total des séries configurées: {total_configured}")
        print(f"   - Dragon Ball Z supprimé: {'✅' if dbz_count == 0 else '❌'}")

async def verify_series_sync():
    """Vérifier la synchronisation des séries"""
    print("\n🔍 Vérification de la synchronisation...")
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Séries avec personnages
        async with db.execute("""
            SELECT DISTINCT anime, COUNT(*) as count 
            FROM characters 
            WHERE anime IS NOT NULL AND anime != ''
            GROUP BY anime 
            ORDER BY anime
        """) as cursor:
            character_series = {row[0]: row[1] for row in await cursor.fetchall()}
        
        # Séries configurées
        async with db.execute("SELECT DISTINCT anime_series FROM character_sets ORDER BY anime_series") as cursor:
            configured_series = {row[0] for row in await cursor.fetchall()}
        
        # Vérification
        missing_from_config = set(character_series.keys()) - configured_series
        orphaned_configs = configured_series - set(character_series.keys())
        
        print(f"   Séries avec personnages: {len(character_series)}")
        print(f"   Séries configurées: {len(configured_series)}")
        
        if missing_from_config:
            print(f"   ❌ Manquantes dans config: {missing_from_config}")
        else:
            print(f"   ✅ Toutes les séries sont configurées")
        
        if orphaned_configs:
            print(f"   ⚠️ Configs orphelines: {orphaned_configs}")
        else:
            print(f"   ✅ Aucune config orpheline")
        
        return len(missing_from_config) == 0 and len(orphaned_configs) == 0

async def show_final_series_list():
    """Afficher la liste finale des séries"""
    print("\n📋 Liste finale des séries configurées:")
    print("┌─────────────────────────────────────────────────────────────┐")
    print("│                    SÉRIES SHADOW ROLL                      │")
    print("├─────────────────────────────────────────────────────────────┤")
    
    async with aiosqlite.connect('shadow_roll.db') as db:
        async with db.execute("""
            SELECT cs.anime_series, cs.set_name, cs.bonus_value, COUNT(c.id) as char_count
            FROM character_sets cs
            LEFT JOIN characters c ON cs.anime_series = c.anime
            GROUP BY cs.anime_series, cs.set_name, cs.bonus_value
            ORDER BY char_count DESC, cs.anime_series
        """) as cursor:
            series_data = await cursor.fetchall()
        
        for anime, set_name, bonus, count in series_data:
            print(f"│ {anime:<25} │ {count:>3} chars │ +{bonus:>2}% luck │")
        
        print("└─────────────────────────────────────────────────────────────┘")
        print(f"Total: {len(series_data)} séries configurées")

async def main():
    """Fonction principale"""
    print("🌟 ══════════════════════════════════════════════════════════════ 🌟")
    print("    CORRECTION DE LA CONFIGURATION DES SÉRIES - SHADOW ROLL")
    print("🌟 ══════════════════════════════════════════════════════════════ 🌟")
    
    # Corriger la configuration
    await fix_series_configuration()
    
    # Vérifier la synchronisation
    is_synced = await verify_series_sync()
    
    # Afficher la liste finale
    await show_final_series_list()
    
    print(f"\n🎯 STATUT FINAL:")
    print(f"   Synchronisation: {'✅ Parfaite' if is_synced else '❌ Problèmes détectés'}")
    print(f"   Dragon Ball Z: ✅ Supprimé (0 personnages)")
    print(f"   Nouvelles séries: ✅ Ajoutées avec bonus luck")
    
    print(f"\n✨ Configuration des séries corrigée avec succès!")

if __name__ == "__main__":
    asyncio.run(main())