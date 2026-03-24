# -*- coding: utf-8 -*-
import csv
import time
import random
import logging
import re
import os
from typing import List, Dict, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GaoKaoCnSpider:
    """掌上高考数据爬虫（使用 Selenium 处理动态页面）"""

    BASE_URL = "https://www.gaokao.cn"

    def __init__(self, output_dir: str = './data', proxy: Optional[str] = None,
                 max_retries: int = 3, delay: float = 2, headless: bool = True,
                 driver_path: Optional[str] = None):
        """
        初始化爬虫
        :param output_dir: CSV输出目录
        :param proxy: 代理地址（格式：http://ip:port）
        :param max_retries: 最大重试次数（页面加载失败时）
        :param delay: 操作间隔（秒）
        :param headless: 是否无头模式
        :param driver_path: ChromeDriver 路径（默认从 PATH 查找）
        """
        self.output_dir = output_dir
        self.proxy = proxy
        self.max_retries = max_retries
        self.delay = delay
        self.headless = headless
        self.driver_path = driver_path
        self.driver = None

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_driver(self):
        """初始化 ChromeDriver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        # 自定义 User-Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        if self.driver_path:
            self.driver = webdriver.Chrome(executable_path=self.driver_path, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

    def fetch_school_name(self, school_id: str) -> Optional[str]:
        """通过API获取学校名称（仍用requests）"""
        import requests
        url = f"https://static-data.gaokao.cn/www/2.0/school/{school_id}/info.json"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == '0000':
                    return data['data'].get('name')
        except Exception as e:
            logger.error(f"获取学校名称失败: {e}")
        return None

    def wait_for_table(self, timeout=20):
        """等待表格出现"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.tb-normal"))
            )
            return True
        except TimeoutException:
            logger.warning("表格加载超时")
            return False

    def select_dropdown_option(self, option_text: str, dropdown_selector: str, value_selector: str = None):
        """
        选择下拉框选项（通用方法）
        :param option_text: 要选择的选项文本（如 "北京"）
        :param dropdown_selector: 下拉框容器的 CSS 选择器
        :param value_selector: 可选，选项元素的选择器（默认使用包含文本的 div）
        """
        try:
            # 点击下拉框打开菜单
            dropdown = self.driver.find_element(By.CSS_SELECTOR, dropdown_selector)
            dropdown.click()
            time.sleep(0.5)
            # 查找选项
            if value_selector:
                option = self.driver.find_element(By.CSS_SELECTOR, f"{value_selector}[title='{option_text}']")
            else:
                # 查找包含文本的 div（或 li）
                option = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'score-plan_item__') and text()='{option_text}']")
            option.click()
            time.sleep(0.5)
            logger.debug(f"选择下拉选项: {option_text}")
        except Exception as e:
            logger.error(f"选择下拉选项失败: {option_text}, 错误: {e}")

    def get_major_groups(self) -> List[str]:
        """获取专业组选项"""
        groups = ['全部']
        try:
            group_box = self.driver.find_element(By.CSS_SELECTOR, "div[class*='score-plan_groupBox__']")
            items = group_box.find_elements(By.CSS_SELECTOR, "div[class*='score-plan_item__']")
            groups = [item.text.strip() for item in items if item.text.strip()]
        except Exception:
            pass
        return groups

    def parse_table(self, province: str, year: str, batch: str, major_group: str) -> List[Dict]:
        """解析当前页面表格数据"""
        records = []
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "table.tb-normal")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) < 2:
                    continue
                # 第一个 td：专业信息
                major_div = tds[0].find_element(By.CSS_SELECTOR, "div[class*='score-plan_majorInfoTd']")
                # 专业名称
                major_name = major_div.find_element(By.TAG_NAME, "h3").text.strip()
                # 子专业名称（p标签）
                try:
                    major_second_name = major_div.find_element(By.TAG_NAME, "p").text.strip()
                except:
                    major_second_name = ""
                # 选科要求
                try:
                    xkq_div = major_div.find_element(By.CSS_SELECTOR, "div[class*='score-plan_xkyq']")
                    text = xkq_div.text.strip()
                    match = re.search(r'选科要求[：:]\s*(.*?)(?:\(|$)', text)
                    subject = match.group(1).strip() if match else ""
                except:
                    subject = ""
                # 第二个 td：分数/位次
                score_text = tds[1].text.strip()
                min_score = None
                min_rank = None
                if '/' in score_text:
                    parts = score_text.split('/')
                    if len(parts) == 2:
                        min_score = self._parse_int(parts[0])
                        min_rank = self._parse_int(parts[1])
                records.append({
                    'major_name': major_name,
                    'major_second_name': major_second_name,
                    'subject': subject,
                    'province': province,
                    'year': year,
                    'batch': batch,
                    'major_group': major_group,
                    'min_score': min_score,
                    'min_rank': min_rank,
                })
        except Exception as e:
            logger.error(f"解析表格失败: {e}")
        return records

    def fetch_plan_data(self, province: str, year: str, batch: str) -> Dict[Tuple[str, str, str], int]:
        """获取招生计划数据（同样使用 Selenium）"""
        plan_map = {}
        url = f"{self.BASE_URL}/school/{self.school_id}/sturule"
        self.driver.get(url)
        # 等待页面加载（可能需要等待下拉框）
        time.sleep(3)
        # 选择省份、年份、批次（复用下拉选择方法）
        self.select_dropdown_option(province, "div[class*='filter-compents_filterSeletcBox__']:nth-child(1) div.ant-select-selection", None)
        self.select_dropdown_option(year, "div[class*='filter-compents_filterSeletcBox__']:nth-child(2) div.ant-select-selection", None)
        self.select_dropdown_option(batch, "div[class*='filter-compents_filterSeletcBox__']:nth-child(3) div.ant-select-selection", None)
        # 等待表格出现
        if not self.wait_for_table():
            return plan_map
        # 解析表格
        try:
            table = self.driver.find_element(By.CSS_SELECTOR, "table.tb-normal")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) < 2:
                    continue
                major_div = tds[0].find_element(By.CSS_SELECTOR, "div[class*='score-plan_majorInfoTd']")
                major_name = major_div.find_element(By.TAG_NAME, "h3").text.strip()
                try:
                    major_second_name = major_div.find_element(By.TAG_NAME, "p").text.strip()
                except:
                    major_second_name = ""
                try:
                    xkq_div = major_div.find_element(By.CSS_SELECTOR, "div[class*='score-plan_xkyq']")
                    text = xkq_div.text.strip()
                    match = re.search(r'选科要求[：:]\s*(.*?)(?:\(|$)', text)
                    subject = match.group(1).strip() if match else ""
                except:
                    subject = ""
                plan_text = tds[1].text.strip()
                plan_count = self._parse_int(plan_text)
                key = (major_name, major_second_name, subject)
                plan_map[key] = plan_count
        except Exception as e:
            logger.error(f"解析计划表失败: {e}")
        return plan_map

    def _parse_int(self, s: str) -> Optional[int]:
        try:
            return int(''.join(filter(str.isdigit, s)))
        except:
            return None

    def fetch_school_data(self, school_id: str, school_name: str,
                          provinces: List[str], years: List[str], batches: List[str]) -> int:
        """爬取单个学校的全部数据"""
        self.school_id = school_id
        total = 0
        output_file = os.path.join(self.output_dir, f"admission_{school_id}.csv")
        fieldnames = ['school_name', 'major_name', 'major_second_name', 'province',
                      'year', 'plan_count', 'subject', 'batch', 'major_group',
                      'min_score', 'min_rank']

        with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if os.path.getsize(output_file) == 0:
                writer.writeheader()

            for province in provinces:
                for year in years:
                    for batch in batches:
                        logger.info(f"处理 {school_name} - {province} {year} {batch}")
                        url = f"{self.BASE_URL}/school/{school_id}/provinceline"
                        self.driver.get(url)
                        # 等待下拉框加载
                        time.sleep(3)
                        # 选择省份、年份、批次
                        self.select_dropdown_option(province, "div[class*='filter-compents_filterSeletcBox__']:nth-child(1) div.ant-select-selection", None)
                        self.select_dropdown_option(year, "div[class*='filter-compents_filterSeletcBox__']:nth-child(2) div.ant-select-selection", None)
                        self.select_dropdown_option(batch, "div[class*='filter-compents_filterSeletcBox__']:nth-child(3) div.ant-select-selection", None)
                        # 等待表格出现
                        if not self.wait_for_table():
                            continue
                        # 获取专业组选项
                        groups = self.get_major_groups()
                        all_records = []
                        for group in groups:
                            if group != '全部':
                                # 点击专业组选项（需要点击对应div）
                                try:
                                    group_div = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'score-plan_item__') and text()='{group}']")
                                    group_div.click()
                                    time.sleep(1)
                                except:
                                    logger.warning(f"未找到专业组: {group}")
                                    continue
                            records = self.parse_table(province, year, batch, group)
                            all_records.extend(records)
                        if not all_records:
                            continue
                        # 获取计划数据
                        plan_map = self.fetch_plan_data(province, year, batch)
                        for rec in all_records:
                            rec['school_name'] = school_name
                            key = (rec['major_name'], rec['major_second_name'], rec['subject'])
                            rec['plan_count'] = plan_map.get(key)
                            writer.writerow(rec)
                            total += 1
                        f.flush()
                        time.sleep(self.delay)
        return total

    def run(self, school_ids: List[str], provinces: Optional[List[str]] = None,
            years: Optional[List[str]] = None, batches: Optional[List[str]] = None):
        """
        运行爬虫
        :param school_ids: 学校ID列表，如 ['330', '1']
        :param provinces: 省份列表，None则自动从页面获取（暂不实现，使用默认）
        :param years: 年份列表，None则自动获取
        :param batches: 批次列表，None则自动获取
        """
        if provinces is None:
            provinces = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江',
                         '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆',
                         '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆']
        if years is None:
            years = ['2021', '2022', '2023', '2024', '2025']
        if batches is None:
            batches = ['本科批', '专科批']

        self._init_driver()
        try:
            for school_id in school_ids:
                school_name = self.fetch_school_name(school_id)
                if not school_name:
                    logger.error(f"无法获取学校 {school_id} 的名称，跳过")
                    continue
                logger.info(f"开始爬取学校: {school_name} (ID: {school_id})")
                total = self.fetch_school_data(school_id, school_name, provinces, years, batches)
                logger.info(f"学校 {school_name} 爬取完成，共 {total} 条记录")
        finally:
            self.close()


if __name__ == '__main__':
    # 使用示例
    spider = GaoKaoCnSpider(
        output_dir='../data',
        delay=3,          # 操作间隔（秒）
        headless=True,    # 无头模式，设为 False 可看到浏览器窗口
        # driver_path='C:/path/to/chromedriver.exe'  # 如需指定路径
    )
    spider.run(school_ids=['330'])  # 只爬取西安交通大学