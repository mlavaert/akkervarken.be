let cart = {};
let currentBatch = null; // Track which batch is currently selected

// Helper function to format price in euros
function formatPrice(price) {
    return '€' + parseFloat(price).toFixed(2).replace('.', ',');
}

function toggleBatch(header) {
    const batch = header.parentElement;
    const content = batch.querySelector('.batch-content');
    const icon = header.querySelector('.toggle-icon');
    const allBatches = document.querySelectorAll('.batch');

    // If this batch is already open, don't close it (keep at least one open)
    if (batch.classList.contains('open')) {
        return;
    }

    // Close all other batches
    allBatches.forEach(otherBatch => {
        if (otherBatch !== batch) {
            otherBatch.classList.remove('open');
            otherBatch.classList.add('closed');
            const otherIcon = otherBatch.querySelector('.toggle-icon');
            otherIcon.textContent = '+';
        }
    });

    // Open this batch
    batch.classList.remove('closed');
    batch.classList.add('open');
    icon.textContent = '−';
}

function updateQuantity(productId, quantity) {
    quantity = parseInt(quantity) || 0;

    // Update the visual display
    const display = document.getElementById(`qty-display-${productId}`);
    const input = document.getElementById(`qty-${productId}`);

    if (display) {
        display.textContent = quantity;
    }
    if (input) {
        input.value = quantity;
    }

    if (quantity <= 0) {
        delete cart[productId];
        // If cart is empty, reset current batch
        if (Object.keys(cart).length === 0) {
            currentBatch = null;
            enableAllBatches();
        }
    } else {
        const product = document.querySelector(`[data-id="${productId}"]`);
        const productBatch = product.dataset.batch;

        // Check if this is from a different batch
        if (currentBatch && currentBatch !== productBatch) {
            alert(`Je kunt alleen producten uit één batch bestellen.\n\nJe hebt al producten uit "${currentBatch}" geselecteerd.\n\nWil je vlees uit meerdere batches? Plaats dan afzonderlijke bestellingen.`);
            // Reset the quantity to 0
            updateQuantity(productId, 0);
            return;
        }

        // Set current batch if this is the first item
        if (!currentBatch) {
            currentBatch = productBatch;
            disableOtherBatches(productBatch);
        }

        cart[productId] = {
            name: product.dataset.name,
            price: parseFloat(product.dataset.price),
            weight: product.dataset.weight,
            pickupStart: product.dataset.pickupStart,
            pickupEnd: product.dataset.pickupEnd,
            batch: product.dataset.batch,
            quantity: quantity
        };
    }
    updateOrderSummary();
}

function disableOtherBatches(selectedBatch) {
    const allBatches = document.querySelectorAll('.batch');
    allBatches.forEach(batch => {
        // Check if any product in this batch matches the selected batch
        const productsInBatch = batch.querySelectorAll('.product');
        let isSameBatch = false;

        productsInBatch.forEach(product => {
            if (product.dataset.batch === selectedBatch) {
                isSameBatch = true;
            }
        });

        if (!isSameBatch) {
            batch.classList.add('disabled');
            // Disable all inputs in this batch
            const inputs = batch.querySelectorAll('input, button');
            inputs.forEach(input => {
                input.disabled = true;
            });
        }
    });
}

function enableAllBatches() {
    const allBatches = document.querySelectorAll('.batch');
    allBatches.forEach(batch => {
        batch.classList.remove('disabled');
        // Enable all inputs in this batch
        const inputs = batch.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = false;
        });
    });
}

function increaseQuantity(productId) {
    const input = document.getElementById(`qty-${productId}`);
    const max = parseInt(input.max);
    const current = parseInt(input.value) || 0;
    if (current < max) {
        input.value = current + 1;
        updateQuantity(productId, input.value);
    }
}

function decreaseQuantity(productId) {
    const input = document.getElementById(`qty-${productId}`);
    const current = parseInt(input.value) || 0;
    if (current > 0) {
        input.value = current - 1;
        updateQuantity(productId, input.value);
    }
}

function updateOrderSummary() {
    const orderItems = document.getElementById('order-items');
    const orderTotal = document.getElementById('order-total');
    const sendButton = document.getElementById('send-order');
    const orderSummary = document.querySelector('.order-summary');
    const batches = document.querySelector('.batches');

    if (Object.keys(cart).length === 0) {
        orderItems.innerHTML = '<p>Geen items geselecteerd</p>';
        orderTotal.innerHTML = '';
        sendButton.style.display = 'none';
        orderSummary.classList.remove('has-items');
        if (batches) {
            batches.classList.remove('has-order');
        }
        return;
    }

    // Add class to show order summary is active
    orderSummary.classList.add('has-items');
    if (batches) {
        batches.classList.add('has-order');
    }

    // Since we only allow one batch, this is simplified
    let html = `<div class="order-batch"><strong>${currentBatch}</strong><ul>`;
    let totalItems = 0;
    let totalPrice = 0;

    for (const [productId, item] of Object.entries(cart)) {
        const itemTotal = item.price * item.quantity;
        totalPrice += itemTotal;
        totalItems += item.quantity;
        html += `<li>${item.quantity}x ${item.name} (${item.weight}) - ${formatPrice(itemTotal)}<br><small>Ophalen: ${item.pickupStart} tot ${item.pickupEnd}</small></li>`;
    }
    html += '</ul></div>';

    orderItems.innerHTML = html;
    orderTotal.innerHTML = `<div class="total-summary"><strong>Totaal:</strong> <span class="total-price">${formatPrice(totalPrice)}</span><br><small>${totalItems} pakket(ten)</small></div>`;
    sendButton.style.display = 'block';
}

function sendOrder() {
    if (Object.keys(cart).length === 0) {
        alert('Selecteer eerst producten om te bestellen.');
        return;
    }

    let emailBody = 'Beste Akkervarken.be,%0D%0A%0D%0A';
    emailBody += 'Hierbij mijn bestelling:%0D%0A%0D%0A';

    let totalItems = 0;
    let totalPrice = 0;

    // Get batch name and pickup dates from first item
    const firstItem = Object.values(cart)[0];
    const batchName = firstItem.batch;
    const pickupStart = firstItem.pickupStart;
    const pickupEnd = firstItem.pickupEnd;

    emailBody += `Batch: ${batchName}%0D%0A`;
    emailBody += `Ophalen tussen: ${pickupStart} en ${pickupEnd}%0D%0A%0D%0A`;
    emailBody += 'Producten:%0D%0A';

    for (const [productId, item] of Object.entries(cart)) {
        const itemTotal = item.price * item.quantity;
        totalPrice += itemTotal;
        totalItems += item.quantity;
        emailBody += `- ${item.quantity}x ${item.name} (${item.weight}) - ${formatPrice(itemTotal)}%0D%0A`;
    }

    emailBody += `%0D%0ATotaal: ${formatPrice(totalPrice)} (${totalItems} pakket(ten))%0D%0A%0D%0A`;
    emailBody += 'Betaling bij afhaling.%0D%0A%0D%0A';
    emailBody += 'Graag bevestiging van deze bestelling.%0D%0A%0D%0A';
    emailBody += 'Met vriendelijke groeten,%0D%0A';
    emailBody += '[Vul hier je naam in]';

    const subject = `Bestelling Akkervarken.be - ${batchName}`;
    const mailtoLink = `mailto:info@akkervarken.be?subject=${encodeURIComponent(subject)}&body=${emailBody}`;

    window.location.href = mailtoLink;
}
