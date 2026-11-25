# User data validation
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Information required to create a user account
class UserCreate(BaseModel):
    username: str = Field(min_length = 3, max_length = 50)
    email: EmailStr

# Data that can be edited
class UserUpdate(BaseModel):
    username: str | None = Field(default = None, min_length = 3, max_length = 50)
    email: EmailStr | None = None

# Data returned by the API
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
