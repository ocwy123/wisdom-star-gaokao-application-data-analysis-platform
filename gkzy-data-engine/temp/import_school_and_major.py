# -*- coding: utf-8 -*-
"""
导入高校和专业数据到 MySQL 数据库
文件位置：temp/import_data.py
数据文件：data/school_data.jl, data/major_data.jl
"""

import json
import os
import pymysql
from datetime import datetime

# ==================== 数据库配置 ====================
DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

# 文件路径（脚本位于 temp 目录，data 目录与其同级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHOOL_FILE = os.path.join(BASE_DIR, 'data', 'school_data.jl')
MAJOR_FILE = os.path.join(BASE_DIR, 'data', 'major_data.jl')
# =================================================


def connect_db():
    """创建数据库连接"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise


def import_schools(cursor):
    """导入高校数据"""
    if not os.path.exists(SCHOOL_FILE):
        print(f"文件不存在: {SCHOOL_FILE}")
        return

    schools = []
    with open(SCHOOL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                schools.append(json.loads(line))

    print(f"读取到 {len(schools)} 所学校数据")
    inserted = 0
    skipped = 0

    for school in schools:
        # 检查学校是否已存在（根据名称）
        cursor.execute("SELECT id FROM edu_school WHERE name = %s", (school['name'],))
        if cursor.fetchone():
            skipped += 1
            continue

        now = datetime.now()
        # 处理布尔值转为 int (1/0)
        is_985 = 1 if school.get('is_985') else 0
        is_211 = 1 if school.get('is_211') else 0
        is_double_first = 1 if school.get('is_double_first') else 0

        cursor.execute("""
            INSERT INTO edu_school (
                name, code, province, city, type,
                is_985, is_211, is_double_first,
                founded_year, description, website,
                phd_count, master_count, logo,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            school.get('name', ''),
            school.get('code', ''),
            school.get('province', ''),
            school.get('city', ''),
            school.get('type', ''),
            is_985,
            is_211,
            is_double_first,
            school.get('founded_year'),
            school.get('description', ''),
            school.get('website', ''),
            school.get('phd_count'),
            school.get('master_count'),
            school.get('logo', ''),
            now,
            now
        ))
        inserted += 1

    print(f"学校导入完成: 插入 {inserted} 条, 跳过 {skipped} 条")


def import_majors(cursor):
    """导入专业数据"""
    if not os.path.exists(MAJOR_FILE):
        print(f"文件不存在: {MAJOR_FILE}")
        return

    majors = []
    with open(MAJOR_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                majors.append(json.loads(line))

    print(f"读取到 {len(majors)} 个专业数据")
    inserted = 0
    skipped = 0

    for major in majors:
        # 检查专业是否已存在（根据名称）
        cursor.execute("SELECT id FROM edu_major WHERE name = %s", (major['name'],))
        if cursor.fetchone():
            skipped += 1
            continue

        now = datetime.now()
        cursor.execute("""
            INSERT INTO edu_major (
                name, code, duration, degree, subjects, description,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            major.get('name', ''),
            major.get('code', ''),
            major.get('duration'),
            major.get('degree', ''),
            major.get('subjects', ''),
            major.get('description', ''),
            now,
            now
        ))
        inserted += 1

    print(f"专业导入完成: 插入 {inserted} 条, 跳过 {skipped} 条")


def main():
    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            import_schools(cursor)
            import_majors(cursor)
        conn.commit()
        print("所有数据导入完成")
    except Exception as e:
        print(f"导入出错: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    main()