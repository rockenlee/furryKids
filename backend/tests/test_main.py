import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查接口"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """测试根路径接口"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "毛孩子AI后端服务"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_docs_endpoint(client: AsyncClient):
    """测试API文档接口"""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"] 