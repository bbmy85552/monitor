# database.py
import os
import asyncio
import aiomysql
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from dotenv import load_dotenv

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

class DatabaseManager:
    def __init__(self):
        self.pool = None
    
    async def init_pool(self):
        """初始化数据库连接池"""
        self.pool = await aiomysql.create_pool(**DB_CONFIG)
    
    async def close_pool(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def execute_query(self, query: str, params: tuple = None):
        """执行查询语句"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
    
    async def execute_insert(self, query: str, params: tuple = None):
        """执行插入语句并返回插入的ID"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return cursor.lastrowid
    
    async def execute_update(self, query: str, params: tuple = None):
        """执行更新语句并返回影响的行数"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                result = await cursor.execute(query, params)
                return result

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