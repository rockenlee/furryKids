"""
动态分享数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Feed(Base):
    """动态分享模型"""
    __tablename__ = "feeds"
    
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)  # 动态内容
    images = Column(JSON, nullable=True)  # 图片URL列表
    mood = Column(String(20), nullable=True)  # 心情标签
    tags = Column(JSON, nullable=True)  # 话题标签
    likes_count = Column(Integer, default=0)  # 点赞数
    comments_count = Column(Integer, default=0)  # 评论数
    shares_count = Column(Integer, default=0)  # 分享数
    is_public = Column(Boolean, default=True)  # 是否公开
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    pet = relationship("Pet")
    user = relationship("User") 