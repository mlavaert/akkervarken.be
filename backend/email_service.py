import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Set up Jinja2 environment for email templates
template_dir = os.path.join(os.path.dirname(__file__), "templates", "email")
jinja_env = Environment(loader=FileSystemLoader(template_dir))


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
        self.admin_email = os.getenv("ADMIN_EMAIL")
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])

        if not self.enabled:
            logger.warning("Email service not configured - emails will not be sent")

    async def send_email(
        self, to_email: str, subject: str, html_body: str, text_body: str = None
    ) -> bool:
        """Send an email"""
        if not self.enabled:
            logger.warning(
                f"Email not sent (service disabled): {subject} to {to_email}"
            )
            return False

        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            if text_body:
                message.attach(MIMEText(text_body, "plain", "utf-8"))
            message.attach(MIMEText(html_body, "html", "utf-8"))

            # Send email - use TLS for port 465, STARTTLS for 587
            use_tls = self.smtp_port == 465
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=use_tls,  # SSL/TLS for port 465
                start_tls=(not use_tls),  # STARTTLS for port 587
                timeout=10,  # 10 second timeout
            )

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            logger.exception("Full email error traceback:")
            return False

    async def send_order_confirmation_to_customer(
        self,
        customer_email: str,
        customer_name: str,
        order_id: int,
        batch_name: str,
        pickup_info: str,
        items: List[Dict],
        total: float,
    ) -> bool:
        """Send order confirmation email to customer"""

        subject = f"Bevestiging bestelling #{order_id} - Akkervarken.be"

        html_body = self._render_customer_confirmation_html(
            customer_name, order_id, batch_name, pickup_info, items, total
        )

        text_body = self._render_customer_confirmation_text(
            customer_name, order_id, batch_name, pickup_info, items, total
        )

        return await self.send_email(customer_email, subject, html_body, text_body)

    async def send_order_notification_to_admin(
        self,
        order_id: int,
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        batch_name: str,
        pickup_info: str,
        items: List[Dict],
        total: float,
        notes: str = None,
    ) -> bool:
        """Send new order notification to admin"""

        subject = f"Nieuwe bestelling #{order_id} - {customer_name}"

        html_body = self._render_admin_notification_html(
            order_id,
            customer_name,
            customer_phone,
            customer_email,
            batch_name,
            pickup_info,
            items,
            total,
            notes,
        )

        text_body = self._render_admin_notification_text(
            order_id,
            customer_name,
            customer_phone,
            customer_email,
            batch_name,
            pickup_info,
            items,
            total,
            notes,
        )

        return await self.send_email(self.admin_email, subject, html_body, text_body)

    def _render_customer_confirmation_html(
        self,
        name: str,
        order_id: int,
        batch: str,
        pickup: str,
        items: List[Dict],
        total: float,
    ) -> str:
        """Render customer confirmation email HTML"""
        template = jinja_env.get_template("customer-confirmation.html")
        return template.render(
            name=name,
            order_id=order_id,
            batch=batch,
            pickup=pickup,
            items=items,
            total=total,
        )


    def _render_customer_confirmation_text(
        self,
        name: str,
        order_id: int,
        batch: str,
        pickup: str,
        items: List[Dict],
        total: float,
    ) -> str:
        """Render customer confirmation email plain text"""
        template = jinja_env.get_template("customer-confirmation.txt")
        return template.render(
            name=name,
            order_id=order_id,
            batch=batch,
            pickup=pickup,
            items=items,
            total=total,
        )

    def _render_admin_notification_html(
        self,
        order_id: int,
        name: str,
        phone: str,
        email: str,
        batch: str,
        pickup: str,
        items: List[Dict],
        total: float,
        notes: str = None,
    ) -> str:
        """Render admin notification email HTML"""
        template = jinja_env.get_template("admin-notification.html")
        return template.render(
            order_id=order_id,
            name=name,
            phone=phone,
            email=email,
            batch=batch,
            pickup=pickup,
            items=items,
            total=total,
            notes=notes,
        )


    def _render_admin_notification_text(
        self,
        order_id: int,
        name: str,
        phone: str,
        email: str,
        batch: str,
        pickup: str,
        items: List[Dict],
        total: float,
        notes: str = None,
    ) -> str:
        """Render admin notification email plain text"""
        template = jinja_env.get_template("admin-notification.txt")
        return template.render(
            order_id=order_id,
            name=name,
            phone=phone,
            email=email,
            batch=batch,
            pickup=pickup,
            items=items,
            total=total,
            notes=notes,
        )


# Global email service instance
email_service = EmailService()
