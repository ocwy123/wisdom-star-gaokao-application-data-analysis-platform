# test_gaokao.py
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def test_spider():
    # 指定 ChromeDriver 路径（请修改为您的实际路径）
    driver_path = r"D:\Code_and_Project\hwadee2026\broad-explore\gkzy-data-engine\spiders\chromedriver.exe"
    # 如果放在系统PATH中，可以简化：service = Service()
    service = Service(executable_path=driver_path)
    
    # 配置 Chrome 选项
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 调试时注释掉，可以看到浏览器界面
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

    # 启动浏览器
    print("正在启动浏览器...")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        # 目标 URL
        url = "https://www.gaokao.cn/school/330/provinceline"
        print(f"正在访问: {url}")
        driver.get(url)
        time.sleep(3)  # 等待初始渲染

        # 定义下拉框选择函数
        def select_dropdown(option_text, container_selector):
            """选择下拉框中的选项"""
            try:
                # 点击下拉框打开菜单
                dropdown = driver.find_element(By.CSS_SELECTOR, container_selector)
                dropdown.click()
                time.sleep(0.5)
                # 查找选项
                option = driver.find_element(By.XPATH, f"//div[contains(@class, 'score-plan_item__') and text()='{option_text}']")
                option.click()
                time.sleep(0.5)
                print(f"✓ 已选择: {option_text}")
                return True
            except Exception as e:
                print(f"✗ 选择 '{option_text}' 失败: {e}")
                return False

        # 选择省份（北京）
        print("\n选择省份...")
        select_dropdown("北京", "div[class*='filter-compents_filterSeletcBox__']:nth-child(1) div.ant-select-selection")
        
        # 选择年份（2023）
        print("选择年份...")
        select_dropdown("2023", "div[class*='filter-compents_filterSeletcBox__']:nth-child(2) div.ant-select-selection")
        
        # 选择批次（本科批）
        print("选择批次...")
        select_dropdown("本科批", "div[class*='filter-compents_filterSeletcBox__']:nth-child(3) div.ant-select-selection")

        # 等待表格出现
        print("\n等待表格加载...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.tb-normal"))
            )
            print("✓ 表格已加载")
        except TimeoutException:
            print("✗ 表格加载超时")
            # 打印当前页面源代码前500字符用于调试
            print("页面源代码片段:", driver.page_source[:500])
            return

        # 解析表格数据
        print("\n开始解析表格...")
        table = driver.find_element(By.CSS_SELECTOR, "table.tb-normal")
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        print(f"共找到 {len(rows)} 行数据\n")
        
        print("前5行数据预览：")
        print("-" * 80)
        for i, row in enumerate(rows[:5]):
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            
            # 专业信息
            major_div = tds[0].find_element(By.CSS_SELECTOR, "div[class*='score-plan_majorInfoTd']")
            major_name = major_div.find_element(By.TAG_NAME, "h3").text.strip()
            
            # 子专业
            try:
                major_second = major_div.find_element(By.TAG_NAME, "p").text.strip()
            except NoSuchElementException:
                major_second = ""
            
            # 选科要求
            try:
                xkq = major_div.find_element(By.CSS_SELECTOR, "div[class*='score-plan_xkyq']").text.strip()
                match = re.search(r'选科要求[：:]\s*(.*?)(?:\(|$)', xkq)
                subject = match.group(1) if match else ""
            except:
                subject = ""
            
            # 分数/位次
            score_text = tds[1].text.strip()
            
            print(f"{i+1}. 专业: {major_name} {major_second}")
            print(f"   选科: {subject}")
            print(f"   分数/位次: {score_text}")
            print()

        # 获取专业组选项
        print("\n专业组选项：")
        try:
            group_box = driver.find_element(By.CSS_SELECTOR, "div[class*='score-plan_groupBox__']")
            groups = group_box.find_elements(By.CSS_SELECTOR, "div[class*='score-plan_item__']")
            group_texts = [g.text.strip() for g in groups if g.text.strip()]
            print(f"✓ 找到 {len(group_texts)} 个专业组: {', '.join(group_texts)}")
        except Exception as e:
            print(f"✗ 未找到专业组: {e}")

        print("\n测试完成！")

    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭浏览器
        print("\n关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    test_spider()