"""
用户数据迁移配置文件
请根据你的实际数据库配置修改以下参数
"""

# Passport Web 数据库配置（源数据库）
PASSPORT_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password_here",  # 请修改为你的MySQL密码
    "database": "passport"
}

# 毛孩子AI 数据库配置（目标数据库）
# 这个会自动使用 app/core/config.py 中的配置

# Passport Web 用户表字段映射
# 如果你的passport数据库用户表字段名不同，请修改这里
PASSPORT_USER_FIELDS = {
    "id": "id",
    "username": "username", 
    "password": "password",  # 已加密的密码
    "provider": "provider",
    "provider_id": "providerId",  # 注意大小写
    "email": "email",
    "display_name": "displayName",  # 注意大小写
    "created_at": "createdAt",  # 注意大小写
    "updated_at": "updatedAt"   # 注意大小写
}

# 迁移选项
MIGRATION_OPTIONS = {
    "skip_existing_users": True,  # 跳过已存在的用户
    "preserve_user_ids": False,   # 是否保持原用户ID（可能会有冲突）
    "batch_size": 100,           # 批量处理大小
    "verify_passwords": False,    # 是否验证密码格式（bcrypt）
} 