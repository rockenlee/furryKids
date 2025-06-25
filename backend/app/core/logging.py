import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """配置日志系统"""
    
    # 移除默认的日志处理器
    logger.remove()
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # 添加文件日志处理器（如果配置了日志文件）
    if hasattr(settings, 'LOG_FILE') and settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            format=file_format,
            level=settings.LOG_LEVEL,
            rotation="10 MB",
            retention="7 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
    
    # 添加错误日志文件处理器
    if hasattr(settings, 'ERROR_LOG_FILE') and settings.ERROR_LOG_FILE:
        logger.add(
            settings.ERROR_LOG_FILE,
            format=file_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
    
    logger.info("日志系统初始化完成")


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger 