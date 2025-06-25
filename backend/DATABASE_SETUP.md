# 毛孩子AI - 数据库配置文档

## 📊 数据库配置总结

### MySQL Docker 配置
- **容器名称**: `mysql-container`
- **MySQL版本**: 9.3.0
- **端口映射**: `3306:3306`
- **root密码**: `your_password`

### 项目专用数据库配置
- **数据库名**: `furry_kids`
- **用户名**: `furry_user`
- **密码**: `furry_password`
- **字符集**: `utf8mb4`
- **排序规则**: `utf8mb4_unicode_ci`

### 连接信息
```bash
# 使用项目用户连接
docker exec -it mysql-container mysql -u furry_user -pfurry_password

# 使用项目数据库
USE furry_kids;
```

### 权限配置
```sql
-- 已创建的数据库和用户
CREATE DATABASE IF NOT EXISTS furry_kids CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'furry_user'@'%' IDENTIFIED BY 'furry_password';
GRANT ALL PRIVILEGES ON furry_kids.* TO 'furry_user'@'%';
FLUSH PRIVILEGES;
```

## 🔧 环境变量配置

项目已配置的环境变量（`.env`文件）：

```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=furry_user
MYSQL_PASSWORD=furry_password
MYSQL_DATABASE=furry_kids

# 服务器配置
HOST=0.0.0.0
PORT=3001

# 其他配置...
```

## ✅ 验证状态

- ✅ MySQL Docker容器运行正常
- ✅ 数据库 `furry_kids` 创建成功
- ✅ 用户 `furry_user` 创建成功并具有完整权限
- ✅ 连接测试通过
- ✅ 环境变量配置完成
- ✅ 项目目录结构完整

## 🚀 下一步

1. **安装Python依赖**:
   ```bash
   source venv/bin/activate
   pip install fastapi uvicorn pymysql python-dotenv sqlalchemy alembic
   ```

2. **配置OpenRouter API密钥**:
   在 `.env` 文件中设置：
   ```env
   OPENROUTER_API_KEY=your-actual-api-key-here
   ```

3. **初始化数据库表结构**:
   ```bash
   # 生成迁移文件
   alembic revision --autogenerate -m "Initial migration"
   
   # 执行迁移
   alembic upgrade head
   ```

4. **启动开发服务器**:
   ```bash
   python scripts/dev.py start
   # 或
   uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
   ```

5. **访问API文档**:
   - Swagger UI: http://localhost:3001/docs
   - ReDoc: http://localhost:3001/redoc

## 🔍 故障排除

### 常见问题

1. **MySQL容器未运行**:
   ```bash
   docker start mysql-container
   ```

2. **连接被拒绝**:
   - 检查容器端口映射
   - 确认用户权限设置

3. **字符编码问题**:
   - 确保使用 `utf8mb4` 字符集
   - 检查连接字符串配置

### 检查命令

```bash
# 检查容器状态
docker ps | grep mysql

# 测试数据库连接
docker exec mysql-container mysql -u furry_user -pfurry_password -e "SELECT 1"

# 查看数据库
docker exec mysql-container mysql -u furry_user -pfurry_password -e "SHOW DATABASES;"

# 运行配置测试
python3 simple_test.py
```

---

**配置完成时间**: $(date)  
**状态**: ✅ 已完成并验证 