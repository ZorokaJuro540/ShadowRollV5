"""
Script pour configurer le bot Shadow Roll pour l'hébergement multi-serveurs
Configure les permissions et génère les liens d'invitation
"""
import discord
from discord.ext import commands
import os
import asyncio

# Configuration des permissions requises pour le bot
REQUIRED_PERMISSIONS = discord.Permissions(
    # Permissions de base
    read_messages=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    use_external_emojis=True,
    add_reactions=True,
    
    # Permissions pour les commandes slash
    use_application_commands=True,
    
    # Permissions pour la gestion des messages
    manage_messages=True,
    
    # Permissions pour les threads (optionnel)
    create_public_threads=True,
    send_messages_in_threads=True,
    
    # Permissions pour les rôles (optionnel pour les admins)
    manage_roles=False,  # Non requis pour le fonctionnement de base
    
    # Permissions pour les webhooks (optionnel)
    manage_webhooks=False
)

async def generate_invite_link():
    """Générer un lien d'invitation pour le bot"""
    
    # ID du bot (à récupérer depuis l'application Discord)
    client_id = os.getenv('DISCORD_CLIENT_ID')
    
    if not client_id:
        print("❌ DISCORD_CLIENT_ID non trouvé dans les variables d'environnement")
        print("📝 Pour obtenir votre Client ID:")
        print("   1. Allez sur https://discord.com/developers/applications")
        print("   2. Sélectionnez votre application bot")
        print("   3. Copiez l'Application ID / Client ID")
        print("   4. Ajoutez DISCORD_CLIENT_ID=votre_id aux variables d'environnement")
        return None
    
    # Générer l'URL d'invitation
    invite_url = discord.utils.oauth_url(
        client_id=int(client_id),
        permissions=REQUIRED_PERMISSIONS,
        scopes=('bot', 'applications.commands')
    )
    
    return invite_url

def print_server_setup_guide():
    """Afficher le guide de configuration pour les nouveaux serveurs"""
    
    print("\n" + "="*60)
    print("🤖 GUIDE DE CONFIGURATION MULTI-SERVEURS")
    print("="*60)
    
    print("\n📋 PERMISSIONS REQUISES:")
    print("   ✓ Lire les messages")
    print("   ✓ Envoyer des messages")
    print("   ✓ Intégrer des liens")
    print("   ✓ Joindre des fichiers")
    print("   ✓ Lire l'historique des messages")
    print("   ✓ Utiliser les emojis externes")
    print("   ✓ Ajouter des réactions")
    print("   ✓ Utiliser les commandes d'application")
    print("   ✓ Gérer les messages (optionnel)")
    print("   ✓ Créer des threads publics (optionnel)")
    
    print("\n🛠️ CONFIGURATION AUTOMATIQUE:")
    print("   • Base de données SQLite (créée automatiquement)")
    print("   • Système de joueurs (auto-enregistrement)")
    print("   • Collections individuelles par serveur")
    print("   • Commandes slash synchronisées automatiquement")
    
    print("\n🎮 FONCTIONNALITÉS DISPONIBLES:")
    print("   • Système de gacha avec 161 personnages d'anime")
    print("   • Jeu 'Tu préfères' avec personnages féminins")
    print("   • Système d'équipement et d'évolution")
    print("   • Boutique et système d'échange")
    print("   • Succès et classements")
    print("   • Interface en français complète")
    
    print("\n👑 COMMANDES ADMIN (optionnelles):")
    print("   • Ajouter des administrateurs avec !addadmin @utilisateur")
    print("   • Créer des personnages personnalisés")
    print("   • Gérer les séries d'anime")
    print("   • Modifier les valeurs et raretés")
    
    print("\n🚀 DÉMARRAGE RAPIDE:")
    print("   1. Invitez le bot avec le lien généré")
    print("   2. Tapez !menu ou /menu pour commencer")
    print("   3. Utilisez !roll ou /roll pour vos premières invocations")
    print("   4. Explorez !game pour les mini-jeux")

async def check_bot_permissions():
    """Vérifier les permissions actuelles du bot"""
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Token Discord non trouvé")
        return False
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"\n✅ Bot connecté: {bot.user}")
        print(f"📊 Serveurs actuels: {len(bot.guilds)}")
        
        for guild in bot.guilds:
            print(f"   - {guild.name} ({guild.id}) - {guild.member_count} membres")
            
            # Vérifier les permissions dans ce serveur
            me = guild.get_member(bot.user.id)
            if me:
                perms = me.guild_permissions
                print(f"     Permissions: {'✓' if perms.send_messages else '✗'} Messages, "
                      f"{'✓' if perms.embed_links else '✗'} Embeds, "
                      f"{'✓' if perms.use_application_commands else '✗'} Slash Commands")
        
        await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    return True

def create_server_config_template():
    """Créer un template de configuration pour les serveurs"""
    
    config_template = """
# Configuration Shadow Roll Bot - Template Serveur

## Variables d'environnement requises:
DISCORD_TOKEN=votre_token_bot
DISCORD_CLIENT_ID=votre_client_id

## Commandes de base:
- !menu / /menu : Menu principal
- !roll / /roll : Invocation de personnages
- !profile / /profile : Profil du joueur
- !daily / /daily : Récompense quotidienne
- !game : Mini-jeux (Tu préfères, etc.)

## Configuration admin (optionnelle):
- !addadmin @utilisateur : Ajouter un admin
- !adminpanel : Panel d'administration
- !createchar : Créer un personnage personnalisé

## Fonctionnalités automatiques:
- Base de données SQLite (shadow_roll.db)
- Système de cache pour les performances
- Synchronisation automatique des commandes slash
- Sauvegarde automatique des données

## Support:
- Le bot fonctionne de manière autonome
- Aucune configuration manuelle requise
- Compatible avec tous les serveurs Discord
"""
    
    with open("SERVER_SETUP_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(config_template)
    
    print("📄 Guide de configuration créé: SERVER_SETUP_GUIDE.md")

async def main():
    """Fonction principale de configuration multi-serveurs"""
    
    print("🔧 Configuration du bot Shadow Roll pour l'hébergement multi-serveurs...")
    
    # Générer le lien d'invitation
    invite_link = await generate_invite_link()
    
    if invite_link:
        print(f"\n🔗 LIEN D'INVITATION GÉNÉRÉ:")
        print(f"   {invite_link}")
        print("\n📋 Copiez ce lien et partagez-le pour inviter le bot sur d'autres serveurs")
    
    # Vérifier les permissions actuelles
    print("\n🔍 Vérification des permissions actuelles...")
    await check_bot_permissions()
    
    # Créer le guide de configuration
    create_server_config_template()
    
    # Afficher le guide complet
    print_server_setup_guide()
    
    print("\n" + "="*60)
    print("✅ CONFIGURATION MULTI-SERVEURS TERMINÉE")
    print("="*60)
    print("\nLe bot Shadow Roll est maintenant prêt pour l'hébergement multi-serveurs!")
    print("Utilisez le lien d'invitation ci-dessus pour l'ajouter à d'autres serveurs.")

if __name__ == "__main__":
    asyncio.run(main())