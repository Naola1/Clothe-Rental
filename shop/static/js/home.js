document.addEventListener('DOMContentLoaded', () => {
    const mainImage = document.getElementById('main-image');
    const thumbnailImages = document.querySelectorAll('.thumbnail-images img');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (mainImage && thumbnailImages.length > 0 && prevBtn && nextBtn) {
        let currentIndex = 0;
        let visibleRangeStart = 0;
        let autoplayInterval;

        // Update main image
        function updateMainImage(index) {
            mainImage.src = thumbnailImages[index].src;
        }

        // Update the visibility of the thumbnail images
        function updateThumbnailVisibility() {
            thumbnailImages.forEach((thumbnail, index) => {
                thumbnail.style.display = (index >= visibleRangeStart && index < visibleRangeStart + 2) ? 'block' : 'none';
            });
        }

        // Update image when thumbnail is clicked
        thumbnailImages.forEach((thumbnail, index) => {
            thumbnail.addEventListener('click', () => {
                currentIndex = index;
                updateMainImage(currentIndex);
                visibleRangeStart = Math.floor(currentIndex / 3) * 3;
                updateThumbnailVisibility();
                resetAutoplay();
            });
        });

        // Move to the previous image
        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + thumbnailImages.length) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 3) * 3;
            updateThumbnailVisibility();
            resetAutoplay();
        });

        // Move to the next image
        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 3) * 3;
            updateThumbnailVisibility();
            resetAutoplay();
        });

        // Autoplay function: changes the image every 5 seconds
        function startAutoplay() {
            autoplayInterval = setInterval(() => {
                currentIndex = (currentIndex + 1) % thumbnailImages.length;
                updateMainImage(currentIndex);
                visibleRangeStart = Math.floor(currentIndex / 3) * 3;
                updateThumbnailVisibility();
            }, 5000); // Change image every 5 seconds
        }

        // Stops autoplay and restarts it
        function resetAutoplay() {
            clearInterval(autoplayInterval);
            startAutoplay();
        }

        // Initialize the first image and start autoplay
        updateMainImage(currentIndex);
        updateThumbnailVisibility();
        startAutoplay();
    }
});
