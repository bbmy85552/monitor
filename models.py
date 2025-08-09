# models.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

# ==================== 系统监控相关模型 ====================

class CpuInfo(BaseModel):
    """CPU信息模型"""
    cpu_percent: float = Field(..., description="CPU使用率")
    cpu_count_physical: int = Field(..., description="物理CPU核心数")
    cpu_count_logical: int = Field(..., description="逻辑CPU核心数")
    cpu_per_core: list[float] = Field(..., description="每个CPU核心的使用率")

class VirtualMemory(BaseModel):
    """虚拟内存信息模型"""
    total: int = Field(..., description="总内存（字节）")
    available: int = Field(..., description="可用内存（字节）")
    used: int = Field(..., description="已使用内存（字节）")
    free: int = Field(..., description="空闲内存（字节）")
    percent: float = Field(..., description="内存使用率")
    active: Optional[int] = Field(None, description="活跃内存")
    inactive: Optional[int] = Field(None, description="非活跃内存")
    buffers: Optional[int] = Field(None, description="缓冲区内存")
    cached: Optional[int] = Field(None, description="缓存内存")

class SwapMemory(BaseModel):
    """交换内存信息模型"""
    total: int = Field(..., description="总交换内存（字节）")
    used: int = Field(..., description="已使用交换内存（字节）")
    free: int = Field(..., description="空闲交换内存（字节）")
    percent: float = Field(..., description="交换内存使用率")
    sin: int = Field(..., description="换入内存字节数")
    sout: int = Field(..., description="换出内存字节数")

class MemoryInfo(BaseModel):
    """内存信息模型"""
    virtual_memory: VirtualMemory = Field(..., description="虚拟内存信息")
    swap_memory: SwapMemory = Field(..., description="交换内存信息")

class DiskUsage(BaseModel):
    """磁盘使用率模型"""
    total: int = Field(..., description="总磁盘空间（字节）")
    used: int = Field(..., description="已使用磁盘空间（字节）")
    free: int = Field(..., description="空闲磁盘空间（字节）")
    percent: float = Field(..., description="磁盘使用率")

class DiskIO(BaseModel):
    """磁盘IO模型"""
    read_count: Optional[int] = Field(None, description="读取次数")
    write_count: Optional[int] = Field(None, description="写入次数")
    read_bytes: Optional[int] = Field(None, description="读取字节数")
    write_bytes: Optional[int] = Field(None, description="写入字节数")
    read_time: Optional[int] = Field(None, description="读取时间（毫秒）")
    write_time: Optional[int] = Field(None, description="写入时间（毫秒）")

class DiskInfo(BaseModel):
    """磁盘信息模型"""
    disk_usage: DiskUsage = Field(..., description="磁盘使用率信息")
    disk_io: DiskIO = Field(..., description="磁盘IO信息")

class NetworkIO(BaseModel):
    """网络IO模型"""
    bytes_sent: int = Field(..., description="发送字节数")
    bytes_recv: int = Field(..., description="接收字节数")
    packets_sent: int = Field(..., description="发送数据包数")
    packets_recv: int = Field(..., description="接收数据包数")
    errin: int = Field(..., description="输入错误数")
    errout: int = Field(..., description="输出错误数")
    dropin: int = Field(..., description="输入丢弃包数")
    dropout: int = Field(..., description="输出丢弃包数")

class NetworkInfo(BaseModel):
    """网络信息模型"""
    network_io: NetworkIO = Field(..., description="网络IO信息")
    connections_count: int = Field(..., description="网络连接数")

class TcpConnections(BaseModel):
    """TCP连接信息模型"""
    total_connections: int = Field(..., description="总TCP连接数")
    established: int = Field(..., description="已建立连接数")
    time_wait: int = Field(..., description="TIME_WAIT状态连接数")
    close_wait: int = Field(..., description="CLOSE_WAIT状态连接数")
    listening: int = Field(..., description="LISTENING状态连接数")
    others: int = Field(..., description="其他状态连接数")

class ProcessMemoryInfo(BaseModel):
    """进程内存信息模型"""
    rss: int = Field(..., description="常驻内存集大小（字节）")
    vms: int = Field(..., description="虚拟内存大小（字节）")
    shared: Optional[int] = Field(None, description="共享内存大小")
    text: Optional[int] = Field(None, description="代码段大小")
    lib: Optional[int] = Field(None, description="库大小")
    data: Optional[int] = Field(None, description="数据段大小")
    dirty: Optional[int] = Field(None, description="脏页大小")

class ProcessCpuTimes(BaseModel):
    """进程CPU时间模型"""
    user: float = Field(..., description="用户态CPU时间（秒）")
    system: float = Field(..., description="内核态CPU时间（秒）")
    children_user: float = Field(..., description="子进程用户态CPU时间（秒）")
    children_system: float = Field(..., description="子进程内核态CPU时间（秒）")

class ProcessInfo(BaseModel):
    """进程信息模型"""
    pid: int = Field(..., description="进程ID")
    name: str = Field(..., description="进程名称")
    cpu_percent: float = Field(..., description="进程CPU使用率")
    memory_percent: float = Field(..., description="进程内存使用率")
    memory_info: ProcessMemoryInfo = Field(..., description="进程内存信息")
    cpu_times: ProcessCpuTimes = Field(..., description="进程CPU时间")
    num_threads: int = Field(..., description="线程数")
    status: str = Field(..., description="进程状态")
    create_time: str = Field(..., description="进程创建时间")

class SystemUptime(BaseModel):
    """系统运行时间模型"""
    boot_time: str = Field(..., description="系统启动时间")
    uptime_seconds: float = Field(..., description="运行时间（秒）")
    uptime_formatted: str = Field(..., description="格式化的运行时间")

class SystemMetrics(BaseModel):
    """系统监控指标模型"""
    timestamp: str = Field(..., description="数据时间戳")
    cpu: CpuInfo = Field(..., description="CPU信息")
    memory: MemoryInfo = Field(..., description="内存信息")
    disk: DiskInfo = Field(..., description="磁盘信息")
    network: NetworkInfo = Field(..., description="网络信息")
    tcp_connections: TcpConnections = Field(..., description="TCP连接信息")
    process: ProcessInfo = Field(..., description="进程信息")
    system_uptime: SystemUptime = Field(..., description="系统运行时间")

class SystemMetricsResponse(BaseModel):
    """系统监控指标响应模型"""
    status: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: SystemMetrics = Field(..., description="系统监控数据")

class SystemHistoryResponse(BaseModel):
    """系统历史数据响应模型"""
    status: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: list[SystemMetrics] = Field(..., description="系统历史数据列表")
    count: int = Field(..., description="数据条数")

class SystemStatsResponse(BaseModel):
    """系统统计信息响应模型"""
    status: int = Field(..., description="状态码")
    message: str = Field(..., description="响应消息")
    data: dict = Field(..., description="系统统计信息") 