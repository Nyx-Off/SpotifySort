#!/bin/bash
# Quick start script for SpotifySort Web Interface

# Trouver le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "╔═══════════════════════════════════════════════╗"
echo "║        SpotifySort Web Server                 ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Vérifier si le venv existe
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Exécutez d'abord : ./install.sh"
    exit 1
fi

# Activer le venv
source "$SCRIPT_DIR/venv/bin/activate"

# Check if dependencies are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "Starting web server..."
echo "Access the interface at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python3 -m spotifysort.web.app "$@"
