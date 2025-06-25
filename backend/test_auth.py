#!/usr/bin/env python3
"""
认证系统测试脚本
测试FastAPI认证接口的兼容性
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class AuthTester:
    """认证系统测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
    
    async def test_health(self) -> bool:
        """测试健康检查"""
        try:
            response = await self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ 服务健康检查通过")
                return True
            else:
                print(f"❌ 服务健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接服务失败: {e}")
            return False
    
    async def test_register(self, username: str, password: str) -> bool:
        """测试用户注册"""
        try:
            data = {"username": username, "password": password}
            response = await self.session.post(
                f"{self.base_url}/auth/register",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 用户注册成功: {result['user']['username']}")
                self.access_token = result.get('access_token')
                return True
            else:
                result = response.json()
                print(f"❌ 用户注册失败: {result.get('detail', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ 注册请求失败: {e}")
            return False
    
    async def test_login(self, username: str, password: str) -> bool:
        """测试用户登录"""
        try:
            data = {"username": username, "password": password}
            response = await self.session.post(
                f"{self.base_url}/auth/login",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 用户登录成功: {result['user']['username']}")
                self.access_token = result.get('access_token')
                
                # 打印响应格式（验证兼容性）
                print(f"📋 响应格式: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
            else:
                result = response.json()
                print(f"❌ 用户登录失败: {result.get('detail', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ 登录请求失败: {e}")
            return False
    
    async def test_get_user_info(self) -> bool:
        """测试获取用户信息（Cookie方式）"""
        try:
            response = await self.session.get(f"{self.base_url}/auth/user")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 获取用户信息成功: {result['user']['username']}")
                print(f"📋 认证方式: {result['authType']}")
                return True
            else:
                result = response.json()
                print(f"❌ 获取用户信息失败: {result.get('detail', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ 获取用户信息请求失败: {e}")
            return False
    
    async def test_token_auth(self) -> bool:
        """测试Token认证"""
        if not self.access_token:
            print("❌ 没有access_token，跳过Token认证测试")
            return False
        
        try:
            # 测试Bearer Token方式
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.session.get(
                f"{self.base_url}/auth/user",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Token认证成功: {result['user']['username']}")
                print(f"📋 认证方式: {result['authType']}")
                return True
            else:
                print(f"❌ Token认证失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Token认证请求失败: {e}")
            return False
    
    async def test_token_info(self) -> bool:
        """测试通过Token获取用户信息"""
        if not self.access_token:
            print("❌ 没有access_token，跳过Token信息测试")
            return False
        
        try:
            data = {"accessToken": self.access_token}
            response = await self.session.post(
                f"{self.base_url}/auth/user/info",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Token信息获取成功: {result['user']['username']}")
                print(f"📋 Token过期时间: {result['tokenInfo']['expiresAt']}")
                return True
            else:
                result = response.json()
                print(f"❌ Token信息获取失败: {result.get('detail', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Token信息请求失败: {e}")
            return False
    
    async def test_logout(self) -> bool:
        """测试用户登出"""
        try:
            response = await self.session.post(f"{self.base_url}/auth/logout")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 用户登出成功: {result['message']}")
                return True
            else:
                print(f"❌ 用户登出失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 登出请求失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 FastAPI认证系统兼容性测试")
        print("=" * 60)
        
        # 测试用户凭据
        test_username = "test_user_" + str(int(asyncio.get_event_loop().time()))
        test_password = "test123456"
        
        tests = [
            ("服务健康检查", self.test_health()),
            ("用户注册", self.test_register(test_username, test_password)),
            ("用户登录", self.test_login(test_username, test_password)),
            ("获取用户信息(Cookie)", self.test_get_user_info()),
            ("Token认证", self.test_token_auth()),
            ("Token信息获取", self.test_token_info()),
            ("用户登出", self.test_logout()),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_coro in tests:
            print(f"\n🔍 测试: {test_name}")
            try:
                result = await test_coro
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ 测试异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed}/{total} 通过")
        if passed == total:
            print("🎉 所有测试通过！认证系统兼容性良好")
            print("💡 可以安全地将iOS应用迁移到FastAPI后端")
        else:
            print("⚠️ 部分测试失败，请检查配置和依赖")
        print("=" * 60)
        
        await self.session.aclose()


async def main():
    """主函数"""
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 测试目标: {base_url}")
    
    tester = AuthTester(base_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 