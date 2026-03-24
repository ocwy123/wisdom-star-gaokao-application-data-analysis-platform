# spiders/school_major_crawler.py
import csv
import json
import os
import time
import random

import requests

# 配置
SCHOOL_CODE_URL = "https://static-data.gaokao.cn/www/2.0/school/school_code.json?a=www.gaokao.cn"
XUEKE_RANK_URL_TEMPLATE = "https://static-data.gaokao.cn/www/2.0/school/{school_id}/xueke_rank.json?a=www.gaokao.cn"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join("..", OUTPUT_DIR, "school_major_data.csv")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_DELAY = (0.5, 1)  # 随机延时范围（秒）

def make_request(url):
    """发送请求并返回 JSON 数据，失败时返回 None"""
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"请求失败: {url}, 错误: {e}")
        return None

def fetch_school_list():
    """获取学校 ID 和名称的映射"""
    data = make_request(SCHOOL_CODE_URL)
    if not data or data.get("code") != "0000":
        print("获取学校列表失败")
        return {}

    school_map = {}
    for key, info in data.get("data", {}).items():
        school_id = info.get("school_id")
        name = info.get("name")
        if school_id and name:
            school_map[school_id] = name
    return school_map

def fetch_school_majors(school_id):
    """获取某个学校的学科排名数据，返回 (专业名, 等级) 列表"""
    url = XUEKE_RANK_URL_TEMPLATE.format(school_id=school_id)
    data = make_request(url)
    if not data or data.get("code") != "0000":
        return []

    items = data.get("data", {}).get("item", [])
    majors = []
    for round_items in items:
        for item in round_items:
            major_name = item.get("xueke_name")
            score = item.get("xueke_rank_score")
            if major_name and score:
                majors.append((major_name, score))
    return majors

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 获取所有学校
    school_map = fetch_school_list()
    print(f"共获取到 {len(school_map)} 所学校")

    # 打开 CSV 文件，准备逐行写入
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["school_name", "major_name", "description"])
        f.flush()  # 立即写入表头

        for idx, (school_id, school_name) in enumerate(school_map.items(), 1):
            print(f"正在处理 ({idx}/{len(school_map)}): {school_name} ({school_id})")
            majors = fetch_school_majors(school_id)
            if not majors:
                print(f"  {school_name} 无学科评估数据")
                continue

            for major_name, score in majors:
                description = f"学科评估：{score}"
                writer.writerow([school_name, major_name, description])
            f.flush()  # 每所学校数据写入后立即刷新到磁盘

            # 随机延时，避免请求过快
            delay = random.uniform(*REQUEST_DELAY)
            time.sleep(delay)

    print(f"完成！数据已保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()