"""
毛孩子AI后端服务主入口
FastAPI应用配置和启动
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import time
import os

from app.core.config import settings
from app.core.database import init_db, close_db, db_manager
from app.api.v1 import auth, pets, feeds, ai, users


# 配置限流器
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动毛孩子AI后端服务...")
    
    try:
        # 创建上传目录
        os.makedirs("uploads/pets", exist_ok=True)
        logger.info("✅ 上传目录创建完成")
        
        # 初始化数据库
        await init_db()
        logger.info("✅ 数据库初始化完成")
        
        # 数据库健康检查
        if await db_manager.health_check():
            logger.info("✅ 数据库连接正常")
        else:
            logger.error("❌ 数据库连接失败")
            
        logger.info(f"🌟 服务启动成功 - {settings.PROJECT_NAME} v{settings.VERSION}")
        
    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("🛑 正在关闭服务...")
    await close_db()
    logger.info("✅ 服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="为宠物主人提供AI互动、社交分享等功能的后端API服务",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 添加静态文件服务
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 添加限流器到应用
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间到响应头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # 记录慢请求
    if process_time > 1.0:
        logger.warning(
            f"🐌 慢请求警告 - {request.method} {request.url.path} "
            f"耗时: {process_time:.2f}s"
        )
    
    return response


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"❌ 未处理的异常 - {request.method} {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error": str(exc) if settings.DEBUG else "Internal server error",
            "path": str(request.url.path),
        }
    )


# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(pets.router, prefix="/api/pets", tags=["宠物"])
app.include_router(feeds.router, prefix="/api/feeds", tags=["动态"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI互动"])


# 根路径
@app.get("/", tags=["系统"])
async def root():
    """根路径 - 服务信息"""
    return {
        "message": f"欢迎使用{settings.PROJECT_NAME}！",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "API文档已关闭",
        "endpoints": {
            "health": "/api/health",
            "auth": "/auth/*",
            "users": "/api/users/*",
            "pets": "/api/pets/*",
            "feeds": "/api/feeds/*",
            "ai": "/api/ai/*",
        }
    }


# 健康检查
@app.get("/api/health", tags=["系统"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db_healthy = await db_manager.health_check()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "timestamp": time.time(),
            "checks": {
                "database": "ok" if db_healthy else "error",
                "api": "ok"
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "error": str(e)
            }
        )


# 服务器信息
@app.get("/api/info", tags=["系统"])
@limiter.limit("5/minute")
async def server_info(request: Request):
    """获取服务器信息"""
    import platform
    import psutil
    
    try:
        return {
            "service": {
                "name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "environment": "development" if settings.DEBUG else "production",
            },
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": f"{psutil.virtual_memory().total // (1024**3)}GB",
            },
            "uptime": time.time(),
        }
    except Exception as e:
        logger.error(f"获取服务器信息失败: {e}")
        return {"error": "无法获取服务器信息"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 启动开发服务器 - {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 