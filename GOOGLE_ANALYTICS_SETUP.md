# Google Analytics Setup with Cookie Consent

This website now includes Google Analytics with a custom cookie consent banner that complies with GDPR requirements.

## Features

✅ **Cookie Consent Banner** - Appears on first visit, asks users to accept or decline cookies
✅ **No CMP Required** - Custom implementation without third-party Consent Management Platform
✅ **GDPR Compliant** - Only loads Google Analytics after user consent
✅ **Privacy-First** - IP anonymization enabled, respects user choices
✅ **Persistent Choice** - User consent stored for 365 days
✅ **Mobile Responsive** - Banner adapts to all screen sizes

## Setup Instructions

### 1. Get Your Google Analytics Measurement ID

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property (or use an existing one)
3. Copy your Measurement ID (format: `G-XXXXXXXXXX`)

### 2. Configure Hugo

Edit `hugo.toml` and add your Measurement ID:

```toml
[params]
  googleAnalytics = 'G-XXXXXXXXXX'  # Replace with your actual ID
```

### 3. Deploy

Build and deploy your site:

```bash
hugo --gc --minify
```

The changes will auto-deploy via GitHub Actions when pushed to `main`.

## How It Works

### First Visit
- User visits the website
- Cookie consent banner appears at the bottom
- Google Analytics is **NOT** loaded until user makes a choice

### User Accepts
- Consent stored in `cookie_consent` cookie (expires in 365 days)
- Google Analytics loads and begins tracking
- Banner disappears

### User Declines
- Consent refusal stored in `cookie_consent` cookie
- Google Analytics is **NOT** loaded
- Any existing GA cookies are deleted
- Banner disappears

### Return Visits
- If user previously accepted → GA loads automatically, no banner
- If user previously declined → GA stays disabled, no banner
- User can reset their choice (see below)

## User Privacy Features

- **IP Anonymization**: Enabled by default (`anonymize_ip: true`)
- **Secure Cookies**: `SameSite=Lax;Secure` flags set
- **Easy Reset**: Users can change their mind at any time

## Resetting Consent

Users can reset their cookie consent by opening the browser console and running:

```javascript
window.resetCookieConsent()
```

This will delete the consent cookie and reload the page, showing the banner again.

## Files Added/Modified

### New Files
- `themes/minimal/layouts/partials/cookie-consent.html` - Banner HTML
- `themes/minimal/assets/js/cookie-consent.js` - Consent management logic

### Modified Files
- `themes/minimal/assets/css/style.css` - Added banner styling (lines 1267-1381)
- `themes/minimal/layouts/_default/baseof.html` - Integrated banner and scripts
- `hugo.toml` - Added `googleAnalytics` parameter

## Customization

### Change Banner Text

Edit `themes/minimal/layouts/partials/cookie-consent.html`:

```html
<p>Your custom message here...</p>
```

### Change Banner Styling

Edit the `.cookie-consent-banner` section in `themes/minimal/assets/css/style.css` (starting at line 1267).

### Change Consent Duration

Edit `cookie-consent.js` and modify:

```javascript
const CONSENT_EXPIRY_DAYS = 365; // Change to desired number of days
```

## Testing

### Test Cookie Consent Banner
1. Clear your browser cookies for `akkervarken.be`
2. Visit the website
3. You should see the cookie consent banner at the bottom

### Test Analytics Loading
1. Open browser DevTools (F12) → Network tab
2. Accept cookies
3. Look for requests to `googletagmanager.com` - they should appear
4. Check Console - you should see "Google Analytics initialized"

### Test Cookie Decline
1. Clear cookies and reload
2. Decline cookies
3. Check Network tab - no requests to `googletagmanager.com`
4. Check Console - you should see "Google Analytics disabled"

## Notes

- The website currently also uses SimpleAnalytics (privacy-first, no cookies required)
- Both analytics systems can run simultaneously without conflict
- If you want to remove SimpleAnalytics, delete lines 105-107 in `baseof.html`

## Compliance

This implementation provides basic GDPR compliance by:
- ✅ Requesting consent before setting cookies
- ✅ Providing a clear accept/decline choice
- ✅ Respecting user decisions
- ✅ Allowing users to change their minds

**Important**: Ensure your privacy policy (`/privacyverklaring/`) is updated to mention:
- That you use Google Analytics
- What data is collected
- How long cookies are stored
- How users can opt-out or reset consent
