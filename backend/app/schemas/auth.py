"""
认证相关的数据模式
兼容Passport Web接口格式
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    password: str
    email: Optional[EmailStr] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """用户信息更新请求"""
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """密码修改请求"""
    current_password: str
    new_password: str


class PasswordReset(BaseModel):
    """密码重置请求"""
    username: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应信息"""
    id: int
    username: str
    provider: str
    email: Optional[str] = None
    displayName: Optional[str] = None


class AuthResponse(BaseModel):
    """认证响应"""
    success: bool
    message: str
    user: UserResponse
    access_token: Optional[str] = None


class UserInfo(BaseModel):
    """用户详细信息"""
    id: int
    username: str
    provider: str
    email: Optional[str] = None
    displayName: Optional[str] = None
    avatarUrl: Optional[str] = None
    isActive: bool = True
    isVerified: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class TokenRequest(BaseModel):
    """Token请求"""
    accessToken: str


class TokenInfo(BaseModel):
    """Token信息"""
    type: str
    issuedAt: str
    expiresAt: str


class UserInfoResponse(BaseModel):
    """用户信息响应（通过Token获取）"""
    success: bool
    user: UserInfo
    tokenInfo: TokenInfo


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool
    message: str
    code: Optional[str] = None 