// File: c:/Users/work/Documents/lp-agent/frontend/js/course-detail.js
// Purpose: Handle course detail page logic, completion, and certificate export.

import {
    buildCertificateData,
    COMPLETION_THRESHOLD_PERCENT,
    createCompletionStorageKey,
    isEligibleForCompletion,
} from './course-detail-helpers.js';

const API_BASE_URL = "http://localhost:8000/api/v1";
let currentUser = null;
let currentCourse = null;
let videoProgress = 0;
let progressInterval = null;
let currentCompletionRecord = null;

document.addEventListener('DOMContentLoaded', () => {
    initializePage();
});

function showAlert(message, type = 'success') {
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
        const detail = Array.isArray(error.detail)
            ? error.detail.map(item => item.msg || JSON.stringify(item)).join('; ')
            : error.detail;
        throw new Error(detail || 'Request failed');
    }

    return response.json();
}

function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function getPlanContext() {
    const planItemId = getUrlParameter('planItemId');
    const planId = getUrlParameter('planId') || currentUser?.last_plan_id;
    return { planId, planItemId };
}

async function initializePage() {
    currentUser = getFromStorage('user');
    if (!currentUser) {
        window.location.href = 'index.html';
        return;
    }

    document.getElementById('userNameDisplay').textContent = currentUser.username;

    const courseId = getUrlParameter('courseId');
    if (!courseId) {
        showAlert('No course selected', 'error');
        return;
    }

    await loadCourseDetails(courseId);

    document.getElementById('backBtn').addEventListener('click', goBackToPlan);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('markCompleteBtn').addEventListener('click', markCourseComplete);
    document.getElementById('downloadCertificateBtn').addEventListener('click', downloadCertificate);
}

async function loadCourseDetails(courseId) {
    try {
        currentCourse = await apiCall(`/courses/${courseId}`);
        renderCourseDetails();
        loadOrCreateVideo();
        loadProgressFromStorage();
        loadCompletionRecord();
        syncCompletionUI();
    } catch (error) {
        showAlert('Failed to load course details: ' + error.message, 'error');
    }
}

function renderCourseDetails() {
    document.getElementById('courseTitle').textContent = currentCourse.title;
    document.getElementById('courseDescription').textContent = currentCourse.description || 'No description available';

    const difficultyLevel = currentCourse.difficulty_level || 'Beginner';
    const difficultyClass = `badge-${difficultyLevel.toLowerCase()}`;
    document.getElementById('difficultyBadge').className = `badge ${difficultyClass}`;
    document.getElementById('difficultyBadge').textContent = difficultyLevel;

    document.getElementById('duration').textContent = currentCourse.duration_hours || 0;
    document.getElementById('provider').textContent = currentCourse.provider || '-';
    document.getElementById('format').textContent = currentCourse.format || '-';

    const skillsContainer = document.getElementById('skillsTags');
    skillsContainer.innerHTML = '';
    if (currentCourse.skills && currentCourse.skills.length > 0) {
        currentCourse.skills.forEach(skill => {
            const tag = document.createElement('div');
            tag.className = 'skill-tag';
            tag.textContent = skill;
            skillsContainer.appendChild(tag);
        });
    } else {
        skillsContainer.innerHTML = '<span style="color: #6b7280; font-size: 14px;">No skills listed</span>';
    }

    const prereqContainer = document.getElementById('prerequisitesList');
    prereqContainer.innerHTML = '';
    if (currentCourse.prerequisites && currentCourse.prerequisites.length > 0) {
        const list = document.createElement('ul');
        list.style.margin = '0';
        list.style.paddingLeft = '20px';
        currentCourse.prerequisites.forEach(prereq => {
            const item = document.createElement('li');
            item.textContent = prereq;
            list.appendChild(item);
        });
        prereqContainer.appendChild(list);
    } else {
        prereqContainer.textContent = 'None';
    }
}

function loadOrCreateVideo() {
    const videoContainer = document.getElementById('videoContainer');
    videoContainer.innerHTML = '';

    if (currentCourse.youtube_url) {
        const iframe = document.createElement('iframe');
        iframe.src = currentCourse.youtube_url + '?enablejsapi=1';
        iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
        iframe.allowFullscreen = true;
        videoContainer.appendChild(iframe);

        if (currentCourse.youtube_url.includes('youtube.com/embed/')) {
            setupVideoTracking();
        }
    } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'video-placeholder';
        placeholder.textContent = 'No video available for this course';
        videoContainer.appendChild(placeholder);
    }
}

function setupVideoTracking() {
    progressInterval = setInterval(() => {
        updateVideoProgress();
    }, 5000);
}

function updateVideoProgress() {
    const currentPercentage = Math.min(videoProgress + Math.random() * 5, 100);
    videoProgress = currentPercentage;
    updateProgressDisplay(videoProgress);
    saveProgressToStorage();
}

function updateProgressDisplay(percentage) {
    document.getElementById('progressFill').style.width = percentage + '%';
    document.getElementById('progressPercentage').textContent = Math.round(percentage);
}

function saveProgressToStorage() {
    const progressKey = `course_progress_${currentCourse.id}`;
    saveToStorage(progressKey, {
        courseId: currentCourse.id,
        progress: videoProgress,
        timestamp: new Date().toISOString()
    });
}

function loadProgressFromStorage() {
    const progressKey = `course_progress_${currentCourse.id}`;
    const saved = getFromStorage(progressKey);

    if (saved) {
        videoProgress = saved.progress;
        updateProgressDisplay(videoProgress);
    }
}

function loadCompletionRecord() {
    const { planId, planItemId } = getPlanContext();
    if (!planId || !planItemId) {
        currentCompletionRecord = null;
        return;
    }

    currentCompletionRecord = getFromStorage(createCompletionStorageKey(planId, planItemId));
}

function persistCompletionRecord() {
    const { planId, planItemId } = getPlanContext();

    if (!planId || !planItemId || !currentCourse) {
        throw new Error('Cannot determine current plan or plan item');
    }

    currentCompletionRecord = {
        courseId: currentCourse.id,
        planId,
        planItemId,
        completedAt: new Date().toISOString(),
        username: currentUser.username,
        courseTitle: currentCourse.title
    };

    saveToStorage(
        createCompletionStorageKey(planId, planItemId),
        currentCompletionRecord
    );
}

function syncCompletionUI() {
    const completeBtn = document.getElementById('markCompleteBtn');
    const certificateBtn = document.getElementById('downloadCertificateBtn');

    if (currentCompletionRecord) {
        completeBtn.disabled = true;
        completeBtn.textContent = 'Completed';
        certificateBtn.classList.remove('hidden');
        return;
    }

    completeBtn.disabled = false;
    completeBtn.textContent = 'Mark as Completed';
    certificateBtn.classList.add('hidden');
}

async function markCourseComplete() {
    if (!currentCourse || !isEligibleForCompletion(videoProgress)) {
        showAlert(`Please watch at least ${COMPLETION_THRESHOLD_PERCENT}% of the video before marking as complete`, 'error');
        return;
    }

    const btn = document.getElementById('markCompleteBtn');
    btn.disabled = true;
    btn.textContent = 'Marking...';

    try {
        videoProgress = 100;
        updateProgressDisplay(100);
        saveProgressToStorage();

        const { planId, planItemId } = getPlanContext();
        if (!planId || !planItemId) {
            throw new Error('Cannot determine current plan or plan item');
        }

        await apiCall(`/plans/${planId}/items/${planItemId}/status`, 'PUT', {
            status: 'completed'
        });

        persistCompletionRecord();
        syncCompletionUI();
        showAlert('Course marked as completed!', 'success');
    } catch (error) {
        showAlert('Failed to mark course complete: ' + error.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Mark as Completed';
    }
}

function populateCertificateTemplate() {
    if (!currentCourse || !currentCompletionRecord) {
        throw new Error('Certificate data is not available yet');
    }

    const certificateData = buildCertificateData({
        user: currentUser,
        course: currentCourse,
        completionRecord: currentCompletionRecord
    });

    document.getElementById('certificateLearnerName').textContent = certificateData.learnerName;
    document.getElementById('certificateStatement').textContent =
        `has successfully completed the course "${certificateData.courseTitle}" through Learning Plan Agent.`;
    document.getElementById('certificateCourseTitle').textContent = certificateData.courseTitle;
    document.getElementById('certificateCompletionDate').textContent = certificateData.completionDate;
    document.getElementById('certificateId').textContent = certificateData.certificateId;
    document.getElementById('certificateProvider').textContent = certificateData.provider;
    document.getElementById('certificateFormat').textContent = certificateData.format;
    document.getElementById('certificateDuration').textContent = `${certificateData.durationHours} hours`;
    document.getElementById('certificateDifficulty').textContent = certificateData.difficulty;
    document.getElementById('certificateSkills').textContent = certificateData.skillsText;

    return certificateData;
}

async function downloadCertificate() {
    if (!currentCompletionRecord) {
        showAlert('Complete the course first to download the certificate', 'error');
        return;
    }

    if (typeof window.html2pdf === 'undefined') {
        showAlert('Certificate export library is unavailable. Please refresh and try again.', 'error');
        return;
    }

    const template = document.getElementById('certificateTemplate');

    try {
        const certificateData = populateCertificateTemplate();
        template.classList.remove('hidden');

        await window.html2pdf().set({
            margin: 0,
            filename: `certificate-${currentCourse.id}-${currentCompletionRecord.completedAt.slice(0, 10)}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2, useCORS: true, backgroundColor: '#fffdf8' },
            jsPDF: { unit: 'px', format: [794, 1122], orientation: 'portrait' }
        }).from(template.firstElementChild).save();

        showAlert(`Certificate downloaded for ${certificateData.courseTitle}`, 'success');
    } catch (error) {
        showAlert('Failed to generate certificate: ' + error.message, 'error');
    } finally {
        template.classList.add('hidden');
    }
}

function goBackToPlan() {
    const fromURL = getUrlParameter('from') || 'dashboard.html';
    window.location.href = fromURL;
}

function logout() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    localStorage.clear();
    window.location.href = 'index.html';
}
