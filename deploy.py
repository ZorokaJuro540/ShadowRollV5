"""
Script de déploiement automatique pour Shadow Roll Bot
Prépare le bot pour l'hébergement sur différentes plateformes
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_deployment_package():
    """Créer un package de déploiement complet"""
    
    print("📦 Création du package de déploiement...")
    
    # Créer le dossier de déploiement
    deploy_dir = Path("deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Fichiers essentiels à copier
    essential_files = [
        "main.py",
        "Procfile",
        "runtime.txt",
        "app.json",
        "railway.toml",
        "render.yaml",
        "fly.toml",
        "Dockerfile",
        "docker-compose.yml",
        "setup_database.py",
        ".env.example",
        "DEPLOYMENT_GUIDE.md"
    ]
    
    # Dossiers essentiels
    essential_dirs = [
        "core",
        "modules",
        "assets",
        "docs"
    ]
    
    # Copier les fichiers
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, deploy_dir / file)
            print(f"✅ Copié: {file}")
    
    # Copier les dossiers
    for dir_name in essential_dirs:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, deploy_dir / dir_name)
            print(f"✅ Copié: {dir_name}/")
    
    # Créer le fichier requirements.txt depuis pyproject.toml
    create_requirements_txt(deploy_dir)
    
    # Créer le fichier .gitignore
    create_gitignore(deploy_dir)
    
    # Créer le README pour le déploiement
    create_deployment_readme(deploy_dir)
    
    print(f"📦 Package de déploiement créé dans: {deploy_dir}")
    return deploy_dir

def create_requirements_txt(deploy_dir):
    """Créer requirements.txt depuis pyproject.toml"""
    
    requirements_content = """discord.py==2.5.2
aiosqlite==0.21.0
aiohttp>=3.7.4
Pillow>=8.0.0
python-dotenv>=0.19.0
requests>=2.25.0
beautifulsoup4>=4.9.0
pytz>=2021.1
"""
    
    with open(deploy_dir / "requirements.txt", "w") as f:
        f.write(requirements_content)
    
    print("✅ requirements.txt créé")

def create_gitignore(deploy_dir):
    """Créer .gitignore pour le déploiement"""
    
    gitignore_content = """# Environnement Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# Bot spécifique
*.db
*.db-shm
*.db-wal
logs/
backups/
.replit
replit.nix
"""
    
    with open(deploy_dir / ".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore créé")

def create_deployment_readme(deploy_dir):
    """Créer README spécifique au déploiement"""
    
    readme_content = """# Shadow Roll Bot - Déploiement

## Déploiement rapide

### Variables d'environnement requises
```
DISCORD_TOKEN=votre_token_discord
DISCORD_CLIENT_ID=votre_client_id_discord
```

### Plateformes supportées

#### Heroku
```bash
heroku create votre-app-name
heroku config:set DISCORD_TOKEN=votre_token
heroku config:set DISCORD_CLIENT_ID=votre_client_id
git push heroku main
```

#### Railway
1. Connectez votre repo GitHub
2. Configurez les variables d'environnement
3. Déployez automatiquement

#### Render
1. Connectez votre repo GitHub
2. Utilisez le fichier render.yaml
3. Configurez les variables d'environnement

#### Fly.io
```bash
fly launch
fly secrets set DISCORD_TOKEN=votre_token
fly secrets set DISCORD_CLIENT_ID=votre_client_id
fly deploy
```

#### Docker
```bash
docker build -t shadow-roll-bot .
docker run -e DISCORD_TOKEN=votre_token -e DISCORD_CLIENT_ID=votre_client_id shadow-roll-bot
```

## Fonctionnalités
- 161 personnages d'anime
- Système de gacha complet
- Jeu "Tu préfères" avec 47 personnages féminins
- Interface française
- Multi-serveurs

## Support
Consultez DEPLOYMENT_GUIDE.md pour plus de détails.
"""
    
    with open(deploy_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ README.md créé")

def generate_invite_link():
    """Générer le lien d'invitation du bot"""
    
    print("\n🔗 Génération du lien d'invitation...")
    
    permissions = 414464724032  # Permissions calculées
    
    print("Pour générer votre lien d'invitation:")
    print(f"https://discord.com/api/oauth2/authorize?client_id=VOTRE_CLIENT_ID&permissions={permissions}&scope=bot%20applications.commands")
    print("\nRemplacez VOTRE_CLIENT_ID par l'ID de votre application Discord")

def main():
    """Fonction principale de déploiement"""
    
    print("🚀 Script de déploiement Shadow Roll Bot")
    print("=" * 50)
    
    # Créer le package de déploiement
    deploy_dir = create_deployment_package()
    
    # Générer le lien d'invitation
    generate_invite_link()
    
    print("\n" + "=" * 50)
    print("✅ DÉPLOIEMENT PRÉPARÉ AVEC SUCCÈS!")
    print("=" * 50)
    print(f"📁 Package créé dans: {deploy_dir}")
    print("📋 Prochaines étapes:")
    print("  1. Copiez le contenu du dossier 'deploy' vers votre plateforme")
    print("  2. Configurez les variables d'environnement DISCORD_TOKEN et DISCORD_CLIENT_ID")
    print("  3. Déployez selon la plateforme choisie")
    print("  4. Consultez DEPLOYMENT_GUIDE.md pour plus de détails")
    print("\n🌟 Le bot Shadow Roll est prêt pour l'hébergement!")

if __name__ == "__main__":
    main()