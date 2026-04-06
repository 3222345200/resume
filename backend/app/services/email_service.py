import smtplib
from email.message import EmailMessage

from fastapi import HTTPException, status

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def _send_email(subject: str, email: str, content: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise EmailDeliveryError("Email service is not configured.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = email
    message.set_content(content)

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
            return

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
            if settings.smtp_use_starttls:
                server.starttls()
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except Exception as exc:
        raise EmailDeliveryError("Failed to send verification email. Please try again later.") from exc


def send_register_verification_email(email: str, code: str) -> None:
    _send_email(
        "OfferPilot registration code",
        email,
        (
            "You are registering an OfferPilot account.\n\n"
            f"Your verification code is: {code}\n"
            f"This code expires in {settings.auth_email_code_expire_minutes} minutes.\n\n"
            "If you did not request this, please ignore this email."
        ),
    )


def send_password_reset_email(email: str, code: str) -> None:
    _send_email(
        "OfferPilot password reset code",
        email,
        (
            "You requested to reset your OfferPilot password.\n\n"
            f"Your verification code is: {code}\n"
            f"This code expires in {settings.auth_email_code_expire_minutes} minutes.\n\n"
            "If you did not request this, please ignore this email."
        ),
    )


def raise_email_delivery_http_error(exc: EmailDeliveryError) -> None:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
