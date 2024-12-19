document.addEventListener('DOMContentLoaded', () => {
    const mainImage = document.getElementById('main-image');
    const thumbnailImages = document.querySelectorAll('.thumbnail-images img');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');

    if (mainImage && thumbnailImages.length > 0 && prevBtn && nextBtn) {
        let currentIndex = 0;
        let visibleRangeStart = 0;

        function updateMainImage(index) {
            mainImage.src = thumbnailImages[index].src;
        }

        function updateThumbnailVisibility() {
            thumbnailImages.forEach((thumbnail, index) => {
                thumbnail.style.display = (index >= visibleRangeStart && index < visibleRangeStart + 2) ? 'block' : 'none';
            });
        }

        thumbnailImages.forEach((thumbnail, index) => {
            thumbnail.addEventListener('click', () => {
                currentIndex = index;
                updateMainImage(currentIndex);
                visibleRangeStart = Math.floor(currentIndex / 3) * 3;
                updateThumbnailVisibility();
            });
        });

        prevBtn.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + thumbnailImages.length) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 3) * 3;
            updateThumbnailVisibility();
        });

        nextBtn.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % thumbnailImages.length;
            updateMainImage(currentIndex);
            visibleRangeStart = Math.floor(currentIndex / 3) * 3;
            updateThumbnailVisibility();
        });

        updateMainImage(currentIndex);
        updateThumbnailVisibility();
    }
});
