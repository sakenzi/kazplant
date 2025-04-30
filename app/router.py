from fastapi import APIRouter
from app.api.auth.auth_api import router as auth_router
from app.api.plants.plant_api import router as plant_router
from app.api.users.user_api import router as user_router
from app.api.questions.question_api import router as question_router
from app.api.photos.photo_api import router as photo_router


route = APIRouter()

route.include_router(auth_router, prefix='/auth', tags=["USER_AUTHENTICATION"])
route.include_router(plant_router, prefix='/plants', tags=["PLANTS"])
route.include_router(user_router, prefix='/users', tags=["USERS"])
route.include_router(question_router, prefix='/questions', tags=["QUESTIONS"])
route.include_router(photo_router, prefix='/photo', tags=["PHOTOS"])