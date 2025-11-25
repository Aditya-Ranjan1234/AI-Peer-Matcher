/**
 * Configuration for API endpoint
 * Update this after deploying the backend to Vercel
 */

// Default to localhost for development
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://your-backend-url.vercel.app'; // Replace with actual Vercel backend URL after deployment

export { API_BASE_URL };
