# 部署指南 - 解决 SSL 连接问题

## 🚨 重要：腾讯云数据库 SSL 连接配置

根据 `fix.md` 文件的分析，腾讯云数据库强制要求所有来自公网的连接都必须使用 SSL/TLS 加密。本项目已经针对此问题进行了优化。

## 🔧 修改内容

### 1. 数据库连接优化
- ✅ 添加了 SSL 支持
- ✅ 根据环境变量自动启用/禁用 SSL
- ✅ 兼容本地开发和生产环境

### 2. 环境变量配置
新增了以下环境变量：
- `DB_SSL_ENABLED`: 控制是否启用 SSL 连接
- `APP_ENV`: 环境标识，生产环境自动启用 SSL

## 🚀 Vercel 部署配置

### 步骤 1: 设置环境变量
在 Vercel 项目设置中添加以下环境变量：

```bash
# 数据库配置
DB_HOST=your_tencent_cloud_host
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# 🔐 SSL 配置（关键）
DB_SSL_ENABLED=true
APP_ENV=production

# 腾讯云 COS 配置
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=ap-hongkong
COS_BUCKET=your_bucket_name
COS_SCHEME=https
```

### 步骤 2: 部署验证
1. 部署后访问 `/health` 端点检查数据库连接
2. 查看 Vercel 函数日志，确认 SSL 连接状态

## 🏠 本地开发配置

### 选项 1: 本地不使用 SSL（推荐）
```bash
# .env 文件
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_local_username
DB_PASSWORD=your_local_password
DB_NAME=your_local_database
DB_SSL_ENABLED=false
APP_ENV=development
```

### 选项 2: 本地也使用 SSL
```bash
# .env 文件
DB_HOST=your_tencent_cloud_host
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name
DB_SSL_ENABLED=true
APP_ENV=development
```

## 📋 问题排查

### 1. 检查日志
启动应用后查看日志中的以下信息：
- `已启用数据库SSL连接` - 确认 SSL 已启用
- `数据库连接池初始化成功` - 确认连接成功

### 2. 健康检查
访问 `/health` 端点：
```bash
curl https://your-app.vercel.app/health
```

成功响应：
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "database_test": 1
}
```

### 3. 常见错误
- **Connection timed out**: 通常是 SSL 配置问题
- **Access denied**: 数据库用户名/密码错误
- **Unknown database**: 数据库名称错误

## 🔍 技术细节

### SSL 配置逻辑
```python
# 自动检测是否需要启用 SSL
if os.getenv('APP_ENV') == 'production' or os.getenv('DB_SSL_ENABLED', 'false').lower() == 'true':
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    DB_CONFIG['ssl'] = ssl_context
```

### 为什么这样配置？
1. **生产环境自动启用**: `APP_ENV=production` 时自动启用 SSL
2. **手动控制**: 通过 `DB_SSL_ENABLED` 手动控制
3. **云厂商兼容**: 设置 `check_hostname=False` 和 `verify_mode=ssl.CERT_NONE` 适配腾讯云等云厂商

## 📝 验证清单

部署前请确认：
- [ ] 已在 Vercel 中设置 `DB_SSL_ENABLED=true`
- [ ] 已在 Vercel 中设置 `APP_ENV=production`
- [ ] 数据库连接信息正确
- [ ] 腾讯云 COS 配置正确
- [ ] `/health` 端点返回正常

## 🎯 预期结果

修复后，你应该能够：
1. ✅ 本地开发正常运行
2. ✅ Vercel 部署成功连接数据库
3. ✅ 图像上传到腾讯云 COS 正常
4. ✅ 所有 API 端点正常工作 