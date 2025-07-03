# models.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class ThemeEnum(str, Enum):
    light = "light"
    dark = "dark"

class BubblePositionEnum(str, Enum):
    left = "left"
    right = "right"

class AssetTypeEnum(str, Enum):
    chatbot_icon = "chatbot_icon"
    bubble_icon = "bubble_icon"

class ImageData(BaseModel):
    """图像数据模型"""
    asset_type: AssetTypeEnum
    file_data: str = Field(..., description="Base64 编码的图像数据")
    file_name: str = Field(..., description="原始文件名")
    file_type: str = Field(..., description="MIME 类型")
    file_size: int = Field(..., description="文件大小（字节）")

class ChatInterfaceUpdateRequest(BaseModel):
    """聊天界面更新请求模型"""
    chatbot_id: str = Field(..., description="聊天机器人ID")
    
    # 消息与显示
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    initial_messages: Optional[str] = Field(None, description="初始消息")
    suggested_message_1: Optional[str] = Field(None, max_length=200, description="建议消息1")
    suggested_message_2: Optional[str] = Field(None, max_length=200, description="建议消息2")
    suggested_message_3: Optional[str] = Field(None, max_length=200, description="建议消息3")
    suggested_message_4: Optional[str] = Field(None, max_length=200, description="建议消息4")
    message_placeholder: Optional[str] = Field(None, max_length=200, description="消息占位符")
    footer_content: Optional[str] = Field(None, description="页脚内容")
    
    # 外观与主题
    theme: Optional[ThemeEnum] = Field(ThemeEnum.light, description="主题")
    user_message_color: Optional[str] = Field(None, max_length=50, description="用户消息颜色")
    sync_header_color: Optional[bool] = Field(False, description="同步头部颜色")
    
    # 气泡设置
    bubble_color: Optional[str] = Field(None, max_length=50, description="气泡颜色")
    bubble_position: Optional[BubblePositionEnum] = Field(BubblePositionEnum.right, description="气泡位置")
    
    # 行为与功能开关
    auto_open_seconds: Optional[int] = Field(0, description="自动打开秒数")
    show_suggested_after_first_message: Optional[bool] = Field(False, description="首次消息后显示建议")
    collect_feedback: Optional[bool] = Field(False, description="收集反馈")
    allow_regeneration: Optional[bool] = Field(False, description="允许重新生成")
    
    # 现有图片URL
    chatbot_icon_url: Optional[str] = Field(None, max_length=255, description="聊天机器人图标URL")
    bubble_icon_url: Optional[str] = Field(None, max_length=255, description="气泡图标URL")
    
    # 新上传的图像数据
    chatbot_icon_data: Optional[ImageData] = Field(None, description="聊天机器人图标数据")
    bubble_icon_data: Optional[ImageData] = Field(None, description="气泡图标数据")

class ChatInterfaceUpdateResponse(BaseModel):
    """聊天界面更新响应模型"""
    status: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    chatbot_icon_url: Optional[str] = Field(None, description="聊天机器人图标最终URL")
    bubble_icon_url: Optional[str] = Field(None, description="气泡图标最终URL")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: int = Field(..., description="状态码")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="错误详情") 