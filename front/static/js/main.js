const main_js_dictionary = {}

function reset_password(btn){
    const modal = new bootstrap.Modal(document.getElementById('resetPasswordModal'));
    document.getElementById('newPasswordUsername').value = btn.dataset.email;
    modal.show();
}

function reset_immutable_password(btn){
    const modal = new bootstrap.Modal(document.getElementById('resetImmutablePasswordModal'));
    modal.show();
}


function load_main_js_dictionnary(language){
    return new Promise((r,e) => {
        loadTranslations("main.js",language).then((dct) => {
            Object.entries(dct).forEach( e => main_js_dictionary[e[0]] = e[1] );
            r();
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailForm');
    const submitEmailBtn = document.getElementById('submitEmailBtn');
    const passwordInput = document.getElementById('password');
    const passwordStrength = document.getElementById('passwordStrength');
    const newPasswordInput = document.getElementById('newPassword');
    
    // Password strength indicator
    passwordInput.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        updatePasswordStrengthIndicator(strength);
    });

    newPasswordInput.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        updatePasswordStrengthIndicator(strength, 'newPasswordStrength');
    });
    
    function calculatePasswordStrength(password) {
        if (password.length === 0) return 0;
        
        let strength = 0;
        
        // Length contributes up to 50% of strength
        if (password.length >= 8) strength += 50;
        else if (password.length >= 4) strength += 25;
        
        // Character variety contributes the remaining 50%
        const hasLowercase = /[a-z]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasNumbers = /[0-9]/.test(password);
        const hasSpecial = /[^a-zA-Z0-9]/.test(password);
        
        const varietyCount = [hasLowercase, hasUppercase, hasNumbers, hasSpecial].filter(Boolean).length;
        strength += (varietyCount * 12.5); // Each category adds 12.5% (total 50 for all 4)
        
        return Math.min(100, Math.round(strength));
    }
    
    function updatePasswordStrengthIndicator(strength, elementId = 'passwordStrength') {
        const indicator = document.getElementById(elementId);
        indicator.style.width = strength + '%';
        
        if (strength < 30) {
            indicator.style.backgroundColor = '#dc3545'; // Weak - red
        } else if (strength < 70) {
            indicator.style.backgroundColor = '#ffc107'; // Medium - yellow
        } else {
            indicator.style.backgroundColor = '#198754'; // Strong - green
        }
    }
    
    // Form validation and submission
    submitEmailBtn.addEventListener('click', function() {
        const firstName = document.getElementById('firstName').value.trim();
        const lastName = document.getElementById('lastName').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        let isValid = true;
        
        // Clear previous errors
        document.querySelectorAll('.form-error').forEach(el => el.textContent = '');
        
        // Validate first name (required, alphanumeric starting with letter)
        if (!firstName) {
            document.getElementById('firstNameError').textContent = main_js_dictionary['error_first_name_required'];
            isValid = false;
        } else if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(firstName)) {
            document.getElementById('firstNameError').textContent = main_js_dictionary['error_first_name_format'];
            isValid = false;
        }
        
        // Validate last name (optional, but if provided must be alphanumeric starting with letter)
        if (lastName && !/^[a-zA-Z][a-zA-Z0-9]*$/.test(lastName)) {
            document.getElementById('lastNameError').textContent = main_js_dictionary['error_last_name_format'];
            isValid = false;
        }
        
        // Validate password
        if (!password) {
            document.getElementById('passwordError').textContent = main_js_dictionary['error_password_required'];
            isValid = false;
        } else if (password.length < 8) {
            document.getElementById('passwordError').textContent = main_js_dictionary['error_password_length'];
            isValid = false;
        }
        
        // Validate confirm password
        if (!confirmPassword) {
            document.getElementById('confirmPasswordError').textContent = main_js_dictionary['error_confirm_password_required'];
            isValid = false;
        } else if (password !== confirmPassword) {
            document.getElementById('confirmPasswordError').textContent = main_js_dictionary['error_passwords_mismatch'];
            isValid = false;
        }
        
        // If valid, proceed with form submission
        if (isValid) {
            document.getElementById('firstName').name = "firstName"
            document.getElementById('lastName').name = "lastName"
            document.getElementById('password').name = "password"
            document.getElementById('confirmPassword').name = "confirmPassword"
            emailForm.submit();
        }
    });

    document.getElementById('submitResetPasswordBtn').addEventListener('click', function() {
        const newPassword = document.getElementById('newPassword').value;
        const confirmNewPassword = document.getElementById('confirmNewPassword').value;
        
        document.getElementById('newPasswordError').textContent = '';
        document.getElementById('confirmNewPasswordError').textContent = '';
        
        let isValid = true;
        
        if (!newPassword) {
            document.getElementById('newPasswordError').textContent = main_js_dictionary['error_new_password_required'];
            isValid = false;
        } else if (newPassword.length < 8) {
            document.getElementById('newPasswordError').textContent = main_js_dictionary['error_password_length'];
            isValid = false;
        }
        
        if (!confirmNewPassword) {
            document.getElementById('confirmNewPasswordError').textContent = main_js_dictionary['error_confirm_new_password_required'];
            isValid = false;
        } else if (newPassword !== confirmNewPassword) {
            document.getElementById('confirmNewPasswordError').textContent = main_js_dictionary['error_passwords_mismatch'];
            isValid = false;
        }
        
        if (isValid) {
            document.getElementById('newPasswordUsername').name = "username"
            document.getElementById('newPassword').name = "password"
            document.getElementById('confirmNewPassword').name = "confirmPassword"
            resetPasswordForm.submit();
        }
    });
});