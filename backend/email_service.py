import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "bestellingen@akkervarken.be")
        self.admin_email = os.getenv("ADMIN_EMAIL", "info@akkervarken.be")
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])

        if not self.enabled:
            logger.warning("Email service not configured - emails will not be sent")

    async def send_email(
        self, to_email: str, subject: str, html_body: str, text_body: str = None
    ) -> bool:
        """Send an email"""
        if not self.enabled:
            logger.warning(f"Email not sent (service disabled): {subject} to {to_email}")
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
            use_tls = (self.smtp_port == 465)
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

    async def test_send_email(
        self, to_email: str, subject: str, html_body: str, text_body: str = None
    ):
        """Test email sending - raises exceptions instead of catching them"""
        if not self.enabled:
            raise Exception("Email service not enabled")

        message = MIMEMultipart("alternative")
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject

        if text_body:
            message.attach(MIMEText(text_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))

        # Send email - let exceptions bubble up for diagnostics
        # Use TLS for port 465, STARTTLS for 587
        use_tls = (self.smtp_port == 465)
        await aiosmtplib.send(
            message,
            hostname=self.smtp_host,
            port=self.smtp_port,
            username=self.smtp_user,
            password=self.smtp_password,
            use_tls=use_tls,  # SSL/TLS for port 465
            start_tls=(not use_tls),  # STARTTLS for port 587
            timeout=10,
        )

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
        self, name: str, order_id: int, batch: str, pickup: str, items: List[Dict], total: float
    ) -> str:
        """Render customer confirmation email HTML"""
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #6a8e6a; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .order-details { background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
        .total { font-size: 1.2em; font-weight: bold; margin-top: 15px; padding-top: 15px; border-top: 2px solid #6a8e6a; }
        .footer { text-align: center; padding: 20px; font-size: 0.9em; color: #666; }
        .button { display: inline-block; padding: 12px 24px; background-color: #6a8e6a; color: white; text-decoration: none; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bedankt voor je bestelling!</h1>
        </div>
        <div class="content">
            <p>Beste {{ name }},</p>
            <p>We hebben je bestelling goed ontvangen. Hieronder vind je een overzicht:</p>

            <div class="order-details">
                <h3>Bestelling #{{ order_id }}</h3>
                <p><strong>Batch:</strong> {{ batch }}</p>
                <p><strong>Ophalen:</strong> {{ pickup }}</p>

                <h4>Producten:</h4>
                {% for item in items %}
                <div class="item">
                    <span>{{ item.quantity }}x {{ item.name }}</span>
                    <span>€{{ "%.2f"|format(item.subtotal) }}</span>
                </div>
                {% endfor %}

                <div class="total">
                    <div class="item">
                        <span>Totaal:</span>
                        <span>€{{ "%.2f"|format(total) }}</span>
                    </div>
                </div>
            </div>

            <p><strong>Betaling:</strong> Contant of via QR code bij afhaling.</p>
            <p>We nemen binnenkort contact met je op om de bestelling te bevestigen en de afhaaldetails door te geven.</p>
            <p>Heb je vragen? Neem gerust contact met ons op!</p>
        </div>
        <div class="footer">
            <p>
                <strong>Akkervarken.be</strong><br>
                Wolfstede 7, 1745 Opwijk<br>
                info@akkervarken.be | +32 494 18 50 76
            </p>
        </div>
    </div>
</body>
</html>
        """)

        return template.render(
            name=name,
            order_id=order_id,
            batch=batch,
            pickup=pickup,
            items=items,
            total=total,
        )

    def _render_customer_confirmation_text(
        self, name: str, order_id: int, batch: str, pickup: str, items: List[Dict], total: float
    ) -> str:
        """Render customer confirmation email plain text"""
        text = f"""Beste {name},

We hebben je bestelling goed ontvangen. Hieronder vind je een overzicht:

BESTELLING #{order_id}
Batch: {batch}
Ophalen: {pickup}

PRODUCTEN:
"""
        for item in items:
            text += f"{item['quantity']}x {item['name']} - €{item['subtotal']:.2f}\n"

        text += f"\nTOTAAL: €{total:.2f}\n\n"
        text += """Betaling: Contant of via QR code bij afhaling.

We nemen binnenkort contact met je op om de bestelling te bevestigen en de afhaaldetails door te geven.

Heb je vragen? Neem gerust contact met ons op!

---
Akkervarken.be
Wolfstede 7, 1745 Opwijk
info@akkervarken.be | +32 494 18 50 76
"""
        return text

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
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #856404; color: white; padding: 20px; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .order-details { background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
        .customer-info { background-color: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #856404; }
        .total { font-size: 1.2em; font-weight: bold; margin-top: 15px; padding-top: 15px; border-top: 2px solid #856404; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔔 Nieuwe Bestelling #{{ order_id }}</h2>
        </div>
        <div class="content">
            <div class="customer-info">
                <h3>Klantgegevens</h3>
                <p><strong>Naam:</strong> {{ name }}</p>
                {% if phone %}
                <p><strong>Telefoon:</strong> <a href="tel:{{ phone }}">{{ phone }}</a></p>
                {% endif %}
                {% if email %}
                <p><strong>Email:</strong> <a href="mailto:{{ email }}">{{ email }}</a></p>
                {% endif %}
            </div>

            <div class="order-details">
                <p><strong>Batch:</strong> {{ batch }}</p>
                <p><strong>Ophalen:</strong> {{ pickup }}</p>

                <h4>Producten:</h4>
                {% for item in items %}
                <div class="item">
                    <span>{{ item.quantity }}x {{ item.name }}</span>
                    <span>€{{ "%.2f"|format(item.subtotal) }}</span>
                </div>
                {% endfor %}

                <div class="total">
                    <div class="item">
                        <span>Totaal:</span>
                        <span>€{{ "%.2f"|format(total) }}</span>
                    </div>
                </div>

                {% if notes %}
                <div style="margin-top: 15px; padding: 10px; background-color: #f0f0f0; border-radius: 3px;">
                    <strong>Opmerkingen:</strong><br>
                    {{ notes }}
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
        """)

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
        text = f"""NIEUWE BESTELLING #{order_id}

KLANTGEGEVENS:
Naam: {name}
"""
        if phone:
            text += f"Telefoon: {phone}\n"
        if email:
            text += f"Email: {email}\n"

        text += f"\nBatch: {batch}\nOphalen: {pickup}\n\nPRODUCTEN:\n"

        for item in items:
            text += f"{item['quantity']}x {item['name']} - €{item['subtotal']:.2f}\n"

        text += f"\nTOTAAL: €{total:.2f}\n"

        if notes:
            text += f"\nOPMERKINGEN:\n{notes}\n"

        return text


# Global email service instance
email_service = EmailService()
