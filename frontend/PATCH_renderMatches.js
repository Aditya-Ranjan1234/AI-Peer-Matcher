// ============================================
// COPY AND PASTE THIS INTO app.js
// Replace lines 295-335 with this code
// ============================================

    async loadMatches() {
    const userId = localStorage.getItem('userId');
    try {
        const data = await apiRequest(`/match/${encodeURIComponent(userId)}?top_k=5&use_cf=true`);
        this.renderMatches(data);
    } catch (e) {
        this.showError("Failed to load matches");
    }
},

renderMatches(data) {
    const matches = data.matches || [];
    let html = '';

    // Add CF info badge if using CF
    if (data.using_collaborative_filtering) {
        html += `
                <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); color: #a78bfa; padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem;">
                    <span style="font-size: 1.2rem;">🤖</span>
                    <span>Using Collaborative Filtering with ${data.total_collaborations} collaboration ratings</span>
                </div>
            `;
    }

    if (!matches.length) {
        html += '<p class="empty-state">No matches found yet.</p>';
        elements.matchesContainer.innerHTML = html;
        return;
    }

    matches.forEach((m, index) => {
        // Support both old and new API formats
        const hybrid = (m.hybrid_score || m.nlp_score || m.score || 0) * 100;
        const nlp = (m.nlp_score || m.score || 0) * 100;
        const graph = (m.graph_score || 0) * 100;
        const cf = (m.cf_score || 0) * 100;

        html += `
                <div class="match-card" style="animation-delay: ${index * 0.1}s;">
                    <div class="match-header">
                        <div class="match-info">
                            <h3>${m.name}</h3>
                            <p class="match-id">USN: ${m.student_id}</p>
                        </div>
                        <div class="score-container">
                            <div class="score-item">
                                <div class="score-value hybrid">${Math.round(hybrid)}%</div>
                                <div class="score-label">Hybrid</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value nlp">${Math.round(nlp)}%</div>
                                <div class="score-label">AI NLP</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value graph">${Math.round(graph)}%</div>
                                <div class="score-label">Graph</div>
                            </div>
                            <div class="score-item">
                                <div class="score-value cf">${Math.round(cf)}%</div>
                                <div class="score-label">CF</div>
                            </div>
                        </div>
                    </div>
                    <div class="match-details">
                        <div class="detail-item"><strong>Strengths:</strong> ${m.strengths}</div>
                        <div class="detail-item"><strong>Needs:</strong> ${m.weaknesses}</div>
                    </div>
                </div>
            `;
    });

    elements.matchesContainer.innerHTML = html;
},
