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
  const productGrid = document.getElementById('product-grid');

  // Fetch and render products from API
  async function loadProducts() {
    try {
      const apiUrl = window.API_URL || 'https://api.akkervarken.be';
      const response = await fetch(`${apiUrl}/api/products`);

      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }

      const products = await response.json();

      // Clear loading message
      productGrid.innerHTML = '';

      // Render products
      products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.dataset.productId = product.slug;
        card.dataset.productName = product.name;
        card.dataset.productPrice = product.price;
        card.dataset.productWeight = product.weight_display;
        card.dataset.packagingGrams = product.unit_grams || '';

        card.innerHTML = `
          <div class="product-name">${product.name}</div>
          <div class="product-price">€${product.price.toFixed(2)}</div>
          <div class="product-weight">${product.weight_display}</div>
        `;

        card.addEventListener('click', handleProductClick);
        productGrid.appendChild(card);
      });

    } catch (error) {
      console.error('Error loading products:', error);
      productGrid.innerHTML = '<div class="error-message">Fout bij laden van producten. Ververs de pagina.</div>';
    }
  }

  // Event Listeners
  // Product cards will be attached dynamically after loading

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
      quantityInput.placeholder = 'bijv. 0,5';
      quantityInput.inputMode = 'decimal';
      // Pre-fill with packaging weight if available
      if (currentProduct.packagingGrams) {
        quantityInput.value = (currentProduct.packagingGrams / 1000).toFixed(2);
      } else {
        quantityInput.value = '';
      }
    } else {
      inputLabel.textContent = 'Aantal:';
      quantityInput.placeholder = 'bijv. 2';
      quantityInput.inputMode = 'numeric';
      quantityInput.value = '1';
    }

    modal.classList.add('active');

    // Focus and select input for immediate typing
    // Use longer timeout on mobile for better keyboard handling
    setTimeout(() => {
      quantityInput.focus();
      // Delay select slightly to ensure focus is complete
      setTimeout(() => {
        quantityInput.select();
      }, 50);
    }, 150);

    updateModalSubtotal();
  }

  function closeModal() {
    modal.classList.remove('active');
    currentProduct = null;
    quantityInput.value = '';
    modalSubtotal.textContent = '€0.00';
  }

  // Helper function to normalize and parse quantity input
  function parseQuantityInput() {
    // Get the raw input value and normalize it (replace comma with dot, remove spaces)
    const rawValue = quantityInput.value.trim().replace(',', '.');
    const parsed = parseFloat(rawValue);
    return isNaN(parsed) ? 0 : parsed;
  }

  function handleQuantityInput(e) {
    let value = quantityInput.value;
    const cursorPos = quantityInput.selectionStart;

    // Remove any non-numeric characters except comma, dot, and first character can be negative
    value = value.replace(/[^0-9.,]/g, '');

    // Replace ALL commas with dots (Belgian keyboard uses comma)
    value = value.replace(/,/g, '.');

    // Ensure only one decimal separator
    const parts = value.split('.');
    if (parts.length > 2) {
      value = parts[0] + '.' + parts.slice(1).join('');
    }

    // Update the input value if it changed
    if (value !== quantityInput.value) {
      quantityInput.value = value;
      // Try to maintain cursor position
      quantityInput.setSelectionRange(cursorPos, cursorPos);
    }

    updateModalSubtotal();
  }

  function updateModalSubtotal() {
    const quantity = parseQuantityInput();
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
    const quantity = parseQuantityInput();

    if (!quantity || quantity <= 0) {
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
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day} ${hours}:${minutes}`;
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

    // Populate total and VAT
    const total = currentSale.reduce((sum, item) => sum + item.subtotal, 0);
    const vatAmount = total * 0.06 / 1.06; // Calculate VAT amount from total (prices include 6% VAT)
    document.getElementById('receipt-total-amount').textContent = `€${total.toFixed(2)}`;
    document.getElementById('receipt-vat-amount').textContent = `€${vatAmount.toFixed(2)}`;

    // Trigger print with a small delay to ensure DOM updates
    setTimeout(() => {
      window.print();
    }, 100);
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
  loadProducts();
  renderSale();
})();
