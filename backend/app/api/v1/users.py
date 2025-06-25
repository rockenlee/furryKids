"""
用户管理相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse, UserInfo, UserUpdate, PasswordChange, PasswordReset
from app.api.v1.auth import get_current_user, verify_password, get_password_hash
from app.middleware.auth import require_admin

router = APIRouter(tags=["用户"])


@router.get("/health")
async def users_health():
    """用户服务健康检查"""
    return {"status": "ok", "service": "users"}


@router.get("/profile", response_model=UserInfo)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户详细信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        displayName=current_user.display_name,
        avatarUrl=current_user.avatar_url,
        isActive=current_user.is_active,
        isVerified=current_user.is_verified,
        provider=current_user.provider,
        createdAt=current_user.created_at,
        updatedAt=current_user.updated_at
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    # 允许更新的字段
    update_fields = {}
    if update_data.display_name is not None:
        update_fields["display_name"] = update_data.display_name
    if update_data.email is not None:
        update_fields["email"] = str(update_data.email)
    if update_data.avatar_url is not None:
        update_fields["avatar_url"] = update_data.avatar_url
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有有效的更新字段"
        )
    
    # 如果更新邮箱，检查是否已存在
    if "email" in update_fields:
        result = await db.execute(
            select(User).where(User.email == update_fields["email"], User.id != current_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 更新用户信息
    await db.execute(
        update(User).where(User.id == current_user.id).values(**update_fields)
    )
    await db.commit()
    
    # 获取更新后的用户信息
    result = await db.execute(select(User).where(User.id == current_user.id))
    updated_user = result.scalar_one()
    
    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        provider=updated_user.provider,
        email=updated_user.email,
        displayName=updated_user.display_name
    )


@router.delete("/profile")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除用户账户"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    # 软删除：将用户标记为非活跃
    await db.execute(
        update(User).where(User.id == current_user.id).values(is_active=False)
    )
    await db.commit()
    
    return {"success": True, "message": "账户已删除"}


@router.get("/list", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（管理员功能）"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    # 简单的权限检查，后续可以扩展为角色权限系统
    # 这里暂时允许所有登录用户查看用户列表
    
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            provider=user.provider,
            email=user.email,
            displayName=user.display_name
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取用户信息"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        provider=user.provider,
        email=user.email,
        displayName=user.display_name
    )


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或token无效"
        )
    
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 检查新密码长度
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少6位"
        )
    
    # 更新密码
    new_hashed_password = get_password_hash(password_data.new_password)
    await db.execute(
        update(User).where(User.id == current_user.id).values(hashed_password=new_hashed_password)
    )
    await db.commit()
    
    return {"success": True, "message": "密码修改成功"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """重置密码（简化版本）"""
    # 查找用户
    query = select(User).where(User.username == reset_data.username)
    if reset_data.email:
        query = query.where(User.email == reset_data.email)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        # 即使用户不存在也返回成功，防止用户名枚举攻击
        return {"success": True, "message": "如果用户存在，重置链接已发送到邮箱"}
    
    # 生成临时密码（实际项目中应该发送邮件重置链接）
    import random
    import string
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # 更新为临时密码
    new_hashed_password = get_password_hash(temp_password)
    await db.execute(
        update(User).where(User.id == user.id).values(hashed_password=new_hashed_password)
    )
    await db.commit()
    
    # 在实际项目中，这里应该发送邮件而不是直接返回密码
    return {
        "success": True, 
        "message": "密码重置成功",
        "temp_password": temp_password,  # 仅用于演示，实际项目中不应返回
        "note": "请使用临时密码登录后立即修改密码"
    } 