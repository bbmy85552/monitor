#!/bin/bash

# 状态检查脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PID_FILE="$PROJECT_DIR/app.pid"
LOG_FILE="$PROJECT_DIR/app.log"

echo "=== FastAPI应用状态检查 ==="
echo ""

# 检查PID文件
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 应用正在运行"
        echo "   PID: $PID"
        echo "   PID文件: $PID_FILE"
        echo "   日志文件: $LOG_FILE"
        echo ""
        
        # 检查端口是否在监听
        if netstat -tlnp 2>/dev/null | grep -q ":8000.*$PID"; then
            echo "✅ 端口8000正在监听"
        else
            echo "⚠️  端口8000未在监听"
        fi
        
        # 测试健康检查接口
        echo ""
        echo "正在测试健康检查接口..."
        HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
        if [ "$HEALTH_RESPONSE" = "200" ]; then
            echo "✅ 健康检查接口正常"
        else
            echo "❌ 健康检查接口异常 (HTTP $HEALTH_RESPONSE)"
        fi
        
    else
        echo "❌ 应用未运行 (PID文件存在但进程不存在)"
        rm -f "$PID_FILE"
    fi
else
    echo "❌ 应用未运行 (PID文件不存在)"
fi

echo ""
echo "=== 日志信息 ==="
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "日志文件大小: $LOG_SIZE"
    echo "最后10行日志:"
    echo "----------------------------------------"
    tail -n 10 "$LOG_FILE"
    echo "----------------------------------------"
else
    echo "日志文件不存在: $LOG_FILE"
fi

echo ""
echo "=== 系统资源 ==="
echo "Python进程:"
ps aux | grep "python.*main.py" | grep -v grep || echo "无相关Python进程"

echo ""
echo "端口8000占用情况:"
netstat -tlnp 2>/dev/null | grep ":8000" || echo "端口8000未被占用"