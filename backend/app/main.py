from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from app.api.router import api_router
from app.core.config import settings
# import sentry_sdk


# if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
#     sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI()


@app.exception_handler(Exception)
async def general_exception_handler(_, exc: Exception):
    """
    Handle all uncaught exceptions and return a 500 Internal Server Error
    """
    logger.error(exc)

    res = JSONResponse(
        status_code=500,
        content={
            "code": 1,
            "message": "Internal Server Error",
        },
    )
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Credentials"] = "true"
    return res


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/healthz")
async def health():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")

# gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0 --timeout 600 app.main:app
