import json
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from app.api.deps import UserDependency
from app.services.sandbox_service import sandbox_service
from app.utils.chat import chat_event_stream


router = APIRouter(tags=["chat"])


class ChatCompletionRequest(BaseModel):
    app_id: UUID
    prompt: str
    mode: Optional[Literal["plan"]] = None


@router.post("/completion")
async def chat_completion(current_user: UserDependency, data: ChatCompletionRequest):
    prompt = data.prompt
    app_id = data.app_id
    mode = data.mode
    sbx = await sandbox_service.get_by_app_id(app_id)
    if not sbx:
        sbx = await sandbox_service.create(app_id)

    cost_exceeded = False
    try:
        result = sbx.commands.run(cmd="npx ccusage@latest --json", timeout=0)
        obj = json.loads(result.stdout)
        if 7 - obj["totals"]["totalCost"] <= 0:
            cost_exceeded = True
    except Exception as e:
        logger.error(e)
    if cost_exceeded:
        raise HTTPException(status_code=402, detail="Usage limit exceeded for this app")

    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    handle = await sandbox_service.chat(app_id=app_id, prompt=prompt, mode=mode)

    return StreamingResponse(
        chat_event_stream(sbx=sbx, handle=handle),
        headers=headers,
    )
