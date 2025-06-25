"""
AI对话相关API路由
"""

from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI对话"])

@router.get("/health")
async def ai_health():
    """AI服务健康检查"""
    return {"status": "ok", "service": "ai"} 