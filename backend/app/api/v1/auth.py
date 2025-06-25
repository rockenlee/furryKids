"""
用户认证相关API路由
兼容Passport Web认证系统接口
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, UserResponse, AuthResponse, 
    UserInfo, TokenRequest, ErrorResponse
)

router = APIRouter(tags=["认证"])
security = HTTPBearer(auto_error=False)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


def verify_token(token: str) -> Optional[dict]:
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


@router.get("/health")
async def auth_health():
    """认证服务健康检查"""
    return {"status": "ok", "service": "auth"}


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    兼容Passport Web接口格式
    """
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={"success": False, "message": "用户名已存在"}
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        provider="local"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(new_user.id), "username": new_user.username}
    )
    
    return AuthResponse(
        success=True,
        message="注册成功",
        user=UserResponse(
            id=new_user.id,
            username=new_user.username,
            provider=new_user.provider
        ),
        access_token=access_token
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    兼容Passport Web接口格式，同时支持JWT
    """
    # 验证用户
    user = await get_user_by_username(db, user_data.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "用户名不存在"}
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "密码错误"}
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    # 设置Cookie（兼容Session模式）
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=60 * 60 * 24,  # 24小时
        httponly=True,
        secure=False,  # 开发环境设为False
        samesite="lax"
    )
    
    return AuthResponse(
        success=True,
        message="登录成功",
        user=UserResponse(
            id=user.id,
            username=user.username,
            provider=user.provider
        ),
        access_token=access_token
    )


@router.post("/logout")
async def logout(response: Response):
    """
    用户登出
    兼容Passport Web接口格式
    """
    # 清除Cookie
    response.delete_cookie(key="access_token")
    
    return {"success": True, "message": "登出成功"}


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(security)
) -> Optional[User]:
    """
    获取当前用户（支持Cookie和Bearer Token两种方式）
    """
    access_token = None
    
    # 优先从Authorization header获取token
    if token and token.credentials:
        access_token = token.credentials
    # 其次从Cookie获取
    elif "access_token" in request.cookies:
        access_token = request.cookies["access_token"]
    
    if not access_token:
        return None
    
    # 验证token
    payload = verify_token(access_token)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # 获取用户信息
    user = await get_user_by_id(db, int(user_id))
    return user


@router.get("/user")
async def get_user_info(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    兼容Passport Web接口格式
    """
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False, 
                "message": "Not authenticated",
                "code": "NOT_AUTHENTICATED"
            }
        )
    
    # 判断认证方式
    auth_type = "session" if "access_token" in request.cookies else "token"
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "provider": current_user.provider,
            "email": current_user.email,
            "displayName": current_user.display_name
        },
        "authType": auth_type
    }


@router.post("/user/info")
async def get_user_by_token(
    token_request: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    根据AccessToken获取用户信息
    兼容Passport Web接口格式
    """
    if not token_request.accessToken:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "AccessToken是必需的",
                "code": "ACCESS_TOKEN_MISSING"
            }
        )
    
    # 验证token
    payload = verify_token(token_request.accessToken)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "无效的令牌",
                "code": "INVALID_TOKEN"
            }
        )
    
    # 检查token类型
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "无效的令牌类型",
                "code": "INVALID_TOKEN_TYPE"
            }
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "令牌中缺少用户信息",
                "code": "INVALID_TOKEN"
            }
        )
    
    # 获取用户信息
    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "用户不存在",
                "code": "USER_NOT_FOUND"
            }
        )
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "provider": user.provider,
            "email": user.email,
            "displayName": user.display_name
        },
        "tokenInfo": {
            "type": "access",
            "issuedAt": datetime.fromtimestamp(payload.get("iat", 0)).isoformat(),
            "expiresAt": datetime.fromtimestamp(payload.get("exp", 0)).isoformat()
        }
    } 