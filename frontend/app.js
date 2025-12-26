/**
 * Frontend Logic for AI Peer Matcher & Project Hub v2.0
 * Handles Auth, Matching, Teams, and Projects
 */

import { API_BASE_URL } from './config.js';

// --- Constants ---
const SECTIONS = {
    LANDING: 'landing-section',
    AUTH: 'auth-section',
    CREATE: 'create-section',
    DASHBOARD: 'dashboard-section',
    TEAM: 'team-section'
};

const TABS = {
    FINDER: 'finder-tab',
    PROJECTS: 'projects-tab',
    SETTINGS: 'settings-tab'
};

const SUBJECTS = [
    "Mathematics", "Physics", "Chemistry", "Biology",
    "Computer Science", "Programming", "English Literature",
    "Creative Writing", "History", "Economics",
    "Psychology", "Business", "Statistics", "Art", "Music"
];

// --- State ---
let state = {
    user: null, // { id, name, token }
    currentTab: TABS.FINDER,
    matches: [],
    projects: []
};

// --- DOM Elements ---
const elements = {
    sections: document.querySelectorAll('.section'),
    loadingOverlay: document.getElementById('loading-overlay'),
    loadingText: document.getElementById('loading-text'),

    // Landing
    checkUsnInput: document.getElementById('check-usn'),
    checkIdBtn: document.getElementById('check-id-btn'),
    showSignupLink: document.getElementById('show-signup-link'),

    // Auth
    authTitle: document.getElementById('auth-title'),
    authSubtitle: document.getElementById('auth-subtitle'),
    authUserInfo: document.getElementById('auth-user-info'),
    authUserName: document.getElementById('auth-user-name'),
    authPasswordInput: document.getElementById('auth-password'),
    authSubmitBtn: document.getElementById('auth-submit-btn'),
    authBackBtn: document.getElementById('auth-back-btn'),

    // Profile
    profileForm: document.getElementById('profile-form'),
    strengthsGrid: document.getElementById('strengths-grid'),
    weaknessesGrid: document.getElementById('weaknesses-grid'),

    // Dashboard
    tabs: document.querySelectorAll('.tab-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    logoutBtn: document.getElementById('logout-btn'),
    matchesContainer: document.getElementById('matches-container'),
    projectsContainer: document.getElementById('projects-container'),

    // Team
    formTeamBtn: document.getElementById('form-team-btn'),
    teamSection: document.getElementById('team-section'),
    teamContainer: document.getElementById('team-container'),
    teamBackBtn: document.getElementById('team-back-btn'),

    closeProjectModal: document.getElementById('close-project-modal'),

    // Projects
    createProjectBtn: document.getElementById('create-project-btn'),
    projectModal: document.getElementById('project-modal'),
    projectForm: document.getElementById('project-form'),
    projectFilter: document.getElementById('project-filter'),

    // Settings / Edit Profile
    editProfileForm: document.getElementById('edit-profile-form'),
    editNameInput: document.getElementById('edit-name'),
    editStrengthsGrid: document.getElementById('edit-strengths-grid'),
    editWeaknessesGrid: document.getElementById('edit-weaknesses-grid'),
    editStrengthsOther: document.getElementById('edit-strengths-other'),
    editWeaknessesOther: document.getElementById('edit-weaknesses-other')
};

// --- Initialization ---

function init() {
    populateGrids();
    setupEventListeners();
    checkAutoLogin();
    App.startPolling();
}

function populateGrids() {
    const createItem = (val, type) => `
        <label class="checkbox-item">
            <input type="checkbox" name="${type}" value="${val}">
            <span>${val}</span>
        </label>
    `;

    if (elements.strengthsGrid) {
        elements.strengthsGrid.innerHTML = SUBJECTS.map(s => createItem(s, 'strength')).join('');
    }
    if (elements.weaknessesGrid) {
        elements.weaknessesGrid.innerHTML = SUBJECTS.map(s => createItem(s, 'weakness')).join('');
    }

    // Also for edit grids
    if (elements.editStrengthsGrid) {
        elements.editStrengthsGrid.innerHTML = SUBJECTS.map(s => createItem(s, 'edit-strength')).join('');
    }
    if (elements.editWeaknessesGrid) {
        elements.editWeaknessesGrid.innerHTML = SUBJECTS.map(s => createItem(s, 'edit-weakness')).join('');
    }
}

// --- API Helpers ---

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('token');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, { ...options, headers });
        const data = await response.json();

        if (!response.ok) {
            let errorMsg = 'Something went wrong';
            if (data && data.detail) {
                if (typeof data.detail === 'string') {
                    errorMsg = data.detail;
                } else if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
                } else if (typeof data.detail === 'object') {
                    errorMsg = JSON.stringify(data.detail);
                }
            }
            throw new Error(errorMsg);
        }

        return data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

// --- Logic Wrapper ---

const App = {
    showLoading(msg) {
        elements.loadingText.textContent = msg;
        elements.loadingOverlay.classList.add('active');
    },

    hideLoading() {
        elements.loadingOverlay.classList.remove('active');
    },

    // --- Status Polling Logic ---
    async checkBackendStatus() {
        const dot = document.querySelector('.status-dot');
        const text = document.querySelector('.status-text');
        const indicator = document.getElementById('backend-status');

        try {
            // Using a simple fetch with a short timeout to check connectivity
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);

            const response = await fetch(API_BASE_URL + '/', { signal: controller.signal });
            clearTimeout(timeoutId);

            if (response.ok) {
                indicator.className = 'status-indicator online';
                text.textContent = 'Server: Online';
            } else {
                indicator.className = 'status-indicator offline';
                text.textContent = 'Server: Starting...';
            }
        } catch (e) {
            indicator.className = 'status-indicator offline';
            text.textContent = 'Server: Offline';
        }
    },

    startPolling() {
        this.checkBackendStatus();
        setInterval(() => this.checkBackendStatus(), 15000);
    },

    showError(msg, container = null) {
        const err = document.createElement('div');
        err.className = 'error-message';
        err.textContent = msg;

        const target = container || document.querySelector('.section.active .auth-card') || document.body;
        target.prepend(err);
        setTimeout(() => err.remove(), 4000);
    },

    switchSection(sectionId) {
        elements.sections.forEach(s => s.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');
    },

    switchTab(tabId) {
        elements.tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tabId));
        elements.tabPanes.forEach(p => p.classList.toggle('active', p.id === tabId));
        state.currentTab = tabId;

        if (tabId === TABS.FINDER) this.loadMatches();
        else if (tabId === TABS.PROJECTS) this.loadProjects();
        else if (tabId === TABS.SETTINGS) this.loadCurrentProfile();
    },

    async checkId() {
        const id = elements.checkUsnInput.value.trim();
        if (!id) return this.showError("Please enter a Student ID");

        this.showLoading("Checking records...");
        try {
            const result = await apiRequest(`/check-id/${encodeURIComponent(id)}`);
            if (result.exists) {
                // Prepare Login
                state.user = { id, name: result.name };
                elements.authTitle.textContent = "Welcome Back";
                elements.authSubtitle.textContent = "Enter your password to continue";
                elements.authUserName.textContent = result.name;
                elements.authUserInfo.style.display = 'flex';
                elements.authSubmitBtn.querySelector('.btn-text').textContent = "Log In";
                this.switchSection(SECTIONS.AUTH);
            } else {
                this.showError(`ID ${id} not found. Please create a profile first.`);
            }
        } catch (e) {
            this.showError(e.message);
        } finally {
            this.hideLoading();
        }
    },

    async login(password) {
        this.showLoading("Authenticating...");
        try {
            const response = await apiRequest('/login', {
                method: 'POST',
                body: JSON.stringify({ id: state.user.id, password })
            });

            localStorage.setItem('token', response.access_token);
            localStorage.setItem('userId', state.user.id);
            localStorage.setItem('userName', state.user.name);

            this.onLoginSuccess();
        } catch (e) {
            this.showError("Invalid password. Please try again.");
        } finally {
            this.hideLoading();
        }
    },

    onLoginSuccess() {
        this.switchSection(SECTIONS.DASHBOARD);
        this.switchTab(TABS.FINDER);
    },

    async loadMatches() {
        const userId = localStorage.getItem('userId');
        try {
            const data = await apiRequest(`/match/${encodeURIComponent(userId)}?top_k=5`);
            this.renderMatches(data.matches);
        } catch (e) {
            this.showError("Failed to load matches");
        }
    },

    renderMatches(matches) {
        elements.matchesContainer.innerHTML = matches.length ? '' : '<p class="empty-state">No matches found yet.</p>';
        matches.forEach(m => {
            const card = document.createElement('div');
            card.className = 'match-card';
            const score = Math.round(m.score * 100);
            card.innerHTML = `
                <div class="match-header">
                    <div class="match-info">
                        <h3>${m.name}</h3>
                        <p class="match-id">USN: ${m.student_id}</p>
                    </div>
                    <div class="match-score">
                        <div class="score-label">Compatibility</div>
                        <div class="score-value">${score}%</div>
                    </div>
                </div>
                <div class="match-details">
                    <div class="detail-item"><strong>Strengths:</strong> ${m.strengths}</div>
                    <div class="detail-item"><strong>Needs:</strong> ${m.weaknesses}</div>
                </div>
            `;
            elements.matchesContainer.appendChild(card);
        });
    },

    async formTeam() {
        const userId = localStorage.getItem('userId');
        this.showLoading("Analyzing team dynamics...");
        try {
            const data = await apiRequest(`/match/team/${encodeURIComponent(userId)}`);
            this.renderTeam(data.team, data.total_score);
            this.switchSection(SECTIONS.TEAM);
        } catch (e) {
            this.showError(e.message);
        } finally {
            this.hideLoading();
        }
    },

    renderTeam(members, totalScore) {
        elements.teamContainer.innerHTML = '';
        members.forEach(m => {
            const card = document.createElement('div');
            card.className = 'match-card';
            card.innerHTML = `
                <h3>${m.name}</h3>
                <p class="match-id">${m.id}</p>
                <div class="detail-item" style="font-size: 0.8rem">
                    <strong>Roles:</strong> ${m.strengths}
                </div>
            `;
            elements.teamContainer.appendChild(card);
        });
    },

    async loadProjects() {
        try {
            const data = await apiRequest('/projects');
            state.projects = data.projects || [];
            this.renderProjects(state.projects);
        } catch (e) {
            console.error(e);
        }
    },

    renderProjects(projects) {
        const filter = elements.projectFilter?.value.toLowerCase() || '';
        const filtered = projects.filter(p => {
            if (!filter) return true;
            const tags = (p.tags || []).join(',').toLowerCase();
            return tags.includes(filter) || p.title.toLowerCase().includes(filter);
        });

        elements.projectsContainer.innerHTML = filtered.length ? '' : '<p class="empty-state">No matching projects found.</p>';

        filtered.forEach(p => {
            const card = document.createElement('div');
            card.className = 'project-card';
            const relevance = p.relevance_score ? Math.round(p.relevance_score * 100) : null;
            const isCreator = p.creator_id === localStorage.getItem('userId');

            card.innerHTML = `
                <div class="project-header">
                    <div style="flex: 1">
                        <h3 style="display: flex; align-items: center; gap: 10px;">
                            ${p.title}
                            ${isCreator ? `<span class="delete-project-btn" title="Delete Project" style="cursor: pointer; color: var(--error); font-size: 1rem;">🗑️</span>` : ''}
                        </h3>
                        ${relevance ? `<span class="relevance-badge">${relevance}% Match</span>` : ''}
                    </div>
                </div>
                <p class="project-description">${p.description}</p>
                <div class="project-stack">
                    ${(p.stack || '').split(',').map(s => `<span class="tag">${s.trim()}</span>`).join('')}
                </div>
                ${p.tags && p.tags.length ? `
                <div class="project-tags" style="margin-top: 5px; display: flex; gap: 5px; flex-wrap: wrap;">
                    ${p.tags.map(t => `<span class="tag" style="background: rgba(99, 102, 241, 0.1); border-color: var(--accent-primary); font-size: 0.7rem;">${t}</span>`).join('')}
                </div>` : ''}
                <div class="project-footer">
                    <span class="project-creator">By ${p.creator_name}</span>
                    <button class="vote-btn ${p.voted_by.includes(localStorage.getItem('userId')) ? 'active' : ''}" data-id="${p.id}">
                        <span>👍</span> <span>${p.votes}</span>
                    </button>
                </div>
            `;

            const voteBtn = card.querySelector('.vote-btn');
            voteBtn.onclick = () => this.voteProject(p.id);

            if (isCreator) {
                const delBtn = card.querySelector('.delete-project-btn');
                delBtn.onclick = (e) => {
                    e.stopPropagation();
                    if (confirm("Delete this project idea?")) {
                        this.deleteProject(p.id);
                    }
                };
            }

            elements.projectsContainer.appendChild(card);
        });
    },

    async deleteProject(projectId) {
        try {
            await apiRequest(`/projects/${projectId}`, { method: 'DELETE' });
            this.loadProjects();
        } catch (e) {
            this.showError(e.message);
        }
    },

    async voteProject(projectId) {
        try {
            await apiRequest(`/projects/${projectId}/vote`, { method: 'POST' });
            this.loadProjects();
        } catch (e) {
            this.showError(e.message);
        }
    },

    async handleProfileSubmit(e) {
        e.preventDefault();
        const fd = new FormData(elements.profileForm);

        // Collect checkboxes
        const getCheckboxes = (name) => Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(c => c.value);
        const strengths = getCheckboxes('strength');
        const weaknesses = getCheckboxes('weakness');

        const otherStrengths = document.getElementById('strengths-other').value.trim();
        if (otherStrengths) strengths.push(...otherStrengths.split(',').map(s => s.trim()));

        const otherWeaknesses = document.getElementById('weaknesses-other').value.trim();
        if (otherWeaknesses) weaknesses.push(...otherWeaknesses.split(',').map(s => s.trim()));

        const profileData = {
            id: fd.get('id').trim(),
            name: fd.get('name').trim(),
            strengths: strengths.join(', '),
            weaknesses: weaknesses.join(', '),
            preferences: "",
            description: ""
        };

        const password = document.getElementById('new-password').value;

        this.showLoading("Creating profile...");
        try {
            // 1. Create Profile
            await apiRequest('/profiles', { method: 'POST', body: JSON.stringify(profileData) });
            // 2. Signup (Create User)
            await apiRequest('/signup', { method: 'POST', body: JSON.stringify({ id: profileData.id, password }) });
            // 3. Login
            state.user = { id: profileData.id, name: profileData.name };
            await this.login(password);
        } finally {
            this.hideLoading();
        }
    },

    async changePassword(e) {
        e.preventDefault();
        const oldPass = document.getElementById('old-password').value;
        const newPass = document.getElementById('change-new-password').value;
        const confirmPass = document.getElementById('confirm-new-password').value;

        if (newPass.length < 8) {
            return this.showError("New password must be at least 8 characters");
        }

        if (newPass !== confirmPass) {
            return this.showError("New passwords do not match");
        }

        this.showLoading("Updating password...");
        try {
            await apiRequest('/change-password', {
                method: 'POST',
                body: JSON.stringify({ old_password: oldPass, new_password: newPass })
            });
            alert("Password updated successfully!");
            document.getElementById('change-password-form').reset();
            this.switchTab(TABS.FINDER);
        } catch (e) {
            this.showError(e.message);
        } finally {
            this.hideLoading();
        }
    },

    async loadCurrentProfile() {
        const userId = localStorage.getItem('userId');
        this.showLoading("Loading your profile...");
        try {
            const profile = await apiRequest(`/profiles/${encodeURIComponent(userId)}`);

            // Fill Name
            elements.editNameInput.value = profile.name;

            // Fill Checkboxes
            const strengths = profile.strengths.split(',').map(s => s.trim());
            const weaknesses = profile.weaknesses.split(',').map(s => s.trim());

            // Helper to check boxes
            const checkBoxes = (gridId, list, otherInputId) => {
                const checkboxes = document.querySelectorAll(`#${gridId} input[type="checkbox"]`);
                const matched = [];
                checkboxes.forEach(cb => {
                    if (list.includes(cb.value)) {
                        cb.checked = true;
                        matched.push(cb.value);
                    } else {
                        cb.checked = false;
                    }
                });

                // Find items in list not in checkboxes
                const others = list.filter(item => !matched.includes(item));
                document.getElementById(otherInputId).value = others.join(', ');
            };

            checkBoxes('edit-strengths-grid', strengths, 'edit-strengths-other');
            checkBoxes('edit-weaknesses-grid', weaknesses, 'edit-weaknesses-other');

        } catch (e) {
            this.showError("Failed to load profile details");
        } finally {
            this.hideLoading();
        }
    },

    async updateProfile(e) {
        e.preventDefault();
        const userId = localStorage.getItem('userId');

        // Collect checkboxes
        const getCheckboxes = (gridId) => Array.from(document.querySelectorAll(`#${gridId} input[type="checkbox"]:checked`)).map(c => c.value);
        const strengths = getCheckboxes('edit-strengths-grid');
        const weaknesses = getCheckboxes('edit-weaknesses-grid');

        const otherStrengths = elements.editStrengthsOther.value.trim();
        if (otherStrengths) strengths.push(...otherStrengths.split(',').map(s => s.trim()));

        const otherWeaknesses = elements.editWeaknessesOther.value.trim();
        if (otherWeaknesses) weaknesses.push(...otherWeaknesses.split(',').map(s => s.trim()));

        const profileData = {
            id: userId,
            name: elements.editNameInput.value.trim(),
            strengths: strengths.join(', '),
            weaknesses: weaknesses.join(', '),
            preferences: "",
            description: ""
        };

        this.showLoading("Updating profile...");
        try {
            await apiRequest(`/profiles/${encodeURIComponent(userId)}`, {
                method: 'PUT',
                body: JSON.stringify(profileData)
            });
            alert("Profile updated successfully!");
            this.switchTab(TABS.FINDER);
        } catch (e) {
            this.showError(e.message);
        } finally {
            this.hideLoading();
        }
    }
};

// --- Event Listeners ---

function setupEventListeners() {
    // Flow
    elements.checkIdBtn.onclick = () => App.checkId();
    elements.showSignupLink.onclick = (e) => { e.preventDefault(); App.switchSection(SECTIONS.CREATE); };
    elements.authBackBtn.onclick = () => App.switchSection(SECTIONS.LANDING);

    elements.authSubmitBtn.onclick = () => {
        const pass = elements.authPasswordInput.value;
        if (pass) App.login(pass);
    };

    // Profile
    elements.profileForm.onsubmit = (e) => App.handleProfileSubmit(e);

    // Auth back button in create profile
    const profileBack = document.createElement('button');
    profileBack.className = 'btn btn-link';
    profileBack.textContent = "← Back to Login";
    profileBack.onclick = (e) => { e.preventDefault(); App.switchSection(SECTIONS.LANDING); };
    elements.profileForm.appendChild(profileBack);

    // Tabs
    elements.tabs.forEach(btn => {
        btn.onclick = () => App.switchTab(btn.dataset.tab);
    });

    // Logout
    elements.logoutBtn.onclick = () => {
        localStorage.clear();
        App.switchSection(SECTIONS.LANDING);
    };

    // Team
    elements.formTeamBtn.onclick = () => App.formTeam();
    elements.teamBackBtn.onclick = () => App.switchSection(SECTIONS.DASHBOARD);

    // Project Modal
    elements.createProjectBtn.onclick = () => elements.projectModal.classList.add('active');
    elements.closeProjectModal.onclick = () => elements.projectModal.classList.remove('active');

    elements.projectForm.onsubmit = async (e) => {
        e.preventDefault();
        const tags = document.getElementById('project-tags').value;
        const body = {
            title: document.getElementById('project-title').value,
            description: document.getElementById('project-desc').value,
            stack: document.getElementById('project-stack').value,
            tags: tags ? tags.split(',').map(t => t.trim()) : []
        };

        App.showLoading("Posting project...");
        try {
            await apiRequest('/projects', { method: 'POST', body: JSON.stringify(body) });
            elements.projectModal.classList.remove('active');
            elements.projectForm.reset();
            App.loadProjects();
        } catch (e) {
            App.showError(e.message);
        } finally {
            App.hideLoading();
        }
    };

    // Filter listener
    if (elements.projectFilter) {
        elements.projectFilter.oninput = () => App.renderProjects(state.projects);
    }

    // Settings
    const changePassForm = document.getElementById('change-password-form');
    if (changePassForm) {
        changePassForm.onsubmit = (e) => App.changePassword(e);
    }

    if (elements.editProfileForm) {
        elements.editProfileForm.onsubmit = (e) => App.updateProfile(e);
    }
}

function checkAutoLogin() {
    const token = localStorage.getItem('token');
    if (token) {
        App.onLoginSuccess();
    }
}

// Start
init();
