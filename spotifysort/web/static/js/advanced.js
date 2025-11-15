// Advanced sorting and playlist management

let allPlaylists = [];
let selectedPlaylistIds = [];
let discoveredGenres = [];

// Show advanced sort modal
function showAdvancedSortModal() {
    const modal = new bootstrap.Modal(document.getElementById('advancedSortModal'));
    modal.show();

    // Reset form
    document.getElementById('genreDiscoverySection').style.display = 'none';
    document.getElementById('filterGenres').value = '';
    document.getElementById('advancedPreview').style.display = 'none';
    document.getElementById('advancedCreateBtn').style.display = 'none';
    document.getElementById('advancedAnalyzeBtn').style.display = 'inline-block';
    discoveredGenres = [];

    // Load playlists for selection
    loadPlaylistsForSelection();
}

// Show playlist manager
function showPlaylistManager() {
    const modal = new bootstrap.Modal(document.getElementById('playlistManagerModal'));
    modal.show();

    loadPlaylistsForManagement();
}

// Toggle playlist selection section
function togglePlaylistSelection() {
    const source = document.querySelector('input[name="source"]:checked').value;
    const section = document.getElementById('playlistSelectionSection');

    if (source === 'playlists') {
        section.style.display = 'block';
        loadPlaylistsForSelection();
    } else {
        section.style.display = 'none';
    }
}

// Load playlists for selection
async function loadPlaylistsForSelection() {
    try {
        const response = await fetch('/api/playlists');
        allPlaylists = await response.json();

        const container = document.getElementById('playlistCheckboxes');

        if (allPlaylists.length === 0) {
            container.innerHTML = '<p class="text-muted">No playlists found</p>';
            return;
        }

        let html = '<div class="mb-2"><button type="button" class="btn btn-sm btn-outline-primary me-2" onclick="selectAllPlaylists()">Select All</button>';
        html += '<button type="button" class="btn btn-sm btn-outline-secondary" onclick="deselectAllPlaylists()">Deselect All</button></div>';

        allPlaylists.forEach(playlist => {
            const isLikedSongs = playlist.id === 'liked_songs';
            html += `
                <div class="form-check">
                    <input class="form-check-input playlist-checkbox" type="checkbox"
                           value="${playlist.id}" id="pl_${playlist.id}"
                           onchange="updateSelectedPlaylists()">
                    <label class="form-check-label" for="pl_${playlist.id}">
                        ${escapeHtml(playlist.name)}
                        <small class="text-muted">(${playlist.tracks_total} tracks)${isLikedSongs ? ' - Your library' : ''}</small>
                    </label>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading playlists:', error);
        document.getElementById('playlistCheckboxes').innerHTML =
            '<p class="text-danger">Error loading playlists</p>';
    }
}

// Select all playlists
function selectAllPlaylists() {
    document.querySelectorAll('.playlist-checkbox').forEach(cb => cb.checked = true);
    updateSelectedPlaylists();
}

// Deselect all playlists
function deselectAllPlaylists() {
    document.querySelectorAll('.playlist-checkbox').forEach(cb => cb.checked = false);
    updateSelectedPlaylists();
}

// Update selected playlists array
function updateSelectedPlaylists() {
    selectedPlaylistIds = Array.from(document.querySelectorAll('.playlist-checkbox:checked'))
        .map(cb => cb.value);

    // Show/hide discover genres button
    const discoverBtn = document.getElementById('discoverGenresBtn');
    if (discoverBtn) {
        discoverBtn.style.display = selectedPlaylistIds.length > 0 ? 'inline-block' : 'none';
    }
}

// Discover genres from selected playlists
async function discoverGenres() {
    if (selectedPlaylistIds.length === 0) {
        alert('Please select at least one playlist first');
        return;
    }

    const btn = document.getElementById('discoverGenresBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

    try {
        const response = await fetch('/api/discover-genres', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({playlist_ids: selectedPlaylistIds})
        });

        if (!response.ok) {
            throw new Error('Failed to discover genres');
        }

        const data = await response.json();
        discoveredGenres = data.genres;

        // Display genres
        displayGenreCheckboxes(discoveredGenres);

        // Show success message with info about tracks analyzed
        let message = `Found ${discoveredGenres.length} genres`;
        if (data.limited) {
            message += ` (analyzed first ${data.tracks_analyzed} tracks to avoid rate limiting)`;
        } else {
            message += ` (${data.tracks_analyzed} tracks analyzed)`;
        }

        document.getElementById('genreDiscoveryText').textContent = message;
        document.getElementById('genreDiscoverySection').style.display = 'block';

    } catch (error) {
        alert('Error discovering genres: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// Display genre checkboxes
function displayGenreCheckboxes(genres) {
    const container = document.getElementById('genreCheckboxes');

    if (genres.length === 0) {
        container.innerHTML = '<p class="text-muted mb-0">No genres found</p>';
        return;
    }

    let html = '';
    genres.forEach((genre, index) => {
        html += `
            <div class="form-check">
                <input class="form-check-input genre-checkbox" type="checkbox"
                       value="${escapeHtml(genre.name)}" id="genre_${index}"
                       onchange="updateGenreFilter()" checked>
                <label class="form-check-label" for="genre_${index}">
                    ${escapeHtml(genre.name)}
                    <small class="text-muted">(${genre.count} tracks)</small>
                </label>
            </div>
        `;
    });

    container.innerHTML = html;
    updateGenreFilter();
}

// Update genre filter based on selected checkboxes
function updateGenreFilter() {
    const selectedGenres = Array.from(document.querySelectorAll('.genre-checkbox:checked'))
        .map(cb => cb.value);

    const filterInput = document.getElementById('filterGenres');
    filterInput.value = selectedGenres.join(', ');
}

// Select all genres
function selectAllGenres() {
    document.querySelectorAll('.genre-checkbox').forEach(cb => cb.checked = true);
    updateGenreFilter();
}

// Deselect all genres
function deselectAllGenres() {
    document.querySelectorAll('.genre-checkbox').forEach(cb => cb.checked = false);
    updateGenreFilter();
}

// Analyze with advanced filters
async function analyzeAdvanced() {
    const source = document.querySelector('input[name="source"]:checked').value;
    const btn = document.getElementById('advancedAnalyzeBtn');

    // Validate
    if (source === 'playlists' && selectedPlaylistIds.length === 0) {
        alert('Please select at least one playlist');
        return;
    }

    const playlistName = document.getElementById('advancedPlaylistName').value.trim();
    if (!playlistName) {
        alert('Please enter a playlist name');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';

    try {
        // Build filters
        const filters = {
            source: source,
            playlist_ids: source === 'playlists' ? selectedPlaylistIds : null,
            genres: document.getElementById('filterGenres').value.trim(),
            mood: document.getElementById('filterMood').value,
            year_from: document.getElementById('filterYearFrom').value,
            year_to: document.getElementById('filterYearTo').value,
            artists: document.getElementById('filterArtists').value.trim()
        };

        const response = await fetch('/api/filter-tracks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(filters)
        });

        if (!response.ok) {
            throw new Error('Failed to analyze');
        }

        const result = await response.json();

        // Show preview
        const preview = document.getElementById('advancedPreview');
        const previewText = document.getElementById('advancedPreviewText');

        previewText.textContent = `Found ${result.count} tracks matching your filters`;
        preview.style.display = 'block';

        // Enable create button
        document.getElementById('advancedCreateBtn').style.display = 'inline-block';

    } catch (error) {
        alert('Error analyzing: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-search"></i> Preview';
    }
}

// Create playlist with advanced filters
async function createAdvanced() {
    const source = document.querySelector('input[name="source"]:checked').value;
    const playlistName = document.getElementById('advancedPlaylistName').value.trim();
    const isPublic = document.getElementById('advancedMakePublic').checked;

    // Hide modal and show progress
    bootstrap.Modal.getInstance(document.getElementById('advancedSortModal')).hide();

    const progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
    progressModal.show();

    document.getElementById('progressText').textContent = 'Creating filtered playlist...';

    try {
        // Build filters
        const filters = {
            source: source,
            playlist_ids: source === 'playlists' ? selectedPlaylistIds : null,
            genres: document.getElementById('filterGenres').value.trim(),
            mood: document.getElementById('filterMood').value,
            year_from: document.getElementById('filterYearFrom').value,
            year_to: document.getElementById('filterYearTo').value,
            artists: document.getElementById('filterArtists').value.trim(),
            name: playlistName,
            public: isPublic
        };

        const response = await fetch('/api/create-filtered-playlist', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(filters)
        });

        if (!response.ok) {
            throw new Error('Failed to create playlist');
        }

        const result = await response.json();

        document.getElementById('progressText').innerHTML = `
            <div class="success-message">
                <i class="fas fa-check-circle fa-3x mb-3"></i>
                <h5>Success!</h5>
                <p>Created playlist "${result.name}" with ${result.tracks_added} tracks</p>
            </div>
        `;

        // Reload playlists after 2 seconds
        setTimeout(() => {
            progressModal.hide();
            loadPlaylists();
        }, 3000);

    } catch (error) {
        progressModal.hide();
        alert('Error creating playlist: ' + error.message);
    }
}

// Load playlists for management
async function loadPlaylistsForManagement() {
    try {
        const response = await fetch('/api/playlists');
        allPlaylists = await response.json();

        const container = document.getElementById('playlistManagerContent');

        if (allPlaylists.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No playlists found</p>';
            return;
        }

        displayPlaylistsForManagement(allPlaylists);

    } catch (error) {
        console.error('Error loading playlists:', error);
        document.getElementById('playlistManagerContent').innerHTML =
            '<p class="text-danger text-center">Error loading playlists</p>';
    }
}

// Display playlists for management
function displayPlaylistsForManagement(playlists) {
    const container = document.getElementById('playlistManagerContent');

    let html = '<div class="table-responsive"><table class="table table-hover">';
    html += '<thead><tr>';
    html += '<th>Name</th>';
    html += '<th>Tracks</th>';
    html += '<th>Public</th>';
    html += '<th>Actions</th>';
    html += '</tr></thead><tbody>';

    playlists.forEach(playlist => {
        const isLikedSongs = playlist.id === 'liked_songs';
        const spotifyUrl = isLikedSongs ? 'https://open.spotify.com/collection/tracks' : `https://open.spotify.com/playlist/${playlist.id}`;

        html += `
            <tr class="playlist-row" data-name="${escapeHtml(playlist.name).toLowerCase()}">
                <td>
                    <div class="d-flex align-items-center">
                        <img src="${playlist.image || 'https://via.placeholder.com/40'}"
                             alt="" class="me-2" style="width:40px;height:40px;border-radius:5px;">
                        <div>
                            <strong>${escapeHtml(playlist.name)}</strong>
                            ${isLikedSongs ? '<br><small class="text-muted">Your library</small>' : ''}
                        </div>
                    </div>
                </td>
                <td>${playlist.tracks_total}</td>
                <td>${playlist.public ? '<span class="badge bg-success">Public</span>' : '<span class="badge bg-secondary">Private</span>'}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewPlaylistDetails('${playlist.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${!isLikedSongs ? `
                        <button class="btn btn-sm btn-primary" onclick="renamePlaylist('${playlist.id}', '${escapeHtml(playlist.name)}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deletePlaylist('${playlist.id}', '${escapeHtml(playlist.name)}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : '<span class="text-muted small">Read-only</span>'}
                    <a href="${spotifyUrl}" target="_blank" class="btn btn-sm btn-success">
                        <i class="fab fa-spotify"></i>
                    </a>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Filter playlists in manager
function filterPlaylists() {
    const searchTerm = document.getElementById('playlistSearch').value.toLowerCase();
    const rows = document.querySelectorAll('.playlist-row');

    rows.forEach(row => {
        const name = row.getAttribute('data-name');
        if (name.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// View playlist details
async function viewPlaylistDetails(playlistId) {
    const modal = new bootstrap.Modal(document.getElementById('playlistDetailsModal'));
    const content = document.getElementById('playlistDetailsContent');

    content.innerHTML = '<div class="text-center"><div class="spinner-border text-success"></div><p class="mt-2">Loading...</p></div>';
    modal.show();

    try {
        const response = await fetch(`/api/playlist/${playlistId}/tracks`);
        const data = await response.json();

        document.getElementById('playlistDetailsTitle').textContent = data.name;

        const isLikedSongs = data.is_liked_songs || playlistId === 'liked_songs';

        let html = `
            <div class="mb-3">
                <strong>Tracks:</strong> ${data.tracks.length} ${data.tracks.length >= 100 && isLikedSongs ? '(showing first 100)' : ''} |
                <strong>Public:</strong> ${data.public ? 'Yes' : 'No'}
                ${isLikedSongs ? '<br><span class="text-muted small">Note: You cannot remove individual tracks from Liked Songs here. Unlike them directly in Spotify.</span>' : ''}
            </div>
            <div class="list-group" style="max-height: 400px; overflow-y: auto;">
        `;

        data.tracks.forEach((track, index) => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex align-items-center">
                        <span class="me-3 text-muted">${index + 1}</span>
                        <div class="flex-grow-1">
                            <strong>${escapeHtml(track.name)}</strong><br>
                            <small class="text-muted">${escapeHtml(track.artists)}</small>
                        </div>
                        ${!isLikedSongs ? `
                            <button class="btn btn-sm btn-danger" onclick="removeTrackFromPlaylist('${playlistId}', '${track.uri}', ${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        content.innerHTML = html;

    } catch (error) {
        content.innerHTML = '<p class="text-danger">Error loading playlist details</p>';
    }
}

// Rename playlist
async function renamePlaylist(playlistId, currentName) {
    const newName = prompt('Enter new playlist name:', currentName);

    if (!newName || newName === currentName) {
        return;
    }

    try {
        const response = await fetch(`/api/playlist/${playlistId}/rename`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: newName})
        });

        if (!response.ok) {
            throw new Error('Failed to rename');
        }

        alert('Playlist renamed successfully!');
        loadPlaylistsForManagement();
        loadPlaylists();

    } catch (error) {
        alert('Error renaming playlist: ' + error.message);
    }
}

// Delete playlist
async function deletePlaylist(playlistId, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/playlist/${playlistId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete');
        }

        alert('Playlist deleted successfully!');
        loadPlaylistsForManagement();
        loadPlaylists();

    } catch (error) {
        alert('Error deleting playlist: ' + error.message);
    }
}

// Remove track from playlist
async function removeTrackFromPlaylist(playlistId, trackUri, index) {
    if (!confirm('Remove this track from the playlist?')) {
        return;
    }

    try {
        const response = await fetch(`/api/playlist/${playlistId}/tracks`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({track_uri: trackUri})
        });

        if (!response.ok) {
            throw new Error('Failed to remove track');
        }

        alert('Track removed successfully!');
        viewPlaylistDetails(playlistId);

    } catch (error) {
        alert('Error removing track: ' + error.message);
    }
}

// Utility function to escape HTML (reuse from app.js if needed)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
