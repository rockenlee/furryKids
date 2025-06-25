#!/usr/bin/env python3
"""
OpenRouter API简化测试脚本
使用免费模型进行测试
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openrouter_simple():
    """简单测试OpenRouter连接"""
    print("🧪 OpenRouter 简化测试")
    print("=" * 40)
    
    # 检查API密钥
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'your-openrouter-api-key-here':
        print("❌ API密钥未配置")
        return False
    
    print(f"✅ API密钥: {api_key[:20]}...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # 使用免费模型进行测试
        free_models = [
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free"
        ]
        
        success = False
        for model in free_models:
            try:
                print(f"\n🔍 测试模型: {model}")
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "请简单说一句话：你好，我是毛孩子AI！"}
                    ],
                    max_tokens=50
                )
                
                ai_response = response.choices[0].message.content
                print(f"✅ 成功！AI回复: {ai_response}")
                success = True
                break
                
            except Exception as e:
                print(f"❌ 模型 {model} 失败: {e}")
                continue
        
        if success:
            print(f"\n🎉 OpenRouter配置成功！")
            print(f"🚀 推荐在.env中设置: DEFAULT_MODEL={model}")
            return True
        else:
            print(f"\n❌ 所有测试模型都失败了")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_simple()
    sys.exit(0 if success else 1) 