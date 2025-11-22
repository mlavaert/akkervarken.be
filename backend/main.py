from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import os
import logging
from database import engine
from orders import router as orders_router
from admin import router as admin_router
from products import router as products_router
from batches import api_router as batches_api_router, admin_router as batches_admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Akkervarken API",
    version="1.0.0",
    description="Backend API for Akkervarken.be webshop and POS system",
)


@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup"""
    logger.info("Running startup tasks...")

    # Run database migrations using Alembic API
    try:
        logger.info("Running database migrations...")

        from alembic.config import Config
        from alembic import command

        # Create Alembic config
        alembic_cfg = Config("alembic.ini")

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        logger.info("✅ Migrations completed successfully")
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        logger.exception("Full migration error traceback:")
        # Don't crash the app, just log the error
        # This allows the API to still start if migrations fail


# CORS setup - allow requests from your website
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://akkervarken.be").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (shared admin assets, etc.)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routers
# Public API endpoints (no auth required)
app.include_router(products_router)
app.include_router(batches_api_router)
app.include_router(orders_router)

# Admin endpoints (auth required)
app.include_router(admin_router)
app.include_router(batches_admin_router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Akkervarken API is running!",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    """Health check endpoint with database connection status"""
    health_status = {"status": "healthy", "api": "ok", "database": "unknown"}

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
