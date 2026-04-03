from fastapi import APIRouter

from app.modules.campaigns.router import router as campaigns_router
from app.modules.device_profiles.router import router as device_profiles_router
from app.modules.eligibility.router import router as eligibility_router
from app.modules.feedback.router import router as feedback_router
from app.modules.health.router import router as health_router
from app.modules.projects.router import router as projects_router
from app.modules.tasks.router import router as tasks_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(campaigns_router)
api_router.include_router(device_profiles_router)
api_router.include_router(eligibility_router)
api_router.include_router(feedback_router)
api_router.include_router(tasks_router)
