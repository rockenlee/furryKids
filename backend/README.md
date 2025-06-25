# 毛孩子AI后端服务 (Python FastAPI)

基于FastAPI + SQLAlchemy + MySQL的现代化后端API服务，为毛孩子AI应用提供用户认证、宠物管理、AI互动、社交分享等功能。

## 📋 版本信息

### 🎯 v0.1.0 - 基础架构完成 ✅

#### ✅ 已实现功能
- **FastAPI应用框架**: 完整的异步Web框架配置
- **数据库连接**: MySQL + SQLAlchemy异步ORM
- **配置管理**: Pydantic Settings环境变量管理
- **日志系统**: Loguru结构化日志记录
- **中间件系统**: 请求日志、CORS、限流保护
- **AI客户端**: OpenRouter集成，支持多模型
- **数据库迁移**: Alembic自动迁移管理
- **容器化**: Docker + Docker Compose完整配置
- **测试框架**: Pytest异步测试支持
- **开发工具**: 开发脚本和环境管理

#### 🎯 交付标准达成
- [x] 服务启动正常（http://localhost:3001）
- [x] 健康检查接口可访问（/api/health）
- [x] API文档自动生成（/docs）
- [x] 数据库连接测试通过
- [x] Docker镜像构建成功
- [x] 基础测试覆盖率 > 80%
- [x] 日志系统正常工作
- [x] 请求响应时间监控

#### 📦 技术栈
- **后端框架**: FastAPI 0.104+
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0
- **AI服务**: OpenRouter (多模型支持)
- **日志**: Loguru
- **测试**: Pytest + AsyncIO
- **容器**: Docker + Docker Compose

### ⏳ 下阶段计划
- **v0.2.0**: 用户认证系统 (Week 3-4)
- **v0.3.0**: 宠物管理功能 (Week 5-6)
- **v0.4.0**: AI对话系统 (Week 7-8)

## 🚀 快速开始

### 环境要求
- Python 3.11+
- MySQL 8.0+
- Redis 6.0+ (可选，用于缓存)

### 安装步骤

1. **克隆项目并进入后端目录**
```bash
cd backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

5. **配置数据库**
```sql
-- 创建数据库
CREATE DATABASE furry_kids CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'furry_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON furry_kids.* TO 'furry_user'@'localhost';
FLUSH PRIVILEGES;
```

6. **启动服务**
```bash
# 开发模式
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

## 📡 API文档

启动服务后访问：
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## 🏗️ 技术架构

### 核心技术栈
- **Web框架**: FastAPI 0.104+
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0
- **AI服务**: OpenRouter (OpenAI兼容)
- **认证**: JWT + Bcrypt
- **异步**: asyncio + aiohttp

### 项目结构
```
backend/
├── app/                     # 应用主目录
│   ├── main.py             # FastAPI应用入口
│   ├── core/               # 核心配置
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   └── security.py     # 安全认证
│   ├── models/             # SQLAlchemy模型
│   │   ├── user.py         # 用户模型
│   │   ├── pet.py          # 宠物模型
│   │   ├── feed.py         # 动态模型
│   │   └── message.py      # 消息模型
│   ├── schemas/            # Pydantic模式
│   │   ├── user.py         # 用户数据模式
│   │   ├── pet.py          # 宠物数据模式
│   │   └── response.py     # 响应模式
│   ├── api/                # API路由
│   │   └── v1/             # API版本1
│   │       ├── auth.py     # 认证路由
│   │       ├── pets.py     # 宠物路由
│   │       ├── feeds.py    # 动态路由
│   │       └── ai.py       # AI路由
│   ├── services/           # 业务逻辑层
│   │   ├── auth_service.py # 认证服务
│   │   ├── pet_service.py  # 宠物服务
│   │   └── ai_service.py   # AI服务
│   └── utils/              # 工具函数
│       ├── ai_client.py    # OpenRouter客户端
│       └── helpers.py      # 辅助函数
├── alembic/                # 数据库迁移
├── tests/                  # 测试文件
├── requirements.txt        # Python依赖
└── README.md              # 项目文档
```

## 🔧 配置说明

### 环境变量配置

#### 数据库配置
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=furry_kids
```

#### OpenRouter AI配置
```env
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-3.5-turbo
```

#### JWT认证配置
```env
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🤖 AI功能特色

### OpenRouter集成
- 支持多种AI模型（GPT-3.5、GPT-4、Claude等）
- 个性化宠物对话生成
- 智能动态内容创作
- 情感分析和心情识别

### 宠物AI特性
- **个性化对话**: 根据宠物品种、性格生成专属回复
- **上下文记忆**: 保持对话连贯性和情感连续性
- **动态生成**: AI自动创作宠物朋友圈内容
- **情感分析**: 理解用户情绪并调整宠物回应

## 📊 API端点概览

### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/logout` - 用户登出
- `GET /auth/me` - 获取当前用户

### 宠物管理
- `GET /api/pets` - 获取宠物列表
- `POST /api/pets` - 创建宠物
- `PUT /api/pets/{id}` - 更新宠物信息
- `DELETE /api/pets/{id}` - 删除宠物

### AI互动
- `POST /api/ai/chat` - 与宠物聊天
- `POST /api/ai/generate-post` - 生成动态内容
- `GET /api/ai/conversation/{pet_id}` - 获取对话历史

### 动态分享
- `GET /api/feeds` - 获取动态列表
- `POST /api/feeds` - 发布动态
- `POST /api/feeds/{id}/like` - 点赞动态
- `POST /api/feeds/{id}/comment` - 评论动态

## 🧪 开发调试

### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app tests/
```

### 代码格式化
```bash
# 格式化代码
black app/
isort app/

# 类型检查
mypy app/

# 代码风格检查
flake8 app/
```

### 数据库迁移
```bash
# 初始化迁移
alembic init alembic

# 创建迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

## 🐳 Docker部署

### 构建镜像
```bash
docker build -t furry-kids-backend .
```

### 运行容器
```bash
docker run -d \
  --name furry-kids-api \
  -p 3001:3001 \
  -e MYSQL_HOST=host.docker.internal \
  -e OPENROUTER_API_KEY=your-key \
  furry-kids-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## 📈 性能优化

### 数据库优化
- 使用连接池管理数据库连接
- 添加适当的索引
- 查询优化和分页

### API性能
- 异步处理提高并发能力
- 请求限流防止滥用
- Gzip压缩减少传输大小
- 响应缓存提高速度

### AI服务优化
- Token使用量监控
- 请求缓存减少API调用
- 异步处理提高响应速度

## 🔒 安全特性

- JWT令牌认证
- 密码哈希加密
- 请求限流
- CORS跨域保护
- SQL注入防护
- XSS攻击防护

## 📝 开发规范

### 代码风格
- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 使用类型提示增强代码可读性

### 提交规范
- 功能: `feat: 添加宠物管理功能`
- 修复: `fix: 修复登录验证问题`
- 文档: `docs: 更新API文档`
- 重构: `refactor: 优化数据库查询`

## 🆘 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库连接信息
   - 确认数据库用户权限

2. **AI服务调用失败**
   - 检查OpenRouter API密钥
   - 验证网络连接
   - 查看API配额使用情况

3. **依赖安装问题**
   - 使用虚拟环境隔离依赖
   - 更新pip到最新版本
   - 检查Python版本兼容性

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请：
- 提交Issue
- 联系开发团队
- 查看文档和FAQ 