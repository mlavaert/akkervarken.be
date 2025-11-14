# Cookie Banner & Google Analytics - Instructies

## Wat is er toegevoegd?

Uw website heeft nu een **cookie consent banner** (toestemmingsbanner) die automatisch verschijnt wanneer iemand uw website voor het eerst bezoekt. Deze banner is GDPR-compliant en voldoet aan de Europese privacywetgeving.

## Hoe ziet het eruit?

Wanneer bezoekers uw website bezoeken, verschijnt onderaan het scherm een banner met:
- 🍪 Een emoji en "Cookies" als titel
- Uitleg over het gebruik van cookies
- Twee knoppen: **"Accepteren"** (groen) en **"Weigeren"** (grijs)

De banner is volledig responsive en past zich aan op mobiele telefoons.

## Google Analytics instellen

### Stap 1: Google Analytics Account aanmaken

1. Ga naar [analytics.google.com](https://analytics.google.com/)
2. Maak een nieuwe GA4 property aan voor akkervarken.be
3. Kopieer uw **Measurement ID** (ziet eruit als `G-XXXXXXXXXX`)

### Stap 2: Measurement ID toevoegen

Open het bestand `hugo.toml` en vul uw Measurement ID in:

```toml
[params]
  googleAnalytics = 'G-XXXXXXXXXX'  # Vervang met uw echte ID
```

### Stap 3: Website opnieuw bouwen

```bash
hugo --gc --minify
```

Push de wijzigingen naar GitHub - de website wordt automatisch opnieuw gedeployed.

## Hoe werkt het?

### ✅ Bezoeker accepteert cookies
- Google Analytics wordt geladen
- Website gebruik wordt bijgehouden
- Keuze wordt 1 jaar onthouden
- Banner verdwijnt

### ❌ Bezoeker weigert cookies
- Google Analytics wordt NIET geladen
- Geen tracking
- Keuze wordt 1 jaar onthouden
- Banner verdwijnt

### 🔄 Terugkerende bezoekers
- Als ze eerder geaccepteerd hebben → GA laadt automatisch
- Als ze eerder geweigerd hebben → Geen tracking
- Banner wordt niet opnieuw getoond (tenzij cookies gewist zijn)

## Privacy features

- **IP-anonimisering**: IP-adressen worden geanonimiseerd
- **Veilige cookies**: Cookies zijn beveiligd met `SameSite=Lax;Secure`
- **Respects user choice**: De keuze van de bezoeker wordt altijd gerespecteerd
- **Geen CMP nodig**: Alles is custom gebouwd, geen externe diensten

## Bezoekers kunnen van gedachten veranderen

Als een bezoeker hun keuze wil wijzigen:
1. Open de browser console (F12)
2. Typ: `window.resetCookieConsent()`
3. De pagina herlaadt en de banner verschijnt opnieuw

## Tekst aanpassen

### Banner tekst wijzigen

Bewerk `themes/minimal/layouts/partials/cookie-consent.html` (regels 5-6):

```html
<h3>🍪 Cookies</h3>
<p>Uw eigen tekst hier...</p>
```

### Kleuren aanpassen

Bewerk `themes/minimal/assets/css/style.css` vanaf regel 1267.

Bijvoorbeeld, om de accepteer-knop een andere kleur te geven:
```css
.cookie-btn-accept {
    background: #uw-kleur-hier;
    color: white;
}
```

## Testen

### Test de banner
1. Wis cookies voor akkervarken.be in uw browser
2. Bezoek de website
3. Banner verschijnt onderaan

### Test Google Analytics
1. Open DevTools (F12) → Network tabblad
2. Klik op "Accepteren"
3. Zoek naar requests naar `googletagmanager.com`
4. Deze zouden moeten verschijnen

### Test weigeren
1. Wis cookies en herlaad
2. Klik op "Weigeren"
3. Check Network tab → geen requests naar Google
4. Check Console → "Google Analytics disabled" bericht

## Belangrijke notitie over privacybeleid

⚠️ **Update uw privacyverklaring** (`/privacyverklaring/`)

Voeg toe:
- Dat u Google Analytics gebruikt
- Welke data verzameld wordt
- Hoe lang cookies bewaard blijven (1 jaar)
- Dat bezoekers kunnen weigeren
- Hoe bezoekers hun keuze kunnen wijzigen

## SimpleAnalytics

De website gebruikt momenteel ook SimpleAnalytics (privacy-first, geen cookies).

Beide kunnen naast elkaar bestaan:
- SimpleAnalytics = privacy-first, geen toestemming nodig
- Google Analytics = uitgebreidere data, toestemming vereist

Als u SimpleAnalytics wil verwijderen, verwijder regels 105-107 in `baseof.html`.

## Support

Bij vragen over deze implementatie:
- Bekijk `GOOGLE_ANALYTICS_SETUP.md` voor technische details (Engels)
- Check de console in uw browser voor error messages
- Test altijd in een incognito window na wijzigingen

## Bestanden gewijzigd/toegevoegd

### Nieuw
- `themes/minimal/layouts/partials/cookie-consent.html`
- `themes/minimal/assets/js/cookie-consent.js`
- `GOOGLE_ANALYTICS_SETUP.md`
- `COOKIE_BANNER_NL.md` (dit bestand)

### Gewijzigd
- `themes/minimal/assets/css/style.css` (styling toegevoegd)
- `themes/minimal/layouts/_default/baseof.html` (banner geïntegreerd)
- `hugo.toml` (Google Analytics parameter toegevoegd)
