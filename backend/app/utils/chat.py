import json
from json.decoder import JSONDecodeError
import re
from typing import Any, Generator, Literal, Optional, TypedDict

from e2b import CommandHandle, Sandbox
from loguru import logger

from app.models.app import AppStage


JSON_BLOCK_PATTERN = re.compile(r"^```json.*?```$", re.DOTALL)

ABILITY_CONFIG_PATH = "/home/user/.ability.json"


class ChatEvent(TypedDict):
    id: Optional[str]
    timestamp: Optional[str]
    role: Optional[Literal["user", "assistant"]]
    event: Literal["end", "error", "message", "plan", "progress", "tool_use"]
    data: Any


def is_json_block(text: str) -> bool:
    return JSON_BLOCK_PATTERN.match(text) is not None


def make_chat_event(obj: dict[Any, Any]) -> Optional[ChatEvent]:
    if obj.get("isVisibleInTranscriptOnly") or obj["type"] == "system" or "uuid" not in obj:
        return None

    if obj.get("type") == "result":
        return {
            "event": "end",
            "data": {
                "duration_ms": obj.get("duration_ms"),
                "duration_api_ms": obj.get("duration_api_ms"),
                "is_error": obj.get("is_error"),
                "num_turns": obj.get("num_turns"),
                "total_cost_usd": obj.get("total_cost_usd"),
                "usage": obj.get("usage"),
            },
        }

    content = obj.get("message", {}).get("content")
    if isinstance(content, str):
        # user message
        return {"event": "message", "data": content}
    elif isinstance(content, list):
        # assistant message
        for block in obj["message"]["content"]:
            if block.get("type") == "text":
                text = block.get("text")
                if text and is_json_block(text):
                    try:
                        data = json.loads(text.removeprefix("```json").removesuffix("```"))
                        return {"event": "plan", "data": data}
                    except Exception as e:
                        logger.error(e)
                        return {"event": "error", "data": "Unexpected planning error"}

                return {"event": "message", "data": text}
            elif block.get("type") == "tool_use":
                tool_name = block.get("name")
                tool_input = block.get("input")

                if tool_name == "TodoWrite":
                    todos = tool_input.get("todos")
                    if todos and len(todos) > 0:
                        return {
                            "event": "progress",
                            "data": tool_input.get("todos"),
                        }
                return {"event": "tool_use", "data": {"name": tool_name}}

    return None


def chat_event_stream(sbx: Sandbox, handle: CommandHandle) -> Generator[str, None, None]:
    try:
        last_chunk: str = ""
        has_plan = False
        has_progress = False
        updated = False
        for stdout, stderr, pty in handle:
            if stdout:
                chunk = last_chunk + stdout
                try:
                    obj = json.loads(chunk)
                    last_chunk = ""
                    event = make_chat_event(obj)
                    if event:
                        yield f"{json.dumps(event)}\n"
                        try:
                            match event["event"]:
                                case "plan":
                                    has_plan = True
                                    data = json.dumps({"stage": AppStage.PLANNING}, indent=2)
                                    sbx.files.write(ABILITY_CONFIG_PATH, data)
                                case "progress":
                                    has_progress = True
                                    stage = AppStage.BUILDING
                                    if all(x["status"] == "completed" for x in event["data"]):
                                        stage = AppStage.BUILT
                                    data = json.dumps({"stage": stage}, indent=2)
                                    sbx.files.write(ABILITY_CONFIG_PATH, data)
                                case "tool_use":
                                    if event["data"]["name"] == "Edit" or event["data"]["name"] == "Write":
                                        updated = True
                                        stage = AppStage.BUILDING
                                        data = json.dumps({"stage": stage}, indent=2)
                                        sbx.files.write(ABILITY_CONFIG_PATH, data)
                                case "error":
                                    handle.kill()
                                    break
                                case "end":
                                    if not has_plan and not has_progress and updated:
                                        data = json.dumps({"stage": AppStage.BUILT}, indent=2)
                                        sbx.files.write(ABILITY_CONFIG_PATH, data)
                                    handle.kill()
                                    break
                        except Exception as e:
                            logger.error(e)
                except JSONDecodeError:
                    last_chunk = chunk
            if stderr:
                logger.debug("stderr: {}", stderr)
            if pty:
                logger.debug("pty: {}", pty)
    except Exception as e:
        logger.error(e)
        event = json.dumps({"event": "error", "data": "Internal Server Error"})
        yield event
