const API_URL = (window.location.protocol === 'http:' || window.location.protocol === 'https:')
    ? `${window.location.origin}/api/`
    : "http://127.0.0.1:8000/api/";

console.log('✅ HostelHub API Helper v1.2.1 Loaded');

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

    // Supervisor specific: Worker management
    const workerAccess = settings.find(s => s.key === 'worker_management_access');
    if (workerAccess && workerAccess.value === false) {
        const item = document.querySelector('li[onclick*="workers.html"]');
        if (item) item.style.display = 'none';

        if (window.location.pathname.includes('workers.html')) {
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
