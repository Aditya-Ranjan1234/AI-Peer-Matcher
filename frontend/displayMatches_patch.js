/**
 * PASTE THIS CODE into your existing app.js file
 * Replace the displayMatches function with this version
 */

// Updated displayMatches function with full CF support
async function displayMatches(data) {
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
            <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); color: #a78bfa; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🤖</span>
                <span>Using Collaborative Filtering with ${data.total_collaborations} collaboration ratings</span>
            </div>
        `;
    }

    // Render each match
    data.matches.forEach((match, index) => {
        // Handle both old and new API response formats
        const hybridScore = match.hybrid_score !== undefined ? match.hybrid_score : match.score;
        const nlpScore = match.nlp_score !== undefined ? match.nlp_score : match.score;
        const graphScore = match.graph_score || 0;
        const cfScore = match.cf_score || 0;

        const hybridPercent = (hybridScore * 100).toFixed(0);
        const nlpPercent = (nlpScore * 100).toFixed(0);
        const graphPercent = (graphScore * 100).toFixed(0);
        const cfPercent = (cfScore * 100).toFixed(0);

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
