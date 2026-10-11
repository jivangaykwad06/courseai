import os
import smtplib

from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


MAIL_SERVER = os.getenv(
    "MAIL_SERVER",
    "smtp.gmail.com"
)

MAIL_PORT = int(
    os.getenv(
        "MAIL_PORT",
        "587"
    )
)

MAIL_USERNAME = os.getenv(
    "MAIL_USERNAME"
)

MAIL_PASSWORD = os.getenv(
    "MAIL_PASSWORD"
)


def send_verification_otp(
    recipient_email,
    otp
):

    if not MAIL_USERNAME:
        raise RuntimeError(
            "MAIL_USERNAME is missing from .env"
        )

    if not MAIL_PASSWORD:
        raise RuntimeError(
            "MAIL_PASSWORD is missing from .env"
        )


    message = EmailMessage()

    message["Subject"] = (
        "CourseAI - Email Verification OTP"
    )

    message["From"] = MAIL_USERNAME

    message["To"] = recipient_email


    message.set_content(
        f"""
Hello,

Welcome to CourseAI!

Your email verification OTP is:

{otp}

This OTP is valid for 10 minutes.

Please do not share this OTP with anyone.

Regards,
CourseAI
AI-Powered Personalized Learning
"""
    )


    server = None

    try:

        server = smtplib.SMTP(
            MAIL_SERVER,
            MAIL_PORT,
            timeout=30
        )

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(
            MAIL_USERNAME,
            MAIL_PASSWORD
        )

        server.send_message(
            message
        )

        return True

    finally:

        if server:

            try:
                server.quit()

            except Exception:
                pass