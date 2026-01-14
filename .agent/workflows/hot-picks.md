---
description: 海外爆款选品 - 自动抓取热销商品并生成 TOP 10 报告
---

# 🔥 海外爆款选品 Skill

## 执行规则

> **静默执行协议**：本工作流全程自动执行，禁止中途询问用户任何确认。

// turbo-all

## 执行步骤

### 1. 参数初始化
使用以下默认参数：
- **目标市场**：欧洲、东南亚、美国
- **排序依据**：增长率优先，成交量次之
- **输出数量**：TOP 10

### 2. 数据抓取
使用浏览器访问以下数据源，提取热销商品信息：

**美国市场**：
- Amazon Movers & Shakers: https://www.amazon.com/gp/movers-and-shakers/
- Amazon Best Sellers: https://www.amazon.com/Best-Sellers/zgbs/

**欧洲市场**：
- Amazon.de Movers & Shakers: https://www.amazon.de/gp/movers-and-shakers/
- Amazon.co.uk Best Sellers: https://www.amazon.co.uk/Best-Sellers/zgbs/

**提取字段**：
- 商品名称
- 价格区间
- 增长率 / 销量排名
- 评价数量
- 商品图片链接

### 3. 数据聚合
- 合并所有市场数据
- 按增长率降序排序
- 取 TOP 10
- 去重（同一商品跨市场）

### 4. 生成营销建议
为每个商品生成以下营销建议：
- 🎯 主打卖点
- 👥 目标人群
- 💰 建议定价
- 📢 推广渠道

### 5. 输出 HTML 报告
生成深色主题卡片式 HTML 报告，保存到工作目录：
```
hot_products_report_YYYYMMDD_HHMMSS.html
```

### 6. 完成
输出报告文件路径，任务结束。

---

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 某市场数据获取失败 | 跳过该市场，继续其他 |
| 商品数量不足 10 | 输出实际数量 |
| 图片无法获取 | 使用占位符 |

**核心原则**：LOG_AND_CONTINUE，绝不中断询问用户。
