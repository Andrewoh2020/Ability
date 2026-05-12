from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from supabase import AsyncClient

from app.core.db import get_db_session, get_supabase_client
from app.models.user import User


SupabaseDependency = Annotated[AsyncClient, Depends(get_supabase_client)]

DBSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="token")
optional_oauth2 = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

AccessTokenDependency = Annotated[str, Depends(reusable_oauth2)]
OptionalTokenDependency = Annotated[Optional[str], Depends(optional_oauth2)]


async def get_current_user(
    access_token: AccessTokenDependency,
    db: DBSessionDependency,
    sb: SupabaseDependency,
) -> User:
    """Get current user from access_token and validate at the same time"""
    try:
        response = await sb.auth.get_user(access_token)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.exec(select(User).where(User.id == response.user.id))
    user = result.first()

    if not user:
        logger.error("User not found in the database")
        raise HTTPException(status_code=404, detail="User not found")

    await ensure_user_profile(user, sb, db)

    return user

async def get_current_user_optional(
    access_token: OptionalTokenDependency,
    db: DBSessionDependency,
    sb: SupabaseDependency,
) -> Optional[User]:
    if not access_token:
        return None

    try:
        response = await sb.auth.get_user(access_token)
    except Exception:
        return None

    result = await db.exec(select(User).where(User.id == response.user.id))
    user = result.first()

    if user:
        await ensure_user_profile(user, sb, db)

    return user

async def ensure_user_profile(
    user: User,
    sb: SupabaseDependency,
    db: DBSessionDependency
) -> None:
    response = await sb.table("profiles").select("*").eq("id", str(user.id)).execute()

    if response.data:
        return None

    raw_metadata = user.raw_user_meta_data or {}

    profile_data = {
        "id": str(user.id),
        "full_name": raw_metadata.get("full_name"),
        "avatar_url": raw_metadata.get("avatar_url"),
    }
    await sb.table("profiles").upsert(
        profile_data,
        on_conflict="id",
        ignore_duplicates=True
    ).execute()

OptionalUserDependency = Annotated[Optional[User], Depends(get_current_user_optional)]

UserDependency = Annotated[User, Depends(get_current_user)]
