"""
动态分享相关API路由
"""

from fastapi import APIRouter

router = APIRouter(prefix="/feeds", tags=["动态"])

@router.get("/health")
async def feeds_health():
    """动态服务健康检查"""
    return {"status": "ok", "service": "feeds"} 