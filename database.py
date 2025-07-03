# database.py
import os
import asyncio
import aiomysql
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv
import logging
import ssl

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
    'autocommit': True
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
    
    async def init_pool(self):
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
            
            self.pool = await aiomysql.create_pool(**DB_CONFIG)
            self._is_initialized = True
            logger.info("数据库连接池初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {str(e)}")
            self.pool = None
            self._is_initialized = False
            raise e
    
    async def close_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self._is_initialized = False
            logger.info("数据库连接池已关闭")
    
    def _check_pool(self):
        """检查连接池状态"""
        if not self._is_initialized or self.pool is None:
            raise RuntimeError("数据库连接池未初始化，请检查数据库配置和网络连接")
    
    async def execute_query(self, query: str, params: tuple = None):
        """执行查询语句"""
        self._check_pool()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params)
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            raise e
    
    async def execute_insert(self, query: str, params: tuple = None):
        """执行插入语句并返回插入的ID"""
        self._check_pool()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params)
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"数据库插入失败: {str(e)}")
            raise e
    
    async def execute_update(self, query: str, params: tuple = None):
        """执行更新语句并返回影响的行数"""
        self._check_pool()
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    result = await cursor.execute(query, params)
                    return result
        except Exception as e:
            logger.error(f"数据库更新失败: {str(e)}")
            raise e

# 全局数据库管理器实例
db_manager = DatabaseManager()

class ImageInformation:
    """图像信息模型"""
    
    @staticmethod
    async def create(chatbot_id: str, file_name: str, file_type: str, 
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
        
        await db_manager.execute_insert(query, params)
        return asset_id
    
    @staticmethod
    async def update_cos_url(asset_id: str, cos_url: str):
        """更新COS URL"""
        query = """
        UPDATE image_information 
        SET cos_url = %s, upload_status = 'success', updated_at = NOW()
        WHERE asset_id = %s
        """
        
        await db_manager.execute_update(query, (cos_url, asset_id))

class ChatbotInterface:
    """聊天界面配置模型"""
    
    @staticmethod
    async def upsert(data: Dict[str, Any]) -> bool:
        """插入或更新聊天界面配置"""
        # 检查是否已存在
        check_query = "SELECT id FROM chatbot_interface WHERE chatbot_id = %s"
        existing = await db_manager.execute_query(check_query, (data['chatbot_id'],))
        
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
        
        await db_manager.execute_update(query, params)
        return True
    
    @staticmethod
    async def get_by_chatbot_id(chatbot_id: str) -> Optional[Dict[str, Any]]:
        """根据chatbot_id获取配置"""
        query = "SELECT * FROM chatbot_interface WHERE chatbot_id = %s"
        result = await db_manager.execute_query(query, (chatbot_id,))
        return result[0] if result else None 