#!/bin/bash

# 停止脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PID_FILE="$PROJECT_DIR/app.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "正在停止应用 (PID: $PID)..."
        kill $PID
        
        # 等待进程停止
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # 如果进程仍在运行，强制停止
        if ps -p $PID > /dev/null 2>&1; then
            echo "强制停止应用..."
            kill -9 $PID
        fi
        
        rm -f "$PID_FILE"
        echo "✅ 应用已停止"
    else
        echo "⚠️  应用未运行"
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️  PID文件不存在"
fi

# 停止所有相关的python进程
pkill -f "python.*main.py" 2>/dev/null || true
echo "已清理所有相关进程"