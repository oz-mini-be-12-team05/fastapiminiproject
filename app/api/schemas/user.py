from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, SecretStr, ConfigDict, model_validator


# ----------------------
# Auth / User Schemas
# ----------------------
class SignupRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=50)
    password: SecretStr = Field(..., min_length=8, max_length=72)
    password_confirm: SecretStr = Field(..., min_length=8, max_length=72)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "name": "홍길동",
            "password": "P@ssw0rd!",
            "password_confirm": "P@ssw0rd!",
        }
    })

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("password and password_confirm do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=72)
    remember_me: bool = False

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "user@example.com", "password": "P@ssw0rd!", "remember_me": False}
    })


# 쿠키 방식도 지원하고 싶다면 refresh_token을 optional 로 두고,
# 바디에 없으면 쿠키에서 읽도록 엔드포인트에서 처리.
class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(
        None, min_length=20, description="JWT refresh token (쿠키 사용 시 생략 가능)"
    )
    reason: Optional[str] = None


# OAuth2 표준 관점에서 소문자 권장. 호환 위해 둘 다 허용하려면 Literal["bearer", "Bearer"].
class TokenResponse(BaseModel):
    token_type: Literal["bearer"] = "bearer"
    access_token: str
    refresh_token: Optional[str] = None  # 로그인 응답에는 존재, refresh 응답엔 보통 없음
    expires_in: int = Field(..., ge=1)   # access 만료(초)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "token_type": "bearer",
            "access_token": "<JWT>",
            "refresh_token": "<JWT>",
            "expires_in": 1800,
        }
    })


class MessageResponse(BaseModel):
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20, description="JWT refresh token")


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UpdateMeRequest(BaseModel):
    # 프로필 필드
    name: Optional[str] = Field(None, max_length=100)
    nickname: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)

    # 비밀번호 변경용
    current_password: Optional[SecretStr] = None
    new_password: Optional[SecretStr] = Field(None, min_length=8, max_length=72)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "홍길동",
            "nickname": "길동",
            "phone_number": "010-1234-5678",
            "current_password": "P@ssw0rd!",
            "new_password": "N3wP@ssw0rd!",
        }
    })
