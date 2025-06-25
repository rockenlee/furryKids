#!/usr/bin/env python3
"""
数据库连接测试脚本
测试MySQL连接和基础配置
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core.config import settings
    print("✅ 配置加载成功")
    print(f"   - 数据库: {settings.MYSQL_DATABASE}")
    print(f"   - 用户: {settings.MYSQL_USER}")
    print(f"   - 主机: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)


async def test_database_connection():
    """测试数据库连接"""
    try:
        from app.core.database import db_manager
        
        print("\n🔍 测试数据库连接...")
        
        # 健康检查
        is_healthy = await db_manager.health_check()
        
        if is_healthy:
            print("✅ 数据库连接成功！")
            print(f"   - 数据库URL: {settings.async_database_url}")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接错误: {e}")
        return False


async def test_ai_client():
    """测试AI客户端配置"""
    try:
        from app.utils.ai_client import OpenRouterClient
        
        print("\n🤖 测试AI客户端配置...")
        
        client = OpenRouterClient()
        
        if settings.OPENROUTER_API_KEY == "your-openrouter-api-key-here":
            print("⚠️  OpenRouter API密钥未配置")
            print("   请在.env文件中设置OPENROUTER_API_KEY")
            return False
        else:
            print("✅ OpenRouter配置正常")
            print(f"   - API密钥: {settings.OPENROUTER_API_KEY[:10]}...")
            print(f"   - 基础URL: {settings.OPENROUTER_BASE_URL}")
            print(f"   - 默认模型: {settings.DEFAULT_MODEL}")
            return True
            
    except Exception as e:
        print(f"❌ AI客户端配置错误: {e}")
        return False


def test_directories():
    """测试目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = ["logs", "uploads"]
    all_good = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            all_good = False
    
    return all_good


async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 毛孩子AI后端服务 - 配置测试")
    print("=" * 60)
    
    # 测试目录
    dirs_ok = test_directories()
    
    # 测试数据库
    db_ok = await test_database_connection()
    
    # 测试AI客户端
    ai_ok = test_ai_client()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    results = [
        ("目录结构", dirs_ok),
        ("数据库连接", db_ok),
        ("AI客户端配置", ai_ok)
    ]
    
    all_passed = True
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'通过' if status else '失败'}")
        if not status:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！项目配置完成，可以启动服务了！")
        print("\n🚀 下一步:")
        print("   1. 如果需要AI功能，请配置OPENROUTER_API_KEY")
        print("   2. 运行: python scripts/dev.py start")
        print("   3. 访问: http://localhost:3001/docs")
    else:
        print("\n⚠️  存在配置问题，请检查上述错误并修复")
        
    return all_passed


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        sys.exit(1) 