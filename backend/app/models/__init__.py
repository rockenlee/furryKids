"""
数据模型包
"""

from .user import User
from .pet import Pet
from .feed import Feed
from .message import Message, MessageType

__all__ = [
    "User",
    "Pet", 
    "Feed",
    "Message",
    "MessageType"
]

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class BaseModel(Base):
    """数据库模型基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 