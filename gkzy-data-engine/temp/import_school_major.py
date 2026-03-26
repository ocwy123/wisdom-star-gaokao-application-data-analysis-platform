#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入学校-专业关联数据
- 一次性读取学校、专业映射表
- 使用 map 进行批量匹配
- 批量插入数据库
"""

import os
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from datetime import datetime

# ==================== 配置 ====================
DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'school_major_data.csv')


def main():
    # 读取 CSV
    df = pd.read_csv(CSV_FILE)

    # 去除空格
    df['school_name'] = df['school_name'].str.strip()
    df['major_name'] = df['major_name'].str.strip()
    df['description'] = df['description'].fillna('').str.strip()

    # 连接数据库获取映射
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4")
    school_df = pd.read_sql("SELECT id, name FROM edu_school", engine)
    major_df = pd.read_sql("SELECT id, name FROM edu_major", engine)

    # 构建映射字典
    school_map = school_df.set_index('name')['id'].to_dict()
    major_map = major_df.set_index('name')['id'].to_dict()

    # 匹配 ID
    df['school_id'] = df['school_name'].map(school_map)
    df['major_id'] = df['major_name'].map(major_map)

    # 删除匹配失败的行
    before = len(df)
    df_clean = df.dropna(subset=['school_id', 'major_id'])
    after = len(df_clean)
    print(f"原始行数: {before}, 有效行数: {after}, 丢弃行数: {before - after}")

    # 转换 ID 为整数
    df_clean['school_id'] = df_clean['school_id'].astype(int)
    df_clean['major_id'] = df_clean['major_id'].astype(int)

    # 添加时间戳
    now = datetime.now()
    df_clean['created_at'] = now
    df_clean['updated_at'] = now

    # 批量插入
    df_clean[['school_id', 'major_id', 'description', 'created_at', 'updated_at']] \
        .to_sql('edu_school_major', engine, if_exists='append', index=False, chunksize=1000)

    print(f"成功插入 {len(df_clean)} 条记录")


if __name__ == "__main__":
    main()