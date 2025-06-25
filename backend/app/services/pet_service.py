"""
宠物服务层
处理宠物相关的业务逻辑
"""

import os
import uuid
import aiofiles
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, UploadFile
import json

from app.models.pet import Pet, PetPhoto, PetMood
from app.models.user import User
from app.schemas.pet import (
    PetCreate, PetUpdate, PetResponse, PetDetailResponse, 
    PetListResponse, PetStats, PetPhotoCreate, PetPhotoResponse
)


class PetService:
    """宠物服务类"""

    @staticmethod
    async def create_pet(
        db: AsyncSession, 
        pet_data: PetCreate, 
        owner_id: int
    ) -> PetDetailResponse:
        """
        创建新宠物
        """
        # 检查用户是否存在
        user_result = await db.execute(select(User).where(User.id == owner_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 创建宠物实例
        pet = Pet(
            name=pet_data.name,
            breed=pet_data.breed,
            age=pet_data.age,
            gender=pet_data.gender,
            color=pet_data.color,
            size=pet_data.size,
            weight=pet_data.weight,
            personality=pet_data.personality,
            current_mood=pet_data.current_mood,
            mood_description=pet_data.mood_description,
            response_style=pet_data.response_style or "friendly",
            owner_id=owner_id
        )

        # 设置性格标签
        if pet_data.personality_tags:
            pet.personality_tags = pet_data.personality_tags

        db.add(pet)
        await db.commit()
        await db.refresh(pet)

        return await PetService.get_pet_detail(db, pet.id, owner_id)

    @staticmethod
    async def get_pet_detail(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int
    ) -> PetDetailResponse:
        """
        获取宠物详细信息
        """
        result = await db.execute(
            select(Pet)
            .options(selectinload(Pet.photos))
            .where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        return PetDetailResponse.from_orm(pet)

    @staticmethod
    async def get_pets_by_owner(
        db: AsyncSession, 
        owner_id: int,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        mood_filter: Optional[PetMood] = None
    ) -> PetListResponse:
        """
        获取用户的宠物列表
        """
        # 构建查询条件
        conditions = [Pet.owner_id == owner_id, Pet.is_active == True]
        
        if search:
            search_pattern = f"%{search}%"
            conditions.append(
                or_(
                    Pet.name.ilike(search_pattern),
                    Pet.breed.ilike(search_pattern)
                )
            )
        
        if mood_filter:
            conditions.append(Pet.current_mood == mood_filter)

        # 计算总数
        count_result = await db.execute(
            select(func.count(Pet.id)).where(and_(*conditions))
        )
        total = count_result.scalar()

        # 获取分页数据
        offset = (page - 1) * size
        result = await db.execute(
            select(Pet)
            .where(and_(*conditions))
            .order_by(Pet.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        pets = result.scalars().all()

        # 转换为响应格式
        pet_responses = [PetResponse.from_orm(pet) for pet in pets]

        return PetListResponse(
            pets=pet_responses,
            total=total,
            page=page,
            size=size,
            has_next=total > page * size
        )

    @staticmethod
    async def update_pet(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int, 
        pet_data: PetUpdate
    ) -> PetDetailResponse:
        """
        更新宠物信息
        """
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        # 更新字段
        update_data = pet_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "personality_tags":
                pet.personality_tags = value
            else:
                setattr(pet, field, value)

        await db.commit()
        await db.refresh(pet)

        return await PetService.get_pet_detail(db, pet.id, owner_id)

    @staticmethod
    async def delete_pet(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int
    ) -> bool:
        """
        删除宠物（软删除）
        """
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        pet.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def update_pet_mood(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int, 
        mood: PetMood,
        description: Optional[str] = None
    ) -> PetResponse:
        """
        更新宠物心情
        """
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        pet.current_mood = mood
        if description:
            pet.mood_description = description

        await db.commit()
        await db.refresh(pet)

        return PetResponse.from_orm(pet)

    @staticmethod
    async def add_pet_interaction(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int
    ) -> PetResponse:
        """
        增加宠物互动次数
        """
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        pet.add_interaction()
        await db.commit()
        await db.refresh(pet)

        return PetResponse.from_orm(pet)

    @staticmethod
    async def add_pet_photo(
        db: AsyncSession, 
        pet_id: int, 
        owner_id: int, 
        photo_data: PetPhotoCreate
    ) -> PetPhotoResponse:
        """
        添加宠物照片
        """
        # 验证宠物存在且属于当前用户
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        # 如果是设置为头像，先取消其他头像
        if photo_data.is_avatar:
            await db.execute(
                select(PetPhoto)
                .where(and_(PetPhoto.pet_id == pet_id, PetPhoto.is_avatar == True))
            )
            # 更新其他照片的头像状态
            existing_photos_result = await db.execute(
                select(PetPhoto).where(and_(PetPhoto.pet_id == pet_id, PetPhoto.is_avatar == True))
            )
            for existing_photo in existing_photos_result.scalars().all():
                existing_photo.is_avatar = False

        # 创建新照片
        photo = PetPhoto(
            pet_id=pet_id,
            url=photo_data.url,
            thumbnail_url=photo_data.thumbnail_url,
            description=photo_data.description,
            is_avatar=photo_data.is_avatar
        )

        db.add(photo)
        await db.commit()
        await db.refresh(photo)

        # 如果是头像，更新宠物的头像URL
        if photo_data.is_avatar:
            pet.avatar_url = photo_data.url
            await db.commit()

        return PetPhotoResponse.from_orm(photo)

    @staticmethod
    async def get_pet_stats(
        db: AsyncSession, 
        owner_id: int
    ) -> PetStats:
        """
        获取用户宠物统计信息
        """
        # 总宠物数
        total_result = await db.execute(
            select(func.count(Pet.id)).where(Pet.owner_id == owner_id)
        )
        total_pets = total_result.scalar()

        # 活跃宠物数
        active_result = await db.execute(
            select(func.count(Pet.id)).where(and_(Pet.owner_id == owner_id, Pet.is_active == True))
        )
        active_pets = active_result.scalar()

        # 总互动次数
        interactions_result = await db.execute(
            select(func.sum(Pet.interaction_count)).where(and_(Pet.owner_id == owner_id, Pet.is_active == True))
        )
        total_interactions = interactions_result.scalar() or 0

        # 平均等级
        level_result = await db.execute(
            select(func.avg(Pet.level)).where(and_(Pet.owner_id == owner_id, Pet.is_active == True))
        )
        average_level = float(level_result.scalar() or 0)

        # 心情分布
        mood_result = await db.execute(
            select(Pet.current_mood, func.count(Pet.id))
            .where(and_(Pet.owner_id == owner_id, Pet.is_active == True))
            .group_by(Pet.current_mood)
        )
        mood_distribution = {mood.value: count for mood, count in mood_result.all()}

        return PetStats(
            total_pets=total_pets,
            active_pets=active_pets,
            total_interactions=total_interactions,
            average_level=average_level,
            mood_distribution=mood_distribution
        )

    @staticmethod
    async def upload_pet_photo(
        db: AsyncSession,
        pet_id: int,
        owner_id: int,
        file: UploadFile,
        description: Optional[str] = None,
        is_avatar: bool = False
    ) -> PetPhotoResponse:
        """
        上传宠物照片
        """
        # 验证宠物存在且属于当前用户
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        # 验证文件类型
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型，请上传jpg、png或gif格式的图片"
            )

        # 验证文件大小（5MB限制）
        max_size = 5 * 1024 * 1024  # 5MB
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小不能超过5MB"
            )

        # 创建上传目录
        upload_dir = "uploads/pets"
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)

        # 构建访问URL
        file_url = f"/uploads/pets/{unique_filename}"

        # 如果是设置为头像，先取消其他头像
        if is_avatar:
            existing_photos_result = await db.execute(
                select(PetPhoto).where(and_(PetPhoto.pet_id == pet_id, PetPhoto.is_avatar == True))
            )
            for existing_photo in existing_photos_result.scalars().all():
                existing_photo.is_avatar = False

        # 创建照片记录
        photo = PetPhoto(
            pet_id=pet_id,
            url=file_url,
            description=description,
            file_size=file_size,
            is_avatar=is_avatar
        )

        db.add(photo)
        await db.commit()
        await db.refresh(photo)

        # 如果是头像，更新宠物的头像URL
        if is_avatar:
            pet.avatar_url = file_url
            await db.commit()

        return PetPhotoResponse.from_orm(photo)

    @staticmethod
    async def get_pet_photos(
        db: AsyncSession,
        pet_id: int,
        owner_id: int
    ) -> List[PetPhotoResponse]:
        """
        获取宠物照片列表
        """
        # 验证宠物存在且属于当前用户
        result = await db.execute(
            select(Pet).where(and_(Pet.id == pet_id, Pet.owner_id == owner_id, Pet.is_active == True))
        )
        pet = result.scalar_one_or_none()
        
        if not pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="宠物不存在"
            )

        # 获取照片列表
        photos_result = await db.execute(
            select(PetPhoto)
            .where(PetPhoto.pet_id == pet_id)
            .order_by(PetPhoto.is_avatar.desc(), PetPhoto.created_at.desc())
        )
        photos = photos_result.scalars().all()

        return [PetPhotoResponse.from_orm(photo) for photo in photos]

    @staticmethod
    async def delete_pet_photo(
        db: AsyncSession,
        photo_id: int,
        owner_id: int
    ) -> bool:
        """
        删除宠物照片
        """
        # 查找照片并验证权限
        result = await db.execute(
            select(PetPhoto)
            .join(Pet)
            .where(and_(
                PetPhoto.id == photo_id,
                Pet.owner_id == owner_id,
                Pet.is_active == True
            ))
        )
        photo = result.scalar_one_or_none()
        
        if not photo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="照片不存在"
            )

        # 删除文件
        if photo.url.startswith("/uploads/"):
            file_path = photo.url[1:]  # 去掉开头的 /
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    # 文件删除失败不影响数据库记录删除
                    print(f"删除文件失败: {e}")

        # 如果删除的是头像，清除宠物的头像URL
        if photo.is_avatar:
            pet_result = await db.execute(
                select(Pet).where(Pet.id == photo.pet_id)
            )
            pet = pet_result.scalar_one_or_none()
            if pet:
                pet.avatar_url = None

        # 删除数据库记录
        await db.delete(photo)
        await db.commit()

        return True 