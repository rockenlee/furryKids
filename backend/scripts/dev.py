#!/usr/bin/env python3
"""
开发脚本 - 快速启动和管理开发环境
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import db_manager


async def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    try:
        if await db_manager.health_check():
            print("✅ 数据库连接正常")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False


def run_migrations():
    """运行数据库迁移"""
    print("🔄 运行数据库迁移...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ 数据库迁移完成")
            return True
        else:
            print(f"❌ 数据库迁移失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据库迁移错误: {e}")
        return False


def start_server():
    """启动开发服务器"""
    print("🚀 启动开发服务器...")
    try:
        subprocess.run([
            "uvicorn",
            "app.main:app",
            "--host", settings.HOST,
            "--port", str(settings.PORT),
            "--reload",
            "--log-level", "info"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=project_root
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 测试运行错误: {e}")
        return False


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    try:
        result = subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            cwd=project_root
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 依赖安装错误: {e}")
        return False


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="毛孩子AI开发脚本")
    parser.add_argument(
        "command",
        choices=["start", "test", "check", "migrate", "install"],
        help="要执行的命令"
    )
    
    args = parser.parse_args()
    
    if args.command == "install":
        install_dependencies()
    elif args.command == "check":
        await check_database()
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "test":
        run_tests()
    elif args.command == "start":
        print(f"🌟 启动 {settings.PROJECT_NAME} v{settings.VERSION}")
        
        # 检查数据库连接
        if not await check_database():
            print("❌ 请检查数据库配置和连接")
            return
        
        # 运行迁移
        if not run_migrations():
            print("❌ 数据库迁移失败，请检查配置")
            return
        
        # 启动服务器
        start_server()


if __name__ == "__main__":
    asyncio.run(main()) 