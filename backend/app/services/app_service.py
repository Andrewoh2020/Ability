from datetime import datetime
from app.utils.common import utc_now
from uuid import UUID

from loguru import logger
from sqlmodel import select, desc, update, and_
from sqlalchemy import func
from typing import Dict, Any, Optional, TypedDict

from app.core.db import async_session
from app.models.app import App, AppLite, AppLike, AppCollection
from app.models.user import Profile, UserLite, UserFollow
from app.utils.common import SingletonMeta


def get_start_of_month() -> datetime:
    now = utc_now()
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def make_app_lite(a: App, p: Profile) -> AppLite:
    return AppLite(
        id=a.id,
        name=a.name,
        description=a.description,
        category=a.category,
        icon=a.icon,
        cover=a.cover,
        creator=UserLite(id=p.id, full_name=p.full_name, avatar_url=p.avatar_url),
        created_at=a.created_at,
    )


class DiscoveredAppsResponse(TypedDict):
    apps: list[AppLite]
    hasMore: bool


class AppService(metaclass=SingletonMeta):
    async def app_community(self, app_id: UUID, current_user_id: Optional[str] = None) -> Dict[str, Any]:
        async with async_session() as session:
            update_stmt = update(App).where(App.id == app_id).values(page_view=App.page_view + 1)
            await session.exec(update_stmt)

            stmt = select(App, Profile).join(Profile, App.user_id == Profile.id).where(App.id == app_id)

            result = await session.exec(stmt)
            row = result.first()

            app, profile = row

            followers_stmt = select(func.count()).where(UserFollow.following_id == profile.id)
            followers_count = await session.scalar(followers_stmt) or 0

            response_data = {
                "id": str(app.id),
                "name": app.name,
                "description": app.description,
                "category": app.category,
                "icon": app.icon,
                "cover": app.cover,
                "page_view": app.page_view,
                "likes_count": app.likes_count,
                "bookmarks_count": app.bookmarks_count,
                "updated_at": app.updated_at,
                "creator": {
                    "id": str(profile.id),
                    "full_name": profile.full_name,
                    "avatar_url": profile.avatar_url,
                    "followers_count": followers_count,
                },
            }

            if current_user_id:
                bookmark_check_stmt = select(func.count()).where(
                    and_(
                        AppCollection.app_id == app_id,
                        AppCollection.user_id == current_user_id,
                        AppCollection.type == "bookmarked",
                    )
                )
                res_count = await session.scalar(bookmark_check_stmt) or 0
                has_bookmark = res_count > 0

                response_data["has_bookmark"] = has_bookmark

                collection_update_stmt = (
                    update(AppCollection)
                    .where(AppCollection.app_id == app_id, AppCollection.user_id == current_user_id)
                    .values(last_accessed_at=utc_now())
                )
                await session.exec(collection_update_stmt)
                await session.commit()

            return response_data

    async def bookmark_toggle(self, app_id: UUID, user_id: UUID) -> bool:
        async with async_session() as session:
            async with session.begin():
                app = await session.get(App, app_id)
                if not app:
                    logger.error(f"App not found: {str(app_id)}")
                    return False

                collection_stmt = (
                    select(AppCollection)
                    .where(
                        AppCollection.app_id == app_id,
                        AppCollection.user_id == user_id,
                        AppCollection.type == "bookmarked",
                    )
                    .with_for_update()
                )
                collection_result = await session.exec(collection_stmt)
                existing_collection = collection_result.first()

                if existing_collection:
                    await session.delete(existing_collection)

                    update_stmt = (
                        update(App)
                        .where(App.id == app_id)
                        .values(bookmarks_count=func.greatest(App.bookmarks_count - 1, 0))
                    )
                    await session.exec(update_stmt)
                else:
                    update_stmt = update(App).where(App.id == app_id).values(bookmarks_count=App.bookmarks_count + 1)
                    await session.exec(update_stmt)

                    now = utc_now()
                    new_collection = AppCollection(
                        app_id=app_id,
                        user_id=user_id,
                        type="bookmarked",
                        created_at=now,
                        last_accessed_at=now,
                    )
                    session.add(new_collection)

                return True

    async def list_featured_app(self) -> list[AppLite]:
        async with async_session() as session:
            data = []
            stmt = (
                select(App, Profile)
                .join(Profile, App.user_id == Profile.id)
                .where(App.is_featured.is_(True))
                .order_by(desc(App.created_at))
            )
            rows = await session.exec(stmt)
            for a, p in rows:
                data.append(make_app_lite(a, p))
            return data

    async def list_popular_app(self) -> list[AppLite]:
        async with async_session() as session:
            data = []
            stmt = (
                select(App, Profile)
                .join(Profile, App.user_id == Profile.id)
                .where(App.name.is_not(None))
                .where(App.created_at > get_start_of_month())
                .order_by(desc(App.created_at))
                .limit(5)
                .offset(0)
            )
            rows = await session.exec(stmt)
            for a, p in rows:
                data.append(make_app_lite(a, p))
            return data

    async def list_popular_app_v2(self) -> list[AppLite]:
        async with async_session() as session:
            # Calculate the popularity score:
            # Use the Reddit/Hacker News-style time decay algorithm
            # Popularity =
            # (Likes + Bookmarks * 2) / (Hours Since Creation + 2)^1.8

            # Calculate time difference (hours)
            hours_since_created = (
                func.extract('epoch', func.now() - App.created_at) / 3600
            )

            # Calculate the hot score
            hot_score = (
                (App.likes_count + App.bookmarks_count * 2) /
                func.power(hours_since_created + 2, 1.8)
            )

            stmt = (
                select(App, Profile, hot_score.label('hot_score'))
                .join(Profile, App.user_id == Profile.id)
                .where(App.name.is_not(None))
                .order_by(hot_score.desc())
                .limit(5)
            )

            rows = await session.exec(stmt)

            data = []
            for a, p, _ in rows:  # Ignore hot_score, we only need AppLite
                data.append(make_app_lite(a, p))

            return data

    async def list_discovered_app(
        self, page: int, category: str | None = None, size: int = 12
    ) -> DiscoveredAppsResponse:
        async with async_session() as session:
            if page < 1:
                page = 1
            limit = size
            data = []
            stmt = select(App, Profile).join(Profile, App.user_id == Profile.id).where(App.name.is_not(None))
            if category:
                stmt = stmt.where(App.category == category)
            start_index = (page - 1) * limit
            stmt = stmt.order_by(desc(App.created_at)).limit(limit).offset(start_index)
            rows = await session.exec(stmt)
            for a, p in rows:
                data.append(make_app_lite(a, p))
            hasMore = len(data) == limit
            return {"apps": data, "hasMore": hasMore}

    async def like_app(self, app_id: UUID, user_id: UUID) -> bool:
        async with async_session() as session:
            async with session.begin():
                app = await session.get(App, app_id)
                if not app:
                    logger.error(f"App not found: {str(app_id)}")
                    return False

                like_stmt = (
                    select(AppLike).where(AppLike.app_id == app_id, AppLike.user_id == user_id).with_for_update()
                )
                like_result = await session.exec(like_stmt)
                existing_like = like_result.first()

                if existing_like:
                    await session.delete(existing_like)

                    update_stmt = (
                        update(App).where(App.id == app_id).values(likes_count=func.greatest(App.likes_count - 1, 0))
                    )
                    await session.exec(update_stmt)

                else:
                    new_like = AppLike(app_id=app_id, user_id=user_id)
                    session.add(new_like)

                    update_stmt = update(App).where(App.id == app_id).values(likes_count=App.likes_count + 1)
                    await session.exec(update_stmt)
                return True

    async def get_app(self, app_id: UUID) -> Optional[App]:
        async with async_session() as session:
            app = await session.get(App, app_id)
            return app


app_service = AppService()
