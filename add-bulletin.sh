#!/bin/bash
# AI 资讯快报 - 添加新一期并自动更新归档首页
# 用法: ./add-bulletin.sh /path/to/AI_News_Bulletin_YYYY-MM-DD.html

set -e

# 检查参数
if [ $# -eq 0 ]; then
    echo "❌ 用法: ./add-bulletin.sh <html文件路径>"
    echo "   示例: ./add-bulletin.sh ~/Downloads/AI_News_Bulletin_2026-04-25.html"
    exit 1
fi

SOURCE_FILE="$1"

# 检查文件是否存在
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ 文件不存在: $SOURCE_FILE"
    exit 1
fi

# 从文件名提取日期
FILENAME=$(basename "$SOURCE_FILE")
if [[ "$FILENAME" =~ ([0-9]{4})-([0-9]{2})-([0-9]{2}) ]]; then
    YEAR="${BASH_REMATCH[1]}"
    MONTH="${BASH_REMATCH[2]}"
    DAY="${BASH_REMATCH[3]}"
else
    # 如果文件名没有日期，使用今天
    YEAR=$(date +%Y)
    MONTH=$(date +%m)
    DAY=$(date +%d)
fi

# 创建目录
TARGET_DIR="$YEAR/$MONTH"
mkdir -p "$TARGET_DIR"

# 复制文件
TARGET_FILE="$TARGET_DIR/$DAY.html"
cp "$SOURCE_FILE" "$TARGET_FILE"
echo "✅ 已复制到 $TARGET_FILE"

# 更新 index.html - 添加新日期链接
INDEX_FILE="index.html"
if [ -f "$INDEX_FILE" ]; then
    # 检查是否已存在该日期
    if grep -q "$YEAR/$MONTH/$DAY.html" "$INDEX_FILE"; then
        echo "⚠️  日期 $YEAR-$MONTH-$DAY 已存在于首页，跳过更新"
    else
        # 在第一个 day-list div 中插入新链接（插入到最前面）
        NEW_LINK="                        <a href=\"./$YEAR/$MONTH/$DAY.html\" class=\"day-link\">\n                            <span class=\"date\">$MONTH-$DAY</span>\n                            <span>AI 资讯快报</span>\n                            <span class=\"tag\">12板块</span>\n                        </a>"
        
        # 使用临时文件
        awk -v link="$NEW_LINK" '
            /<div class="day-list">/ {
                print
                print link
                next
            }
            { print }
        ' "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"
        
        echo "✅ 已更新首页归档列表"
    fi
fi

# Git 提交并推送
if [ -d ".git" ]; then
    git add .
    git commit -m "add: $YEAR-$MONTH-$DAY bulletin"
    git push
    echo "✅ 已推送到 GitHub"
    echo ""
    echo "🌐 在线地址: https://你的用户名.github.io/ai-news-bulletin/$YEAR/$MONTH/$DAY.html"
else
    echo ""
    echo "⚠️  当前目录不是 Git 仓库"
    echo "    请按 README.md 中的步骤初始化并推送到 GitHub"
fi

echo ""
echo "📁 本期归档: $TARGET_FILE"
