#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
按学校名称拼音排序 school_data.jl 文件。
需要安装 pypinyin 库：pip install pypinyin
"""

import json
import os
import sys
from pathlib import Path

try:
    from pypinyin import pinyin, Style
except ImportError:
    print("错误：请先安装 pypinyin 库，运行：pip install pypinyin")
    sys.exit(1)


def get_pinyin_key(name):
    """
    将中文名称转换为拼音字符串（不带声调），用于排序。
    """
    # 获取每个字的拼音（不带声调）
    pinyins = pinyin(name, style=Style.NORMAL, errors='ignore')
    # 将列表转为字符串，例如 [['bei'], ['jing'], ['da'], ['xue']] -> 'beijingdaxue'
    return ''.join([item[0] for item in pinyins if item])


def main():
    # 定义文件路径（脚本位于 temp 目录，与 data 目录同级）
    script_dir = Path(__file__).parent.resolve()
    data_dir = script_dir.parent / "data"
    input_file = data_dir / "school_data.jl"
    output_file = data_dir / "school_data_sorted.jl"

    # 检查输入文件是否存在
    if not input_file.is_file():
        print(f"错误：找不到输入文件 {input_file}")
        sys.exit(1)

    # 读取所有学校数据
    schools = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                school = json.loads(line)
                schools.append(school)
            except json.JSONDecodeError as e:
                print(f"警告：第 {line_num} 行 JSON 解析失败，已跳过。错误：{e}")

    if not schools:
        print("错误：没有有效数据可排序。")
        sys.exit(1)

    # 按名称拼音排序
    schools.sort(key=lambda x: get_pinyin_key(x.get('name', '')))

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for school in schools:
            f.write(json.dumps(school, ensure_ascii=False) + '\n')

    print(f"排序完成！共处理 {len(schools)} 条记录，结果已保存至：{output_file}")


if __name__ == "__main__":
    main()