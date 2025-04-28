from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    fullname: str
    email: str
    password: str