"""
Spotify Authentication Module
Handles OAuth authentication with Spotify API
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SpotifyAuthenticator:
    """Handles Spotify API authentication"""

    # Required Spotify API scopes
    SCOPES = [
        "user-library-read",           # Read saved tracks
        "user-top-read",                # Read top artists and tracks
        "playlist-read-private",        # Read private playlists
        "playlist-read-collaborative",  # Read collaborative playlists
        "playlist-modify-public",       # Create/modify public playlists
        "playlist-modify-private",      # Create/modify private playlists
        "user-read-recently-played",    # Read recently played
    ]

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, cache_path=None):
        """
        Initialize Spotify authenticator

        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            redirect_uri: OAuth redirect URI
            cache_path: Path to cache authentication token
        """
        self.client_id = client_id or os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = redirect_uri or os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not found. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET "
                "environment variables or pass them as arguments."
            )

        # Set cache path
        if cache_path is None:
            cache_dir = Path.home() / '.cache' / 'spotifysort'
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path = str(cache_dir / 'spotify_token.json')

        self.cache_path = cache_path
        self.sp = None

    def authenticate(self):
        """
        Authenticate with Spotify API

        Returns:
            Spotipy client instance
        """
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=" ".join(self.SCOPES),
                cache_path=self.cache_path,
                open_browser=True
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Test authentication
            user = self.sp.current_user()
            logger.info(f"Successfully authenticated as {user['display_name']} ({user['id']})")

            return self.sp

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    def get_client(self):
        """
        Get authenticated Spotify client

        Returns:
            Spotipy client instance
        """
        if self.sp is None:
            self.authenticate()
        return self.sp

    def is_authenticated(self):
        """Check if user is authenticated"""
        try:
            if self.sp is None:
                return False
            self.sp.current_user()
            return True
        except:
            return False

    def get_user_info(self):
        """Get current user information"""
        if not self.is_authenticated():
            self.authenticate()

        user = self.sp.current_user()
        return {
            'id': user['id'],
            'name': user['display_name'],
            'email': user.get('email'),
            'country': user.get('country'),
            'product': user.get('product'),  # free, premium
            'followers': user['followers']['total'],
            'image': user['images'][0]['url'] if user.get('images') else None
        }
