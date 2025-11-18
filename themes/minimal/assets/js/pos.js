// Point of Sale JavaScript
(function() {
  'use strict';

  let currentSale = [];
  let currentProduct = null;

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

  // Event Listeners
  document.querySelectorAll('.product-card').forEach(card => {
    card.addEventListener('click', handleProductClick);
  });

  cancelBtn.addEventListener('click', closeModal);
  addBtn.addEventListener('click', addToSale);
  newSaleBtn.addEventListener('click', newSale);
  printBtn.addEventListener('click', printReceipt);
  quantityInput.addEventListener('input', updateModalSubtotal);
  quantityInput.addEventListener('keypress', handleEnterKey);

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
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

  function updateModalSubtotal() {
    const quantity = parseFloat(quantityInput.value) || 0;
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
    const quantity = parseFloat(quantityInput.value);

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

    // Show/hide print button based on whether there are items
    if (currentSale.length > 0) {
      printBtn.style.display = 'flex';
    } else {
      printBtn.style.display = 'none';
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

  // Initialize
  renderSale();
})();
