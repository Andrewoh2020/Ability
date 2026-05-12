from datetime import datetime
from app.utils.common import utc_now
from uuid import UUID
from typing import Optional

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select, asc, desc, func, delete, update

from app.core.db import async_session
from app.models.user import Profile, UserLite
from app.models.comment import Comment, CommentLite, ReplyLite, CommentLikes
from app.models.app import App
from app.utils.common import SingletonMeta


def make_comment_lite(c: Comment, p: Profile, is_like: Optional[bool] = None) -> CommentLite:
    return CommentLite(
        id=c.id,
        parent_id=c.parent_id,
        content="[Comment Deleted]" if c.deleted_at else c.content,
        replies_count=c.replies_count,
        creator=UserLite(
            id=p.id,
            full_name=p.full_name,
            avatar_url=p.avatar_url
        ),
        created_at=c.created_at,
        likes_count=c.likes_count,
        is_like=is_like
    )

def make_reply_lite(c: Comment, p: Profile, is_like: Optional[bool] = None) -> ReplyLite:
    return ReplyLite(
        id=c.id,
        parent_id=c.parent_id,
        content=c.content,
        creator=UserLite(
            id=p.id,
            full_name=p.full_name,
            avatar_url=p.avatar_url
        ),
        created_at=c.created_at,
        likes_count=c.likes_count,
        is_like=is_like
    )

class CommentService(metaclass=SingletonMeta):
    async def list_comment(
        self,
        app_id: UUID,
        current_user_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 10
    ) -> tuple[list[CommentLite], int]:
        async with async_session() as session:
            count_stmt = (
                select(func.count(1))
                .where(Comment.app_id == app_id, Comment.parent_id.is_(None))
                .scalar_subquery()
            )

            stmt = (
                select(Comment, Profile, count_stmt.label("total"))
                .join(Profile, Comment.user_id == Profile.id)
                .where(Comment.app_id == app_id, Comment.parent_id.is_(None))
                .order_by(desc(Comment.created_at))
                .offset(offset)
                .limit(limit)
            )

            result = await session.exec(stmt)
            rows = result.all()

            if not rows:
                return [], 0

            total = rows[0][2] if rows else 0
            comment_ids = [row[0].id for row in rows]

            liked_comment_ids = set()
            if current_user_id and comment_ids:
                like_stmt = (
                    select(CommentLikes.comment_id)
                    .where(
                        CommentLikes.user_id == current_user_id,
                        CommentLikes.comment_id.in_(comment_ids)
                    )
                )
                like_result = await session.scalars(like_stmt)
                liked_comment_ids = set(like_result.all())

            data = []
            for c, p, _ in rows:
                is_liked = c.id in liked_comment_ids if current_user_id else None
                comment_lite = make_comment_lite(c, p, is_like=is_liked)
                data.append(comment_lite)

            return data, total

    async def list_reply(self, comment_id: UUID, current_user_id: Optional[str] = None) -> list[ReplyLite]:
        async with async_session() as session:
            # 查询所有回复
            stmt = (
                select(Comment, Profile)
                .join(Profile, Comment.user_id == Profile.id)
                .where(Comment.parent_id == comment_id)
                .order_by(asc(Comment.created_at))
            )

            result = await session.exec(stmt)
            rows = result.all()

            if not rows:
                return []

            reply_ids = [row[0].id for row in rows]

            liked_comment_ids = set()
            if current_user_id and reply_ids:
                like_stmt = (
                    select(CommentLikes.comment_id)
                    .where(
                        CommentLikes.user_id == current_user_id,
                        CommentLikes.comment_id.in_(reply_ids)
                    )
                )
                like_result = await session.scalars(like_stmt)
                liked_comment_ids = set(like_result.all())

            data = []
            for c, p in rows:
                is_liked = c.id in liked_comment_ids if current_user_id else None
                reply_lite = make_reply_lite(c, p, is_like=is_liked)
                data.append(reply_lite)

            return data

    async def create_comment(self, app_id: UUID, user_id: UUID, content: str, parent_id: UUID | None = None) -> UUID | None:
        async with async_session() as session:
            try:
                async with session.begin():
                    app = await session.get(App, app_id)
                    if not app:
                        logger.error(f"app not found: {str(app_id)}")
                        return None

                    if parent_id:
                        stmt = select(Comment).where(Comment.id == parent_id).with_for_update()
                        result = await session.exec(stmt)
                        parent_comment = result.first()
                        if not parent_comment:
                            logger.error(f"parent comment not found: {str(parent_id)}")
                            return None
                        if parent_comment.parent_id:
                            logger.error(f"parent comment {str(parent_id)} has parent comment: {str(parent_comment.parent_id)}")
                            return None
                        parent_comment.replies_count += 1
                        session.add(parent_comment)

                    comment = Comment(content=content, app_id=app_id, user_id=user_id, parent_id=parent_id)
                    session.add(comment)
                    await session.flush()
                    comment_id = comment.id
                    await session.commit()
                    return comment_id
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def update_comment(self, comment_id: UUID, user_id: UUID, content: str) -> bool:
        async with async_session() as session:
            try:
                async with session.begin():
                    stmt = select(Comment).where(Comment.id == comment_id).with_for_update()
                    result = await session.exec(stmt)
                    comment = result.first()

                    if not comment:
                        logger.error(f"comment not found: {str(comment_id)}")
                        return False

                    if comment.user_id != user_id:
                        logger.error("Forbidden")
                        return False
                    comment.content = content
                    comment.updated_at = utc_now()
                    session.add(comment)
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def delete_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        async with async_session() as session:
            try:
                async with session.begin():
                    comment = await session.get(Comment, comment_id)

                    if not comment:
                        logger.error(f"comment not found: {str(comment_id)}")
                        return False

                    if comment.user_id != user_id:
                        logger.error("Forbidden")
                        return False

                    if comment.parent_id:
                        parent_stmt = select(Comment).where(Comment.id == comment.parent_id).with_for_update()
                        result = await session.exec(parent_stmt)
                        parent_comment = result.first()
                        if parent_comment:
                            parent_comment.replies_count -= 1
                            session.add(parent_comment)

                    await session.exec(delete(Comment).where(Comment.parent_id == comment_id))
                    await session.delete(comment)
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def like_comment(self, comment_id: UUID, user_id: UUID) -> bool:
        async with async_session() as session:
            try:
                async with session.begin():
                    comment = await session.get(Comment, comment_id)
                    if not comment:
                        logger.error(f"Comment not found: {str(comment_id)}")
                        return False, False

                    like_stmt = select(CommentLikes).where(
                        CommentLikes.comment_id == comment_id,
                        CommentLikes.user_id == user_id
                    ).with_for_update()
                    like_result = await session.exec(like_stmt)
                    existing_like = like_result.first()

                    if existing_like:
                        await session.delete(existing_like)

                        update_stmt = (
                            update(Comment)
                            .where(Comment.id == comment_id)
                            .values(likes_count=func.greatest(Comment.likes_count - 1, 0))
                        )
                        await session.exec(update_stmt)

                        return True

                    else:
                        new_like = CommentLikes(
                            comment_id=comment_id,
                            user_id=user_id
                        )
                        session.add(new_like)

                        update_stmt = (
                            update(Comment)
                            .where(Comment.id == comment_id)
                            .values(likes_count=Comment.likes_count + 1)
                        )
                        await session.exec(update_stmt)

                        return True

            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error in like_comment: {e}")
                raise e


comment_service = CommentService()
