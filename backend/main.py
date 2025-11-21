from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
import logging
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


@app.get("/debug/email-test")
async def test_email():
    """
    TEMPORARY: Test email configuration and send a test email.
    Returns detailed error information if email fails.
    TODO: Remove this endpoint in production after testing.
    """
    from email_service import email_service

    # Check if email is enabled
    if not email_service.enabled:
        return {
            "success": False,
            "error": "Email service not enabled",
            "config": {
                "smtp_host": email_service.smtp_host or "NOT SET",
                "smtp_port": email_service.smtp_port,
                "smtp_user": email_service.smtp_user or "NOT SET",
                "from_email": email_service.from_email,
                "admin_email": email_service.admin_email,
            }
        }

    # Try to send a test email to admin using test method that raises exceptions
    try:
        await email_service.test_send_email(
            to_email=email_service.admin_email,
            subject="Test email from Akkervarken API",
            html_body="<h1>Test Email</h1><p>This is a test email from the Akkervarken backend API.</p>",
            text_body="Test Email\n\nThis is a test email from the Akkervarken backend API."
        )

        return {
            "success": True,
            "message": "Email sent successfully! Check your inbox.",
            "config": {
                "smtp_host": email_service.smtp_host,
                "smtp_port": email_service.smtp_port,
                "smtp_user": email_service.smtp_user,
                "from_email": email_service.from_email,
                "to_email": email_service.admin_email,
            }
        }
    except Exception as e:
        logger.exception("Email test failed")
        import traceback
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc().split("\n")[-10:],  # Last 10 lines
            "config": {
                "smtp_host": email_service.smtp_host,
                "smtp_port": email_service.smtp_port,
                "smtp_user": email_service.smtp_user,
                "from_email": email_service.from_email,
                "to_email": email_service.admin_email,
            }
        }
