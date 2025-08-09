#!/bin/bash

# 日志查看脚本

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

LOG_FILE="$PROJECT_DIR/app.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 日志文件不存在: $LOG_FILE"
    exit 1
fi

echo "=== FastAPI应用日志 ==="
echo "日志文件: $LOG_FILE"
echo "文件大小: $(du -h "$LOG_FILE" | cut -f1)"
echo ""

# 根据参数显示不同内容
case "${1:-tail}" in
    "tail")
        echo "显示最后50行日志 (按Ctrl+C退出):"
        echo "----------------------------------------"
        tail -f -n 50 "$LOG_FILE"
        ;;
    "all")
        echo "显示完整日志内容:"
        echo "----------------------------------------"
        cat "$LOG_FILE"
        ;;
    "error")
        echo "显示错误日志 (包含ERROR):"
        echo "----------------------------------------"
        grep -i "error\|exception\|traceback" "$LOG_FILE" | tail -n 20
        ;;
    "info")
        echo "显示信息日志 (包含INFO):"
        echo "----------------------------------------"
        grep -i "info" "$LOG_FILE" | tail -n 20
        ;;
    "monitor")
        echo "显示监控相关日志:"
        echo "----------------------------------------"
        grep -i "monitor\|metrics\|sqlite" "$LOG_FILE" | tail -n 20
        ;;
    "stats")
        echo "日志统计信息:"
        echo "----------------------------------------"
        echo "总行数: $(wc -l < "$LOG_FILE")"
        echo "错误行数: $(grep -i "error\|exception" "$LOG_FILE" | wc -l)"
        echo "信息行数: $(grep -i "info" "$LOG_FILE" | wc -l)"
        echo "监控相关行数: $(grep -i "monitor\|metrics\|sqlite" "$LOG_FILE" | wc -l)"
        ;;
    *)
        echo "用法: $0 [tail|all|error|info|monitor|stats]"
        echo ""
        echo "选项说明:"
        echo "  tail    - 实时显示日志 (默认)"
        echo "  all     - 显示完整日志"
        echo "  error   - 显示错误日志"
        echo "  info    - 显示信息日志"
        echo "  monitor - 显示监控相关日志"
        echo "  stats   - 显示日志统计"
        ;;
esac