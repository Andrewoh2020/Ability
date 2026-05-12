from fastapi import APIRouter

from app.models.common import ApiResponse
from app.services.app_service import app_service


router = APIRouter(tags=["feeds"])


@router.get("/featured")
async def list_featured_app():
    data = await app_service.list_featured_app()
    return ApiResponse(data=data)

@router.get("/popular")
async def list_popular_app():
    data = await app_service.list_popular_app()
    return ApiResponse(data=data)

@router.get("/discovered")
async def list_discovered_app(
    page: int = 1,
    category: str | None = None,
    size: int = 12,
):
    size = min(max(size, 1), 100)
    data = await app_service.list_discovered_app(page, category, size)
    return ApiResponse(data=data)
