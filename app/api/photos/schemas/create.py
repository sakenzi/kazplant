from pydantic import BaseModel


class PhotoCreate(BaseModel):
    photo: str


class 