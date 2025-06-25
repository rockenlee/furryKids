# 毛孩子AI - iOS应用设置指南

## 概述

毛孩子AI是一个iOS原生应用，为宠物主人提供AI互动陪伴体验。现已集成用户认证系统，支持用户注册、登录和个人档案管理。

## 功能特性

### 🔐 用户认证系统
- **本地账户注册/登录**：支持用户名密码认证
- **会话管理**：基于Cookie的会话保持
- **账户安全**：密码加密存储，安全登出
- **OAuth支持**：预留Google和Facebook第三方登录接口

### 🐾 核心功能
1. **宠物主页（Profile）**：展示宠物信息、等级系统、性格标签
2. **动态分享（Feed）**：社交动态流，点赞评论分享
3. **AI互动（Interaction）**：智能聊天，语音播报，情感表达
4. **用户中心**：个人信息管理，登出功能

## 技术架构

### 前端技术栈
- **UI框架**：SwiftUI
- **状态管理**：Combine + ObservableObject
- **网络通信**：URLSession + Combine
- **语音功能**：AVFoundation (TTS)

### 后端集成
- **API基础URL**：`http://localhost:3001`
- **认证方式**：Session-based (Cookie)
- **数据格式**：JSON

## 环境要求

### 开发环境
- Xcode 14.0+
- iOS 15.0+
- macOS 12.0+

### 运行环境
- iOS 15.0+
- 网络连接（访问本地后端服务）

## 安装配置

### 1. 克隆项目
```bash
cd /path/to/your/workspace
# 项目已在 FurryKids 目录中
```

### 2. 后端服务设置
```bash
# 确保后端服务运行在 localhost:3001
# 参考 api-documentation.md 启动后端服务
```

### 3. 打开iOS项目
```bash
cd FurryKids
open FurryKids.xcodeproj
```

### 4. 配置网络权限
项目已配置Info.plist允许访问localhost HTTP服务：
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>localhost</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

## 使用说明

### 首次启动
1. 应用启动后显示登录界面
2. 点击"测试服务器连接"验证后端服务状态
3. 选择注册新账户或使用已有账户登录

### 用户注册
1. 在登录界面点击"没有账户？点击注册"
2. 输入用户名和密码
3. 点击"注册"按钮
4. 注册成功后自动登录并进入主应用

### 用户登录
1. 输入已注册的用户名和密码
2. 点击"登录"按钮
3. 登录成功后进入主应用界面

### 主应用导航
- **首页**：浏览宠物动态，点赞评论
- **聊天**：与AI宠物互动聊天
- **宠物**：查看和管理宠物档案
- **我的**：用户个人中心，查看账户信息，登出

### 用户登出
1. 切换到"我的"标签页
2. 点击"登出"按钮
3. 确认登出操作
4. 返回登录界面

## API集成

### 认证相关接口

#### 用户注册
```
POST /auth/register
Content-Type: application/json

{
    "username": "用户名",
    "password": "密码"
}
```

#### 用户登录
```
POST /auth/login
Content-Type: application/json

{
    "username": "用户名", 
    "password": "密码"
}
```

#### 获取用户信息
```
GET /api/user
Cookie: session_cookie
```

#### 用户登出
```
POST /auth/logout
Cookie: session_cookie
```

#### 健康检查
```
GET /api/health
```

### 响应格式
```json
{
    "success": true,
    "message": "操作成功",
    "user": {
        "id": 1,
        "username": "testuser",
        "provider": "local",
        "email": null,
        "displayName": null
    }
}
```

## 文件结构

```
FurryKids/
├── Models/
│   ├── User.swift              # 用户数据模型
│   ├── Pet.swift               # 宠物数据模型
│   ├── Feed.swift              # 动态数据模型
│   └── Message.swift           # 消息数据模型
├── Services/
│   ├── AuthService.swift       # 认证服务
│   ├── AIService.swift         # AI服务
│   ├── DataService.swift       # 数据服务
│   └── NetworkManager.swift    # 网络管理
├── Stores/
│   ├── AuthStore.swift         # 认证状态管理
│   ├── InteractionStore.swift  # 互动状态管理
│   └── (其他Store文件)
├── Views/
│   ├── LoginView.swift         # 登录界面
│   ├── UserProfileView.swift   # 用户个人中心
│   ├── FeedView.swift          # 动态页面
│   ├── InteractionView.swift   # 聊天页面
│   ├── ProfileView.swift       # 宠物档案页面
│   └── CreateFeedView.swift    # 发布动态
├── Utilities/
│   ├── Color+Extensions.swift  # 颜色扩展
│   └── SpeechHelper.swift      # 语音助手
└── FurryKidsApp.swift          # 应用入口
```

## 故障排除

### 网络连接问题
1. **无法连接服务器**
   - 确认后端服务运行在localhost:3001
   - 检查防火墙和网络设置
   - 使用"测试服务器连接"功能验证

2. **认证失败**
   - 检查用户名密码是否正确
   - 确认后端数据库连接正常
   - 查看应用日志和后端日志

### 应用崩溃
1. **启动崩溃**
   - 检查iOS版本兼容性
   - 清除应用数据重新安装
   - 查看Xcode控制台错误信息

2. **网络请求失败**
   - 检查Info.plist网络配置
   - 确认模拟器/设备网络连接
   - 验证API端点可访问性

## 开发调试

### Xcode调试
1. 设置断点调试网络请求
2. 使用Console查看日志输出
3. 网络调试使用Instruments

### 网络调试
```bash
# 检查后端服务状态
curl http://localhost:3001/api/health

# 测试登录接口
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

## 扩展功能

### OAuth登录集成
1. 在Google/Facebook开发者平台注册应用
2. 配置OAuth回调URL
3. 实现OAuth登录流程
4. 更新Info.plist URL Schemes

### 推送通知
1. 配置APNs证书
2. 集成推送通知SDK
3. 实现消息推送功能

### 数据持久化
1. 使用Core Data存储本地数据
2. 实现离线模式支持
3. 数据同步机制

## 参考文档

- [API文档](../api-documentation.md)
- [部署指南](./DEPLOYMENT-GUIDE.md)
- [服务器集成指南](./SERVER-INTEGRATION-GUIDE.md)

## 支持联系

如遇问题，请检查：
1. 后端服务是否正常运行
2. 网络配置是否正确
3. iOS版本是否兼容
4. 参考故障排除章节

---

© 2024 毛孩子AI团队. 保留所有权利. 