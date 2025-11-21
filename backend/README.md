# Akkervarken Backend API

FastAPI backend for the Akkervarken.be order system with database persistence and email notifications.

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL (optional for local development)

### Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration (optional for testing without email)
```

4. **Run database migrations:**
```bash
# Make sure DATABASE_URL is set in your .env file or Railway will set it
alembic upgrade head
```

5. **Run the server:**
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation
Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Railway Deployment

### Step 1: Prepare Your Repository

1. Commit all backend files:
```bash
cd backend
git add .
git commit -m "Add minimal FastAPI backend"
git push
```

### Step 2: Create Railway Project

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `akkervarken.be` repository
6. Railway will detect the Python app in `/backend`

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "New" or the "+" button
2. Select "Database" → "Add PostgreSQL"
3. Done! Railway automatically sets the `DATABASE_URL` environment variable

### Step 4: Run Database Migrations

After Railway creates your database:

1. In Railway, go to your FastAPI service
2. Click "Settings" → "Deploy"
3. Add a deployment command or run manually via Railway CLI:
```bash
alembic upgrade head
```

Or via the Railway console (in the service dashboard).

### Step 5: Configure Environment Variables

1. Go to your FastAPI service in Railway
2. Click "Variables" tab
3. Add these variables (see .env.example for full list):
   - `ALLOWED_ORIGINS` = `https://akkervarken.be`
   - `SMTP_HOST` = `smtp.sendgrid.net` (or your SMTP server)
   - `SMTP_PORT` = `587`
   - `SMTP_USER` = `apikey` (for SendGrid) or your SMTP username
   - `SMTP_PASSWORD` = `your-sendgrid-api-key` (get from SendGrid)
   - `FROM_EMAIL` = `bestellingen@akkervarken.be`
   - `ADMIN_EMAIL` = `info@akkervarken.be`

### Step 6: Deploy

Railway automatically deploys when you push to GitHub!

```bash
git push
```

Railway will:
1. Detect changes
2. Build your app
3. Deploy it
4. Give you a URL like: `https://your-app.up.railway.app`

### Step 7: Verify Deployment

Visit your Railway URL:
- `https://your-app.up.railway.app/` - Should return JSON with "Akkervarken API is running!"
- `https://your-app.up.railway.app/health` - Should return database connection status
- `https://your-app.up.railway.app/docs` - Swagger UI documentation
- Test the order API using the instructions in the "Testing" section below

## Project Structure

```
backend/
├── main.py              # FastAPI application & route registration
├── database.py          # Database connection setup
├── models.py            # SQLAlchemy database models (Order, OrderItem)
├── schemas.py           # Pydantic schemas for API validation
├── orders.py            # Order API endpoints
├── email_service.py     # Email sending service
├── alembic.ini          # Alembic configuration
├── alembic/             # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_orders.py
├── requirements.txt     # Python dependencies
├── railway.toml         # Railway deployment config
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Environment Variables

| Variable | Description | Set By | Required |
|----------|-------------|--------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Railway (automatic) | Yes |
| `PORT` | Port to run the server on | Railway (automatic) | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | You (manual) | Yes |
| `SMTP_HOST` | SMTP server hostname | You (manual) | For emails |
| `SMTP_PORT` | SMTP server port (usually 587) | You (manual) | For emails |
| `SMTP_USER` | SMTP username | You (manual) | For emails |
| `SMTP_PASSWORD` | SMTP password/API key | You (manual) | For emails |
| `FROM_EMAIL` | Email sender address | You (manual) | For emails |
| `ADMIN_EMAIL` | Admin notification email | You (manual) | For emails |

## Testing the Order API

### 1. Test with Swagger UI (Easiest)

1. Start the server locally or visit your Railway deployment
2. Go to http://localhost:8000/docs (or your Railway URL + `/docs`)
3. Find the `POST /api/orders/` endpoint
4. Click "Try it out"
5. Use the pre-filled example or modify it
6. Click "Execute"
7. Check the response - you should get an order ID

### 2. Test with cURL

```bash
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Klant",
    "customer_phone": "+32494123456",
    "customer_email": "test@example.com",
    "batch_id": "15-december-2024",
    "batch_name": "15 december 2024",
    "pickup_info": "2024-12-15 om 10:00",
    "notes": "Test bestelling",
    "total_amount": 25.50,
    "total_items": 2,
    "items": [
      {
        "product_id": "15-december-2024-gehakt",
        "product_name": "Gehakt",
        "quantity": 2,
        "unit_price": 8.50,
        "subtotal": 17.00,
        "packaging_info": "2 stuks × ±500g"
      },
      {
        "product_id": "15-december-2024-spek",
        "product_name": "Ontbijtspek",
        "quantity": 1,
        "unit_price": 8.50,
        "expected_price": 8.50,
        "subtotal": 8.50,
        "packaging_info": "±450g"
      }
    ]
  }'
```

### 3. Retrieve an Order

```bash
# Get order by ID
curl "http://localhost:8000/api/orders/1"

# List all orders
curl "http://localhost:8000/api/orders/"

# Filter by batch
curl "http://localhost:8000/api/orders/?batch_id=15-december-2024"
```

### 4. Check Email Delivery

**Without email configured:**
- Orders will be saved to the database
- No emails will be sent (check logs for warnings)
- API will return `email_sent: false`

**With email configured:**
- Customer gets confirmation email (if email provided)
- Admin gets notification email
- Check spam folder if emails don't arrive
- Check Railway logs for email sending status

### 5. Database Migrations

```bash
# Create a new migration (after changing models.py)
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## Troubleshooting

**App won't start:**
- Check Railway logs in the dashboard
- Verify `requirements.txt` has all dependencies
- Make sure `railway.toml` start command is correct

**Database connection failed:**
- Verify PostgreSQL service is running in Railway
- Check that `DATABASE_URL` is set in environment variables

**CORS errors:**
- Add your domain to `ALLOWED_ORIGINS` environment variable
- Format: `https://akkervarken.be,http://localhost:1313`

**Emails not sending:**
- Check Railway logs for email errors
- Verify SMTP credentials are correct
- Test with a simple SMTP test script first
- Check spam folder for delivered emails
- Emails are optional - API will work without them

**Database migration errors:**
- Make sure DATABASE_URL is set
- Run `alembic upgrade head` in Railway console
- Check for migration conflicts

## Useful Commands

```bash
# Development server
uvicorn main:app --reload

# Run with specific port
uvicorn main:app --port 8080

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head          # Apply all migrations
alembic downgrade -1          # Rollback one migration
alembic revision --autogenerate -m "message"  # Create new migration
alembic history               # View migration history

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip freeze > requirements.txt
```

## API Endpoints

### Orders

- `POST /api/orders/` - Create a new order
- `GET /api/orders/{order_id}` - Get order details
- `GET /api/orders/` - List orders (with optional filters)
  - Query params: `skip`, `limit`, `batch_id`, `status_filter`

See full API documentation at `/docs` when running the server.

## Support

For Railway-specific help:
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

For FastAPI help:
- Docs: https://fastapi.tiangolo.com
