#!/usr/bin/env python3
"""
毛孩子AI服务启动脚本
"""

import uvicorn
import sys
import os

def main():
    print("🚀 启动毛孩子AI后端服务...")
    print("📍 端口: 8002")
    print("📚 API文档: http://localhost:8002/docs")
    print("🔧 开发模式: 热重载启用")
    print("-" * 50)
    
    try:
        # 确保在正确的目录
        if not os.path.exists("app/main.py"):
            print("❌ 错误: 请在backend目录下运行此脚本")
            sys.exit(1)
        
        # 启动服务
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8002,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 