import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_verification import AuthVerificationChallenge

CAPTCHA_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ"
EMAIL_CODE_ALPHABET = string.digits
CAPTCHA_LENGTH = 4
EMAIL_CODE_LENGTH = 6


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _random_text(alphabet: str, length: int) -> str:
    return "".join(random.choice(alphabet) for _ in range(length))


def build_captcha_svg(code: str) -> str:
    chars = []
    palette = ["#0f172a", "#155eef", "#1d4ed8", "#334155"]
    for index, char in enumerate(code):
        x = 24 + index * 22
        y = 34 + (index % 2) * 5
        rotate = (-12, 9, -7, 11)[index % 4]
        color = palette[index % len(palette)]
        chars.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-size="24" '
            f'font-family="Verdana, Arial, sans-serif" font-weight="700" '
            f'transform="rotate({rotate} {x} {y})">{char}</text>'
        )

    noise = "".join(
        f'<line x1="{12 + i * 16}" y1="{10 + (i % 3) * 11}" x2="{28 + i * 16}" y2="{42 - (i % 3) * 8}" '
        f'stroke="rgba(21,94,239,0.18)" stroke-width="2" />'
        for i in range(4)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="132" height="48" viewBox="0 0 132 48" role="img" '
        'aria-label="captcha">'
        '<rect width="132" height="48" rx="12" fill="#f8fafc" />'
        f'{noise}{"".join(chars)}'
        '</svg>'
    )


def create_captcha_challenge(db: Session, purpose: str = "register") -> AuthVerificationChallenge:
    challenge = AuthVerificationChallenge(
        purpose=purpose,
        captcha_code=_random_text(CAPTCHA_ALPHABET, CAPTCHA_LENGTH),
        captcha_expires_at=_now() + timedelta(minutes=settings.auth_captcha_expire_minutes),
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def get_challenge_or_404(db: Session, challenge_id: str, purpose: str = "register") -> AuthVerificationChallenge:
    challenge = (
        db.query(AuthVerificationChallenge)
        .filter(
            AuthVerificationChallenge.id == challenge_id,
            AuthVerificationChallenge.purpose == purpose,
        )
        .first()
    )
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="验证码会话不存在，请刷新后重试")
    return challenge


def ensure_captcha_valid(challenge: AuthVerificationChallenge, captcha_answer: str) -> None:
    if challenge.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前验证码已使用，请重新获取")
    if challenge.captcha_expires_at < _now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="字母验证码已过期，请刷新后重试")
    if challenge.captcha_code.upper() != captcha_answer.strip().upper():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="字母验证码错误")


def ensure_email_code_send_allowed(challenge: AuthVerificationChallenge) -> None:
    if challenge.email_code_sent_at is None:
        return
    next_retry_at = challenge.email_code_sent_at + timedelta(seconds=settings.auth_email_code_cooldown_seconds)
    if next_retry_at > _now():
        remaining = int((next_retry_at - _now()).total_seconds()) + 1
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"请在 {remaining} 秒后再发送验证码")


def issue_email_code(challenge: AuthVerificationChallenge, email: str) -> str:
    code = _random_text(EMAIL_CODE_ALPHABET, EMAIL_CODE_LENGTH)
    current_time = _now()
    challenge.email = email.strip().lower()
    challenge.email_code = code
    challenge.email_code_sent_at = current_time
    challenge.email_code_expires_at = current_time + timedelta(minutes=settings.auth_email_code_expire_minutes)
    return code


def verify_email_code(challenge: AuthVerificationChallenge, email: str, email_code: str) -> None:
    if challenge.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该验证码已完成注册，请重新发起")
    if not challenge.email or challenge.email != email.strip().lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱与发送验证码时不一致")
    if challenge.email_code is None or challenge.email_code_expires_at is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先获取邮箱验证码")
    if challenge.email_code_expires_at < _now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱验证码已过期，请重新获取")
    if challenge.email_code != email_code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱验证码错误")


def mark_challenge_used(db: Session, challenge: AuthVerificationChallenge) -> None:
    challenge.used_at = _now()
    db.add(challenge)
    db.commit()
