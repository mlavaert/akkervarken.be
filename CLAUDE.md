# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-based static website for Akkervarken.be, a Belgian farm selling fresh pork meat directly to customers. The site is built with Hugo 0.151.0 and features a custom minimal theme with an integrated e-commerce ordering system.

**Live site**: https://akkervarken.be
**Language**: Dutch (nl-BE)
**Location**: Opwijk, Belgium

## Coding Style

### YAML

- Always use lisp-case
- Always use 2-space indents

## Building and Running

### Local Development
```bash
# Start Hugo development server with drafts
hugo server -D

# Build for production (outputs to ./public)
hugo --gc --minify
```

### Deployment
The site auto-deploys to GitHub Pages via `.github/workflows/hugo.yml` on pushes to `main`. The workflow:
- Uses Hugo Extended 0.151.0
- Runs `hugo --gc --minify` for production build
- Deploys the `./public` directory

## Project Structure

### Documentation

Project documentation should go into the `docs` directory

### Content Architecture
- **Content files** (`/content/*.md`): Markdown pages with front matter
  - `_index.md` - Homepage content
  - `over-ons.md` - About page
  - `webshop.md` - E-commerce ordering page
  - `contact.md` - Contact information

### Data-Driven E-commerce System
The webshop is powered by YAML data files rather than a traditional database:

- **`/data/products.yaml`**: Product catalog
  - Each product has: id, name, description (supports markdown), price, weight, optional image
  - Descriptions can include markdown formatting for emphasis

- **`/data/batches.yaml`**: Slaughter/pickup batches
  - Each batch specifies: id, name, pickup date range, location
  - Links products to batches (lists available product IDs)
  - **Critical constraint**: Customers can only order from ONE batch per order

### Theme Structure (`/themes/minimal/`)
Custom theme with these key components:

**Layouts**:
- `layouts/index.html` - Homepage with image slideshow and hero section
- `layouts/_default/baseof.html` - Base template with nav, footer, SEO partials
- `layouts/_default/webshop.html` - E-commerce template with batch-based product display
- `layouts/_default/single.html` - Standard content pages
- `layouts/partials/seo.html` - SEO meta tags
- `layouts/partials/structured-data.html` - JSON-LD structured data for search engines

**Assets**:
- `assets/css/style.css` - Main stylesheet
- `assets/js/webshop.js` - Shopping cart logic, batch validation, email ordering
- `assets/js/slideshow.js` - Homepage image carousel

Hugo Pipes processes these assets with minification and fingerprinting for cache-busting.

### Static Assets
- `/static/img/` - Product images, slideshow images, logo
- `/static/favicon.ico` - Site favicon

## Key Technical Patterns

### Hugo Asset Pipeline
Assets use Hugo Pipes for optimization:
```go
{{- $css := resources.Get "css/style.css" -}}
{{- $css = $css | minify | fingerprint -}}
<link rel="stylesheet" href="{{ $css.RelPermalink }}" integrity="{{ $css.Data.Integrity }}">
```

### Batch-Based Ordering System
The webshop enforces single-batch ordering:
- Each product card includes `data-batch` attribute
- JavaScript validates all items in cart belong to same batch
- Users must place separate orders for different batches
- No stock tracking - customers can order unlimited quantities

### Product Display Pattern
Products are rendered by:
1. Iterating through batches in `batches.yaml`
2. For each batch's `available-products`, looking up full product details from `products.yaml`
3. Displaying product with batch-specific pickup info
4. Generating unique product IDs as `{batch-id}-{product-id}`

### Order Submission
Orders are submitted via `mailto:` link with pre-filled email containing:
- Selected products with quantities
- Prices and total
- Pickup location and dates
- Customer name and contact info

## Configuration

### Hugo Config (`hugo.toml`)
Key settings:
- SEO parameters in `[params]` section (description, keywords, images)
- Contact info in `[params.social]` and `[params.location]`
- Image quality/processing in `[imaging]`
- Minification settings in `[minify]`

### SEO & Analytics
- robots.txt enabled (`enableRobotsTXT = true`)
- Custom SEO partial with Open Graph and Twitter Cards
- JSON-LD structured data for LocalBusiness and products
- Privacy-first analytics via SimpleAnalytics (not Google Analytics)

## Hugo Shortcodes

The site includes a custom `img` shortcode for images that replaces raw HTML (which Hugo's default Goldmark renderer blocks):

### img shortcode
Displays images with various styling options:
```
{{< img src="/img/photo.jpg" alt="Description" style="polaroid" >}}
```

**Style options:**
- `polaroid` - White-bordered polaroid style with shadow (best for content images)
- `center` - Standard centered image with rounded corners (default)
- `tilt-left` - Centered image tilted 2° left for visual interest
- `tilt-right` - Centered image tilted 2° right for visual interest

The shortcode is defined in `themes/minimal/layouts/shortcodes/img.html` and maps to CSS classes in `style.css` (lines 112-173).

**Image optimization:** All images should be resized to max 1200px (longest edge) and optimized to ~85% quality before adding to `/static/img/` to ensure fast page loads.

## Development Notes

### When Adding Products
1. Add product definition to `data/products.yaml` with unique ID
2. Add product ID to relevant batch(es) in `data/batches.yaml`
3. Optionally add product image to `/static/img/`

### When Adding New Batches
1. Add batch to `data/batches.yaml` with:
   - Unique ID (format: "DD-month-YYYY")
   - Human-readable name
   - Pickup date range (YYYY-MM-DD format)
   - Pickup location
   - List of available product IDs

### Webshop JavaScript Dependencies
The `webshop.js` file must handle:
- Quantity increase/decrease (no limits)
- Cart total calculation
- Batch validation (single batch per order)
- Email order generation with proper formatting

### Content Updates
All content is in Dutch. Key terminology:
- "Ophalen" = Pickup
- "Bestelling" = Order
- "Beschikbaar" = Available
- "Pakket" = Package/Bundle
