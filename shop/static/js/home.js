document.addEventListener('DOMContentLoaded', () => {
    const imageGrid = document.getElementById('image-grid');
    const imageContainers = imageGrid ? imageGrid.querySelectorAll('div[class*="relative overflow-hidden"]') : [];
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (imageContainers.length > 0 && prevBtn && nextBtn) {
        let currentIndex = 0;
        let autoplayInterval;
        let isAnimating = false;

        function updateImages(index, direction = 'next') {
            if (isAnimating) return;
            isAnimating = true;

            const promises = [];
            imageContainers.forEach((container, i) => {
                const imageIndex = (index + i) % carouselImages.length;
                const promise = new Promise((resolve) => {
                    const img = new Image();
                    img.onload = resolve;
                    img.src = carouselImages[imageIndex].url;
                });
                promises.push(promise);
            });

            Promise.all(promises).then(() => {
                imageContainers.forEach(container => {
                    container.style.transition = 'none';
                    container.style.transform = direction === 'next' ? 'translateX(100%)' : 'translateX(-100%)';
                });

                imageGrid.offsetHeight;

                imageContainers.forEach((container, i) => {
                    const imageIndex = (index + i) % carouselImages.length;
                    const imgElement = container.querySelector('img');
                    const titleElement = container.querySelector('h3');
                    const descElement = container.querySelector('p');
                    
                    imgElement.style.transition = 'transform 0.5s ease-out';
                    container.style.transition = 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                    
                    imgElement.src = carouselImages[imageIndex].url;
                    titleElement.textContent = carouselImages[imageIndex].name;
                    descElement.textContent = carouselImages[imageIndex].description;
                    
                    container.style.transform = 'translateX(0)';
                });

                setTimeout(() => {
                    isAnimating = false;
                }, 500);
            });
        }

        function startAutoplay() {
            let lastTime = 0;
            const interval = 5000;

            function animate(currentTime) {
                if (!lastTime) lastTime = currentTime;
                
                if (currentTime - lastTime >= interval) {
                    if (!isAnimating) {
                        currentIndex = (currentIndex + 1) % carouselImages.length;
                        updateImages(currentIndex, 'next');
                    }
                    lastTime = currentTime;
                }
                
                autoplayInterval = requestAnimationFrame(animate);
            }

            autoplayInterval = requestAnimationFrame(animate);
        }

        function resetAutoplay() {
            cancelAnimationFrame(autoplayInterval);
            startAutoplay();
        }

        imageContainers.forEach(container => {
            const img = container.querySelector('img');
            img.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            
            container.addEventListener('mouseenter', () => {
                img.style.transform = 'scale(1.1)';
            });
            
            container.addEventListener('mouseleave', () => {
                img.style.transform = 'scale(1)';
            });
        });

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

        startAutoplay();
    }
});