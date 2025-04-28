from sqlalchemy import String, Column, Integer, func, DateTime, Text
from sqlalchemy.orm import relationship
from database.db import Base



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), default="")
    full_name = Column(String(100), default="")
    email = Column(String(100), default="")
    password = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
