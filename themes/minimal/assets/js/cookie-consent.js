/**
 * Cookie Consent Management for Google Analytics
 * Manages user consent for analytics cookies without using a CMP
 * Uses Google Consent Mode v2 for improved measurement
 */

(function() {
    'use strict';

    const CONSENT_COOKIE_NAME = 'cookie_consent';
    const CONSENT_EXPIRY_DAYS = 365;
    const GA_MEASUREMENT_ID = window.GA_MEASUREMENT_ID; // Set from Hugo config

    /**
     * Initialize Google Consent Mode v2 with default deny state
     * This must run BEFORE gtag.js loads
     */
    function initializeConsentMode() {
        window.dataLayer = window.dataLayer || [];
        function gtag() {
            window.dataLayer.push(arguments);
        }
        window.gtag = gtag;

        // Set default consent state to 'denied' before any tracking
        gtag('consent', 'default', {
            'ad_storage': 'denied',
            'ad_user_data': 'denied',
            'ad_personalization': 'denied',
            'analytics_storage': 'denied',
            'functionality_storage': 'denied',
            'personalization_storage': 'denied',
            'security_storage': 'granted', // Always allowed for security
            'wait_for_update': 500 // Wait 500ms for consent update
        });
    }

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
     * Load Google Analytics gtag.js script
     * This can be loaded early because Consent Mode controls data collection
     */
    function loadGtagScript() {
        if (!GA_MEASUREMENT_ID) {
            console.warn('Google Analytics Measurement ID not configured');
            return;
        }

        // Load gtag.js script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
        document.head.appendChild(script);

        // Configure GA4 with privacy settings
        script.onload = function() {
            window.gtag('js', new Date());
            window.gtag('config', GA_MEASUREMENT_ID, {
                'anonymize_ip': true,
                'cookie_flags': 'SameSite=Lax;Secure',
                'allow_google_signals': false, // Disable for privacy
                'allow_ad_personalization_signals': false
            });
        };
    }

    /**
     * Grant consent and update Consent Mode
     */
    function grantConsent() {
        if (window.gtag) {
            window.gtag('consent', 'update', {
                'analytics_storage': 'granted',
                'functionality_storage': 'granted',
                'personalization_storage': 'granted'
            });
            console.log('Google Analytics consent granted');
        }
    }

    /**
     * Deny consent and update Consent Mode
     */
    function denyConsent() {
        if (window.gtag) {
            window.gtag('consent', 'update', {
                'analytics_storage': 'denied',
                'functionality_storage': 'denied',
                'personalization_storage': 'denied'
            });
            console.log('Google Analytics consent denied');
        }
        // Remove any existing GA cookies
        removeGACookies();
    }

    /**
     * Remove Google Analytics cookies
     */
    function removeGACookies() {
        const gaCookies = ['_ga', '_gat', '_gid'];
        gaCookies.forEach(cookieName => {
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
            // Also try with domain
            const domain = window.location.hostname;
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=${domain}`;
            document.cookie = `${cookieName}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=.${domain}`;
        });
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
        grantConsent();
        hideBanner();
    }

    /**
     * Handle decline cookies
     */
    function declineCookies() {
        setCookie(CONSENT_COOKIE_NAME, 'declined', CONSENT_EXPIRY_DAYS);
        denyConsent();
        hideBanner();
    }

    /**
     * Initialize consent management
     */
    function init() {
        // Initialize Consent Mode v2 first (before GA loads)
        initializeConsentMode();

        // Load GA script immediately (Consent Mode controls data collection)
        loadGtagScript();

        // Check existing consent and update consent state accordingly
        const consentStatus = getCookie(CONSENT_COOKIE_NAME);

        if (consentStatus === 'accepted') {
            // User has already accepted - grant consent
            grantConsent();
        } else if (consentStatus === 'declined') {
            // User has declined - deny consent and remove cookies
            denyConsent();
        } else {
            // No consent decision yet - show banner
            // Consent Mode keeps analytics_storage as 'denied' until user decides
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
        denyConsent();
        location.reload();
    };

})();
