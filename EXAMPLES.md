# SpotifySort Usage Examples

This document provides practical examples for using SpotifySort.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Library Management](#library-management)
3. [Playlist Creation](#playlist-creation)
4. [Advanced Filtering](#advanced-filtering)
5. [Web Interface](#web-interface)
6. [Automation](#automation)

## Getting Started

### Initial Setup

```bash
# 1. Install SpotifySort
cd SpotifySort
pip install -e .

# 2. Configure your music directories (edit config.yaml)
nano config.yaml

# 3. Scan your music library
spotifysort scan ~/Music
```

### First Commands

```bash
# View statistics
spotifysort stats

# List all tracks
spotifysort list

# List first 20 tracks
spotifysort list --limit 20

# Get help
spotifysort --help
```

## Library Management

### Scanning Music

```bash
# Scan default directories (from config.yaml)
spotifysort scan

# Scan specific directories
spotifysort scan ~/Music /media/external/Music

# Scan and update existing tracks
spotifysort scan --update

# Scan without subdirectories
spotifysort scan --no-recursive ~/Music/Singles
```

### Browsing Your Collection

```bash
# Browse all artists
spotifysort browse --what artists

# Browse all albums
spotifysort browse --what albums

# Browse albums by specific artist
spotifysort browse --what albums --artist "Pink Floyd"

# Browse genres
spotifysort browse --what genres

# Browse by year
spotifysort browse --what years
```

### Searching and Filtering

```bash
# Search for a song
spotifysort list --search "bohemian rhapsody"

# Find all songs by an artist
spotifysort list --artist "The Beatles"

# Find all songs in a genre
spotifysort list --genre "Jazz"

# Find songs from a specific year
spotifysort list --year 1975

# Combine filters
spotifysort list --artist "Miles Davis" --year 1959

# Complex search
spotifysort list --genre "Rock" --year 1970 --limit 50
```

## Playlist Creation

### Basic Playlists

```bash
# Create an empty playlist
spotifysort create-playlist "My Favorites"

# Create with description
spotifysort create-playlist "Chill Vibes" --description "Relaxing music for studying"

# List all playlists
spotifysort playlists

# View playlist contents
spotifysort show-playlist 1
```

### Adding Tracks to Playlists

```bash
# First, find track IDs
spotifysort list --artist "Queen" --limit 10

# Add tracks to playlist (use track IDs from above)
spotifysort add-to-playlist 1 5 12 27 38

# Add multiple tracks at once
spotifysort add-to-playlist 2 100 101 102 103 104 105
```

### Smart Playlists

```bash
# Create a genre-based playlist
spotifysort smart-playlist "Jazz Collection" --genre "Jazz"

# Create a decade playlist
spotifysort smart-playlist "90s Hits" --year 1990

# Create an artist playlist
spotifysort smart-playlist "Beatles Complete" --artist "The Beatles"

# Create a genre + year playlist
spotifysort smart-playlist "Classic Rock 70s" --genre "Rock" --year 1970

# Create an album playlist
spotifysort smart-playlist "Dark Side Collection" --album "Dark Side of the Moon"
```

### Exporting Playlists

```bash
# Export as M3U (default)
spotifysort export-playlist 1 ~/Music/Playlists/favorites.m3u

# Export as PLS
spotifysort export-playlist 1 ~/Music/Playlists/favorites.pls --format pls

# Export with relative paths (good for portability)
spotifysort export-playlist 1 favorites.m3u --relative

# Export all your playlists
for id in $(seq 1 10); do
    spotifysort export-playlist $id ~/Music/Playlists/playlist_$id.m3u
done
```

### Importing Playlists

```bash
# Import an M3U file
spotifysort import-playlist ~/Downloads/playlist.m3u

# Import with custom name
spotifysort import-playlist ~/Downloads/playlist.m3u --name "Imported Mix"

# Import multiple playlists
for file in ~/Downloads/*.m3u; do
    spotifysort import-playlist "$file"
done
```

## Advanced Filtering

### Complex Searches

```bash
# Find all jazz from the 1960s
spotifysort list --genre "Jazz" --year 1960

# Find specific artist's albums
spotifysort browse --what albums --artist "David Bowie"

# Search across all fields
spotifysort list --search "love" --limit 100

# Find music by country (if metadata available)
spotifysort list --country "UK"
```

### Using Limits

```bash
# Get top 10 tracks
spotifysort list --limit 10

# Get 50 random tracks
spotifysort list --limit 50

# Browse first 20 artists
spotifysort browse --what artists --limit 20
```

## Web Interface

### Starting the Web Server

```bash
# Basic start (localhost only)
python -m spotifysort.web.app

# Access from other devices on network
python -m spotifysort.web.app --host 0.0.0.0

# Use custom port
python -m spotifysort.web.app --port 8080

# Enable debug mode (development)
python -m spotifysort.web.app --debug

# Use custom config file
python -m spotifysort.web.app --config /path/to/config.yaml

# Run in background
nohup python -m spotifysort.web.app > spotifysort.log 2>&1 &

# Or use the quick start script
./run_web.sh
```

### Web Interface Usage

1. **Open Browser**: Go to `http://localhost:5000`

2. **Browse Library**:
   - Use the search box to find tracks
   - Apply filters (artist, genre, year)
   - Click on tracks to see details

3. **Create Playlists**:
   - Click "New Playlist"
   - Enter name and description
   - Add tracks from library

4. **Browse Collections**:
   - Click "Browse" in navigation
   - Choose Artists, Albums, or Genres
   - Click items to filter library

5. **Export Playlists**:
   - View playlist details
   - Click "Export" button
   - Download M3U file

## Automation

### Automatic Scanning with Cron

```bash
# Edit crontab
crontab -e

# Add these lines:

# Scan music daily at 2 AM
0 2 * * * /usr/local/bin/spotifysort scan --update

# Scan every 6 hours
0 */6 * * * /usr/local/bin/spotifysort scan --update

# Scan weekly on Sunday at midnight
0 0 * * 0 /usr/local/bin/spotifysort scan --update
```

### Backup Scripts

```bash
# Create backup script: backup_spotifysort.sh
#!/bin/bash
BACKUP_DIR=~/backups/spotifysort
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d)

# Backup database
cp ~/.local/share/spotifysort/music_library.db $BACKUP_DIR/db_$DATE.db

# Backup config
cp config.yaml $BACKUP_DIR/config_$DATE.yaml

echo "Backup completed: $BACKUP_DIR"

# Make executable
chmod +x backup_spotifysort.sh

# Add to cron for weekly backups
# 0 0 * * 0 /path/to/backup_spotifysort.sh
```

### Auto-Start Web Server on Boot

```bash
# Create systemd service
sudo nano /etc/systemd/system/spotifysort.service

# Add:
[Unit]
Description=SpotifySort Web Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/SpotifySort
ExecStart=/usr/bin/python3 -m spotifysort.web.app --host 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable spotifysort
sudo systemctl start spotifysort
```

### Batch Operations

```bash
# Create multiple playlists from genres
for genre in Jazz Rock Classical Electronic; do
    spotifysort smart-playlist "$genre Mix" --genre "$genre"
done

# Export all playlists
spotifysort playlists | grep -oP '^\d+' | while read id; do
    spotifysort export-playlist $id ~/Music/Playlists/playlist_$id.m3u
done

# Scan multiple directories
for dir in ~/Music /media/music /mnt/nas/music; do
    spotifysort scan "$dir"
done
```

## Real-World Scenarios

### Scenario 1: Organizing a New Music Collection

```bash
# 1. Initial scan
spotifysort scan ~/Music

# 2. Check what you have
spotifysort stats
spotifysort browse --what genres

# 3. Create genre playlists
spotifysort smart-playlist "Rock Collection" --genre "Rock"
spotifysort smart-playlist "Jazz Collection" --genre "Jazz"

# 4. Export for media player
spotifysort export-playlist 1 ~/Music/rock.m3u
spotifysort export-playlist 2 ~/Music/jazz.m3u
```

### Scenario 2: Party Playlist

```bash
# 1. Find upbeat music
spotifysort list --genre "Dance" --limit 100

# 2. Create party playlist
spotifysort smart-playlist "Party Mix" --genre "Dance"

# 3. Add more genres
spotifysort smart-playlist "Party Mix Extended" --genre "Electronic"

# 4. Export for DJ software
spotifysort export-playlist 3 ~/party_mix.m3u
```

### Scenario 3: Discovering Old Music

```bash
# Find music from the 70s
spotifysort list --year 1970 --limit 50

# Create decade playlists
spotifysort smart-playlist "70s Classics" --year 1970
spotifysort smart-playlist "80s Hits" --year 1980
spotifysort smart-playlist "90s Gold" --year 1990
```

### Scenario 4: Artist Deep Dive

```bash
# 1. Find all songs by artist
spotifysort list --artist "Pink Floyd"

# 2. Browse their albums
spotifysort browse --what albums --artist "Pink Floyd"

# 3. Create artist collection
spotifysort smart-playlist "Pink Floyd Complete" --artist "Pink Floyd"

# 4. Export for portable player
spotifysort export-playlist 5 ~/Music/pink_floyd.m3u
```

## API Usage Examples

### Using curl

```bash
# Get statistics
curl http://localhost:5000/api/stats

# List tracks
curl http://localhost:5000/api/tracks

# Search tracks
curl "http://localhost:5000/api/search?q=love"

# Get playlists
curl http://localhost:5000/api/playlists

# Create playlist
curl -X POST http://localhost:5000/api/playlists \
  -H "Content-Type: application/json" \
  -d '{"name":"API Playlist","description":"Created via API"}'

# Export playlist
curl http://localhost:5000/api/playlists/1/export?format=m3u -o playlist.m3u
```

### Using Python

```python
import requests

# Get statistics
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
print(f"Total tracks: {stats['total_tracks']}")

# Search for tracks
response = requests.get('http://localhost:5000/api/search',
                       params={'q': 'love', 'limit': 10})
tracks = response.json()
for track in tracks:
    print(f"{track['artist']} - {track['title']}")

# Create playlist
response = requests.post('http://localhost:5000/api/playlists',
                        json={'name': 'My Playlist',
                              'description': 'Created via Python'})
playlist = response.json()
print(f"Created playlist ID: {playlist['id']}")
```

## Tips and Tricks

### Performance Tips

```bash
# Use limits for large libraries
spotifysort list --limit 100

# Filter before listing
spotifysort list --genre "Rock" --year 1970

# Use web interface for browsing large collections
python -m spotifysort.web.app
```

### Organization Tips

```bash
# Create genre-based organization
spotifysort smart-playlist "Rock" --genre "Rock"
spotifysort smart-playlist "Jazz" --genre "Jazz"
spotifysort smart-playlist "Classical" --genre "Classical"

# Create decade-based organization
for year in 1960 1970 1980 1990 2000 2010 2020; do
    spotifysort smart-playlist "${year}s Music" --year $year
done

# Create artist collections for favorite artists
for artist in "The Beatles" "Pink Floyd" "Miles Davis"; do
    spotifysort smart-playlist "$artist Collection" --artist "$artist"
done
```

### Maintenance Tips

```bash
# Regular rescans to update library
spotifysort scan --update

# Check library health
spotifysort stats

# Backup database regularly
cp ~/.local/share/spotifysort/music_library.db ~/backups/

# Export important playlists
spotifysort export-playlist 1 ~/backups/favorites.m3u
```

---

For more information, see the [README.md](README.md) and [INSTALL.md](INSTALL.md) files.
