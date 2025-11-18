/**
 * Centralized Analytics Tracking
 * Manages all analytics events for Google Analytics 4
 * Handles consent checking and provides clean API for tracking
 */

(function() {
    'use strict';

    /**
     * Check if analytics is available and consent is granted
     */
    function isAnalyticsEnabled() {
        return typeof window.gtag === 'function';
    }

    /**
     * Track when product list is viewed (page load)
     */
    function trackProductList(products) {
        if (!isAnalyticsEnabled()) return;

        const items = products.map((product, index) => ({
            item_id: product.id,
            item_name: product.name,
            item_category: product.batch,
            price: product.expectedPrice > 0 ? product.expectedPrice : product.price,
            index: index
        }));

        if (items.length > 0) {
            window.gtag('event', 'view_item_list', {
                currency: 'EUR',
                item_list_id: 'webshop_products',
                item_list_name: 'Webshop Producten',
                items: items
            });
        }
    }

    /**
     * Track when item is added to cart
     */
    function trackAddToCart(productId, item, batch) {
        if (!isAnalyticsEnabled()) return;

        const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;

        window.gtag('event', 'add_to_cart', {
            currency: 'EUR',
            value: itemPrice,
            items: [{
                item_id: productId,
                item_name: item.name,
                item_category: batch,
                price: itemPrice,
                quantity: 1
            }]
        });
    }

    /**
     * Track when item is removed from cart
     */
    function trackRemoveFromCart(productId, item) {
        if (!isAnalyticsEnabled()) return;

        const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;

        window.gtag('event', 'remove_from_cart', {
            currency: 'EUR',
            value: itemPrice * item.quantity,
            items: [{
                item_id: productId,
                item_name: item.name,
                item_category: item.batch,
                price: itemPrice,
                quantity: item.quantity
            }]
        });
    }

    /**
     * Track when cart is viewed/updated
     */
    function trackViewCart(cart, totalPrice) {
        if (!isAnalyticsEnabled()) return;

        const items = Object.entries(cart).map(([productId, item]) => {
            const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;
            return {
                item_id: productId,
                item_name: item.name,
                item_category: item.batch,
                price: itemPrice,
                quantity: item.quantity
            };
        });

        window.gtag('event', 'view_cart', {
            currency: 'EUR',
            value: totalPrice,
            items: items
        });
    }

    /**
     * Track when checkout process begins
     */
    function trackBeginCheckout(cart, batchName, totalPrice) {
        if (!isAnalyticsEnabled()) return;

        const items = Object.entries(cart).map(([productId, item]) => {
            const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;
            return {
                item_id: productId,
                item_name: item.name,
                item_category: batchName,
                price: itemPrice,
                quantity: item.quantity
            };
        });

        window.gtag('event', 'begin_checkout', {
            currency: 'EUR',
            value: totalPrice,
            items: items
        });
    }

    /**
     * Track completed purchase
     */
    function trackPurchase(cart, batchName, totalPrice) {
        if (!isAnalyticsEnabled()) return;

        const items = Object.entries(cart).map(([productId, item]) => {
            const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;
            return {
                item_id: productId,
                item_name: item.name,
                item_category: batchName,
                price: itemPrice,
                quantity: item.quantity
            };
        });

        window.gtag('event', 'purchase', {
            currency: 'EUR',
            value: totalPrice,
            items: items
        });
    }

    /**
     * Track CTA (Call-to-Action) button clicks
     */
    function trackCTAClick(buttonId, destination) {
        if (!isAnalyticsEnabled()) return;

        window.gtag('event', 'cta_click', {
            event_category: 'engagement',
            event_label: buttonId,
            destination_url: destination
        });
    }

    /**
     * Track contact interactions (email, phone, WhatsApp)
     */
    function trackContact(method, value) {
        if (!isAnalyticsEnabled()) return;

        window.gtag('event', 'contact', {
            event_category: 'lead_generation',
            contact_method: method,
            contact_value: value
        });
    }

    /**
     * Track checkout abandonment
     */
    function trackCheckoutAbandonment(reason, cart, totalPrice) {
        if (!isAnalyticsEnabled()) return;

        const items = Object.entries(cart).map(([productId, item]) => {
            const itemPrice = item.expectedPrice > 0 ? item.expectedPrice : item.price;
            return {
                item_id: productId,
                item_name: item.name,
                item_category: item.batch,
                price: itemPrice,
                quantity: item.quantity
            };
        });

        window.gtag('event', 'checkout_abandon', {
            event_category: 'ecommerce',
            abandonment_reason: reason,
            currency: 'EUR',
            value: totalPrice,
            items: items
        });
    }

    /**
     * Track order email fallback methods
     */
    function trackOrderFallback(method) {
        if (!isAnalyticsEnabled()) return;

        window.gtag('event', 'order_fallback', {
            event_category: 'ecommerce',
            fallback_method: method
        });
    }

    // Expose Analytics API globally
    window.Analytics = {
        trackProductList: trackProductList,
        trackAddToCart: trackAddToCart,
        trackRemoveFromCart: trackRemoveFromCart,
        trackViewCart: trackViewCart,
        trackBeginCheckout: trackBeginCheckout,
        trackPurchase: trackPurchase,
        trackCTAClick: trackCTAClick,
        trackContact: trackContact,
        trackCheckoutAbandonment: trackCheckoutAbandonment,
        trackOrderFallback: trackOrderFallback
    };

})();
