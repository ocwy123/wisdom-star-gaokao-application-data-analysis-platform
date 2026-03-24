#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import pymysql
import datetime
import os

# ==================== 配置信息 ====================
DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

INPUT_CSV = os.path.join('..', 'data', 'ana_score_segment.csv')
OUTPUT_CSV = os.path.join('..', 'data', 'ana_score_segment_cleaned.csv')

# ==================== 数据清洗 ====================
def clean_data():
    print(f"正在读取文件: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV, encoding='utf-8')
    print(f"原始数据行数: {len(df)}")

    # 第一步：去除所有列完全重复的行（可选，但保留能减少后续计算）
    df = df.drop_duplicates()
    print(f"去除完全重复后行数: {len(df)}")

    # 第二步：按照唯一键 (province, year, subject, score) 去重，保留每组第一条记录
    key_cols = ['province', 'year', 'subject', 'score']
    df_cleaned = df.drop_duplicates(subset=key_cols, keep='first')
    print(f"按唯一键去重后行数: {len(df_cleaned)}")

    # 保存清洗后的文件
    df_cleaned.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')
    print(f"清洗后的文件已保存到: {OUTPUT_CSV}")

    return df_cleaned

# ==================== 数据入库 ====================
def insert_to_db(df):
    print("正在连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 使用反引号包裹字段名，避免与保留字冲突（如 rank）
    insert_sql = """
        INSERT INTO ana_score_segment 
        (`province`, `year`, `subject`, `batch`, `score`, `rank`, `same_score_count`, `created_at`, `updated_at`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    now = datetime.datetime.now()

    data_to_insert = []
    for _, row in df.iterrows():
        batch_val = row['batch'] if pd.notna(row['batch']) else None
        data_to_insert.append((
            row['province'],
            int(row['year']),
            row['subject'],
            batch_val,
            int(row['score']),
            int(row['rank']),
            int(row['same_score_count']),
            now,
            now
        ))

    print(f"准备插入 {len(data_to_insert)} 条记录...")
    try:
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        print("数据插入成功！")
    except Exception as e:
        conn.rollback()
        print(f"插入失败: {e}")
    finally:
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")

# ==================== 主函数 ====================
def main():
    df_cleaned = clean_data()
    insert_to_db(df_cleaned)

if __name__ == '__main__':
    main()