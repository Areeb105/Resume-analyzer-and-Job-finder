
/**
 * Auth Validation & UX Enhancements
 */

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    const loginForm = document.getElementById('login-form');

    // --- Registration Logic ---
    if (registerForm) {
        setupRegistrationValidation();
    }

    // --- Login Logic ---
    if (loginForm) {
        setupLoginValidation();
    }
});

function setupRegistrationValidation() {
    const passwordInput = document.getElementById('password');
    const requirementsList = document.createElement('ul');
    requirementsList.id = 'password-requirements';
    requirementsList.className = 'requirements-list';

    // Insert requirements list after password input
    passwordInput.parentNode.insertBefore(requirementsList, passwordInput.nextSibling);

    const requirements = [
        { regex: /.{8,}/, text: 'At least 8 characters' },
        { regex: /[A-Z]/, text: 'At least one uppercase letter' },
        { regex: /[a-z]/, text: 'At least one lowercase letter' },
        { regex: /[0-9]/, text: 'At least one number' },
        { regex: /[^A-Za-z0-9]/, text: 'At least one special character' }
    ];

    // Initial render of requirements
    renderRequirements(requirements, '');

    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        renderRequirements(requirements, password);
        updateInputStyle(passwordInput, checkAllRequirements(requirements, password));
    });

    const confirmPasswordInput = document.getElementById('confirm-password');
    confirmPasswordInput.addEventListener('input', (e) => {
        const password = passwordInput.value;
        const confirm = e.target.value;

        if (confirm && password !== confirm) {
            confirmPasswordInput.setCustomValidity("Passwords do not match");
            confirmPasswordInput.classList.add('invalid');
            confirmPasswordInput.classList.remove('valid');
        } else {
            confirmPasswordInput.setCustomValidity("");
            confirmPasswordInput.classList.remove('invalid');
            if (confirm) confirmPasswordInput.classList.add('valid');
        }
    });
}

function renderRequirements(requirements, password) {
    const list = document.getElementById('password-requirements');
    list.innerHTML = '';

    requirements.forEach(req => {
        const isMet = req.regex.test(password);
        const li = document.createElement('li');
        li.className = isMet ? 'met' : 'unmet';
        li.innerHTML = `
            <span class="icon">${isMet ? '✓' : '○'}</span>
            <span>${req.text}</span>
        `;
        list.appendChild(li);
    });
}

function checkAllRequirements(requirements, password) {
    return requirements.every(req => req.regex.test(password));
}

function updateInputStyle(input, isValid) {
    if (input.value.length > 0) {
        if (isValid) {
            input.classList.remove('invalid');
            input.classList.add('valid');
        } else {
            input.classList.remove('valid');
            input.classList.add('invalid');
        }
    } else {
        input.classList.remove('valid', 'invalid');
    }
}

function setupLoginValidation() {
    const passwordInput = document.getElementById('password');
    const capsWarning = document.createElement('div');
    capsWarning.id = 'caps-warning';
    capsWarning.style.display = 'none';
    capsWarning.textContent = '⚠️ Caps Lock is ON';
    capsWarning.className = 'form-warning'; // We'll add this class to CSS

    passwordInput.parentNode.insertBefore(capsWarning, passwordInput.nextSibling);

    passwordInput.addEventListener('keyup', (e) => {
        if (e.getModifierState('CapsLock')) {
            capsWarning.style.display = 'block';
        } else {
            capsWarning.style.display = 'none';
        }
    });
}
