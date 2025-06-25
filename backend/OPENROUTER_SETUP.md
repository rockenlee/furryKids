# OpenRouter 配置指南

## 📋 概览

OpenRouter 是一个统一的AI模型API服务，提供对数百个AI模型的访问，包括OpenAI、Anthropic、Google等提供商的模型。通过单一API端点即可访问多种模型，并自动处理故障转移和成本优化。

## 🔑 获取API密钥

### 1. 注册OpenRouter账户
1. 访问 [OpenRouter.ai](https://openrouter.ai)
2. 点击 "Sign up with email/wallet" 注册账户
3. 验证邮箱并完成注册

### 2. 创建API密钥
1. 登录后，点击页面上的 "Keys" 按钮
2. 点击 "Create Key" 创建新的API密钥
3. 为密钥命名（如：furry-kids-ai-backend）
4. 点击 "Create" 生成密钥
5. **重要**: 复制并安全保存生成的密钥，这是唯一显示机会

### 3. 充值账户（可选）
- OpenRouter提供免费额度用于测试
- 生产环境建议充值以确保服务稳定性
- 支持信用卡和加密货币充值

## ⚙️ 配置项目

### 1. 配置环境变量

在 `.env` 文件中添加您的OpenRouter API密钥：

```bash
# OpenRouter AI配置
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-3.5-turbo

# 可选：网站信息（用于OpenRouter排行榜）
SITE_URL=http://localhost:3001
SITE_NAME=毛孩子AI
```

### 2. 推荐模型配置

根据不同用途，推荐以下模型：

#### 🐾 宠物对话 (性价比)
```bash
DEFAULT_MODEL=openai/gpt-3.5-turbo
# 成本低，响应快，适合日常对话
```

#### 🧠 智能对话 (平衡)
```bash
DEFAULT_MODEL=openai/gpt-4o-mini
# 更智能，成本适中
```

#### 🎯 高质量对话 (高端)
```bash
DEFAULT_MODEL=openai/gpt-4o
# 最高质量，成本较高
```

#### 🆓 免费测试
```bash
DEFAULT_MODEL=google/gemma-2-9b-it:free
# 完全免费，适合开发测试
```

## 🔧 技术集成

### 1. AI客户端配置

我们的项目已经预配置了OpenRouter客户端 (`app/utils/ai_client.py`)，支持：

- ✅ 兼容OpenAI SDK
- ✅ 自动故障转移
- ✅ 成本优化
- ✅ 流式响应
- ✅ 个性化宠物对话

### 2. 使用示例

```python
from app.utils.ai_client import OpenRouterClient

# 初始化客户端
client = OpenRouterClient()

# 生成宠物对话
response = await client.generate_pet_response(
    pet_name="小白",
    pet_personality="活泼可爱",
    user_message="你今天心情怎么样？",
    context="用户刚回家"
)

print(response)  # 小白的个性化回复
```

### 3. 环境配置检查

使用我们的测试脚本检查配置：

```bash
# 运行配置测试
python3 simple_test.py

# 或使用完整测试
python3 test_db_connection.py
```

## 📊 模型选择指南

### 按用途选择

| 用途 | 推荐模型 | 特点 | 成本 |
|------|----------|------|------|
| 日常对话 | `openai/gpt-3.5-turbo` | 快速、便宜 | 💰 |
| 智能助手 | `openai/gpt-4o-mini` | 平衡性能成本 | 💰💰 |
| 专业对话 | `openai/gpt-4o` | 最高质量 | 💰💰💰 |
| 开发测试 | `google/gemma-2-9b-it:free` | 免费 | 🆓 |
| 创意写作 | `anthropic/claude-3-haiku` | 创意强 | 💰💰 |

### 按语言优化

| 语言 | 推荐模型 | 说明 |
|------|----------|------|
| 中文 | `openai/gpt-4o` | 中文理解最佳 |
| 英文 | `anthropic/claude-3-sonnet` | 英文表达优秀 |
| 多语言 | `google/gemini-pro` | 多语言支持好 |

## 💡 最佳实践

### 1. 成本控制
```bash
# 设置每日使用限额
DAILY_USAGE_LIMIT=10.00  # 美元

# 使用免费模型进行开发
DEVELOPMENT_MODEL=google/gemma-2-9b-it:free
PRODUCTION_MODEL=openai/gpt-3.5-turbo
```

### 2. 性能优化
```bash
# 启用缓存减少重复请求
ENABLE_RESPONSE_CACHE=true
CACHE_TTL=3600  # 1小时

# 设置超时时间
REQUEST_TIMEOUT=30  # 秒
```

### 3. 安全配置
```bash
# API密钥安全
# ❌ 不要在代码中硬编码API密钥
# ✅ 使用环境变量
# ✅ 定期轮换密钥
# ✅ 监控使用情况
```

## 🔍 故障排除

### 常见问题

1. **API密钥无效**
   ```bash
   Error: Invalid API key
   ```
   - 检查 `.env` 文件中的 `OPENROUTER_API_KEY`
   - 确认密钥格式正确（以 `sk-or-v1-` 开头）
   - 验证密钥是否被撤销

2. **余额不足**
   ```bash
   Error: Insufficient credits
   ```
   - 登录OpenRouter查看余额
   - 充值账户或使用免费模型

3. **模型不可用**
   ```bash
   Error: Model not found
   ```
   - 检查模型名称拼写
   - 访问 [OpenRouter Models](https://openrouter.ai/models) 查看可用模型
   - 某些模型可能需要特定权限

4. **请求超时**
   ```bash
   Error: Request timeout
   ```
   - 增加 `REQUEST_TIMEOUT` 值
   - 检查网络连接
   - 尝试其他模型

### 测试连接

```bash
# 快速测试API连接
curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 📈 监控和分析

### 1. 使用情况监控
- 登录OpenRouter Dashboard查看：
  - 每日/每月使用量
  - 成本分析
  - 模型性能统计

### 2. 日志配置
```bash
# 启用详细日志
LOG_LEVEL=DEBUG
OPENROUTER_LOG_REQUESTS=true
```

## 🚀 快速开始

### 1. 完整配置示例

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env

# 添加以下配置：
OPENROUTER_API_KEY=your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-3.5-turbo
SITE_URL=http://localhost:3001
SITE_NAME=毛孩子AI
```

### 2. 验证配置
```bash
# 运行测试
python3 simple_test.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

### 3. 测试AI功能
访问 http://localhost:3001/docs 测试AI对话接口

---

## 📞 支持

- **OpenRouter文档**: https://openrouter.ai/docs
- **模型列表**: https://openrouter.ai/models  
- **价格信息**: https://openrouter.ai/models?tab=pricing
- **Discord社区**: https://discord.gg/openrouter

---

**配置完成后，您的毛孩子AI将拥有强大的多模型AI对话能力！** 🐾✨ 