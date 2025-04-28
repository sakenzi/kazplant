from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str