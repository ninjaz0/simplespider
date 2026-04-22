import time
import random
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================================
# 办公室复印纸采购优化大作业 - 第一阶段：真实淘宝爬虫
# 学号：20250001 (请自行修改)
# 姓名：张三 (请自行修改)
# 脚本说明：基于 Selenium 的淘宝真实数据抓取，需要手动扫码登录
# ==============================================================================

def init_driver():
    """初始化Selenium WebDriver，配置反检测参数"""
    chrome_options = Options()
    
    # 绕过基本的 WebDriver 检测
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 解决部分系统下可能出现的问题
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 自动下载并设置 Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 执行 CDP 脚本，修改 window.navigator.webdriver，进一步防止被识别为爬虫
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def scrape_taobao_data(keyword="A4复印纸", max_items=100):
    """主爬取逻辑"""
    driver = init_driver()
    scraped_data = []
    
    try:
        # 1. 打开淘宝首页准备登录
        print(">>> 正在打开淘宝首页...")
        driver.get("https://www.taobao.com/")
        
        # 2. 引导用户手动扫码登录
        print(">>> 【重要提示】由于淘宝安全机制，搜索结果可能被登录弹窗拦截。")
        print(">>> 请在弹出的浏览器中，手动扫码登录。")
        
        search_url = f"https://s.taobao.com/search?q={keyword}"
        driver.get(search_url)
        
        # 使用最稳妥的手动确认方式
        input(">>> [等待操作] 请在浏览器中完成扫码登录，并在看到【A4复印纸的商品列表】后，在此处按【回车键】继续...")
            
        print(">>> 登录成功！开始抓取商品信息...")
        
        # 3. 开始解析商品页面
        # 淘宝页面采用动态瀑布流加载，需要向下滚动以加载全部图片和元素
        for i in range(1, 6):
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {i/5});")
            time.sleep(random.uniform(1.0, 1.5))
            
        # 等待商品卡片元素出现
        # 淘宝目前的商品卡片通常带有 'Card--' 或类似 class，这里使用更通用的 XPath 匹配尝试
        # 注意：淘宝前端经常改版，以下定位器基于当前主流版本。如果失败可能需要根据实际情况 F12 调整
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'Card--') or contains(@class, 'item-')]"))
            )
        except:
            print(">>> 页面加载缓慢或选择器已更改，尝试直接提取...")

        # 提取商品信息
        items = driver.find_elements(By.XPATH, "//div[contains(@class, 'Card--') or contains(@class, 'item-')]")
        
        print(f"当前页面共发现 {len(items)} 个商品卡片，正在解析...")
        
        count = 0
        import re
        for item in items:
            if count >= max_items:
                break
            try:
                # 淘宝页面元素class被严重混淆，我们直接提取卡片的全部文本，然后基于文本特征智能解析
                card_text = item.text
                if not card_text:
                    continue
                    
                text_lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                if len(text_lines) < 3:
                    continue
                    
                price_text = ""
                title = ""
                shop = ""
                
                for i, line in enumerate(text_lines):
                    # 识别价格
                    if '¥' in line or '￥' in line:
                        if line.strip() in ['¥', '￥']:
                            if i + 1 < len(text_lines):
                                price_text = text_lines[i+1]
                        else:
                            price_text = line.replace('¥', '').replace('￥', '').strip()
                            
                    # 识别标题 (包含关键词且较长)
                    if len(line) >= 8 and ('A4' in line.upper() or '纸' in line or '复印' in line or '打印' in line):
                        title = line
                        
                    # 识别店铺
                    if line.endswith('店') or '专营' in line or '办公' in line or line.endswith('部'):
                        shop = line
                        
                # 极端后备方案：如果文本没分好行
                if not price_text:
                    prices = re.findall(r'[¥￥]\s*(\d+\.?\d*)', card_text)
                    if prices:
                        price_text = prices[0]
                        
                if not price_text:
                    continue  # 没有价格的卡片通常是广告位或占位符，直接跳过
                    
                if not title:
                    title = text_lines[0] if len(text_lines) > 0 else "未知名称"
                    
                if not shop:
                    shop = text_lines[-1] if len(text_lines) > 0 else "未知店铺"

                # 二次清洗提取出的价格（只保留数字）
                nums = re.findall(r'\d+\.?\d*', price_text)
                if nums:
                    price_val = nums[0]
                else:
                    continue
                
                # 获取简单的品牌/型号推断
                brand = "未知品牌"
                for b in ["得力", "晨光", "齐心", "天章", "亚太", "百旺", "纸老虎", "玛丽"]:
                    if b in title:
                        brand = b
                        break

                scraped_data.append({
                    "商品ID": f"A4_TB_{random.randint(10000, 99999)}",
                    "日期": datetime.now().strftime("%Y-%m-%d"),
                    "真实平台价格": price_val,
                    "品牌": brand,
                    "型号": "70g" if "70g" in title.lower() or "70克" in title else "80g",
                    "商品来源网站": "淘宝网",
                    "商品来源店铺": shop,
                    "数据获取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "商品原标题": title
                })
                count += 1
                
            except Exception as e:
                # 忽略个别解析失败的卡片（如广告位）
                pass
                
        print(f">>> 成功抓取了 {len(scraped_data)} 条有效商品数据！")
        
    except Exception as e:
        print(f"抓取过程中发生错误: {e}")
        
    finally:
        print(">>> 关闭浏览器...")
        driver.quit()
        
    return scraped_data

def save_data(data, filename="raw_scraped_data.csv"):
    if not data:
        print("[警告] 无数据可保存")
        return
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"[成功] 淘宝真实数据已保存至 {filename}")

if __name__ == "__main__":
    print("=" * 50)
    print("启动 淘宝Selenium自动化爬虫程序")
    print("=" * 50)
    
    # 抓取数据
    data = scrape_taobao_data(keyword="A4复印纸", max_items=50)
    
    # 保存原始爬取数据
    save_data(data, "raw_scraped_data.csv")
    
    # 同时为了满足作业提交要求，直接复制一份命名为 [学号]_result.csv 方便您直接提交
    # 但建议您还是运行预处理脚本来进行正规的清洗流程
    if data:
        df = pd.DataFrame(data)
        df.to_csv("20250001_result.csv", index=False, encoding='utf-8-sig')
        print("[成功] 结果已同步保存为PK赛需要的 20250001_result.csv")
