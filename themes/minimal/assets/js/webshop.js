let cart = {};
let currentBatch = null;

// Helper functions
function formatPrice(price) {
    return '€' + parseFloat(price).toFixed(2).replace('.', ',');
}

function getItemPrice(item) {
    return item.expectedPrice > 0 ? item.expectedPrice : item.price;
}

function calculateCartTotals() {
    let totalItems = 0;
    let totalPrice = 0;
    Object.values(cart).forEach(item => {
        totalItems += item.quantity;
        totalPrice += getItemPrice(item) * item.quantity;
    });
    return { totalItems, totalPrice };
}

// Scroll to a specific batch and open it
function scrollToBatch(batchId) {
    const batchElement = document.getElementById(batchId);
    if (batchElement) {
        // Open the batch if it's closed
        if (batchElement.classList.contains('closed')) {
            const header = batchElement.querySelector('.batch-header');
            if (header) {
                toggleBatch(header);
            }
        }
        // Scroll to the batch with offset for sticky header
        const yOffset = -20;
        const y = batchElement.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: 'smooth' });
    }
}

function toggleBatch(header) {
    const batch = header.parentElement;
    const icon = header.querySelector('.toggle-icon');

    // If this batch is already open, don't close it (keep at least one open)
    if (batch.classList.contains('open')) return;

    // Close all other batches
    document.querySelectorAll('.batch').forEach(otherBatch => {
        if (otherBatch !== batch) {
            otherBatch.classList.remove('open');
            otherBatch.classList.add('closed');
            otherBatch.querySelector('.toggle-icon').textContent = '+';
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
        // Track removal if item was in cart
        if (oldQuantity > 0 && window.Analytics) {
            window.Analytics.trackRemoveFromCart(productId, cart[productId]);
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
        const batchType = product.dataset.batchType || 'regular';

        // Get pickup info - either slots (for batches) or text (for freezer)
        let pickupSlots = [];
        let pickupText = '';

        if (batchType === 'freezer') {
            pickupText = JSON.parse(product.dataset.pickupText || '""');
        } else {
            pickupSlots = JSON.parse(product.dataset.pickupSlots || '[]');
        }

        cart[productId] = {
            name: product.dataset.name,
            price: price,
            weight: product.dataset.weight,
            pickupSlots: pickupSlots,
            pickupText: pickupText,
            batch: product.dataset.batch,
            batchType: batchType,
            quantity: quantity,
            packagingPieces: parseInt(product.dataset.packagingPieces) || 0,
            packagingGrams: parseInt(product.dataset.packagingGrams) || 0,
            expectedPrice: expectedPrice
        };

        // Track add to cart (only when item is first added)
        if (oldQuantity === 0 && window.Analytics) {
            window.Analytics.trackAddToCart(productId, {
                name: product.dataset.name,
                price: price,
                expectedPrice: expectedPrice
            }, productBatch);
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

function updateOrderSummary() {
    const orderItems = document.getElementById('order-items');
    const orderSummary = document.querySelector('.order-summary');
    const batches = document.querySelector('.batches');

    if (Object.keys(cart).length === 0) {
        orderItems.innerHTML = '';
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

    const { totalItems, totalPrice } = calculateCartTotals();

    // Track view_cart event when cart has items
    if (window.Analytics) {
        window.Analytics.trackViewCart(cart, totalPrice);
    }

    // Compact summary - single line layout
    orderItems.innerHTML = `
        <div class="compact-cart-summary">
            <span class="cart-batch-name">${currentBatch}</span>
            <span class="cart-separator">|</span>
            <span class="cart-item-count">${totalItems} stuks</span>
            <span class="cart-total-price">${formatPrice(totalPrice)}</span>
            <button id="send-order" onclick="showCheckout()">Bestellen</button>
        </div>
    `;
}

function showCheckout() {
    if (Object.keys(cart).length === 0) {
        alert('Selecteer eerst producten om te bestellen.');
        return;
    }

    // Populate checkout order summary
    populateCheckoutSummary();

    // Show the checkout overlay
    const overlay = document.getElementById('checkout-overlay');
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling

    // Clear any previous form inputs
    document.getElementById('form-name').value = '';
    document.getElementById('form-phone').value = '';
    document.getElementById('form-notes').value = '';
    document.getElementById('checkout-terms-checkbox').checked = false;

    // Update submit button state
    updateCheckoutSubmitButton();

    // Track begin_checkout event
    if (window.Analytics) {
        const firstItem = Object.values(cart)[0];
        const batchName = firstItem.batch;
        const { totalPrice } = calculateCartTotals();

        window.Analytics.trackBeginCheckout(cart, batchName, totalPrice);
    }
}

function hideCheckout() {
    const overlay = document.getElementById('checkout-overlay');

    // Track checkout abandonment if cart has items
    if (Object.keys(cart).length > 0 && window.Analytics) {
        const { totalPrice } = calculateCartTotals();
        window.Analytics.trackCheckoutAbandonment('user_cancelled', cart, totalPrice);
    }

    overlay.style.display = 'none';
    document.body.style.overflow = ''; // Restore scrolling
}

function populateCheckoutSummary() {
    const checkoutItems = document.getElementById('checkout-order-items');
    const checkoutTotal = document.getElementById('checkout-order-total');

    // Get batch name and pickup info from first item
    const firstItem = Object.values(cart)[0];
    const batchName = firstItem.batch;
    const batchType = firstItem.batchType || 'regular';

    // Build pickup info text
    let pickupInfo = '';
    if (batchType === 'freezer') {
        pickupInfo = firstItem.pickupText;
    } else {
        pickupInfo = firstItem.pickupSlots.map(slot => `${slot.date} om ${slot.time}`).join(', ');
    }

    const { totalItems, totalPrice } = calculateCartTotals();
    let html = '<div class="order-items-list">';
    let orderDetails = '';

    for (const [productId, item] of Object.entries(cart)) {
        const pricePerItem = getItemPrice(item);
        const itemTotal = pricePerItem * item.quantity;

        // Build packaging info text
        let packagingText = '';
        if (item.expectedPrice > 0) {
            // For per kg items
            if (item.packagingGrams > 0) {
                if (item.packagingPieces > 1) {
                    packagingText = `${item.packagingPieces} stuks × ±${item.packagingGrams}g`;
                } else {
                    packagingText = `±${item.packagingGrams}g`;
                }
            }
        } else {
            // For fixed-price items
            if (item.packagingGrams > 0 && item.packagingPieces > 1) {
                packagingText = `${item.packagingPieces} stuks`;
            }
        }

        html += `
            <div class="order-item">
                <div class="order-item-info">
                    <div class="order-item-name">${item.name}</div>
                    <div class="order-item-details">
                        ${packagingText ? `<span class="order-item-packaging-small">${packagingText}</span>` : ''}
                        <span class="order-item-price">${formatPrice(itemTotal)}</span>
                    </div>
                </div>
                <div class="order-item-controls">
                    <button type="button" class="order-qty-btn-small" onclick="decreaseQuantityFromCheckout('${productId}')">−</button>
                    <span class="order-qty-display-small" id="checkout-qty-${productId}">${item.quantity}</span>
                    <button type="button" class="order-qty-btn-small" onclick="increaseQuantityFromCheckout('${productId}')">+</button>
                </div>
            </div>
        `;
    }
    html += '</div>';

    checkoutItems.innerHTML = html;
    checkoutTotal.innerHTML = `
        <div class="pickup-batch"><strong>Batch:</strong> ${batchName}</div>
        <div class="pickup-info-text"><strong>📦 Ophalen:</strong> ${pickupInfo}</div>
        <div class="total-line">
            <span class="total-label">Totaal:</span>
            <span class="total-price">${formatPrice(totalPrice)}</span>
        </div>
        <div class="total-items">${totalItems} pakket(ten)</div>
    `;
}

function increaseQuantityFromCheckout(productId) {
    increaseQuantity(productId);
    // Update the checkout display
    const checkoutQty = document.getElementById(`checkout-qty-${productId}`);
    if (checkoutQty && cart[productId]) {
        checkoutQty.textContent = cart[productId].quantity;
    }
    // Refresh checkout summary to update totals
    populateCheckoutSummary();
}

function decreaseQuantityFromCheckout(productId) {
    decreaseQuantity(productId);

    // If item was removed, refresh the entire checkout
    if (!cart[productId]) {
        if (Object.keys(cart).length === 0) {
            // Cart is empty, close checkout
            hideCheckout();
        } else {
            // Refresh checkout summary
            populateCheckoutSummary();
        }
    } else {
        // Update the checkout display
        const checkoutQty = document.getElementById(`checkout-qty-${productId}`);
        if (checkoutQty) {
            checkoutQty.textContent = cart[productId].quantity;
        }
        // Refresh checkout summary to update totals
        populateCheckoutSummary();
    }
}

function updateCheckoutSubmitButton() {
    const submitBtn = document.getElementById('checkout-submit');
    const termsCheckbox = document.getElementById('checkout-terms-checkbox');
    const nameInput = document.getElementById('form-name');

    if (submitBtn && termsCheckbox && nameInput) {
        const isValid = termsCheckbox.checked &&
                       nameInput.value.trim() !== '';
        submitBtn.disabled = !isValid;
    }
}

function buildOrderEmailBody(name, phone, notes) {
    // Build email body
    let emailBody = 'Beste Akkervarken.be,\n\n';
    emailBody += 'Hierbij mijn bestelling:\n\n';

    // Get batch info for pickup details and subject
    const firstItem = Object.values(cart)[0];
    const batchName = firstItem.batch;
    const batchType = firstItem.batchType || 'regular';

    // List products first
    emailBody += 'Producten:\n';

    let totalItems = 0;
    let totalPrice = 0;

    for (const [productId, item] of Object.entries(cart)) {
        const pricePerItem = getItemPrice(item);
        const itemTotal = pricePerItem * item.quantity;
        totalPrice += itemTotal;
        totalItems += item.quantity;

        // Build price info for email
        let priceInfo = '';

        if (item.packagingGrams > 0 && item.expectedPrice > 0) {
            // For per kg items, show price per kg
            priceInfo = ` @ ${formatPrice(item.price)}/kg`;
        } else {
            // For fixed-price items, no additional price info
            priceInfo = '';
        }

        emailBody += `- ${item.quantity}x ${item.name}${priceInfo} - ${formatPrice(itemTotal)}\n`;
    }

    emailBody += `\nTotaal: ${formatPrice(totalPrice)} (${totalItems} stuks)\n\n`;

    // Pickup information
    if (batchType === 'freezer') {
        emailBody += `Ophalen: ${firstItem.pickupText}\n\n`;
    } else {
        emailBody += 'Ophaalmomenten:\n';
        firstItem.pickupSlots.forEach(slot => {
            emailBody += `  - ${slot.date} om ${slot.time}\n`;
        });
        emailBody += '\n';
    }

    emailBody += 'Betaling bij afhaling.\n\n';

    if (notes) {
        emailBody += `Opmerkingen:\n${notes}\n\n`;
    }

    emailBody += 'Graag bevestiging van deze bestelling.\n\n';
    emailBody += 'Met vriendelijke groeten,\n';
    emailBody += name;
    if (phone) {
        emailBody += `\n${phone}`;
    }

    return { emailBody, batchName, totalPrice };
}

function showMailtoFallback(emailBody, subject) {
    // Get phone number from overlay data attribute
    const overlay = document.getElementById('checkout-overlay');
    const phoneNumber = overlay.dataset.phone || '+32494185076';
    const phoneDisplay = phoneNumber;
    const whatsappLink = `https://wa.me/${phoneNumber.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(emailBody)}`;

    // Replace the checkout content with fallback instructions
    const checkoutContent = document.querySelector('.checkout-content');
    checkoutContent.innerHTML = `
        <div style="grid-column: 1 / -1;">
            <div class="mailto-fallback">
                <h4>⚠️ E-mailclient niet beschikbaar</h4>
                <p class="mailto-fallback-text">
                    Het lijkt erop dat je geen e-mailclient hebt geconfigureerd. Geen probleem!<br>
                    <strong>Verstuur je bestelling eenvoudig via WhatsApp of kopieer de gegevens handmatig.</strong>
                </p>

                <div class="fallback-actions" style="margin-bottom: 24px;">
                    <a href="${whatsappLink}"
                       target="_blank"
                       class="btn-whatsapp btn-whatsapp-large"
                       style="text-decoration: none;"
                       onclick="if(window.Analytics)window.Analytics.trackContact('whatsapp','${phoneNumber}')">
                        <span>💬</span>
                        <span>Verstuur via WhatsApp</span>
                    </a>
                    <a href="mailto:info@akkervarken.be?subject=${encodeURIComponent(subject)}"
                       class="btn-copy"
                       style="text-decoration: none;"
                       onclick="if(window.Analytics)window.Analytics.trackOrderFallback('retry_mailto')">
                        <span>✉️</span>
                        <span>Open e-mail opnieuw</span>
                    </a>
                </div>

                <details style="margin-top: 24px;">
                    <summary style="cursor: pointer; padding: 12px; background: rgba(133, 100, 4, 0.1); border-radius: 8px; margin-bottom: 12px; font-weight: 600; color: #856404;">
                        📋 Of kopieer de bestelling handmatig
                    </summary>
                    <div>
                        <p class="mailto-fallback-text" style="margin-bottom: 12px;">
                            Hieronder vind je alle details van je bestelling. Kopieer deze en plak ze in een e-mail naar <strong>info@akkervarken.be</strong>:
                        </p>

                        <div class="order-details-box" id="order-details-text">${emailBody}</div>

                        <button class="btn-copy" onclick="copyOrderDetails()" style="width: 100%; justify-content: center; margin-top: 12px;">
                            <span>📋</span>
                            <span id="copy-btn-text">Kopieer bestelling</span>
                        </button>
                    </div>
                </details>

                <div class="contact-info-box" style="margin-top: 24px;">
                    <strong>Direct contact:</strong><br>
                    📞 Bel ons op <a href="tel:${phoneNumber}" style="color: #6a8e6a; font-weight: 600;" onclick="if(window.Analytics)window.Analytics.trackContact('phone','${phoneNumber}')">${phoneDisplay}</a>
                </div>
            </div>
        </div>
    `;
}

function copyOrderDetails() {
    const orderText = document.getElementById('order-details-text').textContent;
    const copyBtn = document.getElementById('copy-btn-text');
    const copyButton = event.currentTarget;

    // Track copy action
    if (window.Analytics) {
        window.Analytics.trackOrderFallback('copy_order');
    }

    navigator.clipboard.writeText(orderText).then(() => {
        // Show success state
        copyBtn.textContent = '✓ Gekopieerd!';
        copyButton.classList.add('copied');

        // Reset after 3 seconds
        setTimeout(() => {
            copyBtn.textContent = 'Kopieer bestelling';
            copyButton.classList.remove('copied');
        }, 3000);
    }).catch(err => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = orderText;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            copyBtn.textContent = '✓ Gekopieerd!';
            copyButton.classList.add('copied');
            setTimeout(() => {
                copyBtn.textContent = 'Kopieer bestelling';
                copyButton.classList.remove('copied');
            }, 3000);
        } catch (err) {
            alert('Kopiëren mislukt. Selecteer de tekst handmatig en druk op Ctrl+C (of Cmd+C op Mac).');
        }
        document.body.removeChild(textArea);
    });
}

function submitOrder() {
    if (Object.keys(cart).length === 0) {
        alert('Selecteer eerst producten om te bestellen.');
        return;
    }

    // Get form values
    const name = document.getElementById('form-name').value.trim();
    const phone = document.getElementById('form-phone').value.trim();
    const notes = document.getElementById('form-notes').value.trim();
    const termsCheckbox = document.getElementById('checkout-terms-checkbox');

    // Validate
    if (!name) {
        alert('Vul alstublieft je naam in.');
        return;
    }

    if (!termsCheckbox.checked) {
        alert('Je moet akkoord gaan met de algemene voorwaarden om te bestellen.');
        return;
    }

    // Build email body
    const { emailBody, batchName, totalPrice } = buildOrderEmailBody(name, phone, notes);
    const subject = `Bestelling Akkervarken.be - ${batchName}`;
    const mailtoLink = `mailto:info@akkervarken.be?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`;

    // Track conversion event
    if (window.Analytics) {
        window.Analytics.trackPurchase(cart, batchName, totalPrice);
    }

    // Instead of trying to detect failure, show a helper message
    // and give users an easy way to access the fallback if needed
    showOrderConfirmationWithFallback(emailBody, subject, mailtoLink);
}

function showOrderConfirmationWithFallback(emailBody, subject, mailtoLink) {
    // Replace checkout content with confirmation and fallback option
    const checkoutContent = document.querySelector('.checkout-content');

    // Get phone number for WhatsApp
    const overlay = document.getElementById('checkout-overlay');
    const phoneNumber = overlay.dataset.phone || '+32494185076';
    const whatsappLink = `https://wa.me/${phoneNumber.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(emailBody)}`;

    checkoutContent.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px;">
            <div style="font-size: 3em; margin-bottom: 20px;">✅</div>
            <h3 style="color: #6a8e6a; margin-bottom: 16px;">Bestelling wordt geopend in je e-mailprogramma</h3>
            <p style="color: #6b7c6b; margin-bottom: 24px; line-height: 1.6;">
                Je e-mailprogramma zou nu moeten openen met een vooraf ingevulde bestelling.<br>
                Controleer de gegevens en verstuur de e-mail om je bestelling af te ronden.
            </p>

            <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px;">
                <a href="${mailtoLink}" class="btn-primary" style="text-decoration: none;" onclick="if(window.Analytics)window.Analytics.trackOrderFallback('reopen_mailto')">
                    ✉️ Open e-mail opnieuw
                </a>
                <a href="${whatsappLink}" target="_blank" class="btn-whatsapp" style="text-decoration: none;" onclick="if(window.Analytics)window.Analytics.trackContact('whatsapp','${phoneNumber}')">
                    💬 Verstuur via WhatsApp
                </a>
            </div>

            <details style="max-width: 600px; margin: 0 auto; text-align: left;">
                <summary style="cursor: pointer; padding: 12px; background: rgba(106, 142, 106, 0.05); border-radius: 8px; margin-bottom: 12px;">
                    <strong style="color: #6a8e6a;">❓ Werkt het niet? Klik hier voor meer opties</strong>
                </summary>
                <div style="padding: 16px; background: rgba(106, 142, 106, 0.03); border-radius: 8px; margin-top: 12px;">
                    <p style="margin-bottom: 16px; color: #6b7c6b;">
                        Als je e-mailprogramma niet opent, kan je ook:
                    </p>
                    <button type="button" class="btn-secondary" style="width: 100%; margin-bottom: 12px;" onclick="if(window.Analytics)window.Analytics.trackOrderFallback('manual_send');showManualFallback('${encodeURIComponent(emailBody)}', '${encodeURIComponent(subject)}')">
                        📋 Kopieer bestelling om handmatig te versturen
                    </button>
                    <p style="color: #6b7c6b; font-size: 0.9em; margin-top: 12px;">
                        Of neem direct contact op via telefoon: <a href="tel:${phoneNumber}" style="color: #6a8e6a; font-weight: 600;">${phoneNumber}</a>
                    </p>
                </div>
            </details>
        </div>
    `;

    // Automatically try to open mailto
    window.location.href = mailtoLink;
}

function showManualFallback(encodedEmailBody, encodedSubject) {
    const emailBody = decodeURIComponent(encodedEmailBody);
    const subject = decodeURIComponent(encodedSubject);
    showMailtoFallback(emailBody, subject);
}

// Track view_item_list event when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (window.Analytics) {
        const productElements = document.querySelectorAll('.product');
        const products = [];

        productElements.forEach((product) => {
            products.push({
                id: product.dataset.id,
                name: product.dataset.name,
                price: parseFloat(product.dataset.price),
                batch: product.dataset.batch,
                expectedPrice: parseFloat(product.dataset.expectedPrice) || 0
            });
        });

        if (products.length > 0) {
            window.Analytics.trackProductList(products);
        }
    }
});
