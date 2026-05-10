from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal, Optional


Role = Literal["attendee", "organizer"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Optional[Role] = "attendee"

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if v is None:
            return "attendee"
        v = str(v).strip().lower()
        if v not in ("attendee", "organizer"):
            raise ValueError("role must be 'attendee' or 'organizer'")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    bio: str
    avatar_url: str


class UserUpdate(BaseModel):
    name: str
    bio: str
    avatar_url: str
