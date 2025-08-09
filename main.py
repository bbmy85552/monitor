# main.py
from fastapi import FastAPI, Query, HTTPException, Request
from datetime import datetime, date, timedelta
import random  # 导入 random 模块用于生成随机数
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging

# 配置日志
import logging
import logging.handlers
import os

# 创建日志目录
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.handlers.RotatingFileHandler(
            f'{log_dir}/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
    ]
)

logger = logging.getLogger(__name__)

# 导入自定义模块
from database import sqlite_manager, SystemMetricsSQLite
from system_monitor import system_monitor
from monitoring_scheduler import monitoring_scheduler, start_monitoring, stop_monitoring
from models import (
    SystemMetricsResponse,
    SystemHistoryResponse,
    SystemStatsResponse
)


# -----------------------------------------------------------
# 生命周期管理
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await start_monitoring()
        logger.info("系统监控调度器已启动")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        raise e
    yield
    try:
        await stop_monitoring()
        logger.info("系统监控调度器已停止")
    except Exception as e:
        logger.error(f"停止监控调度器时发生错误: {str(e)}")


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
    "https://ai-dev.awesomefuture.top",
    "https://domain-test.novatime.top"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有标头
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/monitor", response_class=HTMLResponse, tags=["Monitor"])
async def monitor_page():
    """
    系统监控仪表板页面
    """
    with open("static/monitor.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点，用于检查数据库连接和服务状态
    """
    try:
        # 检查 SQLite 可用性
        result = sqlite_manager.execute_query("SELECT 1 as test")
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

# ==================== 系统监控相关API端点 ====================

@app.get("/monitor/current", 
         response_model=SystemMetricsResponse,
         tags=["System Monitor"])
async def get_current_metrics():
    """
    获取当前系统监控指标
    包括CPU、内存、磁盘、网络、TCP连接、进程等信息
    """
    try:
        metrics_data = system_monitor.get_current_metrics()
        
        return SystemMetricsResponse(
            status=200,
            message="获取当前系统监控指标成功",
            data=metrics_data
        )
    except Exception as e:
        logger.error(f"获取当前系统监控指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取当前系统监控指标失败: {str(e)}")


@app.get("/monitor/latest", 
         response_model=SystemMetricsResponse,
         tags=["System Monitor"])
async def get_latest_metrics():
    """
    获取数据库中最新的系统监控指标
    """
    try:
        latest_metrics = SystemMetricsSQLite.get_latest()
        
        if not latest_metrics:
            raise HTTPException(status_code=404, detail="暂无监控数据")
        
        # 转换为API响应格式
        metrics_data = {
            "timestamp": latest_metrics["timestamp"],
            "cpu": {
                "cpu_percent": latest_metrics["cpu_percent"],
                "cpu_count_physical": 0,  # 数据库中未存储
                "cpu_count_logical": 0,   # 数据库中未存储
                "cpu_per_core": []        # 数据库中未存储
            },
            "memory": {
                "virtual_memory": {
                    "total": latest_metrics["memory_total"],
                    "available": latest_metrics["memory_total"] - latest_metrics["memory_used"],
                    "used": latest_metrics["memory_used"],
                    "free": latest_metrics["memory_total"] - latest_metrics["memory_used"],
                    "percent": latest_metrics["memory_percent"]
                },
                "swap_memory": {
                    "total": 0,
                    "used": 0,
                    "free": 0,
                    "percent": 0,
                    "sin": 0,
                    "sout": 0
                }
            },
            "disk": {
                "disk_usage": {
                    "total": latest_metrics["disk_total"],
                    "used": latest_metrics["disk_used"],
                    "free": latest_metrics["disk_total"] - latest_metrics["disk_used"],
                    "percent": latest_metrics["disk_percent"]
                },
                "disk_io": {
                    "read_count": None,
                    "write_count": None,
                    "read_bytes": None,
                    "write_bytes": None,
                    "read_time": None,
                    "write_time": None
                }
            },
            "network": {
                "network_io": {
                    "bytes_sent": latest_metrics["network_bytes_sent"],
                    "bytes_recv": latest_metrics["network_bytes_recv"],
                    "packets_sent": 0,
                    "packets_recv": 0,
                    "errin": 0,
                    "errout": 0,
                    "dropin": 0,
                    "dropout": 0
                },
                "connections_count": latest_metrics["tcp_connections"]
            },
            "tcp_connections": {
                "total_connections": latest_metrics["tcp_connections"],
                "established": 0,
                "time_wait": 0,
                "close_wait": 0,
                "listening": 0,
                "others": 0
            },
            "process": {
                "pid": 0,
                "name": "unknown",
                "cpu_percent": latest_metrics["process_cpu_percent"],
                "memory_percent": latest_metrics["process_memory_percent"],
                "memory_info": {
                    "rss": latest_metrics["process_memory_rss"],
                    "vms": 0,
                    "shared": None,
                    "text": None,
                    "lib": None,
                    "data": None,
                    "dirty": None
                },
                "cpu_times": {
                    "user": 0,
                    "system": 0,
                    "children_user": 0,
                    "children_system": 0
                },
                "num_threads": 0,
                "status": "unknown",
                "create_time": "unknown"
            },
            "system_uptime": {
                "boot_time": "unknown",
                "uptime_seconds": latest_metrics["uptime_seconds"],
                "uptime_formatted": f"{int(latest_metrics['uptime_seconds'] // 86400)} days"
            }
        }
        
        return SystemMetricsResponse(
            status=200,
            message="获取最新系统监控指标成功",
            data=metrics_data
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新系统监控指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取最新系统监控指标失败: {str(e)}")


@app.get("/monitor/history",
         response_model=SystemHistoryResponse,
         tags=["System Monitor"])
async def get_metrics_history(
    hours: int = Query(24, ge=1, le=168, description="查询历史数据的时间范围（小时），默认24小时，最大168小时（7天）")
):
    """
    获取系统监控历史数据
    """
    try:
        history_data = SystemMetricsSQLite.get_history(hours)
        
        # 转换为API响应格式
        formatted_history = []
        for record in history_data:
            metrics_data = {
                "timestamp": record["timestamp"],
                "cpu": {
                    "cpu_percent": record["cpu_percent"],
                    "cpu_count_physical": 0,
                    "cpu_count_logical": 0,
                    "cpu_per_core": []
                },
                "memory": {
                    "virtual_memory": {
                        "total": record["memory_total"],
                        "available": record["memory_total"] - record["memory_used"],
                        "used": record["memory_used"],
                        "free": record["memory_total"] - record["memory_used"],
                        "percent": record["memory_percent"]
                    },
                    "swap_memory": {
                        "total": 0,
                        "used": 0,
                        "free": 0,
                        "percent": 0,
                        "sin": 0,
                        "sout": 0
                    }
                },
                "disk": {
                    "disk_usage": {
                        "total": record["disk_total"],
                        "used": record["disk_used"],
                        "free": record["disk_total"] - record["disk_used"],
                        "percent": record["disk_percent"]
                    },
                    "disk_io": {
                        "read_count": None,
                        "write_count": None,
                        "read_bytes": None,
                        "write_bytes": None,
                        "read_time": None,
                        "write_time": None
                    }
                },
                "network": {
                    "network_io": {
                        "bytes_sent": record["network_bytes_sent"],
                        "bytes_recv": record["network_bytes_recv"],
                        "packets_sent": 0,
                        "packets_recv": 0,
                        "errin": 0,
                        "errout": 0,
                        "dropin": 0,
                        "dropout": 0
                    },
                    "connections_count": record["tcp_connections"]
                },
                "tcp_connections": {
                    "total_connections": record["tcp_connections"],
                    "established": 0,
                    "time_wait": 0,
                    "close_wait": 0,
                    "listening": 0,
                    "others": 0
                },
                "process": {
                    "pid": 0,
                    "name": "unknown",
                    "cpu_percent": record["process_cpu_percent"],
                    "memory_percent": record["process_memory_percent"],
                    "memory_info": {
                        "rss": record["process_memory_rss"],
                        "vms": 0,
                        "shared": None,
                        "text": None,
                        "lib": None,
                        "data": None,
                        "dirty": None
                    },
                    "cpu_times": {
                        "user": 0,
                        "system": 0,
                        "children_user": 0,
                        "children_system": 0
                    },
                    "num_threads": 0,
                    "status": "unknown",
                    "create_time": "unknown"
                },
                "system_uptime": {
                    "boot_time": "unknown",
                    "uptime_seconds": record["uptime_seconds"],
                    "uptime_formatted": f"{int(record['uptime_seconds'] // 86400)} days"
                }
            }
            formatted_history.append(metrics_data)
        
        return SystemHistoryResponse(
            status=200,
            message=f"获取历史监控数据成功",
            data=formatted_history,
            count=len(formatted_history)
        )
    except Exception as e:
        logger.error(f"获取历史监控数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取历史监控数据失败: {str(e)}")


@app.get("/monitor/history/range",
         response_model=SystemHistoryResponse,
         tags=["System Monitor"])
async def get_metrics_history_by_range(
    start_time: str = Query(..., description="开始时间 (ISO 8601格式)"),
    end_time: str = Query(..., description="结束时间 (ISO 8601格式)")
):
    """
    根据时间范围获取系统监控历史数据
    """
    try:
        # 验证时间格式
        try:
            from datetime import datetime
            datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="时间格式不正确，请使用ISO 8601格式")
        
        history_data = SystemMetricsSQLite.get_history_by_range(start_time, end_time)
        
        # 转换为API响应格式（与上面的历史数据接口相同）
        formatted_history = []
        for record in history_data:
            metrics_data = {
                "timestamp": record["timestamp"],
                "cpu": {
                    "cpu_percent": record["cpu_percent"],
                    "cpu_count_physical": 0,
                    "cpu_count_logical": 0,
                    "cpu_per_core": []
                },
                "memory": {
                    "virtual_memory": {
                        "total": record["memory_total"],
                        "available": record["memory_total"] - record["memory_used"],
                        "used": record["memory_used"],
                        "free": record["memory_total"] - record["memory_used"],
                        "percent": record["memory_percent"]
                    },
                    "swap_memory": {
                        "total": 0,
                        "used": 0,
                        "free": 0,
                        "percent": 0,
                        "sin": 0,
                        "sout": 0
                    }
                },
                "disk": {
                    "disk_usage": {
                        "total": record["disk_total"],
                        "used": record["disk_used"],
                        "free": record["disk_total"] - record["disk_used"],
                        "percent": record["disk_percent"]
                    },
                    "disk_io": {
                        "read_count": None,
                        "write_count": None,
                        "read_bytes": None,
                        "write_bytes": None,
                        "read_time": None,
                        "write_time": None
                    }
                },
                "network": {
                    "network_io": {
                        "bytes_sent": record["network_bytes_sent"],
                        "bytes_recv": record["network_bytes_recv"],
                        "packets_sent": 0,
                        "packets_recv": 0,
                        "errin": 0,
                        "errout": 0,
                        "dropin": 0,
                        "dropout": 0
                    },
                    "connections_count": record["tcp_connections"]
                },
                "tcp_connections": {
                    "total_connections": record["tcp_connections"],
                    "established": 0,
                    "time_wait": 0,
                    "close_wait": 0,
                    "listening": 0,
                    "others": 0
                },
                "process": {
                    "pid": 0,
                    "name": "unknown",
                    "cpu_percent": record["process_cpu_percent"],
                    "memory_percent": record["process_memory_percent"],
                    "memory_info": {
                        "rss": record["process_memory_rss"],
                        "vms": 0,
                        "shared": None,
                        "text": None,
                        "lib": None,
                        "data": None,
                        "dirty": None
                    },
                    "cpu_times": {
                        "user": 0,
                        "system": 0,
                        "children_user": 0,
                        "children_system": 0
                    },
                    "num_threads": 0,
                    "status": "unknown",
                    "create_time": "unknown"
                },
                "system_uptime": {
                    "boot_time": "unknown",
                    "uptime_seconds": record["uptime_seconds"],
                    "uptime_formatted": f"{int(record['uptime_seconds'] // 86400)} days"
                }
            }
            formatted_history.append(metrics_data)
        
        return SystemHistoryResponse(
            status=200,
            message=f"获取指定时间范围历史监控数据成功",
            data=formatted_history,
            count=len(formatted_history)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指定时间范围历史监控数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取指定时间范围历史监控数据失败: {str(e)}")


@app.get("/monitor/stats",
         response_model=SystemStatsResponse,
         tags=["System Monitor"])
async def get_system_stats():
    """
    获取系统统计信息
    包括CPU、内存、磁盘的平均使用率等
    """
    try:
        # 获取最近24小时的数据
        history_data = SystemMetricsSQLite.get_history(24)
        
        if not history_data:
            raise HTTPException(status_code=404, detail="暂无监控数据")
        
        # 计算统计数据
        cpu_values = [record["cpu_percent"] for record in history_data if record["cpu_percent"] is not None]
        memory_values = [record["memory_percent"] for record in history_data if record["memory_percent"] is not None]
        disk_values = [record["disk_percent"] for record in history_data if record["disk_percent"] is not None]
        tcp_values = [record["tcp_connections"] for record in history_data if record["tcp_connections"] is not None]
        
        stats = {
            "period_hours": 24,
            "total_records": len(history_data),
            "cpu_stats": {
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
                "current": cpu_values[-1] if cpu_values else 0
            },
            "memory_stats": {
                "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0,
                "current": memory_values[-1] if memory_values else 0
            },
            "disk_stats": {
                "avg": sum(disk_values) / len(disk_values) if disk_values else 0,
                "max": max(disk_values) if disk_values else 0,
                "min": min(disk_values) if disk_values else 0,
                "current": disk_values[-1] if disk_values else 0
            },
            "tcp_stats": {
                "avg": sum(tcp_values) / len(tcp_values) if tcp_values else 0,
                "max": max(tcp_values) if tcp_values else 0,
                "min": min(tcp_values) if tcp_values else 0,
                "current": tcp_values[-1] if tcp_values else 0
            },
            "latest_update": history_data[0]["timestamp"] if history_data else None,
            "oldest_update": history_data[-1]["timestamp"] if history_data else None
        }
        
        return SystemStatsResponse(
            status=200,
            message="获取系统统计信息成功",
            data=stats
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取系统统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取系统统计信息失败: {str(e)}")


@app.post("/monitor/collect",
         tags=["System Monitor"])
async def collect_metrics():
    """
    手动触发收集一次系统监控指标
    """
    try:
        metrics_data = system_monitor.get_current_metrics()
        
        # 存储到SQLite数据库
        metrics_id = SystemMetricsSQLite.create(metrics_data)
        
        return {
            "status": 200,
            "message": "系统监控指标收集成功",
            "metrics_id": metrics_id,
            "timestamp": metrics_data["timestamp"]
        }
    except Exception as e:
        logger.error(f"收集系统监控指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"收集系统监控指标失败: {str(e)}")


@app.post("/monitor/cleanup",
         tags=["System Monitor"])
async def cleanup_old_metrics(
    days_to_keep: int = Query(30, ge=1, le=365, description="保留天数，默认30天")
):
    """
    清理指定天数前的旧监控数据
    """
    try:
        affected_rows = SystemMetricsSQLite.cleanup_old_data(days_to_keep)
        
        return {
            "status": 200,
            "message": f"清理完成，删除了 {affected_rows} 条记录",
            "days_kept": days_to_keep,
            "deleted_records": affected_rows
        }
    except Exception as e:
        logger.error(f"清理旧监控数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清理旧监控数据失败: {str(e)}")


@app.get("/monitor/scheduler/status",
         tags=["System Monitor"])
async def get_scheduler_status():
    """
    获取监控调度器状态
    """
    try:
        is_running = monitoring_scheduler.is_monitoring()
        
        return {
            "status": 200,
            "message": "获取调度器状态成功",
            "data": {
                "is_running": is_running,
                "interval_seconds": monitoring_scheduler.interval_seconds,
                "status_text": "运行中" if is_running else "已停止"
            }
        }
    except Exception as e:
        logger.error(f"获取调度器状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")


@app.post("/monitor/scheduler/start",
         tags=["System Monitor"])
async def start_scheduler():
    """
    启动监控调度器
    """
    try:
        if monitoring_scheduler.is_monitoring():
            return {
                "status": 200,
                "message": "监控调度器已经在运行中",
                "data": {
                    "is_running": True,
                    "interval_seconds": monitoring_scheduler.interval_seconds
                }
            }
        
        await monitoring_scheduler.start()
        
        return {
            "status": 200,
            "message": "监控调度器启动成功",
            "data": {
                "is_running": True,
                "interval_seconds": monitoring_scheduler.interval_seconds
            }
        }
    except Exception as e:
        logger.error(f"启动监控调度器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动监控调度器失败: {str(e)}")


@app.post("/monitor/scheduler/stop",
         tags=["System Monitor"])
async def stop_scheduler():
    """
    停止监控调度器
    """
    try:
        if not monitoring_scheduler.is_monitoring():
            return {
                "status": 200,
                "message": "监控调度器未在运行",
                "data": {
                    "is_running": False,
                    "interval_seconds": monitoring_scheduler.interval_seconds
                }
            }
        
        await monitoring_scheduler.stop()
        
        return {
            "status": 200,
            "message": "监控调度器已停止",
            "data": {
                "is_running": False,
                "interval_seconds": monitoring_scheduler.interval_seconds
            }
        }
    except Exception as e:
        logger.error(f"停止监控调度器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"停止监控调度器失败: {str(e)}")


@app.post("/monitor/scheduler/configure",
         tags=["System Monitor"])
async def configure_scheduler(
    interval_seconds: int = Query(..., ge=10, le=3600, description="收集间隔（秒），范围10-3600秒")
):
    """
    配置监控调度器参数
    """
    try:
        was_running = monitoring_scheduler.is_monitoring()
        
        # 如果正在运行，先停止
        if was_running:
            await monitoring_scheduler.stop()
        
        # 更新配置
        monitoring_scheduler.interval_seconds = interval_seconds
        
        # 如果之前在运行，重新启动
        if was_running:
            await monitoring_scheduler.start()
        
        return {
            "status": 200,
            "message": f"监控调度器配置更新成功，收集间隔: {interval_seconds} 秒",
            "data": {
                "interval_seconds": interval_seconds,
                "is_running": monitoring_scheduler.is_monitoring(),
                "was_restarted": was_running
            }
        }
    except Exception as e:
        logger.error(f"配置监控调度器失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"配置监控调度器失败: {str(e)}")
