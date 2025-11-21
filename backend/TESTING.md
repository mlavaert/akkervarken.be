# Testing Guide for Order API

This guide will help you test the order API before deploying it to production and integrating with the frontend.

## Quick Start Testing

### 1. Local Setup (Without Database)

If you just want to test the API structure without a database:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start server (will run without database - some endpoints will fail)
uvicorn main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

### 2. Local Setup (With Database)

For full testing with database persistence:

**Option A: Use Railway Database Locally**

1. Get your Railway DATABASE_URL from Railway dashboard
2. Create a `.env` file:
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
ALLOWED_ORIGINS=http://localhost:1313,http://localhost:8000
```

3. Run migrations and start server:
```bash
alembic upgrade head
uvicorn main:app --reload
```

**Option B: Use Local PostgreSQL**

1. Install PostgreSQL locally
2. Create a database:
```bash
createdb akkervarken_dev
```

3. Create `.env` file:
```bash
DATABASE_URL=postgresql://localhost/akkervarken_dev
ALLOWED_ORIGINS=http://localhost:1313,http://localhost:8000
```

4. Run migrations and start server:
```bash
alembic upgrade head
uvicorn main:app --reload
```

## Testing Scenarios

### Test 1: Create an Order (Basic)

**Using Swagger UI:**
1. Go to http://localhost:8000/docs
2. Expand `POST /api/orders/`
3. Click "Try it out"
4. Click "Execute" (uses the example data)
5. Verify response has `"success": true` and an `order_id`

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jan Janssens",
    "customer_phone": "+32494123456",
    "customer_email": "jan@example.com",
    "batch_id": "test-batch-2024",
    "batch_name": "Test Batch 2024",
    "pickup_info": "2024-12-20 om 14:00",
    "notes": "Test order",
    "total_amount": 45.50,
    "total_items": 3,
    "items": [
      {
        "product_id": "test-gehakt",
        "product_name": "Gehakt",
        "quantity": 2,
        "unit_price": 8.50,
        "subtotal": 17.00,
        "packaging_info": "2 stuks × ±500g"
      },
      {
        "product_id": "test-spek",
        "product_name": "Ontbijtspek",
        "quantity": 1,
        "unit_price": 12.00,
        "expected_price": 13.50,
        "subtotal": 13.50,
        "packaging_info": "±450g"
      },
      {
        "product_id": "test-worst",
        "product_name": "Worst",
        "quantity": 1,
        "unit_price": 15.00,
        "subtotal": 15.00
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "order_id": 1,
  "message": "Bestelling #1 succesvol aangemaakt",
  "email_sent": false
}
```

### Test 2: Retrieve an Order

```bash
curl http://localhost:8000/api/orders/1
```

**Expected Response:**
```json
{
  "id": 1,
  "customer_name": "Jan Janssens",
  "customer_phone": "+32494123456",
  "customer_email": "jan@example.com",
  "batch_id": "test-batch-2024",
  "batch_name": "Test Batch 2024",
  "pickup_info": "2024-12-20 om 14:00",
  "notes": "Test order",
  "total_amount": 45.50,
  "total_items": 3,
  "status": "PENDING",
  "created_at": "2024-11-21T10:30:00Z",
  "updated_at": null,
  "items": [
    {
      "id": 1,
      "product_id": "test-gehakt",
      "product_name": "Gehakt",
      "quantity": 2,
      "unit_price": 8.50,
      "expected_price": null,
      "subtotal": 17.00,
      "packaging_info": "2 stuks × ±500g"
    },
    ...
  ]
}
```

### Test 3: List All Orders

```bash
# Get all orders
curl http://localhost:8000/api/orders/

# Filter by batch
curl "http://localhost:8000/api/orders/?batch_id=test-batch-2024"

# Pagination
curl "http://localhost:8000/api/orders/?skip=0&limit=10"
```

### Test 4: Test Email Sending

**Setup Email (Optional):**

1. Get a SendGrid API key (free tier available)
2. Add to `.env`:
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=bestellingen@akkervarken.be
ADMIN_EMAIL=your-test-email@example.com
```

3. Restart server
4. Create an order with a valid email address
5. Check your inbox for:
   - Customer confirmation (if customer_email provided)
   - Admin notification (sent to ADMIN_EMAIL)

**Without Email:**
- Orders still work perfectly
- `email_sent` will be `false` in response
- Check logs: "Email service not configured - emails will not be sent"

### Test 5: Validation Testing

Test that the API properly validates inputs:

**Missing required field:**
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test",
    "batch_id": "test",
    "items": []
  }'
```
Expected: 422 Validation Error

**Invalid email:**
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test",
    "customer_email": "not-an-email",
    "batch_id": "test",
    "batch_name": "Test",
    "total_amount": 10,
    "total_items": 1,
    "items": [{"product_id": "p1", "product_name": "P1", "quantity": 1, "unit_price": 10, "subtotal": 10}]
  }'
```
Expected: 422 Validation Error (invalid email format)

**Negative price:**
```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test",
    "batch_id": "test",
    "batch_name": "Test",
    "total_amount": -10,
    "total_items": 1,
    "items": [{"product_id": "p1", "product_name": "P1", "quantity": 1, "unit_price": 10, "subtotal": 10}]
  }'
```
Expected: 422 Validation Error (price must be > 0)

## Database Testing

### Verify Data Persistence

```bash
# Create an order
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d @test_order.json

# Stop the server
# Restart the server

# Verify order is still there
curl http://localhost:8000/api/orders/1
```

### Test Migration Rollback

```bash
# Check current migration
alembic current

# Rollback
alembic downgrade -1

# Verify tables are gone (orders should fail)
curl http://localhost:8000/api/orders/

# Re-apply migration
alembic upgrade head

# Verify orders work again
curl http://localhost:8000/api/orders/
```

## Testing on Railway

### 1. Deploy to Railway

```bash
# Make sure all backend files are committed
git add backend/
git commit -m "Add order API"
git push
```

### 2. Run Migrations on Railway

Use Railway CLI or web console:
```bash
alembic upgrade head
```

### 3. Test Railway Deployment

Replace `localhost:8000` with your Railway URL in all the curl commands above.

Example:
```bash
curl https://your-app.up.railway.app/api/orders/
```

### 4. Monitor Logs

In Railway dashboard:
1. Go to your service
2. Click "Deployments"
3. View logs for errors

Look for:
- "Order #X created successfully"
- "Email sent successfully" (if configured)
- Any error messages

## Common Issues

### "Database not configured"
- Make sure DATABASE_URL is set in .env or Railway environment variables
- Check database.py:18 - engine should not be None

### "Email service not configured"
- This is just a warning - API works fine without email
- To enable: add SMTP credentials to environment variables

### CORS errors (from frontend)
- Add frontend domain to ALLOWED_ORIGINS
- Format: `https://akkervarken.be,http://localhost:1313`

### Migration errors
```bash
# Reset migrations (DANGER: deletes all data)
alembic downgrade base
alembic upgrade head

# Or recreate database
dropdb akkervarken_dev
createdb akkervarken_dev
alembic upgrade head
```

## Load Testing (Optional)

Test with multiple concurrent orders:

```bash
# Install Apache Bench
sudo apt install apache2-utils  # Linux
brew install httpd  # macOS

# Create test order JSON file
cat > order.json << 'EOF'
{"customer_name":"Load Test","batch_id":"test","batch_name":"Test","total_amount":10,"total_items":1,"items":[{"product_id":"p1","product_name":"Product","quantity":1,"unit_price":10,"subtotal":10}]}
EOF

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -p order.json -T application/json http://localhost:8000/api/orders/
```

## Next Steps

Once testing is complete:
1. Deploy to Railway with all environment variables
2. Test from Railway URL
3. Update frontend to use the new API endpoint
4. Test end-to-end flow from webshop to database
