#!/bin/bash
# AI 资讯快报归档自动更新脚本（Bash 包装器）
# 用法: ./add-bulletin.sh <bulletin_html_file> ["标题描述"]
#
# 功能:
#   1. 从文件名提取日期 (YYYY-MM-DD)
#   2. 复制 HTML 到 YYYY/MM/DD.html
#   3. 自动更新 index.html 时间线（按日期倒序插入）
#   4. 如果年份/月份不存在，自动创建新的分组
#   5. 更新已归档期数统计
#   6. 自动执行 git add / commit / push
#
# 示例:
#   ./add-bulletin.sh ~/workspace/AI_News_Bulletin_2026-04-28.html
#   ./add-bulletin.sh ~/workspace/AI_News_Bulletin_2026-04-28.html "AI 资讯快报 · GPT-6预告 · 百度发布新模型"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: ./add-bulletin.sh <bulletin_html_file> [\"标题描述\"]"
    echo "示例: ./add-bulletin.sh /path/to/AI_News_Bulletin_2026-04-28.html"
    exit 1
fi

HTML_FILE="$1"
CUSTOM_TITLE="${2:-}"

# 检查文件是否存在
if [ ! -f "$HTML_FILE" ]; then
    echo "[错误] 文件不存在: $HTML_FILE"
    exit 1
fi

# 调用 Python 脚本执行核心逻辑
if [ -n "$CUSTOM_TITLE" ]; then
    python3 "$SCRIPT_DIR/add-bulletin.py" "$HTML_FILE" "$CUSTOM_TITLE"
else
    python3 "$SCRIPT_DIR/add-bulletin.py" "$HTML_FILE"
fi
