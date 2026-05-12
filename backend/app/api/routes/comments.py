from html import escape
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, model_validator

from app.api.deps import UserDependency, OptionalUserDependency, SupabaseDependency
from app.models.common import ApiResponse
from app.services.comment_service import comment_service


router = APIRouter(tags=['comments'])


class CommentUpdate(BaseModel):
    content: str

    @model_validator(mode='before')
    def check_content_not_empty(cls, values):
        sanitized_content = escape(values.get('content', '').strip())
        if not sanitized_content:
            raise ValueError('invalid content')
        values['content'] = sanitized_content
        return values

class CommentCreate(CommentUpdate):
    app_id: UUID
    parent_id: Optional[UUID] = None

@router.post('')
async def create_comment(current_user: UserDependency, payload: CommentCreate):
    comment_id = await comment_service.create_comment(
        app_id=payload.app_id,
        user_id=current_user.id,
        content=payload.content,
        parent_id=payload.parent_id,
    )
    if not comment_id:
        return ApiResponse(code=1, message='app or comment not found')
    return ApiResponse(message='ok', data={'id': str(comment_id)})

@router.put('/{id}')
async def update_comment(current_user: UserDependency, id: UUID, payload: CommentUpdate):
    result = await comment_service.update_comment(
        comment_id=id,
        user_id=current_user.id,
        content=payload.content,
    )
    if not result:
        return ApiResponse(code=1, message='failed to update comment')
    return ApiResponse(message='ok')

@router.delete('/{id}')
async def delete_comment(current_user: UserDependency, id: UUID):
    result = await comment_service.delete_comment(comment_id=id, user_id=current_user.id)
    if not result:
        return ApiResponse(code=1, message='failed to delete comment')
    return ApiResponse(message='ok')

@router.get('/{id}/replies')
async def list_comment_replies(id: UUID, current_user: OptionalUserDependency):
    current_user_id = None
    if current_user:
        current_user_id = str(current_user.id)
    data = await comment_service.list_reply(comment_id=id, current_user_id=current_user_id)
    return ApiResponse(code=0, data=data)

@router.post("/{id}/like")
async def like(
    id: str,
    current_user: UserDependency,
    sb: SupabaseDependency,
):
    current_user_id = str(current_user.id)
    await comment_service.like_comment(comment_id=id, user_id=current_user_id)
    return ApiResponse()
