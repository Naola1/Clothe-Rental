document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('id_new_password1');
    const confirmPasswordInput = document.getElementById('id_new_password2');
    const passwordStrengthMeter = document.querySelector('.password-strength-meter');
    const passwordStrengthBar = document.querySelector('.password-strength-bar');
    const passwordRequirements = document.querySelector('.password-requirements');
    const form = document.querySelector('.change-password-form');
  
    // Password strength and validation
    function calculatePasswordStrength(password) {
      let strength = 0;
      const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password),
        specialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password)
      };
  
      // Update requirement indicators
      Object.keys(requirements).forEach(req => {
        const reqElement = passwordRequirements.querySelector(`#req-${req}`);
        if (reqElement) {
          reqElement.classList.toggle('valid', requirements[req]);
          reqElement.classList.toggle('invalid', !requirements[req]);
        }
      });
  
      // Calculate strength
      strength += requirements.length ? 1 : 0;
      strength += requirements.uppercase ? 1 : 0;
      strength += requirements.lowercase ? 1 : 0;
      strength += requirements.number ? 1 : 0;
      strength += requirements.specialChar ? 1 : 0;
  
      return strength;
    }
  
    function updatePasswordStrength() {
      const password = passwordInput.value;
      const strength = calculatePasswordStrength(password);
  
      // Update strength meter
      passwordStrengthBar.style.width = `${(strength / 5) * 100}%`;
      passwordStrengthBar.classList.remove('weak', 'medium', 'strong');
  
      if (strength <= 2) {
        passwordStrengthBar.classList.add('weak');
      } else if (strength <= 4) {
        passwordStrengthBar.classList.add('medium');
      } else {
        passwordStrengthBar.classList.add('strong');
      }
    }
  
    // Password match validation
    function validatePasswordMatch() {
      const password = passwordInput.value;
      const confirmPassword = confirmPasswordInput.value;
  
      if (password !== confirmPassword) {
        confirmPasswordInput.setCustomValidity('Passwords do not match');
        return false;
      } else {
        confirmPasswordInput.setCustomValidity('');
        return true;
      }
    }
  
    // Event Listeners
    if (passwordInput) {
      passwordInput.addEventListener('input', () => {
        updatePasswordStrength();
      });
    }
  
    if (confirmPasswordInput) {
      confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }
  
    // Form submission validation
    if (form) {
      form.addEventListener('submit', (e) => {
        if (!validatePasswordMatch()) {
          e.preventDefault();
        }
      });
    }
  
    // Animated submit button effect
    const submitButton = document.querySelector('.btn-primary');
    if (submitButton) {
      submitButton.addEventListener('mouseenter', createSparkleEffect);
    }
  
    function createSparkleEffect(event) {
      const button = event.target;
      const sparkleCount = 10;
  
      for (let i = 0; i < sparkleCount; i++) {
        const sparkle = document.createElement('div');
        sparkle.classList.add('sparkle');
        
        const size = Math.random() * 5 + 2;
        sparkle.style.width = `${size}px`;
        sparkle.style.height = `${size}px`;
        
        const xPos = Math.random() * button.offsetWidth;
        const yPos = Math.random() * button.offsetHeight;
        
        sparkle.style.left = `${xPos}px`;
        sparkle.style.top = `${yPos}px`;
        
        button.appendChild(sparkle);
        
        setTimeout(() => {
          sparkle.remove();
        }, 500);
      }
    }
  });