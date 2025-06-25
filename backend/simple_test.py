#!/usr/bin/env python3
"""
最简单的FastAPI测试
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="毛孩子AI测试")

@app.get("/")
async def root():
    return {"message": "🐾 毛孩子AI后端服务运行中", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "furrykids-ai"}

if __name__ == "__main__":
    print("🚀 启动简单测试服务...")
    uvicorn.run(app, host="0.0.0.0", port=8001) 