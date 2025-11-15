# Installation Guide - SpotifySort

## Quick Installation (Recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Nyx-Off/SpotifySort.git
cd SpotifySort
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install SpotifySort
```bash
pip install -e .
```

### Step 4: Configure (Optional)
```bash
# Edit config.yaml to add your music directories
nano config.yaml
```

### Step 5: Scan Your Music
```bash
spotifysort scan ~/Music
```

### Step 6: Start Using!

**CLI Usage:**
```bash
spotifysort list
spotifysort stats
```

**Web Interface:**
```bash
python -m spotifysort.web.app
# Then open http://localhost:5000 in your browser
```

## Detailed Installation

### System Requirements

- **Operating System**: Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- **Python**: 3.10 or higher
- **Disk Space**: ~50MB for application + space for database
- **RAM**: Minimal (50MB+ depending on library size)

### Installing Python 3.10+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

### Installing SpotifySort

#### Method 1: Using pip (Recommended)
```bash
# Clone repository
git clone https://github.com/Nyx-Off/SpotifySort.git
cd SpotifySort

# Install in development mode
pip install -e .
```

#### Method 2: Using Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install SpotifySort
pip install -e .
```

#### Method 3: Manual Installation
```bash
# Install dependencies manually
pip install mutagen Flask Flask-CORS click PyYAML tabulate colorama python-dotenv tqdm

# No need to install SpotifySort itself, run from source
python -m spotifysort.cli --help
python -m spotifysort.web.app
```

### Configuration

Create or edit `config.yaml`:

```yaml
# Database location
database:
  path: "~/.local/share/spotifysort/music_library.db"

# Your music directories
library:
  paths:
    - "~/Music"
    - "/media/external/Music"

# Supported audio formats
  supported_formats:
    - ".mp3"
    - ".flac"
    - ".ogg"
    - ".m4a"
    - ".wav"
    - ".opus"
    - ".wma"

# Web server settings
web:
  host: "127.0.0.1"
  port: 5000
  debug: false

# Scanner options
scanner:
  skip_hidden: true
  show_progress: true
  auto_update: true

# Playlist settings
playlists:
  export_format: "m3u"
  export_path: "~/Music/Playlists"
```

### First Run

1. **Scan your music library:**
```bash
spotifysort scan
```

This will:
- Search for audio files in configured directories
- Extract metadata (artist, album, genre, etc.)
- Add tracks to the database

2. **View your library:**
```bash
spotifysort list
spotifysort stats
```

3. **Start web interface:**
```bash
python -m spotifysort.web.app
```

Open `http://localhost:5000` in your browser.

## Post-Installation

### Making CLI Available System-Wide

If installed with pip, `spotifysort` should already be in your PATH.

If not, add to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$PATH:$HOME/.local/bin"
```

### Creating Desktop Shortcut (Optional)

Create `~/.local/share/applications/spotifysort.desktop`:

```desktop
[Desktop Entry]
Type=Application
Name=SpotifySort
Comment=Music Library Manager
Exec=python3 -m spotifysort.web.app
Icon=audio-player
Terminal=false
Categories=Audio;AudioVideo;Player;
```

### Running as System Service (Optional)

Create `/etc/systemd/system/spotifysort.service`:

```ini
[Unit]
Description=SpotifySort Web Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/SpotifySort
ExecStart=/usr/bin/python3 -m spotifysort.web.app --host 0.0.0.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable spotifysort
sudo systemctl start spotifysort
```

## Troubleshooting Installation

### "Command not found: spotifysort"

**Solution:**
```bash
# Check if installed
pip list | grep spotifysort

# Add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Or run directly
python -m spotifysort.cli --help
```

### "Module not found: mutagen/flask/etc"

**Solution:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Or install individually
pip install mutagen Flask click
```

### Permission Errors

**Solution:**
```bash
# Don't use sudo with pip (bad practice)
# Instead, use --user flag
pip install --user -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Creation Fails

**Solution:**
```bash
# Create database directory manually
mkdir -p ~/.local/share/spotifysort

# Check permissions
chmod 755 ~/.local/share/spotifysort
```

## Updating SpotifySort

```bash
cd SpotifySort
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstallation

```bash
# Uninstall package
pip uninstall spotifysort

# Remove database (optional)
rm -rf ~/.local/share/spotifysort

# Remove configuration (optional)
rm -rf ~/.config/spotifysort
```

## Getting Help

- Check README.md for usage examples
- Run `spotifysort --help` for CLI help
- Visit GitHub issues: https://github.com/Nyx-Off/SpotifySort/issues
