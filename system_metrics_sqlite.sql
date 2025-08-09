-- SQLite数据库创建脚本
-- 系统监控指标表

-- 删除已存在的表（如果存在）
DROP TABLE IF EXISTS system_metrics;

-- 创建系统监控指标表
CREATE TABLE system_metrics (
    metrics_id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    cpu_percent REAL,
    memory_percent REAL,
    memory_used INTEGER,
    memory_total INTEGER,
    disk_percent REAL,
    disk_used INTEGER,
    disk_total INTEGER,
    tcp_connections INTEGER,
    network_bytes_sent INTEGER,
    network_bytes_recv INTEGER,
    process_cpu_percent REAL,
    process_memory_percent REAL,
    process_memory_rss INTEGER,
    uptime_seconds INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX idx_timestamp ON system_metrics(timestamp);
CREATE INDEX idx_cpu_percent ON system_metrics(cpu_percent);
CREATE INDEX idx_memory_percent ON system_metrics(memory_percent);

-- 插入示例数据（可选）
INSERT INTO system_metrics (metrics_id, timestamp, cpu_percent, memory_percent, memory_used, memory_total, disk_percent, disk_used, disk_total, tcp_connections, network_bytes_sent, network_bytes_recv, process_cpu_percent, process_memory_percent, process_memory_rss, uptime_seconds) VALUES 
('550e8400-e29b-41d4-a716-446655440000', datetime('now'), 25.5, 60.2, 8246339584, 137438953472, 45.8, 102341017600, 223384899584, 15, 12345678, 23456789, 5.2, 2.1, 12345678, 86400);