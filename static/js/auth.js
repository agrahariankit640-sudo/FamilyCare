document.addEventListener('DOMContentLoaded', () => {
    // Helper to display errors inside auth cards
    function showAuthError(form, message) {
        let errDiv = form.querySelector('#error-message') || document.getElementById('error-message');
        if (errDiv) {
            errDiv.textContent = message;
            errDiv.style.display = 'block';
        }
        if (typeof App !== 'undefined' && App.toast) {
            App.toast.show(message, 'error');
        }
    }

    function clearAuthError(form) {
        let errDiv = form.querySelector('#error-message') || document.getElementById('error-message');
        if (errDiv) {
            errDiv.textContent = '';
            errDiv.style.display = 'none';
        }
    }

    // Login form handling
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthError(loginForm);

            const emailInput = loginForm.querySelector('#email') || loginForm.querySelector('input[name="email"]');
            const passInput = loginForm.querySelector('#password') || loginForm.querySelector('input[name="password"]');
            const rememberInput = loginForm.querySelector('#remember') || loginForm.querySelector('input[name="remember"]');

            const email = emailInput ? emailInput.value.trim() : '';
            const password = passInput ? passInput.value : '';
            const remember = rememberInput ? rememberInput.checked : false;

            if (!email || !password) {
                showAuthError(loginForm, 'Please enter both email and password');
                return;
            }

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            if (typeof App !== 'undefined' && App.loading) {
                App.loading.showBtn(submitBtn);
            }

            try {
                const res = await API.auth.login({ email, password, remember });
                if (typeof App !== 'undefined' && App.toast) {
                    App.toast.show('Login successful', 'success');
                }
                window.location.href = '/dashboard';
            } catch (error) {
                console.error('Login error:', error);
                showAuthError(loginForm, error.message || 'Invalid email or password');
            } finally {
                if (typeof App !== 'undefined' && App.loading) {
                    App.loading.hideBtn(submitBtn);
                }
            }
        });
    }

    // Register form handling
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        const passInput = registerForm.querySelector('input[name="password"]');
        const confirmPassInput = registerForm.querySelector('input[name="confirm_password"]');
        const strengthIndicator = document.getElementById('password-strength');

        // Password strength indicator
        if (passInput && strengthIndicator) {
            passInput.addEventListener('input', () => {
                const result = App.form.validatePassword(passInput.value);
                strengthIndicator.textContent = result.message;
                strengthIndicator.className = result.valid ? 'text-success' : 'text-warning';
            });
        }

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearAuthError(registerForm);

            const validation = App.form.validate(registerForm);
            if (!validation.isValid) return;
            
            if (passInput && confirmPassInput && passInput.value !== confirmPassInput.value) {
                App.form.showFieldError(confirmPassInput, 'Passwords do not match');
                return;
            }

            if (passInput) {
                const pwdValidation = App.form.validatePassword(passInput.value);
                if (!pwdValidation.valid) {
                    App.form.showFieldError(passInput, pwdValidation.message);
                    return;
                }
            }
            
            const submitBtn = registerForm.querySelector('button[type="submit"]');
            App.loading.showBtn(submitBtn);
            
            try {
                const data = App.form.getData(registerForm);
                await API.auth.register(data);
                App.toast.show('Registration successful! Please login.', 'success');
                setTimeout(() => window.location.href = '/login', 1500);
            } catch (error) {
                showAuthError(registerForm, error.message || 'Registration failed');
            } finally {
                App.loading.hideBtn(submitBtn);
            }
        });
    }

    // Direct, reliable password toggle handler
    document.querySelectorAll('.password-toggle, .toggle-password').forEach(btn => {
        if (btn.dataset.authToggleBound) return;
        btn.dataset.authToggleBound = 'true';
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const group = this.closest('.password-input-group') || this.parentElement;
            const input = group ? group.querySelector('input') : null;
            if (input) {
                const isPass = input.type === 'password';
                input.type = isPass ? 'text' : 'password';
                this.innerHTML = `<i data-lucide="${isPass ? 'eye-off' : 'eye'}"></i>`;
                if (typeof lucide !== 'undefined' && lucide.createIcons) {
                    lucide.createIcons();
                }
            }
        });
    });
});
