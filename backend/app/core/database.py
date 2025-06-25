"""
数据库连接管理
使用SQLAlchemy 2.0的异步引擎和会话管理
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
from loguru import logger

from .config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,  # 开发环境下打印SQL
    pool_pre_ping=True,   # 连接池预检测
    pool_recycle=3600,    # 连接回收时间（秒）
    pool_size=20,         # 连接池大小
    max_overflow=30,      # 最大溢出连接数
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# 创建基础模型类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于FastAPI的Depends
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话错误: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库
    创建所有表
    """
    try:
        # 导入所有模型以确保它们被注册
        from app.models import user, pet, feed, message  # noqa: F401
        
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ 数据库表创建成功")
            
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def close_db() -> None:
    """
    关闭数据库连接
    """
    try:
        await engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def health_check(self) -> bool:
        """数据库健康检查"""
        try:
            async with self.session_factory() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return False
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        return self.session_factory()


# 创建全局数据库管理器实例
db_manager = DatabaseManager() 