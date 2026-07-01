import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import settings


def generate_otp() -> str:
    """Generates a random 6-digit numeric OTP as a string."""
    return str(random.randint(100000, 999999))


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Sends the OTP to the user's email via SMTP.

    If SMTP credentials aren't configured (e.g. during local development),
    the OTP is printed to the console instead of failing, so the flow can
    still be tested end-to-end without a real mail server.
    """
    subject = "Your IntelliPath Password Reset OTP"
    body = (
        f"Hello,\n\n"
        f"Your One-Time Password (OTP) for resetting your IntelliPath password is:\n\n"
        f"    {otp}\n\n"
        f"This OTP is valid for {settings.OTP_EXPIRE_MINUTES} minutes. "
        f"If you did not request a password reset, you can safely ignore this email.\n\n"
        f"— The IntelliPath Team"
    )

    # Local-dev fallback: no SMTP configured, so just log it.
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print(f"[DEV MODE] No SMTP configured. OTP for {to_email} is: {otp}")
        return True

    try:
        message = MIMEMultipart()
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())

        return True
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        return False
