document.addEventListener('DOMContentLoaded', () => {
    const profileContainer = document.querySelector('.profile-container');
    const userInfoElements = document.querySelectorAll('.user-info p');
    const actionButtons = document.querySelectorAll('.btn');
  
    // Add interactive hover effects
    userInfoElements.forEach(element => {
      element.addEventListener('mouseenter', (e) => {
        e.target.style.transform = 'scale(1.02)';
        e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
      });
  
      element.addEventListener('mouseleave', (e) => {
        e.target.style.transform = 'scale(1)';
        e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
      });
    });
  
    // Add particle-like sparkle effect on buttons
    actionButtons.forEach(button => {
      button.addEventListener('mouseenter', createSparkleEffect);
    });
  
    // function createSparkleEffect(event) {
    //   const button = event.target;
    //   const sparkleCount = 10;
  
    //   for (let i = 0; i < sparkleCount; i++) {
    //     const sparkle = document.createElement('div');
    //     sparkle.classList.add('sparkle');
        
    //     const size = Math.random() * 5 + 2;
    //     sparkle.style.width = `${size}px`;
    //     sparkle.style.height = `${size}px`;
        
    //     const xPos = Math.random() * button.offsetWidth;
    //     const yPos = Math.random() * button.offsetHeight;
        
    //     sparkle.style.left = `${xPos}px`;
    //     sparkle.style.top = `${yPos}px`;
        
    //     button.appendChild(sparkle);
        
    //     setTimeout(() => {
    //       sparkle.remove();
    //     }, 500);
    //   }
    // }
  
    // Optional: Add subtle background animation
    function createBackgroundAnimation() {
      const gradient = document.createElement('div');
      gradient.classList.add('background-gradient');
      profileContainer.appendChild(gradient);
    }
  
    createBackgroundAnimation();
  });