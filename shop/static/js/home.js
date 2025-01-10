document.addEventListener('DOMContentLoaded', () => {
    const imageGrid = document.getElementById('image-grid');
    const imageContainers = imageGrid ? imageGrid.querySelectorAll('div[class*="relative overflow-hidden"]') : [];
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (imageContainers.length > 0 && prevBtn && nextBtn) {
        let currentIndex = 0;
        let autoplayInterval;
        let isAnimating = false;

        // Update images with animation
        function updateImages(index, direction = 'next') {
            if (isAnimating) return;
            isAnimating = true;

            // Add transition class to all containers
            imageContainers.forEach((container) => {
                container.style.transition = 'transform 0.8s ease-in-out';
                container.style.transform = direction === 'next' ? 'translateX(-100%)' : 'translateX(100%)';
            });

            setTimeout(() => {
                imageContainers.forEach((container, i) => {
                    const imageIndex = (index + i) % carouselImages.length;
                    const imgElement = container.querySelector('img');
                    const titleElement = container.querySelector('h3');
                    const descElement = container.querySelector('p');

                    // Update content
                    imgElement.src = carouselImages[imageIndex].url;
                    titleElement.textContent = carouselImages[imageIndex].name;
                    descElement.textContent = carouselImages[imageIndex].description;

                    // Reset position instantly
                    container.style.transition = 'none';
                    container.style.transform = direction === 'next' ? 'translateX(100%)' : 'translateX(-100%)';
                });

                // Force reflow
                imageGrid.offsetHeight;

                // Animate to final position
                imageContainers.forEach((container) => {
                    container.style.transition = 'transform 0.5s ease-in-out';
                    container.style.transform = 'translateX(0)';
                });

                setTimeout(() => {
                    isAnimating = false;
                }, 500);
            }, 500);
        }

        // Autoplay function with smoother transitions
        function startAutoplay() {
            autoplayInterval = setInterval(() => {
                if (!isAnimating) {
                    currentIndex = (currentIndex + 1) % carouselImages.length;
                    updateImages(currentIndex, 'next');
                }
            }, 5000);
        }

        function resetAutoplay() {
            clearInterval(autoplayInterval);
            startAutoplay();
        }

        // Event listeners with direction
        prevBtn.addEventListener('click', () => {
            if (!isAnimating) {
                currentIndex = (currentIndex - 1 + carouselImages.length) % carouselImages.length;
                updateImages(currentIndex, 'prev');
                resetAutoplay();
            }
        });

        nextBtn.addEventListener('click', () => {
            if (!isAnimating) {
                currentIndex = (currentIndex + 1) % carouselImages.length;
                updateImages(currentIndex, 'next');
                resetAutoplay();
            }
        });

        // Add hover effect for smoother zoom
        imageContainers.forEach(container => {
            container.addEventListener('mouseenter', () => {
                const img = container.querySelector('img');
                img.style.transform = 'scale(1.1)';
            });

            container.addEventListener('mouseleave', () => {
                const img = container.querySelector('img');
                img.style.transform = 'scale(1)';
            });
        });

        // Initialize autoplay
        startAutoplay();
    }
});