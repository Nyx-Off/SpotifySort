#!/bin/bash
# Installation automatique de SpotifySort avec environnement virtuel

echo "╔═══════════════════════════════════════════════╗"
echo "║     SpotifySort - Installation Script        ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "✓ Python 3 trouvé : $(python3 --version)"
echo ""

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "✓ Environnement virtuel créé"
else
    echo "✓ Environnement virtuel existant trouvé"
fi

# Activer l'environnement virtuel
echo ""
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mettre à jour pip
echo ""
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip -q

# Installer les dépendances
echo ""
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Installer SpotifySort
echo ""
echo "🎵 Installation de SpotifySort..."
pip install -e .

# Exécuter les tests
echo ""
echo "🧪 Exécution des tests..."
python test_basic.py

# Résumé
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║         Installation terminée !               ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "Pour utiliser SpotifySort, activez d'abord l'environnement virtuel :"
echo ""
echo "  source venv/bin/activate"
echo ""
echo "Ou utilisez les scripts fournis :"
echo ""
echo "  ./spotifysort.sh scan ~/Music      # Scanner votre musique"
echo "  ./spotifysort.sh list              # Lister les morceaux"
echo "  ./spotifysort.sh stats             # Voir les statistiques"
echo "  ./run_web.sh                       # Lancer l'interface web"
echo ""
