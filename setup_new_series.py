"""
Script pour configurer les nouvelles séries ajoutées
"""

import asyncio
import aiosqlite

async def setup_new_series():
    async with aiosqlite.connect('shadow_roll.db') as db:
        # Récupérer toutes les séries
        async with db.execute('SELECT DISTINCT anime FROM characters ORDER BY anime') as cursor:
            all_series = [row[0] for row in await cursor.fetchall()]
        
        # Récupérer les séries configurées
        async with db.execute('SELECT DISTINCT anime_series FROM character_sets ORDER BY anime_series') as cursor:
            configured_series = [row[0] for row in await cursor.fetchall()]
        
        missing_series = [serie for serie in all_series if serie not in configured_series]
        
        print(f"Séries manquantes à configurer: {missing_series}")
        
        # Nouvelles configurations
        new_configs = [
            ('Re Zero', 'Monde Magique', 8, '+8% chance aux invocations'),
            ('Solo Leveling', 'Chasseurs Éveillés', 9, '+9% chance aux invocations'),
            ('Meme', 'Légendes Internet', 5, '+5% chance aux invocations'),
            ('Fate Stay Night', 'Guerre du Graal', 7, '+7% chance aux invocations')
        ]
        
        for anime, series_name, luck_bonus, description in new_configs:
            if anime in missing_series:
                await db.execute('''
                    INSERT OR REPLACE INTO character_sets 
                    (set_name, anime_series, description, bonus_type, bonus_value, bonus_description) 
                    VALUES (?, ?, ?, 'luck', ?, ?)
                ''', (series_name, anime, f"Collection {anime}", luck_bonus, description))
                print(f"✅ Ajouté: {anime} -> {series_name} (+{luck_bonus}% luck)")
        
        await db.commit()
        
        # Vérifier le total
        async with db.execute('SELECT COUNT(DISTINCT anime_series) FROM character_sets') as cursor:
            total = (await cursor.fetchone())[0]
        
        print(f"📊 Total des séries configurées: {total}")

if __name__ == "__main__":
    asyncio.run(setup_new_series())