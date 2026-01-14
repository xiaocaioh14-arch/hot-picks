"""
海外爆款选品自动抓取脚本
使用 Playwright 抓取 Amazon 热销榜数据，生成 HTML 报告
支持飞书推送通知
"""

import asyncio
import json
import os
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# GitHub Pages 报告地址
REPORT_URL = "https://xiaocaioh14-arch.github.io/hot-picks/reports/latest.html"

# 数据源配置
DATA_SOURCES = {
    "usa": {
        "name": "美国",
        "flag": "🇺🇸",
        "movers_shakers": "https://www.amazon.com/gp/movers-and-shakers/",
        "best_sellers": "https://www.amazon.com/Best-Sellers/zgbs/"
    },
    "uk": {
        "name": "英国",
        "flag": "🇬🇧",
        "movers_shakers": "https://www.amazon.co.uk/gp/movers-and-shakers/",
        "best_sellers": "https://www.amazon.co.uk/Best-Sellers/zgbs/"
    },
    "de": {
        "name": "德国",
        "flag": "🇩🇪",
        "movers_shakers": "https://www.amazon.de/gp/movers-and-shakers/",
        "best_sellers": "https://www.amazon.de/Best-Sellers/zgbs/"
    }
}

async def scrape_amazon_movers_shakers(page, url, market_info):
    """抓取 Amazon Movers & Shakers 页面"""
    products = []
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        # 滚动页面加载更多内容
        for _ in range(3):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(1000)
        
        # 提取商品信息
        items = await page.query_selector_all('[data-asin]')
        
        for i, item in enumerate(items[:15]):  # 取前15个
            try:
                name_el = await item.query_selector('span.a-size-base-plus, span.a-size-medium, .a-link-normal span')
                price_el = await item.query_selector('.a-price .a-offscreen, .a-price-whole')
                rank_el = await item.query_selector('.a-badge-text, .a-size-small')
                
                name = await name_el.inner_text() if name_el else "未知商品"
                price = await price_el.inner_text() if price_el else "价格待定"
                
                # 尝试提取增长率
                growth = "新进榜"
                growth_el = await item.query_selector('.a-size-small.a-color-success, .a-color-success')
                if growth_el:
                    growth_text = await growth_el.inner_text()
                    if '%' in growth_text:
                        growth = growth_text
                
                if name and len(name) > 5:
                    products.append({
                        "name": name[:80],
                        "price": price,
                        "growth": growth,
                        "market": market_info["name"],
                        "flag": market_info["flag"],
                        "source": "Movers & Shakers"
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"抓取 {market_info['name']} Movers & Shakers 失败: {e}")
    
    return products

async def scrape_amazon_best_sellers(page, url, market_info):
    """抓取 Amazon Best Sellers 页面"""
    products = []
    try:
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        # 滚动页面
        for _ in range(3):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(1000)
        
        # 提取商品信息
        items = await page.query_selector_all('.p13n-sc-uncoverable-faceout, [data-asin]')
        
        for i, item in enumerate(items[:10]):
            try:
                name_el = await item.query_selector('._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y, .a-link-normal span, .a-size-base-plus')
                price_el = await item.query_selector('.a-price .a-offscreen, ._cDEzb_p13n-sc-price_3mJ9Z')
                rating_el = await item.query_selector('.a-icon-alt, .a-size-small')
                
                name = await name_el.inner_text() if name_el else "未知商品"
                price = await price_el.inner_text() if price_el else "价格待定"
                
                if name and len(name) > 5:
                    products.append({
                        "name": name[:80],
                        "price": price,
                        "growth": f"#{i+1} 热销",
                        "market": market_info["name"],
                        "flag": market_info["flag"],
                        "source": "Best Sellers"
                    })
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"抓取 {market_info['name']} Best Sellers 失败: {e}")
    
    return products

def generate_marketing_tips(product):
    """生成营销建议"""
    name = product["name"].lower()
    
    # 根据商品类别生成不同建议
    if any(kw in name for kw in ["airpods", "headphone", "earbuds", "bluetooth"]):
        return {
            "卖点": "音质清晰 + 无线便携 + 长续航",
            "人群": "通勤族、运动爱好者、远程办公人群",
            "定价": "突出性价比，对标品牌价格8折",
            "渠道": "短视频开箱测评、科技博主合作"
        }
    elif any(kw in name for kw in ["kitchen", "scale", "cooking"]):
        return {
            "卖点": "精准便捷 + 厨房必备 + 高性价比",
            "人群": "烘焙爱好者、健康饮食人群、新手厨师",
            "定价": "低价引流款，建议¥39-69",
            "渠道": "美食博主搭配食谱推荐"
        }
    elif any(kw in name for kw in ["soap", "clean", "wash"]):
        return {
            "卖点": "天然成分 + 香氛怡人 + 环保补充装",
            "人群": "注重生活品质的家庭用户",
            "定价": "中端价位¥39-59",
            "渠道": "家居生活类 KOL、小红书种草"
        }
    elif any(kw in name for kw in ["skincare", "toner", "pad", "beauty"]):
        return {
            "卖点": "韩国护肤科技 + 毛孔清洁神器",
            "人群": "18-35岁女性、韩妆爱好者",
            "定价": "中高端¥99-169",
            "渠道": "美妆博主测评、抖音带货直播"
        }
    elif any(kw in name for kw in ["dumbbell", "fitness", "sport", "gym"]):
        return {
            "卖点": "舒适握感 + 家用健身必备",
            "人群": "居家健身人群、健身初学者",
            "定价": "性价比路线¥59-99",
            "渠道": "健身博主推荐、运动类社群"
        }
    elif any(kw in name for kw in ["bottle", "water", "cup"]):
        return {
            "卖点": "保温保冷 + 便携设计 + 高颜值",
            "人群": "户外运动爱好者、上班族",
            "定价": "中端¥89-159",
            "渠道": "运动户外社群、健身房合作"
        }
    elif any(kw in name for kw in ["case", "cover", "protect"]):
        return {
            "卖点": "保护设备 + 多款颜色 + 超低价",
            "人群": "数码产品用户、配件收集者",
            "定价": "低价爆款¥19.9-39.9",
            "渠道": "电商首页推荐、买正品送配件活动"
        }
    else:
        return {
            "卖点": "品质保证 + 性价比高",
            "人群": "大众消费者",
            "定价": "参考市场同类产品定价",
            "渠道": "多平台推广、社交媒体种草"
        }

def generate_html_report(products, timestamp):
    """生成 HTML 报告"""
    
    # 按增长率排序（新进榜排前面）
    def sort_key(p):
        if "新进榜" in p["growth"]:
            return 0
        elif "%" in p["growth"]:
            try:
                return 1 - int(p["growth"].replace("%", "").replace("+", "")) / 1000
            except:
                return 0.5
        else:
            return 0.8
    
    products.sort(key=sort_key)
    top_products = products[:10]
    
    # 生成商品卡片 HTML
    cards_html = ""
    for i, product in enumerate(top_products, 1):
        tips = generate_marketing_tips(product)
        
        # 选择图标
        name_lower = product["name"].lower()
        if any(kw in name_lower for kw in ["airpods", "headphone", "earbuds"]):
            icon = "🎧"
        elif any(kw in name_lower for kw in ["kitchen", "scale"]):
            icon = "⚖️"
        elif any(kw in name_lower for kw in ["soap", "clean"]):
            icon = "🧴"
        elif any(kw in name_lower for kw in ["skincare", "toner", "beauty"]):
            icon = "💊"
        elif any(kw in name_lower for kw in ["dumbbell", "fitness"]):
            icon = "🏋️"
        elif any(kw in name_lower for kw in ["bottle", "water"]):
            icon = "🥤"
        elif any(kw in name_lower for kw in ["case", "cover"]):
            icon = "📱"
        else:
            icon = "📦"
        
        cards_html += f'''
            <div class="product-card">
                <div class="product-image">{icon}</div>
                <span class="product-rank">#{i}</span>
                <span class="product-market">{product["flag"]} {product["market"]}</span>
                <div class="product-info">
                    <h3 class="product-name">{product["name"]}</h3>
                    <div class="metrics">
                        <span class="metric growth">📈 {product["growth"]}</span>
                        <span class="metric price">💰 {product["price"]}</span>
                        <span class="metric hot">🔥 {product["source"]}</span>
                    </div>
                    <div class="growth-bar">
                        <div class="growth-bar-fill" style="width: {90 - i*5}%"></div>
                    </div>
                    <div class="marketing-tips">
                        <h4>🎯 营销建议</h4>
                        <ul>
                            <li><strong>主打卖点</strong>：{tips["卖点"]}</li>
                            <li><strong>目标人群</strong>：{tips["人群"]}</li>
                            <li><strong>建议定价</strong>：{tips["定价"]}</li>
                            <li><strong>推广渠道</strong>：{tips["渠道"]}</li>
                        </ul>
                    </div>
                </div>
            </div>
        '''
    
    # 计算最高增长率
    max_growth = "新进榜"
    for p in top_products:
        if "%" in p["growth"]:
            max_growth = p["growth"]
            break
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>海外爆款选品 TOP 10 - {timestamp[:10]}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0f0f23;
            --bg-card: #1a1a2e;
            --accent: #00d4ff;
            --accent-secondary: #ff6b6b;
            --accent-green: #4ade80;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #16213e 100%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 40px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 50px; }}
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}
        .header .meta {{ color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; }}
        .header .meta span {{ display: inline-block; margin: 0 10px; }}
        .header .meta .separator {{ color: var(--accent); }}
        .stats-bar {{
            display: flex; justify-content: center; gap: 40px; margin-top: 25px;
            padding: 20px; background: rgba(0,212,255,0.05); border-radius: 12px;
            border: 1px solid rgba(0,212,255,0.1);
        }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 1.8rem; font-weight: 700; color: var(--accent); }}
        .stat-label {{ font-size: 0.8rem; color: var(--text-secondary); margin-top: 5px; }}
        .products-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px; margin-top: 40px;
        }}
        .product-card {{
            background: var(--bg-card); border-radius: 16px; overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1); position: relative;
        }}
        .product-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0,212,255,0.2);
        }}
        .product-image {{
            width: 100%; height: 200px; object-fit: cover;
            background: linear-gradient(135deg, #2a2a4a 0%, #1a1a2e 100%);
            display: flex; align-items: center; justify-content: center; font-size: 4rem;
        }}
        .product-info {{ padding: 20px; }}
        .product-rank {{
            position: absolute; top: 15px; left: 15px;
            background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
            color: white; font-weight: bold; padding: 8px 16px; border-radius: 20px;
            font-size: 0.85rem; box-shadow: 0 4px 15px rgba(0,212,255,0.3);
        }}
        .product-market {{
            position: absolute; top: 15px; right: 15px;
            background: rgba(0,0,0,0.6); color: white; padding: 6px 12px;
            border-radius: 15px; font-size: 0.75rem; backdrop-filter: blur(10px);
        }}
        .product-name {{
            font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; line-height: 1.4;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .metrics {{ display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }}
        .metric {{
            display: flex; align-items: center; gap: 6px; font-size: 0.9rem;
            padding: 6px 12px; border-radius: 8px; background: rgba(255,255,255,0.05);
        }}
        .metric.growth {{ color: var(--accent-green); background: rgba(74,222,128,0.1); }}
        .metric.price {{ color: var(--accent); background: rgba(0,212,255,0.1); }}
        .metric.hot {{ color: var(--accent-secondary); background: rgba(255,107,107,0.1); }}
        .growth-bar {{
            width: 100%; height: 6px; background: rgba(255,255,255,0.1);
            border-radius: 3px; margin: 15px 0; overflow: hidden;
        }}
        .growth-bar-fill {{
            height: 100%; background: linear-gradient(90deg, var(--accent-green), var(--accent));
            border-radius: 3px; transition: width 0.5s ease;
        }}
        .marketing-tips {{
            background: rgba(0,212,255,0.08); border-radius: 12px; padding: 15px;
            margin-top: 15px; border: 1px solid rgba(0,212,255,0.1);
        }}
        .marketing-tips h4 {{
            font-size: 0.9rem; color: var(--accent); margin-bottom: 12px;
            display: flex; align-items: center; gap: 8px;
        }}
        .marketing-tips ul {{ list-style: none; font-size: 0.85rem; color: var(--text-secondary); }}
        .marketing-tips li {{
            padding: 8px 0; padding-left: 22px; position: relative;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .marketing-tips li:last-child {{ border-bottom: none; }}
        .marketing-tips li::before {{ content: "→"; position: absolute; left: 0; color: var(--accent); }}
        .footer {{
            text-align: center; margin-top: 60px; padding: 30px;
            color: var(--text-secondary); font-size: 0.85rem;
            background: rgba(0,0,0,0.2); border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        .footer p {{ margin: 8px 0; }}
        .footer .warning {{ color: var(--accent-secondary); }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8rem; }}
            .stats-bar {{ flex-direction: column; gap: 20px; }}
            .products-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔥 海外爆款选品 TOP 10</h1>
            <p class="meta">
                <span>📅 生成时间：{timestamp}</span>
                <span class="separator">|</span>
                <span>🌍 市场：欧洲 · 美国</span>
                <span class="separator">|</span>
                <span>📊 数据源：Amazon Movers & Shakers + Best Sellers</span>
            </p>
            <div class="stats-bar">
                <div class="stat-item">
                    <div class="stat-value">{len(top_products)}</div>
                    <div class="stat-label">精选爆款</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">3</div>
                    <div class="stat-label">覆盖市场</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{max_growth}</div>
                    <div class="stat-label">最高增长</div>
                </div>
            </div>
        </header>
        <div class="products-grid">
            {cards_html}
        </div>
        <footer class="footer">
            <p class="warning">⚠️ 数据仅供参考，具体选品请结合实际市场情况和供应链能力综合分析</p>
            <p>📊 数据来源：Amazon Movers & Shakers + Best Sellers 榜单</p>
            <p>⏱️ 数据时效性：每日自动更新</p>
            <p>🤖 由 GitHub Actions 自动生成</p>
        </footer>
    </div>
</body>
</html>'''
    
    return html

def send_feishu_notification(products, webhook_url):
    """发送飞书通知"""
    if not webhook_url:
        print("⚠️ 未配置飞书 Webhook，跳过通知")
        return
    
    # 生成时间
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 取 TOP 3 商品
    top3 = products[:3]
    
    # 构建商品列表文本
    products_text = ""
    emojis = ["1️⃣", "2️⃣", "3️⃣"]
    for i, product in enumerate(top3):
        name = product["name"][:40] + "..." if len(product["name"]) > 40 else product["name"]
        products_text += f"{emojis[i]} {name}\n    {product['flag']} {product['market']} | 📈 {product['growth']}\n\n"
    
    # 构建飞书消息卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "red",
                "title": {
                    "tag": "plain_text",
                    "content": "🔥 海外爆款选品日报"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "plain_text",
                        "content": f"📅 {timestamp}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**📊 今日 TOP 3 精选**\n\n{products_text}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "📊 查看完整报告"
                            },
                            "type": "primary",
                            "url": REPORT_URL
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "数据来源: Amazon Movers & Shakers + Best Sellers"
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(webhook_url, json=card, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("StatusCode") == 0 or result.get("code") == 0:
                print("✅ 飞书通知发送成功")
            else:
                print(f"⚠️ 飞书通知发送失败: {result}")
        else:
            print(f"⚠️ 飞书通知发送失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ 飞书通知发送异常: {e}")

async def main():
    """主函数"""
    print("🚀 开始抓取海外爆款数据...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    all_products = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for market_key, market_info in DATA_SOURCES.items():
            print(f"📊 正在抓取 {market_info['name']} 市场...")
            
            # 抓取 Movers & Shakers
            products = await scrape_amazon_movers_shakers(
                page, 
                market_info["movers_shakers"], 
                market_info
            )
            all_products.extend(products)
            print(f"  ✅ Movers & Shakers: {len(products)} 个商品")
            
            # 抓取 Best Sellers
            products = await scrape_amazon_best_sellers(
                page,
                market_info["best_sellers"],
                market_info
            )
            all_products.extend(products)
            print(f"  ✅ Best Sellers: {len(products)} 个商品")
        
        await browser.close()
    
    print(f"\n📦 共抓取 {len(all_products)} 个商品")
    
    # 生成报告
    html = generate_html_report(all_products, timestamp)
    
    # 确保 reports 目录存在
    os.makedirs("reports", exist_ok=True)
    
    # 保存报告
    filename = f"reports/hot_products_{datetime.now().strftime('%Y%m%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {filename}")
    
    # 同时保存一份最新版本
    with open("reports/latest.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ 最新报告: reports/latest.html")
    
    # 发送飞书通知
    feishu_webhook = os.environ.get("FEISHU_WEBHOOK", "")
    if feishu_webhook:
        # 按增长率排序后的商品用于通知
        def sort_key(p):
            if "新进榜" in p["growth"]:
                return 0
            elif "%" in p["growth"]:
                try:
                    return 1 - int(p["growth"].replace("%", "").replace("+", "")) / 1000
                except:
                    return 0.5
            else:
                return 0.8
        
        sorted_products = sorted(all_products, key=sort_key)[:10]
        send_feishu_notification(sorted_products, feishu_webhook)

if __name__ == "__main__":
    asyncio.run(main())
