# 系统监控功能说明

## 功能概述

本项目新增了系统监控功能，可以实时监控服务器的运行状态，包括CPU使用率、内存使用率、磁盘使用率、网络IO、TCP连接数等关键指标，并支持历史数据存储和查询。

## 主要功能

### 1. 实时监控指标
- **CPU信息**: 使用率、物理核心数、逻辑核心数、各核心使用率
- **内存信息**: 虚拟内存、交换内存的使用情况
- **磁盘信息**: 磁盘使用率、磁盘IO统计
- **网络信息**: 网络IO统计、连接数统计
- **TCP连接**: 总连接数、各状态连接数统计
- **进程信息**: 当前进程的CPU、内存使用情况
- **系统运行时间**: 系统启动时间和运行时长

### 2. 历史数据存储
- 监控数据定期存储到MySQL数据库
- 支持数据清理功能，避免数据无限增长
- 默认保留30天历史数据

### 3. 定时收集
- 内置调度器，支持自动定期收集监控数据
- 默认每60秒收集一次，可配置
- 支持启动/停止调度器

### 4. API端点

#### 获取当前系统状态
- **GET** `/monitor/current` - 获取当前系统监控指标

#### 获取历史数据
- **GET** `/monitor/latest` - 获取数据库中最新的监控数据
- **GET** `/monitor/history?hours=24` - 获取指定小时数的历史数据
- **GET** `/monitor/history/range?start_time=...&end_time=...` - 根据时间范围获取历史数据

#### 统计信息
- **GET** `/monitor/stats` - 获取系统统计信息（平均值、最大值、最小值等）

#### 手动操作
- **POST** `/monitor/collect` - 手动触发收集一次监控数据
- **POST** `/monitor/cleanup?days_to_keep=30` - 清理指定天数前的旧数据

#### 调度器管理
- **GET** `/monitor/scheduler/status` - 获取调度器状态
- **POST** `/monitor/scheduler/start` - 启动调度器
- **POST** `/monitor/scheduler/stop` - 停止调度器
- **POST** `/monitor/scheduler/configure?interval_seconds=60` - 配置调度器参数

## 数据库表结构

创建 `system_metrics` 表存储监控数据：

```sql
CREATE TABLE IF NOT EXISTS system_metrics (
    metrics_id VARCHAR(36) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_percent DECIMAL(5,2),
    memory_percent DECIMAL(5,2),
    memory_used BIGINT,
    memory_total BIGINT,
    disk_percent DECIMAL(5,2),
    disk_used BIGINT,
    disk_total BIGINT,
    tcp_connections INT,
    network_bytes_sent BIGINT,
    network_bytes_recv BIGINT,
    process_cpu_percent DECIMAL(5,2),
    process_memory_percent DECIMAL(5,2),
    process_memory_rss BIGINT,
    uptime_seconds BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_cpu_percent (cpu_percent),
    INDEX idx_memory_percent (memory_percent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 文件结构

- `system_monitor.py` - 系统监控核心模块
- `monitoring_scheduler.py` - 监控调度器
- `system_metrics_schema.sql` - 数据库表结构
- `models.py` - 数据模型（新增监控相关模型）
- `main.py` - API端点实现
- `database.py` - 数据库操作（新增SystemMetrics类）

## 依赖

新增依赖：
- `psutil==5.9.6` - 系统监控库

## 使用方法

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **创建数据库表**:
   ```bash
   mysql -u your_username -p your_database < system_metrics_schema.sql
   ```

3. **启动应用**:
   ```bash
   python main.py
   ```

4. **访问API文档**:
   启动后访问 `http://localhost:8000/docs` 查看完整的API文档

## 配置说明

- **监控间隔**: 默认60秒，可通过API或修改代码调整
- **数据保留**: 默认30天，可通过清理API调整
- **自动启动**: 应用启动时自动开始监控，关闭时自动停止

## 示例API调用

### 获取当前系统状态
```bash
curl http://localhost:8000/monitor/current
```

### 获取最近24小时历史数据
```bash
curl http://localhost:8000/monitor/history?hours=24
```

### 获取统计信息
```bash
curl http://localhost:8000/monitor/stats
```

### 手动收集数据
```bash
curl -X POST http://localhost:8000/monitor/collect
```

## 注意事项

1. 确保MySQL数据库已正确配置
2. 确保有足够的权限创建表和插入数据
3. 监控数据会占用一定的存储空间，定期清理旧数据
4. 在生产环境中，建议根据实际需求调整监控间隔和数据保留期限