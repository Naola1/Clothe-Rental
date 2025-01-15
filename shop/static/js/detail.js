document.addEventListener('DOMContentLoaded', function() {
    const durationSelect = document.getElementById('duration');
    const rentalDateInput = document.getElementById('rental_date');
    const returnDateInput = document.getElementById('return_date');
    const totalPriceElement = document.getElementById('totalPrice');
    const rentNowBtn = document.getElementById('rentNowBtn');
    const paymentModal = document.getElementById('paymentModal');
    const cancelPaymentBtn = document.getElementById('cancelPayment');

    const modalDuration = document.getElementById('modalDuration');
    const modalStartDate = document.getElementById('modalStartDate');
    const modalReturnDate = document.getElementById('modalReturnDate');
    const modalTotalPrice = document.getElementById('modalTotalPrice');

    const modalRentalDuration = document.getElementById('modalRentalDuration');
    const modalRentalStartDate = document.getElementById('modalRentalStartDate');
    const modalRentalNotes = document.getElementById('modalRentalNotes');
    const modalRentalAmount = document.getElementById('modalRentalAmount');

    function updateRentalDetails() {
        if (!rentalDateInput.value) return;

        const startDate = new Date(rentalDateInput.value);
        const duration = parseInt(durationSelect.value);
        
        const returnDate = new Date(startDate);
        returnDate.setDate(startDate.getDate() + duration);
        returnDateInput.value = returnDate.toISOString().split('T')[0];

        const pricePerDay = parseFloat(document.querySelector('[data-price]').getAttribute('data-price'));
        totalPriceElement.textContent = `$${(pricePerDay * duration).toFixed(2)}`;
    }

    durationSelect.addEventListener('change', updateRentalDetails);
    rentalDateInput.addEventListener('change', updateRentalDetails);

    rentNowBtn.addEventListener('click', function() {
        if (!rentalDateInput.value || !durationSelect.value) {
            alert('Please select a start date and duration.');
            return;
        }

        modalDuration.textContent = `${durationSelect.value} day(s)`;
        modalStartDate.textContent = rentalDateInput.value;
        modalReturnDate.textContent = returnDateInput.value;
        modalTotalPrice.textContent = totalPriceElement.textContent;

        modalRentalDuration.value = durationSelect.value;
        modalRentalStartDate.value = rentalDateInput.value;
        modalRentalNotes.value = document.getElementById('notes').value || '';
        modalRentalAmount.value = totalPriceElement.textContent.replace('$', '');

        paymentModal.classList.remove('hidden');
    });

    cancelPaymentBtn.addEventListener('click', () => paymentModal.classList.add('hidden'));

    paymentModal.addEventListener('click', function(event) {
        if (event.target === paymentModal) {
            paymentModal.classList.add('hidden');
        }
    });
});