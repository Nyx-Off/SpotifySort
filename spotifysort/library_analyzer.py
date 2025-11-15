"""
Spotify Library Analyzer
Analyzes user's Spotify library and extracts metadata
"""

import logging
from typing import List, Dict, Set
from tqdm import tqdm
from collections import defaultdict

logger = logging.getLogger(__name__)


class SpotifyLibraryAnalyzer:
    """Analyzes Spotify library and extracts useful information"""

    def __init__(self, spotify_client):
        self.sp = spotify_client

    def get_saved_tracks(self, limit=None):
        """
        Get all user's saved tracks

        Args:
            limit: Maximum number of tracks to fetch (None = all)

        Returns:
            List of track dictionaries
        """
        tracks = []
        offset = 0
        batch_size = 50

        logger.info("Fetching saved tracks...")

        with tqdm(desc="Loading saved tracks", unit=" tracks") as pbar:
            while True:
                results = self.sp.current_user_saved_tracks(limit=batch_size, offset=offset)

                if not results['items']:
                    break

                for item in results['items']:
                    track = self._extract_track_info(item['track'])
                    tracks.append(track)
                    pbar.update(1)

                    if limit and len(tracks) >= limit:
                        break

                offset += batch_size

                if not results['next'] or (limit and len(tracks) >= limit):
                    break

        logger.info(f"Fetched {len(tracks)} saved tracks")
        return tracks[:limit] if limit else tracks

    def get_user_playlists(self, include_liked_songs=True):
        """
        Get all user's playlists

        Args:
            include_liked_songs: Include "Liked Songs" as first entry

        Returns:
            List of playlist dictionaries
        """
        playlists = []

        # Add Liked Songs as first entry
        if include_liked_songs:
            try:
                # Get count of liked songs
                saved_tracks = self.sp.current_user_saved_tracks(limit=1)
                liked_count = saved_tracks['total']

                playlists.append({
                    'id': 'liked_songs',
                    'name': '♥ Liked Songs',
                    'owner': 'You',
                    'tracks_total': liked_count,
                    'public': False,
                    'description': 'Your liked songs collection',
                    'image': None,
                    'is_liked_songs': True
                })
            except Exception as e:
                logger.warning(f"Could not fetch liked songs count: {e}")

        offset = 0
        batch_size = 50

        logger.info("Fetching user playlists...")

        while True:
            results = self.sp.current_user_playlists(limit=batch_size, offset=offset)

            if not results['items']:
                break

            for playlist in results['items']:
                playlists.append({
                    'id': playlist['id'],
                    'name': playlist['name'],
                    'owner': playlist['owner']['display_name'],
                    'tracks_total': playlist['tracks']['total'],
                    'public': playlist['public'],
                    'description': playlist.get('description', ''),
                    'image': playlist['images'][0]['url'] if playlist.get('images') else None,
                    'is_liked_songs': False
                })

            offset += batch_size

            if not results['next']:
                break

        logger.info(f"Found {len(playlists)} playlists")
        return playlists

    def get_playlist_tracks(self, playlist_id):
        """Get all tracks from a specific playlist"""
        tracks = []
        offset = 0
        batch_size = 100

        while True:
            results = self.sp.playlist_tracks(playlist_id, limit=batch_size, offset=offset)

            if not results['items']:
                break

            for item in results['items']:
                if item['track']:
                    track = self._extract_track_info(item['track'])
                    tracks.append(track)

            offset += batch_size

            if not results['next']:
                break

        return tracks

    def get_top_artists(self, time_range='medium_term', limit=50):
        """
        Get user's top artists

        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
            limit: Number of artists

        Returns:
            List of artist dictionaries
        """
        results = self.sp.current_user_top_artists(time_range=time_range, limit=limit)

        artists = []
        for artist in results['items']:
            artists.append({
                'id': artist['id'],
                'name': artist['name'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'followers': artist['followers']['total'],
                'image': artist['images'][0]['url'] if artist.get('images') else None
            })

        return artists

    def get_top_tracks(self, time_range='medium_term', limit=50):
        """Get user's top tracks"""
        results = self.sp.current_user_top_tracks(time_range=time_range, limit=limit)

        tracks = []
        for track in results['items']:
            tracks.append(self._extract_track_info(track))

        return tracks

    def get_audio_features(self, track_ids):
        """
        Get audio features for multiple tracks

        Features include: danceability, energy, key, loudness, mode,
        speechiness, acousticness, instrumentalness, liveness, valence, tempo
        """
        if not track_ids:
            return []

        # Spotify API accepts max 100 IDs at a time
        batch_size = 100
        all_features = []

        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i + batch_size]
            features = self.sp.audio_features(batch)
            all_features.extend([f for f in features if f])

        return all_features

    def analyze_library_by_genre(self, tracks=None):
        """
        Analyze library and group by genre

        Returns:
            Dictionary {genre: [tracks]}
        """
        if tracks is None:
            tracks = self.get_saved_tracks()

        genre_map = defaultdict(list)

        logger.info("Analyzing genres...")

        for track in tqdm(tracks, desc="Analyzing genres"):
            # Get artist genres
            artist_id = track['artists'][0]['id']
            try:
                artist = self.sp.artist(artist_id)
                genres = artist['genres']

                if not genres:
                    genres = ['Unknown']

                for genre in genres:
                    genre_map[genre].append(track)

            except Exception as e:
                logger.warning(f"Error fetching artist info: {e}")
                genre_map['Unknown'].append(track)

        return dict(genre_map)

    def analyze_library_by_artist(self, tracks=None):
        """Group tracks by artist"""
        if tracks is None:
            tracks = self.get_saved_tracks()

        artist_map = defaultdict(list)

        for track in tracks:
            artist_name = track['artists'][0]['name']
            artist_map[artist_name].append(track)

        return dict(artist_map)

    def analyze_library_by_year(self, tracks=None):
        """Group tracks by release year"""
        if tracks is None:
            tracks = self.get_saved_tracks()

        year_map = defaultdict(list)

        for track in tracks:
            year = track.get('release_year', 'Unknown')
            year_map[year].append(track)

        return dict(year_map)

    def analyze_library_by_mood(self, tracks=None):
        """
        Analyze tracks by mood using audio features

        Moods:
        - Happy: high valence, high energy
        - Sad: low valence, low energy
        - Energetic: high energy, high tempo
        - Calm: low energy, low tempo
        - Party: high danceability, high energy
        """
        if tracks is None:
            tracks = self.get_saved_tracks()

        track_ids = [t['id'] for t in tracks]
        features = self.get_audio_features(track_ids)

        mood_map = {
            'Happy': [],
            'Sad': [],
            'Energetic': [],
            'Calm': [],
            'Party': [],
            'Chill': []
        }

        feature_dict = {f['id']: f for f in features if f}

        for track in tracks:
            f = feature_dict.get(track['id'])
            if not f:
                continue

            # Classify by mood
            if f['valence'] > 0.6 and f['energy'] > 0.6:
                mood_map['Happy'].append(track)
            if f['valence'] < 0.4 and f['energy'] < 0.4:
                mood_map['Sad'].append(track)
            if f['energy'] > 0.7 and f['tempo'] > 120:
                mood_map['Energetic'].append(track)
            if f['energy'] < 0.4 and f['tempo'] < 100:
                mood_map['Calm'].append(track)
            if f['danceability'] > 0.7 and f['energy'] > 0.7:
                mood_map['Party'].append(track)
            if f['acousticness'] > 0.5 and f['energy'] < 0.5:
                mood_map['Chill'].append(track)

        return mood_map

    def get_library_statistics(self, tracks=None):
        """Get comprehensive library statistics"""
        if tracks is None:
            tracks = self.get_saved_tracks()

        artists = set()
        albums = set()
        genres = set()

        total_duration = 0

        for track in tracks:
            artists.add(track['artists'][0]['name'])
            albums.add(track['album']['name'])
            total_duration += track['duration_ms']

        # Get genre statistics
        artist_ids = list(set([t['artists'][0]['id'] for t in tracks]))
        for i in range(0, len(artist_ids), 50):
            batch = artist_ids[i:i+50]
            artists_data = self.sp.artists(batch)
            for artist in artists_data['artists']:
                genres.update(artist['genres'])

        return {
            'total_tracks': len(tracks),
            'total_artists': len(artists),
            'total_albums': len(albums),
            'total_genres': len(genres),
            'total_duration_ms': total_duration,
            'total_duration_hours': total_duration / (1000 * 60 * 60),
            'genres': list(genres)
        }

    def get_tracks_from_playlists(self, playlist_ids):
        """
        Get all tracks from specified playlists

        Args:
            playlist_ids: List of playlist IDs (use 'liked_songs' for Liked Songs)

        Returns:
            List of track dictionaries
        """
        all_tracks = []
        seen_track_ids = set()

        logger.info(f"Fetching tracks from {len(playlist_ids)} playlists...")

        for playlist_id in playlist_ids:
            try:
                # Handle special case for Liked Songs
                if playlist_id == 'liked_songs':
                    logger.info("Fetching liked songs...")
                    liked_tracks = self.get_saved_tracks()
                    for track in liked_tracks:
                        if track['id'] not in seen_track_ids:
                            all_tracks.append(track)
                            seen_track_ids.add(track['id'])
                    continue

                # Regular playlist
                results = self.sp.playlist_tracks(playlist_id)

                while results:
                    for item in results['items']:
                        if item['track'] and item['track']['id'] not in seen_track_ids:
                            track = self._extract_track_info(item['track'])
                            if track:
                                all_tracks.append(track)
                                seen_track_ids.add(track['id'])

                    # Get next page
                    if results['next']:
                        results = self.sp.next(results)
                    else:
                        break

            except Exception as e:
                logger.error(f"Error fetching playlist {playlist_id}: {e}")

        logger.info(f"Fetched {len(all_tracks)} unique tracks from playlists")
        return all_tracks

    def filter_tracks(self, tracks, genres=None, mood=None, year_from=None, year_to=None, artists=None):
        """
        Filter tracks based on various criteria

        Args:
            tracks: List of track dictionaries
            genres: List of genres to filter by (case-insensitive)
            mood: Mood filter (happy, sad, energetic, calm, party)
            year_from: Minimum release year
            year_to: Maximum release year
            artists: List of artist names to filter by (case-insensitive)

        Returns:
            List of filtered tracks
        """
        filtered = tracks

        # Filter by year
        if year_from or year_to:
            filtered = [
                t for t in filtered
                if t.get('release_year') and
                (not year_from or t['release_year'] >= year_from) and
                (not year_to or t['release_year'] <= year_to)
            ]

        # Filter by artists
        if artists:
            artists_lower = [a.strip().lower() for a in artists if a.strip()]
            filtered = [
                t for t in filtered
                if any(artist_name.lower() in artists_lower
                      for artist_name in [a['name'] for a in t['artists']])
            ]

        # Filter by genre
        if genres:
            genres_lower = [g.strip().lower() for g in genres if g.strip()]
            filtered_by_genre = []

            for track in filtered:
                try:
                    artist_id = track['artists'][0]['id']
                    artist = self.sp.artist(artist_id)
                    artist_genres = [g.lower() for g in artist.get('genres', [])]

                    # Check if any of the track's genres match the filter
                    if any(any(filter_genre in genre for genre in artist_genres)
                          for filter_genre in genres_lower):
                        filtered_by_genre.append(track)

                except Exception as e:
                    logger.warning(f"Error checking genres for track: {e}")

            filtered = filtered_by_genre

        # Filter by mood
        if mood:
            track_ids = [t['id'] for t in filtered]
            features = self.get_audio_features(track_ids)
            feature_dict = {f['id']: f for f in features if f}

            mood_filtered = []

            for track in filtered:
                f = feature_dict.get(track['id'])
                if not f:
                    continue

                # Apply mood filter
                add_track = False
                mood_lower = mood.lower()

                if mood_lower == 'happy' and f['valence'] > 0.6 and f['energy'] > 0.6:
                    add_track = True
                elif mood_lower == 'sad' and f['valence'] < 0.4 and f['energy'] < 0.4:
                    add_track = True
                elif mood_lower == 'energetic' and f['energy'] > 0.7 and f['tempo'] > 120:
                    add_track = True
                elif mood_lower == 'calm' and f['energy'] < 0.4 and f['tempo'] < 100:
                    add_track = True
                elif mood_lower == 'party' and f['danceability'] > 0.7 and f['energy'] > 0.7:
                    add_track = True

                if add_track:
                    mood_filtered.append(track)

            filtered = mood_filtered

        logger.info(f"Filtered {len(filtered)} tracks from {len(tracks)} total tracks")
        return filtered

    def _extract_track_info(self, track):
        """Extract relevant information from track object"""
        if not track:
            return None

        return {
            'id': track['id'],
            'name': track['name'],
            'artists': [{'id': a['id'], 'name': a['name']} for a in track['artists']],
            'album': {
                'id': track['album']['id'],
                'name': track['album']['name'],
                'release_date': track['album']['release_date'],
            },
            'duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'explicit': track['explicit'],
            'preview_url': track.get('preview_url'),
            'uri': track['uri'],
            'release_year': int(track['album']['release_date'][:4]) if track['album']['release_date'] else None
        }
