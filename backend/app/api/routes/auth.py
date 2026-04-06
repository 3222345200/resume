from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import (
    CaptchaResponseSchema,
    ResetPasswordSchema,
    SendRegisterCodeResponseSchema,
    SendRegisterCodeSchema,
    SendPasswordResetCodeSchema,
    TokenResponseSchema,
    UserLoginSchema,
    UserReadSchema,
    UserRegisterSchema,
)
from app.services.auth_verification import (
    build_captcha_svg,
    create_captcha_challenge,
    ensure_captcha_valid,
    ensure_email_code_send_allowed,
    get_challenge_or_404,
    issue_email_code,
    mark_challenge_used,
    verify_email_code,
)
from app.services.email_service import (
    EmailDeliveryError,
    raise_email_delivery_http_error,
    send_password_reset_email,
    send_register_verification_email,
)

router = APIRouter(prefix='/auth', tags=['auth'])
logger = get_logger('auth')


def _to_user_schema(user: User) -> UserReadSchema:
    return UserReadSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        email_verified=bool(user.email_verified),
        created_at=user.created_at.isoformat(),
    )


def _has_login_access(user: User) -> bool:
    return user.email is None or bool(user.email_verified)


@router.get('/captcha', response_model=CaptchaResponseSchema)
def get_captcha(
    purpose: str = Query(default='register', pattern='^(register|password_reset)$'),
    db: Session = Depends(get_db),
) -> CaptchaResponseSchema:
    challenge = create_captcha_challenge(db, purpose=purpose)
    logger.info('captcha_created challenge_id=%s', challenge.id)
    return CaptchaResponseSchema(
        captcha_id=challenge.id,
        captcha_svg=build_captcha_svg(challenge.captcha_code),
        expires_at=challenge.captcha_expires_at.isoformat(),
    )


@router.post('/send-register-code', response_model=SendRegisterCodeResponseSchema)
def send_register_code(payload: SendRegisterCodeSchema, db: Session = Depends(get_db)) -> SendRegisterCodeResponseSchema:
    email = payload.email.strip().lower()
    logger.info('send_register_code_requested email=%s verification_id=%s', email, payload.captcha_id)

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        logger.warning('send_register_code_rejected_email_exists email=%s', email)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='该邮箱已注册，请直接登录')

    challenge = get_challenge_or_404(db, payload.captcha_id, purpose='register')
    ensure_captcha_valid(challenge, payload.captcha_answer)
    ensure_email_code_send_allowed(challenge)

    code = issue_email_code(challenge, email)
    try:
        send_register_verification_email(email, code)
    except EmailDeliveryError as exc:
        logger.exception('send_register_code_email_delivery_failed email=%s verification_id=%s', email, challenge.id)
        db.rollback()
        raise_email_delivery_http_error(exc)

    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    logger.info('send_register_code_succeeded email=%s verification_id=%s', email, challenge.id)

    return SendRegisterCodeResponseSchema(
        message='邮箱验证码已发送，请查收邮件',
        verification_id=challenge.id,
        cooldown_seconds=settings.auth_email_code_cooldown_seconds,
    )


@router.post('/register', response_model=TokenResponseSchema, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterSchema, db: Session = Depends(get_db)) -> TokenResponseSchema:
    email = payload.email.strip().lower()
    logger.info('register_requested username=%s email=%s verification_id=%s', payload.username, email, payload.verification_id)

    existing = db.query(User).filter(User.username == payload.username).first()
    if existing is not None:
        logger.warning('register_rejected_username_exists username=%s', payload.username)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='用户名已存在')

    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email is not None:
        logger.warning('register_rejected_email_exists email=%s', email)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='该邮箱已注册，请直接登录')

    challenge = get_challenge_or_404(db, payload.verification_id, purpose='register')
    verify_email_code(challenge, email, payload.email_code)

    user = User(
        username=payload.username,
        email=email,
        email_verified=True,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    mark_challenge_used(db, challenge)
    logger.info('register_succeeded user_id=%s username=%s email=%s', user.id, user.username, user.email)
    return TokenResponseSchema(access_token=create_access_token(user.username), user=_to_user_schema(user))


@router.post('/send-password-reset-code', response_model=SendRegisterCodeResponseSchema)
def send_password_reset_code(payload: SendPasswordResetCodeSchema, db: Session = Depends(get_db)) -> SendRegisterCodeResponseSchema:
    email = payload.email.strip().lower()
    logger.info('send_password_reset_code_requested email=%s verification_id=%s', email, payload.captcha_id)

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning('send_password_reset_code_rejected_email_missing email=%s', email)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This email is not registered.')

    challenge = get_challenge_or_404(db, payload.captcha_id, purpose='password_reset')
    ensure_captcha_valid(challenge, payload.captcha_answer)
    ensure_email_code_send_allowed(challenge)

    code = issue_email_code(challenge, email)
    try:
        send_password_reset_email(email, code)
    except EmailDeliveryError as exc:
        logger.exception('send_password_reset_code_email_delivery_failed email=%s verification_id=%s', email, challenge.id)
        db.rollback()
        raise_email_delivery_http_error(exc)

    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    logger.info('send_password_reset_code_succeeded email=%s verification_id=%s', email, challenge.id)

    return SendRegisterCodeResponseSchema(
        message='Password reset code sent. Please check your email.',
        verification_id=challenge.id,
        cooldown_seconds=settings.auth_email_code_cooldown_seconds,
    )


@router.post('/reset-password')
def reset_password(payload: ResetPasswordSchema, db: Session = Depends(get_db)) -> dict[str, str]:
    email = payload.email.strip().lower()
    logger.info('reset_password_requested email=%s verification_id=%s', email, payload.verification_id)

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        logger.warning('reset_password_rejected_email_missing email=%s', email)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This email is not registered.')

    challenge = get_challenge_or_404(db, payload.verification_id, purpose='password_reset')
    verify_email_code(challenge, email, payload.email_code)

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()
    mark_challenge_used(db, challenge)
    logger.info('reset_password_succeeded user_id=%s email=%s', user.id, email)
    return {'message': 'Password reset successful. Please log in with your new password.'}


@router.post('/login', response_model=TokenResponseSchema)
def login(payload: UserLoginSchema, db: Session = Depends(get_db)) -> TokenResponseSchema:
    logger.info('login_requested username=%s', payload.username)
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        logger.warning('login_failed_invalid_credentials username=%s', payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='账号或密码错误')
    if not _has_login_access(user):
        logger.warning('login_failed_unverified user_id=%s username=%s', user.id, user.username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='该账号尚未完成邮箱验证，暂时不能使用')
    logger.info('login_succeeded user_id=%s username=%s', user.id, user.username)
    return TokenResponseSchema(access_token=create_access_token(user.username), user=_to_user_schema(user))


@router.get('/me', response_model=UserReadSchema)
def me(current_user: User = Depends(get_current_user)) -> UserReadSchema:
    if not _has_login_access(current_user):
        logger.warning('me_rejected_unverified user_id=%s username=%s', current_user.id, current_user.username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='当前账号尚未完成邮箱验证')
    logger.info('me_succeeded user_id=%s username=%s', current_user.id, current_user.username)
    return _to_user_schema(current_user)
