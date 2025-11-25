/**
 * Configuration for API endpoint
 * Update this after deploying the backend to Vercel
 */

// Default to localhost for development
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://ai-peer-matcher.onrender.com'; // Your Render backend URL

export { API_BASE_URL };
