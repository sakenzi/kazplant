from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import uuid
from sqlalchemy.future import select
from model.model import Leaf, Disease, LeafDisease
from app.api.leafs.commands.model import classify_leaf
from fastapi import UploadFile, HTTPException
from sqlalchemy import insert


UPLOAD_DIR = "uploads/photos/leafs"

async def create_leaf(
    file: UploadFile,
    db: AsyncSession, 
    user_id: int
) -> LeafDisease:
    filename = f"{uuid.uuid4()}.jpg"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    disease_id = classify_leaf(path)  

    result = await db.execute(select(Disease).where(Disease.id == disease_id))
    disease = result.scalar_one_or_none()
    if not disease:
        raise HTTPException(status_code=404, detail=f"Disease ID {disease_id} not found")

    leaf = Leaf(photo=path, user_id=user_id)
    db.add(leaf)
    await db.flush()

    leaf_disease = LeafDisease(leaf_id=leaf.id, disease_id=disease.id)
    db.add(leaf_disease)
    await db.commit()

    await db.refresh(leaf_disease, attribute_names=["leaf", "disease"])

    return leaf_disease