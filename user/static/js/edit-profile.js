document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.edit-profile-form');
  const inputs = form.querySelectorAll('input, select, textarea');
  const fileInput = form.querySelector('input[type="file"]');
  const submitButton = form.querySelector('button[type="submit"]');

  inputs.forEach(input => {
      input.addEventListener('input', () => {
          validateInput(input);
      });

      input.addEventListener('blur', () => {
          validateInput(input);
      });
  });

  function validateInput(input) {
      if (input.value.trim() === '' && input.hasAttribute('required')) {
          showError(input, 'This field cannot be empty');
      } else {
          clearError(input);
      }
  }

  function showError(input, message) {
      clearError(input);

      const errorElement = document.createElement('div');
      errorElement.className = 'input-error';
      errorElement.textContent = message;
      errorElement.style.color = 'var(--error-color)';
      errorElement.style.fontSize = '0.8rem';
      errorElement.style.marginTop = '0.25rem';

      input.parentNode.insertBefore(errorElement, input.nextSibling);
      input.classList.add('invalid');
  }

  function clearError(input) {
      const errorElement = input.parentNode.querySelector('.input-error');
      if (errorElement) {
          errorElement.remove();
      }
      input.classList.remove('invalid');
  }

  if (fileInput) {
      fileInput.addEventListener('change', (e) => {
          const file = e.target.files[0];
          if (file) {
              const reader = new FileReader();
              reader.onload = (event) => {
                  console.log('File selected:', file.name);
              };
              reader.readAsDataURL(file);
          }
      });
  }

  submitButton.addEventListener('mouseenter', createSparkleEffect);

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