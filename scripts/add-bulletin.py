#!/usr/bin/env python3
"""
AI 资讯快报归档自动更新脚本
用法: python3 add-bulletin.py <bulletin_html_file> ["标题描述"]

功能:
1. 从文件名提取日期 (YYYY-MM-DD)
2. 复制 HTML 到 YYYY/MM/DD.html
3. 在 index.html 时间线中插入新日期链接（按日期倒序）
4. 如果年份/月份不存在，自动创建新的分组
5. 更新已归档期数统计
6. 自动执行 git add / commit / push
"""

import sys
import os
import re
import shutil
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(REPO_DIR, "index.html")


def extract_date_from_filename(filepath):
    """从文件名提取日期，支持 YYYY-MM-DD 格式"""
    basename = os.path.basename(filepath)
    # 尝试匹配文件名中的日期
    m = re.search(r'(\d{4})[-_]*(\d{2})[-_]*(\d{2})', basename)
    if m:
        year, month, day = m.groups()
        return year, month, day
    raise ValueError(f"无法从文件名 '{basename}' 提取日期，需要包含 YYYY-MM-DD 格式")


def get_date_title(filepath, custom_title=None):
    """获取日期标题，优先使用自定义标题，否则从 HTML <title> 提取"""
    if custom_title:
        return custom_title
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'<title>([^<]*)</title>', content)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return "AI 资讯快报"


def copy_bulletin(filepath, year, month, day):
    """复制 HTML 到日期目录，并注入归档首页链接"""
    dest_dir = os.path.join(REPO_DIR, year, month)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"{day}.html")
    
    # 读取源文件内容
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有归档链接，如果没有则注入
    archive_link = f'https://maplelian.github.io/ai-news-bulletin/'
    if 'archive-link' not in content:
        # 在 date-badge 后插入归档链接
        content = content.replace(
            '</span>\n  </div>\n</header>',
            f'</span>\n    <br>\n    <a href="{archive_link}" class="archive-link" target="_blank">&#x1F4C1; 查看所有归档期数</a>\n  </div>\n</header>'
        )
        
        # 注入 CSS 样式（在 .hero .date-badge 后）
        archive_css = '''.hero .archive-link { display: inline-flex; align-items: center; gap: 0.4rem; margin-top: 1rem; color: #fbbf24; text-decoration: none; font-size: 0.9rem; font-weight: 600; padding: 0.5rem 1.25rem; border-radius: 999px; border: 1px solid rgba(251,191,36,0.3); background: rgba(251,191,36,0.1); transition: all 0.3s; }
.hero .archive-link:hover { background: rgba(251,191,36,0.2); border-color: rgba(251,191,36,0.5); color: #fde68a; }'''
        content = content.replace(
            '.hero .date-badge { display: inline-block;',
            f'{archive_css}\n.hero .date-badge {{ display: inline-block;'
        )
    
    # 写入目标文件
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[复制] {filepath} -> {dest_path}")
    return dest_path


def update_index(year, month, day, title):
    """更新 index.html 时间线 + 最新一期卡片"""
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 更新最新一期卡片
    date_str = f"{year}年{int(month)}月{int(day)}日"
    latest_pattern = r'<div class="latest-card">.*?</div>\s*</div>\s*<a href="[^"]*">[^<]*</a>\s*</div>'
    latest_replacement = f'''<div class="latest-card">
    <div>
      <div class="text">最新一期：{date_str}</div>
      <div class="date">覆盖 50+ 条精选资讯 · 3 大核心趋势 · 3 条今日头条</div>
    </div>
    <a href="./{year}/{month}/{day}.html">阅读 &rarr;</a>
  </div>'''
    content = re.sub(latest_pattern, latest_replacement, content, flags=re.DOTALL)

    # 2. 更新统计数字 - 增加期数
    content = re.sub(
        r'(<div class="stat-value">)(\d+)(</div><div class="stat-label">期已归档</div>)',
        lambda m: f'{m.group(1)}{int(m.group(2)) + 1}{m.group(3)}',
        content
    )

    # 2. 构建新的日期链接 HTML
    new_link = f'''          <a href="./{year}/{month}/{day}.html" class="day-link">
            <span class="date-badge">{month}-{day}</span>
            <span class="title">{title}</span>
            <span class="arrow">→</span>
          </a>'''

    # 3. 检查该年份是否已存在
    year_pattern = rf'<div class="year-label">{year}</div>'
    if not re.search(year_pattern, content):
        # 创建新年份组 - 插入到 timeline 的开始（最新的年份在最前面）
        new_year_block = f'''    <div class="year-group">
      <div class="year-label">{year}</div>
      <div class="month-group">
        <div class="month-label">{get_month_label(month)}</div>
        <div class="day-list">
{new_link}
        </div>
      </div>
    </div>'''
        # 在第一个 .year-group 之前插入
        content = re.sub(
            r'(<div class="timeline">\s*)',
            rf'\1\n{new_year_block}\n',
            content
        )
        print(f"[新建] 年份 {year}，月份 {get_month_label(month)}")
    else:
        # 年份存在，检查月份
        month_label = get_month_label(month)
        month_pattern = rf'(<div class="year-label">{year}</div>.*?<div class="month-label">{month_label}</div>\s*<div class="day-list">)(.*?)(</div>)'
        month_match = re.search(month_pattern, content, re.DOTALL)

        if month_match:
            # 月份存在，按日期倒序插入
            existing_links = month_match.group(2)
            # 检查是否已存在该日期
            if f'{month}-{day}' in existing_links:
                print(f"[跳过] {year}-{month}-{day} 已存在于时间线中")
                with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                    f.write(content)
                return

            # 插入到月份 day-list 的开头（保持倒序）
            new_links = f"\n{new_link}\n{existing_links.rstrip()}"
            content = content[:month_match.start(2)] + new_links + content[month_match.end(2):]
            print(f"[插入] {year}-{month}-{day} 到 {month_label}")
        else:
            # 年份存在但月份不存在 - 在年份内的最后插入新月份
            # 找到 year-group 的末尾，在其前插入新月份
            year_block_pattern = rf'(<div class="year-label">{year}</div>.*?</div>\s*)(</div>\s*</div>\s*<div class="year-group">|</div>\s*</div>\s*</div>\s*</div>\s*<footer>)'
            year_match = re.search(year_block_pattern, content, re.DOTALL)
            if year_match:
                new_month_block = f'''      <div class="month-group">
        <div class="month-label">{month_label}</div>
        <div class="day-list">
{new_link}
        </div>
      </div>
'''
                insert_pos = year_match.start(2)
                content = content[:insert_pos] + new_month_block + content[insert_pos:]
                print(f"[新建] 月份 {month_label} 到年份 {year}")
            else:
                print(f"[警告] 无法找到年份 {year} 的插入位置")

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[更新] {INDEX_FILE}")


def get_month_label(month_num):
    """月份数字转中文标签"""
    labels = {
        '01': '一月', '02': '二月', '03': '三月', '04': '四月',
        '05': '五月', '06': '六月', '07': '七月', '08': '八月',
        '09': '九月', '10': '十月', '11': '十一月', '12': '十二月'
    }
    return labels.get(month_num, f'{month_num}月')


def git_commit_push(year, month, day):
    """执行 git add / commit / push"""
    os.chdir(REPO_DIR)
    os.system('git add .')
    commit_msg = f'add: {year}-{month}-{day} bulletin'
    ret = os.system(f'git commit -m "{commit_msg}"')
    if ret != 0:
        print("[提示] git commit 没有新变更或出现错误")
    ret = os.system('git push origin main')
    if ret == 0:
        print(f"[推送] 成功发布到 GitHub Pages")
    else:
        print(f"[错误] git push 失败，请检查网络或认证")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 add-bulletin.py <bulletin_html_file> [\"标题描述\"]")
        print("示例: python3 add-bulletin.py /path/to/AI_News_Bulletin_2026-04-28.html")
        sys.exit(1)

    filepath = sys.argv[1]
    custom_title = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(filepath):
        print(f"[错误] 文件不存在: {filepath}")
        sys.exit(1)

    year, month, day = extract_date_from_filename(filepath)
    title = get_date_title(filepath, custom_title)

    print(f"\n{'='*50}")
    print(f"日期: {year}-{month}-{day}")
    print(f"标题: {title}")
    print(f"{'='*50}\n")

    copy_bulletin(filepath, year, month, day)
    update_index(year, month, day, title)
    git_commit_push(year, month, day)

    print(f"\n{'='*50}")
    print(f"完成! 访问: https://maplelian.github.io/ai-news-bulletin/")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
