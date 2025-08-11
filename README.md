# Server Monitor

一个基于 FastAPI 的服务器监控系统，提供实时系统监控、历史数据存储和可视化 Web 界面。

## ✨ 主要功能

### 🔍 实时监控
- **CPU 监控**: 使用率、核心数、各核心状态
- **内存监控**: 虚拟内存、交换内存使用情况
- **磁盘监控**: 使用率、IO 统计
- **网络监控**: 流量统计、连接数
- **TCP 连接**: 各状态连接数统计
- **进程监控**: 当前进程资源使用情况
- **系统信息**: 运行时间、启动时间

### 📊 数据管理
- **自动收集**: 可配置的定时数据收集（默认 60 秒）
- **历史存储**: SQLite 数据库存储历史数据
- **数据查询**: 支持时间范围查询
- **统计分析**: 提供平均值、最大值、最小值等统计信息
- **数据清理**: 自动清理过期数据（默认保留 30 天）

### 🌐 Web 界面
- **实时仪表板**: 现代化的监控界面
- **历史图表**: 数据可视化展示
- **调度器管理**: 启动/停止监控任务
- **手动操作**: 手动收集数据、清理数据

### 🔧 API 接口
- **RESTful API**: 完整的 REST API 接口
- **实时数据**: 获取当前系统状态
- **历史数据**: 查询历史监控数据
- **统计信息**: 获取系统性能统计
- **调度器控制**: 管理监控任务

## 🖥️ 支持环境

### 操作系统
- ✅ **Linux** (Ubuntu, CentOS, Debian 等)
- ✅ **macOS** (10.13+)
- ✅ **Windows** (10/11)

### Python 版本
- ✅ **Python 3.8+**
- ✅ **Python 3.9+**
- ✅ **Python 3.10+**
- ✅ **Python 3.11+**
- ✅ **Python 3.12+**（推荐）

### 部署方式
- ✅ **本地部署**


## 🚀 快速开始

### 环境要求
- Python 3.12
- uv

### 1. 克隆项目
```bash
git clone <repository-url>
cd server-monitor
```

### 2. 创建虚拟环境
```bash
uv init
uv venv
# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 3. 安装依赖
```bash
uv add -r requirements.txt
```

### 4. 运行应用

#### 方式一：使用脚本（推荐）
```bash
# 启动应用
./start.sh

# 查看状态
./status.sh

# 停止应用
./stop.sh

# 查看日志
./logs.sh
```

#### 方式二：直接运行
```bash
# 使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 或使用 python
python main.py
```


### 5. 访问应用
- **Web 监控界面**: http://localhost:8000/monitor
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health



## 🔧 配置说明

### 环境变量
```bash
# 监控间隔（秒）
MONITORING_INTERVAL=60

# 数据保留天数
DATA_RETENTION_DAYS=30

# 日志级别
LOG_LEVEL=INFO

# 绑定地址
HOST=0.0.0.0

# 端口
PORT=8000
```

### 配置文件
主要配置在 `main.py` 中：
- CORS 配置
- 监控间隔
- 数据保留策略

## 📊 API 文档

### 主要端点

#### 系统监控
- `GET /monitor/current` - 获取当前系统状态
- `GET /monitor/latest` - 获取最新监控数据
- `GET /monitor/history?hours=24` - 获取历史数据
- `GET /monitor/stats` - 获取统计信息

#### 调度器管理
- `GET /monitor/scheduler/status` - 获取调度器状态
- `POST /monitor/scheduler/start` - 启动调度器
- `POST /monitor/scheduler/stop` - 停止调度器
- `POST /monitor/scheduler/configure` - 配置调度器

#### 数据操作
- `POST /monitor/collect` - 手动收集数据
- `POST /monitor/cleanup` - 清理旧数据

### 示例请求
```bash
# 获取当前系统状态
curl http://localhost:8000/monitor/current

# 获取最近24小时历史数据
curl http://localhost:8000/monitor/history?hours=24

# 获取统计信息
curl http://localhost:8000/monitor/stats
```

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t server-monitor .
```

### 运行容器
```bash
docker run -d \
  --name server-monitor \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  server-monitor
```

### Docker Compose
```yaml
version: '3.8'
services:
  server-monitor:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## ☁️ 云部署

### Vercel 部署
项目已配置 `vercel.json`，可以直接部署到 Vercel：

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

## 🛠️ 开发指南

### 项目结构
```
server-monitor/
├── main.py                 # 主应用入口
├── system_monitor.py      # 系统监控核心
├── database.py            # 数据库操作
├── models.py              # 数据模型
├── monitoring_scheduler.py # 监控调度器
├── requirements.txt       # 依赖列表
├── vercel.json           # Vercel 配置
├── static/
│   └── monitor.html      # Web 监控界面
├── start.sh              # 启动脚本
├── stop.sh               # 停止脚本
├── status.sh             # 状态脚本
└── logs.sh               # 日志脚本
```

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd server-monitor

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload
```

## 🐛 故障排除

### 常见问题

#### 1. 权限问题
```bash
# Linux/macOS 上可能需要权限
sudo chmod +x *.sh
```

#### 2. 端口占用
```bash
# 查看端口占用
lsof -i :8000

# 或使用其他端口
uvicorn main:app --port 8001
```

#### 3. 数据库问题
```bash
# 删除数据库文件重新创建
rm -f monitoring.db
```

#### 4. 依赖问题
```bash
# 更新 pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 📈 性能优化

### 监控间隔调整
根据服务器性能调整监控间隔：
- 高性能服务器: 30 秒
- 一般服务器: 60 秒（默认）
- 低性能服务器: 120 秒

### 数据清理策略
- 生产环境: 保留 7-30 天
- 开发环境: 保留 3-7 天
- 测试环境: 保留 1-3 天

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：
- 创建 Issue
- 发送邮件
- 提交 Pull Request

---

**⭐ 如果这个项目对您有帮助，请给个 star！**