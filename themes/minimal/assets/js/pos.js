// Point of Sale JavaScript
(function() {
  'use strict';

  let currentSale = [];
  let currentProduct = null;
  let qrCode = null;

  // DOM Elements
  const modal = document.getElementById('input-modal');
  const modalProductName = document.getElementById('modal-product-name');
  const modalProductInfo = document.getElementById('modal-product-info');
  const inputLabel = document.getElementById('input-label');
  const quantityInput = document.getElementById('quantity-input');
  const modalSubtotal = document.getElementById('modal-subtotal');
  const cancelBtn = document.getElementById('cancel-btn');
  const addBtn = document.getElementById('add-btn');
  const newSaleBtn = document.getElementById('new-sale');
  const saleItemsContainer = document.getElementById('sale-items');
  const totalAmount = document.getElementById('total-amount');
  const printBtn = document.getElementById('print-receipt');
  const paymentBtn = document.getElementById('payment-btn');
  const saleActions = document.getElementById('sale-actions');
  const paymentModal = document.getElementById('payment-modal');
  const closePaymentBtn = document.getElementById('close-payment');
  const paymentDoneBtn = document.getElementById('payment-done');

  // Event Listeners
  document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', handleProductClick);
  });

  cancelBtn.addEventListener('click', closeModal);
  addBtn.addEventListener('click', addToSale);
  newSaleBtn.addEventListener('click', newSale);
  printBtn.addEventListener('click', printReceipt);
  paymentBtn.addEventListener('click', showPaymentQR);
  closePaymentBtn.addEventListener('click', closePaymentModal);
  paymentDoneBtn.addEventListener('click', handlePaymentDone);
  quantityInput.addEventListener('input', handleQuantityInput);
  quantityInput.addEventListener('keypress', handleEnterKey);

  // Close modals on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modal.classList.contains('active')) {
        closeModal();
      }
      if (paymentModal.classList.contains('active')) {
        closePaymentModal();
      }
    }
  });

  function handleProductClick(e) {
    const card = e.currentTarget;
    currentProduct = {
      id: card.dataset.productId,
      name: card.dataset.productName,
      price: parseFloat(card.dataset.productPrice),
      weight: card.dataset.productWeight,
      packagingGrams: card.dataset.packagingGrams ? parseInt(card.dataset.packagingGrams) : null
    };

    openModal();
  }

  function openModal() {
    modalProductName.textContent = currentProduct.name;
    modalProductInfo.textContent = `€${currentProduct.price.toFixed(2)} ${currentProduct.weight}`;

    // Determine if this is per kg or per piece
    const isPerKg = currentProduct.weight.includes('kg');

    if (isPerKg) {
      inputLabel.textContent = 'Gewicht (kg):';
      quantityInput.step = '0.01';
      quantityInput.placeholder = 'bijv. 0.5';
      quantityInput.inputMode = 'decimal';
      // Pre-fill with packaging weight if available
      if (currentProduct.packagingGrams) {
        quantityInput.value = (currentProduct.packagingGrams / 1000).toFixed(2);
      } else {
        quantityInput.value = '';
      }
    } else {
      inputLabel.textContent = 'Aantal:';
      quantityInput.step = '1';
      quantityInput.placeholder = 'bijv. 2';
      quantityInput.inputMode = 'numeric';
      quantityInput.value = '1';
    }

    modal.classList.add('active');

    // Select all text on focus for easy replacement
    setTimeout(() => {
      quantityInput.focus();
      quantityInput.select();
    }, 100);

    updateModalSubtotal();
  }

  function closeModal() {
    modal.classList.remove('active');
    currentProduct = null;
    quantityInput.value = '';
    modalSubtotal.textContent = '€0.00';
  }

  function handleQuantityInput() {
    // Replace comma with dot for Belgian/European keyboards
    let value = quantityInput.value;
    if (value.includes(',')) {
      // Get cursor position before replacement
      const cursorPos = quantityInput.selectionStart;
      // Replace comma with dot
      quantityInput.value = value.replace(',', '.');
      // Restore cursor position
      quantityInput.setSelectionRange(cursorPos, cursorPos);
    }
    updateModalSubtotal();
  }

  function updateModalSubtotal() {
    // Normalize the input value (replace comma with dot)
    const normalizedValue = quantityInput.value.replace(',', '.');
    const quantity = parseFloat(normalizedValue) || 0;
    const subtotal = quantity * currentProduct.price;
    modalSubtotal.textContent = `€${subtotal.toFixed(2)}`;
  }

  function handleEnterKey(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addToSale();
    }
  }

  function addToSale() {
    // Normalize the input value (replace comma with dot)
    const normalizedValue = quantityInput.value.replace(',', '.');
    const quantity = parseFloat(normalizedValue);

    if (!quantity || quantity <= 0 || isNaN(quantity)) {
      alert('Voer een geldige hoeveelheid in');
      return;
    }

    const isPerKg = currentProduct.weight.includes('kg');
    const displayQuantity = isPerKg ? `${quantity.toFixed(2)} kg` : `${quantity}x`;
    const subtotal = quantity * currentProduct.price;

    const saleItem = {
      productId: currentProduct.id,
      productName: currentProduct.name,
      quantity: quantity,
      displayQuantity: displayQuantity,
      unitPrice: currentProduct.price,
      subtotal: subtotal
    };

    currentSale.push(saleItem);
    closeModal();
    renderSale();
  }

  function renderSale() {
    if (currentSale.length === 0) {
      saleItemsContainer.innerHTML = '<div class="empty-sale">Selecteer een product om te beginnen</div>';
      updateTotal();
      return;
    }

    let html = '<div class="sale-items-list">';

    currentSale.forEach((item, index) => {
      html += `
        <div class="sale-item">
          <div class="sale-item-main">
            <div class="sale-item-name">${item.productName}</div>
            <button class="btn-remove" data-index="${index}" title="Verwijder">×</button>
          </div>
          <div class="sale-item-details">
            <span class="sale-item-quantity">${item.displayQuantity}</span>
            <span class="sale-item-price">× €${item.unitPrice.toFixed(2)}</span>
            <span class="sale-item-subtotal">€${item.subtotal.toFixed(2)}</span>
          </div>
        </div>
      `;
    });

    html += '</div>';
    saleItemsContainer.innerHTML = html;

    // Add remove listeners
    document.querySelectorAll('.btn-remove').forEach(btn => {
      btn.addEventListener('click', function() {
        const index = parseInt(this.dataset.index);
        removeFromSale(index);
      });
    });

    updateTotal();
  }

  function removeFromSale(index) {
    currentSale.splice(index, 1);
    renderSale();
  }

  function updateTotal() {
    const total = currentSale.reduce((sum, item) => sum + item.subtotal, 0);
    totalAmount.textContent = `€${total.toFixed(2)}`;

    // Show/hide action buttons based on whether there are items
    if (currentSale.length > 0) {
      saleActions.style.display = 'flex';
    } else {
      saleActions.style.display = 'none';
    }
  }

  function newSale() {
    if (currentSale.length > 0) {
      if (!confirm('Nieuwe verkoop starten? De huidige verkoop wordt gewist.')) {
        return;
      }
    }
    currentSale = [];
    renderSale();
  }

  function printReceipt() {
    if (currentSale.length === 0) {
      return;
    }

    // Populate receipt date
    const now = new Date();
    const dateStr = now.toLocaleDateString('nl-BE', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    document.getElementById('receipt-date').textContent = dateStr;

    // Populate receipt items
    const receiptItemsContainer = document.getElementById('receipt-items');
    let itemsHtml = '';

    currentSale.forEach(item => {
      itemsHtml += `
        <div class="receipt-item">
          <div class="receipt-item-line1">
            <span>${item.productName}</span>
            <span>€${item.subtotal.toFixed(2)}</span>
          </div>
          <div class="receipt-item-line2">
            <span>${item.displayQuantity}</span>
            <span>@ €${item.unitPrice.toFixed(2)}</span>
          </div>
        </div>
      `;
    });

    receiptItemsContainer.innerHTML = itemsHtml;

    // Populate total
    const total = currentSale.reduce((sum, item) => sum + item.subtotal, 0);
    document.getElementById('receipt-total-amount').textContent = `€${total.toFixed(2)}`;

    // Trigger print
    window.print();
  }

  // Payment QR Code Functions
  function showPaymentQR() {
    if (currentSale.length === 0) {
      return;
    }

    const total = currentSale.reduce((sum, item) => sum + item.subtotal, 0);
    const reference = generatePaymentReference();

    // Update payment modal display
    document.getElementById('payment-amount').textContent = `€${total.toFixed(2)}`;
    document.getElementById('payment-reference').textContent = reference;

    // Clear any existing QR code first
    const container = document.getElementById('qr-container');
    if (qrCode) {
      qrCode.clear();
      qrCode = null;
    }
    container.innerHTML = '';

    // Generate EPC QR Code
    const epcData = generateEPCQRData(total, reference);
    generateQRCode(epcData);

    // Show modal
    paymentModal.classList.add('active');
  }

  function closePaymentModal() {
    paymentModal.classList.remove('active');
    // Clear QR code completely
    const container = document.getElementById('qr-container');
    if (qrCode) {
      qrCode.clear();
      qrCode = null;
    }
    // Also clear the container HTML to remove any remnants
    container.innerHTML = '';
  }

  function handlePaymentDone() {
    // Print receipt automatically after payment
    printReceipt();
    closePaymentModal();

    // Start new sale
    setTimeout(() => {
      currentSale = [];
      renderSale();
    }, 100);
  }

  function generatePaymentReference() {
    // Generate a unique reference based on timestamp
    const now = new Date();
    const dateStr = now.toLocaleDateString('nl-BE').replace(/\//g, '');
    const timeStr = now.toLocaleTimeString('nl-BE', { hour: '2-digit', minute: '2-digit' }).replace(/:/g, '');
    return `POS${dateStr}${timeStr}`;
  }

  function generateEPCQRData(amount, reference) {
    // EPC QR Code format (European Payments Council standard)
    // This format is compatible with most Belgian banking apps
    const config = window.PAYMENT_CONFIG || {};
    const iban = config.iban || 'BE00000000000000';
    const bic = config.bic || 'GEBABEBB';
    const beneficiary = config.beneficiary || 'Akkervarken.be';

    // Format amount with exactly 2 decimals
    const formattedAmount = `EUR${amount.toFixed(2)}`;

    // EPC QR Code structure (each line is a field)
    const epcLines = [
      'BCD',                    // Service Tag
      '002',                    // Version
      '1',                      // Character set (1 = UTF-8)
      'SCT',                    // Identification (SEPA Credit Transfer)
      bic,                      // BIC of beneficiary bank
      beneficiary,              // Name of beneficiary (max 70 chars)
      iban,                     // Account number (IBAN)
      formattedAmount,          // Amount (EUR followed by amount)
      '',                       // Purpose (optional, empty)
      reference,                // Structured reference (max 35 chars)
      `Akkervarken POS ${reference}`, // Unstructured remittance (max 140 chars)
      ''                        // Beneficiary to originator info (optional)
    ];

    return epcLines.join('\n');
  }

  function generateQRCode(data) {
    const container = document.getElementById('qr-container');

    // Clear previous QR code
    if (qrCode) {
      qrCode.clear();
      container.innerHTML = '';
    }

    // Generate new QR code using QRCode.js library
    // QRCode.js automatically creates and appends an element to the container
    qrCode = new QRCode(container, {
      text: data,
      width: 300,
      height: 300,
      colorDark: '#000000',
      colorLight: '#ffffff',
      correctLevel: QRCode.CorrectLevel.M
    });
  }

  // Initialize
  renderSale();
})();
