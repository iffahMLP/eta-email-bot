import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


# Set up logging
logging.basicConfig(
    filename="email_log.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class EmailHandler:
    def __init__(self):
        """Initialize email credentials from environment variables."""
        self.sender_email = os.getenv("EMAIL_USER")
        self.sender_password = os.getenv("EMAIL_PASS")

        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials missing in .env file")

    def send_email(self, recipient_email, order_number):
        """Send an email notification to the recipient."""
        subject = f"Update on Your Order {order_number}"
        body = f"""
        Hello,

        We wanted to update you regarding your order {order_number}.
        Please reach out if you need further assistance.

        Best regards,
        ML Performance Team
        """

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            print(f"✅ Email sent to {recipient_email} for order {order_number}")
            logging.info(f"Email sent to {recipient_email} for order {order_number}")

            return True
        except Exception as e:
            print(f"❌ Failed to send email to {recipient_email}: {e}")
            return False
