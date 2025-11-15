"""
CLI interface for SpotifySort
Command-line interface for managing Spotify library and playlists
"""

import click
import os
from pathlib import Path
from tabulate import tabulate
from colorama import Fore, Style, init
from dotenv import load_dotenv

from .spotify_auth import SpotifyAuthenticator
from .library_analyzer import SpotifyLibraryAnalyzer
from .playlist_manager import SpotifyPlaylistManager

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()


def get_authenticated_client():
    """Get authenticated Spotify client"""
    try:
        auth = SpotifyAuthenticator()
        sp = auth.authenticate()
        return sp
    except ValueError as e:
        click.echo(f"{Fore.RED}Error: {e}")
        click.echo(f"{Fore.YELLOW}Please set up your Spotify API credentials:")
        click.echo("1. Go to https://developer.spotify.com/dashboard")
        click.echo("2. Create an application")
        click.echo("3. Copy Client ID and Client Secret")
        click.echo("4. Create a .env file with:")
        click.echo("   SPOTIFY_CLIENT_ID=your_client_id")
        click.echo("   SPOTIFY_CLIENT_SECRET=your_client_secret")
        click.echo("   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback")
        exit(1)


@click.group()
@click.version_option(version='2.0.0')
def main():
    """
    SpotifySort - Organize your Spotify library automatically

    A tool to analyze and sort your Spotify library into organized playlists.
    """
    pass


@main.command()
def auth():
    """Authenticate with Spotify"""
    click.echo(f"{Fore.CYAN}Authenticating with Spotify...")

    try:
        sp = get_authenticated_client()
        auth = SpotifyAuthenticator()
        user_info = auth.get_user_info()

        click.echo(f"\n{Fore.GREEN}✓ Successfully authenticated!")
        click.echo(f"\n{Fore.CYAN}User Information:")
        click.echo(f"  Name: {user_info['name']}")
        click.echo(f"  ID: {user_info['id']}")
        click.echo(f"  Account: {user_info['product']}")
        if user_info.get('email'):
            click.echo(f"  Email: {user_info['email']}")
        click.echo(f"  Followers: {user_info['followers']:,}")

    except Exception as e:
        click.echo(f"{Fore.RED}Authentication failed: {e}")


@main.command()
def info():
    """Show your Spotify account information"""
    sp = get_authenticated_client()
    auth = SpotifyAuthenticator(client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                                 client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'))
    auth.sp = sp

    user_info = auth.get_user_info()

    click.echo(f"\n{Fore.CYAN}{'='*50}")
    click.echo(f"{Fore.CYAN}Spotify Account Information")
    click.echo(f"{Fore.CYAN}{'='*50}\n")

    click.echo(f"{Fore.GREEN}Name:      {Fore.WHITE}{user_info['name']}")
    click.echo(f"{Fore.GREEN}User ID:   {Fore.WHITE}{user_info['id']}")
    click.echo(f"{Fore.GREEN}Account:   {Fore.WHITE}{user_info['product'].upper()}")
    click.echo(f"{Fore.GREEN}Country:   {Fore.WHITE}{user_info.get('country', 'N/A')}")
    click.echo(f"{Fore.GREEN}Followers: {Fore.WHITE}{user_info['followers']:,}\n")


@main.command()
@click.option('--limit', type=int, help='Limit number of tracks to fetch')
def stats(limit):
    """Show statistics about your Spotify library"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)

    click.echo(f"{Fore.CYAN}Analyzing your Spotify library...")

    tracks = analyzer.get_saved_tracks(limit=limit)
    stats = analyzer.get_library_statistics(tracks)

    click.echo(f"\n{Fore.CYAN}{'='*50}")
    click.echo(f"{Fore.CYAN}Library Statistics")
    click.echo(f"{Fore.CYAN}{'='*50}\n")

    click.echo(f"{Fore.GREEN}Total Tracks:  {Fore.WHITE}{stats['total_tracks']:,}")
    click.echo(f"{Fore.GREEN}Artists:       {Fore.WHITE}{stats['total_artists']:,}")
    click.echo(f"{Fore.GREEN}Albums:        {Fore.WHITE}{stats['total_albums']:,}")
    click.echo(f"{Fore.GREEN}Genres:        {Fore.WHITE}{stats['total_genres']:,}")
    click.echo(f"{Fore.GREEN}Total Duration:{Fore.WHITE} {stats['total_duration_hours']:.1f} hours\n")

    if stats['genres']:
        click.echo(f"{Fore.YELLOW}Top Genres:")
        for i, genre in enumerate(stats['genres'][:10], 1):
            click.echo(f"  {i}. {genre}")


@main.command()
@click.option('--limit', type=int, default=50, help='Number of tracks to show')
def tracks(limit):
    """List your saved tracks"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)

    click.echo(f"{Fore.CYAN}Fetching your saved tracks...")
    tracks = analyzer.get_saved_tracks(limit=limit)

    if not tracks:
        click.echo(f"{Fore.YELLOW}No saved tracks found")
        return

    table_data = []
    for i, track in enumerate(tracks, 1):
        artists = ", ".join([a['name'] for a in track['artists']])
        duration = f"{track['duration_ms'] // 60000}:{(track['duration_ms'] // 1000) % 60:02d}"

        table_data.append([
            i,
            track['name'][:40],
            artists[:30],
            track['album']['name'][:30],
            track['release_year'] or 'N/A',
            duration
        ])

    headers = ['#', 'Title', 'Artist', 'Album', 'Year', 'Duration']
    click.echo(f"\n{tabulate(table_data, headers=headers, tablefmt='grid')}")
    click.echo(f"\n{Fore.CYAN}Showing {len(tracks)} tracks")


@main.command()
def playlists():
    """List your Spotify playlists"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)

    click.echo(f"{Fore.CYAN}Fetching your playlists...")
    playlists = analyzer.get_user_playlists()

    if not playlists:
        click.echo(f"{Fore.YELLOW}No playlists found")
        return

    table_data = []
    for i, playlist in enumerate(playlists, 1):
        table_data.append([
            i,
            playlist['name'][:40],
            playlist['owner'][:20],
            playlist['tracks_total'],
            'Public' if playlist['public'] else 'Private'
        ])

    headers = ['#', 'Name', 'Owner', 'Tracks', 'Visibility']
    click.echo(f"\n{tabulate(table_data, headers=headers, tablefmt='grid')}")
    click.echo(f"\n{Fore.CYAN}Total: {len(playlists)} playlists")


@main.command()
@click.option('--time', type=click.Choice(['short', 'medium', 'long']),
              default='medium', help='Time range (short=4 weeks, medium=6 months, long=years)')
@click.option('--limit', type=int, default=20, help='Number of artists to show')
def top_artists(time, limit):
    """Show your top artists"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)

    time_map = {'short': 'short_term', 'medium': 'medium_term', 'long': 'long_term'}
    time_label = {'short': '4 weeks', 'medium': '6 months', 'long': 'all time'}

    click.echo(f"{Fore.CYAN}Fetching your top artists ({time_label[time]})...")
    artists = analyzer.get_top_artists(time_range=time_map[time], limit=limit)

    table_data = []
    for i, artist in enumerate(artists, 1):
        genres = ", ".join(artist['genres'][:3]) if artist['genres'] else 'N/A'

        table_data.append([
            i,
            artist['name'][:40],
            genres[:40],
            artist['popularity'],
            f"{artist['followers']:,}"
        ])

    headers = ['#', 'Artist', 'Genres', 'Popularity', 'Followers']
    click.echo(f"\n{tabulate(table_data, headers=headers, tablefmt='grid')}")


@main.command()
@click.option('--prefix', default='SpotifySort', help='Prefix for playlist names')
@click.option('--public/--private', default=False, help='Make playlists public or private')
@click.option('--limit', type=int, help='Limit number of tracks to analyze')
def sort_by_genre(prefix, public, limit):
    """Create playlists sorted by genre"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)
    manager = SpotifyPlaylistManager(sp)

    click.echo(f"{Fore.CYAN}Analyzing your library by genre...")
    tracks = analyzer.get_saved_tracks(limit=limit)
    genre_map = analyzer.analyze_library_by_genre(tracks)

    click.echo(f"\n{Fore.GREEN}Found {len(genre_map)} genres")

    # Show preview
    click.echo(f"\n{Fore.YELLOW}Genres to create:")
    for genre, tracks in sorted(genre_map.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        click.echo(f"  • {genre}: {len(tracks)} tracks")

    if len(genre_map) > 10:
        click.echo(f"  ... and {len(genre_map) - 10} more")

    if not click.confirm(f"\n{Fore.CYAN}Create {len(genre_map)} playlists on Spotify?"):
        click.echo(f"{Fore.YELLOW}Cancelled")
        return

    click.echo(f"\n{Fore.CYAN}Creating playlists...")
    created = manager.create_genre_playlists(genre_map, prefix=prefix, public=public)

    click.echo(f"\n{Fore.GREEN}✓ Successfully created {len(created)} playlists!")


@main.command()
@click.option('--prefix', default='SpotifySort', help='Prefix for playlist names')
@click.option('--public/--private', default=False, help='Make playlists public or private')
@click.option('--limit', type=int, help='Limit number of tracks to analyze')
def sort_by_mood(prefix, public, limit):
    """Create playlists sorted by mood (Happy, Sad, Energetic, etc.)"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)
    manager = SpotifyPlaylistManager(sp)

    click.echo(f"{Fore.CYAN}Analyzing your library by mood...")
    click.echo(f"{Fore.YELLOW}This may take a while as we analyze audio features...")

    tracks = analyzer.get_saved_tracks(limit=limit)
    mood_map = analyzer.analyze_library_by_mood(tracks)

    # Show preview
    click.echo(f"\n{Fore.YELLOW}Moods found:")
    for mood, mood_tracks in mood_map.items():
        if mood_tracks:
            click.echo(f"  • {mood}: {len(mood_tracks)} tracks")

    if not click.confirm(f"\n{Fore.CYAN}Create mood playlists on Spotify?"):
        click.echo(f"{Fore.YELLOW}Cancelled")
        return

    click.echo(f"\n{Fore.CYAN}Creating playlists...")
    created = manager.create_mood_playlists(mood_map, prefix=prefix, public=public)

    click.echo(f"\n{Fore.GREEN}✓ Successfully created {len(created)} mood playlists!")


@main.command()
@click.option('--prefix', default='SpotifySort', help='Prefix for playlist names')
@click.option('--public/--private', default=False, help='Make playlists public or private')
@click.option('--limit', type=int, help='Limit number of tracks to analyze')
def sort_by_decade(prefix, public, limit):
    """Create playlists sorted by decade (70s, 80s, 90s, etc.)"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)
    manager = SpotifyPlaylistManager(sp)

    click.echo(f"{Fore.CYAN}Analyzing your library by decade...")
    tracks = analyzer.get_saved_tracks(limit=limit)

    click.echo(f"\n{Fore.CYAN}Creating decade playlists...")
    created = manager.create_decade_playlists(tracks, prefix=prefix, public=public)

    click.echo(f"\n{Fore.GREEN}✓ Successfully created {len(created)} decade playlists!")

    for decade, playlist_id in sorted(created.items()):
        click.echo(f"  • {decade}s: https://open.spotify.com/playlist/{playlist_id}")


@main.command()
@click.option('--prefix', default='SpotifySort', help='Prefix for playlist names')
@click.option('--public/--private', default=False, help='Make playlists public or private')
@click.option('--min-tracks', type=int, default=5, help='Minimum tracks per artist')
@click.option('--limit', type=int, help='Limit number of tracks to analyze')
def sort_by_artist(prefix, public, min_tracks, limit):
    """Create playlists for each artist"""
    sp = get_authenticated_client()
    analyzer = SpotifyLibraryAnalyzer(sp)
    manager = SpotifyPlaylistManager(sp)

    click.echo(f"{Fore.CYAN}Analyzing your library by artist...")
    tracks = analyzer.get_saved_tracks(limit=limit)
    artist_map = analyzer.analyze_library_by_artist(tracks)

    # Filter by minimum tracks
    filtered = {k: v for k, v in artist_map.items() if len(v) >= min_tracks}

    click.echo(f"\n{Fore.GREEN}Found {len(filtered)} artists with {min_tracks}+ tracks")

    # Show preview
    click.echo(f"\n{Fore.YELLOW}Top artists:")
    for artist, tracks in sorted(filtered.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        click.echo(f"  • {artist}: {len(tracks)} tracks")

    if not click.confirm(f"\n{Fore.CYAN}Create {len(filtered)} artist playlists?"):
        click.echo(f"{Fore.YELLOW}Cancelled")
        return

    click.echo(f"\n{Fore.CYAN}Creating playlists...")
    created = manager.create_artist_playlists(filtered, prefix=prefix, public=public, min_tracks=min_tracks)

    click.echo(f"\n{Fore.GREEN}✓ Successfully created {len(created)} artist playlists!")


@main.command()
def setup():
    """Interactive setup wizard for Spotify API credentials"""
    click.echo(f"\n{Fore.CYAN}{'='*60}")
    click.echo(f"{Fore.CYAN}SpotifySort Setup Wizard")
    click.echo(f"{Fore.CYAN}{'='*60}\n")

    click.echo(f"{Fore.YELLOW}To use SpotifySort, you need Spotify API credentials.")
    click.echo("Follow these steps:\n")

    click.echo(f"{Fore.GREEN}1. Go to https://developer.spotify.com/dashboard")
    click.echo(f"{Fore.GREEN}2. Log in with your Spotify account")
    click.echo(f"{Fore.GREEN}3. Click 'Create an App'")
    click.echo(f"{Fore.GREEN}4. Fill in the app name and description")
    click.echo(f"{Fore.GREEN}5. Add redirect URI: http://localhost:8888/callback")
    click.echo(f"{Fore.GREEN}6. Copy your Client ID and Client Secret\n")

    if not click.confirm(f"{Fore.CYAN}Have you created your Spotify app?"):
        click.echo(f"\n{Fore.YELLOW}Please complete the setup first, then run this command again.")
        return

    client_id = click.prompt(f"\n{Fore.CYAN}Enter your Client ID", type=str)
    client_secret = click.prompt(f"{Fore.CYAN}Enter your Client Secret", type=str, hide_input=True)
    redirect_uri = click.prompt(f"{Fore.CYAN}Enter Redirect URI",
                                type=str, default="http://localhost:8888/callback")

    # Create .env file
    env_path = Path('.env')

    env_content = f"""# Spotify API Credentials
SPOTIFY_CLIENT_ID={client_id}
SPOTIFY_CLIENT_SECRET={client_secret}
SPOTIFY_REDIRECT_URI={redirect_uri}

# Flask Configuration
FLASK_SECRET_KEY={os.urandom(24).hex()}
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
"""

    with open(env_path, 'w') as f:
        f.write(env_content)

    click.echo(f"\n{Fore.GREEN}✓ Configuration saved to .env file")
    click.echo(f"\n{Fore.CYAN}Testing authentication...")

    try:
        auth = SpotifyAuthenticator(client_id=client_id,
                                    client_secret=client_secret,
                                    redirect_uri=redirect_uri)
        sp = auth.authenticate()
        user = auth.get_user_info()

        click.echo(f"\n{Fore.GREEN}✓ Successfully authenticated as {user['name']}!")
        click.echo(f"\n{Fore.CYAN}Setup complete! You can now use SpotifySort.")
        click.echo(f"\nTry: {Fore.WHITE}spotifysort stats")

    except Exception as e:
        click.echo(f"\n{Fore.RED}✗ Authentication failed: {e}")
        click.echo(f"{Fore.YELLOW}Please check your credentials and try again.")


if __name__ == '__main__':
    main()
