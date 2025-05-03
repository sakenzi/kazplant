from fastapi import APIRouter
from app.api.auth.auth_api import router as auth_router
from app.api.plants.plant_api import router as plant_router
from app.api.users.user_api import router as user_router
from app.api.questions.question_api import router as question_router
from app.api.photos.photo_api import router as photo_router
from app.api.leafs.leaf_api import router as leaf_router
from app.api.training.training_api import router as train_router
from app.api.ai_plants.ai_plant_api import router as ai_plants_router
from app.api.segmentations.segmentation_api import router as segmentations_router


route = APIRouter()

route.include_router(auth_router, prefix='/auth', tags=["USER_AUTHENTICATION"])
route.include_router(plant_router, prefix='/plants', tags=["PLANTS"])
route.include_router(user_router, prefix='/users', tags=["USERS"])
route.include_router(question_router, prefix='/questions', tags=["QUESTIONS"])
route.include_router(photo_router, prefix='/photo', tags=["PHOTOS"])
route.include_router(leaf_router, prefix='/leafs', tags=["LEAFS"])
route.include_router(train_router, prefix='/train', tags=["TRAIN"])
route.include_router(ai_plants_router, prefix='/ai_plants', tags=["AI_PLANTS"])
route.include_router(segmentations_router, prefix='/segmentations', tags=["SEGMENTATIONS"])