# 🔥 海外爆款选品自动化系统

每天自动抓取 Amazon 热销商品数据，生成 TOP 10 选品报告。

## 功能特点

- 🌍 **多市场覆盖**：美国、英国、德国
- 📈 **双榜数据**：Movers & Shakers + Best Sellers
- 🎯 **营销建议**：每个商品附带定制营销策略
- ⏰ **每日自动更新**：GitHub Actions 定时执行

## 查看报告

📊 **最新报告**：[reports/latest.html](reports/latest.html)

## 手动触发

1. 进入 GitHub 仓库的 **Actions** 页面
2. 选择 **🔥 海外爆款选品每日抓取**
3. 点击 **Run workflow**

## 自动执行时间

- **UTC 0:00**（北京时间 **08:00**）

## 项目结构

```
├── .github/workflows/
│   └── daily-scrape.yml    # GitHub Actions 工作流
├── reports/
│   ├── latest.html         # 最新报告
│   └── hot_products_YYYYMMDD.html  # 历史报告
├── scraper.py              # 爬虫脚本
├── requirements.txt        # Python 依赖
└── README.md
```

## 本地运行

```bash
pip install -r requirements.txt
playwright install chromium
python scraper.py
```
