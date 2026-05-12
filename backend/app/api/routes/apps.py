from app.utils.common import utc_now
from io import BytesIO
import json
import os
from uuid import UUID, uuid4

import anthropic
from fastapi import APIRouter, HTTPException
import httpx
from loguru import logger
from PIL import Image
from pydantic import BaseModel
import replicate
from sqlalchemy import text

from app.api.deps import DBSessionDependency, OptionalUserDependency, SupabaseDependency, UserDependency
from app.models.app import AppUpdate, AppStage
from app.models.common import ApiResponse
from app.services.app_service import app_service
from app.services.comment_service import comment_service
from app.services.sandbox_service import sandbox_service
from app.utils.chat import ABILITY_CONFIG_PATH, ChatEvent, make_chat_event


router = APIRouter(tags=["apps"])

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_TOKEN"))


async def generate_and_upload_icon(prompt: str, sb: SupabaseDependency, max_retries: int = 3) -> str | None:
    system_prompt = """
        Role: You are an expert Visual Prompt Engineer for "Ability."
        Task: Transform an app description into a high-end 3D app icon prompt.
        Visual Style Guide (The "Wabi" Aesthetic):
        Object Composition: Choose a unique, simple, and impactful "Hero Object," floating in space with no base. The object should stand out on its own, exuding elegance and lightness. Ensure the shape is distinctive and streamlined, giving a sense of transparency and sophistication.
        Perspective: Use a 3D isometric or 3/4 front-facing view, presenting the object’s depth and high-end appeal. The object should appear as a finely crafted, tactile physical object, with light playing gracefully across its surface, highlighting intricate textures and details.
        Materials: Employ high-contrast textures that create layers of depth. Use a matte, premium base (such as silicone or fine plastic) for the bottom part of the object, while the hero object should feature smooth, refractive materials (like frosted glass, polished chrome, or glowing resin). This contrast between matte and glossy materials should evoke transparency and depth.
        Lighting: Use soft, studio-quality lighting that is delicate yet layered. Implement clear rim lighting (backlighting) to outline the object’s silhouette and subtle drop shadows to create a sense of depth and transparency. The lighting should emphasize the glossy reflections and intricate details of the object, enhancing the luxurious and high-end visual effect.
        Background: The object should be isolated against a plain white or soft gray background to ensure clarity and elegance. The background should be simple and unobtrusive, allowing the object to stand out as the focal point of the design, contributing to the high-end and transparent aesthetic.
        Instructions:
        Simplify the Metaphor: Focus on a single iconic, simple object that represents the core function of the app. For example: “A glowing floating orb” or “A smooth transparent geometric shape.” Avoid complex elements, ensuring the design is refined and visually striking.
        Output Format: Provide ONLY the final prompt text. No preamble.
    """

    for attempt in range(max_retries):
        try:
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
                            Generate an icon prompt for the following app:
                                <app_description>
                                    {prompt}
                                </app_description>
                            Output ONLY the icon prompt text, nothing else.
                        """,
                    }
                ],
            )

            icon_prompt = message.content[0].text

            icon_response = replicate_client.run(
                "bytedance/seedream-4.5",
                input={
                    "size": "2K",
                    "width": 1024,
                    "height": 1024,
                    "prompt": icon_prompt,
                    "max_images": 1,
                    "image_input": [],
                    "aspect_ratio": "1:1",
                    "sequential_image_generation": "disabled",
                },
            )

            if not icon_response or len(icon_response) == 0:
                logger.warning(f"Icon generation attempt {attempt + 1} returned empty response")
                continue

            file_bytes = icon_response[0].read()

            img = Image.open(BytesIO(file_bytes))
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)

            output_buffer = BytesIO()
            img.save(output_buffer, format="WEBP", quality=85)
            compressed_bytes = output_buffer.getvalue()

            now = utc_now()
            date_dir = now.strftime("%Y-%m-%d")
            filename = f"{uuid4().hex}.webp"

            upload_response = await sb.storage.from_("static").upload(
                file=compressed_bytes,
                path=f"icons/{date_dir}/{filename}",
                file_options={"content-type": "image/webp"},
            )

            if upload_response.path:
                url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/static/{upload_response.path}"
                return url
            else:
                logger.warning("upload supabase fail")

        except replicate.exceptions.ModelError as e:
            logger.warning(f"Icon generation attempt {attempt + 1} failed with ModelError: {e}")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            logger.error(f"Icon generation attempt {attempt + 1} failed with unexpected error: {e}")
            if attempt < max_retries - 1:
                continue

    return None


@router.get("")
async def list_my_app(
    current_user: UserDependency,
    sb: SupabaseDependency,
    page: int = 1,
    limit: int = 20,
):
    if limit < 5:
        limit = 5
    elif limit > 100:
        limit = 100
    start_index = (page - 1) * limit
    end_index = start_index + limit - 1
    result = (
        await sb.table("apps")
        .select("id,cover,name,description,category,icon")
        .eq("user_id", current_user.id)
        .order("created_at", desc=True)
        .range(start_index, end_index)
        .execute()
    )
    has_more = len(result.data) == limit
    return ApiResponse(data={"apps": result.data, "hasMore": has_more})


@router.get("/mix")
async def list_by_mix(
    current_user: OptionalUserDependency,
    db: DBSessionDependency,
    user_id: UUID | None = None,
    page: int = 1,
    limit: int = 20,
):
    if limit < 5:
        limit = 5
    elif limit > 100:
        limit = 100

    target_user_id = str(user_id) if user_id else (str(current_user.id) if current_user else None)
    if not target_user_id:
        return ApiResponse(data={"apps": [], "hasMore": False, "total": 0})

    offset = (page - 1) * limit

    sql = text("""
        SELECT a.id, a.cover, a.name, a.description, a.category, a.icon, c.last_accessed_at, c.type
        FROM app_collections c
        JOIN apps a ON c.app_id = a.id
        WHERE c.user_id = :user_id
        ORDER BY c.last_accessed_at DESC
        LIMIT :limit OFFSET :offset
    """)

    result = await db.execute(sql, {"user_id": target_user_id, "limit": limit, "offset": offset})
    rows = result.fetchall()

    apps = [
        {
            "id": str(row.id),
            "cover": row.cover,
            "name": row.name,
            "description": row.description,
            "category": row.category,
            "icon": row.icon,
            "type": row.type,
        }
        for row in rows
    ]

    count_sql = text("SELECT COUNT(*) FROM app_collections WHERE user_id = :user_id")
    count_result = await db.execute(count_sql, {"user_id": target_user_id})
    total = count_result.scalar() or 0

    has_more = len(apps) == limit

    return ApiResponse(data={"apps": apps, "hasMore": has_more, "total": total})


@router.get("/{id}")
async def get_app(id: str, current_user: UserDependency, sb: SupabaseDependency):
    result = await sb.table("apps").select("id,cover,name,description,category,icon,updated_at").eq("id", id).execute()

    await (
        sb.table("app_collections")
        .update({"last_accessed_at": utc_now().isoformat()})
        .eq("app_id", id)
        .eq("user_id", str(current_user.id))
        .execute()
    )

    return ApiResponse(data={"app": result.data[0]})


@router.get("/{id}/community")
async def get_app_community(id: str, current_user: OptionalUserDependency):
    user_id = None
    if current_user:
        user_id = current_user.id
    data = await app_service.app_community(app_id=id, current_user_id=user_id)
    return ApiResponse(data={"app": data})


@router.post("")
async def create_app(current_user: UserDependency, sb: SupabaseDependency):
    create_data = {"user_id": str(current_user.id)}

    result = await sb.table("apps").insert(create_data).execute()
    app_id = result.data[0]["id"]

    await (
        sb.table("app_collections")
        .insert(
            {
                "user_id": str(current_user.id),
                "app_id": app_id,
                "type": "owned",
            }
        )
        .execute()
    )

    return ApiResponse(data={"id": app_id})


@router.put("/{id}")
async def update_app(id: str, form_data: AppUpdate, current_user: UserDependency, sb: SupabaseDependency):
    update_data = form_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = "NOW()"

    await sb.table("apps").update(update_data).eq("id", id).eq("user_id", current_user.id).execute()
    return ApiResponse()


@router.delete("/{id}")
async def delete_app(id: UUID, current_user: UserDependency, sb: SupabaseDependency):
    await sb.table("apps").delete().eq("id", id).eq("user_id", current_user.id).execute()
    try:
        killed = await sandbox_service.kill_by_app_id(id)
        logger.info(f"sandbox of app {str(id)} killed: {killed}")
    except Exception as e:
        logger.error(e)
    return ApiResponse()


@router.get("/{id}/sandbox")
async def get_sandbox_info(id: UUID):
    sbx = await sandbox_service.get_by_app_id(id)
    if not sbx:
        return ApiResponse(code=1, message="sandbox not found")

    async with httpx.AsyncClient() as client:
        try:
            public_url = f"https://{sbx.get_host(3000)}"
            r = await client.get(public_url, timeout=1.0)
            if r.status_code == 200:
                data = {"status": 2, "public_url": public_url}
                return ApiResponse(code=0, data=data)
        except Exception as e:
            logger.error(e)

    return ApiResponse(code=0, data={"status": 0})


@router.post("/{id}/sandbox/actions/preview")
async def preview_sandbox(id: UUID):
    data = await sandbox_service.preview(id)
    return ApiResponse(code=0, message="ok", data=data)


@router.get("/{id}/messages")
async def list_messages(current_user: UserDependency, id: UUID):
    sbx = await sandbox_service.get_by_app_id(id)
    if not sbx:
        return ApiResponse(code=0, data=[])

    messages = []

    try:
        content = sbx.files.read(f"/home/user/.claude/projects/-home-user-app/{str(id)}.jsonl")
        lines = content.strip().splitlines()
        for line in lines:
            obj = json.loads(line)
            if obj.get("isVisibleInTranscriptOnly") or obj["type"] == "system" or "uuid" not in obj:
                continue
            msg = {
                "id": obj["uuid"],
                "timestamp": obj["timestamp"],
                "role": obj["message"]["role"],
            }
            content = obj["message"]["content"]
            if isinstance(content, str):
                msg["type"] = "text"
                msg["data"] = content
            elif isinstance(content, list):
                block = content[0]
                block_type = block.get("type")
                if block_type == "text":
                    msg["type"] = "text"
                    msg["data"] = block.get("text")
                elif block_type == "tool_use":
                    msg["type"] = "tool_use"
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    if tool_name == "Bash":
                        msg["data"] = {
                            "name": tool_name,
                            "input": {"command": tool_input.get("command")},
                        }
                    elif tool_name == "Read" or tool_name == "Write" or tool_name == "Edit":
                        msg["data"] = {
                            "name": tool_name,
                            "input": {"file_path": tool_input.get("file_path")},
                        }
            if "type" in msg and "data" in msg:
                messages.append(msg)
    except Exception as e:
        logger.error(e)

    return ApiResponse(code=0, data=messages)


@router.get("/{id}/comments")
async def list_app_comments(id: UUID, current_user: OptionalUserDependency, page: int = 1, size: int = 10):
    offset = (page - 1) * size
    current_user_id = None
    if current_user:
        current_user_id = str(current_user.id)
    data, total = await comment_service.list_comment(
        app_id=id, current_user_id=current_user_id, offset=offset, limit=size
    )
    return ApiResponse(code=0, data={"data": data, "total": total})


@router.get("/users/{user_id}")
async def list_app_by_user(
    user_id: UUID,
    sb: SupabaseDependency,
    current_user: OptionalUserDependency,
    page: int = 1,
    size: int = 20,
):
    if size < 5:
        size = 5
    elif size > 100:
        size = 100
    start_index = (page - 1) * size
    end_index = start_index + size - 1

    apps_result = (
        await sb.table("apps")
        .select("id,cover,name,description,category,icon")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .range(start_index, end_index)
        .execute()
    )
    count_result = await sb.table("apps").select("*", count="exact").eq("user_id", user_id).execute()

    has_more = len(apps_result.data) == size

    return ApiResponse(
        data={
            "apps": apps_result.data,
            "hasMore": has_more,
            "total": count_result.count if hasattr(count_result, "count") else 0,
        }
    )


@router.post("/{id}/like")
async def like(
    id: str,
    current_user: UserDependency,
    sb: SupabaseDependency,
):
    current_user_id = str(current_user.id)
    await app_service.like_app(app_id=id, user_id=current_user_id)
    return ApiResponse()


@router.get("/{id}/check_like")
async def check_like(
    id: str,
    current_user: OptionalUserDependency,
    sb: SupabaseDependency,
):
    if not current_user:
        return ApiResponse(data={"is_like": False})

    current_id = str(current_user.id)
    check_result = (
        await sb.table("app_likes").select("*", count="exact").eq("user_id", current_id).eq("app_id", id).execute()
    )
    is_like = len(check_result.data) > 0 if check_result.data else False
    return ApiResponse(data={"is_like": is_like})


@router.post("/{id}/bookmarks")
async def bookmark_toggle(
    id: str,
    current_user: UserDependency,
):
    current_user_id = str(current_user.id)
    await app_service.bookmark_toggle(app_id=id, user_id=current_user_id)
    return ApiResponse()


class AppInitRequest(BaseModel):
    prompt: str


VALID_CATEGORIES = {
    "productivity",
    "utility",
    "work",
    "dating",
    "health_fitness",
    "education",
    "entertainment",
    "finance",
    "kids",
    "lifestyle",
    "medical",
    "photo_video",
    "social_networking",
    "sports",
    "travel",
    "weather",
    "games",
    "misc",
}


@router.post("/{id}/init")
async def init(
    id: str,
    data: AppInitRequest,
    current_user: UserDependency,
    sb: SupabaseDependency,
):
    result = await sb.table("apps").select("id,name").eq("id", id).eq("user_id", current_user.id).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="App not found")

    app = result.data[0]
    if app.get("name") is not None:
        raise HTTPException(status_code=404, detail="App already has a name")

    prompt = data.prompt

    # Generate name
    title_response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=30,
        messages=[
            {
                "role": "user",
                "content": f"""
                    Generate an app-style project name based on this content.
                    Rules:
                    - 1-3 words only
                    - Catchy and brandable
                    - Title Case
                    - No punctuation

                    Content: "{prompt}"

                    Return only the name.
                """,
            }
        ],
    )
    name = title_response.content[0].text.strip()

    # Generate description
    description_response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"""
                    Act as a Senior Copywriter. Based on the app info provided, write a one-sentence App Store description.

                    Rules:
                    1. **Output ONLY the description.** No intro, no quotes, no explanations.
                    2. **Length:** Strictly under 80 characters (including spaces).
                    3. **Style:** Compelling, professional, and clear.

                    App Info:
                    {prompt}
                """,
            }
        ],
    )
    description = description_response.content[0].text.strip()[:255]

    # Generate category
    category_response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=30,
        messages=[
            {
                "role": "user",
                "content": f"""
                    ## Role
                    You are a professional App Store categorization expert. Your task is to select the most matching category key from a given library based on the App name or description provided by the user.

                    ## Task
                    Analyze the user's input and find the most appropriate category in the `AppCategories` list below. Output **only** the category **Key**.

                    ## AppCategories List (Key: Value)
                    * productivity: 'Productivity'
                    * utility: 'Utility'
                    * work: 'Work'
                    * dating: 'Dating'
                    * health_fitness: 'Health & Fitness'
                    * education: 'Education'
                    * entertainment: 'Entertainment'
                    * finance: 'Finance'
                    * kids: 'Kids'
                    * lifestyle: 'Lifestyle'
                    * medical: 'Medical'
                    * photo_video: 'Photo & Video'
                    * social_networking: 'Social Networking'
                    * sports: 'Sports'
                    * travel: 'Travel'
                    * weather: 'Weather'
                    * games: 'Games'
                    * misc: 'Misc'

                    ## Rules
                    1. **Output Key Only**: Return only the key name (e.g., `productivity`). Do not include explanations, punctuation, or extra text.
                    2. **Uniqueness**: Select the single most relevant category, even if the App spans multiple fields.
                    3. **Fallback Principle**: If the description is extremely vague or cannot be matched to any category above, return `utility`.
                    4. **Language Understanding**: Accurately map descriptions (even in Chinese) to the corresponding English Key.

                    ## User Input
                    "{prompt}"
                """,
            }
        ],
    )
    category = category_response.content[0].text.strip().lower()
    if category not in VALID_CATEGORIES:
        category = "utility"

    icon_url = await generate_and_upload_icon(prompt, sb)

    update_data = {"name": name, "description": description, "category": category, "updated_at": "NOW()"}
    if icon_url:
        update_data["icon"] = icon_url

    await sb.table("apps").update(update_data).eq("id", id).eq("user_id", current_user.id).execute()

    return ApiResponse(data={"name": name, "description": description, "category": category, "icon": icon_url})


class GenerateIconRequest(BaseModel):
    prompt: str


@router.post("/{id}/icon")
async def icon(
    id: str,
    data: GenerateIconRequest,
    current_user: UserDependency,
    sb: SupabaseDependency,
):
    result = await sb.table("apps").select("id,name").eq("id", id).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="App not found")

    icon_url = await generate_and_upload_icon(data.prompt, sb)

    return ApiResponse(data={"url": icon_url})


@router.get("/{id}/stage")
async def get_app_stage(id: UUID):
    stage = await sandbox_service.get_app_stage(id)
    return ApiResponse(code=0, data=stage)


@router.get("/{id}/events")
async def list_chat_events(current_user: UserDependency, id: UUID):
    sbx = await sandbox_service.get_by_app_id(id)
    if not sbx:
        return ApiResponse(code=0, data=[])

    events: list[ChatEvent] = []

    try:
        content = sbx.files.read(f"/home/user/.claude/projects/-home-user-app/{str(id)}.jsonl")
        lines = content.strip().splitlines()
        for line in lines:
            obj = json.loads(line)
            event = make_chat_event(obj)
            if not event:
                continue

            event["id"] = obj["uuid"]
            event["timestamp"] = obj["timestamp"]
            event["role"] = obj["message"]["role"]

            if event["event"] == "progress":
                while (
                    len(events) > 1
                    and events[-1]["event"] != "plan"
                    and not (events[-1]["event"] == "message" and events[-1]["role"] == "user")
                ):
                    events.pop()
            elif event["event"] == "plan":
                while len(events) > 1 and not (events[-1]["event"] == "message" and events[-1]["role"] == "user"):
                    events.pop()

            events.append(event)

            if event["event"] == "error":
                break

        if events[-1] and events[-1]["event"] == "message" and "localhost:3000" in events[-1]["data"]:
            content = json.dumps({"stage": AppStage.BUILT}, indent=2)
            sbx.files.write(ABILITY_CONFIG_PATH, content)
    except Exception as e:
        logger.error(e)

    return ApiResponse(code=0, data=events)
