// Import and initialize CF module
import { initStarRating, submitRating, loadCollaborationStats } from './cf_module.js';

// Initialize star rating on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing CF module...');
    initStarRating();

    // Set up submit button
    const submitBtn = document.getElementById('submit-rating-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            submitRating();
        });
    }

    // Load stats when ratings tab is shown
    const ratingsTabs = document.querySelectorAll('[data-tab="ratings-tab"]');
    ratingsTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            setTimeout(loadCollaborationStats, 100);
        });
    });
});
