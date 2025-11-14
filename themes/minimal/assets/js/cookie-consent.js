/**
 * Cookie Consent Management for Google Analytics
 * Manages user consent for analytics cookies without using a CMP
 */

(function() {
    'use strict';

    const CONSENT_COOKIE_NAME = 'cookie_consent';
    const CONSENT_EXPIRY_DAYS = 365;
    const GA_MEASUREMENT_ID = window.GA_MEASUREMENT_ID; // Set from Hugo config

    /**
     * Get cookie value by name
     */
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    /**
     * Set cookie with name, value, and expiry
     */
    function setCookie(name, value, days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    }

    /**
     * Initialize Google Analytics with gtag.js
     */
    function initializeGoogleAnalytics() {
        if (!GA_MEASUREMENT_ID) {
            console.warn('Google Analytics Measurement ID not configured');
            return;
        }

        // Load gtag.js script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
        document.head.appendChild(script);

        // Initialize gtag
        window.dataLayer = window.dataLayer || [];
        function gtag() {
            window.dataLayer.push(arguments);
        }
        window.gtag = gtag;

        gtag('js', new Date());
        gtag('config', GA_MEASUREMENT_ID, {
            'anonymize_ip': true, // IP anonymization for privacy
            'cookie_flags': 'SameSite=Lax;Secure'
        });

        console.log('Google Analytics initialized');
    }

    /**
     * Remove Google Analytics cookies and scripts
     */
    function disableGoogleAnalytics() {
        // Disable GA by setting the disable flag
        if (GA_MEASUREMENT_ID) {
            window[`ga-disable-${GA_MEASUREMENT_ID}`] = true;
        }

        // Remove GA cookies
        const gaCookies = ['_ga', '_gat', '_gid'];
        gaCookies.forEach(cookieName => {
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
            // Also try with domain
            const domain = window.location.hostname;
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=${domain}`;
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=.${domain}`;
        });

        console.log('Google Analytics disabled and cookies removed');
    }

    /**
     * Show the cookie consent banner
     */
    function showBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'block';
        }
    }

    /**
     * Hide the cookie consent banner
     */
    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }

    /**
     * Handle accept cookies
     */
    function acceptCookies() {
        setCookie(CONSENT_COOKIE_NAME, 'accepted', CONSENT_EXPIRY_DAYS);
        hideBanner();
        initializeGoogleAnalytics();
    }

    /**
     * Handle decline cookies
     */
    function declineCookies() {
        setCookie(CONSENT_COOKIE_NAME, 'declined', CONSENT_EXPIRY_DAYS);
        hideBanner();
        disableGoogleAnalytics();
    }

    /**
     * Initialize consent management
     */
    function init() {
        const consentStatus = getCookie(CONSENT_COOKIE_NAME);

        if (consentStatus === 'accepted') {
            // User has already accepted - load GA
            initializeGoogleAnalytics();
        } else if (consentStatus === 'declined') {
            // User has declined - ensure GA is disabled
            disableGoogleAnalytics();
        } else {
            // No consent decision yet - show banner
            showBanner();
        }

        // Attach event listeners to buttons
        const acceptBtn = document.getElementById('cookie-accept');
        const declineBtn = document.getElementById('cookie-decline');

        if (acceptBtn) {
            acceptBtn.addEventListener('click', acceptCookies);
        }

        if (declineBtn) {
            declineBtn.addEventListener('click', declineCookies);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose function to allow users to change their consent
    window.resetCookieConsent = function() {
        document.cookie = `${CONSENT_COOKIE_NAME}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
        disableGoogleAnalytics();
        location.reload();
    };

})();
