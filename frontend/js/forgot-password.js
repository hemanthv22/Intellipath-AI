// ==========================================
// FORGOT PASSWORD (OTP) FLOW
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');

    // Keep track of the email + otp across steps
    let userEmail = '';
    let verifiedOtp = '';

    function showStep(stepEl) {
        [step1, step2, step3, step4].forEach(s => s.style.display = 'none');
        stepEl.style.display = 'block';
    }

    function setLoading(btn, loadingText, originalText) {
        btn.textContent = loadingText;
        btn.style.opacity = '0.7';
        btn.disabled = true;
        return () => {
            btn.textContent = originalText;
            btn.style.opacity = '1';
            btn.disabled = false;
        };
    }

    // --- STEP 1: Request OTP ---
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            userEmail = document.getElementById('fpEmail').value.trim();
            const btn = document.getElementById('sendOtpBtn');
            const reset = setLoading(btn, 'Sending OTP...', 'Send OTP');

            try {
                await api.post('/auth/forgot-password', { email: userEmail });
                document.getElementById('otpEmailDisplay').textContent = userEmail;
                showStep(step2);
            } catch (error) {
                alert(`Failed to send OTP: ${error.message}`);
            } finally {
                reset();
            }
        });
    }

    // --- STEP 2: Verify OTP ---
    const otpForm = document.getElementById('otpForm');
    if (otpForm) {
        otpForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const otp = document.getElementById('fpOtp').value.trim();
            const btn = document.getElementById('verifyOtpBtn');
            const reset = setLoading(btn, 'Verifying...', 'Verify OTP');

            try {
                await api.post('/auth/verify-otp', { email: userEmail, otp });
                verifiedOtp = otp;
                showStep(step3);
            } catch (error) {
                alert(`Verification Failed: ${error.message}`);
            } finally {
                reset();
            }
        });
    }

    // --- Resend OTP ---
    const resendLink = document.getElementById('resendOtpLink');
    if (resendLink) {
        resendLink.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await api.post('/auth/forgot-password', { email: userEmail });
                alert('A new OTP has been sent to your email.');
            } catch (error) {
                alert(`Failed to resend OTP: ${error.message}`);
            }
        });
    }

    // --- STEP 3: Reset Password ---
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match.');
                return;
            }

            const btn = document.getElementById('resetPasswordBtn');
            const reset = setLoading(btn, 'Updating...', 'Update Password');

            try {
                await api.post('/auth/reset-password', {
                    email: userEmail,
                    otp: verifiedOtp,
                    new_password: newPassword
                });
                showStep(step4);
            } catch (error) {
                alert(`Failed to reset password: ${error.message}`);
            } finally {
                reset();
            }
        });
    }
});
