"""
Flask web application for SpotifySort
Web interface with Spotify OAuth and playlist management
"""

from flask import Flask, render_template, session, redirect, request, jsonify, url_for
from flask_cors import CORS
from flask_session import Session
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spotifysort.spotify_auth import SpotifyAuthenticator
from spotifysort.library_analyzer import SpotifyLibraryAnalyzer
from spotifysort.playlist_manager import SpotifyPlaylistManager

# Load environment variables
load_dotenv()


def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = '/tmp/spotifysort_sessions'

    Session(app)

    def get_auth_manager():
        """Get Spotify OAuth manager"""
        from spotipy.oauth2 import SpotifyOAuth
        return SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope=" ".join(SpotifyAuthenticator.SCOPES),
            cache_path=None,  # Use session instead
            show_dialog=False
        )

    def get_spotify_client():
        """Get authenticated Spotify client from session"""
        if 'token_info' not in session:
            return None

        try:
            import spotipy
            auth_manager = get_auth_manager()
            # Restore token from session
            token_info = session['token_info']

            # Check if token is expired and refresh if needed
            if auth_manager.is_token_expired(token_info):
                token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
                session['token_info'] = token_info

            return spotipy.Spotify(auth=token_info['access_token'])
        except Exception as e:
            print(f"Error getting Spotify client: {e}")
            return None

    # Routes

    @app.route('/')
    def index():
        """Main page"""
        sp = get_spotify_client()

        if sp:
            try:
                user = sp.current_user()
                return render_template('index.html', user=user, authenticated=True)
            except:
                session.clear()

        return render_template('index.html', authenticated=False)

    @app.route('/login')
    def login():
        """Initiate Spotify OAuth login"""
        try:
            auth_manager = get_auth_manager()
            auth_url = auth_manager.get_authorize_url()
            return redirect(auth_url)
        except Exception as e:
            return f"Authentication error: {e}", 500

    @app.route('/callback')
    def callback():
        """Handle Spotify OAuth callback"""
        try:
            auth_manager = get_auth_manager()
            code = request.args.get('code')

            if not code:
                return "No authorization code received", 400

            # Exchange code for token
            token_info = auth_manager.get_access_token(code, as_dict=True, check_cache=False)
            session['token_info'] = token_info

            return redirect(url_for('index'))
        except Exception as e:
            return f"Callback error: {e}", 500

    @app.route('/logout')
    def logout():
        """Logout and clear session"""
        session.clear()
        return redirect(url_for('index'))

    @app.route('/api/user')
    def api_user():
        """Get current user information"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            auth = SpotifyAuthenticator()
            auth.sp = sp
            user_info = auth.get_user_info()
            return jsonify(user_info)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/stats')
    def api_stats():
        """Get library statistics"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            limit = request.args.get('limit', type=int)
            analyzer = SpotifyLibraryAnalyzer(sp)
            tracks = analyzer.get_saved_tracks(limit=limit)
            stats = analyzer.get_library_statistics(tracks)
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/tracks')
    def api_tracks():
        """Get saved tracks"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            limit = request.args.get('limit', type=int, default=50)
            analyzer = SpotifyLibraryAnalyzer(sp)
            tracks = analyzer.get_saved_tracks(limit=limit)
            return jsonify(tracks)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/playlists')
    def api_playlists():
        """Get user playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            analyzer = SpotifyLibraryAnalyzer(sp)
            playlists = analyzer.get_user_playlists()
            return jsonify(playlists)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/top-artists')
    def api_top_artists():
        """Get top artists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            time_range = request.args.get('time_range', 'medium_term')
            limit = request.args.get('limit', type=int, default=20)

            analyzer = SpotifyLibraryAnalyzer(sp)
            artists = analyzer.get_top_artists(time_range=time_range, limit=limit)
            return jsonify(artists)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analyze/genre', methods=['POST'])
    def api_analyze_genre():
        """Analyze library by genre"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            tracks = analyzer.get_saved_tracks(limit=limit)
            genre_map = analyzer.analyze_library_by_genre(tracks)

            # Convert to list format for JSON
            result = [{'genre': k, 'tracks': len(v)} for k, v in genre_map.items()]
            result.sort(key=lambda x: x['tracks'], reverse=True)

            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analyze/mood', methods=['POST'])
    def api_analyze_mood():
        """Analyze library by mood"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            tracks = analyzer.get_saved_tracks(limit=limit)
            mood_map = analyzer.analyze_library_by_mood(tracks)

            result = [{'mood': k, 'tracks': len(v)} for k, v in mood_map.items() if v]
            result.sort(key=lambda x: x['tracks'], reverse=True)

            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/create-playlists/genre', methods=['POST'])
    def api_create_genre_playlists():
        """Create genre-based playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            prefix = data.get('prefix', 'SpotifySort')
            public = data.get('public', False)
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            manager = SpotifyPlaylistManager(sp)

            tracks = analyzer.get_saved_tracks(limit=limit)
            genre_map = analyzer.analyze_library_by_genre(tracks)
            created = manager.create_genre_playlists(genre_map, prefix=prefix, public=public)

            return jsonify({
                'success': True,
                'created': len(created),
                'playlists': [{'genre': k, 'id': v} for k, v in created.items()]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/create-playlists/mood', methods=['POST'])
    def api_create_mood_playlists():
        """Create mood-based playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            prefix = data.get('prefix', 'SpotifySort')
            public = data.get('public', False)
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            manager = SpotifyPlaylistManager(sp)

            tracks = analyzer.get_saved_tracks(limit=limit)
            mood_map = analyzer.analyze_library_by_mood(tracks)
            created = manager.create_mood_playlists(mood_map, prefix=prefix, public=public)

            return jsonify({
                'success': True,
                'created': len(created),
                'playlists': [{'mood': k, 'id': v} for k, v in created.items()]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/create-playlists/decade', methods=['POST'])
    def api_create_decade_playlists():
        """Create decade-based playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            prefix = data.get('prefix', 'SpotifySort')
            public = data.get('public', False)
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            manager = SpotifyPlaylistManager(sp)

            tracks = analyzer.get_saved_tracks(limit=limit)
            created = manager.create_decade_playlists(tracks, prefix=prefix, public=public)

            return jsonify({
                'success': True,
                'created': len(created),
                'playlists': [{'decade': f"{k}s", 'id': v} for k, v in created.items()]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/create-playlists/artist', methods=['POST'])
    def api_create_artist_playlists():
        """Create artist-based playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            prefix = data.get('prefix', 'SpotifySort')
            public = data.get('public', False)
            min_tracks = data.get('min_tracks', 5)
            limit = data.get('limit')

            analyzer = SpotifyLibraryAnalyzer(sp)
            manager = SpotifyPlaylistManager(sp)

            tracks = analyzer.get_saved_tracks(limit=limit)
            artist_map = analyzer.analyze_library_by_artist(tracks)
            created = manager.create_artist_playlists(artist_map, prefix=prefix,
                                                     public=public, min_tracks=min_tracks)

            return jsonify({
                'success': True,
                'created': len(created),
                'playlists': [{'artist': k, 'id': v} for k, v in created.items()]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/discover-genres', methods=['POST'])
    def api_discover_genres():
        """Discover genres from selected playlists"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            playlist_ids = data.get('playlist_ids', [])

            if not playlist_ids:
                return jsonify({'error': 'No playlists selected'}), 400

            analyzer = SpotifyLibraryAnalyzer(sp)

            # Get tracks from selected playlists (limit to reduce API calls)
            tracks = analyzer.get_tracks_from_playlists(playlist_ids)

            # Limit tracks to avoid rate limiting (max 300 tracks analyzed)
            max_tracks = 300
            if len(tracks) > max_tracks:
                tracks = tracks[:max_tracks]
                limited = True
            else:
                limited = False

            # Analyze genres - optimized version
            from collections import defaultdict
            genre_count = defaultdict(int)

            # Create artist_id -> tracks mapping for efficient counting
            artist_tracks = defaultdict(list)
            for track in tracks:
                artist_id = track['artists'][0]['id']
                artist_tracks[artist_id].append(track)

            # Get unique artist IDs
            artist_ids = list(artist_tracks.keys())

            # Fetch artist info in batches
            for i in range(0, len(artist_ids), 50):
                batch = artist_ids[i:i+50]
                try:
                    artists_data = sp.artists(batch)

                    for artist in artists_data['artists']:
                        artist_id = artist['id']
                        artist_genres = artist.get('genres', [])

                        # Count tracks for this artist's genres
                        track_count = len(artist_tracks[artist_id])

                        if artist_genres:
                            for genre in artist_genres:
                                genre_count[genre] += track_count
                        else:
                            genre_count['Unknown'] += track_count

                except Exception as e:
                    logger.warning(f"Error fetching artist batch: {e}")
                    continue

            # Convert to list and sort by count
            genres = [{'name': genre, 'count': count} for genre, count in genre_count.items()]
            genres.sort(key=lambda x: x['count'], reverse=True)

            return jsonify({
                'genres': genres,
                'tracks_analyzed': len(tracks),
                'limited': limited
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/filter-tracks', methods=['POST'])
    def api_filter_tracks():
        """Filter tracks with advanced criteria"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            analyzer = SpotifyLibraryAnalyzer(sp)

            # Get source tracks
            if data.get('source') == 'playlists' and data.get('playlist_ids'):
                tracks = analyzer.get_tracks_from_playlists(data['playlist_ids'])
            else:
                tracks = analyzer.get_saved_tracks(limit=500)

            # Apply filters
            filtered = analyzer.filter_tracks(
                tracks,
                genres=data.get('genres', '').split(',') if data.get('genres') else None,
                mood=data.get('mood'),
                year_from=int(data['year_from']) if data.get('year_from') else None,
                year_to=int(data['year_to']) if data.get('year_to') else None,
                artists=data.get('artists', '').split(',') if data.get('artists') else None
            )

            return jsonify({'count': len(filtered)})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/create-filtered-playlist', methods=['POST'])
    def api_create_filtered_playlist():
        """Create a playlist with filtered tracks"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            analyzer = SpotifyLibraryAnalyzer(sp)
            manager = SpotifyPlaylistManager(sp)

            # Get source tracks
            if data.get('source') == 'playlists' and data.get('playlist_ids'):
                tracks = analyzer.get_tracks_from_playlists(data['playlist_ids'])
            else:
                tracks = analyzer.get_saved_tracks(limit=500)

            # Apply filters
            filtered = analyzer.filter_tracks(
                tracks,
                genres=data.get('genres', '').split(',') if data.get('genres') else None,
                mood=data.get('mood'),
                year_from=int(data['year_from']) if data.get('year_from') else None,
                year_to=int(data['year_to']) if data.get('year_to') else None,
                artists=data.get('artists', '').split(',') if data.get('artists') else None
            )

            # Create playlist
            playlist_name = data.get('name', 'Filtered Playlist')
            public = data.get('public', False)

            playlist_id = manager.create_playlist(playlist_name, public=public)

            # Extract URIs from track objects
            track_uris = [track['uri'] for track in filtered]
            success = manager.add_tracks_to_playlist(playlist_id, track_uris)

            return jsonify({
                'success': success,
                'name': playlist_name,
                'playlist_id': playlist_id,
                'tracks_added': len(filtered) if success else 0
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/playlist/<playlist_id>/tracks')
    def api_get_playlist_tracks(playlist_id):
        """Get tracks from a specific playlist"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            # Handle special case for Liked Songs
            if playlist_id == 'liked_songs':
                analyzer = SpotifyLibraryAnalyzer(sp)
                liked_tracks = analyzer.get_saved_tracks(limit=100)  # Limit to first 100 for display

                tracks = []
                for track in liked_tracks:
                    tracks.append({
                        'name': track['name'],
                        'artists': ', '.join([a['name'] for a in track['artists']]),
                        'uri': track['uri']
                    })

                return jsonify({
                    'name': '♥ Liked Songs',
                    'public': False,
                    'tracks': tracks,
                    'is_liked_songs': True
                })

            # Regular playlist
            playlist = sp.playlist(playlist_id)

            tracks = []
            for item in playlist['tracks']['items']:
                if item['track']:
                    track = item['track']
                    tracks.append({
                        'name': track['name'],
                        'artists': ', '.join([a['name'] for a in track['artists']]),
                        'uri': track['uri']
                    })

            return jsonify({
                'name': playlist['name'],
                'public': playlist['public'],
                'tracks': tracks,
                'is_liked_songs': False
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/playlist/<playlist_id>/tracks', methods=['DELETE'])
    def api_remove_track_from_playlist(playlist_id):
        """Remove a track from a playlist"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            track_uri = data.get('track_uri')

            if not track_uri:
                return jsonify({'error': 'track_uri required'}), 400

            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])

            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/playlist/<playlist_id>/rename', methods=['POST'])
    def api_rename_playlist(playlist_id):
        """Rename a playlist"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            data = request.get_json() or {}
            new_name = data.get('name')

            if not new_name:
                return jsonify({'error': 'name required'}), 400

            sp.playlist_change_details(playlist_id, name=new_name)

            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/playlist/<playlist_id>', methods=['DELETE'])
    def api_delete_playlist(playlist_id):
        """Unfollow (delete) a playlist"""
        sp = get_spotify_client()
        if not sp:
            return jsonify({'error': 'Not authenticated'}), 401

        try:
            sp.current_user_unfollow_playlist(playlist_id)
            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


def main():
    """Run the web server"""
    import argparse

    parser = argparse.ArgumentParser(description='SpotifySort Web Server')
    parser.add_argument('--host', default=os.getenv('FLASK_HOST', '127.0.0.1'),
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=int(os.getenv('FLASK_PORT', 5000)),
                       help='Port to bind to')
    parser.add_argument('--debug', action='store_true',
                       default=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
                       help='Enable debug mode')

    args = parser.parse_args()

    app = create_app()

    print(f"""
    ╔═══════════════════════════════════════════════╗
    ║        SpotifySort Web Server                 ║
    ╚═══════════════════════════════════════════════╝

    Server running at: http://{args.host}:{args.port}

    1. Open the URL in your browser
    2. Click "Login with Spotify"
    3. Authorize the application
    4. Start organizing your library!

    Press Ctrl+C to stop
    """)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
