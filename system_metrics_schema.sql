-- 系统监控指标表
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

-- 插入示例数据（可选）
INSERT INTO system_metrics (metrics_id, timestamp, cpu_percent, memory_percent, memory_used, memory_total, disk_percent, disk_used, disk_total, tcp_connections, network_bytes_sent, network_bytes_recv, process_cpu_percent, process_memory_percent, process_memory_rss, uptime_seconds) VALUES 
(UUID(), NOW(), 25.5, 60.2, 8246339584, 137438953472, 45.8, 102341017600, 223384899584, 15, 12345678, 23456789, 5.2, 2.1, 12345678, 86400);