import os
from io import BytesIO
from pathlib import Path
from time import time
from typing import Annotated, Optional

from fastapi import APIRouter, Form, UploadFile, Request
from PIL import Image

from app.api.deps import UserDependency, SupabaseDependency, OptionalUserDependency
from app.models.common import ApiResponse
from app.models.user import UserProfile

router = APIRouter(tags=["users"])


@router.get("/me")
async def read_me(current_user: UserDependency, sb: SupabaseDependency):
    """Get current user profile"""
    # Get profile from profiles table
    response = await sb.table("profiles").select("*").eq("id", current_user.id).execute()
    if response.data:
        return ApiResponse(
            data={
                "profile": UserProfile(
                    email=current_user.email,
                    **response.data[0],
                )
            }
        )

    # Fallback to auth user data
    raw_metadata = current_user.raw_user_meta_data or {}
    return ApiResponse(
        data={
            "profile": UserProfile(
                id=current_user.id,
                email=current_user.email,
                full_name=raw_metadata.get("full_name"),
                avatar_url=raw_metadata.get("avatar_url"),
                created_at=current_user.created_at,
                updated_at=current_user.updated_at,
            )
        }
    )


@router.put("/me")
async def update_me(
    request: Request,
    current_user: UserDependency,
    sb: SupabaseDependency,
    full_name: Annotated[str, Form()],
    bio: Annotated[Optional[str], Form()] = None,
    birthday: Annotated[Optional[str], Form()] = None,
    country: Annotated[Optional[str], Form()] = None,
    city: Annotated[Optional[str], Form()] = None,
    file: Annotated[Optional[UploadFile], Form()] = None,
):
    avatar_url = None

    form_data = await request.form()

    interests = form_data.getlist("interests[]")

    if file:
        file_content = await file.read()
        if len(file_content) > 2 * 1024 * 1024:
            return ApiResponse(code=400, message="Image size should be less than 2MB")

        # Compress and convert to WEBP
        img = Image.open(BytesIO(file_content))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((512, 512), Image.Resampling.LANCZOS)

        output_buffer = BytesIO()
        img.save(output_buffer, format="WEBP", quality=85)
        compressed_bytes = output_buffer.getvalue()

        upload_response = await sb.storage.from_("static").upload(
            file=compressed_bytes,
            path=f"{str(current_user.id)}/avatar_{int(time())}.webp",
            file_options={"content-type": "image/webp"},
        )
        if not upload_response.path:
            return ApiResponse(code=1, message="failed to upload avatar")
        avatar_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/static/{upload_response.path}"
    data = {
        "full_name": full_name,
        "bio": bio,
        "birthday": birthday,
        "country": country,
        "city": city,
        "interests": interests,
    }
    if avatar_url:
        data["avatar_url"] = avatar_url
    update_data = {**data, "updated_at": "NOW()"}
    profile_data = await sb.table("profiles").select("*").eq("id", current_user.id).execute()
    if profile_data.data:
        await sb.table("profiles").update(update_data).eq("id", current_user.id).execute()
    else:
        insert_data = {"id": str(current_user.id), "created_at": "NOW()", **update_data}
        await sb.table("profiles").insert(insert_data).execute()

    return ApiResponse(code=0, message="updated", data=data)


@router.get("/{id}")
async def get_community(id: str, sb: SupabaseDependency, current_user: OptionalUserDependency):
    is_following = False
    if current_user and current_user.id != id:
        follow_check = (
            await sb.table("user_follows")
            .select("*", count="exact")
            .eq("follower_id", current_user.id)
            .eq("following_id", id)
            .execute()
        )
        is_following = len(follow_check.data) > 0 if follow_check.data else False

    following_result = await sb.table("user_follows").select("*", count="exact").eq("follower_id", id).execute()
    following_count = following_result.count if hasattr(following_result, "count") else 0

    followers_result = await sb.table("user_follows").select("*", count="exact").eq("following_id", id).execute()
    followers_count = followers_result.count if hasattr(followers_result, "count") else 0

    response = await sb.table("profiles").select("*").eq("id", id).execute()
    if response.data:
        user_data = response.data[0]
        return ApiResponse(
            data={
                "profile": {
                    "id": id,
                    "avatar_url": user_data.get("avatar_url"),
                    "full_name": user_data.get("full_name"),
                    "bio": user_data.get("bio"),
                    "following_count": following_count,
                    "followers_count": followers_count,
                },
                "is_following": is_following,
            }
        )

    user_response = await sb.auth.admin.get_user_by_id(id)
    if user_response and user_response.user:
        user = user_response.user
        raw_metadata = user.user_metadata or {}

        return ApiResponse(
            data={
                "profile": {
                    "id": id,
                    "avatar_url": raw_metadata.get("avatar_url"),
                    "full_name": raw_metadata.get("full_name"),
                    "bio": None,
                    "following_count": following_count,
                    "followers_count": followers_count,
                },
                "is_following": is_following,
            }
        )

    return ApiResponse(code=404, message="User Not Found")


@router.post("/{id}/follow")
async def follow(
    id: str,
    current_user: UserDependency,
    sb: SupabaseDependency,
):
    current_id = str(current_user.id)
    check_result = (
        await sb.table("user_follows")
        .select("*", count="exact")
        .eq("follower_id", current_id)
        .eq("following_id", id)
        .execute()
    )
    is_following = len(check_result.data) > 0 if check_result.data else False

    if is_following:
        await sb.table("user_follows").delete().eq("follower_id", current_id).eq("following_id", id).execute()
    else:
        insert_data = {
            "follower_id": current_id,
            "following_id": id,
        }
        await sb.table("user_follows").insert(insert_data).execute()

    return ApiResponse()


@router.get("/{id}/check_follow")
async def check_follow(
    id: str,
    current_user: OptionalUserDependency,
    sb: SupabaseDependency,
):
    if not current_user:
        return ApiResponse(data={"is_following": False})

    current_id = str(current_user.id)
    check_result = (
        await sb.table("user_follows")
        .select("*", count="exact")
        .eq("follower_id", current_id)
        .eq("following_id", id)
        .execute()
    )
    is_following = len(check_result.data) > 0 if check_result.data else False
    return ApiResponse(data={"is_following": is_following})


@router.get("/{id}/connections")
async def follow(
    id: str,
    current_user: OptionalUserDependency,
    sb: SupabaseDependency,
    page: int = 1,
    size: int = 20,
    type: str = "followers",
):
    if type != "following" and type != "followers":
        type = "followers"

    if type == "followers":
        follow_column = "following_id"
        user_column = "follower_id"
    else:
        follow_column = "follower_id"
        user_column = "following_id"

    if size < 5:
        size = 5
    elif size > 100:
        size = 100
    start_index = (page - 1) * size
    end_index = start_index + size - 1

    follows_result = (
        await sb.table("user_follows")
        .select(user_column, "created_at")
        .eq(follow_column, id)
        .order("created_at", desc=True)
        .range(start_index, end_index)
        .execute()
    )

    count_result = await sb.table("user_follows").select("*", count="exact").eq(follow_column, id).execute()
    total = count_result.count if hasattr(count_result, "count") else 0

    if not follows_result.data:
        return ApiResponse(data={"users": [], "hasMore": False, "total": total})

    user_ids = [item[user_column] for item in follows_result.data]

    profiles_result = await sb.table("profiles").select("id,avatar_url,full_name").in_("id", user_ids).execute()

    profile_map = {profile["id"]: profile for profile in profiles_result.data}

    if current_user:
        current_user_id = str(current_user.id)
        check_result = (
            await sb.table("user_follows")
            .select("following_id")
            .eq("follower_id", current_user_id)
            .in_("following_id", user_ids)
            .execute()
        )
        following_ids = set(item["following_id"] for item in check_result.data)
    else:
        following_ids = set()

    users = []
    for follow_item in follows_result.data:
        user_id = follow_item[user_column]
        if user_id in profile_map:
            user_data = {**profile_map[user_id], "followed_at": follow_item["created_at"]}
            if current_user and str(current_user.id) != user_id:
                user_data["is_following"] = user_id in following_ids
            users.append(user_data)

    has_more = len(users) == size

    return ApiResponse(data={"users": users, "hasMore": has_more, "total": total})
