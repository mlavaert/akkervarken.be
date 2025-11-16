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

    // Track the old quantity for analytics
    const oldQuantity = cart[productId] ? cart[productId].quantity : 0;

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
        // Track remove_from_cart event
        if (oldQuantity > 0 && window.gtag) {
            const removedItem = cart[productId];
            window.gtag('event', 'remove_from_cart', {
                currency: 'EUR',
                value: (removedItem.expectedPrice > 0 ? removedItem.expectedPrice : removedItem.price) * removedItem.quantity,
                items: [{
                    item_id: productId,
                    item_name: removedItem.name,
                    item_category: removedItem.batch,
                    price: removedItem.expectedPrice > 0 ? removedItem.expectedPrice : removedItem.price,
                    quantity: removedItem.quantity
                }]
            });
        }

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

        const price = parseFloat(product.dataset.price);
        const expectedPrice = parseFloat(product.dataset.expectedPrice) || 0;

        cart[productId] = {
            name: product.dataset.name,
            price: price,
            weight: product.dataset.weight,
            pickupSlots: JSON.parse(product.dataset.pickupSlots || '[]'),
            batch: product.dataset.batch,
            quantity: quantity,
            packagingPieces: parseInt(product.dataset.packagingPieces) || 0,
            packagingGrams: parseInt(product.dataset.packagingGrams) || 0,
            expectedPrice: expectedPrice
        };

        // Track add_to_cart event (only when item is first added, not on quantity increase)
        if (oldQuantity === 0 && window.gtag) {
            window.gtag('event', 'add_to_cart', {
                currency: 'EUR',
                value: expectedPrice > 0 ? expectedPrice : price,
                items: [{
                    item_id: productId,
                    item_name: product.dataset.name,
                    item_category: productBatch,
                    price: expectedPrice > 0 ? expectedPrice : price,
                    quantity: 1
                }]
            });
        }
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
    const current = parseInt(input.value) || 0;
    input.value = current + 1;
    updateQuantity(productId, input.value);
}

function decreaseQuantity(productId) {
    const input = document.getElementById(`qty-${productId}`);
    const current = parseInt(input.value) || 0;
    if (current > 0) {
        input.value = current - 1;
        updateQuantity(productId, input.value);
    }
}

// Functions for modifying from order summary
function increaseQuantityFromSummary(productId) {
    increaseQuantity(productId);
}

function decreaseQuantityFromSummary(productId) {
    decreaseQuantity(productId);
}

function removeFromCart(productId) {
    // Set quantity to 0 which will remove it from cart
    updateQuantity(productId, 0);
}

function updateOrderSummary() {
    const orderItems = document.getElementById('order-items');
    const orderTotal = document.getElementById('order-total');
    const sendButton = document.getElementById('send-order');
    const orderSummary = document.querySelector('.order-summary');
    const orderSummaryTitle = document.getElementById('order-summary-title');
    const batches = document.querySelector('.batches');
    const termsContainer = document.getElementById('terms-agreement-container');
    const termsCheckbox = document.getElementById('terms-checkbox');

    if (Object.keys(cart).length === 0) {
        orderItems.innerHTML = '<p>Geen items geselecteerd</p>';
        orderTotal.innerHTML = '';
        sendButton.style.display = 'none';
        if (orderSummaryTitle) {
            orderSummaryTitle.textContent = 'Bestelling';
        }
        if (termsContainer) {
            termsContainer.style.display = 'none';
            if (termsCheckbox) {
                termsCheckbox.checked = false;
            }
        }
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

    // Track view_cart event when cart has items
    if (window.gtag) {
        const cartItems = Object.entries(cart).map(([productId, item]) => ({
            item_id: productId,
            item_name: item.name,
            item_category: item.batch,
            price: item.expectedPrice > 0 ? item.expectedPrice : item.price,
            quantity: item.quantity
        }));

        const cartValue = Object.values(cart).reduce((sum, item) => {
            const price = item.expectedPrice > 0 ? item.expectedPrice : item.price;
            return sum + (price * item.quantity);
        }, 0);

        window.gtag('event', 'view_cart', {
            currency: 'EUR',
            value: cartValue,
            items: cartItems
        });
    }

    // Get pickup slots from first item (all items in cart have same pickup slots since only one batch allowed)
    const firstItem = Object.values(cart)[0];
    const pickupSlotsHtml = firstItem.pickupSlots.map(slot => `<div class="pickup-slot-item">${slot.date} om ${slot.time}</div>`).join('');

    // Update the order summary title with batch name
    if (orderSummaryTitle) {
        orderSummaryTitle.innerHTML = `Bestelling <small>(${currentBatch})</small>`;
    }

    // Since we only allow one batch, this is simplified
    let html = `<div class="order-batch"><div class="order-items-list">`;
    let totalItems = 0;
    let totalPrice = 0;

    for (const [productId, item] of Object.entries(cart)) {
        // Use expectedPrice if available (for per kg items), otherwise use the fixed price
        const pricePerItem = item.expectedPrice > 0 ? item.expectedPrice : item.price;
        const itemTotal = pricePerItem * item.quantity;
        totalPrice += itemTotal;
        totalItems += item.quantity;

        // Build packaging info text and price per kg info
        let packagingText = '';
        let pricePerKgText = '';

        if (item.expectedPrice > 0) {
            // For per kg items, show packaging and price per kg
            if (item.packagingGrams > 0) {
                if (item.packagingPieces > 1) {
                    packagingText = `<span class="order-item-packaging">${item.packagingPieces} stuks × ±${item.packagingGrams}g</span>`;
                } else {
                    packagingText = `<span class="order-item-packaging">±${item.packagingGrams}g per pakket</span>`;
                }
            }
            pricePerKgText = `<span class="order-item-per-kg">${formatPrice(item.price)}/kg</span>`;
        } else {
            // For fixed-price items
            if (item.packagingGrams > 0) {
                if (item.packagingPieces > 1) {
                    packagingText = `<span class="order-item-packaging">${item.packagingPieces} stuks × ±${item.packagingGrams}g</span>`;
                } else {
                    packagingText = `<span class="order-item-packaging">±${item.packagingGrams}g</span>`;
                }
            }
        }

        html += `
            <div class="order-item">
                <div class="order-item-info">
                    <div class="order-item-name">${item.name}</div>
                    <div class="order-item-details">
                        ${packagingText}
                        ${pricePerKgText}
                        <span class="order-item-price">${formatPrice(itemTotal)}</span>
                    </div>
                </div>
                <div class="order-item-controls">
                    <button type="button" class="order-qty-btn" onclick="decreaseQuantityFromSummary('${productId}')" ${item.quantity <= 1 ? '' : ''}>−</button>
                    <span class="order-qty-display">${item.quantity}</span>
                    <button type="button" class="order-qty-btn" onclick="increaseQuantityFromSummary('${productId}')">+</button>
                    <button type="button" class="order-remove-btn" onclick="removeFromCart('${productId}')" title="Verwijderen">×</button>
                </div>
            </div>
        `;
    }
    html += '</div></div>';

    orderItems.innerHTML = html;
    orderTotal.innerHTML = `
        <div class="order-summary-footer">
            <div class="pickup-info">
                <div class="pickup-batch"><strong>Batch:</strong> ${currentBatch}</div>
                <div class="pickup-slots">
                    <div class="pickup-slots-header">📦 <strong>Ophalen:</strong></div>
                    ${pickupSlotsHtml}
                </div>
            </div>
            <div class="total-summary">
                <div class="total-label">Totaal:</div>
                <div class="total-amount">
                    <span class="total-price">${formatPrice(totalPrice)}</span>
                    <small>${totalItems} pakket(ten)</small>
                </div>
            </div>
        </div>
    `;

    // Show terms agreement container
    if (termsContainer) {
        termsContainer.style.display = 'block';
    }

    // Enable/disable send button based on checkbox state
    toggleSendButton();
}

function toggleSendButton() {
    const sendButton = document.getElementById('send-order');
    const termsCheckbox = document.getElementById('terms-checkbox');

    if (sendButton && termsCheckbox) {
        if (termsCheckbox.checked) {
            sendButton.disabled = false;
            sendButton.style.display = 'block';
        } else {
            sendButton.disabled = true;
            sendButton.style.display = 'block';
        }
    }
}

function sendOrder() {
    if (Object.keys(cart).length === 0) {
        alert('Selecteer eerst producten om te bestellen.');
        return;
    }

    // Check if terms are accepted
    const termsCheckbox = document.getElementById('terms-checkbox');
    if (termsCheckbox && !termsCheckbox.checked) {
        alert('Je moet akkoord gaan met de algemene voorwaarden om te bestellen.');
        return;
    }

    // Build email body with regular newlines first
    let emailBody = 'Beste Akkervarken.be,\n\n';
    emailBody += 'Hierbij mijn bestelling:\n\n';

    let totalItems = 0;
    let totalPrice = 0;

    // Get batch name and pickup slots from first item
    const firstItem = Object.values(cart)[0];
    const batchName = firstItem.batch;
    const pickupSlots = firstItem.pickupSlots;

    emailBody += `Batch: ${batchName}\n`;
    emailBody += 'Ophaalmomenten:\n';
    pickupSlots.forEach(slot => {
        emailBody += `  - ${slot.date} om ${slot.time}\n`;
    });
    emailBody += '\nProducten:\n';

    for (const [productId, item] of Object.entries(cart)) {
        // Use expectedPrice if available (for per kg items), otherwise use the fixed price
        const pricePerItem = item.expectedPrice > 0 ? item.expectedPrice : item.price;
        const itemTotal = pricePerItem * item.quantity;
        totalPrice += itemTotal;
        totalItems += item.quantity;

        // Build packaging info for email
        let packagingInfo = '';
        let priceInfo = '';

        if (item.packagingGrams > 0 && item.expectedPrice > 0) {
            // For per kg items, show packaging and price per kg
            if (item.packagingPieces > 1) {
                packagingInfo = ` (${item.packagingPieces} stuks × ±${item.packagingGrams}g, ${formatPrice(item.expectedPrice)}/pakket)`;
            } else {
                packagingInfo = ` (±${item.packagingGrams}g, ${formatPrice(item.expectedPrice)}/pakket)`;
            }
            priceInfo = ` @ ${formatPrice(item.price)}/kg`;
        } else {
            // For fixed-price items, just show the unit
            packagingInfo = item.packagingGrams > 0 && item.packagingPieces > 1
                ? ` (${item.packagingPieces} stuks)`
                : '';
            priceInfo = ` (${item.weight})`;
        }

        emailBody += `- ${item.quantity}x ${item.name}${packagingInfo}${priceInfo} - ${formatPrice(itemTotal)}\n`;
    }

    emailBody += `\nTotaal: ${formatPrice(totalPrice)} (${totalItems} pakket(ten))\n\n`;
    emailBody += 'Betaling bij afhaling.\n\n';
    emailBody += 'Graag bevestiging van deze bestelling.\n\n';
    emailBody += 'Met vriendelijke groeten,\n';
    emailBody += '[Vul hier je naam in]';

    const subject = `Bestelling Akkervarken.be - ${batchName}`;
    // Properly encode both subject and body
    const mailtoLink = `mailto:info@akkervarken.be?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`;

    // Track conversion event with Google Analytics
    if (window.gtag) {
        // GA4 e-commerce event (can be imported as conversion in Google Ads when linked)
        window.gtag('event', 'begin_checkout', {
            currency: 'EUR',
            value: totalPrice,
            items: Object.entries(cart).map(([productId, item]) => ({
                item_id: productId,
                item_name: item.name,
                item_category: batchName,
                price: item.expectedPrice > 0 ? item.expectedPrice : item.price,
                quantity: item.quantity
            }))
        });
    }

    window.location.href = mailtoLink;
}

// Track view_item_list event when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.gtag) {
        const products = document.querySelectorAll('.product');
        const items = [];

        products.forEach((product, index) => {
            const productId = product.dataset.id;
            const productName = product.dataset.name;
            const productPrice = parseFloat(product.dataset.price);
            const productBatch = product.dataset.batch;
            const expectedPrice = parseFloat(product.dataset.expectedPrice) || 0;

            items.push({
                item_id: productId,
                item_name: productName,
                item_category: productBatch,
                price: expectedPrice > 0 ? expectedPrice : productPrice,
                index: index
            });
        });

        if (items.length > 0) {
            window.gtag('event', 'view_item_list', {
                item_list_id: 'webshop_products',
                item_list_name: 'Webshop Producten',
                items: items
            });
        }
    }
});
