# Migadu Email Setup for Akkervarken Backend

This guide explains how to configure the Akkervarken backend to send order confirmation emails using Migadu.

## Prerequisites

- Active Migadu account with your domain (akkervarken.be)
- Email address created for sending orders (e.g., `bestellingen@akkervarken.be`)

## Configuration Steps

### 1. Create Email Address in Migadu

If you haven't already:

1. Log into your Migadu admin panel
2. Go to your domain (akkervarken.be)
3. Create a new mailbox: `bestellingen@akkervarken.be`
   - Or use an existing email like `info@akkervarken.be`

### 2. Get SMTP Credentials

Migadu SMTP settings:
- **SMTP Host**: `smtp.migadu.com`
- **SMTP Port**: `587` (STARTTLS) or `465` (SSL/TLS)
- **Username**: Your full email address (e.g., `bestellingen@akkervarken.be`)
- **Password**: Your email account password

### 3. Configure Environment Variables

#### For Local Development

Create a `.env` file in the `backend/` directory:

```bash
# Database (use your local or Railway database)
DATABASE_URL=postgresql://...

# CORS
ALLOWED_ORIGINS=http://localhost:1313,http://localhost:8000

# Migadu Email Configuration
SMTP_HOST=smtp.migadu.com
SMTP_PORT=587
SMTP_USER=bestellingen@akkervarken.be
SMTP_PASSWORD=your-email-password-here
FROM_EMAIL=bestellingen@akkervarken.be
ADMIN_EMAIL=info@akkervarken.be
```

**Security Note:** Never commit `.env` to git - it's already in `.gitignore`.

#### For Railway Deployment

1. Go to your Railway project
2. Select your FastAPI service
3. Click "Variables" tab
4. Add the following environment variables:

| Variable | Value |
|----------|-------|
| `SMTP_HOST` | `smtp.migadu.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | `bestellingen@akkervarken.be` |
| `SMTP_PASSWORD` | `your-email-password` |
| `FROM_EMAIL` | `bestellingen@akkervarken.be` |
| `ADMIN_EMAIL` | `info@akkervarken.be` |

**Tip:** If you use different emails for sending and receiving notifications, set them accordingly:
- `FROM_EMAIL`: The email that appears in the "From" field (customer confirmations)
- `ADMIN_EMAIL`: Where admin notifications are sent (new order alerts)

### 4. Test Email Sending

#### Local Test

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Create a test order via Swagger UI (http://localhost:8000/docs) or cURL:

```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Klant",
    "customer_email": "your-test-email@example.com",
    "customer_phone": "+32494123456",
    "batch_id": "test-batch",
    "batch_name": "Test Batch",
    "pickup_info": "Test pickup",
    "total_amount": 10.0,
    "total_items": 1,
    "items": [
      {
        "product_id": "test-product",
        "product_name": "Test Product",
        "quantity": 1,
        "unit_price": 10.0,
        "subtotal": 10.0
      }
    ]
  }'
```

**Check:**
1. API response should include `"email_sent": true`
2. Check your test email inbox for customer confirmation
3. Check `info@akkervarken.be` inbox for admin notification
4. Check server logs for: "Email sent successfully"

**If emails don't arrive:**
- Check spam folder
- Verify SMTP credentials are correct
- Check Railway/local logs for error messages
- Verify Migadu account is active and not rate-limited

#### Railway Test

After deploying to Railway:

1. Use your Railway URL instead of localhost
2. Test with the same cURL command
3. Monitor Railway logs: Go to Deployments → View Logs
4. Look for: "Email sent successfully to ..."

## Troubleshooting

### "Failed to send email: Authentication failed"
- Double-check `SMTP_USER` is the full email address
- Verify `SMTP_PASSWORD` is correct
- Try logging into Migadu webmail with same credentials

### "Failed to send email: Connection timeout"
- Check firewall/network settings
- Try port 465 instead of 587
- Verify Railway can make outbound connections (it should)

### Emails go to spam
- Add SPF record to your DNS (Migadu provides this)
- Set up DKIM (Migadu provides this)
- Migadu has good deliverability by default if DNS is configured

### Rate limiting
- Migadu has sending limits based on your plan
- Check your Migadu dashboard for limits
- For high volume, consider upgrading Migadu plan

### Testing without real emails

If you want to test without sending real emails temporarily:

```bash
# In Railway or local .env, comment out the SMTP variables:
# SMTP_HOST=smtp.migadu.com
# SMTP_PORT=587
# SMTP_USER=...
# SMTP_PASSWORD=...
```

The API will still work but won't send emails (logs will show "Email service not configured").

## Email Templates

The backend sends two types of emails:

### 1. Customer Confirmation Email
- **To:** Customer's email address (if provided in order)
- **Subject:** "Bevestiging bestelling #123 - Akkervarken.be"
- **Content:** Order summary, pickup info, products, total
- **Template:** See `email_service.py:_render_customer_confirmation_html()`

### 2. Admin Notification Email
- **To:** `ADMIN_EMAIL` (e.g., info@akkervarken.be)
- **Subject:** "Nieuwe bestelling #123 - Customer Name"
- **Content:** Full order details including customer contact info
- **Template:** See `email_service.py:_render_admin_notification_html()`

## Customizing Email Templates

Email templates are in `backend/email_service.py`. To customize:

1. Edit the Jinja2 templates in `_render_customer_confirmation_html()` or `_render_admin_notification_html()`
2. Test locally first
3. Commit and deploy

## Security Best Practices

1. **Never commit passwords** - Use environment variables only
2. **Use strong passwords** - Consider creating a specific password for SMTP
3. **Monitor logs** - Check for failed authentication attempts
4. **Rotate passwords** - Update SMTP password periodically

## Migadu-Specific Features

### Sender Rewriting
Migadu supports sender rewriting, so you can send from any alias on your domain.

### Custom Reply-To
If you want replies to go to a different address, modify `email_service.py`:

```python
message["Reply-To"] = "contact@akkervarken.be"
```

### Multiple From Addresses
If you want different "from" addresses for different email types, update the email service methods.

## Support

- **Migadu Support**: https://migadu.com/support/
- **Migadu Docs**: https://migadu.com/guides/
- **SMTP Settings**: https://migadu.com/guides/smtp/

## Alternative: App-Specific Password

For better security, you can create an app-specific password in Migadu (if supported by your plan):

1. Log into Migadu admin
2. Go to your mailbox settings
3. Create app-specific password for "Akkervarken Backend"
4. Use that password instead of your main password

This way, if the password is compromised, you can revoke it without changing your main password.
