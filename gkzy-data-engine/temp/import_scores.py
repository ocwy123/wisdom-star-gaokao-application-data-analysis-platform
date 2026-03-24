#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime
import pymysql
from pymysql import OperationalError, ProgrammingError

# 省份代码映射
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

# 类别代码映射
SUBJECT_MAP = {
    "1": "理科",
    "2": "文科",
    "3": "综合类",
    "2073": "物理类",
    "2074": "历史类"
}

DB_CONFIG = {
    "host": "192.168.54.241",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "gkzy_mysql"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE_DIR, "data", "schools_all.json")

def get_school_id(cursor, school_name):
    """根据学校名称从 edu_school 表查询学校ID"""
    query = "SELECT id FROM edu_school WHERE name = %s"
    cursor.execute(query, (school_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def parse_key(key):
    """解析键字符串，返回 (year, province_code, subject_code)"""
    parts = key.split('_')
    if len(parts) != 3:
        raise ValueError(f"Invalid key format: {key}")
    year = parts[0]
    province_code = parts[1]
    subject_code = parts[2]
    return year, province_code, subject_code

def main():
    # 读取JSON文件
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"文件未找到: {JSON_FILE}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        sys.exit(1)

    # 连接数据库
    try:
        conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        print("数据库连接成功")
    except (OperationalError, ProgrammingError) as e:
        print(f"数据库连接失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}")
        sys.exit(1)

    # 统计信息
    total_schools = len(data.get("学校列表", []))
    success_count = 0
    fail_count = 0
    inserted_records = 0

    # 遍历学校列表
    for school in data.get("学校列表", []):
        if school.get("code") != "0000":
            print(f"跳过学校: {school.get('学校名称')}，状态码: {school.get('code')}，消息: {school.get('message')}")
            fail_count += 1
            continue

        school_name = school.get("学校名称")
        school_data = school.get("data")
        if not school_data:
            print(f"学校 {school_name} 无数据，跳过")
            fail_count += 1
            continue

        school_id = get_school_id(cursor, school_name)
        if school_id is None:
            print(f"警告: 在 edu_school 表中未找到学校 '{school_name}'，跳过该学校所有数据")
            fail_count += 1
            continue

        for key, score in school_data.items():
            try:
                year, province_code, subject_code = parse_key(key)
            except ValueError as e:
                print(f"警告: 键 '{key}' 解析失败，跳过该记录。错误: {e}")
                continue

            province_name = PROVINCE_MAP.get(province_code)
            if province_name is None:
                print(f"警告: 未知省份代码 '{province_code}'，跳过记录: {key}")
                continue

            major_name = SUBJECT_MAP.get(subject_code)
            if major_name is None:
                print(f"警告: 未知类别代码 '{subject_code}'，跳过记录: {key}")
                continue

            insert_sql = """
                INSERT INTO edu_adm_record
                (school_id, major_name, province, year, min_score, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            now = datetime.now()
            values = (school_id, major_name, province_name, year, score, now, now)
            try:
                cursor.execute(insert_sql, values)
                inserted_records += 1
            except Exception as e:
                print(f"插入失败: 学校 {school_name}, 键 {key}，错误: {e}")

        success_count += 1
        print(f"已处理学校: {school_name}")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n=== 处理完成 ===")
    print(f"总学校数: {total_schools}")
    print(f"成功处理学校数: {success_count}")
    print(f"跳过/失败学校数: {fail_count}")
    print(f"成功插入记录数: {inserted_records}")

if __name__ == "__main__":
    main()