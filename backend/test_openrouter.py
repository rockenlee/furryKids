#!/usr/bin/env python3
"""
OpenRouter API测试脚本
测试API密钥配置和连接
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        print("❌ python-dotenv未安装")
        return False

async def test_openrouter_config():
    """测试OpenRouter配置"""
    print("🤖 测试OpenRouter配置...")
    
    # 检查环境变量
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    default_model = os.getenv('DEFAULT_MODEL', 'openai/gpt-3.5-turbo')
    
    if not api_key or api_key == 'your-openrouter-api-key-here':
        print("❌ OpenRouter API密钥未配置或仍为默认值")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:20]}...")
    print(f"✅ 基础URL: {base_url}")
    print(f"✅ 默认模型: {default_model}")
    
    return True

async def test_openrouter_connection():
    """测试OpenRouter连接"""
    print("\n🔍 测试OpenRouter API连接...")
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # 测试简单对话
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "请说'你好，我是毛孩子AI！'"}
            ],
            max_tokens=50
        )
        
        ai_response = response.choices[0].message.content
        print(f"✅ API连接成功！")
        print(f"🎯 AI回复: {ai_response}")
        
        return True
        
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

async def test_pet_conversation():
    """测试宠物对话功能"""
    print("\n🐾 测试宠物对话功能...")
    
    try:
        # 使用项目的AI客户端
        from app.utils.ai_client import OpenRouterClient
        
        client = OpenRouterClient()
        
        # 测试宠物对话
        response = await client.generate_pet_response(
            pet_name="小白",
            pet_personality="活泼可爱的小狗",
            user_message="你今天心情怎么样？",
            context="主人刚回家"
        )
        
        print(f"✅ 宠物对话功能正常！")
        print(f"🐕 小白说: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ 宠物对话功能测试失败: {e}")
        print(f"   可能原因: AI客户端代码需要调整或依赖缺失")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 OpenRouter API 配置测试")
    print("=" * 60)
    
    # 加载环境变量
    if not load_env():
        print("❌ 无法加载环境变量")
        return False
    
    # 测试配置
    config_ok = await test_openrouter_config()
    if not config_ok:
        print("\n⚠️  请先正确配置OpenRouter API密钥")
        return False
    
    # 测试连接
    connection_ok = await test_openrouter_connection()
    
    # 测试宠物对话（可选）
    pet_ok = await test_pet_conversation()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    results = [
        ("配置检查", config_ok),
        ("API连接", connection_ok),
        ("宠物对话", pet_ok)
    ]
    
    all_passed = True
    for name, status in results:
        icon = "✅" if status else "❌"
        print(f"{icon} {name}: {'通过' if status else '失败'}")
        if not status:
            all_passed = False
    
    if all_passed:
        print("\n🎉 OpenRouter配置完美！AI功能已就绪！")
        print("\n🚀 下一步:")
        print("   1. 启动服务: uvicorn app.main:app --reload --host 0.0.0.0 --port 3001")
        print("   2. 访问API文档: http://localhost:3001/docs")
        print("   3. 测试AI对话接口")
    else:
        print("\n⚠️  存在问题，请检查上述错误")
        
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
        import traceback
        traceback.print_exc()
        sys.exit(1) 