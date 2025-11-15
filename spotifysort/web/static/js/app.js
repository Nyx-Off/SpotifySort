// SpotifySort Web Application

let currentAnalysis = null;
let currentSortType = null;

// Load initial data on page load
document.addEventListener('DOMContentLoaded', function() {
    const authenticated = document.querySelector('.dashboard');
    if (authenticated) {
        loadStatistics();
        loadPlaylists();
    }
});

// Load library statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/stats?limit=500');
        const stats = await response.json();

        const container = document.getElementById('statsContainer');
        container.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <h3>${stats.total_tracks.toLocaleString()}</h3>
                    <p><i class="fas fa-music"></i> Tracks</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.total_artists.toLocaleString()}</h3>
                    <p><i class="fas fa-user"></i> Artists</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.total_albums.toLocaleString()}</h3>
                    <p><i class="fas fa-compact-disc"></i> Albums</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.total_genres.toLocaleString()}</h3>
                    <p><i class="fas fa-guitar"></i> Genres</p>
                </div>
                <div class="stat-item">
                    <h3>${stats.total_duration_hours.toFixed(1)}</h3>
                    <p><i class="fas fa-clock"></i> Hours</p>
                </div>
            </div>
        `;

    } catch (error) {
        console.error('Error loading statistics:', error);
        document.getElementById('statsContainer').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> Error loading statistics
            </div>
        `;
    }
}

// Load playlists
async function loadPlaylists() {
    try {
        const response = await fetch('/api/playlists');
        const playlists = await response.json();

        const container = document.getElementById('playlistsContainer');

        if (playlists.length === 0) {
            container.innerHTML = `
                <p class="text-muted text-center">No playlists found. Create some using the cards above!</p>
            `;
            return;
        }

        let html = '<div class="list-group">';
        playlists.slice(0, 10).forEach(playlist => {
            const isLikedSongs = playlist.id === 'liked_songs';
            const imageUrl = playlist.image || (isLikedSongs ? 'https://via.placeholder.com/60?text=♥' : 'https://via.placeholder.com/60?text=No+Image');
            const spotifyUrl = isLikedSongs ? 'https://open.spotify.com/collection/tracks' : `https://open.spotify.com/playlist/${playlist.id}`;

            html += `
                <div class="list-group-item playlist-item">
                    <div class="d-flex align-items-center">
                        <img src="${imageUrl}" alt="${playlist.name}" class="me-3">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">${escapeHtml(playlist.name)}</h6>
                            <small class="text-muted">
                                ${playlist.tracks_total} tracks • ${playlist.public ? 'Public' : 'Private'}
                            </small>
                        </div>
                        <a href="${spotifyUrl}"
                           target="_blank"
                           class="btn btn-sm btn-success">
                            <i class="fab fa-spotify"></i> Open
                        </a>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        if (playlists.length > 10) {
            html += `<p class="text-center mt-3 text-muted">Showing 10 of ${playlists.length} playlists</p>`;
        }

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading playlists:', error);
    }
}

// Show sort modal
function showSortModal(type) {
    currentSortType = type;
    document.getElementById('sortType').value = type;
    document.getElementById('analysisResult').style.display = 'none';
    document.getElementById('createBtn').style.display = 'none';
    document.getElementById('analyzeBtn').style.display = 'inline-block';

    const titles = {
        'genre': 'Sort by Genre',
        'mood': 'Sort by Mood',
        'decade': 'Sort by Decade',
        'artist': 'Sort by Artist'
    };

    const descriptions = {
        'genre': 'This will analyze your library and create playlists for each genre (Rock, Pop, Jazz, etc.)',
        'mood': 'Using Spotify\'s audio analysis, this creates mood-based playlists (Happy, Sad, Energetic, Calm, etc.)',
        'decade': 'Create playlists organized by decade (70s, 80s, 90s, 2000s, etc.)',
        'artist': 'Create individual playlists for each artist (only artists with enough tracks)'
    };

    document.getElementById('sortModalTitle').textContent = titles[type];
    document.getElementById('sortDescription').textContent = descriptions[type];

    // Show/hide artist-specific options
    document.getElementById('minTracksSection').style.display =
        type === 'artist' ? 'block' : 'none';

    const modal = new bootstrap.Modal(document.getElementById('sortModal'));
    modal.show();
}

// Analyze library
async function analyzeLibrary() {
    const type = currentSortType;
    const btn = document.getElementById('analyzeBtn');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

    try {
        const response = await fetch(`/api/analyze/${type}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({limit: 500})
        });

        const data = await response.json();
        currentAnalysis = data;

        // Display results
        displayAnalysisResults(data, type);

        // Show create button
        document.getElementById('createBtn').style.display = 'inline-block';

    } catch (error) {
        alert('Error analyzing library: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    }
}

// Display analysis results
function displayAnalysisResults(data, type) {
    const container = document.getElementById('analysisContent');
    const resultDiv = document.getElementById('analysisResult');

    let html = '<div class="mt-3">';

    if (type === 'genre' || type === 'mood') {
        data.slice(0, 10).forEach(item => {
            const label = item.genre || item.mood;
            html += `
                <div class="analysis-item">
                    <span>${label}</span>
                    <span class="badge-custom">${item.tracks} tracks</span>
                </div>
            `;
        });

        if (data.length > 10) {
            html += `<p class="text-muted mt-2">... and ${data.length - 10} more</p>`;
        }
    }

    html += `<div class="alert alert-success mt-3">
        <i class="fas fa-check-circle"></i>
        Ready to create ${data.length} playlists
    </div></div>`;

    container.innerHTML = html;
    resultDiv.style.display = 'block';
}

// Create playlists
async function createPlaylists() {
    const type = currentSortType;
    const prefix = document.getElementById('playlistPrefix').value || 'SpotifySort';
    const isPublic = document.getElementById('makePublic').checked;
    const minTracks = parseInt(document.getElementById('minTracks').value) || 5;

    // Hide modal and show progress
    bootstrap.Modal.getInstance(document.getElementById('sortModal')).hide();

    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    progressModal.show();

    document.getElementById('progressText').textContent = 'Creating playlists on Spotify...';

    try {
        const requestBody = {
            prefix: prefix,
            public: isPublic,
            limit: 500
        };

        if (type === 'artist') {
            requestBody.min_tracks = minTracks;
        }

        const response = await fetch(`/api/create-playlists/${type}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestBody)
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('progressText').innerHTML = `
                <div class="success-message">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <h5>Success!</h5>
                    <p>Created ${result.created} playlists on your Spotify account</p>
                </div>
            `;

            // Reload playlists after 2 seconds
            setTimeout(() => {
                progressModal.hide();
                loadPlaylists();
            }, 3000);

        } else {
            throw new Error(result.error || 'Unknown error');
        }

    } catch (error) {
        progressModal.hide();
        alert('Error creating playlists: ' + error.message);
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
