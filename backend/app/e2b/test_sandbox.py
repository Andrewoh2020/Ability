import json
from random import sample
import sys
import uuid

from anyio import run, sleep
from asyncio import CancelledError
from loguru import logger

from app.services.sandbox_service import sandbox_service
from app.utils.chat import chat_event_stream


prompt = sys.argv[1]

app_id = uuid.uuid4()
logger.info(f"app_id: {str(app_id)}")


async def main():
    sbx = await sandbox_service.create(app_id)
    logger.info("sandbox created")

    async def cleanup():
        logger.info("killing sandbox")

        if await sandbox_service.kill_by_app_id(app_id):
            logger.info("sandbox killed")
        else:
            logger.error("failed to kill sandbox: {}", sbx.sandbox_id)

    plan = None
    logger.info("claude running - plan")
    handle = await sandbox_service.chat(app_id=app_id, prompt=prompt, mode="plan")
    for x in chat_event_stream(sbx=sbx, handle=handle):
        event = json.loads(x)
        if event["event"] == "error":
            logger.error(x)
            await cleanup()
            sys.exit(1)
        logger.info(x)
        if event["event"] == "plan":
            plan = event["data"]

    logger.info("claude running - suggest more features")
    suggest_prompt = "suggest more features"
    handle = await sandbox_service.chat(app_id=app_id, prompt=suggest_prompt, mode="plan")
    for x in chat_event_stream(sbx=sbx, handle=handle):
        event = json.loads(x)
        if event["event"] == "error":
            logger.error(x)
            await cleanup()
            sys.exit(1)
        logger.info(x)
        if event["event"] == "plan":
            plan = event["data"]

    if plan and "features" in plan:
        features = ", ".join([feature["label"] for feature in sample(plan["features"], min(3, len(plan["features"])))])
        plan_prompt = f"selected features: {features}"
        logger.info("updated plan: {}", plan_prompt)
        logger.info("claude running - coding")
        handle = await sandbox_service.chat(app_id=app_id, prompt=plan_prompt)
        for x in chat_event_stream(sbx=sbx, handle=handle):
            event = json.loads(x)
            if event["event"] == "error":
                logger.error(x)
                await cleanup()
                sys.exit(1)
            logger.info(x)

    public_url = await sandbox_service.preview(app_id=app_id)
    logger.info("sandbox preview url: {}", public_url)

    try:
        await sleep(1800)
    except CancelledError:
        await cleanup()
        sys.exit(0)

    await cleanup()


run(main)

# python -m app.e2b.test_sandbox.py 'prompt'
