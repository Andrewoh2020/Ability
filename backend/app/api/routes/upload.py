from fastapi import APIRouter, UploadFile, File
import uuid
import os
from io import BytesIO
from app.utils.common import utc_now
from PIL import Image
from app.core.config import settings
from app.models.common import ApiResponse
from app.api.deps import SupabaseDependency

router = APIRouter(tags=["upload"])

@router.post("/image")
async def image(
    sb: SupabaseDependency,
    file: UploadFile = File(...),
):
    if not file.content_type.startswith('image/'):
        return ApiResponse(code=400, message="Please upload an image file")

    file_bytes = await file.read()
    if len(file_bytes) > 2 * 1024 * 1024:
        return ApiResponse(code=400, message="Image size should be less than 2MB")

    now = utc_now()
    date_dir = now.strftime("%Y-%m-%d")

    # Compress and convert to WEBP
    img = Image.open(BytesIO(file_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((512, 512), Image.Resampling.LANCZOS)

    output_buffer = BytesIO()
    img.save(output_buffer, format="WEBP", quality=85)
    compressed_bytes = output_buffer.getvalue()

    filename = f"{uuid.uuid4().hex}.webp"

    upload_response = await sb.storage.from_('static').upload(
        file=compressed_bytes,
        path=f"images/{date_dir}/{filename}",
        file_options={"content-type": "image/webp"},
    )

    if not upload_response.path:
        return ApiResponse(code=1, message="failed to upload image")

    public_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/static/{upload_response.path}"

    return ApiResponse(data={
        "url": public_url,
    })
