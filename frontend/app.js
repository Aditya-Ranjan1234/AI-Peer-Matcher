/**
 * Frontend Logic for AI-Powered Peer Learning Matcher
 * Handles form submission, API calls, and UI updates
 */

// Import configuration
import { API_BASE_URL } from './config.js';

// DOM Elements
const createSection = document.getElementById('create-section');
const matchesSection = document.getElementById('matches-section');
const profileForm = document.getElementById('profile-form');
const matchesContainer = document.getElementById('matches-container');
const matchSubtitle = document.getElementById('match-subtitle');
const backBtn = document.getElementById('back-btn');
const loadingOverlay = document.getElementById('loading-overlay');

// State
let currentStudentId = null;
let currentStudentName = null;

/**
 * Show loading overlay
 */
function showLoading(message = 'Processing...') {
    loadingOverlay.querySelector('p').textContent = message;
    loadingOverlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    profileForm.insertBefore(errorDiv, profileForm.firstChild);

    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Switch between sections
 */
function showSection(section) {
    createSection.classList.remove('active');
    matchesSection.classList.remove('active');
    section.classList.add('active');
}

/**
 * Create a new student profile
 */
async function createProfile(profileData) {
    const response = await fetch(`${API_BASE_URL}/profiles`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create profile');
    }

    return await response.json();
}

/**
 * Get matches for a student
 */
async function getMatches(studentId, topK = 3) {
    const response = await fetch(`${API_BASE_URL}/match/${studentId}?top_k=${topK}`);

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get matches');
    }

    return await response.json();
}

/**
 * Render match cards
 */
function renderMatches(matchData) {
    matchesContainer.innerHTML = '';

    if (!matchData.matches || matchData.matches.length === 0) {
        matchesContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h3>No matches found yet</h3>
                <p>Add more student profiles to find matches!</p>
            </div>
        `;
        return;
    }

    // Update subtitle
    matchSubtitle.textContent = `Found ${matchData.total_matches} perfect match${matchData.total_matches !== 1 ? 'es' : ''} for ${matchData.student_name}`;

    // Create match cards
    matchData.matches.forEach((match, index) => {
        const matchCard = document.createElement('div');
        matchCard.className = 'match-card';
        matchCard.style.animationDelay = `${index * 0.1}s`;

        const scorePercentage = Math.round(match.score * 100);
        const scoreColor = match.score > 0.7 ? 'var(--success)' :
            match.score > 0.4 ? 'var(--warning)' :
                'var(--error)';

        matchCard.innerHTML = `
            <div class="match-header">
                <div class="match-info">
                    <h3>${match.name}</h3>
                    <p class="match-id">ID: ${match.student_id}</p>
                </div>
                <div class="match-score">
                    <div class="score-label">Match Score</div>
                    <div class="score-value" style="color: ${scoreColor}">${scorePercentage}%</div>
                </div>
            </div>
            <div class="match-details">
                <div class="detail-item">
                    <div class="detail-label">💪 Their Strengths (Can help you with)</div>
                    <div class="detail-value">${match.strengths}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">📚 They Need Help With (You can help them)</div>
                    <div class="detail-value">${match.weaknesses}</div>
                </div>
            </div>
        `;

        matchesContainer.appendChild(matchCard);
    });
}

/**
 * Handle form submission
 */
profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous errors
    const existingError = profileForm.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Get basic form data
    const formData = new FormData(profileForm);

    // Collect checked strengths
    const strengthCheckboxes = document.querySelectorAll('input[name="strength"]:checked');
    const strengthValues = Array.from(strengthCheckboxes).map(cb => cb.value);

    // Add custom strengths from text input
    const strengthsOther = document.getElementById('strengths-other').value.trim();
    if (strengthsOther) {
        const customStrengths = strengthsOther.split(',').map(s => s.trim()).filter(s => s);
        strengthValues.push(...customStrengths);
    }

    // Collect checked weaknesses
    const weaknessCheckboxes = document.querySelectorAll('input[name="weakness"]:checked');
    const weaknessValues = Array.from(weaknessCheckboxes).map(cb => cb.value);

    // Add custom weaknesses from text input
    const weaknessesOther = document.getElementById('weaknesses-other').value.trim();
    if (weaknessesOther) {
        const customWeaknesses = weaknessesOther.split(',').map(s => s.trim()).filter(s => s);
        weaknessValues.push(...customWeaknesses);
    }

    // Collect checked preferences
    const preferenceCheckboxes = document.querySelectorAll('input[name="preference"]:checked');
    const preferenceValues = Array.from(preferenceCheckboxes).map(cb => cb.value);

    // Add custom preferences from text input
    const preferencesOther = document.getElementById('preferences-other').value.trim();
    if (preferencesOther) {
        const customPreferences = preferencesOther.split(',').map(s => s.trim()).filter(s => s);
        preferenceValues.push(...customPreferences);
    }

    // Build profile data object
    const profileData = {
        id: formData.get('id').trim(),
        name: formData.get('name').trim(),
        strengths: strengthValues.join(', '),
        weaknesses: weaknessValues.join(', '),
        preferences: preferenceValues.join(', '),
        description: formData.get('description').trim()
    };

    // Validate required fields
    if (!profileData.id || !profileData.name) {
        showError('Please fill in Student ID and Name');
        return;
    }

    if (strengthValues.length === 0) {
        showError('Please select at least one strength or add custom strengths');
        return;
    }

    if (weaknessValues.length === 0) {
        backBtn.addEventListener('click', () => {
            showSection(createSection);
        });

        /**
         * Check API health on load
         */
        async function checkAPIHealth() {
            try {
                const response = await fetch(`${API_BASE_URL}/`);
                if (response.ok) {
                    console.log('✅ API is online and ready');
                }
            } catch (error) {
                console.warn('⚠️ API is not reachable. Make sure the backend is running.');
                showError('Backend API is not running. Please start the server first.');
            }
        }

        // Initialize
        checkAPIHealth();
