#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pandas 优化版：导入学校分数线到数据库
- 将嵌套 JSON 展开为 DataFrame
- 使用 merge 关联学校 ID
- 批量插入数据库
"""

import json
import os
import sys
import pandas as pd
import pymysql
from sqlalchemy import create_engine

# ==================== 配置 ====================
PROVINCE_MAP = {
    "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
    "21": "辽宁", "22": "吉林", "23": "黑龙江",
    "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建",
    "36": "江西", "37": "山东",
    "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西",
    "46": "海南",
    "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
    "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆"
}

SUBJECT_MAP = {
    "1": "理科",
    "2": "文科",
    "3": "综合类",
    "2073": "物理类",
    "2074": "历史类"
}

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "gkzy_mysql"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, "data", "schools_all.json")


def parse_key(key):
    """解析键 '2025_11_3' -> (year, province_code, subject_code)"""
    parts = key.split('_')
    if len(parts) != 3:
        raise ValueError(f"Invalid key: {key}")
    return parts[0], parts[1], parts[2]


def main():
    # 读取 JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 平铺数据为记录列表
    records = []
    for school in data.get("学校列表", []):
        if school.get("code") != "0000":
            continue
        school_name = school.get("学校名称")
        school_data = school.get("data", {})
        for key, score in school_data.items():
            try:
                year, prov_code, subject_code = parse_key(key)
            except ValueError:
                continue
            records.append({
                "school_name": school_name,
                "year": year,
                "province_code": prov_code,
                "subject_code": subject_code,
                "min_score": score
            })

    if not records:
        print("没有有效数据")
        return

    # 转为 DataFrame
    df = pd.DataFrame(records)

    # 映射省份和科目名称
    df['province'] = df['province_code'].map(PROVINCE_MAP)
    df['major_name'] = df['subject_code'].map(SUBJECT_MAP)
    df.drop(columns=['province_code', 'subject_code'], inplace=True)

    # 连接数据库，获取学校 id 映射
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4")
    school_df = pd.read_sql("SELECT id, name FROM edu_school", engine)

    # 关联学校 id
    df = df.merge(school_df, left_on='school_name', right_on='name', how='inner')
    df.drop(columns=['school_name', 'name'], inplace=True)

    # 添加时间戳
    import datetime
    now = datetime.datetime.now()
    df['created_at'] = now
    df['updated_at'] = now

    # 批量插入数据库
    df[['school_id', 'major_name', 'province', 'year', 'min_score', 'created_at', 'updated_at']] \
        .to_sql('edu_adm_record', engine, if_exists='append', index=False, chunksize=1000)

    print(f"成功插入 {len(df)} 条记录")


if __name__ == "__main__":
    main()