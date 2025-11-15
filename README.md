# 🎵 SpotifySort - Organize Your Spotify Library

Automatically sort and organize your Spotify library into smart playlists by genre, mood, decade, artist, and more!

## ✨ Features

### 🎼 Automatic Library Analysis
- **Genre Detection**: Automatically detect genres using Spotify's artist data
- **Mood Analysis**: AI-powered mood detection using audio features (Happy, Sad, Energetic, Calm, Party, Chill)
- **Decade Sorting**: Organize music by era (70s, 80s, 90s, 2000s, etc.)
- **Artist Collections**: Create playlists for your favorite artists
- **Statistics**: Comprehensive library stats (tracks, artists, albums, genres, listening time)

### 🎧 Smart Playlist Creation
- **One-Click Organization**: Create hundreds of organized playlists in minutes
- **Direct to Spotify**: Playlists are created directly on your Spotify account
- **Customizable**: Choose playlist names, public/private visibility
- **Audio Feature Analysis**: Uses Spotify's advanced audio analysis (danceability, energy, valence, tempo)

### 🖥️ Dual Interface
- **CLI**: Powerful command-line interface for automation
- **Web UI**: Beautiful web interface with OAuth authentication
- **RESTful API**: Complete API for custom integrations

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Spotify account (Free or Premium)
- Spotify Developer App credentials

### Step 1: Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "**Create an App**"
4. Fill in:
   - **App name**: SpotifySort
   - **App description**: Music library organizer
5. Once created, click "**Settings**"
6. Add **Redirect URI**: `http://localhost:8888/callback`
7. Save your **Client ID** and **Client Secret**

### Step 2: Install SpotifySort

```bash
# Clone the repository
git clone https://github.com/Nyx-Off/SpotifySort.git
cd SpotifySort

# Run installation script
chmod +x install.sh
./install.sh
```

### Step 3: Configure Credentials

Run the interactive setup:
```bash
source venv/bin/activate
spotifysort setup
```

Or manually create `.env` file:
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

### Step 4: Start Using!

**CLI:**
```bash
spotifysort auth              # Authenticate with Spotify
spotifysort stats             # View library statistics
spotifysort sort-by-genre     # Create genre playlists
```

**Web Interface:**
```bash
python -m spotifysort.web.app
# Open http://localhost:5000 in your browser
```

## 📖 Usage Guide

### Command-Line Interface

#### Authentication
```bash
# Authenticate with Spotify (first time)
spotifysort auth

# View account info
spotifysort info
```

#### Library Statistics
```bash
# Show library statistics
spotifysort stats

# Show your saved tracks
spotifysort tracks --limit 50

# Show your playlists
spotifysort playlists

# Show top artists
spotifysort top-artists --time short  # last 4 weeks
spotifysort top-artists --time medium # last 6 months
spotifysort top-artists --time long   # all time
```

#### Create Organized Playlists

**Sort by Genre:**
```bash
spotifysort sort-by-genre
# Creates playlists: SpotifySort - Rock, SpotifySort - Pop, etc.

# Custom prefix and make public
spotifysort sort-by-genre --prefix "MyMusic" --public
```

**Sort by Mood:**
```bash
spotifysort sort-by-mood
# Creates: SpotifySort - Happy, SpotifySort - Energetic, etc.
```

**Sort by Decade:**
```bash
spotifysort sort-by-decade
# Creates: SpotifySort - 70s, SpotifySort - 80s, etc.
```

**Sort by Artist:**
```bash
spotifysort sort-by-artist --min-tracks 10
# Creates playlists for artists with 10+ tracks
```

### Web Interface

1. **Start the server:**
   ```bash
   python -m spotifysort.web.app
   ```

2. **Open browser:** http://localhost:5000

3. **Login with Spotify**

4. **Choose sorting method:**
   - Click on a card (Genre, Mood, Decade, Artist)
   - Click "Analyze" to preview
   - Click "Create Playlists" to organize your library

5. **View results in Spotify!**

## 🎯 Sorting Methods Explained

### By Genre
Uses Spotify's genre tags from artists. Creates playlists like:
- Rock, Pop, Hip-Hop, Electronic
- Jazz, Classical, Country, R&B
- Metal, Indie, Folk, etc.

### By Mood
Uses Spotify's audio features API to analyze:
- **Happy**: High valence + high energy
- **Sad**: Low valence + low energy
- **Energetic**: High energy + fast tempo
- **Calm**: Low energy + slow tempo
- **Party**: High danceability + high energy
- **Chill**: High acousticness + low energy

### By Decade
Groups tracks by release year:
- 1970s, 1980s, 1990s, 2000s, 2010s, 2020s

### By Artist
Creates individual playlists for each artist (customizable minimum track count)

## 🛠️ Advanced Configuration

### Environment Variables

Create a `.env` file:

```bash
# Spotify API (Required)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback

# Flask Web Server (Optional)
FLASK_SECRET_KEY=random_secret_key
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
```

### CLI Options

Most commands support these options:
- `--limit`: Limit number of tracks to analyze (for testing)
- `--prefix`: Custom prefix for playlist names
- `--public/--private`: Playlist visibility
- `--min-tracks`: Minimum tracks per artist (for artist sorting)

Example:
```bash
spotifysort sort-by-genre --prefix "MyMusic" --public --limit 100
```

## 🌐 Web API

The web server provides a REST API:

### Endpoints

**Authentication:**
- `GET /login` - OAuth login
- `GET /logout` - Logout

**Data:**
- `GET /api/user` - User information
- `GET /api/stats` - Library statistics
- `GET /api/tracks` - Saved tracks
- `GET /api/playlists` - User playlists
- `GET /api/top-artists` - Top artists

**Analysis:**
- `POST /api/analyze/genre` - Analyze by genre
- `POST /api/analyze/mood` - Analyze by mood

**Playlist Creation:**
- `POST /api/create-playlists/genre` - Create genre playlists
- `POST /api/create-playlists/mood` - Create mood playlists
- `POST /api/create-playlists/decade` - Create decade playlists
- `POST /api/create-playlists/artist` - Create artist playlists

## 📊 Examples

### Organize Your Entire Library by Genre
```bash
spotifysort sort-by-genre
```
Result: Playlists for every genre in your library (Rock, Pop, Jazz, etc.)

### Create Mood Playlists for Workouts
```bash
spotifysort sort-by-mood --prefix "Workout"
```
Result: Workout - Energetic, Workout - Party playlists

### Build Decade Collections
```bash
spotifysort sort-by-decade --prefix "Decades"
```
Result: Decades - 80s, Decades - 90s, etc.

### Artist Deep-Dive
```bash
spotifysort sort-by-artist --min-tracks 5 --prefix "Artists"
```
Result: Individual playlists for artists with 5+ tracks

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details

## 🐛 Troubleshooting

### "Authentication failed"
- Check your Spotify API credentials in `.env`
- Verify redirect URI matches exactly: `http://localhost:8888/callback`
- Make sure your Spotify Developer app is not in development mode restrictions

### "No tracks found"
- Make sure you have saved tracks in your Spotify library
- Try increasing `--limit` parameter
- Check if you're authenticated: `spotifysort auth`

### Web interface not loading
- Ensure port 5000 is not in use
- Try: `python -m spotifysort.web.app --port 8080`
- Check firewall settings

### Rate limiting
- Spotify API has rate limits
- If you hit limits, wait a few minutes
- For large libraries (1000+ tracks), sorting may take several minutes

## 💡 Tips

1. **Start Small**: Test with `--limit 100` before processing entire library
2. **Genre Cleanup**: Spotify genres can be very specific - you might get many playlists
3. **Mood Analysis**: Takes longer as it analyzes audio features for each track
4. **Public Playlists**: Use `--public` to share your organized playlists
5. **Batch Operations**: You can run multiple sort commands - playlists will be created separately

## 🔗 Links

- [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- [Spotify API Documentation](https://developer.spotify.com/documentation/web-api)
- [GitHub Issues](https://github.com/Nyx-Off/SpotifySort/issues)

---

**Made with ❤️ for Spotify users who love organized music**
