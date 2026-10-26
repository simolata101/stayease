import logging
from flask import current_app
from flask_mail import Message
from app import mail

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_email(to_email, subject, body_text, body_html=None):
        """Sends an email using Flask-Mail with error handling."""
        try:
            # Check if mail server is configured
            if not current_app.config.get('MAIL_SERVER'):
                logger.info(f"[Email Disabled] To: {to_email} | Subject: {subject} | Body: {body_text}")
                return False, "Mail server not configured."

            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body_text,
                html=body_html or f"<p>{body_text}</p>"
            )
            
            mail.send(msg)
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Email sent successfully."
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False, f"Email delivery failed: {str(e)}"

    @staticmethod
    def send_booking_status_email(to_email, recipient_name, booking_ref, status, custom_message):
        """Sends a formatted notification for booking status changes."""
        subject = f"StayEase Resort - Booking {booking_ref} Status: {status.upper()}"
        body = f"Hello {recipient_name},\n\n{custom_message}\n\nBooking Reference: {booking_ref}\nStatus: {status.capitalize()}\n\nThank you for choosing StayEase Resort!"
        
        return NotificationService.send_email(to_email, subject, body)
