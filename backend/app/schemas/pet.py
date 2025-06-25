"""
宠物相关的数据模式
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PetGenderEnum(str, Enum):
    """宠物性别枚举"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class PetSizeEnum(str, Enum):
    """宠物体型枚举"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    GIANT = "giant"


class PetMoodEnum(str, Enum):
    """宠物心情枚举"""
    HAPPY = "happy"
    EXCITED = "excited"
    CALM = "calm"
    SLEEPY = "sleepy"
    PLAYFUL = "playful"
    HUNGRY = "hungry"
    SAD = "sad"
    ANXIOUS = "anxious"


class PetCreate(BaseModel):
    """创建宠物请求"""
    name: str = Field(..., min_length=1, max_length=50, description="宠物名称")
    breed: str = Field(..., min_length=1, max_length=100, description="品种")
    age: Optional[int] = Field(None, ge=0, le=300, description="年龄（月）")
    gender: PetGenderEnum = Field(PetGenderEnum.UNKNOWN, description="性别")
    color: Optional[str] = Field(None, max_length=100, description="毛色")
    size: PetSizeEnum = Field(PetSizeEnum.MEDIUM, description="体型")
    weight: Optional[float] = Field(None, ge=0, le=200, description="体重（kg）")
    personality: Optional[str] = Field(None, max_length=200, description="性格描述")
    personality_tags: Optional[List[str]] = Field([], description="性格标签")
    current_mood: PetMoodEnum = Field(PetMoodEnum.HAPPY, description="当前心情")
    mood_description: Optional[str] = Field(None, max_length=200, description="心情描述")
    response_style: Optional[str] = Field("friendly", max_length=50, description="回复风格")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('宠物名称不能为空')
        return v.strip()

    @validator('breed')
    def validate_breed(cls, v):
        if not v.strip():
            raise ValueError('品种不能为空')
        return v.strip()


class PetUpdate(BaseModel):
    """更新宠物请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="宠物名称")
    breed: Optional[str] = Field(None, min_length=1, max_length=100, description="品种")
    age: Optional[int] = Field(None, ge=0, le=300, description="年龄（月）")
    gender: Optional[PetGenderEnum] = Field(None, description="性别")
    color: Optional[str] = Field(None, max_length=100, description="毛色")
    size: Optional[PetSizeEnum] = Field(None, description="体型")
    weight: Optional[float] = Field(None, ge=0, le=200, description="体重（kg）")
    personality: Optional[str] = Field(None, max_length=200, description="性格描述")
    personality_tags: Optional[List[str]] = Field(None, description="性格标签")
    current_mood: Optional[PetMoodEnum] = Field(None, description="当前心情")
    mood_description: Optional[str] = Field(None, max_length=200, description="心情描述")
    response_style: Optional[str] = Field(None, max_length=50, description="回复风格")
    ai_personality_prompt: Optional[str] = Field(None, description="AI个性化提示词")


class PetPhotoBase(BaseModel):
    """宠物照片基础信息"""
    url: str = Field(..., description="照片URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图URL")
    description: Optional[str] = Field(None, max_length=200, description="照片描述")
    is_avatar: bool = Field(False, description="是否为头像")


class PetPhotoCreate(PetPhotoBase):
    """创建宠物照片请求"""
    pass


class PetPhotoResponse(PetPhotoBase):
    """宠物照片响应"""
    id: int
    pet_id: int
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PetResponse(BaseModel):
    """宠物响应信息"""
    id: int
    name: str
    breed: str
    age: Optional[int] = None
    age_display: str
    gender: PetGenderEnum
    color: Optional[str] = None
    size: PetSizeEnum
    weight: Optional[float] = None
    avatar_url: Optional[str] = None
    personality: Optional[str] = None
    personality_tags: List[str] = []
    current_mood: PetMoodEnum
    mood_description: Optional[str] = None
    response_style: str
    interaction_count: int = 0
    experience_points: int = 0
    level: int = 1
    last_interaction_at: Optional[datetime] = None
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PetDetailResponse(PetResponse):
    """宠物详细信息响应"""
    photos: List[PetPhotoResponse] = []
    ai_personality_prompt: Optional[str] = None
    voice_style: Optional[str] = None

    class Config:
        from_attributes = True


class PetListResponse(BaseModel):
    """宠物列表响应"""
    pets: List[PetResponse]
    total: int
    page: int
    size: int
    has_next: bool

    class Config:
        from_attributes = True


class PetStats(BaseModel):
    """宠物统计信息"""
    total_pets: int
    active_pets: int
    total_interactions: int
    average_level: float
    mood_distribution: dict

    class Config:
        from_attributes = True 