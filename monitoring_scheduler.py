import asyncio
import logging
from datetime import datetime
from typing import Optional

from system_monitor import system_monitor
from database import SystemMetricsSQLite

logger = logging.getLogger(__name__)

class MonitoringScheduler:
    def __init__(self, interval_seconds: int = 60):
        """
        初始化监控调度器
        
        Args:
            interval_seconds: 监控数据收集间隔（秒），默认60秒
        """
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    async def _collect_and_store_metrics(self):
        """
        收集并存储监控指标的内部方法
        """
        try:
            # 获取当前监控指标
            metrics_data = system_monitor.get_current_metrics()
            
            # 存储到SQLite数据库
            metrics_id = SystemMetricsSQLite.create(metrics_data)
            
            logger.info(f"监控数据收集成功，ID: {metrics_id}, 时间: {metrics_data['timestamp']}")
            
        except Exception as e:
            logger.error(f"收集监控数据失败: {str(e)}")
    
    async def _monitoring_loop(self):
        """
        监控循环，定期收集数据
        """
        logger.info(f"监控调度器启动，收集间隔: {self.interval_seconds} 秒")
        
        while self.is_running:
            try:
                # 执行数据收集
                await self._collect_and_store_metrics()
                
                # 等待下一次收集
                await asyncio.sleep(self.interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("监控调度器被取消")
                break
            except Exception as e:
                logger.error(f"监控循环发生错误: {str(e)}")
                # 发生错误时也等待一段时间再继续
                await asyncio.sleep(self.interval_seconds)
    
    async def start(self):
        """
        启动监控调度器
        """
        if self.is_running:
            logger.warning("监控调度器已经在运行中")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("监控调度器已启动")
    
    async def stop(self):
        """
        停止监控调度器
        """
        if not self.is_running:
            logger.warning("监控调度器未在运行")
            return
        
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("监控调度器已停止")
    
    def is_monitoring(self) -> bool:
        """
        检查监控调度器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        return self.is_running

# 全局监控调度器实例
monitoring_scheduler = MonitoringScheduler(interval_seconds=60)  # 默认每60秒收集一次

async def start_monitoring():
    """
    启动系统监控的便捷函数
    """
    await monitoring_scheduler.start()

async def stop_monitoring():
    """
    停止系统监控的便捷函数
    """
    await monitoring_scheduler.stop()