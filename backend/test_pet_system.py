#!/usr/bin/env python3
"""
宠物管理系统测试脚本
测试v0.3.0宠物管理系统的完整功能
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "petowner",
    "password": "test123456",
    "email": "petowner@example.com"
}

class PetSystemTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.auth_token = None
        self.created_pet_id = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def register_and_login(self) -> bool:
        """注册并登录测试用户"""
        print("🔐 测试用户认证...")
        
        try:
            # 尝试注册
            register_response = await self.client.post("/auth/register", json=TEST_USER)
            
            # 检查注册响应
            if register_response.status_code == 200:
                # 注册成功，响应中可能包含token
                register_data = register_response.json()
                if register_data.get("success") and register_data.get("access_token"):
                    self.auth_token = register_data["access_token"]
                    print("✅ 用户注册成功并获取Token")
                    return True
                else:
                    print("✅ 用户注册成功，准备登录")
            elif register_response.status_code == 400:
                # 用户已存在，直接登录
                print("✅ 用户已存在，准备登录")
            else:
                print(f"❌ 用户注册失败: {register_response.text}")
                return False
            
            # 如果没有token，尝试登录
            if not self.auth_token:
                login_response = await self.client.post("/auth/login", json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                })
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.auth_token = login_data.get("access_token")
                    print(f"✅ 登录成功，获取Token: {self.auth_token[:20]}...")
                    return True
                else:
                    print(f"❌ 登录失败: {login_response.text}")
                    return False
            
            return True
                
        except Exception as e:
            print(f"❌ 认证过程异常: {e}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    async def test_create_pet(self) -> bool:
        """测试创建宠物"""
        print("\n🐕 测试创建宠物...")
        
        pet_data = {
            "name": "小白",
            "breed": "金毛寻回犬",
            "age": 24,  # 2岁
            "gender": "male",
            "color": "金黄色",
            "size": "large",
            "weight": 30.5,
            "personality": "活泼友善，喜欢玩耍",
            "personality_tags": ["活泼", "友善", "聪明", "忠诚"],
            "current_mood": "happy",
            "mood_description": "今天心情特别好",
            "response_style": "friendly"
        }
        
        try:
            response = await self.client.post(
                "/api/pets/",
                json=pet_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 201:
                pet_info = response.json()
                self.created_pet_id = pet_info["id"]
                print(f"✅ 宠物创建成功！")
                print(f"   - ID: {pet_info['id']}")
                print(f"   - 名称: {pet_info['name']}")
                print(f"   - 品种: {pet_info['breed']}")
                print(f"   - 年龄显示: {pet_info['age_display']}")
                print(f"   - 性格标签: {pet_info['personality_tags']}")
                print(f"   - 等级: {pet_info['level']}")
                return True
            else:
                print(f"❌ 宠物创建失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 创建宠物异常: {e}")
            return False

    async def test_get_pets_list(self) -> bool:
        """测试获取宠物列表"""
        print("\n📋 测试获取宠物列表...")
        
        try:
            response = await self.client.get(
                "/api/pets/",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                pets_data = response.json()
                print(f"✅ 宠物列表获取成功！")
                print(f"   - 总数: {pets_data['total']}")
                print(f"   - 当前页: {pets_data['page']}")
                print(f"   - 每页数量: {pets_data['size']}")
                print(f"   - 宠物数量: {len(pets_data['pets'])}")
                
                if pets_data['pets']:
                    pet = pets_data['pets'][0]
                    print(f"   - 第一只宠物: {pet['name']} ({pet['breed']})")
                
                return True
            else:
                print(f"❌ 获取宠物列表失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取宠物列表异常: {e}")
            return False

    async def test_get_pet_detail(self) -> bool:
        """测试获取宠物详情"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n🔍 测试获取宠物详情 (ID: {self.created_pet_id})...")
        
        try:
            response = await self.client.get(
                f"/api/pets/{self.created_pet_id}",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                pet_detail = response.json()
                print(f"✅ 宠物详情获取成功！")
                print(f"   - 名称: {pet_detail['name']}")
                print(f"   - 品种: {pet_detail['breed']}")
                print(f"   - 年龄: {pet_detail['age_display']}")
                print(f"   - 性别: {pet_detail['gender']}")
                print(f"   - 体型: {pet_detail['size']}")
                print(f"   - 体重: {pet_detail['weight']}kg")
                print(f"   - 心情: {pet_detail['current_mood']}")
                print(f"   - 等级: {pet_detail['level']}")
                print(f"   - 经验值: {pet_detail['experience_points']}")
                print(f"   - 互动次数: {pet_detail['interaction_count']}")
                print(f"   - 照片数量: {len(pet_detail['photos'])}")
                return True
            else:
                print(f"❌ 获取宠物详情失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取宠物详情异常: {e}")
            return False

    async def test_update_pet(self) -> bool:
        """测试更新宠物信息"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n✏️ 测试更新宠物信息 (ID: {self.created_pet_id})...")
        
        update_data = {
            "personality": "非常活泼友善，特别聪明",
            "personality_tags": ["活泼", "友善", "聪明", "忠诚", "贪吃"],
            "weight": 32.0,
            "ai_personality_prompt": "你是一只名叫小白的金毛犬，非常活泼友善，特别喜欢和主人玩耍。"
        }
        
        try:
            response = await self.client.put(
                f"/api/pets/{self.created_pet_id}",
                json=update_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                updated_pet = response.json()
                print(f"✅ 宠物信息更新成功！")
                print(f"   - 性格: {updated_pet['personality']}")
                print(f"   - 性格标签: {updated_pet['personality_tags']}")
                print(f"   - 体重: {updated_pet['weight']}kg")
                print(f"   - AI提示词: {updated_pet.get('ai_personality_prompt', '无')[:50]}...")
                return True
            else:
                print(f"❌ 更新宠物信息失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新宠物信息异常: {e}")
            return False

    async def test_update_mood(self) -> bool:
        """测试更新宠物心情"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n😊 测试更新宠物心情 (ID: {self.created_pet_id})...")
        
        try:
            response = await self.client.patch(
                f"/api/pets/{self.created_pet_id}/mood",
                params={
                    "mood": "excited",
                    "description": "看到主人回家了，特别兴奋！"
                },
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                updated_pet = response.json()
                print(f"✅ 宠物心情更新成功！")
                print(f"   - 当前心情: {updated_pet['current_mood']}")
                print(f"   - 心情描述: {updated_pet['mood_description']}")
                return True
            else:
                print(f"❌ 更新宠物心情失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 更新宠物心情异常: {e}")
            return False

    async def test_add_interaction(self) -> bool:
        """测试增加互动"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n🎮 测试增加宠物互动 (ID: {self.created_pet_id})...")
        
        try:
            # 增加几次互动
            for i in range(3):
                response = await self.client.post(
                    f"/api/pets/{self.created_pet_id}/interaction",
                    headers=self.get_auth_headers()
                )
                
                if response.status_code == 200:
                    pet_data = response.json()
                    print(f"✅ 第{i+1}次互动成功！互动次数: {pet_data['interaction_count']}, 经验值: {pet_data['experience_points']}, 等级: {pet_data['level']}")
                else:
                    print(f"❌ 第{i+1}次互动失败: {response.text}")
                    return False
                    
            return True
                
        except Exception as e:
            print(f"❌ 增加互动异常: {e}")
            return False

    async def test_add_photo(self) -> bool:
        """测试添加宠物照片"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n📸 测试添加宠物照片 (ID: {self.created_pet_id})...")
        
        photo_data = {
            "url": "https://example.com/photos/pet1.jpg",
            "thumbnail_url": "https://example.com/photos/pet1_thumb.jpg",
            "description": "小白在公园玩耍的照片",
            "is_avatar": True
        }
        
        try:
            response = await self.client.post(
                f"/api/pets/{self.created_pet_id}/photos",
                json=photo_data,
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 201:
                photo_info = response.json()
                print(f"✅ 宠物照片添加成功！")
                print(f"   - 照片ID: {photo_info['id']}")
                print(f"   - URL: {photo_info['url']}")
                print(f"   - 描述: {photo_info['description']}")
                print(f"   - 是否头像: {photo_info['is_avatar']}")
                return True
            else:
                print(f"❌ 添加宠物照片失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 添加宠物照片异常: {e}")
            return False

    async def test_get_ai_prompt(self) -> bool:
        """测试获取AI提示词"""
        if not self.created_pet_id:
            print("❌ 没有可用的宠物ID")
            return False
            
        print(f"\n🤖 测试获取AI提示词 (ID: {self.created_pet_id})...")
        
        try:
            response = await self.client.get(
                f"/api/pets/{self.created_pet_id}/ai-prompt",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                ai_data = response.json()
                print(f"✅ AI提示词获取成功！")
                print(f"   - 宠物名称: {ai_data['pet_name']}")
                print(f"   - 当前心情: {ai_data['current_mood']}")
                print(f"   - 回复风格: {ai_data['response_style']}")
                print(f"   - 性格标签: {ai_data['personality_tags']}")
                print(f"   - AI提示词: {ai_data['ai_prompt'][:100]}...")
                return True
            else:
                print(f"❌ 获取AI提示词失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取AI提示词异常: {e}")
            return False

    async def test_get_stats(self) -> bool:
        """测试获取统计信息"""
        print("\n📊 测试获取宠物统计信息...")
        
        try:
            response = await self.client.get(
                "/api/pets/stats",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ 统计信息获取成功！")
                print(f"   - 总宠物数: {stats['total_pets']}")
                print(f"   - 活跃宠物数: {stats['active_pets']}")
                print(f"   - 总互动次数: {stats['total_interactions']}")
                print(f"   - 平均等级: {stats['average_level']:.2f}")
                print(f"   - 心情分布: {stats['mood_distribution']}")
                return True
            else:
                print(f"❌ 获取统计信息失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 获取统计信息异常: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始宠物管理系统完整测试...")
        print("=" * 60)
        
        tests = [
            ("用户认证", self.register_and_login),
            ("创建宠物", self.test_create_pet),
            ("获取宠物列表", self.test_get_pets_list),
            ("获取宠物详情", self.test_get_pet_detail),
            ("更新宠物信息", self.test_update_pet),
            ("更新宠物心情", self.test_update_mood),
            ("增加宠物互动", self.test_add_interaction),
            ("添加宠物照片", self.test_add_photo),
            ("获取AI提示词", self.test_get_ai_prompt),
            ("获取统计信息", self.test_get_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"🏁 测试完成！通过: {passed}/{total}")
        
        if passed == total:
            print("🎉 所有测试通过！v0.3.0宠物管理系统功能正常！")
        else:
            print(f"⚠️  有 {total - passed} 个测试失败，需要检查相关功能")


async def main():
    """主函数"""
    async with PetSystemTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 