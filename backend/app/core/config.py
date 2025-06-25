"""
应用配置管理
使用Pydantic Settings进行环境变量管理和验证
"""

from typing import List, Optional, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "毛孩子AI后端服务"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=3001, env="PORT")
    
    # 数据库配置
    MYSQL_HOST: str = Field(default="localhost", env="MYSQL_HOST")
    MYSQL_PORT: int = Field(default=3306, env="MYSQL_PORT")
    MYSQL_USER: str = Field(default="furry_user", env="MYSQL_USER")
    MYSQL_PASSWORD: str = Field(default="furry_password", env="MYSQL_PASSWORD")
    MYSQL_DATABASE: str = Field(default="furry_kids", env="MYSQL_DATABASE")
    
    # 直接从环境变量读取数据库URL（优先级更高）
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis配置
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # JWT配置
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # OpenRouter配置
    OPENROUTER_API_KEY: str = Field(default="", env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1", 
        env="OPENROUTER_BASE_URL"
    )
    DEFAULT_MODEL: str = Field(
        default="google/gemma-2-9b-it:free", 
        env="DEFAULT_MODEL"
    )
    
    # CORS配置 - 简化为字符串，避免JSON解析问题
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="ALLOWED_ORIGINS"
    )
    
    # 文件上传配置
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field(
        default="jpg,jpeg,png,gif,webp",
        env="ALLOWED_EXTENSIONS"
    )
    
    # 限流配置
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # 秒
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """获取CORS允许的源列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """获取允许的文件扩展名列表"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def database_url(self) -> str:
        """生成数据库连接URL"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )
    
    @property
    def async_database_url(self) -> str:
        """生成异步数据库连接URL"""
        # 优先使用环境变量中的DATABASE_URL
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )
    
    @property
    def DATABASE_URL(self) -> str:
        """向后兼容的数据库URL属性"""
        return self.async_database_url
    
    @property
    def JWT_SECRET_KEY(self) -> str:
        """向后兼容的JWT密钥属性"""
        return self.SECRET_KEY
    
    @property
    def JWT_ALGORITHM(self) -> str:
        """向后兼容的JWT算法属性"""
        return self.ALGORITHM
    
    @property
    def JWT_ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        """向后兼容的JWT过期时间属性"""
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外字段


# 创建全局配置实例
settings = Settings()


# 开发环境配置
class DevSettings(Settings):
    """开发环境配置"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


# 生产环境配置
class ProdSettings(Settings):
    """生产环境配置"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"


def get_settings() -> Settings:
    """根据环境获取配置"""
    import os
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProdSettings()
    else:
        return DevSettings() 