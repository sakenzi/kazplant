from fastapi import APIRouter
from app.api.auth.auth_api import router as auth_router
from app.api.plants.plant_api import router as plant_router


route = APIRouter()

route.include_router(auth_router, prefix='/auth', tags=["USER_AUTHENTICATION"])
route.include_router(plant_router, prefix='/plants', tags=["PLANTS"])