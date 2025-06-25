"""
宠物数据模型
包含宠物的基础信息、外观特征、性格特征等
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class PetGender(str, enum.Enum):
    """宠物性别枚举"""
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class PetSize(str, enum.Enum):
    """宠物体型枚举"""
    SMALL = "small"      # 小型 (< 10kg)
    MEDIUM = "medium"    # 中型 (10-25kg)
    LARGE = "large"      # 大型 (25-45kg)
    GIANT = "giant"      # 巨型 (> 45kg)


class PetMood(str, enum.Enum):
    """宠物心情枚举"""
    HAPPY = "happy"          # 开心
    EXCITED = "excited"      # 兴奋
    CALM = "calm"           # 平静
    SLEEPY = "sleepy"       # 困倦
    PLAYFUL = "playful"     # 爱玩
    HUNGRY = "hungry"       # 饥饿
    SAD = "sad"             # 伤心
    ANXIOUS = "anxious"     # 焦虑


class Pet(Base):
    """
    宠物模型
    存储宠物的完整信息，包括基础信息、外观、性格等
    """
    __tablename__ = "pets"

    # 基础信息
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="宠物名称")
    breed = Column(String(100), nullable=False, comment="品种")
    age = Column(Integer, nullable=True, comment="年龄（月）")
    gender = Column(Enum(PetGender), default=PetGender.UNKNOWN, comment="性别")
    
    # 外观特征
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    color = Column(String(100), nullable=True, comment="毛色")
    size = Column(Enum(PetSize), default=PetSize.MEDIUM, comment="体型")
    weight = Column(Float, nullable=True, comment="体重（kg）")
    
    # 性格特征
    personality = Column(String(200), nullable=True, comment="性格描述")
    traits = Column(Text, nullable=True, comment="性格特征标签（JSON格式）")
    current_mood = Column(Enum(PetMood), default=PetMood.HAPPY, comment="当前心情")
    mood_description = Column(String(200), nullable=True, comment="心情描述")
    
    # AI相关配置
    ai_personality_prompt = Column(Text, nullable=True, comment="AI个性化提示词")
    voice_style = Column(String(50), nullable=True, comment="语音风格")
    response_style = Column(String(50), default="friendly", comment="回复风格")
    
    # 统计信息
    interaction_count = Column(Integer, default=0, comment="互动次数")
    last_interaction_at = Column(DateTime, nullable=True, comment="最后互动时间")
    experience_points = Column(Integer, default=0, comment="经验值")
    level = Column(Integer, default=1, comment="等级")
    
    # 关联关系
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="主人ID")
    
    # 系统字段
    is_active = Column(Boolean, default=True, comment="是否活跃")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系定义
    owner = relationship("User", back_populates="pets")
    photos = relationship("PetPhoto", back_populates="pet", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="pet", cascade="all, delete-orphan")
    feeds = relationship("Feed", back_populates="pet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', breed='{self.breed}', owner_id={self.owner_id})>"

    @property
    def age_display(self) -> str:
        """格式化显示年龄"""
        if not self.age:
            return "未知"
        
        years = self.age // 12
        months = self.age % 12
        
        if years > 0:
            if months > 0:
                return f"{years}岁{months}个月"
            else:
                return f"{years}岁"
        else:
            return f"{months}个月"

    @property
    def personality_tags(self) -> list:
        """获取性格标签列表"""
        if not self.traits:
            return []
        
        try:
            import json
            return json.loads(self.traits)
        except:
            return []

    @personality_tags.setter
    def personality_tags(self, tags: list):
        """设置性格标签"""
        import json
        self.traits = json.dumps(tags, ensure_ascii=False)

    def add_interaction(self):
        """增加互动次数"""
        self.interaction_count += 1
        self.last_interaction_at = datetime.utcnow()
        
        # 简单的经验值系统
        self.experience_points += 1
        
        # 升级逻辑（每10次互动升1级）
        new_level = (self.experience_points // 10) + 1
        if new_level > self.level:
            self.level = new_level

    def get_ai_prompt(self) -> str:
        """获取AI对话提示词"""
        if self.ai_personality_prompt:
            return self.ai_personality_prompt
        
        # 默认提示词模板
        mood_text = {
            PetMood.HAPPY: "心情很好，很开心",
            PetMood.EXCITED: "非常兴奋，充满活力",
            PetMood.CALM: "很平静，很放松",
            PetMood.SLEEPY: "有点困倦，想睡觉",
            PetMood.PLAYFUL: "想要玩耍，很活跃",
            PetMood.HUNGRY: "有点饿了，想吃东西",
            PetMood.SAD: "有点伤心，需要安慰",
            PetMood.ANXIOUS: "有点焦虑，需要关爱"
        }.get(self.current_mood, "心情不错")
        
        personality_desc = self.personality or "友善可爱"
        
        prompt = f"""你是一只名叫{self.name}的{self.breed}，{self.age_display}大。
你的性格是{personality_desc}，目前{mood_text}。
请用宠物的视角和语气回复主人，表现出你的个性特征。
回复要温馨、可爱，符合宠物的特点。"""
        
        return prompt


class PetPhoto(Base):
    """
    宠物照片模型
    存储宠物的照片信息
    """
    __tablename__ = "pet_photos"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False, comment="宠物ID")
    url = Column(String(500), nullable=False, comment="照片URL")
    thumbnail_url = Column(String(500), nullable=True, comment="缩略图URL")
    description = Column(String(200), nullable=True, comment="照片描述")
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    width = Column(Integer, nullable=True, comment="图片宽度")
    height = Column(Integer, nullable=True, comment="图片高度")
    is_avatar = Column(Boolean, default=False, comment="是否为头像")
    
    # 系统字段
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系定义
    pet = relationship("Pet", back_populates="photos")

    def __repr__(self):
        return f"<PetPhoto(id={self.id}, pet_id={self.pet_id}, url='{self.url}')>" 