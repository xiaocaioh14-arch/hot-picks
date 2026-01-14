# 🔥 海外爆款选品自动化教程

> 从零开始搭建一套自动化海外电商选品系统，每天自动抓取 Amazon 热销数据并推送到飞书

---

## 📖 目录

1. [项目简介](#项目简介)
2. [整体思路](#整体思路)
3. [核心难点解析](#核心难点解析)
4. [准备工作](#准备工作)
5. [完整配置流程](#完整配置流程)
6. [常见问题解答](#常见问题解答)

---

## 项目简介

### 这个项目能做什么？

这是一套**全自动化的海外电商选品工具**，它能够：

- ⏰ **每天定时** 自动抓取 Amazon 美国站和欧洲站的热销商品
- 📊 **智能筛选** 增长最快的 TOP 10 商品
- 📝 **生成报告** 输出精美的 HTML 网页报告
- 🌐 **在线访问** 无需下载，浏览器直接查看
- 📱 **飞书推送** 报告生成后自动发送通知到飞书

### 为什么需要这个工具？

做跨境电商或海外营销时，**选品** 是最重要的一环。但手动去 Amazon 查看热销榜单非常耗时，而且容易错过最佳时机。这个工具帮你：

1. **节省时间** - 全自动运行，无需人工操作
2. **不错过机会** - 每天固定时间推送，第一时间发现新爆款
3. **数据可靠** - 直接抓取 Amazon 官方榜单数据

---

## 整体思路

### 工作流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    🔄 每日自动化流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ⏰ 定时触发              🌐 数据抓取              📊 生成报告    │
│   (北京时间 08:00)    →    (Amazon 热销榜)    →    (HTML 网页)   │
│         │                       │                      │        │
│         ↓                       ↓                      ↓        │
│   GitHub Actions          Playwright 爬虫          精美模板      │
│                                                                 │
│         │                       │                      │        │
│         └───────────────────────┴──────────────────────┘        │
│                                 ↓                               │
│                    ┌────────────┴────────────┐                  │
│                    │                         │                  │
│               📤 推送到 GitHub           📱 飞书通知              │
│                    │                         │                  │
│                    ↓                         ↓                  │
│            GitHub Pages 托管           消息卡片推送               │
│            (在线查看报告)              (手机/电脑接收)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈说明

| 组件 | 作用 | 为什么选它 |
|------|------|-----------|
| **Python** | 编写爬虫脚本 | 语法简单，库丰富 |
| **Playwright** | 自动化浏览器 | 能处理动态网页，比 Selenium 更快 |
| **GitHub Actions** | 定时执行任务 | 免费、稳定、无需服务器 |
| **GitHub Pages** | 托管 HTML 报告 | 免费、自动部署 |
| **飞书 Webhook** | 消息推送 | 配置简单，支持消息卡片 |

---

## 核心难点解析

### 难点 1：动态网页爬取

> [!WARNING]
> **问题**：Amazon 页面是动态加载的 JavaScript 网页，普通的 requests 库无法获取完整内容。

**解决方案**：使用 Playwright 自动化浏览器

```python
# 普通 requests（❌ 无法获取动态内容）
import requests
response = requests.get("https://amazon.com/...")

# Playwright（✅ 完整渲染页面后抓取）
from playwright.async_api import async_playwright
async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    await page.goto("https://amazon.com/...")
    # 等待页面加载完成后再抓取
    await page.wait_for_selector(".product-item")
```

---

### 难点 2：GitHub Actions 权限问题

> [!CAUTION]
> **问题**：GitHub Actions 默认只有只读权限，无法将报告推送回仓库。
> 
> 错误信息：`error: failed to push some refs... Permission denied`

**解决方案**：

1. 进入仓库 **Settings** → **Actions** → **General**
2. 找到 **Workflow permissions**
3. 选择 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**
5. 点击 **Save**

![权限设置示意](https://docs.github.com/assets/images/help/repository/actions-workflow-permissions.png)

---

### 难点 3：定时任务时区问题

> [!IMPORTANT]
> **问题**：GitHub Actions 使用 UTC 时区，北京时间比 UTC 早 8 小时。
> 
> 如果你想在北京时间 08:00 运行，需要设置为 UTC 00:00。

**配置示例**：

```yaml
on:
  schedule:
    # UTC 时间 00:00 = 北京时间 08:00
    - cron: '0 0 * * *'
```

**cron 表达式说明**：

```
┌───────────── 分钟 (0 - 59)
│ ┌───────────── 小时 (0 - 23)
│ │ ┌───────────── 日 (1 - 31)
│ │ │ ┌───────────── 月 (1 - 12)
│ │ │ │ ┌───────────── 星期 (0 - 6，0=周日)
│ │ │ │ │
0 0 * * *   每天 UTC 00:00（北京时间 08:00）
```

---

### 难点 4：飞书 Webhook 配置

> [!NOTE]
> **关键点**：飞书机器人的 Webhook 地址需要保密，不能直接写在代码里。

**正确做法**：使用 GitHub Secrets 存储敏感信息

```yaml
# 工作流配置（✅ 安全）
env:
  FEISHU_WEBHOOK: ${{ secrets.FEISHU_WEBHOOK }}

# 直接写在代码里（❌ 不安全，会被恶意调用）
webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

---

## 准备工作

在开始配置之前，请确保你已经准备好以下账号和工具：

### 必需账号

| 账号 | 用途 | 注册地址 |
|------|------|----------|
| **GitHub 账号** | 存放代码、运行自动化任务 | https://github.com |
| **飞书账号** | 接收推送通知 | https://www.feishu.cn |

### 可选工具

| 工具 | 用途 | 说明 |
|------|------|------|
| **VS Code** | 编辑代码 | 推荐安装，方便修改配置 |
| **Git** | 提交代码 | 用于将代码推送到 GitHub |

---

## 完整配置流程

### 第一步：创建 GitHub 仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 输入仓库名称（如 `hot-picks`）
4. 选择 **Public**（GitHub Pages 免费版需要公开仓库）
5. 点击 **Create repository**

> [!TIP]
> 建议仓库名使用英文和短横线，避免中文或特殊字符。

---

### 第二步：上传项目代码

将以下文件上传到你的仓库：

```
仓库根目录/
├── .github/
│   └── workflows/
│       └── daily-scrape.yml    # 自动化工作流配置
├── reports/                     # 报告输出目录（初始可为空）
├── scraper.py                   # 爬虫主脚本
└── requirements.txt             # Python 依赖
```

> [!IMPORTANT]
> **关键文件说明**：
> 
> - `daily-scrape.yml`：定义了什么时候运行、运行什么命令
> - `scraper.py`：核心爬虫逻辑，抓取数据和生成报告
> - `requirements.txt`：列出需要安装的 Python 库

---

### 第三步：配置 GitHub Actions 权限

> [!CAUTION]
> **这一步非常重要！** 如果不配置，工作流会因为权限问题失败。

1. 进入你的仓库页面
2. 点击 **Settings**（设置）
3. 左侧菜单选择 **Actions** → **General**
4. 滚动到 **Workflow permissions** 部分
5. 选择 **Read and write permissions**
6. ✅ 勾选 **Allow GitHub Actions to create and approve pull requests**
7. 点击 **Save** 保存

---

### 第四步：启用 GitHub Pages

让你的报告可以在线访问：

1. 进入仓库 **Settings**
2. 左侧菜单选择 **Pages**
3. **Source** 选择 **Deploy from a branch**
4. **Branch** 选择 `main`（或 `master`），文件夹选择 `/ (root)`
5. 点击 **Save**

几分钟后，你的报告就可以通过以下格式的链接访问：

```
https://你的用户名.github.io/仓库名/reports/latest.html
```

---

### 第五步：创建飞书机器人

1. 打开飞书桌面端或网页版
2. 创建一个新群聊（或使用现有群聊）
3. 点击群聊右上角的 **⚙️ 设置**
4. 选择 **群机器人** → **添加机器人**
5. 选择 **自定义机器人**
6. 设置机器人名称（如：`海外爆款选品助手`）
7. **复制 Webhook 地址**（非常重要！）

> [!WARNING]
> **Webhook 地址格式示例**：
> ```
> https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
> ```
> 
> 这个地址要保密，不要分享给他人！

---

### 第六步：配置 GitHub Secret

将飞书 Webhook 地址安全地存储到 GitHub：

1. 进入仓库 **Settings**
2. 左侧菜单选择 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. **Name** 填写：`FEISHU_WEBHOOK`
5. **Secret** 填写：你的飞书 Webhook 地址
6. 点击 **Add secret**

---

### 第七步：手动触发测试

确认配置是否正确：

1. 进入仓库的 **Actions** 页面
2. 左侧选择 **🔥 海外爆款选品每日抓取**
3. 点击 **Run workflow** → **Run workflow**
4. 等待工作流运行完成（约 1-2 分钟）

> [!TIP]
> **如何判断是否成功？**
> 
> ✅ 成功标志：
> - 工作流显示绿色 ✓
> - 飞书群收到消息通知
> - `reports/` 目录下生成了 HTML 文件
> 
> ❌ 失败排查：
> - 点击工作流查看日志
> - 常见错误见下方「常见问题解答」

---

## 常见问题解答

### Q1：工作流显示 "Permission denied" 错误

> [!CAUTION]
> **原因**：GitHub Actions 没有写入权限

**解决方法**：参考「第三步：配置 GitHub Actions 权限」

---

### Q2：飞书没有收到通知

> [!NOTE]
> **可能原因**：
> 1. Webhook 地址配置错误
> 2. GitHub Secret 名称拼写错误
> 3. 机器人被移出群聊

**排查步骤**：

1. 检查 GitHub Secret 名称是否为 `FEISHU_WEBHOOK`（注意大小写）
2. 检查 Webhook 地址是否完整复制
3. 确认机器人仍在群聊中

---

### Q3：GitHub Pages 页面显示 404

> [!TIP]
> **可能原因**：Pages 还没部署完成，或者路径错误

**解决方法**：

1. 等待几分钟让 GitHub 完成部署
2. 确认访问路径正确：`https://用户名.github.io/仓库名/reports/latest.html`
3. 检查 `reports/` 目录是否有文件

---

### Q4：如何修改抓取时间？

修改 `.github/workflows/daily-scrape.yml` 中的 cron 表达式：

```yaml
on:
  schedule:
    # 修改这里的时间
    - cron: '0 0 * * *'  # UTC 00:00 = 北京 08:00
```

**常用时间对照表**：

| 北京时间 | UTC 时间 | cron 表达式 |
|---------|---------|-------------|
| 06:00 | 22:00 (前一天) | `0 22 * * *` |
| 08:00 | 00:00 | `0 0 * * *` |
| 12:00 | 04:00 | `0 4 * * *` |
| 20:00 | 12:00 | `0 12 * * *` |

---

### Q5：如何添加更多市场/类目？

编辑 `scraper.py` 中的 `DATA_SOURCES` 配置：

```python
DATA_SOURCES = {
    "usa": {
        "movers": "https://www.amazon.com/gp/movers-and-shakers/...",
        "best": "https://www.amazon.com/Best-Sellers/..."
    },
    # 添加新市场
    "japan": {
        "movers": "https://www.amazon.co.jp/gp/movers-and-shakers/...",
        "best": "https://www.amazon.co.jp/Best-Sellers/..."
    }
}
```

---

## 🎉 完成！

恭喜你完成了全部配置！现在系统会：

1. ⏰ 每天北京时间 08:00 自动运行
2. 🔄 抓取 Amazon 美国站和欧洲站热销数据
3. 📊 生成精美的 TOP 10 报告
4. 📱 自动推送到你的飞书群

**有问题？** 欢迎提 Issue 或联系作者！

---

> 📝 本教程由 AI 辅助生成，最后更新：2026-01-14
