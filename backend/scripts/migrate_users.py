#!/usr/bin/env python3
"""
用户数据迁移脚本
从 Passport Web 的 passport 数据库迁移用户数据到毛孩子AI的 furry_kids 数据库
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, select
from loguru import logger

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User


class UserMigrator:
    """用户数据迁移器"""
    
    def __init__(self):
        # 源数据库连接（Passport Web）
        self.source_engine = create_async_engine(
            "mysql+aiomysql://root:password@localhost:3306/passport",
            echo=True
        )
        
        # 目标数据库连接（毛孩子AI）
        self.target_session_factory = AsyncSessionLocal
        
    async def fetch_passport_users(self) -> List[Dict[str, Any]]:
        """从passport数据库获取用户数据"""
        async with self.source_engine.begin() as conn:
            # 查询passport数据库的用户表
            result = await conn.execute(text("""
                SELECT 
                    id,
                    username,
                    password as hashed_password,
                    provider,
                    providerId as provider_id,
                    email,
                    displayName as display_name,
                    createdAt as created_at,
                    updatedAt as updated_at
                FROM users 
                ORDER BY id
            """))
            
            users = []
            for row in result:
                users.append({
                    'original_id': row.id,
                    'username': row.username,
                    'hashed_password': row.hashed_password,
                    'provider': row.provider or 'local',
                    'provider_id': row.provider_id,
                    'email': row.email,
                    'display_name': row.display_name,
                    'created_at': row.created_at,
                    'updated_at': row.updated_at
                })
            
            logger.info(f"从passport数据库获取到 {len(users)} 个用户")
            return users
    
    async def migrate_user(self, session: AsyncSession, user_data: Dict[str, Any]) -> bool:
        """迁移单个用户"""
        try:
            # 检查用户是否已存在
            existing_user = await session.execute(
                select(User).where(User.username == user_data['username'])
            )
            if existing_user.scalar_one_or_none():
                logger.warning(f"用户 {user_data['username']} 已存在，跳过")
                return False
            
            # 创建新用户
            new_user = User(
                username=user_data['username'],
                hashed_password=user_data['hashed_password'],
                provider=user_data['provider'],
                provider_id=user_data['provider_id'],
                email=user_data['email'],
                display_name=user_data['display_name'],
                created_at=user_data['created_at'] or datetime.utcnow(),
                updated_at=user_data['updated_at'] or datetime.utcnow()
            )
            
            session.add(new_user)
            await session.flush()  # 获取新用户ID
            
            logger.info(f"✅ 迁移用户: {user_data['username']} (原ID: {user_data['original_id']} -> 新ID: {new_user.id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 迁移用户 {user_data['username']} 失败: {e}")
            return False
    
    async def run_migration(self):
        """执行完整迁移"""
        logger.info("🚀 开始用户数据迁移...")
        
        try:
            # 1. 获取源数据
            passport_users = await self.fetch_passport_users()
            
            if not passport_users:
                logger.warning("没有找到需要迁移的用户数据")
                return
            
            # 2. 迁移用户数据
            success_count = 0
            failed_count = 0
            
            async with self.target_session_factory() as session:
                for user_data in passport_users:
                    success = await self.migrate_user(session, user_data)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                
                # 提交事务
                await session.commit()
            
            logger.info(f"🎉 迁移完成! 成功: {success_count}, 失败: {failed_count}")
            
        except Exception as e:
            logger.error(f"❌ 迁移过程出错: {e}")
            raise
        
        finally:
            await self.source_engine.dispose()
    
    async def verify_migration(self):
        """验证迁移结果"""
        logger.info("🔍 验证迁移结果...")
        
        try:
            # 统计源数据库用户数
            async with self.source_engine.begin() as conn:
                source_result = await conn.execute(text("SELECT COUNT(*) as count FROM users"))
                source_count = source_result.scalar()
            
            # 统计目标数据库用户数
            async with self.target_session_factory() as session:
                target_result = await session.execute(text("SELECT COUNT(*) as count FROM users"))
                target_count = target_result.scalar()
            
            logger.info(f"📊 源数据库用户数: {source_count}")
            logger.info(f"📊 目标数据库用户数: {target_count}")
            
            if target_count >= source_count:
                logger.info("✅ 迁移验证通过")
            else:
                logger.warning("⚠️ 目标数据库用户数少于源数据库，请检查迁移过程")
                
        except Exception as e:
            logger.error(f"❌ 验证过程出错: {e}")
        
        finally:
            await self.source_engine.dispose()


async def main():
    """主函数"""
    print("=" * 60)
    print("🔄 毛孩子AI - 用户数据迁移工具")
    print("=" * 60)
    
    migrator = UserMigrator()
    
    # 询问用户确认
    confirm = input("\n⚠️  即将从passport数据库迁移用户数据到furry_kids数据库\n是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("❌ 迁移已取消")
        return
    
    try:
        # 执行迁移
        await migrator.run_migration()
        
        # 验证结果
        await migrator.verify_migration()
        
        print("\n" + "=" * 60)
        print("🎉 用户数据迁移完成！")
        print("💡 接下来可以：")
        print("   1. 测试FastAPI认证接口")
        print("   2. 更新iOS应用的API地址")
        print("   3. 停用Passport Web服务")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        print("\n💡 请检查：")
        print("   1. passport数据库连接配置")
        print("   2. furry_kids数据库是否正常")
        print("   3. 用户表结构是否匹配")


if __name__ == "__main__":
    asyncio.run(main()) 