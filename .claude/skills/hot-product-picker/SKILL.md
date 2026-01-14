---
name: hot-product-picker
description: 自动抓取海外电商平台热销商品数据，生成 TOP 10 爆款选品报告，并为每个商品提供营销建议。支持多市场（欧洲、东南亚、美国），输出精美 HTML 卡片式报告。
license: MIT
---

# 🔥 海外爆款选品 Skill (Hot Product Picker)

## ⚡️ 静默执行协议 (Quiet Mode Protocol)

> [!CAUTION]
> **执行本 Skill 时，必须严格遵守以下协议：**
>
> 1. **禁止询问确认**：Do not ask for confirmation to proceed.
> 2. **一次性完成**：Generate the full output in one go.
> 3. **默认值填充**：If data is missing, use the defined defaults.
> 4. **静默错误处理**：Log errors silently and continue execution.
> 5. **绝不中断**：Never output "是否继续？"、"需要更多信息" 等打断工作流的语句。

---

## 🎯 触发条件 (Trigger)

当用户表达以下意图时触发此 Skill：

### ✅ 触发示例
- "帮我分析海外爆款商品"
- "找一下跨境电商热销品"
- "给我生成选品 TOP 10"
- "什么产品在国外卖得好"
- "海外热销榜分析"

### ❌ 不触发示例
- "帮我查某个具体商品的价格"（信息查询，非选品分析）
- "国内电商有什么爆款"（非海外市场）

---

## 📥 输入参数 (Input)

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `markets` | string[] | 否 | `["europe", "southeast_asia", "usa"]` | 目标市场 |
| `top_count` | number | 否 | `10` | 返回商品数量 |
| `sort_by` | string | 否 | `"growth_rate"` | 排序依据：growth_rate / sales_volume |

**默认行为**：用户未指定任何参数时，自动使用默认值执行，**绝不询问**。

---

## 📤 输出 (Output)

生成一个 HTML 文件，保存到工作目录：

```
hot_products_report_YYYYMMDD_HHMMSS.html
```

### 报告结构
```
├── 🏠 报告头部
│   ├── 标题：海外爆款选品 TOP 10
│   ├── 生成时间
│   └── 数据来源说明
├── 📦 商品卡片 x 10
│   ├── 商品图片
│   ├── 商品名称
│   ├── 增长率 / 销量排名
│   ├── 价格区间
│   ├── 来源平台
│   └── 🎯 营销建议（3-5条）
└── 📝 报告尾部
    └── 免责声明 & 数据时效性说明
```

---

## 🔄 执行流程 (Workflow)

### Step 1: 参数解析与默认值填充
```
IF 用户未指定 markets THEN markets = ["europe", "southeast_asia", "usa"]
IF 用户未指定 top_count THEN top_count = 10
IF 用户未指定 sort_by THEN sort_by = "growth_rate"
```

### Step 2: 数据源选择
根据目标市场，选择可访问的数据源：

| 市场 | 首选数据源 | 备用数据源 |
|------|------------|------------|
| Europe | Amazon.de/co.uk Movers & Shakers | Google Trends |
| Southeast Asia | Shopee Top Products | Amazon.sg |
| USA | Amazon.com Best Sellers | Google Shopping Trends |

### Step 3: 浏览器模拟抓取
使用 `browser_subagent` 访问目标页面：

```
FOR EACH data_source IN selected_sources:
    1. 打开页面
    2. 等待加载完成
    3. 提取商品列表（名称、价格、排名、增长率、图片）
    4. IF 失败 THEN 记录日志 → 尝试备用源 → 继续
```

### Step 4: 数据聚合与排序
```
1. 合并所有市场数据
2. 按 sort_by 字段排序（默认增长率）
3. 取 TOP N 商品
4. 去重（同一商品多市场出现）
```

### Step 5: 生成营销建议
为每个商品生成营销建议：

```
营销建议模板:
├── 🎯 主打卖点：基于商品特性
├── 👥 目标人群：基于品类和价格
├── 💰 建议定价：参考原价 + 利润空间
├── 📢 推广渠道：基于市场特性
└── ⚠️ 注意事项：物流、合规等
```

### Step 6: 渲染 HTML 报告
使用现代卡片式设计生成 HTML：

```html
<!-- 设计要点 -->
- 深色渐变主题
- 卡片悬停动效
- 响应式布局
- 数据可视化（增长率进度条）
```

### Step 7: 保存并输出
```
1. 保存 HTML 到工作目录
2. 输出文件路径给用户
3. 完成，不询问后续操作
```

---

## 🛡️ 错误处理 (Error Handling)

| 错误场景 | 处理方式 | 用户可见性 |
|----------|----------|------------|
| 网络超时 | 重试 2 次 → 跳过 | 报告中标注"数据暂不可用" |
| 反爬拦截 | 切换备用数据源 | 静默处理 |
| 页面结构变化 | 使用通用解析 → 失败则跳过 | 报告中减少该来源数据 |
| 图片加载失败 | 使用占位图 | 显示占位图 |
| TOP 10 不足 | 输出实际数量 | 报告标注实际数量 |
| 全部数据源失败 | 输出空报告 + 说明 | 说明"当前无法获取数据" |

**核心原则**：`LOG_AND_CONTINUE`，绝不抛出错误给用户。

---

## 📝 Few-Shot Examples

### ✅ Good Case: 一步到位

**用户输入**：
```
帮我分析一下海外爆款商品
```

**正确执行**：
```
[执行中] 正在抓取欧洲市场数据...
[执行中] 正在抓取东南亚市场数据...
[执行中] 正在抓取美国市场数据...
[执行中] 数据聚合与排序...
[执行中] 生成营销建议...
[完成] 报告已生成：hot_products_report_20260114_095500.html
```

---

### ❌ Anti-Pattern: 中途打断（禁止！）

**用户输入**：
```
帮我分析一下海外爆款商品
```

**错误执行（禁止）**：
```
❌ 请问您想分析哪个市场的商品？
   1. 欧洲
   2. 东南亚
   3. 美国
   4. 全部

❌ 您希望按什么指标排序？
   1. 增长率
   2. 销量

❌ 我遇到了一些问题，是否继续？
```

> [!WARNING]
> **以上任何一种中途询问都是严重错误，必须避免！**

---

## 🎨 HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海外爆款选品 TOP 10</title>
    <style>
        :root {
            --bg-primary: #0f0f23;
            --bg-card: #1a1a2e;
            --accent: #00d4ff;
            --accent-secondary: #ff6b6b;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 100%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 40px 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header .meta {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }
        
        .product-card {
            background: var(--bg-card);
            border-radius: 16px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .product-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,212,255,0.2);
        }
        
        .product-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: #2a2a4a;
        }
        
        .product-info {
            padding: 20px;
        }
        
        .product-rank {
            display: inline-block;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            color: white;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 10px;
        }
        
        .product-name {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .metrics {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .metric {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9rem;
        }
        
        .metric.growth {
            color: #4ade80;
        }
        
        .metric.price {
            color: var(--accent);
        }
        
        .marketing-tips {
            background: rgba(0,212,255,0.1);
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .marketing-tips h4 {
            font-size: 0.9rem;
            color: var(--accent);
            margin-bottom: 10px;
        }
        
        .marketing-tips ul {
            list-style: none;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .marketing-tips li {
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .marketing-tips li::before {
            content: "→";
            position: absolute;
            left: 0;
            color: var(--accent);
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔥 海外爆款选品 TOP 10</h1>
            <p class="meta">生成时间：{{TIMESTAMP}} | 数据来源：多平台聚合</p>
        </header>
        
        <div class="products-grid">
            {{PRODUCT_CARDS}}
        </div>
        
        <footer class="footer">
            <p>⚠️ 数据仅供参考，具体选品请结合实际市场情况分析</p>
            <p>数据时效性：抓取时快照，榜单每日更新</p>
        </footer>
    </div>
</body>
</html>
```

---

## 🧪 验证清单 (Validation Checklist)

执行后自检：

- [ ] 是否全程无中断询问？
- [ ] 是否生成了 HTML 文件？
- [ ] 报告中是否包含 TOP 10 商品？
- [ ] 每个商品是否有营销建议？
- [ ] 遇到错误是否静默处理？

---

## 📌 版本信息

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1 | 2026-01-14 | MVP 版本，支持多市场数据抓取 |
