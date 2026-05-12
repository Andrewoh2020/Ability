from app.models.user import UserSignUp  # Updated import
from fastapi import HTTPException, status
from typing import Dict, Any
from app.core.db import get_supabase_client
from app.utils.common import SingletonMeta


class AuthService(metaclass=SingletonMeta):
    async def sign_up(self, user_data: UserSignUp) -> Dict[str, Any]:
        """Register a new user"""
        try:
            supabase = await get_supabase_client()
            response = await supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name
                    }
                }
            })

            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )

            return {
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user"""
        try:
            supabase = await get_supabase_client()
            response = await supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

            return {
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

    async def get_user_from_token(self, token: str) -> Dict[str, Any]:
        """Get user from JWT token"""
        try:
            supabase = await get_supabase_client()
            response = await supabase.auth.get_user(token)
            if response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            return response.user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

auth_service = AuthService()
