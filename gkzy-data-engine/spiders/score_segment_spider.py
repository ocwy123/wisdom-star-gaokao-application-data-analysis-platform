#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取高考一分一段表数据
保存为 CSV 文件：data/ana_score_segment.csv
"""

import csv
import json
import os
import random
import time
from typing import Dict, List, Optional, Tuple

import requests

# ==================== 配置 ====================
BASE_URL = "https://static-data.gaokao.cn/www/2.0/section2021"

# 省份代码 -> 省份名称映射（基于常见高考省份代码）
PROVINCE_MAP = {
    "11": "北京市", "12": "天津市", "13": "河北省", "14": "山西省", "15": "内蒙古自治区",
    "21": "辽宁省", "22": "吉林省", "23": "黑龙江省",
    "31": "上海市", "32": "江苏省", "33": "浙江省", "34": "安徽省", "35": "福建省",
    "36": "江西省", "37": "山东省",
    "41": "河南省", "42": "湖北省", "43": "湖南省", "44": "广东省", "45": "广西壮族自治区",
    "46": "海南省",
    "50": "重庆市", "51": "四川省", "52": "贵州省", "53": "云南省", "54": "西藏自治区",
    "61": "陕西省", "62": "甘肃省", "63": "青海省", "64": "宁夏回族自治区", "65": "新疆维吾尔自治区",
    # 可能还有其它特殊代码，按需添加
}

# 选科代码 -> 选科名称映射
SUBJECT_MAP = {
    "1": "理科",
    "2": "文科",
    "3": "综合",
    "2073": "物理类",
    "2074": "历史类",
}

# 批次类型（本专科）遍历值
BATCH_TYPES = ["1", "2", "3"]  # 1:本科 2:专科 3:不分本/专科

# 年份范围（2016~2025）
YEARS = list(range(2016, 2026))

# 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.gaokao.cn/",
}

# 请求延迟范围（秒）
DELAY_MIN = 1.0
DELAY_MAX = 3.0

# 超时设置
TIMEOUT = 10

# 输出文件路径
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join("..", OUTPUT_DIR, "ana_score_segment.csv")

# ==================== 工具函数 ====================
def ensure_dir(path: str) -> None:
    """确保目录存在"""
    if not os.path.exists(path):
        os.makedirs(path)


def safe_int(s: str) -> int:
    """安全转换为整数，失败返回0"""
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def extract_score(score_str: str) -> int:
    """
    从分数段字符串中提取整数分数
    例："681-750" -> 681
        "678" -> 678
    """
    if not score_str:
        return 0
    # 取第一个数字部分
    part = score_str.split("-")[0].strip()
    return safe_int(part)


def fetch_data(year: int, prov_code: str, subject_code: str, batch_type: str) -> Optional[Dict]:
    """
    请求指定组合的数据，返回 JSON 解析后的字典，如果失败返回 None
    """
    url = f"{BASE_URL}/{year}/{prov_code}/{subject_code}/{batch_type}/lists.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code != 200:
            return None
        data = response.json()
        # 检查业务状态码
        if data.get("code") != "0000":
            return None
        # 检查是否有数据
        if not data.get("data", {}).get("search"):
            return None
        return data
    except (requests.RequestException, json.JSONDecodeError):
        return None


def process_search(search_dict: Dict, year: int, prov_name: str, subject_name: str) -> List[Tuple]:
    """
    处理 data.search 字典，返回待写入的行列表
    每行格式：(province, year, subject, batch, score, rank, same_score_count)
    """
    rows = []
    for key, item in search_dict.items():
        # 提取字段
        score_str = item.get("score", "")
        score = extract_score(score_str)
        rank = safe_int(item.get("total", "0"))
        same_cnt = safe_int(item.get("num", "0"))
        batch = item.get("batch_name", "").strip()
        if not batch:
            batch = "未知批次"

        # 只保存有效数据
        if score > 0 and rank > 0:
            rows.append((prov_name, year, subject_name, batch, score, rank, same_cnt))
    return rows


# ==================== 主爬取逻辑 ====================
def main():
    ensure_dir(OUTPUT_DIR)

    # 打开 CSV 文件写入
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["province", "year", "subject", "batch", "score", "rank", "same_score_count"])

        total_requests = 0
        total_rows = 0

        for year in YEARS:
            for prov_code, prov_name in PROVINCE_MAP.items():
                for subject_code, subject_name in SUBJECT_MAP.items():
                    for batch_type in BATCH_TYPES:
                        total_requests += 1
                        # 请求数据
                        data = fetch_data(year, prov_code, subject_code, batch_type)
                        if not data:
                            # 无数据则跳过
                            continue

                        # 提取 search 部分
                        search_dict = data.get("data", {}).get("search")
                        if not search_dict:
                            continue

                        # 处理并写入
                        rows = process_search(search_dict, year, prov_name, subject_name)
                        for row in rows:
                            writer.writerow(row)
                            total_rows += 1

                        # 输出进度提示
                        print(f"[{total_requests}] {year}-{prov_name}({prov_code})-{subject_name}({subject_code})-{batch_type} -> {len(rows)} rows")

                        # 随机延迟，避免反爬
                        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        print(f"\n爬取完成！总计请求 {total_requests} 次，有效数据 {total_rows} 条。")
        print(f"数据已保存至：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()