# database.py
import os
import logging
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
from dotenv import load_dotenv
import ssl
from dbutils.pooled_db import PooledDB

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'cursorclass': DictCursor
}

# 根据环境添加SSL配置
# 如果是生产环境或者配置了SSL，则启用SSL连接
if os.getenv('APP_ENV') == 'production' or os.getenv('DB_SSL_ENABLED', 'false').lower() == 'true':
    # 创建SSL上下文
    ssl_context = ssl.create_default_context()
    # 对于腾讯云等云厂商，通常不需要验证主机名
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    DB_CONFIG['ssl'] = ssl_context
    logger.info("已启用数据库SSL连接")
else:
    logger.info("未启用数据库SSL连接（本地开发环境）")

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self._is_initialized = False
    
    def init_pool(self):
        """初始化数据库连接池"""
        try:
            logger.info("正在初始化数据库连接池...")
            logger.info(f"数据库配置: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, user={DB_CONFIG['user']}, db={DB_CONFIG['db']}")
            
            # 显示SSL状态
            if 'ssl' in DB_CONFIG:
                logger.info("SSL连接: 已启用")
            else:
                logger.info("SSL连接: 未启用")
            
            # 验证必要的环境变量
            if not all([DB_CONFIG['host'], DB_CONFIG['user'], DB_CONFIG['password'], DB_CONFIG['db']]):
                missing_vars = []
                if not DB_CONFIG['host']: missing_vars.append('DB_HOST')
                if not DB_CONFIG['user']: missing_vars.append('DB_USER')
                if not DB_CONFIG['password']: missing_vars.append('DB_PASSWORD')
                if not DB_CONFIG['db']: missing_vars.append('DB_NAME')
                
                error_msg = f"缺少必要的环境变量: {', '.join(missing_vars)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 创建连接池
            self.pool = PooledDB(
                creator=pymysql,
                maxconnections=10,  # 连接池最大连接数
                mincached=2,        # 初始化时创建的连接数
                maxcached=5,        # 连接池最大空闲连接数
                maxshared=3,        # 连接池最大共享连接数
                blocking=True,      # 连接池中如果没有可用连接后是否阻塞等待
                maxusage=None,      # 一个连接最多被重复使用的次数，None表示无限制
                **DB_CONFIG
            )
            
            self._is_initialized = True
            logger.info("数据库连接池初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {str(e)}")
            self.pool = None
            self._is_initialized = False
            raise e
    
    def close_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool = None
            self._is_initialized = False
            logger.info("数据库连接池已关闭")
    
    def _check_pool(self):
        """检查连接池状态"""
        if not self._is_initialized or self.pool is None:
            raise RuntimeError("数据库连接池未初始化，请检查数据库配置和网络连接")
    
    def execute_query(self, query: str, params: tuple = None):
        """执行查询语句"""
        self._check_pool()
        try:
            conn = self.pool.connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            raise e
    
    def execute_insert(self, query: str, params: tuple = None):
        """执行插入语句并返回插入的ID"""
        self._check_pool()
        try:
            conn = self.pool.connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.lastrowid
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"数据库插入失败: {str(e)}")
            raise e
    
    def execute_update(self, query: str, params: tuple = None):
        """执行更新语句并返回影响的行数"""
        self._check_pool()
        try:
            conn = self.pool.connection()
            try:
                with conn.cursor() as cursor:
                    result = cursor.execute(query, params)
                    return result
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"数据库更新失败: {str(e)}")
            raise e

# 全局数据库管理器实例
db_manager = DatabaseManager()

class ImageInformation:
    """图像信息模型"""
    
    @staticmethod
    def create(chatbot_id: str, file_name: str, file_type: str, 
                    file_size: int, asset_type: str, cos_url: str = None) -> str:
        """创建图像信息记录"""
        asset_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO image_information 
        (asset_id, chatbot_id, file_name, file_type, file_size, cos_url, asset_type, upload_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            asset_id, chatbot_id, file_name, file_type, file_size, 
            cos_url, asset_type, 'success' if cos_url else 'pending'
        )
        
        db_manager.execute_insert(query, params)
        return asset_id
    
    @staticmethod
    def update_cos_url(asset_id: str, cos_url: str):
        """更新COS URL"""
        query = """
        UPDATE image_information 
        SET cos_url = %s, upload_status = 'success', updated_at = NOW()
        WHERE asset_id = %s
        """
        
        db_manager.execute_update(query, (cos_url, asset_id))

class ChatbotInterface:
    """聊天界面配置模型"""
    
    @staticmethod
    def upsert(data: Dict[str, Any]) -> bool:
        """插入或更新聊天界面配置"""
        # 检查是否已存在
        check_query = "SELECT id FROM chatbot_interface WHERE chatbot_id = %s"
        existing = db_manager.execute_query(check_query, (data['chatbot_id'],))
        
        if existing:
            # 更新现有记录
            query = """
            UPDATE chatbot_interface SET
                display_name = %s,
                initial_messages = %s,
                suggested_message_1 = %s,
                suggested_message_2 = %s,
                suggested_message_3 = %s,
                suggested_message_4 = %s,
                message_placeholder = %s,
                footer_content = %s,
                theme = %s,
                user_message_color = %s,
                sync_header_color = %s,
                bubble_color = %s,
                bubble_position = %s,
                auto_open_seconds = %s,
                show_suggested_after_first_message = %s,
                collect_feedback = %s,
                allow_regeneration = %s,
                chatbot_icon_url = %s,
                bubble_icon_url = %s,
                updated_at = NOW()
            WHERE chatbot_id = %s
            """
            
            params = (
                data.get('display_name'),
                data.get('initial_messages'),
                data.get('suggested_message_1'),
                data.get('suggested_message_2'),
                data.get('suggested_message_3'),
                data.get('suggested_message_4'),
                data.get('message_placeholder'),
                data.get('footer_content'),
                data.get('theme'),
                data.get('user_message_color'),
                data.get('sync_header_color'),
                data.get('bubble_color'),
                data.get('bubble_position'),
                data.get('auto_open_seconds'),
                data.get('show_suggested_after_first_message'),
                data.get('collect_feedback'),
                data.get('allow_regeneration'),
                data.get('chatbot_icon_url'),
                data.get('bubble_icon_url'),
                data['chatbot_id']
            )
            
        else:
            # 插入新记录
            query = """
            INSERT INTO chatbot_interface (
                chatbot_id, display_name, initial_messages, suggested_message_1,
                suggested_message_2, suggested_message_3, suggested_message_4,
                message_placeholder, footer_content, theme, user_message_color,
                sync_header_color, bubble_color, bubble_position, auto_open_seconds,
                show_suggested_after_first_message, collect_feedback, allow_regeneration,
                chatbot_icon_url, bubble_icon_url
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            params = (
                data['chatbot_id'],
                data.get('display_name'),
                data.get('initial_messages'),
                data.get('suggested_message_1'),
                data.get('suggested_message_2'),
                data.get('suggested_message_3'),
                data.get('suggested_message_4'),
                data.get('message_placeholder'),
                data.get('footer_content'),
                data.get('theme'),
                data.get('user_message_color'),
                data.get('sync_header_color'),
                data.get('bubble_color'),
                data.get('bubble_position'),
                data.get('auto_open_seconds'),
                data.get('show_suggested_after_first_message'),
                data.get('collect_feedback'),
                data.get('allow_regeneration'),
                data.get('chatbot_icon_url'),
                data.get('bubble_icon_url')
            )
        
        db_manager.execute_update(query, params)
        return True
    
    @staticmethod
    def get_by_chatbot_id(chatbot_id: str) -> Optional[Dict[str, Any]]:
        """根据chatbot_id获取配置"""
        query = "SELECT * FROM chatbot_interface WHERE chatbot_id = %s"
        result = db_manager.execute_query(query, (chatbot_id,))
        return result[0] if result else None 

class SystemMetrics:
    """系统监控指标模型"""
    
    @staticmethod
    def create(metrics_data: Dict[str, Any]) -> str:
        """创建系统监控指标记录"""
        metrics_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO system_metrics 
        (metrics_id, timestamp, cpu_percent, memory_percent, memory_used, memory_total, 
         disk_percent, disk_used, disk_total, tcp_connections, network_bytes_sent, network_bytes_recv,
         process_cpu_percent, process_memory_percent, process_memory_rss, uptime_seconds)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
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
        
        db_manager.execute_insert(query, params)
        return metrics_id
    
    @staticmethod
    def get_latest() -> Optional[Dict[str, Any]]:
        """获取最新的系统指标"""
        query = """
        SELECT * FROM system_metrics 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        result = db_manager.execute_query(query)
        return result[0] if result else None
    
    @staticmethod
    def get_history(hours: int = 24) -> List[Dict[str, Any]]:
        """获取指定时间范围内的历史数据"""
        query = """
        SELECT * FROM system_metrics 
        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
        ORDER BY timestamp DESC
        """
        result = db_manager.execute_query(query, (hours,))
        return result
    
    @staticmethod
    def get_history_by_range(start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """根据时间范围获取历史数据"""
        query = """
        SELECT * FROM system_metrics 
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp DESC
        """
        result = db_manager.execute_query(query, (start_time, end_time))
        return result
    
    @staticmethod
    def cleanup_old_data(days_to_keep: int = 30) -> int:
        """清理指定天数前的旧数据"""
        query = """
        DELETE FROM system_metrics 
        WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        affected_rows = db_manager.execute_update(query, (days_to_keep,))
        return affected_rows


# ==================== SQLite数据库管理类 ====================

class SQLiteManager:
    """SQLite数据库管理类，专门用于系统监控功能"""
    
    def __init__(self, db_path: str = 'monitoring.db'):
        """
        初始化SQLite数据库管理器
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """确保数据库文件和表存在"""
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(self.db_path):
                logger.info(f"SQLite数据库文件不存在，将创建新文件: {self.db_path}")
            
            # 连接数据库并检查表是否存在
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查system_metrics表是否存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='system_metrics'
            """)
            
            if not cursor.fetchone():
                logger.info("system_metrics表不存在，正在创建...")
                self._create_tables(cursor)
                conn.commit()
                logger.info("system_metrics表创建成功")
            else:
                logger.info("SQLite数据库和表已存在")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"SQLite数据库初始化失败: {str(e)}")
            raise
    
    def _create_tables(self, cursor):
        """创建数据库表"""
        cursor.execute("""
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
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX idx_timestamp ON system_metrics(timestamp)")
        cursor.execute("CREATE INDEX idx_cpu_percent ON system_metrics(cpu_percent)")
        cursor.execute("CREATE INDEX idx_memory_percent ON system_metrics(memory_percent)")
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 启用字典行访问
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行查询操作"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # 将结果转换为字典列表
            result = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"SQLite查询执行失败: {str(e)}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """执行插入操作"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            row_count = cursor.rowcount
            conn.close()
            return row_count
            
        except Exception as e:
            logger.error(f"SQLite插入执行失败: {str(e)}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新操作"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            row_count = cursor.rowcount
            conn.close()
            return row_count
            
        except Exception as e:
            logger.error(f"SQLite更新执行失败: {str(e)}")
            raise
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """执行删除操作"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            row_count = cursor.rowcount
            conn.close()
            return row_count
            
        except Exception as e:
            logger.error(f"SQLite删除执行失败: {str(e)}")
            raise


# 全局SQLite数据库管理器实例
sqlite_manager = SQLiteManager()


class SystemMetricsSQLite:
    """基于SQLite的系统监控指标模型"""
    
    @staticmethod
    def create(metrics_data: Dict[str, Any]) -> str:
        """创建系统监控指标记录"""
        metrics_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO system_metrics 
        (metrics_id, timestamp, cpu_percent, memory_percent, memory_used, memory_total, 
         disk_percent, disk_used, disk_total, tcp_connections, network_bytes_sent, network_bytes_recv,
         process_cpu_percent, process_memory_percent, process_memory_rss, uptime_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
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
        logger.info(f"监控数据已保存到SQLite数据库，ID: {metrics_id}")
        return metrics_id
    
    @staticmethod
    def get_latest() -> Optional[Dict[str, Any]]:
        """获取最新的系统指标"""
        query = """
        SELECT * FROM system_metrics 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        result = sqlite_manager.execute_query(query)
        return result[0] if result else None
    
    @staticmethod
    def get_history(hours: int = 24) -> List[Dict[str, Any]]:
        """获取指定时间范围内的历史数据"""
        query = """
        SELECT * FROM system_metrics 
        WHERE timestamp >= datetime('now', '-{} hours')
        ORDER BY timestamp DESC
        """.format(hours)
        
        result = sqlite_manager.execute_query(query)
        return result
    
    @staticmethod
    def get_history_by_range(start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """根据时间范围获取历史数据"""
        query = """
        SELECT * FROM system_metrics 
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
        """
        result = sqlite_manager.execute_query(query, (start_time, end_time))
        return result
    
    @staticmethod
    def cleanup_old_data(days_to_keep: int = 30) -> int:
        """清理指定天数前的旧数据"""
        query = """
        DELETE FROM system_metrics 
        WHERE timestamp < datetime('now', '-{} days')
        """.format(days_to_keep)
        
        affected_rows = sqlite_manager.execute_delete(query)
        logger.info(f"清理了 {affected_rows} 条旧记录（保留 {days_to_keep} 天）")
        return affected_rows
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取数据库统计信息"""
        query = """
        SELECT 
            COUNT(*) as total_records,
            MIN(timestamp) as oldest_record,
            MAX(timestamp) as latest_record,
            AVG(cpu_percent) as avg_cpu_percent,
            AVG(memory_percent) as avg_memory_percent,
            AVG(disk_percent) as avg_disk_percent
        FROM system_metrics
        """
        
        result = sqlite_manager.execute_query(query)
        return result[0] if result else {} 