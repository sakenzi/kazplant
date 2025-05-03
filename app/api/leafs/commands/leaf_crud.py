from sqlalchemy.ext.asyncio import AsyncSession
import shutil
import uuid
from sqlalchemy.future import select
from model.model import Leaf, Disease, LeafDisease
from app.api.leafs.commands.model import classify_leaf
from fastapi import UploadFile, HTTPException
from sqlalchemy import insert
from sqlalchemy.orm import selectinload
from app.api.leafs.schemas.response import SegmentationResult
from torchvision import transforms
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import onnxruntime as ort
import cv2


UPLOAD_DIR = "uploads/photos/leafs"
MODEL_PATH = "app/api/leafs/commands/deeplabv3_resnet50.onnx"

async def create_leaf(
    photo: UploadFile,
    db: AsyncSession, 
    user_id: int
) -> LeafDisease:
    filename = f"{uuid.uuid4()}.jpg"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

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


async def get_all_leafs(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(LeafDisease)
        .join(LeafDisease.leaf)
        .options(selectinload(LeafDisease.leaf), selectinload(LeafDisease.disease))
        .where(LeafDisease.leaf.has(user_id=user_id))
    )
    return result.scalars().all()


async def process_segmentation(file: UploadFile) -> SegmentationResult:
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents)).convert("RGB")
        image = image.resize((512, 512))

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        image_tensor = transform(image).unsqueeze(0).numpy()

        ort_session = ort.InferenceSession(MODEL_PATH)
        input_name = ort_session.get_inputs()[0].name

        outputs = ort_session.run(None, {input_name: image_tensor})
        segmented_image = np.argmax(outputs[0], axis=1)[0]

        infected_class = 1
        infected_area_mask = segmented_image == infected_class
        infected_area = np.sum(infected_area_mask)
        total_area = infected_area_mask.size
        infection_ratio = infected_area / total_area

        if infection_ratio < 0.1:
            infection_level = "Малое поражение"
        elif infection_ratio < 0.3:
            infection_level = "Среднее поражение"
        else:
            infection_level = "Тяжелое поражение"

        segmented_image_color = cv2.applyColorMap(segmented_image.astype(np.uint8), cv2.COLORMAP_JET)
        image_np = np.array(image)
        image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        final_image = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)

        _, buffer = cv2.imencode(".jpg", final_image)
        segmented_image_base64 = base64.b64encode(buffer).decode("utf-8")

        return SegmentationResult(
            infection_ratio=infection_ratio,
            infection_level=infection_level
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")