from fastapi import APIRouter
from .routes import auth, users, upload, apps, chat, feeds, comments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(upload.router, prefix="/upload")
api_router.include_router(apps.router, prefix="/apps")
api_router.include_router(chat.router, prefix="/chat")
api_router.include_router(feeds.router, prefix="/feeds")
api_router.include_router(comments.router, prefix="/comments")
