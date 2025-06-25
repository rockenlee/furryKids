# 毛孩子AI - 部署指南

## 🏗️ 架构概览

```
┌─────────────────┐    HTTPS     ┌─────────────────┐
│   iOS App       │ ────────────► │   后端API       │
│   (前端)        │              │   (Node.js)     │
└─────────────────┘              └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   数据库        │
                                 │ (PostgreSQL)    │
                                 └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   AI服务        │
                                 │  (OpenAI API)   │
                                 └─────────────────┘
```

## 🎯 部署方案对比

### 方案1: 云服务分离部署 (推荐)

#### 优点 ✅
- 高可用性和自动扩缩容
- 专业运维团队维护
- 安全性和备份保障
- 全球CDN加速

#### 成本 💰
- **小型应用**: $50-100/月
- **中型应用**: $200-500/月
- **大型应用**: $500+/月

#### 技术栈
```yaml
前端部署:
  - iOS App Store
  - TestFlight (测试)

后端部署:
  - Vercel/Railway (Node.js)
  - Heroku/DigitalOcean
  - AWS/阿里云/腾讯云

数据库:
  - Supabase (PostgreSQL)
  - MongoDB Atlas
  - AWS RDS

AI服务:
  - OpenAI API
  - Hugging Face
  - 自建AI服务
```

### 方案2: VPS自建部署

#### 优点 ✅
- 成本可控
- 完全控制权
- 学习价值高

#### 缺点 ❌
- 需要运维知识
- 安全性需自己保障
- 扩容需手动处理

#### 成本 💰
- **VPS服务器**: $10-30/月
- **域名**: $10-20/年
- **SSL证书**: 免费(Let's Encrypt)
- **总计**: $15-40/月

## 🚀 推荐部署方案

### 阶段1: 快速原型 (开发测试)

#### 后端部署: Vercel + Supabase
```bash
# 1. 创建Node.js项目
npm init -y
npm install express cors helmet morgan
npm install @supabase/supabase-js
npm install openai

# 2. 部署到Vercel
npm install -g vercel
vercel --prod

# 3. 配置环境变量
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
```

#### 数据库: Supabase (免费额度)
```sql
-- 在Supabase中创建表
-- 参考: API-Design.md中的PostgreSQL表结构
```

#### 前端配置
```swift
// 更新APIConfig
struct APIConfig {
    static let baseURL = "https://your-app.vercel.app/api/v1"
    static let openAIKey = "" // 留空，由后端处理
}
```

### 阶段2: 生产环境 (正式上线)

#### 后端部署: Railway/DigitalOcean
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
EXPOSE 3000

CMD ["npm", "start"]
```

#### 数据库: 托管PostgreSQL
```yaml
# railway.toml 或 docker-compose.yml
services:
  api:
    build: .
    environment:
      - DATABASE_URL=${{Postgres.DATABASE_URL}}
      - OPENAI_API_KEY=${{OPENAI_API_KEY}}
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=furryai
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD}}
```

## 📱 iOS端配置

### 开发环境配置
```swift
// APIConfig.swift
struct APIConfig {
    #if DEBUG
    static let baseURL = "http://localhost:3000/api/v1"
    #else
    static let baseURL = "https://your-production-api.com/api/v1"
    #endif
    
    static let timeout: TimeInterval = 30
    static let maxRetries = 3
}
```

### 网络安全配置
```xml
<!-- Info.plist -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSExceptionDomains</key>
    <dict>
        <key>your-api-domain.com</key>
        <dict>
            <key>NSExceptionRequiresForwardSecrecy</key>
            <false/>
        </dict>
    </dict>
</dict>
```

## 🔧 后端服务示例

### Node.js + Express 最小示例
```javascript
// server.js
const express = require('express');
const cors = require('cors');
const { createClient } = require('@supabase/supabase-js');
const OpenAI = require('openai');

const app = express();
const port = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());

// 初始化服务
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// 路由
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    
    if (error) throw error;
    
    res.json({
      success: true,
      data: {
        id: data.user.id,
        email: data.user.email,
        token: data.session.access_token,
      }
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      error: error.message,
    });
  }
});

app.post('/api/v1/ai/chat', async (req, res) => {
  try {
    const { message, petName, personality } = req.body;
    
    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: `你是一只名叫${petName}的${personality}宠物。用可爱、活泼的语气与主人交流。`
        },
        {
          role: "user",
          content: message
        }
      ],
      temperature: 0.8,
      max_tokens: 200,
    });
    
    const reply = completion.choices[0].message.content;
    
    res.json({
      success: true,
      data: {
        reply,
        mood: extractMood(reply),
        confidence: 0.8,
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

// 情绪提取函数
function extractMood(text) {
  if (text.includes('开心') || text.includes('高兴')) return '开心';
  if (text.includes('兴奋') || text.includes('激动')) return '兴奋';
  if (text.includes('累') || text.includes('困')) return '困倦';
  return '平静';
}

app.listen(port, () => {
  console.log(`服务器运行在端口 ${port}`);
});
```

### package.json
```json
{
  "name": "furryai-backend",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "@supabase/supabase-js": "^2.38.0",
    "openai": "^4.20.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

## 🌍 域名和SSL配置

### 域名购买和配置
```bash
# 1. 购买域名 (推荐)
# - Namecheap: $10-15/年
# - GoDaddy: $12-20/年
# - 阿里云: ¥50-100/年

# 2. DNS配置
# A记录: api.yourdomain.com -> 服务器IP
# CNAME: www.yourdomain.com -> yourdomain.com
```

### SSL证书 (免费)
```bash
# 使用Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d api.yourdomain.com
```

## 📊 监控和日志

### 基础监控
```javascript
// 添加到Express应用
const morgan = require('morgan');
app.use(morgan('combined'));

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});
```

### 错误追踪
```javascript
// 错误处理中间件
app.use((error, req, res, next) => {
  console.error('Error:', error);
  
  res.status(500).json({
    success: false,
    error: '服务器内部错误',
    message: process.env.NODE_ENV === 'development' ? error.message : undefined,
  });
});
```

## 🔒 安全配置

### 基础安全
```javascript
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// 安全头
app.use(helmet());

// 限流
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100, // 最多100个请求
});
app.use('/api/', limiter);

// CORS配置
app.use(cors({
  origin: ['https://yourdomain.com'],
  credentials: true,
}));
```

## 📈 扩容策略

### 水平扩容
```yaml
# docker-compose.yml
version: '3.8'
services:
  api-1:
    build: .
    environment:
      - NODE_ENV=production
  
  api-2:
    build: .
    environment:
      - NODE_ENV=production
  
  nginx:
    image: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 负载均衡
```nginx
# nginx.conf
upstream api_servers {
    server api-1:3000;
    server api-2:3000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## ✅ 部署检查清单

### 后端部署
- [ ] 选择云服务提供商
- [ ] 配置数据库
- [ ] 设置环境变量
- [ ] 配置域名和SSL
- [ ] 设置监控和日志
- [ ] 配置备份策略

### 前端配置
- [ ] 更新API端点配置
- [ ] 配置网络安全策略
- [ ] 测试API连接
- [ ] 配置错误处理
- [ ] 添加离线缓存

### 安全配置
- [ ] 启用HTTPS
- [ ] 配置CORS
- [ ] 添加请求限流
- [ ] 设置安全头
- [ ] 配置身份验证

## 🎯 快速开始

### 1分钟部署到Vercel
```bash
# 克隆后端模板
git clone https://github.com/your-username/furryai-backend
cd furryai-backend

# 安装依赖
npm install

# 部署
npx vercel --prod

# 配置环境变量
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
```

### iOS端配置
```swift
// 更新APIConfig.swift
struct APIConfig {
    static let baseURL = "https://your-app.vercel.app/api/v1"
}
```

就这样！你的应用就可以使用真实的后端服务了。

## 💡 最佳实践建议

1. **开始简单**: 先用Vercel + Supabase快速原型
2. **逐步升级**: 根据用户增长升级到专业服务
3. **监控优先**: 从第一天就添加监控和日志
4. **安全第一**: 始终使用HTTPS和适当的认证
5. **备份重要**: 定期备份数据库和配置 