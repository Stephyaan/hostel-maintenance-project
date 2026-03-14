const API_URL = "/api/";

console.log('✅ HostelHub API Helper v1.2.1 Loaded');

// --- Global Design & Personalization ---
// --- Global Design & Personalization ---
function updatePortalClock() {
    const timeEl = document.getElementById('currentTime');
    const dateEl = document.getElementById('currentDate');
    if (!timeEl || !dateEl) return;

    const now = new Date();
    timeEl.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const options = { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
    dateEl.innerText = now.toLocaleDateString('en-US', options).toUpperCase();
}

// Initial update and sync
setInterval(updatePortalClock, 1000);

function personalizeDashboard() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const welcomeTitle = document.getElementById('welcomeTitle');
    const welcomeSub = document.getElementById('welcomeSub');

    if (!welcomeTitle) return;

    const role = user.role || 'Guest';
    let icon = '👋';
    if (role === 'admin') icon = '🛡️';
    else if (role === 'supervisor') icon = '👷';

    // Set Greeting
    const name = user.first_name || user.username || 'User';
    welcomeTitle.innerHTML = `Hello, ${name} <span class="wave">${icon}</span>`;

    // Set Subtext if it exists
    if (welcomeSub) {
        if (role === 'student' && user.block && user.room_number) {
            welcomeSub.innerText = `Block ${user.block} · Room ${user.room_number}`;
        } else if (role === 'supervisor') {
            welcomeSub.innerText = `Optimizing hostel maintenance and worker performance.`;
        } else if (role === 'admin') {
            welcomeSub.innerText = `Full oversight of hostel infrastructure and configurations.`;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updatePortalClock();
    personalizeDashboard();
});

// Generic API Fetcher
async function apiCall(endpoint, method = "GET", data = null) {
    const token = localStorage.getItem("token"); // Assuming we'll store JWT token here
    const headers = {
        "Content-Type": "application/json",
    };

    if (token) {
        headers["Authorization"] = `Token ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (data) {
        config.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        if (response.status === 401) {
            // Unauthorized - redirect to login
            logout();
            return null;
        }
        if (response.status === 204) {
            // No Content (e.g. successful DELETE)
            return true;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || JSON.stringify(error) || "API Error");
        }
        return await response.json();
    } catch (error) {
        console.error("API Call Failed:", error);
        // Removed alert to prevent annoying popups on page load/network issues
        return null;
    }
}

function logout() {
    localStorage.clear();
    // Redirect to root login page
    window.location.href = "/";
}

// Global UI Settings Syncer
async function syncSidebarSettings() {
    const settings = await apiCall('settings/', 'GET');
    if (!settings) return;

    // Student specific: Resource Requests
    const resourceModule = settings.find(s => s.key === 'resource_request_module');
    if (resourceModule && resourceModule.value === false) {
        const item = document.querySelector('li[onclick*="request_resources.html"]');
        if (item) item.style.display = 'none';

        // If user is currently on that page, redirect away
        if (window.location.pathname.includes('request_resources.html')) {
            window.location.href = 'dashboard.html';
        }
    }

    // Supervisor specific: Reports
    const reportAccess = settings.find(s => s.key === 'performance_reports_access');
    if (reportAccess && reportAccess.value === false) {
        const item = document.querySelector('li[onclick*="reports.html"]');
        if (item) item.style.display = 'none';

        if (window.location.pathname.includes('reports.html')) {
            window.location.href = 'dashboard.html';
        }
    }
}
