document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const durationSelect = document.getElementById('duration');
    const rentalDateInput = document.getElementById('rental_date');
    const returnDateInput = document.getElementById('return_date');
    const totalPriceElement = document.getElementById('totalPrice');
    const rentNowBtn = document.getElementById('rentNowBtn');
    const paymentModal = document.getElementById('paymentModal');
    const cancelPaymentBtn = document.getElementById('cancelPayment');

    // Modal elements
    const modalDuration = document.getElementById('modalDuration');
    const modalStartDate = document.getElementById('modalStartDate');
    const modalReturnDate = document.getElementById('modalReturnDate');
    const modalTotalPrice = document.getElementById('modalTotalPrice');

    // Hidden input fields for payment modal
    const modalRentalDuration = document.getElementById('modalRentalDuration');
    const modalRentalStartDate = document.getElementById('modalRentalStartDate');
    const modalRentalNotes = document.getElementById('modalRentalNotes');
    const modalRentalAmount = document.getElementById('modalRentalAmount');

    // Calculate return date and total price
    function updateRentalDetails() {
        if (!rentalDateInput.value) return;

        const startDate = new Date(rentalDateInput.value);
        const duration = parseInt(durationSelect.value);
        
        // Calculate return date
        const returnDate = new Date(startDate);
        returnDate.setDate(startDate.getDate() + duration);
        returnDateInput.value = returnDate.toISOString().split('T')[0];

        // Calculate total price
        const pricePerDay = parseFloat(document.querySelector('[data-price]').getAttribute('data-price'));
        totalPriceElement.textContent = `$${(pricePerDay * duration).toFixed(2)}`;
    }

    // Event listeners for updates
    durationSelect.addEventListener('change', updateRentalDetails);
    rentalDateInput.addEventListener('change', updateRentalDetails);

    // Rent Now Button - Open Payment Modal
    rentNowBtn.addEventListener('click', function() {
        if (!rentalDateInput.value || !durationSelect.value) {
            alert('Please select a start date and duration.');
            return;
        }

        // Populate modal with rental details
        modalDuration.textContent = `${durationSelect.value} day(s)`;
        modalStartDate.textContent = rentalDateInput.value;
        modalReturnDate.textContent = returnDateInput.value;
        modalTotalPrice.textContent = totalPriceElement.textContent;

        // Set hidden input values for form submission
        modalRentalDuration.value = durationSelect.value;
        modalRentalStartDate.value = rentalDateInput.value;
        modalRentalNotes.value = document.getElementById('notes').value || '';
        modalRentalAmount.value = totalPriceElement.textContent.replace('$', '');

        paymentModal.classList.remove('hidden');
    });

    // Cancel Payment Button
    cancelPaymentBtn.addEventListener('click', () => paymentModal.classList.add('hidden'));

    // Close modal if clicked outside
    paymentModal.addEventListener('click', function(event) {
        if (event.target === paymentModal) {
            paymentModal.classList.add('hidden');
        }
    });
});
