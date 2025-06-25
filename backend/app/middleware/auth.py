"""
认证中间件
处理JWT token验证和用户权限管理
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选，不强制要求认证）
    用于某些端点可以匿名访问但登录后有额外功能的场景
    """
    if not credentials:
        return None
    
    try:
        # 解码JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
            
    except JWTError:
        return None
    
    # 从数据库获取用户信息
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        return None
        
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前用户（必须认证）
    用于需要强制登录的端点
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（必须是活跃状态）
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前已验证用户（必须是已验证状态）
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户未验证，请先验证邮箱"
        )
    return current_user


class RoleChecker:
    """
    角色检查器
    用于检查用户是否具有特定角色或权限
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        # 目前用户模型中没有角色字段，这里先做一个简单的实现
        # 后续可以扩展为更复杂的权限系统
        
        # 假设用户名为 "admin" 的用户是管理员
        user_roles = []
        if current_user.username == "admin":
            user_roles.append("admin")
        else:
            user_roles.append("user")
        
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join(self.allowed_roles)}"
            )
        
        return current_user


# 预定义的角色检查器
require_admin = RoleChecker(["admin"])
require_user = RoleChecker(["user", "admin"])


def create_access_token(data: dict) -> str:
    """
    创建访问令牌
    """
    from datetime import datetime, timedelta
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证令牌并返回载荷
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None 