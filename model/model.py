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

    plants = relationship("Plant", back_populates="user")
    leafs = relationship("Leaf", back_populates="user")


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

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship("User", back_populates="plants")
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

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates='leafs')
    leaf_diseases = relationship("LeafDisease", back_populates="leaf")


class Disease(Base):
    __tablename__ = 'diseases'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), default="")
    treatment = Column(Text, default="")
    prevention = Column(Text, default="")

    leaf_diseases = relationship("LeafDisease", back_populates="disease")


class LeafDisease(Base):
    __tablename__ = "leaf_diseases"

    id = Column(Integer, primary_key=True, index=True)
    leaf_id = Column(Integer, ForeignKey("leafs.id"), nullable=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)

    leaf = relationship("Leaf", back_populates="leaf_diseases")
    disease = relationship("Disease", back_populates="leaf_diseases")


"""AI"""
class AIPlant(Base):
    __tablename__ = "ai_plants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, default="")

    ai_photos = relationship("AIPhoto", back_populates="ai_plant")


class AIType(Base):
    __tablename__ = "ai_types"

    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), default="")

    ai_photos = relationship("AIPhoto", back_populates="ai_type")


class AIPhoto(Base):
    __tablename__ = "ai_photos"

    id = Column(Integer, primary_key=True, index=True)
    photo = Column(Text, default="")

    ai_plant_id = Column(Integer, ForeignKey("ai_plants.id"), nullable=True)
    ai_type_id = Column(Integer, ForeignKey("ai_types.id"), nullable=True)

    ai_plant = relationship("AIPlant", back_populates="ai_photos")
    ai_type = relationship("AIType", back_populates="ai_photos")


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), default="")
    epochs = Column(Integer, default=0)
    batch_size = Column(Integer, default=0)
    best_val_accuracy = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    training_epochs = relationship("TrainingEpoch", back_populates="training_session")


class TrainingEpoch(Base):
    __tablename__ = "training_epochs"

    id = Column(Integer, primary_key=True, index=True)
    epoch_num = Column(Integer, default=0)
    train_loss = Column(Float, default=0)
    train_accuracy = Column(Float, default=0)
    val_accuracy = Column(Float, default=0)
    
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=True)

    training_session = relationship("TrainingSession", back_populates="training_epochs")