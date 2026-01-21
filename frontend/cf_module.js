/**
 * Collaborative Filtering UI Module
 * Handles star ratings, peer feedback submission, and collaboration statistics display
 */

// API Base URL
const API_BASE_URL = 'http://localhost:8000';

/**
 * Initialize star rating interaction
 */
export function initStarRating() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating-value');
    const ratingText = document.getElementById('rating-text');

    const ratingLabels = {
        1: '⭐ Poor',
        2: '⭐⭐ Fair',
        3: '⭐⭐⭐ Good',
        4: '⭐⭐⭐⭐ Very Good',
        5: '⭐⭐⭐⭐⭐ Excellent'
    };

    stars.forEach((star, index) => {
        // Hover effect
        star.addEventListener('mouseenter', () => {
            stars.forEach((s, i) => {
                if (i <= index) {
                    s.classList.add('hovered');
                } else {
                    s.classList.remove('hovered');
                }
            });
        });

        // Click to select
        star.addEventListener('click', () => {
            const rating = parseInt(star.dataset.rating);
            ratingInput.value = rating;

            // Update visual state
            stars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });

            // Update text
            ratingText.textContent = ratingLabels[rating];
            ratingText.style.color = '#ffc107';
        });
    });

    // Remove hover effect when leaving the rating area
    const ratingContainer = document.getElementById('star-rating');
    ratingContainer.addEventListener('mouseleave', () => {
        stars.forEach(s => s.classList.remove('hovered'));
    });
}

/**
 * Submit a collaboration rating
 */
export async function submitRating() {
    const peerID = document.getElementById('peer-to-rate').value.trim();
    const rating = parseFloat(document.getElementById('rating-value').value);
    const context = document.getElementById('project-context').value.trim();
    const feedback = document.getElementById('peer-feedback').value.trim();

    // Validation
    if (!peerID) {
        showNotification('Please enter a student ID to rate', 'error');
        return;
    }

    if (rating === 0) {
        showNotification('Please select a rating', 'error');
        return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
        showNotification('You must be logged in to rate peers', 'error');
        return;
    }

    try {
        showLoading(true, 'Submitting rating...');

        const response = await fetch(`${API_BASE_URL}/collaborations/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                student_id: peerID,
                rating: rating,
                worked_together: true,
                feedback: feedback || null,
                project_context: context || null
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit rating');
        }

        showNotification('Rating submitted successfully! 🎉', 'success');

        // Reset form
        document.getElementById('peer-to-rate').value = '';
        document.getElementById('rating-value').value = '0';
        document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
        document.getElementById('project-context').value = '';
        document.getElementById('peer-feedback').value = '';
        document.getElementById('rating-text').textContent = 'Click to rate';
        document.getElementById('rating-text').style.color = '';

        // Reload stats
        await loadCollaborationStats();

    } catch (error) {
        console.error('Error submitting rating:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Load and display collaboration statistics
 */
export async function loadCollaborationStats() {
    const userID = localStorage.getItem('user_id');
    if (!userID) return;

    try {
        const response = await fetch(`${API_BASE_URL}/collaborations/stats/${userID}`);

        if (!response.ok) {
            throw new Error('Failed to load statistics');
        }

        const stats = await response.json();
        const statsDiv = document.getElementById('collab-stats');

        if (stats.total_collaborations === 0) {
            statsDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">📊 No collaboration history yet</p>
                    <p style="font-size: 0.9rem;">Start rating your peers to build your reputation!</p>
                </div>
            `;
            return;
        }

        let html = '<div class="collab-stats-content">';

        // Total collaborations
        html += `
            <div class="stat-item">
                <span class="stat-label">Total Ratings Received</span>
                <span class="stat-value">${stats.total_collaborations}</span>
            </div>
        `;

        // Average rating
        html += `
            <div class="stat-item">
                <span class="stat-label">Average Rating</span>
                <span class="stat-value">${stats.average_rating.toFixed(1)} / 5.0</span>
            </div>
        `;

        // Top rated peers
        if (stats.top_rated_peers && stats.top_rated_peers.length > 0) {
            html += '<h5 style="margin-top: 1rem; margin-bottom: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">Top Collaborators</h5>';
            html += '<ul class="top-peers-list">';

            stats.top_rated_peers.forEach(peer => {
                html += `
                    <li class="peer-item">
                        <span class="peer-name">${peer.name}</span>
                        <span class="peer-rating">${peer.avg_rating.toFixed(1)} ★</span>
                    </li>
                `;
            });

            html += '</ul>';
        }

        html += '</div>';
        statsDiv.innerHTML = html;

    } catch (error) {
        console.error('Error loading stats:', error);
        const statsDiv = document.getElementById('collab-stats');
        statsDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--error);">
                <p>Failed to load statistics</p>
            </div>
        `;
    }
}

/**
 * Update match display to show all score components including CF
 */
export function displayMatchesWithCF(data) {
    const container = document.getElementById('matches-container');

    if (!data.matches || data.matches.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                <p style="font-size: 1.2rem;">No matches found yet</p>
                <p style="font-size: 0.9rem;">Create more profiles or adjust your criteria</p>
            </div>
        `;
        return;
    }

    let html = '';

    // Add CF info badge if using CF
    if (data.using_collaborative_filtering) {
        html += `
            <div class="cf-info-badge">
                <span class="icon">🤖</span>
                <span>Using Collaborative Filtering with ${data.total_collaborations} collaboration ratings</span>
            </div>
        `;
    }

    // Render each match
    data.matches.forEach((match, index) => {
        const hybridPercent = (match.hybrid_score * 100).toFixed(0);
        const nlpPercent = (match.nlp_score * 100).toFixed(0);
        const graphPercent = (match.graph_score * 100).toFixed(0);
        const cfPercent = (match.cf_score * 100).toFixed(0);

        html += `
            <div class="match-card" style="animation-delay: ${index * 0.1}s;">
                <div class="match-header">
                    <div>
                        <h3>${match.name}</h3>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">${match.student_id}</p>
                    </div>
                    <div class="score-container">
                        <div class="score-item">
                            <span class="score-value hybrid">${hybridPercent}%</span>
                            <span class="score-label">Hybrid</span>
                        </div>
                        <div class="score-item">
                            <span class="score-value nlp">${nlpPercent}%</span>
                            <span class="score-label">AI NLP</span>
                        </div>
                        <div class="score-item">
                            <span class="score-value graph">${graphPercent}%</span>
                            <span class="score-label">Graph</span>
                        </div>
                        <div class="score-item">
                            <span class="score-value cf">${cfPercent}%</span>
                            <span class="score-label">CF</span>
                        </div>
                    </div>
                </div>
                <div class="match-details">
                    <div class="detail-item">
                        <span class="detail-label">Strengths:</span>
                        <p>${match.strengths}</p>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Weaknesses:</span>
                        <p>${match.weaknesses}</p>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notif = document.createElement('div');
    notif.className = type === 'success' ? 'success-message' : 'error-message';
    notif.textContent = message;
    notif.style.position = 'fixed';
    notif.style.top = '80px';
    notif.style.right = '20px';
    notif.style.zIndex = '2000';
    notif.style.maxWidth = '400px';

    document.body.appendChild(notif);

    // Remove after 4 seconds
    setTimeout(() => {
        notif.style.opacity = '0';
        notif.style.transform = 'translateX(400px)';
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

/**
 * Show/hide loading overlay
 */
function showLoading(show, message = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const text = document.getElementById('loading-text');

    if (show) {
        text.textContent = message;
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}
