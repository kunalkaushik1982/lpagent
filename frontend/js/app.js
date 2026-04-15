// File: c:/Users/work/Documents/lp-agent/frontend/js/app.js
// Purpose: Main frontend logic and API interaction.

const API_BASE_URL = "http://localhost:8000/api/v1";

// ============================================================================
// Utility Functions
// ============================================================================

function showAlert(message, type = 'error') {
    const container = document.getElementById('alertContainer');
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    container.innerHTML = '';
    container.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}

function saveToStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function getFromStorage(key) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
}

function clearStorage() {
    localStorage.clear();
}

// ============================================================================
// API Functions
// ============================================================================

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
}

// ============================================================================
// Authentication Page (index.html)
// ============================================================================

if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', () => {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const showRegisterLink = document.getElementById('showRegister');
        const showLoginLink = document.getElementById('showLogin');
        const backToLogin = document.getElementById('backToLogin');
        
        // Toggle between login and register
        showRegisterLink?.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.classList.add('hidden');
            registerForm.classList.remove('hidden');
            backToLogin.classList.remove('hidden');
            showRegisterLink.parentElement.classList.add('hidden');
        });
        
        showLoginLink?.addEventListener('click', (e) => {
            e.preventDefault();
            registerForm.classList.add('hidden');
            loginForm.classList.remove('hidden');
            backToLogin.classList.add('hidden');
            showRegisterLink.parentElement.classList.remove('hidden');
        });
        
        // Handle Login
        loginForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            try {
                const result = await apiCall('/login', 'POST', { username, password });
                saveToStorage('user', result);
                window.location.href = 'dashboard.html';
            } catch (error) {
                showAlert(error.message);
            }
        });
        
        // Handle Registration
        registerForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const userData = {
                username: document.getElementById('regUsername').value,
                password: document.getElementById('regPassword').value,
                current_role: document.getElementById('currentRole').value,
                target_role: document.getElementById('targetRole').value,
                experience_years: parseInt(document.getElementById('experience').value) || 0
            };
            
            try {
                await apiCall('/register', 'POST', userData);
                showAlert('Account created! Please login.', 'success');
                showLoginLink.click(); // Switch to login form
            } catch (error) {
                showAlert(error.message);
            }
        });
    });
}

// ============================================================================
// Dashboard Page (dashboard.html)
// ============================================================================

if (window.location.pathname.includes('dashboard.html')) {
    let currentUser = null;
    let currentPlan = null;
    
    document.addEventListener('DOMContentLoaded', async () => {
        // Check authentication
        const user = getFromStorage('user');
        if (!user || !user.user_id) {
            window.location.href = 'index.html';
            return;
        }
        
        currentUser = user;
        document.getElementById('userNameDisplay').textContent = user.username;
        
        // Load user profile
        await loadUserProfile();
        
        // Try to load existing plan
        await loadLearningPlan();
        
        // Event listeners
        document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
        document.getElementById('editProfileBtn')?.addEventListener('click', showEditProfile);
        document.getElementById('cancelEditBtn')?.addEventListener('click', hideEditProfile);
        document.getElementById('profileForm')?.addEventListener('submit', handleProfileUpdate);
        document.getElementById('generatePlanBtn')?.addEventListener('click', handleGeneratePlan);
    });
    
    function handleLogout() {
        clearStorage();
        window.location.href = 'index.html';
    }
    
    async function loadUserProfile() {
        try {
            const profile = await apiCall(`/users/${currentUser.user_id}`);
            
            document.getElementById('displayCurrentRole').textContent = profile.current_role || '-';
            document.getElementById('displayTargetRole').textContent = profile.target_role || '-';
            document.getElementById('displayExperience').textContent = profile.experience_years 
                ? `${profile.experience_years} years` 
                : '-';
            
            // Display skills
            const skillsText = profile.skills && profile.skills.length > 0 
                ? profile.skills.join(', ') 
                : '-';
            document.getElementById('displaySkills').textContent = skillsText;
            
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    }
    
    function showEditProfile() {
        // Populate form with current values
        document.getElementById('editCurrentRole').value = 
            document.getElementById('displayCurrentRole').textContent !== '-' 
                ? document.getElementById('displayCurrentRole').textContent 
                : '';
        document.getElementById('editTargetRole').value = 
            document.getElementById('displayTargetRole').textContent !== '-' 
                ? document.getElementById('displayTargetRole').textContent 
                : '';
        const expText = document.getElementById('displayExperience').textContent;
        document.getElementById('editExperience').value = 
            expText !== '-' ? parseInt(expText) : 0;
        
        document.getElementById('profileSection').classList.add('hidden');
        document.getElementById('editProfileSection').classList.remove('hidden');
    }
    
    function hideEditProfile() {
        document.getElementById('editProfileSection').classList.add('hidden');
        document.getElementById('profileSection').classList.remove('hidden');
    }
    
    async function handleProfileUpdate(e) {
        e.preventDefault();
        
        const skills = document.getElementById('editSkills').value
            .split(',')
            .map(s => s.trim())
            .filter(s => s.length > 0);
        
        const updateData = {
            current_role: document.getElementById('editCurrentRole').value,
            target_role: document.getElementById('editTargetRole').value,
            experience_years: parseInt(document.getElementById('editExperience').value),
            skills: skills.length > 0 ? skills : null
        };
        
        try {
            await apiCall(`/users/${currentUser.user_id}/profile`, 'PUT', updateData);
            await loadUserProfile();
            hideEditProfile();
            showAlert('Profile updated successfully!', 'success');
        } catch (error) {
            showAlert('Failed to update profile: ' + error.message, 'error');
        }
    }
    
    async function handleGeneratePlan() {
        const btn = document.getElementById('generatePlanBtn');
        btn.disabled = true;
        btn.textContent = 'Generating...';
        
        try {
            const plan = await apiCall('/plans/generate', 'POST', { 
                user_id: currentUser.user_id 
            });
            currentPlan = plan;
            currentUser.last_plan_id = plan.plan_id;
            saveToStorage('user', currentUser);
            renderTimeline(plan);
            btn.textContent = 'Regenerate Plan';
        } catch (error) {
            showAlert('Failed to generate plan: ' + error.message, 'error');
            btn.textContent = 'Generate Plan';
        } finally {
            btn.disabled = false;
        }
    }
    
    async function loadLearningPlan() {
        try {
            const plan = await apiCall(`/plans/user/${currentUser.user_id}`);
            currentPlan = plan;
            currentUser.last_plan_id = plan.plan_id;
            saveToStorage('user', currentUser);
            renderTimeline(plan);
        } catch (error) {
            // No plan exists yet, that's okay
            console.log('No existing plan found');
        }
    }
    
    function renderTimeline(plan) {
        const container = document.getElementById('timelineContainer');
        const statsDiv = document.getElementById('planStats');
        
        if (!plan || !plan.items || plan.items.length === 0) {
            statsDiv.classList.add('hidden');
            container.innerHTML = '';
            
            if (plan && plan.warning) {
                const warningDiv = document.createElement('div');
                warningDiv.className = 'alert alert-error';
                warningDiv.style.marginBottom = '20px';
                warningDiv.innerHTML = `⚠️ ${plan.warning}`;
                container.appendChild(warningDiv);
            }
            
            container.innerHTML += '<p style="text-align: center; color: #6b7280; padding: 40px;">No courses in plan. If your target role has no matching courses, try a different role or update your skill profile.</p>';
            return;
        }
        
        // Update stats
        document.getElementById('totalCourses').textContent = plan.items.length;
        document.getElementById('totalHours').textContent = plan.total_duration_hours;
        const completed = plan.items.filter(item => item.status === 'completed').length;
        document.getElementById('completedCourses').textContent = completed;
        statsDiv.classList.remove('hidden');
        
        // Render timeline
        container.innerHTML = '';
        
        // Show warning if present
        if (plan.warning) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-error';
            warningDiv.style.marginBottom = '20px';
            warningDiv.innerHTML = `⚠️ ${plan.warning}`;
            container.appendChild(warningDiv);
        }
        
        plan.items.forEach(item => {
            const timelineItem = document.createElement('div');
            timelineItem.className = `timeline-item ${item.status === 'completed' ? 'completed' : ''}`;
            timelineItem.style.cursor = 'pointer';
            timelineItem.style.transition = 'all 0.2s ease';
            
            const difficultyClass = item.difficulty_level 
                ? `badge-${item.difficulty_level.toLowerCase()}` 
                : 'badge-beginner';
            
            timelineItem.innerHTML = `
                <div class="timeline-number">${item.sequence_order}</div>
                <div class="timeline-content">
                    <h3 style="margin-bottom: 8px;">${item.course_title}</h3>
                    <div class="timeline-meta">
                        <span class="badge ${difficultyClass}">${item.difficulty_level || 'N/A'}</span>
                        <span style="color: #6b7280; font-size: 14px;">⏱️ ${item.duration_hours || 0} hours</span>
                        <span style="color: #6b7280; font-size: 14px;">📊 ${item.status}</span>
                    </div>
                    ${item.explanation ? `<p class="timeline-description">${item.explanation}</p>` : ''}
                    <p style="color: #3b82f6; font-size: 12px; margin-top: 8px; margin-bottom: 0;">Click to view course details →</p>
                </div>
            `;
            
            // Add hover effect
            timelineItem.addEventListener('mouseenter', () => {
                timelineItem.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                timelineItem.style.transform = 'translateY(-2px)';
            });
            
            timelineItem.addEventListener('mouseleave', () => {
                timelineItem.style.boxShadow = 'none';
                timelineItem.style.transform = 'translateY(0)';
            });
            
            // Add click handler to open course details
            timelineItem.addEventListener('click', () => {
                const params = new URLSearchParams({
                    courseId: item.course_id,
                    planItemId: item.id,
                    planId: plan.plan_id,
                    from: 'dashboard.html'
                });
                window.location.href = `course-detail.html?${params.toString()}`;
            });
            
            container.appendChild(timelineItem);
        });
    }
}
