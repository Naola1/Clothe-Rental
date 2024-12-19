document.addEventListener('DOMContentLoaded', () => {
    // === Image Carousel Logic ===
    const mainImage = document.getElementById('main-image');
    const thumbnailImages = document.querySelectorAll('.thumbnail-images img');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (mainImage && thumbnailImages.length > 0 && prevBtn && nextBtn) {
        let currentIndex = 0;
        let visibleRangeStart = 0;

        // Update the main image based on the selected thumbnail
        const updateMainImage = (index) => {
            const thumbnailSrc = thumbnailImages[index].getAttribute('data-src');
            mainImage.src = thumbnailSrc;
        };

        // Update the visibility of the thumbnails
        const updateThumbnailVisibility = () => {
            thumbnailImages.forEach((thumbnail, index) => {
                thumbnail.style.display = (index >= visibleRangeStart && index < visibleRangeStart + 2) ? 'block' : 'none';
            });
        };

        // Event listeners for thumbnails
        thumbnailImages.forEach((thumbnail, index) => {
            thumbnail.addEventListener('click', () => {
                currentIndex = index;
                updateMainImage(currentIndex);
                visibleRangeStart = Math.floor(currentIndex / 2) * 2;
                updateThumbnailVisibility();
            });
        });

        // Navigation buttons logic
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + thumbnailImages.length) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 2) * 2;
            updateThumbnailVisibility();
        });

        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 2) * 2;
            updateThumbnailVisibility();
        });

        // Initialize the carousel
        updateMainImage(currentIndex);
        updateThumbnailVisibility();
    }

    // === Transparent Navbar Logic ===
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    navbar.classList.add('navbar-transparent');
                } else {
                    navbar.classList.remove('navbar-transparent');
                }
            },
            { threshold: 0.1 }
        );

        const heroSection = document.querySelector('header');
        if (heroSection) {
            observer.observe(heroSection);
        }
    }
});