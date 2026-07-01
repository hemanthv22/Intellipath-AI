const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = {
    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'An error occurred');
            }

            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

// --- GLOBAL UI HANDLERS ---
// Because this file is loaded on every page, we handle global layout elements here.
// --- GLOBAL UI HANDLERS ---
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Dynamic Profile Loader
    const userNameText = document.getElementById('userNameText');
    if (userNameText) {
        // Look for the user session data saved during login
        const savedUser = JSON.parse(localStorage.getItem('userData'));
        
        if (savedUser && savedUser.name) {
            userNameText.innerText = savedUser.name;
        } else {
            // Truly dynamic fallback if no user is found/logged in
            userNameText.innerText = "Guest User"; 
        }
    }

    // 2. Universal Logout Handler
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.clear();
            window.location.href = 'index.html'; 
        });
    }
});