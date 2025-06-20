# main.py
from fastapi import FastAPI, Query
from datetime import datetime, date, timedelta
import random  # 导入 random 模块用于生成随机数
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------------------------------------
# 创建 FastAPI 应用
# -----------------------------------------------------------
app = FastAPI(
    title="Analytics API",
    description="为前端提供分析页面的数据支持",
    version="1.0.0"
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
    loop_end_date = end_date.date()
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
"""
{
    "chatbot_id": "dc2b0e714bccfa50e70a238ea86c34c09ff73cb99136b1caef0ee9e61580b700",
    "time_range": {
        "start_date": "2025-06-11T00:00:00",
        "end_date": "2025-06-18T23:59:59"
    },
    "chats": {
        "summary": {
            "total_chats": {
                "value": 244,
                "change_percentage": -0.42
            },
            "total_messages": {
                "value": 589,
                "change_percentage": -0.08
            },
            "positive_feedback_messages": {
                "value": 374,
                "change_percentage": 0.27
            },
            "negative_feedback_messages": {
                "value": 34,
                "change_percentage": 0.07
            }
        },
        "chats_over_time": [
            {
                "date": "2025-06-11",
                "count": 10
            },
            {
                "date": "2025-06-12",
                "count": 27
            },
            {
                "date": "2025-06-13",
                "count": 25
            },
            {
                "date": "2025-06-14",
                "count": 36
            },
            {
                "date": "2025-06-15",
                "count": 13
            },
            {
                "date": "2025-06-16",
                "count": 44
            },
            {
                "date": "2025-06-17",
                "count": 46
            },
            {
                "date": "2025-06-18",
                "count": 43
            }
        ],
        "geo": [
            {
                "country": "United States",
                "count": 146
            },
            {
                "country": "China",
                "count": 199
            },
            {
                "country": "Japan",
                "count": 25
            },
            {
                "country": "Germany",
                "count": 152
            },
            {
                "country": "United Kingdom",
                "count": 154
            },
            {
                "country": "India",
                "count": 90
            },
            {
                "country": "Canada",
                "count": 136
            }
        ]
    },
    "topics": {
        "total_topics_identified": 5,
        "distribution": [
            {
                "category": "情感咨询",
                "count": 69,
                "percentage": 0.22
            },
            {
                "category": "功能使用",
                "count": 62,
                "percentage": 0.2
            },
            {
                "category": "文案编写",
                "count": 73,
                "percentage": 0.23
            },
            {
                "category": "内容续写",
                "count": 53,
                "percentage": 0.17
            },
            {
                "category": "代码生成",
                "count": 56,
                "percentage": 0.18
            }
        ]
    },
    "sentiment": {
        "overall_sentiment_score": 0.06,
        "distribution": [
            {
                "category": "Positive",
                "count": 374,
                "percentage": 0.63
            },
            {
                "category": "Neutral",
                "count": 181,
                "percentage": 0.31
            },
            {
                "category": "Negative",
                "count": 34,
                "percentage": 0.06
            }
        ],
        "sentiment_over_time": [
            {
                "date": "2025-06-11",
                "positive_count": 70,
                "negative_count": 4,
                "neutral_count": 26
            },
            {
                "date": "2025-06-12",
                "positive_count": 43,
                "negative_count": 4,
                "neutral_count": 27
            },
            {
                "date": "2025-06-13",
                "positive_count": 55,
                "negative_count": 1,
                "neutral_count": 28
            },
            {
                "date": "2025-06-14",
                "positive_count": 28,
                "negative_count": 6,
                "neutral_count": 12
            },
            {
                "date": "2025-06-15",
                "positive_count": 53,
                "negative_count": 1,
                "neutral_count": 30
            },
            {
                "date": "2025-06-16",
                "positive_count": 38,
                "negative_count": 2,
                "neutral_count": 21
            },
            {
                "date": "2025-06-17",
                "positive_count": 23,
                "negative_count": 6,
                "neutral_count": 17
            },
            {
                "date": "2025-06-18",
                "positive_count": 64,
                "negative_count": 10,
                "neutral_count": 20
            }
        ]
    }
}
"""
# 如何运行:
# 1. 保存代码为 main.py
# 2. 在终端运行: uvicorn main:app --reload