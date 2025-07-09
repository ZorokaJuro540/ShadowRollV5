FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY pyproject.toml uv.lock ./

# Installer UV pour la gestion des dépendances
RUN pip install uv

# Installer les dépendances Python
RUN uv sync --frozen

# Copier le code source
COPY . .

# Créer le répertoire de données
RUN mkdir -p data

# Initialiser la base de données
RUN python setup_database.py

# Exposer le port (pas nécessaire pour un bot Discord mais utile pour les health checks)
EXPOSE 8080

# Commande par défaut
CMD ["python", "main.py"]