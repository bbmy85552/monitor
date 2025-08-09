import psutil
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        
    def get_cpu_info(self) -> Dict:
        """获取CPU使用率信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_count_physical": cpu_count,
                "cpu_count_logical": cpu_count_logical,
                "cpu_per_core": psutil.cpu_percent(interval=1, percpu=True)
            }
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {"error": str(e)}
    
    def get_memory_info(self) -> Dict:
        """获取内存使用率信息"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "virtual_memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free,
                    "percent": memory.percent,
                    "active": getattr(memory, 'active', None),
                    "inactive": getattr(memory, 'inactive', None),
                    "buffers": getattr(memory, 'buffers', None),
                    "cached": getattr(memory, 'cached', None)
                },
                "swap_memory": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent,
                    "sin": swap.sin,
                    "sout": swap.sout
                }
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {"error": str(e)}
    
    def get_disk_info(self) -> Dict:
        """获取磁盘使用率信息"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                "disk_usage": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": disk_usage.percent
                },
                "disk_io": {
                    "read_count": disk_io.read_count if disk_io else None,
                    "write_count": disk_io.write_count if disk_io else None,
                    "read_bytes": disk_io.read_bytes if disk_io else None,
                    "write_bytes": disk_io.write_bytes if disk_io else None,
                    "read_time": disk_io.read_time if disk_io else None,
                    "write_time": disk_io.write_time if disk_io else None
                }
            }
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict:
        """获取网络信息"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            return {
                "network_io": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout
                },
                "connections_count": net_connections
            }
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {"error": str(e)}
    
    def get_tcp_connections(self) -> Dict:
        """获取TCP连接详细信息"""
        try:
            connections = psutil.net_connections(kind='tcp')
            tcp_stats = {
                "total_connections": len(connections),
                "established": 0,
                "time_wait": 0,
                "close_wait": 0,
                "listening": 0,
                "others": 0
            }
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    tcp_stats["established"] += 1
                elif conn.status == 'TIME_WAIT':
                    tcp_stats["time_wait"] += 1
                elif conn.status == 'CLOSE_WAIT':
                    tcp_stats["close_wait"] += 1
                elif conn.status == 'LISTEN':
                    tcp_stats["listening"] += 1
                else:
                    tcp_stats["others"] += 1
            
            return tcp_stats
        except Exception as e:
            logger.error(f"获取TCP连接信息失败: {e}")
            return {"error": str(e)}
    
    def get_process_info(self) -> Dict:
        """获取进程信息"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_times = process.cpu_times()
            
            return {
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "shared": getattr(memory_info, 'shared', None),
                    "text": getattr(memory_info, 'text', None),
                    "lib": getattr(memory_info, 'lib', None),
                    "data": getattr(memory_info, 'data', None),
                    "dirty": getattr(memory_info, 'dirty', None)
                },
                "cpu_times": {
                    "user": cpu_times.user,
                    "system": cpu_times.system,
                    "children_user": cpu_times.children_user,
                    "children_system": cpu_times.children_system
                },
                "num_threads": process.num_threads(),
                "status": process.status(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return {"error": str(e)}
    
    def get_system_uptime(self) -> Dict:
        """获取系统运行时间"""
        try:
            boot_time = psutil.boot_time()
            boot_datetime = datetime.fromtimestamp(boot_time)
            uptime = time.time() - boot_time
            
            # 转换为天数、小时、分钟、秒
            days = int(uptime // (24 * 3600))
            hours = int((uptime % (24 * 3600)) // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            
            return {
                "boot_time": boot_datetime.isoformat(),
                "uptime_seconds": uptime,
                "uptime_formatted": f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            }
        except Exception as e:
            logger.error(f"获取系统运行时间失败: {e}")
            return {"error": str(e)}
    
    def get_current_metrics(self) -> Dict:
        """获取所有当前系统指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "tcp_connections": self.get_tcp_connections(),
            "process": self.get_process_info(),
            "system_uptime": self.get_system_uptime()
        }

# 全局监控实例
system_monitor = SystemMonitor()