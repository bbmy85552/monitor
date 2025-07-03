# main.py
from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, date, timedelta
import random  # 导入 random 模块用于生成随机数
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入自定义模块
from database import db_manager, ChatbotInterface, ImageInformation
from cos_service import cos_service
from models import (
    ChatInterfaceUpdateRequest,
    ChatInterfaceUpdateResponse,
    ErrorResponse
)


# -----------------------------------------------------------
# 生命周期管理
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库连接池
    try:
        db_manager.init_pool()
        logger.info("应用启动成功，数据库连接池初始化完成")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        raise e
    yield
    # 关闭时清理数据库连接池
    db_manager.close_pool()


# -----------------------------------------------------------
# 创建 FastAPI 应用
# -----------------------------------------------------------
app = FastAPI(
    title="Chatbot Settings API",
    description="为前端提供聊天机器人设置和分析页面的数据支持",
    version="1.0.0",
    lifespan=lifespan
)
origin_regex = r"^(http://localhost(:\d+)?|https://ai-rag-.*\.vercel\.app)$"

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://192.168.105.13:3000",
    "https://ai-dev.awesomefuture.top"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有标头
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点，用于检查数据库连接和服务状态
    """
    try:
        # 检查数据库连接
        test_query = "SELECT 1 as test"
        result = db_manager.execute_query(test_query)
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "database_test": result[0]['test'] if result else None
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/analytics/data", tags=["Analytics"])
async def get_analytics_data(
        chatbot_id: str = Query(..., description="聊天机器人的唯一标识符", example="cb_12345"),
        start_date: datetime = Query(..., description="查询的开始时间 (ISO 8601格式)", example="2025-06-01T00:00:00Z"),
        end_date: datetime = Query(..., description="查询的结束时间 (ISO 8601格式)", example="2025-06-15T23:59:59Z")
):
    """
    根据 chatbot_id 和时间范围，获取分析页面所需的全量数据。
    """
    analytics_data = _get_mock_data(chatbot_id, start_date, end_date)
    return analytics_data


def _get_mock_data(chatbot_id: str, start_date: datetime, end_date: datetime) -> dict:
    """
    生成在一定范围内随机波动的模拟数据。
    """
    # --- 动态生成日期范围 ---
    all_dates = []
    current_date = start_date.date()
    # Corrected end_date logic to be inclusive
    loop_end_date = (end_date - timedelta(days=1)).date()  # 减去一天
    while current_date <= loop_end_date:
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    # --- 随机生成时间序列数据 ---
    chats_over_time = [{"date": d.isoformat(), "count": random.randint(5, 50)} for d in all_dates]

    sentiment_over_time = [{
        "date": d.isoformat(),
        "positive_count": random.randint(20, 80),
        "negative_count": random.randint(0, 10),
        "neutral_count": random.randint(10, 30)
    } for d in all_dates]

    # --- 根据时间序列数据计算总览数据 ---
    total_chats_value = sum(item['count'] for item in chats_over_time)

    total_positive = sum(item['positive_count'] for item in sentiment_over_time)
    total_negative = sum(item['negative_count'] for item in sentiment_over_time)
    total_neutral = sum(item['neutral_count'] for item in sentiment_over_time)
    total_messages_value = total_positive + total_negative + total_neutral

    # --- 随机生成话题分布 ---
    topic_categories = ["情感咨询", "功能使用", "文案编写", "内容续写", "代码生成"]
    topics_distribution = [{"category": cat, "count": random.randint(10, 100)} for cat in topic_categories]
    total_topic_count = sum(item['count'] for item in topics_distribution)
    for item in topics_distribution:
        item["percentage"] = round(item["count"] / total_topic_count, 2) if total_topic_count > 0 else 0

    # --- 随机生成地理位置分布数据 (新增) ---
    # --- 随机生成地理位置分布数据 (使用英文名，以符合前端要求) ---
    geo_countries_english = ["United States", "China", "Japan", "Germany", "United Kingdom", "India", "Canada"]
    geo_distribution = [{"country": country, "count": random.randint(10, 200)} for country in geo_countries_english]

    # --- 组装最终的 mock_data ---
    mock_data = {
        "chatbot_id": chatbot_id,
        "time_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "chats": {
            "summary": {
                "total_chats": {
                    "value": total_chats_value,
                    "change_percentage": round(random.uniform(-0.5, 0.5), 2)
                },
                "total_messages": {
                    "value": total_messages_value,
                    "change_percentage": round(random.uniform(-0.5, 0.5), 2)
                },
                "positive_feedback_messages": {
                    "value": total_positive,
                    "change_percentage": round(random.uniform(-0.5, 0.5), 2)
                },
                "negative_feedback_messages": {
                    "value": total_negative,
                    "change_percentage": round(random.uniform(-0.5, 0.5), 2)
                }
            },
            "chats_over_time": chats_over_time,
            # 新增的 GEO 数据
            "geo": geo_distribution
        },
        "topics": {
            "total_topics_identified": len(topics_distribution),
            "distribution": topics_distribution
        },
        "sentiment": {
            "overall_sentiment_score": round(random.uniform(-1.0, 1.0), 2),
            "distribution": [
                {
                    "category": "Positive",
                    "count": total_positive,
                    "percentage": round(total_positive / total_messages_value, 2) if total_messages_value > 0 else 0
                },
                {
                    "category": "Neutral",
                    "count": total_neutral,
                    "percentage": round(total_neutral / total_messages_value, 2) if total_messages_value > 0 else 0
                },
                {
                    "category": "Negative",
                    "count": total_negative,
                    "percentage": round(total_negative / total_messages_value, 2) if total_messages_value > 0 else 0
                },
            ],
            "sentiment_over_time": sentiment_over_time
        }
    }
    return mock_data


@app.post("/settings/update_chat_interface",
          response_model=ChatInterfaceUpdateResponse,
          responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
          tags=["Settings"])
async def update_chat_interface(request: ChatInterfaceUpdateRequest):
    """
    更新聊天界面设置，包括图像上传处理
    """
    try:
        # 准备数据库保存的数据
        save_data = {
            'chatbot_id': request.chatbot_id,
            'display_name': request.display_name,
            'initial_messages': request.initial_messages,
            'suggested_message_1': request.suggested_message_1,
            'suggested_message_2': request.suggested_message_2,
            'suggested_message_3': request.suggested_message_3,
            'suggested_message_4': request.suggested_message_4,
            'message_placeholder': request.message_placeholder,
            'footer_content': request.footer_content,
            'theme': request.theme.value if request.theme else None,
            'user_message_color': request.user_message_color,
            'sync_header_color': request.sync_header_color,
            'bubble_color': request.bubble_color,
            'bubble_position': request.bubble_position.value if request.bubble_position else None,
            'auto_open_seconds': request.auto_open_seconds,
            'show_suggested_after_first_message': request.show_suggested_after_first_message,
            'collect_feedback': request.collect_feedback,
            'allow_regeneration': request.allow_regeneration,
            'chatbot_icon_url': request.chatbot_icon_url,
            'bubble_icon_url': request.bubble_icon_url
        }

        # 处理聊天机器人图标上传
        final_chatbot_icon_url = request.chatbot_icon_url
        if request.chatbot_icon_data:
            success, cos_url, error = cos_service.upload_base64_image(
                base64_data=request.chatbot_icon_data.file_data,
                file_name=request.chatbot_icon_data.file_name,
                asset_type=request.chatbot_icon_data.asset_type.value,
                chatbot_id=request.chatbot_id
            )

            if success:
                # 保存图像信息到数据库
                ImageInformation.create(
                    chatbot_id=request.chatbot_id,
                    file_name=request.chatbot_icon_data.file_name,
                    file_type=request.chatbot_icon_data.file_type,
                    file_size=request.chatbot_icon_data.file_size,
                    asset_type=request.chatbot_icon_data.asset_type.value,
                    cos_url=cos_url
                )
                final_chatbot_icon_url = cos_url
            else:
                raise HTTPException(status_code=400, detail=f"聊天机器人图标上传失败: {error}")

        # 处理气泡图标上传
        final_bubble_icon_url = request.bubble_icon_url
        if request.bubble_icon_data:
            success, cos_url, error = cos_service.upload_base64_image(
                base64_data=request.bubble_icon_data.file_data,
                file_name=request.bubble_icon_data.file_name,
                asset_type=request.bubble_icon_data.asset_type.value,
                chatbot_id=request.chatbot_id
            )

            if success:
                # 保存图像信息到数据库
                ImageInformation.create(
                    chatbot_id=request.chatbot_id,
                    file_name=request.bubble_icon_data.file_name,
                    file_type=request.bubble_icon_data.file_type,
                    file_size=request.bubble_icon_data.file_size,
                    asset_type=request.bubble_icon_data.asset_type.value,
                    cos_url=cos_url
                )
                final_bubble_icon_url = cos_url
            else:
                raise HTTPException(status_code=400, detail=f"气泡图标上传失败: {error}")

        # 更新数据库中的最终URL
        save_data['chatbot_icon_url'] = final_chatbot_icon_url
        save_data['bubble_icon_url'] = final_bubble_icon_url

        # 保存到数据库
        ChatbotInterface.upsert(save_data)

        return ChatInterfaceUpdateResponse(
            status=200,
            message="聊天界面设置保存成功",
            chatbot_icon_url=final_chatbot_icon_url,
            bubble_icon_url=final_bubble_icon_url
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.get("/settings/chat_interface/{chatbot_id}",
         tags=["Settings"])
async def get_chat_interface(chatbot_id: str):
    """
    获取聊天界面设置
    """
    try:
        settings = ChatbotInterface.get_by_chatbot_id(chatbot_id)
        if not settings:
            raise HTTPException(status_code=404, detail="聊天机器人配置不存在")

        return {
            "status": 200,
            "data": settings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.get("/settings/get_chatbot_interface_data/{chatbot_id}",
         tags=["Settings"])
async def get_chatbot_interface_data(chatbot_id: str):
    """
    获取指定chatbot_id的完整聊天界面配置数据
    返回chatbot_interface表的所有字段
    """
    try:
        # 从数据库获取完整的聊天界面配置数据
        interface_data = ChatbotInterface.get_by_chatbot_id(chatbot_id)

        if not interface_data:
            raise HTTPException(status_code=404, detail="指定的聊天机器人配置不存在")

        return {
            "status": 200,
            "message": "获取聊天界面配置成功",
            "data": interface_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
