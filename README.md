# AI 资讯快报归档站

每日自动生成的 AI 行业资讯快报，按日期归档，支持浏览器直接阅读。

🔗 **在线访问地址**：`https://你的用户名.github.io/ai-news-bulletin/`

---

## 项目结构

```
ai-news-bulletin/
├── index.html          # 归档首页（按年/月/日自动排列）
├── 2026/
│   └── 04/
│       └── 24.html     # 2026-04-24 的快报
├── push.sh             # 一键推送到 GitHub 脚本
├── add-bulletin.sh     # 添加新一期快报的脚本
└── .github/
    └── workflows/
        └── deploy.yml  # 自动部署配置（可选）
```

---

## 快速开始（5分钟部署）

### 第1步：在 GitHub 创建仓库

1. 打开 [github.com/new](https://github.com/new)
2. 仓库名称填 `ai-news-bulletin`
3. 选择 **Public**（公开）
4. 不要勾选 "Add a README"（我们已经有了）
5. 点击 **Create repository**

### 第2步：推送本地代码

```bash
# 进入项目目录
cd ai-news-bulletin

# 初始化 Git 仓库
git init
git add .
git commit -m "init: AI news bulletin archive"

# 关联远程仓库（把 USERNAME 换成你的 GitHub 用户名）
git remote add origin https://github.com/USERNAME/ai-news-bulletin.git

# 推送
git branch -M main
git push -u origin main
```

### 第3步：开启 GitHub Pages

1. 打开仓库页面 → **Settings** → **Pages**
2. Source 选择 **Deploy from a branch**
3. Branch 选择 `main`，文件夹选择 `/(root)`
4. 点击 **Save**
5. 等待 1-2 分钟，访问 `https://USERNAME.github.io/ai-news-bulletin/`

---

## 每日发布新快报

### 方式一：手动复制（适合首次）

```bash
# 1. 把生成的 HTML 复制到对应日期目录
mkdir -p 2026/04
cp /path/to/AI_News_Bulletin_2026-04-25.html 2026/04/25.html

# 2. 编辑 index.html，在 timeline 中添加新日期链接
# （或使用下方的自动化脚本）

# 3. 推送
git add .
git commit -m "add: 2026-04-25 bulletin"
git push
```

### 方式二：使用自动化脚本（推荐）

```bash
# 添加新一期快报
./add-bulletin.sh /path/to/AI_News_Bulletin_2026-04-25.html

# 脚本会自动：
# 1. 按日期创建目录结构（如 2026/04/25.html）
# 2. 更新 index.html 首页的归档列表
# 3. 提交并推送到 GitHub
```

### 方式三：配置 GitHub Actions 全自动（高级）

仓库已包含 `.github/workflows/deploy.yml`。如果你希望完全自动化，可以：

1. 在本地或服务器设置定时任务（cron），每天生成快报后推送到 GitHub
2. 或者配置 webhook，让 QoderWork 生成完成后自动触发推送

---

## 自定义域名（可选）

如果你想用 `news.yourcompany.com` 这样的域名：

1. 在仓库根目录创建 `CNAME` 文件，内容写你的域名：
   ```
   news.yourcompany.com
   ```
2. 在你的域名 DNS 提供商处添加 CNAME 记录：
   - 主机记录：`news`
   - 记录值：`USERNAME.github.io`
3. 在 GitHub Pages 设置中，Custom domain 填入你的域名，点击 Save

---

## 技术说明

- **托管**：GitHub Pages（免费、稳定、全球 CDN）
- **构建**：纯静态 HTML，无需构建步骤
- **更新频率**：每日
- **访问控制**：公开（适合对外展示）

---

## 常见问题

**Q: 为什么不用 Cloudflare Pages / Vercel / Netlify？**  
A: GitHub Pages 与 GitHub 仓库天然集成，有完整的版本历史，且完全免费。如果你已有 GitHub 账号，这是最简单的方案。其他平台也可以，推送方式类似。

**Q: 可以改成公司内部访问吗？**  
A: 可以。方案一：把仓库设为 Private，使用 GitHub Enterprise 的 Pages 功能。方案二：把静态文件部署到公司内网服务器或 NAS。方案三：上传到公司的 Confluence/Notion/语雀等知识库。

**Q: 文件名是中文会有问题吗？**  
A: GitHub Pages 对中文文件名支持不太好，所以我们使用 `2026/04/24.html` 这种纯英文路径，归档首页显示中文日期。
