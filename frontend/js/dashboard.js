document.addEventListener('DOMContentLoaded', () => {

    // --- 1. SECURITY CHECK ---
    // If there is no token, the user shouldn't be here.
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // --- 2. DYNAMIC USERNAME ---
    // Get the name we saved during the login/signup process
    const userName = localStorage.getItem('user_name') || 'User';
    const userNameElement = document.getElementById('userNameText');

    if (userNameElement) {
        userNameElement.textContent = userName;
    }

    // --- 3. LOGOUT FUNCTIONALITY ---
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            // Clear all session data from the browser
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_name');

            // Optional: Friendly goodbye
            console.log("Session cleared. Logging out...");

            // Redirect to landing page
            window.location.href = 'index.html';
        });
    }

    // --- 4. SETTINGS REDIRECT ---
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            window.location.href = 'settings.html';
        });
    }

    // Load Dashboard Stats
const xpElement = document.getElementById('xpPoints');
const skillsElement = document.getElementById('skillsMastered');
const streakElement = document.getElementById('learningStreak');

if (xpElement) {
    xpElement.textContent = localStorage.getItem('xp_points') || 0;
}

if (skillsElement) {
    skillsElement.textContent = localStorage.getItem('skills_mastered') || 0;
}

if (streakElement) {
    streakElement.textContent =
        `${localStorage.getItem('learning_streak') || 0} Days`;
}

    // --- 5. DASHBOARD INTERACTIVITY (Optional) ---
    // You can add logic here to fetch real stats from the backend later
    console.log(`Welcome to your dashboard, ${userName}!`);
});