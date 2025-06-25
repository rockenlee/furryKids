#!/usr/bin/env python3
"""
毛孩子AI开发服务器启动脚本
使用8000端口，localhost绑定
"""

import uvicorn
import sys
import os

def main():
    print("🐾 毛孩子AI后端服务")
    print("=" * 40)
    print("📍 地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔧 开发模式: 热重载启用")
    print("=" * 40)
    
    # 确保在正确的目录
    if not os.path.exists("app/main.py"):
        print("❌ 错误: 请在backend目录下运行此脚本")
        print("   cd backend && python3 start_dev_server.py")
        sys.exit(1)
    
    try:
        # 启动开发服务器
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",  # 使用localhost避免网络权限问题
            port=8000,         # 使用8000端口
            reload=True,       # 启用热重载
            log_level="info",  # 详细日志
            access_log=True    # 访问日志
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 