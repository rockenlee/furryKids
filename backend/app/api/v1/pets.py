"""
宠物管理API路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.pet import PetMood
from app.schemas.pet import (
    PetCreate, PetUpdate, PetResponse, PetDetailResponse, 
    PetListResponse, PetStats, PetPhotoCreate, PetPhotoResponse,
    PetMoodEnum
)
from app.services.pet_service import PetService

router = APIRouter(tags=["宠物管理"])


@router.post("/", response_model=PetDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_pet(
    pet_data: PetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新宠物
    
    - **name**: 宠物名称（必填）
    - **breed**: 品种（必填）
    - **age**: 年龄（月，可选）
    - **gender**: 性别（male/female/unknown）
    - **color**: 毛色（可选）
    - **size**: 体型（small/medium/large/giant）
    - **weight**: 体重（kg，可选）
    - **personality**: 性格描述（可选）
    - **personality_tags**: 性格标签列表（可选）
    - **current_mood**: 当前心情（可选，默认happy）
    - **response_style**: 回复风格（可选，默认friendly）
    """
    return await PetService.create_pet(db, pet_data, current_user.id)


@router.get("/", response_model=PetListResponse)
async def get_my_pets(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（名称或品种）"),
    mood: Optional[PetMoodEnum] = Query(None, description="心情筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的宠物列表
    
    支持分页、搜索和心情筛选
    """
    mood_filter = PetMood(mood) if mood else None
    return await PetService.get_pets_by_owner(
        db, current_user.id, page, size, search, mood_filter
    )


@router.get("/stats", response_model=PetStats)
async def get_pet_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取宠物统计信息
    
    包括总数、活跃数、互动次数、平均等级、心情分布等
    """
    return await PetService.get_pet_stats(db, current_user.id)


@router.get("/{pet_id}", response_model=PetDetailResponse)
async def get_pet_detail(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取宠物详细信息
    
    包括基础信息、照片、AI配置等
    """
    return await PetService.get_pet_detail(db, pet_id, current_user.id)


@router.put("/{pet_id}", response_model=PetDetailResponse)
async def update_pet(
    pet_id: int,
    pet_data: PetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新宠物信息
    
    可以更新任意字段，未提供的字段保持不变
    """
    return await PetService.update_pet(db, pet_id, current_user.id, pet_data)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除宠物（软删除）
    
    宠物不会被物理删除，只是标记为不活跃
    """
    await PetService.delete_pet(db, pet_id, current_user.id)


@router.patch("/{pet_id}/mood", response_model=PetResponse)
async def update_pet_mood(
    pet_id: int,
    mood: PetMoodEnum,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新宠物心情
    
    - **mood**: 新的心情状态
    - **description**: 心情描述（可选）
    """
    return await PetService.update_pet_mood(
        db, pet_id, current_user.id, PetMood(mood), description
    )


@router.post("/{pet_id}/interaction", response_model=PetResponse)
async def add_pet_interaction(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    增加宠物互动次数
    
    每次互动会增加经验值，达到一定经验值会升级
    """
    return await PetService.add_pet_interaction(db, pet_id, current_user.id)


@router.post("/{pet_id}/photos", response_model=PetPhotoResponse, status_code=status.HTTP_201_CREATED)
async def add_pet_photo(
    pet_id: int,
    photo_data: PetPhotoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    添加宠物照片
    
    - **url**: 照片URL（必填）
    - **thumbnail_url**: 缩略图URL（可选）
    - **description**: 照片描述（可选）
    - **is_avatar**: 是否设为头像（可选，默认false）
    
    如果设为头像，会自动取消其他照片的头像状态
    """
    return await PetService.add_pet_photo(db, pet_id, current_user.id, photo_data)


@router.get("/{pet_id}/ai-prompt", response_model=dict)
async def get_pet_ai_prompt(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取宠物的AI对话提示词
    
    用于AI聊天时的个性化配置
    """
    pet_detail = await PetService.get_pet_detail(db, pet_id, current_user.id)
    
    # 构建AI提示词
    mood_text = {
        "happy": "心情很好，很开心",
        "excited": "非常兴奋，充满活力",
        "calm": "很平静，很放松",
        "sleepy": "有点困倦，想睡觉",
        "playful": "想要玩耍，很活跃",
        "hungry": "有点饿了，想吃东西",
        "sad": "有点伤心，需要安慰",
        "anxious": "有点焦虑，需要关爱"
    }.get(pet_detail.current_mood.value, "心情不错")
    
    personality_desc = pet_detail.personality or "友善可爱"
    
    default_prompt = f"""你是一只名叫{pet_detail.name}的{pet_detail.breed}，{pet_detail.age_display}大。
你的性格是{personality_desc}，目前{mood_text}。
请用宠物的视角和语气回复主人，表现出你的个性特征。
回复要温馨、可爱，符合宠物的特点。"""
    
    return {
        "pet_id": pet_id,
        "pet_name": pet_detail.name,
        "ai_prompt": pet_detail.ai_personality_prompt or default_prompt,
        "response_style": pet_detail.response_style,
        "current_mood": pet_detail.current_mood.value,
        "personality_tags": pet_detail.personality_tags
    }

# 文件上传相关API
@router.post("/{pet_id}/upload-photo", response_model=PetPhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_pet_photo(
    pet_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    is_avatar: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传宠物照片
    
    - **file**: 图片文件（必填，支持jpg, jpeg, png, gif）
    - **description**: 照片描述（可选）
    - **is_avatar**: 是否设为头像（可选，默认false）
    
    文件会被保存到uploads/pets/目录下
    """
    return await PetService.upload_pet_photo(db, pet_id, current_user.id, file, description, is_avatar)


@router.get("/{pet_id}/photos", response_model=List[PetPhotoResponse])
async def get_pet_photos(
    pet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取宠物照片列表
    """
    return await PetService.get_pet_photos(db, pet_id, current_user.id)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pet_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除宠物照片
    """
    await PetService.delete_pet_photo(db, photo_id, current_user.id) 