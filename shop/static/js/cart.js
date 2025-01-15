function changeQuantity(itemId, change, stock) {
    const quantityInput = document.getElementById(`quantity-${itemId}`);
    const incrementButton = document.getElementById(`increment-${itemId}`);
    const stockError = document.getElementById(`stock-error-${itemId}`);
    let newQuantity = parseInt(quantityInput.value) + change;

    if (newQuantity < 1) newQuantity = 1;
    if (newQuantity > stock) {
        stockError.classList.remove('hidden');
        stockError.textContent = `Maximum quantity reached. Only ${stock} items available.`;
        newQuantity = stock;
    } else {
        stockError.classList.add('hidden');
    }

    quantityInput.value = newQuantity;

    if (newQuantity >= stock) {
        incrementButton.disabled = true;
        incrementButton.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        incrementButton.disabled = false;
        incrementButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    updateTotal(itemId, stock);

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: newQuantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            quantityInput.value = newQuantity;
            updateTotal(itemId, stock);
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function validateQuantity(itemId, stock) {
    const quantityInput = document.getElementById(`quantity-${itemId}`);
    const incrementButton = document.getElementById(`increment-${itemId}`);
    const stockError = document.getElementById(`stock-error-${itemId}`);
    let newQuantity = parseInt(quantityInput.value);

    if (newQuantity > stock) {
        stockError.classList.remove('hidden');
        stockError.textContent = `Maximum quantity reached. Only ${stock} items available.`;
        newQuantity = stock;
    } else {
        stockError.classList.add('hidden');
    }

    quantityInput.value = newQuantity;

    if (newQuantity >= stock) {
        incrementButton.disabled = true;
        incrementButton.classList.add('opacity-50', 'cursor-not-allowed');
    } else {
        incrementButton.disabled = false;
        incrementButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }

    updateTotal(itemId, stock);
}

function updateTotal(itemId, stock) {
    const quantityInput = document.getElementById(`quantity-${itemId}`);
    const quantity = parseInt(quantityInput.value);

    if (quantity > stock) {
        document.getElementById(`stock-error-${itemId}`).classList.remove('hidden');
        document.getElementById(`stock-error-${itemId}`).textContent = `Only ${stock} items available.`;
        quantityInput.value = stock;
        return;
    } else {
        document.getElementById(`stock-error-${itemId}`).classList.add('hidden');
    }

    const pricePerDay = parseFloat(document.querySelector(`tr[data-item-id="${itemId}"] td:nth-child(3)`).textContent.replace('$', ''));
    const totalPrice = (pricePerDay * quantity).toFixed(2);
    document.getElementById(`total-${itemId}`).textContent = `$${totalPrice}`;

    let subtotal = 0;
    document.querySelectorAll('tbody tr').forEach(row => {
        const total = parseFloat(row.querySelector('td:nth-child(5)').textContent.replace('$', ''));
        subtotal += total;
    });
    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('total-price').textContent = `$${subtotal.toFixed(2)}`;
    document.querySelector('input[name="cart_total"]').value = subtotal.toFixed(2);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function openCheckoutModal() {
    document.getElementById('modalBackdrop').classList.add('active');
    document.getElementById('checkoutModal').classList.add('active');
}

function closeModal() {
    document.getElementById('modalBackdrop').classList.remove('active');
    document.getElementById('checkoutModal').classList.remove('active');
}

function updateRentalType() {
    const rentalType = document.querySelector('input[name="rental_type"]:checked').value;
    const togetherSection = document.getElementById('togetherRental');
    const individualSection = document.getElementById('individualRental');
    
    if (rentalType === 'together') {
        togetherSection.classList.remove('hidden');
        individualSection.classList.add('hidden');
    } else {
        togetherSection.classList.add('hidden');
        individualSection.classList.remove('hidden');
    }
    updateTotalPrice();
}

function calculateReturnDate(input) {
    const form = document.getElementById('rentalForm');
    const startDateInput = form.querySelector('[name="rental_date"]');
    const durationInput = form.querySelector('[name="duration"]');
    
    if (startDateInput.value && durationInput.value) {
        const startDate = new Date(startDateInput.value);
        const duration = parseInt(durationInput.value);
        const returnDate = new Date(startDate);
        returnDate.setDate(returnDate.getDate() + duration);
        
        form.querySelector('[name="return_date"]').value = returnDate.toISOString().split('T')[0];
        
        document.querySelectorAll('#individualRental input[type="hidden"][name="cart_items"]').forEach(input => {
            const itemId = input.value;
            document.querySelector(`[name="rental_date_${itemId}"]`).value = startDateInput.value;
            document.querySelector(`[name="return_date_${itemId}"]`).value = returnDate.toISOString().split('T')[0];
            document.querySelector(`[name="durations_${itemId}"]`).value = duration;
        });
        
        updateTotalPrice();
    }
}

function calculateIndividualPrice(itemId) {
    const startDateInput = document.querySelector(`[name="rental_date_${itemId}"]`);
    const durationInput = document.querySelector(`[name="durations_${itemId}"]`);
    const returnDateInput = document.querySelector(`[name="return_date_${itemId}"]`);
    
    if (startDateInput.value && durationInput.value) {
        const startDate = new Date(startDateInput.value);
        const duration = parseInt(durationInput.value);
        const returnDate = new Date(startDate);
        returnDate.setDate(returnDate.getDate() + duration);
        
        returnDateInput.value = returnDate.toISOString().split('T')[0];
        
        const pricePerDay = parseFloat(document.querySelector(`[name="price_${itemId}"]`).value);
        const totalPrice = (pricePerDay * duration).toFixed(2);
        document.getElementById(`total_${itemId}`).value = `$${totalPrice}`;
        
        updateTotalPrice();
    }
}

function updateTotalPrice() {
    const rentalType = document.querySelector('input[name="rental_type"]:checked').value;
    let total = 0;

    if (rentalType === 'together') {
        const duration = parseInt(document.querySelector('[name="duration"]').value) || 1;
        document.querySelectorAll('input[name="cart_items"]').forEach(input => {
            const itemId = input.value;
            const pricePerDay = parseFloat(document.querySelector(`[name="price_${itemId}"]`).value);
            total += pricePerDay * duration;
        });
    } else {
        document.querySelectorAll('input[name^="durations_"]').forEach((input, index) => {
            const itemId = document.querySelectorAll('input[name="cart_items"]')[index].value;
            const duration = parseInt(input.value) || 1;
            const pricePerDay = parseFloat(document.querySelector(`[name="price_${itemId}"]`).value);
            total += pricePerDay * duration;
        });
    }

    document.getElementById('modalTotal').textContent = `$${total.toFixed(2)}`;
    document.querySelector('input[name="cart_total"]').value = total.toFixed(2);
}

document.getElementById('modalBackdrop').addEventListener('click', closeModal);