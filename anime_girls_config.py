"""
Configuration des personnages d'anime girls pour le jeu "Tu préfères"
Script pour gérer facilement la liste des personnages avec images
"""

# Configuration des personnages d'anime girls
# Format: ("Nom Personnage", "Nom Anime", "URL_Image")
ANIME_GIRLS_LIST = [
    # Attack on Titan
    ("Mikasa Ackerman", "Attack on Titan", "https://cdn.myanimelist.net/images/characters/9/215563.jpg"),
    ("Historia Reiss", "Attack on Titan", "https://static.wikia.nocookie.net/shingekinokyojin/images/f/f4/Historia_Reiss_%28Anime%29_character_image.png"),
    ("Sasha Blouse", "Attack on Titan", "https://static.wikia.nocookie.net/shingekinokyojin/images/4/46/Sasha_Blouse_%28Anime%29_character_image.png"),
    
    # Demon Slayer
    ("Nezuko Kamado", "Demon Slayer", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758947335069739/nezuko.png"),
    ("Shinobu Kocho", "Demon Slayer", "https://static.wikia.nocookie.net/kimetsu-no-yaiba/images/8/86/Shinobu_anime_design.png"),
    ("Kanao Tsuyuri", "Demon Slayer", "https://static.wikia.nocookie.net/kimetsu-no-yaiba/images/1/17/Kanao_anime_design.png"),
    
    # Naruto (Extended)
    ("Hinata Hyuga", "Naruto", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758947637051473/hinata.png"),
    ("Sakura Haruno", "Naruto", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758947901296710/sakura.png"),
    ("Temari", "Naruto", "https://static.wikia.nocookie.net/naruto/images/d/d8/Temari_Part_II.png"),
    ("Ino Yamanaka", "Naruto", "https://static.wikia.nocookie.net/naruto/images/f/f6/Ino_Yamanaka_Part_II.png"),
    ("Tenten", "Naruto", "https://static.wikia.nocookie.net/naruto/images/8/8b/Tenten_Part_II.png"),
    ("Tsunade", "Naruto", "https://static.wikia.nocookie.net/naruto/images/b/b3/Tsunade_infobox2.png"),
    ("Anko Mitarashi", "Naruto", "https://static.wikia.nocookie.net/naruto/images/8/8f/Anko_Mitarashi.png"),
    ("Kurenai Yuhi", "Naruto", "https://static.wikia.nocookie.net/naruto/images/0/07/Kurenai_Yuhi.png"),
    ("Karin", "Naruto", "https://static.wikia.nocookie.net/naruto/images/e/e7/Karin_Part_II.png"),
    ("Konan", "Naruto", "https://static.wikia.nocookie.net/naruto/images/f/f6/Konan.png"),
    ("Mei Terumi", "Naruto", "https://static.wikia.nocookie.net/naruto/images/2/29/Mei_Terumi.png"),
    ("Kushina Uzumaki", "Naruto", "https://static.wikia.nocookie.net/naruto/images/4/42/Kushina_Uzumaki.png"),
    ("Samui", "Naruto", "https://static.wikia.nocookie.net/naruto/images/3/3f/Samui.png"),
    ("Shizune", "Naruto", "https://static.wikia.nocookie.net/naruto/images/7/7a/Shizune.png"),
    
    # Re:Zero
    ("Rem", "Re:Zero", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758948098691092/rem.png"),
    ("Emilia", "Re:Zero", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758948182577162/emilia.png"),
    ("Ram", "Re:Zero", "https://static.wikia.nocookie.net/rezero/images/f/f1/Ram_Anime.png"),
    ("Beatrice", "Re:Zero", "https://static.wikia.nocookie.net/rezero/images/8/8f/Beatrice_Anime.png"),
    
    # Sword Art Online
    ("Asuna", "Sword Art Online", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758948266463272/asuna.png"),
    ("Sinon", "Sword Art Online", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758948350349362/sinon.png"),
    ("Silica", "Sword Art Online", "https://static.wikia.nocookie.net/swordartonline/images/6/61/Silica_SAO.png"),
    ("Lisbeth", "Sword Art Online", "https://static.wikia.nocookie.net/swordartonline/images/7/7c/Lisbeth_SAO.png"),
    
    
    # Fairy Tail
    ("Erza Scarlet", "Fairy Tail", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949135401002/erza.png"),
    ("Lucy Heartfilia", "Fairy Tail", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949227950140/lucy.png"),
    ("Wendy Marvell", "Fairy Tail", "https://static.wikia.nocookie.net/fairytail/images/f/f4/Wendy_Marvell_Anime_S2.png"),
    ("Levy McGarden", "Fairy Tail", "https://static.wikia.nocookie.net/fairytail/images/9/9f/Levy_McGarden_Anime_S2.png"),
    
    # My Hero Academia (Extended)
    ("Ochaco Uraraka", "My Hero Academia", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949320499229/ochaco.png"),
    ("Momo Yaoyorozu", "My Hero Academia", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949408780348/momo.png"),
    ("Tsuyu Asui", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/f/f4/Tsuyu_Asui_Anime.png"),
    ("Kyoka Jiro", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/c/c7/Kyoka_Jiro_Anime.png"),
    ("Mina Ashido", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/a/a1/Mina_Ashido_Anime.png"),
    ("Toru Hagakure", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/7/7b/Toru_Hagakure_Anime.png"),
    ("Nejire Hado", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/9/9e/Nejire_Hado_Anime.png"),
    ("Himiko Toga", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/c/c9/Himiko_Toga_Anime.png"),
    ("Midnight", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/1/19/Midnight_Anime.png"),
    ("Mt. Lady", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/8/82/Mt._Lady_Anime.png"),
    ("Mirko", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/3/3f/Rumi_Usagiyama_Anime.png"),
    ("Ryuko Tatsuma", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/4/4a/Ryuko_Tatsuma_Anime.png"),
    ("Mina Ashido", "My Hero Academia", "https://static.wikia.nocookie.net/bokunoheroacademia/images/a/a2/Mina_Ashido_Anime.png"),
    
    # One Piece (séparés pour éviter les doublons)
    ("Nami", "One Piece", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949488472094/nami.png"),
    ("Nico Robin", "One Piece", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758949555580978/robin.png"),
    ("Vivi", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/4/4a/Nefertari_Vivi_Anime_Post_Timeskip_Infobox.png"),
    ("Perona", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/8/8f/Perona_Anime_Post_Timeskip_Infobox.png"),


    
    # KonoSuba
    ("Aqua", "KonoSuba", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950286319634/aqua.png"),
    ("Megumin", "KonoSuba", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950370205724/megumin.png"),
    ("Darkness", "KonoSuba", "https://static.wikia.nocookie.net/konosuba/images/d/d8/Darkness_Anime.png"),
    ("Wiz", "KonoSuba", "https://static.wikia.nocookie.net/konosuba/images/6/6d/Wiz_Anime.png"),
    
    # Darling in the FranXX
    ("Zero Two", "Darling in the FranXX", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950454091814/zerotwo.png"),
    ("Ichigo", "Darling in the FranXX", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950537977906/ichigo_darling.png"),
    ("Kokoro", "Darling in the FranXX", "https://static.wikia.nocookie.net/darling-in-the-franxx/images/6/6a/Kokoro_Anime.png"),
    
    # Fate Series
    ("Tohsaka Rin", "Fate Series", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950613475338/rin.png"),
    ("Saber", "Fate Series", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950689238036/saber.png"),
    ("Sakura Matou", "Fate Series", "https://static.wikia.nocookie.net/typemoon/images/e/e8/Sakura_Matou_Fate_stay_night_Anime.png"),
    ("Rider", "Fate Series", "https://static.wikia.nocookie.net/typemoon/images/f/f4/Rider_Fate_stay_night_Anime.png"),
    
    # Kaguya-sama
    ("Kaguya Shinomiya", "Kaguya-sama", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950768664586/kaguya.png"),
    ("Chika Fujiwara", "Kaguya-sama", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950848356352/chika.png"),
    ("Ai Hayasaka", "Kaguya-sama", "https://static.wikia.nocookie.net/kaguyasama-wa-kokurasetai/images/2/2a/Ai_Hayasaka_Anime.png"),
    
    # Kakegurui
    ("Yumeko Jabami", "Kakegurui", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758950924115998/yumeko.png"),
    ("Mary Saotome", "Kakegurui", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758951016665088/mary.png"),
    ("Kirari Momobami", "Kakegurui", "https://static.wikia.nocookie.net/kakegurui/images/3/3b/Kirari_Momobami_Anime.png"),
    
    # Bunny Girl Senpai
    ("Mai Sakurajima", "Bunny Girl Senpai", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758951079186432/mai.png"),
    ("Tomoe Koga", "Bunny Girl Senpai", "https://cdn.discordapp.com/attachments/1047983900438724689/1327758951154946068/tomoe.png"),
    ("Rio Futaba", "Bunny Girl Senpai", "https://static.wikia.nocookie.net/aobuta/images/9/9e/Rio_Futaba_Anime.png"),
    
    # Jujutsu Kaisen
    ("Nobara Kugisaki", "Jujutsu Kaisen", "https://static.wikia.nocookie.net/jujutsu-kaisen/images/d/d0/Nobara_Kugisaki_Anime.png"),
    ("Maki Zenin", "Jujutsu Kaisen", "https://static.wikia.nocookie.net/jujutsu-kaisen/images/0/0c/Maki_Zenin_Anime.png"),
    ("Shoko Ieiri", "Jujutsu Kaisen", "https://static.wikia.nocookie.net/jujutsu-kaisen/images/3/3c/Shoko_Ieiri_Anime.png"),
    
    # Tokyo Ghoul
    ("Touka Kirishima", "Tokyo Ghoul", "https://static.wikia.nocookie.net/tokyoghoul/images/7/73/Touka_Kirishima_Anime.png"),
    ("Rize Kamishiro", "Tokyo Ghoul", "https://static.wikia.nocookie.net/tokyoghoul/images/a/a9/Rize_Kamishiro_Anime.png"),
    ("Hinami Fueguchi", "Tokyo Ghoul", "https://static.wikia.nocookie.net/tokyoghoul/images/5/5a/Hinami_Fueguchi_Anime.png"),
    
    # Chainsaw Man
    ("Power", "Chainsaw Man", "https://static.wikia.nocookie.net/chainsaw-man/images/d/d4/Power_Anime.png"),
    ("Makima", "Chainsaw Man", "https://static.wikia.nocookie.net/chainsaw-man/images/9/9e/Makima_Anime.png"),
    ("Kobeni Higashiyama", "Chainsaw Man", "https://static.wikia.nocookie.net/chainsaw-man/images/c/c3/Kobeni_Higashiyama_Anime.png"),
    
    # Spy x Family
    ("Yor Forger", "Spy x Family", "https://static.wikia.nocookie.net/spy-x-family6409/images/5/5a/Yor_Forger_Anime.png"),
    ("Anya Forger", "Spy x Family", "https://static.wikia.nocookie.net/spy-x-family6409/images/f/f4/Anya_Forger_Anime.png"),
    ("Fiona Frost", "Spy x Family", "https://static.wikia.nocookie.net/spy-x-family6409/images/a/a7/Fiona_Frost_Anime.png"),
    
    # Dragon Ball (Extended)
    ("Bulma", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/4/4a/Bulma_DBS_Anime.png"),
    ("Android 18", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/f/f1/Android_18_DBS_Anime.png"),
    ("Chi-Chi", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/8/8a/Chi-Chi_DBS_Anime.png"),
    ("Videl", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/b/bf/Videl_DBS.png"),
    ("Launch", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/4/4c/Launch_Good.png"),
    ("Pan", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/d/d4/Pan_DBS.png"),
    ("Caulifla", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/4/4c/Caulifla_DBS.png"),
    ("Kale", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/7/7f/Kale_DBS.png"),
    ("Vados", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/3/39/Vados_DBS.png"),
    ("Marcarita", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/8/8c/Marcarita_DBS.png"),
    ("Ribrianne", "Dragon Ball", "https://static.wikia.nocookie.net/dragonball/images/9/9f/Ribrianne_DBS.png"),
    
    # Death Note
    ("Misa Amane", "Death Note", "https://static.wikia.nocookie.net/deathnote/images/4/4a/Misa_Amane_Anime.png"),
    
    # Bleach
    ("Orihime Inoue", "Bleach", "https://static.wikia.nocookie.net/bleach/images/0/0f/Orihime_Inoue_Anime.png"),
    ("Rukia Kuchiki", "Bleach", "https://static.wikia.nocookie.net/bleach/images/2/2f/Rukia_Kuchiki_Anime.png"),
    ("Rangiku Matsumoto", "Bleach", "https://static.wikia.nocookie.net/bleach/images/e/e4/Rangiku_Matsumoto_Anime.png"),
    
    # Haikyuu!!
    ("Kiyoko Shimizu", "Haikyuu!!", "https://static.wikia.nocookie.net/haikyuu/images/8/82/Kiyoko_Shimizu_Anime.png"),
    ("Yachi Hitoka", "Haikyuu!!", "https://static.wikia.nocookie.net/haikyuu/images/6/63/Yachi_Hitoka_Anime.png"),
    
    # Food Wars!
    ("Erina Nakiri", "Food Wars!", "https://static.wikia.nocookie.net/shokugekinosoma/images/c/c8/Erina_Nakiri_Anime.png"),
    ("Megumi Tadokoro", "Food Wars!", "https://static.wikia.nocookie.net/shokugekinosoma/images/f/f7/Megumi_Tadokoro_Anime.png"),
    
    # Mob Psycho 100
    ("Tome Kurata", "Mob Psycho 100", "https://static.wikia.nocookie.net/mob-psycho-100/images/f/f4/Tome_Kurata_Anime.png"),
    
    # Code Geass
    ("C.C.", "Code Geass", "https://static.wikia.nocookie.net/codegeass/images/1/1c/C.C._Anime.png"),
    ("Kallen Stadtfeld", "Code Geass", "https://static.wikia.nocookie.net/codegeass/images/2/29/Kallen_Stadtfeld_Anime.png"),
    
    # Overlord
    ("Albedo", "Overlord", "https://static.wikia.nocookie.net/overlordmaruyama/images/0/0a/Albedo_Anime.png"),
    ("Shalltear Bloodfallen", "Overlord", "https://static.wikia.nocookie.net/overlordmaruyama/images/3/3f/Shalltear_Bloodfallen_Anime.png"),
    
    # One Piece (NEW!)
    ("Nami", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/9/9f/Nami_Anime_Post_Timeskip_Infobox.png"),
    ("Nico Robin", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/4/48/Nico_Robin_Anime_Post_Timeskip_Infobox.png"),
    ("Boa Hancock", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/8/88/Boa_Hancock_Anime_Infobox.png"),
    ("Perona", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/6/6e/Perona_Anime_Post_Timeskip_Infobox.png"),
    ("Vivi Nefertari", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/c/c8/Nefertari_Vivi_Anime_Post_Timeskip_Infobox.png"),
    ("Reiju Vinsmoke", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/2/21/Vinsmoke_Reiju_Anime_Infobox.png"),
    ("Ulti", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/7/77/Ulti_Anime_Infobox.png"),
    ("Black Maria", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/a/ab/Black_Maria_Anime_Infobox.png"),
    ("Yamato", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/d/d2/Yamato_Anime_Infobox.png"),
    ("Carrot", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/8/8c/Carrot_Anime_Infobox.png"),
    ("Hiyori Kozuki", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/f/f6/Kozuki_Hiyori_Anime_Infobox.png"),
    ("Shirahoshi", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/0/02/Shirahoshi_Anime_Infobox.png"),
    ("Rebecca", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/1/1c/Rebecca_Anime_Infobox.png"),
    ("Baby 5", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/3/3c/Baby_5_Anime_Infobox.png"),
    ("Viola", "One Piece", "https://static.wikia.nocookie.net/onepiece/images/f/f2/Viola_Anime_Infobox.png"),

    # Konosuba (NEW!)
    ("Aqua", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/6/60/Aqua_anime.png"),
    ("Megumin", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/8/8e/Megumin_anime.png"),
    ("Darkness", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/e/e0/Darkness_anime.png"),
    ("Wiz", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/f/fc/Wiz_anime.png"),
    ("Yunyun", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/a/ab/Yunyun_anime.png"),
    ("Eris", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/7/7a/Eris_anime.png"),
    ("Luna", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/5/58/Luna_anime.png"),
    ("Iris", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/c/c8/Iris_anime.png"),
    ("Chris", "Konosuba", "https://static.wikia.nocookie.net/konosuba/images/2/2f/Chris_anime.png"),

    # Solo Leveling (NEW!)
    ("Cha Hae-In", "Solo Leveling", "https://static.wikia.nocookie.net/solo-leveling/images/1/1f/Cha_Hae-In_Anime.png"),
    ("Yoo Soohyun", "Solo Leveling", "https://static.wikia.nocookie.net/solo-leveling/images/4/42/Yoo_Soohyun_Anime.png"),
    ("Lee Ju-Hee", "Solo Leveling", "https://static.wikia.nocookie.net/solo-leveling/images/8/8f/Lee_Ju-Hee_Anime.png"),
    ("Norma Selner", "Solo Leveling", "https://static.wikia.nocookie.net/solo-leveling/images/6/6a/Norma_Selner_Anime.png"),

    # Oshi no Ko (NEW!)
    ("Ai Hoshino", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/8/8e/Ai_Hoshino_Anime.png"),
    ("Ruby Hoshino", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/f/f0/Ruby_Hoshino_Anime.png"),
    ("Kana Arima", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/6/6a/Kana_Arima_Anime.png"),
    ("Akane Kurokawa", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/3/31/Akane_Kurokawa_Anime.png"),
    ("Mem-Cho", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/9/90/Mem-Cho_Anime.png"),
    ("Miyako Saitou", "Oshi no Ko", "https://static.wikia.nocookie.net/oshi-no-ko/images/a/a5/Miyako_Saitou_Anime.png"),
    
    # No Game No Life
    ("Shiro", "No Game No Life", "https://static.wikia.nocookie.net/no-game-no-life/images/6/6d/Shiro_Anime.png"),
    ("Stephanie Dola", "No Game No Life", "https://static.wikia.nocookie.net/no-game-no-life/images/e/e9/Stephanie_Dola_Anime.png"),
    
    # Danmachi
    ("Hestia", "Danmachi", "https://static.wikia.nocookie.net/dungeon-ni-deai-wo-motomeru/images/f/f4/Hestia_Anime.png"),
    ("Ais Wallenstein", "Danmachi", "https://static.wikia.nocookie.net/dungeon-ni-deai-wo-motomeru/images/8/85/Ais_Wallenstein_Anime.png"),
    
    # Highschool DxD
    ("Rias Gremory", "Highschool DxD", "https://static.wikia.nocookie.net/highschooldxd/images/3/3b/Rias_Gremory_Anime.png"),
    ("Akeno Himejima", "Highschool DxD", "https://static.wikia.nocookie.net/highschooldxd/images/9/9a/Akeno_Himejima_Anime.png"),
    
    # Toradora!
    ("Taiga Aisaka", "Toradora!", "https://static.wikia.nocookie.net/toradora/images/7/7e/Taiga_Aisaka_Anime.png"),
    ("Minori Kushieda", "Toradora!", "https://static.wikia.nocookie.net/toradora/images/9/96/Minori_Kushieda_Anime.png"),
    ("Ami Kawashima", "Toradora!", "https://static.wikia.nocookie.net/toradora/images/f/f4/Ami_Kawashima_Anime.png"),
    
    # K-On!
    ("Yui Hirasawa", "K-On!", "https://static.wikia.nocookie.net/k-on/images/7/7e/Yui_Hirasawa_Anime.png"),
    ("Mio Akiyama", "K-On!", "https://static.wikia.nocookie.net/k-on/images/a/a9/Mio_Akiyama_Anime.png"),
    ("Ritsu Tainaka", "K-On!", "https://static.wikia.nocookie.net/k-on/images/f/f8/Ritsu_Tainaka_Anime.png"),
    ("Tsumugi Kotobuki", "K-On!", "https://static.wikia.nocookie.net/k-on/images/0/0a/Tsumugi_Kotobuki_Anime.png"),
    ("Azusa Nakano", "K-On!", "https://static.wikia.nocookie.net/k-on/images/3/3a/Azusa_Nakano_Anime.png"),
    
    # Love Live!
    ("Honoka Kosaka", "Love Live!", "https://static.wikia.nocookie.net/love-live/images/f/f4/Honoka_Kosaka_Anime.png"),
    ("Kotori Minami", "Love Live!", "https://static.wikia.nocookie.net/love-live/images/9/9a/Kotori_Minami_Anime.png"),
    ("Umi Sonoda", "Love Live!", "https://static.wikia.nocookie.net/love-live/images/8/82/Umi_Sonoda_Anime.png"),
    
    # Persona
    ("Makoto Niijima", "Persona", "https://static.wikia.nocookie.net/megamitensei/images/f/f4/Makoto_Niijima_Anime.png"),
    ("Futaba Sakura", "Persona", "https://static.wikia.nocookie.net/megamitensei/images/a/a9/Futaba_Sakura_Anime.png"),
    ("Ann Takamaki", "Persona", "https://static.wikia.nocookie.net/megamitensei/images/2/2f/Ann_Takamaki_Anime.png"),
    
    # Black Clover (NEW!)
    ("Noelle Silva", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/7/7f/Noelle_Silva_Anime.png"),
    ("Mimosa Vermillion", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/f/f8/Mimosa_Vermillion_Anime.png"),
    ("Vanessa Enoteca", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/1/1f/Vanessa_Enoteca_Anime.png"),
    ("Charmy Pappitson", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/8/8f/Charmy_Pappitson_Anime.png"),
    ("Dorothy Unsworth", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/3/38/Dorothy_Unsworth_Anime.png"),
    ("Mereoleona Vermillion", "Black Clover", "https://static.wikia.nocookie.net/blackclover/images/0/0f/Mereoleona_Vermillion_Anime.png"),

    # Fire Force (NEW!)
    ("Tamaki Kotatsu", "Fire Force", "https://static.wikia.nocookie.net/fire-brigade-of-flames/images/0/0f/Tamaki_Kotatsu_Anime.png"),
    ("Maki Oze", "Fire Force", "https://static.wikia.nocookie.net/fire-brigade-of-flames/images/1/1f/Maki_Oze_Anime.png"),
    ("Iris", "Fire Force", "https://static.wikia.nocookie.net/fire-brigade-of-flames/images/8/8f/Iris_Anime.png"),
    ("Princess Hibana", "Fire Force", "https://static.wikia.nocookie.net/fire-brigade-of-flames/images/4/4c/Hibana_Anime.png"),

    # Dr. Stone (NEW!)
    ("Kohaku", "Dr. Stone", "https://static.wikia.nocookie.net/dr-stone/images/f/f4/Kohaku_Anime.png"),
    ("Yuzuriha Ogawa", "Dr. Stone", "https://static.wikia.nocookie.net/dr-stone/images/3/3f/Yuzuriha_Ogawa_Anime.png"),
    ("Ruri", "Dr. Stone", "https://static.wikia.nocookie.net/dr-stone/images/0/0f/Ruri_Anime.png"),
    ("Suika", "Dr. Stone", "https://static.wikia.nocookie.net/dr-stone/images/8/8f/Suika_Anime.png"),

    # Violet Evergarden (NEW!)
    ("Violet Evergarden", "Violet Evergarden", "https://static.wikia.nocookie.net/violet-evergarden/images/f/f0/Violet_Evergarden_Anime.png"),
    ("Cattleya Baudelaire", "Violet Evergarden", "https://static.wikia.nocookie.net/violet-evergarden/images/4/4c/Cattleya_Baudelaire_Anime.png"),
    ("Iris Cannary", "Violet Evergarden", "https://static.wikia.nocookie.net/violet-evergarden/images/8/8f/Iris_Cannary_Anime.png"),

    # Hunter x Hunter (NEW!)
    ("Biscuit Krueger", "Hunter x Hunter", "https://static.wikia.nocookie.net/hunterxhunter/images/f/f4/Biscuit_Krueger_Anime.png"),
    ("Menchi", "Hunter x Hunter", "https://static.wikia.nocookie.net/hunterxhunter/images/0/0f/Menchi_Anime.png"),
    ("Palm Siberia", "Hunter x Hunter", "https://static.wikia.nocookie.net/hunterxhunter/images/8/8f/Palm_Siberia_Anime.png"),
    ("Neferpitou", "Hunter x Hunter", "https://static.wikia.nocookie.net/hunterxhunter/images/4/4c/Neferpitou_Anime.png"),

    # Akame ga Kill (NEW!)
    ("Akame", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/f/f4/Akame_Anime.png"),
    ("Mine", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/0/0f/Mine_Anime.png"),
    ("Leone", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/8/8f/Leone_Anime.png"),
    ("Sheele", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/4/4c/Sheele_Anime.png"),
    ("Chelsea", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/f/f0/Chelsea_Anime.png"),
    ("Najenda", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/0/0a/Najenda_Anime.png"),
    ("Esdeath", "Akame ga Kill", "https://static.wikia.nocookie.net/akamegakill/images/1/1f/Esdeath_Anime.png"),

    # Seven Deadly Sins (NEW!)
    ("Elizabeth Liones", "Seven Deadly Sins", "https://static.wikia.nocookie.net/nanatsu-no-taizai/images/f/f4/Elizabeth_Liones_Anime.png"),
    ("Diane", "Seven Deadly Sins", "https://static.wikia.nocookie.net/nanatsu-no-taizai/images/0/0f/Diane_Anime.png"),
    ("Merlin", "Seven Deadly Sins", "https://static.wikia.nocookie.net/nanatsu-no-taizai/images/8/8f/Merlin_Anime.png"),
    ("Jericho", "Seven Deadly Sins", "https://static.wikia.nocookie.net/nanatsu-no-taizai/images/4/4c/Jericho_Anime.png"),

    # Attack on Titan (Additional)
    ("Annie Leonhart", "Attack on Titan", "https://static.wikia.nocookie.net/shingekinokyojin/images/f/f3/Annie_Leonhart_%28Anime%29_character_image.png"),
    ("Pieck Finger", "Attack on Titan", "https://static.wikia.nocookie.net/shingekinokyojin/images/a/a7/Pieck_Finger_%28Anime%29_character_image.png"),
    ("Ymir", "Attack on Titan", "https://static.wikia.nocookie.net/shingekinokyojin/images/8/8f/Ymir_%28Anime%29_character_image.png"),
    
    # JoJo's Bizarre Adventure (NEW!)
    ("Jolyne Cujoh", "JoJo's Bizarre Adventure", "https://static.wikia.nocookie.net/jjba/images/f/f4/Jolyne_Cujoh_Anime.png"),
    ("Trish Una", "JoJo's Bizarre Adventure", "https://static.wikia.nocookie.net/jjba/images/0/0f/Trish_Una_Anime.png"),
    ("Lisa Lisa", "JoJo's Bizarre Adventure", "https://static.wikia.nocookie.net/jjba/images/8/8f/Lisa_Lisa_Anime.png"),
    ("Yukako Yamagishi", "JoJo's Bizarre Adventure", "https://static.wikia.nocookie.net/jjba/images/4/4c/Yukako_Yamagishi_Anime.png"),

    # Fullmetal Alchemist (NEW!)
    ("Winry Rockbell", "Fullmetal Alchemist", "https://static.wikia.nocookie.net/fma/images/f/f4/Winry_Rockbell_Anime.png"),
    ("Riza Hawkeye", "Fullmetal Alchemist", "https://static.wikia.nocookie.net/fma/images/0/0f/Riza_Hawkeye_Anime.png"),
    ("May Chang", "Fullmetal Alchemist", "https://static.wikia.nocookie.net/fma/images/8/8f/May_Chang_Anime.png"),
    ("Olivier Armstrong", "Fullmetal Alchemist", "https://static.wikia.nocookie.net/fma/images/4/4c/Olivier_Armstrong_Anime.png"),

    # Mob Psycho 100 (Additional)
    ("Tome Kurata", "Mob Psycho 100", "https://static.wikia.nocookie.net/mob-psycho-100/images/f/f4/Tome_Kurata_Anime.png"),
    ("Emi", "Mob Psycho 100", "https://static.wikia.nocookie.net/mob-psycho-100/images/0/0f/Emi_Anime.png"),

    # Classroom of the Elite (NEW!)
    ("Suzune Horikita", "Classroom of the Elite", "https://static.wikia.nocookie.net/youkoso-jitsuryoku-shijou-shugi/images/f/f4/Suzune_Horikita_Anime.png"),
    ("Kikyou Kushida", "Classroom of the Elite", "https://static.wikia.nocookie.net/youkoso-jitsuryoku-shijou-shugi/images/0/0f/Kikyou_Kushida_Anime.png"),
    ("Arisu Sakayanagi", "Classroom of the Elite", "https://static.wikia.nocookie.net/youkoso-jitsuryoku-shijou-shugi/images/8/8f/Arisu_Sakayanagi_Anime.png"),

    # Quintessential Quintuplets (NEW!)
    ("Ichika Nakano", "Quintessential Quintuplets", "https://static.wikia.nocookie.net/5-toubun-no-hanayome/images/f/f4/Ichika_Nakano_Anime.png"),
    ("Nino Nakano", "Quintessential Quintuplets", "https://static.wikia.nocookie.net/5-toubun-no-hanayome/images/0/0f/Nino_Nakano_Anime.png"),
    ("Miku Nakano", "Quintessential Quintuplets", "https://static.wikia.nocookie.net/5-toubun-no-hanayome/images/8/8f/Miku_Nakano_Anime.png"),
    ("Yotsuba Nakano", "Quintessential Quintuplets", "https://static.wikia.nocookie.net/5-toubun-no-hanayome/images/4/4c/Yotsuba_Nakano_Anime.png"),
    ("Itsuki Nakano", "Quintessential Quintuplets", "https://static.wikia.nocookie.net/5-toubun-no-hanayome/images/1/1f/Itsuki_Nakano_Anime.png"),
]

def get_anime_girls_by_series():
    """Retourne un dictionnaire groupé par série"""
    by_series = {}
    for name, anime, image_url in ANIME_GIRLS_LIST:
        if anime not in by_series:
            by_series[anime] = []
        by_series[anime].append((name, image_url))
    return by_series

def get_diverse_matchups(count=20):
    """Génère des matchups diversifiés évitant les personnages du même anime"""
    import random
    from collections import defaultdict
    
    # Grouper par anime
    by_anime = defaultdict(list)
    for name, anime, image_url in ANIME_GIRLS_LIST:
        by_anime[anime].append((name, anime, image_url))
    
    matchups = []
    used_characters = set()
    
    # Créer des matchups en évitant les doublons d'anime
    anime_list = list(by_anime.keys())
    
    for _ in range(count):
        # Choisir deux animes différents
        available_animes = [anime for anime in anime_list 
                           if any(char[0] not in used_characters for char in by_anime[anime])]
        
        if len(available_animes) < 2:
            # Réinitialiser si on n'a plus assez d'animes disponibles
            used_characters.clear()
            available_animes = anime_list
        
        anime1, anime2 = random.sample(available_animes, 2)
        
        # Choisir un personnage de chaque anime
        char1_options = [char for char in by_anime[anime1] if char[0] not in used_characters]
        char2_options = [char for char in by_anime[anime2] if char[0] not in used_characters]
        
        if char1_options and char2_options:
            char1 = random.choice(char1_options)
            char2 = random.choice(char2_options)
            
            matchups.append((char1[0], char2[0], char1[2], char2[2]))
            used_characters.add(char1[0])
            used_characters.add(char2[0])
    
    return matchups

def print_stats():
    """Affiche les statistiques de la liste"""
    by_series = get_anime_girls_by_series()
    
    print("📊 STATISTIQUES DES ANIME GIRLS")
    print("=" * 50)
    print(f"Total de personnages: {len(ANIME_GIRLS_LIST)}")
    print(f"Total d'animes: {len(by_series)}")
    print()
    
    print("📋 RÉPARTITION PAR ANIME:")
    print("-" * 30)
    for anime, characters in sorted(by_series.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"{anime}: {len(characters)} personnages")
    
    print()
    print("🎲 EXEMPLE DE MATCHUPS DIVERSIFIÉS:")
    print("-" * 40)
    sample_matchups = get_diverse_matchups(5)
    for i, (char1, char2, _, _) in enumerate(sample_matchups, 1):
        print(f"{i}. {char1} VS {char2}")

if __name__ == "__main__":
    print_stats()