import os

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
import httpx
from loguru import logger
from pydantic import BaseModel, EmailStr

from app.api.deps import SupabaseDependency
from app.models.common import ApiResponse


router = APIRouter(tags=["auth"])
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "http://localhost:5173")


class MagiclinkRequest(BaseModel):
    email: EmailStr


@router.post("/magiclink")
async def sign_in_with_magiclink(data: MagiclinkRequest, sb: SupabaseDependency):
    await sb.auth.sign_in_with_otp({
        "email": data.email,
        "options": {
            "should_create_user": True,
            "email_redirect_to": f"{FRONTEND_HOST}/auth/callback",
        },
    })
    return ApiResponse()

class GoogleLoginRequest(BaseModel):
    code: str

@router.post("/google")
async def sign_in_with_google(data: GoogleLoginRequest, sb: SupabaseDependency):
    """
    Google Login
    """

    form_data = {
        "code": data.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": FRONTEND_HOST,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    if token_response.status_code != 200:
        return ApiResponse(code=401, message="Auth Fail")

    id_token = token_response.json().get("id_token")

    response = await sb.auth.sign_in_with_id_token(
        {
            "provider": "google",
            "token": id_token,
        }
    )
    return ApiResponse(data={
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    })


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, sb: SupabaseDependency):
    try:
        res = await sb.auth.refresh_session(request.refresh_token)

        return ApiResponse(data={
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "expires_in": res.session.expires_in,
        })

    except Exception as e:
        logger.error(e)
        return ApiResponse(code=1)


@router.get("/callback")
async def auth_callback(req: Request, sb: SupabaseDependency):
    query_params = dict(req.query_params)
    token_hash = query_params.get("token_hash")
    next = query_params.get("next")
    try:
        res = await sb.auth.verify_otp({
            "token_hash": token_hash,
            "type": 'email',
        })
        response = RedirectResponse(url=next or FRONTEND_HOST)
        response.set_cookie(key="token", value=res.session.access_token, httponly=True)
        return response
    except Exception as e:
        logger.error(e)
        return RedirectResponse(url=f"{FRONTEND_HOST}/500")
