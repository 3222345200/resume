from pydantic import BaseModel, Field


class UserRegisterSchema(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=20,
        pattern=r"^[A-Za-z0-9]+$",
        description="Only English letters and numbers are allowed.",
    )
    password: str = Field(min_length=8, max_length=128)


class UserLoginSchema(BaseModel):
    username: str = Field(min_length=4, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    password: str = Field(min_length=8, max_length=128)


class UserReadSchema(BaseModel):
    id: str
    username: str
    created_at: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserReadSchema
