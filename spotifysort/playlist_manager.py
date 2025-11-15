"""
Spotify Playlist Manager
Creates and manages playlists on Spotify based on sorting criteria
"""

import logging
from typing import List, Dict
from tqdm import tqdm

logger = logging.getLogger(__name__)


class SpotifyPlaylistManager:
    """Manages playlist creation and organization on Spotify"""

    def __init__(self, spotify_client):
        self.sp = spotify_client
        self.user_id = self.sp.current_user()['id']

    def create_playlist(self, name, description="", public=False):
        """
        Create a new playlist on Spotify

        Args:
            name: Playlist name
            description: Playlist description
            public: Whether playlist is public

        Returns:
            Playlist ID
        """
        try:
            playlist = self.sp.user_playlist_create(
                user=self.user_id,
                name=name,
                public=public,
                description=description
            )

            logger.info(f"Created playlist '{name}' (ID: {playlist['id']})")
            return playlist['id']

        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise

    def add_tracks_to_playlist(self, playlist_id, track_uris):
        """
        Add tracks to a playlist

        Args:
            playlist_id: Spotify playlist ID
            track_uris: List of track URIs

        Returns:
            True if successful
        """
        if not track_uris:
            logger.warning("No tracks to add")
            return False

        # Spotify API allows max 100 tracks per request
        batch_size = 100

        try:
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                self.sp.playlist_add_items(playlist_id, batch)

            logger.info(f"Added {len(track_uris)} tracks to playlist {playlist_id}")
            return True

        except Exception as e:
            logger.error(f"Error adding tracks: {e}")
            return False

    def create_genre_playlists(self, genre_map, prefix="SpotifySort", public=False):
        """
        Create separate playlists for each genre

        Args:
            genre_map: Dictionary {genre: [tracks]}
            prefix: Prefix for playlist names
            public: Whether playlists should be public

        Returns:
            Dictionary {genre: playlist_id}
        """
        created_playlists = {}

        logger.info(f"Creating {len(genre_map)} genre playlists...")

        for genre, tracks in tqdm(genre_map.items(), desc="Creating playlists"):
            if not tracks:
                continue

            playlist_name = f"{prefix} - {genre.title()}"
            description = f"Auto-generated playlist containing {len(tracks)} {genre} tracks"

            try:
                playlist_id = self.create_playlist(playlist_name, description, public)

                track_uris = [t['uri'] for t in tracks if t.get('uri')]
                self.add_tracks_to_playlist(playlist_id, track_uris)

                created_playlists[genre] = playlist_id

            except Exception as e:
                logger.error(f"Error creating playlist for {genre}: {e}")

        logger.info(f"Successfully created {len(created_playlists)} playlists")
        return created_playlists

    def create_artist_playlists(self, artist_map, prefix="SpotifySort", public=False, min_tracks=5):
        """
        Create playlists for each artist (only if they have enough tracks)

        Args:
            artist_map: Dictionary {artist: [tracks]}
            prefix: Prefix for playlist names
            public: Whether playlists should be public
            min_tracks: Minimum tracks needed to create playlist

        Returns:
            Dictionary {artist: playlist_id}
        """
        created_playlists = {}

        # Filter artists with enough tracks
        filtered_artists = {k: v for k, v in artist_map.items() if len(v) >= min_tracks}

        logger.info(f"Creating {len(filtered_artists)} artist playlists...")

        for artist, tracks in tqdm(filtered_artists.items(), desc="Creating artist playlists"):
            playlist_name = f"{prefix} - {artist}"
            description = f"Collection of {len(tracks)} tracks by {artist}"

            try:
                playlist_id = self.create_playlist(playlist_name, description, public)

                track_uris = [t['uri'] for t in tracks if t.get('uri')]
                self.add_tracks_to_playlist(playlist_id, track_uris)

                created_playlists[artist] = playlist_id

            except Exception as e:
                logger.error(f"Error creating playlist for {artist}: {e}")

        return created_playlists

    def create_year_playlists(self, year_map, prefix="SpotifySort", public=False):
        """Create playlists grouped by release year"""
        created_playlists = {}

        logger.info(f"Creating {len(year_map)} year playlists...")

        for year, tracks in tqdm(year_map.items(), desc="Creating year playlists"):
            if not tracks or year == 'Unknown':
                continue

            playlist_name = f"{prefix} - {year}s Music" if len(str(year)) == 3 else f"{prefix} - {year}"
            description = f"Music from {year} - {len(tracks)} tracks"

            try:
                playlist_id = self.create_playlist(playlist_name, description, public)

                track_uris = [t['uri'] for t in tracks if t.get('uri')]
                self.add_tracks_to_playlist(playlist_id, track_uris)

                created_playlists[year] = playlist_id

            except Exception as e:
                logger.error(f"Error creating playlist for {year}: {e}")

        return created_playlists

    def create_mood_playlists(self, mood_map, prefix="SpotifySort", public=False):
        """Create playlists based on mood analysis"""
        created_playlists = {}

        mood_descriptions = {
            'Happy': 'Upbeat and positive vibes',
            'Sad': 'Melancholic and emotional tracks',
            'Energetic': 'High energy and fast-paced music',
            'Calm': 'Relaxing and peaceful tunes',
            'Party': 'Perfect for parties and dancing',
            'Chill': 'Laid-back and acoustic vibes'
        }

        logger.info("Creating mood playlists...")

        for mood, tracks in tqdm(mood_map.items(), desc="Creating mood playlists"):
            if not tracks:
                continue

            playlist_name = f"{prefix} - {mood}"
            description = f"{mood_descriptions.get(mood, '')} - {len(tracks)} tracks"

            try:
                playlist_id = self.create_playlist(playlist_name, description, public)

                track_uris = [t['uri'] for t in tracks if t.get('uri')]
                self.add_tracks_to_playlist(playlist_id, track_uris)

                created_playlists[mood] = playlist_id

            except Exception as e:
                logger.error(f"Error creating {mood} playlist: {e}")

        return created_playlists

    def create_decade_playlists(self, tracks, prefix="SpotifySort", public=False):
        """
        Create playlists grouped by decade

        Args:
            tracks: List of tracks
            prefix: Playlist name prefix
            public: Whether playlists should be public

        Returns:
            Dictionary {decade: playlist_id}
        """
        # Group by decade
        decade_map = {}

        for track in tracks:
            year = track.get('release_year')
            if year:
                decade = (year // 10) * 10
                if decade not in decade_map:
                    decade_map[decade] = []
                decade_map[decade].append(track)

        created_playlists = {}

        logger.info(f"Creating {len(decade_map)} decade playlists...")

        for decade, decade_tracks in tqdm(decade_map.items(), desc="Creating decade playlists"):
            playlist_name = f"{prefix} - {decade}s"
            description = f"Music from the {decade}s - {len(decade_tracks)} tracks"

            try:
                playlist_id = self.create_playlist(playlist_name, description, public)

                track_uris = [t['uri'] for t in decade_tracks if t.get('uri')]
                self.add_tracks_to_playlist(playlist_id, track_uris)

                created_playlists[decade] = playlist_id

            except Exception as e:
                logger.error(f"Error creating {decade}s playlist: {e}")

        return created_playlists

    def create_custom_playlist(self, name, tracks, description="", public=False):
        """
        Create a custom playlist with specified tracks

        Args:
            name: Playlist name
            tracks: List of track dictionaries
            description: Playlist description
            public: Whether playlist should be public

        Returns:
            Playlist ID if successful, None otherwise
        """
        try:
            playlist_id = self.create_playlist(name, description, public)

            track_uris = [t['uri'] for t in tracks if t.get('uri')]
            if track_uris:
                self.add_tracks_to_playlist(playlist_id, track_uris)
                return playlist_id

            return None

        except Exception as e:
            logger.error(f"Error creating custom playlist: {e}")
            return None

    def delete_playlist(self, playlist_id):
        """Unfollow/delete a playlist"""
        try:
            self.sp.current_user_unfollow_playlist(playlist_id)
            logger.info(f"Deleted playlist {playlist_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting playlist: {e}")
            return False

    def get_playlist_info(self, playlist_id):
        """Get detailed information about a playlist"""
        try:
            playlist = self.sp.playlist(playlist_id)
            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'description': playlist.get('description', ''),
                'owner': playlist['owner']['display_name'],
                'public': playlist['public'],
                'tracks_total': playlist['tracks']['total'],
                'followers': playlist['followers']['total'],
                'image': playlist['images'][0]['url'] if playlist.get('images') else None,
                'url': playlist['external_urls']['spotify']
            }
        except Exception as e:
            logger.error(f"Error getting playlist info: {e}")
            return None
