#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称：insert_major_employment.py
功能：从 ../data/specialties_all.json 读取专业就业数据，解析后插入到 MySQL 数据库的 ana_major_employment 表中。
依赖：pymysql

更新说明：
1. 若专业在 edu_major 表中查不到，且专业名以“技术”结尾，则依次尝试：
   - 去掉“技术”二字
   - 去掉“技术”二字后加“学”
   进行匹配。
2. 插入前检查 ana_major_employment 中是否已存在相同 major_id 和 year 的记录，若存在则跳过。
3. 岗位分布使用 detail_pos 字段作为键名。
"""

import json
import re
import html
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

# 文件路径（相对于脚本所在目录）
JSON_FILE = Path(__file__).parent.parent / 'data' / 'specialties_all.json'

def clean_html(raw_html):
    """移除HTML标签并还原转义字符"""
    if not raw_html:
        return None
    text = html.unescape(raw_html)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def build_distribution(items, key_field):
    """
    从 jobdetail 的某个子列表构建 JSON 对象。
    items: 列表
    key_field: 用于取 key 的字段名，如 'name', 'detail_pos', 'area'
    """
    if not items or not isinstance(items, list):
        return None
    dist = {}
    for item in items:
        key = item.get(key_field)
        if not key:
            continue
        try:
            rate = float(item['rate'])
        except (ValueError, TypeError):
            rate = 0.0
        if rate > 0:
            dist[key] = rate
    return json.dumps(dist, ensure_ascii=False) if dist else None

def get_major_id(cursor, major_name):
    """根据专业名称从 edu_major 表中查询 id，支持回退查找"""
    sql = "SELECT id FROM edu_major WHERE name = %s"
    # 直接查找
    cursor.execute(sql, (major_name,))
    result = cursor.fetchone()
    if result:
        return result['id']

    # 若专业名以“技术”结尾，尝试去掉“技术”和加“学”两种方式
    if major_name.endswith('技术'):
        base_name = major_name[:-2]  # 去掉“技术”
        # 尝试 base_name
        cursor.execute(sql, (base_name,))
        result = cursor.fetchone()
        if result:
            print(f"专业映射：{major_name} -> {base_name} (id={result['id']})")
            return result['id']
        # 尝试 base_name + '学'
        candidate = base_name + '学'
        cursor.execute(sql, (candidate,))
        result = cursor.fetchone()
        if result:
            print(f"专业映射：{major_name} -> {candidate} (id={result['id']})")
            return result['id']

    return None

def record_exists(cursor, major_id, year):
    """检查 ana_major_employment 中是否已存在指定专业和年份的记录"""
    sql = "SELECT COUNT(*) AS cnt FROM ana_major_employment WHERE major_id = %s AND year = %s"
    cursor.execute(sql, (major_id, year))
    result = cursor.fetchone()
    return result['cnt'] > 0

def main():
    # 读取JSON文件
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：文件 {JSON_FILE} 不存在")
        return
    except json.JSONDecodeError as e:
        print(f"JSON解析失败：{e}")
        return

    specialties = data.get('专业列表', [])
    if not specialties:
        print("未找到专业列表数据")
        return

    # 连接数据库
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=DictCursor)
        cursor = conn.cursor()
        print("数据库连接成功")
    except pymysql.Error as e:
        print(f"数据库连接失败：{e}")
        return

    inserted = 0
    skipped = 0
    year = 2025

    for item in specialties:
        if item.get('code') != '0000' or not item.get('data'):
            skipped += 1
            continue

        major_data = item['data']
        major_name = major_data.get('name')
        if not major_name:
            skipped += 1
            continue

        # 获取major_id（支持回退匹配）
        major_id = get_major_id(cursor, major_name)
        if not major_id:
            print(f"警告：专业 '{major_name}' 在 edu_major 表中不存在（含回退匹配），跳过")
            skipped += 1
            continue

        # 检查是否已存在
        if record_exists(cursor, major_id, year):
            print(f"跳过：专业 '{major_name}' (id={major_id}) 已存在 {year} 年数据")
            skipped += 1
            continue

        # 提取字段
        prof_salary = major_data.get('professionalsalary')
        avg_salary = prof_salary.get('salaryavg') if prof_salary else None

        prospect_raw = major_data.get('job')
        prospect = clean_html(prospect_raw) if prospect_raw else None

        jobdetail = major_data.get('jobdetail', {})

        # 行业分布（键字段：name）
        industry_items = jobdetail.get('1')
        industry_dist = build_distribution(industry_items, 'name')

        # 岗位分布（键字段：detail_pos）
        post_items = jobdetail.get('3')
        post_dist = build_distribution(post_items, 'detail_pos')

        # 地区分布（键字段：area）
        region_items = jobdetail.get('2')
        region_dist = build_distribution(region_items, 'area')

        # 插入数据
        insert_sql = """
            INSERT INTO ana_major_employment 
            (major_id, year, avg_salary, industry_distribution, post_distribution, region_distribution, prospect, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        try:
            cursor.execute(insert_sql, (
                major_id, year, avg_salary, industry_dist, post_dist, region_dist, prospect
            ))
            inserted += 1
            if inserted % 50 == 0:
                print(f"已插入 {inserted} 条记录...")
        except pymysql.Error as e:
            print(f"插入失败：专业 {major_name} (ID:{major_id}) - {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n执行完成：共处理 {len(specialties)} 条专业记录，成功插入 {inserted} 条，跳过 {skipped} 条。")

if __name__ == '__main__':
    main()