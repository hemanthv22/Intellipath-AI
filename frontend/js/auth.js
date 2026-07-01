// ==========================================
// UI HELPER FUNCTIONS (Global)
// ==========================================
console.log("AUTH JS UPDATED VERSION LOADED");
// Toggle Password Visibility
function togglePassword(inputId, iconElement) {
    const input = document.getElementById(inputId);
    if (input.type === "password") {
        input.type = "text";
        iconElement.classList.remove('fa-eye');
        iconElement.classList.add('fa-eye-slash');
    } else {
        input.type = "password";
        iconElement.classList.remove('fa-eye-slash');
        iconElement.classList.add('fa-eye');
    }
}

// Password Strength Checker
function checkPasswordStrength(password) {
    const container = document.getElementById('strengthMeterContainer');
    const fill = document.getElementById('strengthMeterFill');

    if (!container || !fill) return;

    if (password.length === 0) {
        container.style.display = 'none';
        return;
    }
    container.style.display = 'block';

    let strength = 0;
    if (password.length > 5) strength += 25;
    if (password.length > 7) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9!@#$%^&*]/.test(password)) strength += 25;

    fill.style.width = strength + '%';

    if (strength <= 25) { fill.style.backgroundColor = '#EF4444'; } // Red
    else if (strength <= 50) { fill.style.backgroundColor = '#F59E0B'; } // Yellow
    else { fill.style.backgroundColor = '#10B981'; } // Green
}

// ==========================================
// BACKEND API INTEGRATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {

    // --- LOGIN LOGIC ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Stop the page from refreshing

            // Getting values using the new HTML IDs
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            const submitBtn = document.getElementById('loginBtn');

            try {
                submitBtn.textContent = "Logging in...";
                submitBtn.style.opacity = "0.7";
                submitBtn.disabled = true;

                // Call the FastAPI Login Endpoint
                const response = await api.post('/auth/login', { email, password });
                console.log("Login Response:", response);
                // Save the JWT token to the browser
               localStorage.setItem('access_token', response.access_token);

localStorage.setItem('user_name', response.name);
localStorage.setItem('user_email', email);

localStorage.setItem(
    'userData',
    JSON.stringify({
        name: response.name || email.split('@')[0],
       email: response.email
    })
);

                window.location.href = 'dashboard.html';

            } catch (error) {
                alert(`Login Failed: ${error.message}`);
                submitBtn.textContent = "Sign In";
                submitBtn.style.opacity = "1";
                submitBtn.disabled = false;
            }
        });
    }

    // --- SIGNUP LOGIC ---
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Getting values using the exact HTML IDs
            const name = document.getElementById('signupName').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;
            const college = document.getElementById('signupCollege').value;
            const branch = document.getElementById('signupBranch').value;

            const submitBtn = document.getElementById('signupBtn');

            try {
                submitBtn.textContent = "Creating Account...";
                submitBtn.style.opacity = "0.7";
                submitBtn.disabled = true;

                // Call the FastAPI Signup Endpoint
                await api.post('/auth/signup', { name, email, password, college, branch });

                alert('Account created successfully! Please sign in.');
                window.location.href = 'login.html';

            } catch (error) {
                alert(`Signup Failed: ${error.message}`);
                submitBtn.textContent = "Create Account";
                submitBtn.style.opacity = "1";
                submitBtn.disabled = false;
            }
        });
    }
});