from sqlalchemy import String, Column, Integer, func, DateTime, Text, ForeignKey, Float
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


class Plant(Base):
    __tablename__ = 'plants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), default="")
    description = Column(Text, default="")
    probability = Column(Float, default=0)
    rank = Column(String(100), default="")
    family = Column(String(200), default="")
    kingdom = Column(String(200), default="")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    plant_photo_ids = relationship("PlantPhotoID", back_populates="plant")


class PlantPhoto(Base):
    __tablename__ = 'plant_photos'

    id = Column(Integer, primary_key=True, index=True)
    photo = Column(Text, default="")

    plant_photo_ids = relationship("PlantPhotoID", back_populates="photo")


class PlantPhotoID(Base):
    __tablename__ = 'plant_photo_ids'

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    photo_id = Column(Integer, ForeignKey("plant_photos.id"), nullable=True)

    plant = relationship("Plant", back_populates="plant_photo_ids")
    photo = relationship("PlantPhoto", back_populates="plant_photo_ids")



class Leaf(Base):
    __tablename__ = 'leafs'

    id = Column(Integer, primary_key=True, index=True)
    photo = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)

    # plant = relationship("Plant", back_populates="leafs")