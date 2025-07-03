## 运行

启动开发服务器：
```bash
source .venv/bin/activate
uvicorn main:app --reload 
```


# Chatbot Settings API

基于 FastAPI 的聊天机器人设置管理后端，支持图像上传到腾讯云 COS 和数据库存储。

## 功能特性

- 🎨 **聊天界面设置管理**: 完整的聊天界面配置保存和获取
- 📸 **图像上传**: 自动上传图像到腾讯云 COS
- 🗄️ **数据库集成**: MySQL 数据库存储配置和图像信息
- 📊 **分析数据**: 提供聊天分析数据接口
- 🔄 **异步处理**: 高性能异步数据库操作
- 📝 **API 文档**: 自动生成的 Swagger 文档

## 项目结构

```
Reference/
├── main.py              # 主应用文件
├── database.py          # 数据库配置和模型
├── cos_service.py       # 腾讯云 COS 上传服务
├── models.py            # Pydantic 数据模型
├── requirements.txt     # Python 依赖
├── env.example          # 环境变量示例
└── README.md           # 项目说明
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境配置

复制环境变量示例文件并配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，填写正确的配置：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# 腾讯云 COS 配置
COS_SECRET_ID=your_secret_id
COS_SECRET_KEY=your_secret_key
COS_REGION=ap-hongkong
COS_BUCKET=your_bucket_name
COS_SCHEME=https

# 应用配置
APP_ENV=development
DEBUG=True
```

### 3. 数据库初始化

创建必要的数据库表：

```sql
-- 图像信息表
CREATE TABLE `image_information` (
   `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
   `asset_id` VARCHAR(36) NOT NULL UNIQUE,
   `chatbot_id` VARCHAR(36) NOT NULL,
   `file_name` VARCHAR(255) NOT NULL,
   `file_type` VARCHAR(50) NOT NULL,
   `file_size` INT UNSIGNED NOT NULL,
   `cos_url` VARCHAR(512) NULL,
   `asset_type` ENUM('bubble_icon', 'chatbot_icon') NOT NULL,
   `upload_status` ENUM('pending', 'uploading', 'success', 'failed') NOT NULL DEFAULT 'pending',
   `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (`id`)
);

-- 聊天界面配置表
CREATE TABLE `chatbot_interface` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `chatbot_id` VARCHAR(36) NOT NULL UNIQUE,
    `status` ENUM('active', 'inactive', 'archived') NOT NULL DEFAULT 'active',
    `display_name` VARCHAR(100),
    `initial_messages` TEXT,
    `suggested_message_1` VARCHAR(200),
    `suggested_message_2` VARCHAR(200),
    `suggested_message_3` VARCHAR(200),
    `suggested_message_4` VARCHAR(200),
    `message_placeholder` VARCHAR(200),
    `footer_content` TEXT,
    `theme` ENUM('light', 'dark') NOT NULL DEFAULT 'light',
    `user_message_color` VARCHAR(50) DEFAULT '#3B82F6',
    `sync_header_color` BOOLEAN DEFAULT FALSE,
    `bubble_color` VARCHAR(50) DEFAULT '#3B82F6',
    `bubble_position` ENUM('left', 'right') NOT NULL DEFAULT 'right',
    `auto_open_seconds` INT DEFAULT 0,
    `show_suggested_after_first_message` BOOLEAN DEFAULT FALSE,
    `collect_feedback` BOOLEAN DEFAULT FALSE,
    `allow_regeneration` BOOLEAN DEFAULT FALSE,
    `chatbot_icon_url` VARCHAR(255) NULL,
    `bubble_icon_url` VARCHAR(255) NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
);
```

## 运行应用

### 开发模式

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 接口

### 1. 更新聊天界面设置

**POST** `/settings/update_chat_interface`

包含图像上传和设置保存的统一接口。

**请求体示例**:
```json
{
  "chatbot_id": "cb_12345",
  "display_name": "我的聊天机器人",
  "theme": "light",
  "chatbot_icon_data": {
    "asset_type": "chatbot_icon",
    "file_data": "data:image/jpeg;base64,...",
    "file_name": "avatar.jpg",
    "file_type": "image/jpeg",
    "file_size": 1024000
  },
  "bubble_icon_data": {
    "asset_type": "bubble_icon", 
    "file_data": "data:image/png;base64,...",
    "file_name": "bubble.png",
    "file_type": "image/png",
    "file_size": 512000
  }
}
```

**响应示例**:
```json
{
  "status": 200,
  "message": "聊天界面设置保存成功",
  "chatbot_icon_url": "https://bucket.cos.region.myqcloud.com/path/to/avatar.jpg",
  "bubble_icon_url": "https://bucket.cos.region.myqcloud.com/path/to/bubble.png"
}
```

### 2. 获取聊天界面设置

**GET** `/settings/chat_interface/{chatbot_id}`

### 3. 分析数据

**GET** `/analytics/data`

## 图像上传流程

1. **前端压缩**: 前端使用 canvas 压缩图像为 base64
2. **API 调用**: 发送包含图像数据的请求到后端
3. **图像上传**: 后端解码 base64 并上传到 COS
4. **数据库保存**: 保存图像信息和配置到数据库
5. **返回 URL**: 返回最终的 COS URL 给前端

## 开发说明

### 数据库模型

- **ImageInformation**: 管理上传的图像信息
- **ChatbotInterface**: 管理聊天界面配置

### COS 服务

- 自动生成唯一文件名
- 支持多种图像格式
- 错误处理和重试机制

### API 文档

启动应用后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 错误处理

- 图像上传失败会返回详细错误信息
- 数据库操作失败会自动回滚
- 所有错误都有相应的 HTTP 状态码

## 性能优化

- 使用异步数据库连接池
- 图像上传后自动清理临时文件
- 支持并发请求处理

## 安全考虑

- 文件类型验证
- 文件大小限制
- SQL 注入防护
- CORS 配置 