#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入一分一段表数据
- 使用 pandas 读取 CSV
- 按业务主键去重
- 批量插入数据库
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, 'data', 'ana_score_segment_test.csv')


def main():
    # 读取 CSV
    df = pd.read_csv(INPUT_CSV, encoding='utf-8')
    print(f"原始数据行数: {len(df)}")

    # 去重：先完全重复行，再按唯一键去重
    df = df.drop_duplicates()
    key_cols = ['province', 'year', 'subject', 'score']
    df_clean = df.drop_duplicates(subset=key_cols, keep='first')
    print(f"清洗后行数: {len(df_clean)}")

    # 处理 batch 字段中的空值
    df_clean['batch'] = df_clean['batch'].fillna('未知批次')

    # 添加时间戳
    now = datetime.now()
    df_clean['created_at'] = now
    df_clean['updated_at'] = now

    # 连接数据库并插入
    engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?charset=utf8mb4")
    df_clean.to_sql('ana_score_segment', engine, if_exists='append', index=False, chunksize=1000)
    print(f"成功插入 {len(df_clean)} 条记录")


if __name__ == "__main__":
    main()