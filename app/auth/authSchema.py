from pydantic import BaseModel, EmailStr, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str

class Password(BaseModel):
    user_password: str

    @field_validator('user_password')
    def validate_password_length(cls, v):
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters long')
        if len(v) > 50:  # Optional maximum length
            raise ValueError('Password must not exceed 50 characters')
        return v

class Email(BaseModel):
    user_email: EmailStr

class Login(Email, Password):
    pass
