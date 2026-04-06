from pydantic import BaseModel, Field


class UserRegisterSchema(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^[A-Za-z0-9]+$",
        description="Only English letters and numbers are allowed.",
    )
    password: str = Field(min_length=8, max_length=128)
    email: str = Field(max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    verification_id: str = Field(min_length=1, max_length=120)
    email_code: str = Field(min_length=4, max_length=12, pattern=r"^[0-9]+$")


class UserLoginSchema(BaseModel):
    username: str = Field(min_length=4, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    password: str = Field(min_length=8, max_length=128)


class SendRegisterCodeSchema(BaseModel):
    email: str = Field(max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    captcha_id: str = Field(min_length=1, max_length=120)
    captcha_answer: str = Field(min_length=4, max_length=12, pattern=r"^[A-Za-z]+$")


class SendPasswordResetCodeSchema(BaseModel):
    email: str = Field(max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    captcha_id: str = Field(min_length=1, max_length=120)
    captcha_answer: str = Field(min_length=4, max_length=12, pattern=r"^[A-Za-z]+$")


class ResetPasswordSchema(BaseModel):
    email: str = Field(max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    verification_id: str = Field(min_length=1, max_length=120)
    email_code: str = Field(min_length=4, max_length=12, pattern=r"^[0-9]+$")
    new_password: str = Field(min_length=8, max_length=128)


class CaptchaResponseSchema(BaseModel):
    captcha_id: str
    captcha_svg: str
    expires_at: str


class SendRegisterCodeResponseSchema(BaseModel):
    message: str
    verification_id: str
    cooldown_seconds: int


class UserReadSchema(BaseModel):
    id: str
    username: str
    email: str | None = None
    email_verified: bool
    created_at: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserReadSchema
