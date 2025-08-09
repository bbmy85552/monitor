#!/bin/bash

# 项目启动脚本
# 使用nohup运行FastAPI应用并保存日志

# 设置项目根目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 设置日志文件路径
LOG_FILE="$PROJECT_DIR/app.log"
PID_FILE="$PROJECT_DIR/app.pid"

# 设置环境变量（如果需要）
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "应用已经在运行 (PID: $PID)"
        echo "使用 './stop.sh' 停止应用"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 停止现有进程（如果有）
pkill -f "python3.*main.py" 2>/dev/null || true

# 等待进程完全停止
sleep 2

echo "正在启动FastAPI应用..."
echo "项目目录: $PROJECT_DIR"
echo "日志文件: $LOG_FILE"

# 使用nohup启动应用
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_FILE" 2>&1 &

# 获取进程ID
PID=$!
echo $PID > "$PID_FILE"

# 等待应用启动
sleep 5

# 检查应用是否成功启动
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 应用启动成功!"
    echo "   PID: $PID"
    echo "   日志文件: $LOG_FILE"
    echo "   PID文件: $PID_FILE"
    echo ""
    echo "📝 查看实时日志: tail -f $LOG_FILE"
    echo "🛑 停止应用: ./stop.sh"
    echo "🔍 检查状态: ./status.sh"
    echo ""
    echo "🌐 API文档: http://localhost:8000/docs"
    echo "🏥 健康检查: http://localhost:8000/health"
else
    echo "❌ 应用启动失败!"
    echo "请检查日志文件: $LOG_FILE"
    exit 1
fi