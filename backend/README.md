# Akkervarken Backend API

Minimal FastAPI backend for the Akkervarken.be order system.

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

3. **Run the server:**
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

### Step 4: Configure Environment Variables

1. Go to your FastAPI service in Railway
2. Click "Variables" tab
3. Add these variables:
   - `ALLOWED_ORIGINS` = `https://akkervarken.be`

### Step 5: Deploy

Railway automatically deploys when you push to GitHub!

```bash
git push
```

Railway will:
1. Detect changes
2. Build your app
3. Deploy it
4. Give you a URL like: `https://your-app.up.railway.app`

### Step 6: Verify Deployment

Visit your Railway URL:
- `https://your-app.up.railway.app/` - Should return JSON with "Akkervarken API is running!"
- `https://your-app.up.railway.app/health` - Should return `{"status": "ok"}`
- `https://your-app.up.railway.app/docs` - Swagger UI documentation

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── database.py          # Database connection setup
├── requirements.txt     # Python dependencies
├── railway.toml         # Railway deployment config
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Environment Variables

| Variable | Description | Set By |
|----------|-------------|--------|
| `DATABASE_URL` | PostgreSQL connection string | Railway (automatic) |
| `PORT` | Port to run the server on | Railway (automatic) |
| `ALLOWED_ORIGINS` | CORS allowed origins | You (manual) |

## Next Steps

Once deployed, you can:
1. Add order submission endpoint
2. Create database models for orders
3. Add email notifications
4. Build admin panel

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

## Useful Commands

```bash
# Run locally
uvicorn main:app --reload

# Run with specific port
uvicorn main:app --port 8080

# Run in production mode (no reload)
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Support

For Railway-specific help:
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

For FastAPI help:
- Docs: https://fastapi.tiangolo.com
