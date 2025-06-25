# Passport Web 用户认证系统 API 文档

## 概述

Passport Web 是一个基于 Express.js 和 Passport.js 的用户认证系统，支持本地认证和 OAuth（Google、Facebook）登录。

### 基础信息
- **Base URL**: `http://localhost:3001`
- **Content-Type**: `application/json`
- **认证方式**: Session-based（Cookie）

## 🚀 快速开始

### 环境要求
- Node.js >= 16
- MySQL 数据库
- npm 或 yarn

### 安装配置
```bash
# 克隆项目
git clone <your-repo>
cd passport-web

# 安装后端依赖
cd backend
npm install

# 配置环境变量
cp ../env.example .env
# 编辑 .env 文件，设置数据库连接信息

# 启动服务
npm run dev
```

## 📋 API 接口

### 1. 健康检查

#### `GET /api/health`
检查服务器状态

**响应示例**:
```json
{
  "status": "OK",
  "message": "Server is running"
}
```

---

### 2. 用户认证

#### `POST /auth/register`
用户注册

**请求体**:
```json
{
  "username": "string (必需)",
  "password": "string (必需)"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "johndoe",
    "provider": "local"
  }
}
```

**错误响应** (400):
```json
{
  "success": false,
  "message": "用户名已存在"
}
```

#### `POST /auth/login`
用户登录

**请求体**:
```json
{
  "username": "string (必需)",
  "password": "string (必需)"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "message": "登录成功",
  "user": {
    "id": 1,
    "username": "johndoe",
    "provider": "local"
  }
}
```

**错误响应** (401):
```json
{
  "success": false,
  "message": "用户名不存在" // 或 "密码错误"
}
```

#### `POST /auth/logout`
用户登出

**成功响应** (200):
```json
{
  "success": true,
  "message": "登出成功"
}
```

---

### 3. OAuth 认证

#### `GET /auth/google`
Google OAuth 登录重定向

**功能**: 重定向用户到 Google 登录页面
**权限范围**: `profile`, `email`

#### `GET /auth/google/callback`
Google OAuth 回调处理

**功能**: 处理 Google 登录回调，成功后重定向到前端

#### `GET /auth/facebook`
Facebook OAuth 登录重定向

**功能**: 重定向用户到 Facebook 登录页面
**权限范围**: `email`

#### `GET /auth/facebook/callback`
Facebook OAuth 回调处理

**功能**: 处理 Facebook 登录回调，成功后重定向到前端

---

### 4. 用户信息

#### `GET /api/user`
获取当前登录用户信息（支持Session和Token两种认证方式）

**响应示例** (已认证):
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "provider": "local"
  },
  "authType": "token"
}
```

**响应示例** (未认证, 401):
```json
{
  "success": false,
  "message": "Not authenticated",
  "code": "NOT_AUTHENTICATED"
}
```

#### `POST /api/user/info`
根据AccessToken获取用户信息

**请求参数**:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例** (成功):
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "johndoe",
    "provider": "local",
    "email": "john@example.com",
    "displayName": "John Doe"
  },
  "tokenInfo": {
    "type": "access",
    "issuedAt": "2024-01-01T00:00:00.000Z",
    "expiresAt": "2024-01-01T01:00:00.000Z"
  }
}
```

**响应示例** (AccessToken缺失, 400):
```json
{
  "success": false,
  "message": "AccessToken是必需的",
  "code": "ACCESS_TOKEN_MISSING"
}
```

**响应示例** (Token无效, 401):
```json
{
  "success": false,
  "message": "无效的令牌类型",
  "code": "INVALID_TOKEN_TYPE"
}
```

**响应示例** (用户不存在, 404):
```json
{
  "success": false,
  "message": "用户不存在",
  "code": "USER_NOT_FOUND"
}
```

---

## 🔐 认证机制

### Session 认证
系统使用基于 Session 的认证机制：

1. **登录后**: 服务器设置 Session Cookie
2. **后续请求**: 客户端自动携带 Cookie
3. **权限检查**: 服务器验证 Session 有效性

### Cookie 配置
```javascript
{
  secure: false,      // HTTPS 环境设为 true
  maxAge: 24 * 60 * 60 * 1000,  // 24小时
  httpOnly: true,     // 仅服务器可访问
  sameSite: 'lax'     // CSRF 保护
}
```

---

## 📊 数据模型

### User 模型
```javascript
{
  id: "INTEGER (主键)",
  username: "STRING (唯一)",
  password: "STRING (加密存储)",
  provider: "STRING (local/google/facebook)",
  providerId: "STRING (OAuth用户ID)",
  email: "STRING (邮箱)",
  displayName: "STRING (显示名称)",
  createdAt: "DATETIME",
  updatedAt: "DATETIME"
}
```

---

## 🛠 客户端集成

### JavaScript/Fetch 示例

#### 注册用户
```javascript
async function registerUser(username, password) {
  const response = await fetch('http://localhost:3001/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // 重要：携带 Cookie
    body: JSON.stringify({ username, password })
  });
  
  return await response.json();
}
```

#### 登录用户
```javascript
async function loginUser(username, password) {
  const response = await fetch('http://localhost:3001/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });
  
  return await response.json();
}
```

#### 获取用户信息
```javascript
async function getCurrentUser() {
  const response = await fetch('http://localhost:3001/api/user', {
    credentials: 'include'
  });
  
  if (response.ok) {
    return await response.json();
  } else {
    throw new Error('Not authenticated');
  }
}
```

#### 登出
```javascript
async function logoutUser() {
  const response = await fetch('http://localhost:3001/auth/logout', {
    method: 'POST',
    credentials: 'include'
  });
  
  return await response.json();
}
```

### React 集成示例

#### 认证 Hook
```javascript
import { useState, useEffect, createContext, useContext } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const response = await fetch('http://localhost:3001/api/user', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  }

  const login = async (username, password) => {
    const response = await fetch('http://localhost:3001/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    if (data.success) {
      setUser(data.user);
    }
    return data;
  };

  const logout = async () => {
    await fetch('http://localhost:3001/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

---

## 🌐 OAuth 集成

### Google OAuth 配置

1. **创建 Google 应用**:
   - 访问 [Google Cloud Console](https://console.cloud.google.com/)
   - 创建项目并启用 Google+ API
   - 创建 OAuth 2.0 客户端 ID

2. **配置重定向 URI**:
   ```
   http://localhost:3001/auth/google/callback
   ```

3. **环境变量**:
   ```env
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

### Facebook OAuth 配置

1. **创建 Facebook 应用**:
   - 访问 [Facebook Developers](https://developers.facebook.com/)
   - 创建应用并配置 Facebook 登录

2. **配置重定向 URI**:
   ```
   http://localhost:3001/auth/facebook/callback
   ```

3. **环境变量**:
   ```env
   FACEBOOK_APP_ID=your-facebook-app-id
   FACEBOOK_APP_SECRET=your-facebook-app-secret
   ```

### 前端 OAuth 登录按钮
```javascript
function OAuthButtons() {
  const handleGoogleLogin = () => {
    window.location.href = 'http://localhost:3001/auth/google';
  };

  const handleFacebookLogin = () => {
    window.location.href = 'http://localhost:3001/auth/facebook';
  };

  return (
    <div>
      <button onClick={handleGoogleLogin}>
        使用 Google 登录
      </button>
      <button onClick={handleFacebookLogin}>
        使用 Facebook 登录
      </button>
    </div>
  );
}
```

---

## ⚠️ 错误处理

### 常见错误码

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 成功 | 登录成功 |
| 400 | 请求错误 | 用户名已存在 |
| 401 | 未认证 | 密码错误 |
| 500 | 服务器错误 | 数据库连接失败 |

### 错误响应格式
```json
{
  "success": false,
  "message": "具体错误信息",
  "code": "ERROR_CODE (可选)"
}
```

---

## 🔒 安全注意事项

### 1. CORS 配置
```javascript
app.use(cors({
  origin: 'http://localhost:5173', // 前端地址
  credentials: true // 允许携带 Cookie
}));
```

### 2. Session 安全
- 使用强随机密钥作为 SESSION_SECRET
- 生产环境设置 `secure: true`
- 配置合适的 Cookie 过期时间

### 3. 密码安全
- 使用 bcrypt 加密存储
- 密码强度要求（建议前端验证）

### 4. OAuth 安全
- 定期轮换 Client Secret
- 限制重定向 URI
- 验证 state 参数（防 CSRF）

---

## 📝 环境变量配置

### 必需变量
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=passport
DB_USER=root
DB_PASSWORD=your_password

# Session 密钥
SESSION_SECRET=your-secret-key-here

# 应用配置
PORT=3001
FRONTEND_URL=http://localhost:5173
```

### 可选变量（OAuth）
```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook OAuth
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# 代理配置（如需要）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

---

## 🚀 生产环境部署

### 1. 环境变量调整
```env
NODE_ENV=production
DB_HOST=your-production-db-host
SESSION_SECRET=very-strong-random-secret
FRONTEND_URL=https://yourdomain.com
```

### 2. Session 配置调整
```javascript
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,  // HTTPS 环境
    maxAge: 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'strict'
  }
}));
```

### 3. OAuth 重定向 URI 更新
- Google: `https://yourdomain.com/auth/google/callback`
- Facebook: `https://yourdomain.com/auth/facebook/callback`

---

## 📞 技术支持

如需技术支持或发现问题，请：
1. 查看日志文件
2. 检查环境变量配置
3. 确认数据库连接
4. 验证 OAuth 配置 