# 毛孩子AI - 后端API设计

## 📡 API基础信息

- **Base URL**: `https://your-backend-api.com/api/v1`
- **认证方式**: JWT Token
- **Content-Type**: `application/json`
- **响应格式**: JSON

## 🔐 认证相关

### 用户注册
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response:
{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "用户名",
    "email": "user@example.com",
    "token": "jwt_token_here",
    "avatar": null,
    "createdAt": "2023-12-01T00:00:00Z"
  }
}
```

### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}

Response:
{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "用户名",
    "email": "user@example.com",
    "token": "jwt_token_here",
    "avatar": "avatar_url",
    "createdAt": "2023-12-01T00:00:00Z"
  }
}
```

### 刷新Token
```http
POST /auth/refresh
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "token": "new_jwt_token_here"
  }
}
```

## 👤 用户管理

### 获取用户资料
```http
GET /user/profile
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "用户名",
    "email": "user@example.com",
    "avatar": "avatar_url",
    "createdAt": "2023-12-01T00:00:00Z",
    "updatedAt": "2023-12-01T00:00:00Z"
  }
}
```

### 更新用户资料
```http
PUT /user/profile
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "新用户名",
  "avatar": "new_avatar_url"
}

Response:
{
  "success": true,
  "data": {
    "id": "user_123",
    "username": "新用户名",
    "email": "user@example.com",
    "avatar": "new_avatar_url",
    "updatedAt": "2023-12-01T00:00:00Z"
  }
}
```

## 🐕 宠物管理

### 获取用户的宠物列表
```http
GET /pets/user/{userId}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": [
    {
      "id": "pet_123",
      "userId": "user_123",
      "name": "小白",
      "type": "dog",
      "breed": "金毛",
      "personality": "活泼可爱",
      "avatar": "pet_avatar_url",
      "birthday": "2020-01-01T00:00:00Z",
      "weight": 15.5,
      "healthStatus": "健康",
      "lastFeedTime": "2023-12-01T08:00:00Z",
      "lastWalkTime": "2023-12-01T07:00:00Z",
      "createdAt": "2023-01-01T00:00:00Z",
      "updatedAt": "2023-12-01T00:00:00Z"
    }
  ]
}
```

### 创建新宠物
```http
POST /pets
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "小白",
  "type": "dog",
  "breed": "金毛",
  "personality": "活泼可爱",
  "avatar": "pet_avatar_url",
  "birthday": "2020-01-01T00:00:00Z",
  "weight": 15.5,
  "healthStatus": "健康"
}

Response:
{
  "success": true,
  "data": {
    "id": "pet_123",
    "userId": "user_123",
    "name": "小白",
    "type": "dog",
    "breed": "金毛",
    "personality": "活泼可爱",
    "avatar": "pet_avatar_url",
    "birthday": "2020-01-01T00:00:00Z",
    "weight": 15.5,
    "healthStatus": "健康",
    "createdAt": "2023-12-01T00:00:00Z",
    "updatedAt": "2023-12-01T00:00:00Z"
  }
}
```

### 更新宠物信息
```http
PUT /pets/{petId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "小白",
  "personality": "活泼聪明",
  "weight": 16.0,
  "healthStatus": "健康",
  "lastFeedTime": "2023-12-01T09:00:00Z"
}
```

### 删除宠物
```http
DELETE /pets/{petId}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": true
}
```

## 📱 动态分享

### 获取动态列表
```http
GET /feeds?page=1&limit=20
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": [
    {
      "id": "feed_123",
      "petId": "pet_123",
      "userId": "user_123",
      "petName": "小白",
      "petAvatar": "pet_avatar_url",
      "userName": "主人昵称",
      "userAvatar": "user_avatar_url",
      "content": "今天和小白去公园玩了！",
      "images": ["image_url_1", "image_url_2"],
      "likes": 15,
      "comments": 3,
      "shares": 1,
      "isLiked": false,
      "mood": "开心",
      "topics": ["散步", "公园"],
      "location": "中央公园",
      "createdAt": "2023-12-01T10:00:00Z"
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 10,
    "totalItems": 200,
    "hasNext": true
  }
}
```

### 创建新动态
```http
POST /feeds
Authorization: Bearer {token}
Content-Type: application/json

{
  "petId": "pet_123",
  "content": "今天和小白去公园玩了！",
  "images": ["image_url_1", "image_url_2"],
  "mood": "开心",
  "topics": ["散步", "公园"],
  "location": "中央公园"
}

Response:
{
  "success": true,
  "data": {
    "id": "feed_123",
    "petId": "pet_123",
    "userId": "user_123",
    "content": "今天和小白去公园玩了！",
    "images": ["image_url_1", "image_url_2"],
    "likes": 0,
    "comments": 0,
    "shares": 0,
    "isLiked": false,
    "mood": "开心",
    "topics": ["散步", "公园"],
    "location": "中央公园",
    "createdAt": "2023-12-01T10:00:00Z"
  }
}
```

### 点赞/取消点赞
```http
POST /feeds/{feedId}/like
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "isLiked": true,
    "likesCount": 16
  }
}
```

### 删除动态
```http
DELETE /feeds/{feedId}
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": true
}
```

## 🤖 AI聊天

### 发送消息给AI
```http
POST /ai/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "你好，小白！",
  "petId": "pet_123",
  "petName": "小白",
  "petPersonality": "活泼可爱",
  "conversationHistory": [
    {
      "content": "昨天去散步了吗？",
      "type": "user"
    },
    {
      "content": "是的！我很喜欢散步！",
      "type": "pet",
      "mood": "开心"
    }
  ]
}

Response:
{
  "success": true,
  "data": {
    "reply": "主人好！我今天心情很好呢！",
    "mood": "开心",
    "confidence": 0.85,
    "actions": ["摇尾巴", "跳跃"],
    "emotions": ["开心", "兴奋"]
  }
}
```

### 获取聊天历史
```http
GET /chat/{petId}/history?page=1&limit=50
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": [
    {
      "id": "msg_123",
      "petId": "pet_123",
      "userId": "user_123",
      "content": "你好，小白！",
      "type": "user",
      "mood": null,
      "actions": [],
      "timestamp": "2023-12-01T10:00:00Z",
      "isRead": true
    },
    {
      "id": "msg_124",
      "petId": "pet_123",
      "userId": "user_123",
      "content": "主人好！我今天心情很好呢！",
      "type": "pet",
      "mood": "开心",
      "actions": ["摇尾巴"],
      "timestamp": "2023-12-01T10:00:05Z",
      "isRead": true
    }
  ]
}
```

### 保存聊天消息
```http
POST /chat/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "petId": "pet_123",
  "content": "你好，小白！",
  "type": "user",
  "mood": null,
  "actions": []
}

Response:
{
  "success": true,
  "data": {
    "id": "msg_123",
    "petId": "pet_123",
    "userId": "user_123",
    "content": "你好，小白！",
    "type": "user",
    "mood": null,
    "actions": [],
    "timestamp": "2023-12-01T10:00:00Z",
    "isRead": true
  }
}
```

## 📂 文件上传

### 上传图片
```http
POST /upload/image
Authorization: Bearer {token}
Content-Type: multipart/form-data

form-data:
- image: [file]
- type: "avatar" | "feed" | "pet"

Response:
{
  "success": true,
  "data": {
    "imageUrl": "https://cdn.example.com/images/uploaded_image.jpg",
    "thumbnailUrl": "https://cdn.example.com/images/uploaded_image_thumb.jpg"
  }
}
```

## 📊 统计数据

### 获取宠物统计
```http
GET /pets/{petId}/stats
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "totalFeeds": 25,
    "totalLikes": 150,
    "totalComments": 30,
    "totalChatMessages": 500,
    "lastActiveDate": "2023-12-01T10:00:00Z",
    "moodStats": {
      "开心": 60,
      "兴奋": 25,
      "平静": 10,
      "困倦": 5
    }
  }
}
```

## ❌ 错误响应格式

```json
{
  "success": false,
  "error": "错误类型",
  "message": "详细错误信息",
  "code": 400
}
```

## 🔄 实时功能 (WebSocket)

### 连接WebSocket
```
WSS /ws/chat/{petId}
Authorization: Bearer {token}
```

### 接收实时消息
```json
{
  "type": "ai_message",
  "data": {
    "content": "主人，我想你了！",
    "mood": "想念",
    "timestamp": "2023-12-01T10:00:00Z"
  }
}
```

### 发送实时消息
```json
{
  "type": "user_message",
  "data": {
    "content": "我也想你！",
    "timestamp": "2023-12-01T10:00:05Z"
  }
}
```

## 🚀 技术栈建议

### 后端框架选择
1. **Node.js + Express/Koa**
   - 优点：JavaScript全栈，开发速度快
   - AI集成：OpenAI SDK, Hugging Face
   
2. **Python + FastAPI/Django**
   - 优点：AI生态丰富，ML库众多
   - AI集成：OpenAI, Transformers, LangChain
   
3. **Go + Gin/Echo**
   - 优点：高性能，并发处理好
   - AI集成：HTTP调用外部AI服务

### 数据库选择
1. **PostgreSQL** - 主数据库
2. **Redis** - 缓存和会话
3. **MongoDB** - 聊天记录和日志

### AI服务集成
1. **OpenAI GPT-3.5/4** - 对话生成
2. **自训练模型** - 宠物个性化
3. **情感分析API** - 情绪识别

### 部署方案
1. **Docker + Kubernetes**
2. **AWS/阿里云/腾讯云**
3. **CDN** - 图片和静态资源

## 📈 扩展功能

### Phase 1 - 基础功能
- [x] 用户认证
- [x] 宠物管理
- [x] 基础AI对话
- [x] 动态分享

### Phase 2 - 增强功能
- [ ] 实时聊天
- [ ] 图片识别
- [ ] 语音消息
- [ ] 推送通知

### Phase 3 - 高级功能
- [ ] 宠物健康监控
- [ ] 社交网络
- [ ] AR/VR互动
- [ ] IoT设备集成 