from fastapi import APIRouter, Depends, Request, status
from controllers.auth_controller import AuthController
from models.user_models import UserCreate, UserLogin, ForgotPassword, ResetPassword, UserUpdate
from pydantic import BaseModel, EmailStr

router = APIRouter()

class CheckUserRequest(BaseModel):
    email: EmailStr

@router.post("/check-user")
async def check_user(check_user_data: CheckUserRequest):
    """Check if a user exists with the given email address"""
    return await AuthController.check_user_exists(check_user_data.email)

@router.post("/register")
async def register_user(user_data: UserCreate, request: Request):
    return await AuthController.register_user(user_data, request)

@router.post("/login")
async def login(user_credentials: UserLogin, request: Request):
    return await AuthController.login(user_credentials, request)

@router.post("/forgot-password")
async def forgot_password(forgot_password_data: ForgotPassword):
    return await AuthController.forgot_password(forgot_password_data)

@router.post("/reset-password")
async def reset_password(reset_password_data: ResetPassword):
    return await AuthController.reset_password(reset_password_data)

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(AuthController.get_current_user_info)):
    return current_user

@router.put("/profile")
async def update_profile(user_update: UserUpdate, current_user: dict = Depends(AuthController.update_profile)):
    return current_user
