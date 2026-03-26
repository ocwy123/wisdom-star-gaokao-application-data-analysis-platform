#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 优化版：爬取高考一分一段表数据
- 使用 DataFrame 收集所有数据
- 一次性写入 CSV，提高效率
"""

import csv
import json
import os
import random
import time
import pandas as pd
import requests
from typing import Dict, List, Optional, Tuple

# ==================== 配置 ====================
BASE_URL = "https://static-data.gaokao.cn/www/2.0/section2021"

PROVINCE_MAP = {
    "11": "北京市", "12": "天津市", "13": "河北省", "14": "山西省", "15": "内蒙古自治区",
    "21": "辽宁省", "22": "吉林省", "23": "黑龙江省",
    "31": "上海市", "32": "江苏省", "33": "浙江省", "34": "安徽省", "35": "福建省",
    "36": "江西省", "37": "山东省",
    "41": "河南省", "42": "湖北省", "43": "湖南省", "44": "广东省", "45": "广西壮族自治区",
    "46": "海南省",
    "50": "重庆市", "51": "四川省", "52": "贵州省", "53": "云南省", "54": "西藏自治区",
    "61": "陕西省", "62": "甘肃省", "63": "青海省", "64": "宁夏回族自治区", "65": "新疆维吾尔自治区",
}

SUBJECT_MAP = {
    "1": "理科",
    "2": "文科",
    "3": "综合",
    "2073": "物理类",
    "2074": "历史类",
}

BATCH_TYPES = ["1", "2", "3"]
YEARS = list(range(2016, 2026))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.gaokao.cn/",
}

DELAY_MIN = 1.0
DELAY_MAX = 3.0
TIMEOUT = 10

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join("..", OUTPUT_DIR, "ana_score_segment.csv")


def ensure_dir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def fetch_data(year: int, prov_code: str, subject_code: str, batch_type: str) -> Optional[Dict]:
    url = f"{BASE_URL}/{year}/{prov_code}/{subject_code}/{batch_type}/lists.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get("code") != "0000" or not data.get("data", {}).get("search"):
            return None
        return data
    except Exception:
        return None


def extract_score(score_str: str) -> int:
    """从 "681-750" 或 "678" 中提取整数分数"""
    if not score_str:
        return 0
    part = score_str.split("-")[0].strip()
    try:
        return int(part)
    except ValueError:
        return 0


def main():
    ensure_dir(OUTPUT_DIR)
    all_records = []   # 存储所有行数据（字典列表）

    total_requests = 0
    for year in YEARS:
        for prov_code, prov_name in PROVINCE_MAP.items():
            for subject_code, subject_name in SUBJECT_MAP.items():
                for batch_type in BATCH_TYPES:
                    total_requests += 1
                    data = fetch_data(year, prov_code, subject_code, batch_type)
                    if not data:
                        continue
                    search_dict = data.get("data", {}).get("search", {})
                    for key, item in search_dict.items():
                        score = extract_score(item.get("score", ""))
                        rank = item.get("total", "0")
                        same_cnt = item.get("num", "0")
                        batch = item.get("batch_name", "").strip()
                        if not batch:
                            batch = "未知批次"
                        if score > 0 and int(rank) > 0:
                            all_records.append({
                                "province": prov_name,
                                "year": year,
                                "subject": subject_name,
                                "batch": batch,
                                "score": score,
                                "rank": int(rank),
                                "same_score_count": int(same_cnt)
                            })
                    print(f"[{total_requests}] {year}-{prov_name}-{subject_name}-{batch_type} -> {len(search_dict)} rows")
                    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    # 转换为 DataFrame 并写入 CSV
    df = pd.DataFrame(all_records)
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\n爬取完成！共获取 {len(df)} 条记录。")
    print(f"数据已保存至：{OUTPUT_FILE}")


if __name__ == "__main__":
    main()