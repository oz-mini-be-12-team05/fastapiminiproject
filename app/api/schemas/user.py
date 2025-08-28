from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, SecretStr, ConfigDict, model_validator

class SignupRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=50)
    password: SecretStr = Field(..., min_length=8, max_length=72)
    password_confirm: SecretStr = Field(..., min_length=8, max_length=72)

    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "user@example.com", "name": "홍길동", "password": "P@ssw0rd!", "password_confirm": "P@ssw0rd!"}
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

class LogoutRequest(BaseModel):
    reason: Optional[str] = None

class TokenResponse(BaseModel):
    token_type: Literal["Bearer"] = "Bearer"
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = Field(..., ge=1)

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

    model_config = ConfigDict(from_attributes=True)  # tortoise 객체 -> pydantic 변환

class UpdateMeRequest(BaseModel):
    # 프로필 필드
    name: Optional[str] = Field(None, max_length=100)
    nickname: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)

    # ✅ 비밀번호 변경용 필드 추가
    current_password: Optional[SecretStr] = None
    new_password: Optional[SecretStr] = Field(None, min_length=8, max_length=72)