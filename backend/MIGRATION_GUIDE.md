# 🔄 用户认证系统迁移指南

从 Passport Web (Node.js) 迁移到 FastAPI (Python) 认证系统

## 📋 迁移概述

### 当前状态
- **Passport Web**: 端口3001，Node.js + Express + Session认证
- **毛孩子AI后端**: 端口8000，Python + FastAPI + JWT认证

### 目标状态
- **统一后端**: 端口8000，FastAPI提供所有功能（认证 + 业务逻辑）
- **兼容接口**: 保持与Passport Web完全一致的API格式
- **增强功能**: 支持JWT + Cookie双重认证模式

## 🚀 迁移步骤

### 步骤1：准备工作

1. **确认Passport Web数据库信息**：
   ```bash
   # 检查passport数据库
   mysql -u root -p
   USE passport;
   SHOW TABLES;
   DESCRIBE users;
   SELECT COUNT(*) FROM users;
   ```

2. **配置迁移参数**：
   ```bash
   # 编辑迁移配置
   nano backend/migration_config.py
   
   # 修改数据库密码和字段映射
   PASSPORT_DB_CONFIG = {
       "password": "your_actual_password"  # 改为实际密码
   }
   ```

### 步骤2：安装依赖

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤3：执行数据迁移

```bash
# 运行用户数据迁移脚本
python3 scripts/migrate_users.py

# 或者逐步执行
python3 -c "
import asyncio
from scripts.migrate_users import UserMigrator

async def migrate():
    migrator = UserMigrator()
    await migrator.run_migration()
    await migrator.verify_migration()

asyncio.run(migrate())
"
```

### 步骤4：测试认证系统

```bash
# 确保FastAPI服务运行在8000端口
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 在新终端测试认证接口
python3 test_auth.py
```

### 步骤5：更新iOS应用

```swift
// 修改iOS应用的API配置
// 文件: FurryKids/Services/AuthService.swift

class AuthService: ObservableObject {
    // 从这个：
    private let baseURL = "http://localhost:3001"
    
    // 改为这个：
    private let baseURL = "http://localhost:8000"
    
    // 其他代码保持不变！
}
```

### 步骤6：验证完整流程

1. **启动FastAPI服务**：
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

2. **测试iOS应用登录**：
   - 使用原有的测试账户
   - 验证登录、获取用户信息、登出功能

3. **停用Passport Web**（可选）：
   ```bash
   # 确认iOS应用正常工作后，可以停用原服务
   # pkill -f "node.*passport"
   ```

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务
brew services list | grep mysql
# 或
sudo systemctl status mysql

# 检查数据库权限
mysql -u root -p -e "SHOW DATABASES;"
```

#### 2. 密码格式不兼容
```python
# 如果Passport Web使用不同的密码加密方式
# 需要在迁移脚本中添加密码转换逻辑
```

#### 3. 字段名不匹配
```python
# 修改 migration_config.py 中的字段映射
PASSPORT_USER_FIELDS = {
    "display_name": "display_name",  # 如果字段名不同
    "created_at": "created_time",    # 根据实际情况调整
}
```

### 验证清单

- [ ] 数据库连接正常
- [ ] 用户数据迁移成功
- [ ] 认证接口测试通过
- [ ] iOS应用登录正常
- [ ] 所有原有功能正常

## 📊 接口兼容性对照

### 登录接口
```bash
# Passport Web
POST http://localhost:3001/auth/login
{
  "username": "test",
  "password": "test"
}

# FastAPI (完全兼容)
POST http://localhost:8000/auth/login
{
  "username": "test", 
  "password": "test"
}

# 响应格式完全一致
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "test",
    "provider": "local"
  },
  "access_token": "eyJ..."  // FastAPI额外提供
}
```

### 用户信息接口
```bash
# 两个系统的响应格式完全一致
GET /auth/user
{
  "user": {
    "id": 1,
    "username": "test",
    "provider": "local"
  },
  "authType": "session"  // 或 "token"
}
```

## 🎯 迁移优势

1. **零代码修改** - iOS应用只需要改URL
2. **功能增强** - 支持JWT认证，更安全
3. **性能提升** - 减少跨服务调用
4. **统一技术栈** - 全部使用Python生态
5. **数据一致性** - 用户和业务数据在同一数据库

## 📞 技术支持

如果遇到问题：

1. 检查日志输出
2. 验证数据库连接
3. 确认字段映射正确
4. 测试单个接口功能

迁移完成后，你将拥有一个完全兼容、功能更强的认证系统！ 