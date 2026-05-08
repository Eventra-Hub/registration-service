from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


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
