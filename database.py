import os
import logging
import sqlite3
import uuid
from typing import Optional, Dict, Any, List

# 仅保留与监控相关的 SQLite 实现

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLiteManager:
    """SQLite 数据库管理类，专用于系统监控功能"""

    def __init__(self, db_path: str = 'monitoring.db'):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """确保数据库文件和表存在"""
        try:
            if not os.path.exists(self.db_path):
                logger.info(f"SQLite 数据库文件不存在，将创建新文件: {self.db_path}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查 system_metrics 表是否存在
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='system_metrics'
                """
            )

            if not cursor.fetchone():
                logger.info("system_metrics 表不存在，正在创建...")
                self._create_tables(cursor)
                conn.commit()
                logger.info("system_metrics 表创建成功")
            else:
                logger.info("SQLite 数据库和表已存在")

            conn.close()
        except Exception as e:
            logger.error(f"SQLite 数据库初始化失败: {str(e)}")
            raise

    def _create_tables(self, cursor):
        """创建数据库表"""
        cursor.execute(
            """
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
            )
            """
        )

        cursor.execute("CREATE INDEX idx_timestamp ON system_metrics(timestamp)")
        cursor.execute("CREATE INDEX idx_cpu_percent ON system_metrics(cpu_percent)")
        cursor.execute("CREATE INDEX idx_memory_percent ON system_metrics(memory_percent)")

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return result
        except Exception as e:
            logger.error(f"SQLite 查询执行失败: {str(e)}")
            raise

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            row_count = cursor.rowcount
            conn.close()
            return row_count
        except Exception as e:
            logger.error(f"SQLite 插入执行失败: {str(e)}")
            raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            row_count = cursor.rowcount
            conn.close()
            return row_count
        except Exception as e:
            logger.error(f"SQLite 更新执行失败: {str(e)}")
            raise

    def execute_delete(self, query: str, params: tuple = ()) -> int:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            row_count = cursor.rowcount
            conn.close()
            return row_count
        except Exception as e:
            logger.error(f"SQLite 删除执行失败: {str(e)}")
            raise


# 全局 SQLite 管理器实例
sqlite_manager = SQLiteManager()


class SystemMetricsSQLite:
    """基于 SQLite 的系统监控指标模型"""

    @staticmethod
    def create(metrics_data: Dict[str, Any]) -> str:
        metrics_id = str(uuid.uuid4())
        query = (
            """
            INSERT INTO system_metrics 
            (metrics_id, timestamp, cpu_percent, memory_percent, memory_used, memory_total, 
             disk_percent, disk_used, disk_total, tcp_connections, network_bytes_sent, network_bytes_recv,
             process_cpu_percent, process_memory_percent, process_memory_rss, uptime_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )

        params = (
            metrics_id,
            metrics_data.get('timestamp'),
            metrics_data.get('cpu', {}).get('cpu_percent'),
            metrics_data.get('memory', {}).get('virtual_memory', {}).get('percent'),
            metrics_data.get('memory', {}).get('virtual_memory', {}).get('used'),
            metrics_data.get('memory', {}).get('virtual_memory', {}).get('total'),
            metrics_data.get('disk', {}).get('disk_usage', {}).get('percent'),
            metrics_data.get('disk', {}).get('disk_usage', {}).get('used'),
            metrics_data.get('disk', {}).get('disk_usage', {}).get('total'),
            metrics_data.get('tcp_connections', {}).get('total_connections'),
            metrics_data.get('network', {}).get('network_io', {}).get('bytes_sent'),
            metrics_data.get('network', {}).get('network_io', {}).get('bytes_recv'),
            metrics_data.get('process', {}).get('cpu_percent'),
            metrics_data.get('process', {}).get('memory_percent'),
            metrics_data.get('process', {}).get('memory_info', {}).get('rss'),
            metrics_data.get('system_uptime', {}).get('uptime_seconds')
        )

        sqlite_manager.execute_insert(query, params)
        logger.info(f"监控数据已保存到 SQLite 数据库，ID: {metrics_id}")
        return metrics_id

    @staticmethod
    def get_latest() -> Optional[Dict[str, Any]]:
        query = (
            """
            SELECT * FROM system_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
        )
        result = sqlite_manager.execute_query(query)
        return result[0] if result else None

    @staticmethod
    def get_history(hours: int = 24) -> List[Dict[str, Any]]:
        query = (
            """
            SELECT * FROM system_metrics 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            """.format(hours)
        )
        return sqlite_manager.execute_query(query)

    @staticmethod
    def get_history_by_range(start_time: str, end_time: str) -> List[Dict[str, Any]]:
        query = (
            """
            SELECT * FROM system_metrics 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            """
        )
        return sqlite_manager.execute_query(query, (start_time, end_time))

    @staticmethod
    def cleanup_old_data(days_to_keep: int = 30) -> int:
        query = (
            """
            DELETE FROM system_metrics 
            WHERE timestamp < datetime('now', '-{} days')
            """.format(days_to_keep)
        )
        affected_rows = sqlite_manager.execute_delete(query)
        logger.info(f"清理了 {affected_rows} 条旧记录（保留 {days_to_keep} 天）")
        return affected_rows

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        query = (
            """
            SELECT 
                COUNT(*) as total_records,
                MIN(timestamp) as oldest_record,
                MAX(timestamp) as latest_record,
                AVG(cpu_percent) as avg_cpu_percent,
                AVG(memory_percent) as avg_memory_percent,
                AVG(disk_percent) as avg_disk_percent
            FROM system_metrics
            """
        )
        result = sqlite_manager.execute_query(query)
        return result[0] if result else {} 