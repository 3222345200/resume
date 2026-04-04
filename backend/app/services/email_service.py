import smtplib
from email.message import EmailMessage

from fastapi import HTTPException, status

from app.core.config import settings


class EmailDeliveryError(RuntimeError):
    pass


def send_register_verification_email(email: str, code: str) -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise EmailDeliveryError("邮箱服务未配置，暂时无法发送验证码")

    message = EmailMessage()
    message["Subject"] = "OfferPilot 注册验证码"
    message["From"] = f'{settings.smtp_from_name} <{settings.smtp_from_email}>'
    message["To"] = email
    message.set_content(
        "你正在注册 OfferPilot。\n\n"
        f"本次邮箱验证码为：{code}\n"
        f"验证码 {settings.auth_email_code_expire_minutes} 分钟内有效。\n"
        "如果不是你本人操作，请忽略此邮件。"
    )

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
        raise EmailDeliveryError("验证码邮件发送失败，请稍后重试") from exc


def raise_email_delivery_http_error(exc: EmailDeliveryError) -> None:
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
