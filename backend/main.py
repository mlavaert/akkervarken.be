from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
import logging
import subprocess
from database import engine
from orders import router as orders_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Akkervarken API",
    version="1.0.0",
    description="Backend API for Akkervarken.be webshop and POS system"
)


@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup"""
    logger.info("Running startup tasks...")

    # Run database migrations
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        logger.info(f"✅ Migrations completed successfully")
        if result.stdout:
            logger.info(f"Migration output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration failed: {e.stderr}")
        # Don't crash the app, just log the error
        # This allows the API to still start if migrations fail
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {str(e)}")

# CORS setup - allow requests from your website
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://akkervarken.be").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders_router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Akkervarken API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    """Health check endpoint with database connection status"""
    health_status = {
        "status": "healthy",
        "api": "ok",
        "database": "unknown"
    }

    # Check database connection
    if engine is None:
        health_status["database"] = "not_configured"
        health_status["status"] = "degraded"
    else:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = "error"
            health_status["database_error"] = str(e)
            health_status["status"] = "unhealthy"

    return health_status
