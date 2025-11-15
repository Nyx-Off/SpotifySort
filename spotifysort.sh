#!/bin/bash
# Wrapper script pour exécuter SpotifySort avec venv

# Trouver le répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Vérifier si le venv existe
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "Exécutez d'abord : ./install.sh"
    exit 1
fi

# Activer le venv et exécuter spotifysort
source "$SCRIPT_DIR/venv/bin/activate"
spotifysort "$@"
