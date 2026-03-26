#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试导出功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.analysis import get_metric_name, get_dimension_name

def test_metric_translation():
    """测试指标名称翻译"""
    print("=== 测试指标名称翻译 ===")
    test_metrics = [
        'avg_score', 'heat_score', 'admission_rate',
        'min_score', 'max_score', 'search_count',
        'avg_salary', 'school_count', '985_count'
    ]
    
    for metric in test_metrics:
        chinese_name = get_metric_name(metric)
        print(f"{metric} -> {chinese_name}")
    
    print()

def test_dimension_translation():
    """测试维度名称翻译"""
    print("=== 测试维度名称翻译 ===")
    test_dimensions = ['school', 'major', 'province', 'year', 'score', 'heat']
    
    for dim in test_dimensions:
        chinese_name = get_dimension_name(dim)
        print(f"{dim} -> {chinese_name}")
    
    print()

def test_data_flattening():
    """测试数据展平"""
    print("=== 测试数据展平 ===")
    
    # 模拟多维对比分析结果
    mock_result = [
        {
            'dimension': 'school',
            'dimension_value': '清华大学',
            'school_id': 1,
            'data': {
                'avg_score': 650.5,
                'heat_score': 95.8,
                'admission_rate': 0.05,
                'school_count': 1
            }
        },
        {
            'dimension': 'school',
            'dimension_value': '北京大学',
            'school_id': 2,
            'data': {
                'avg_score': 648.2,
                'heat_score': 94.5,
                'admission_rate': 0.06,
                'school_count': 1
            }
        }
    ]
    
    metrics = ['avg_score', 'heat_score', 'admission_rate', 'school_count']
    
    # 展平数据
    flat_data = []
    for item in mock_result:
        row = {
            '对比项': item.get('dimension_value', ''),
            '维度类型': item.get('dimension', '')
        }
        
        item_data = item.get('data', {})
        for metric in metrics:
            metric_value = item_data.get(metric, '')
            row[get_metric_name(metric)] = metric_value
        
        flat_data.append(row)
    
    # 打印结果
    print("展平后的数据:")
    for row in flat_data:
        print(row)
    
    print()
    
    # 验证字段
    print("验证字段:")
    expected_columns = ['对比项', '维度类型'] + [get_metric_name(m) for m in metrics]
    print(f"预期列：{expected_columns}")
    if flat_data:
        actual_columns = list(flat_data[0].keys())
        print(f"实际列：{actual_columns}")
        print(f"字段匹配：{expected_columns == actual_columns}")
    
    print()

if __name__ == '__main__':
    print("测试导出功能...\n")
    
    test_metric_translation()
    test_dimension_translation()
    test_data_flattening()
    
    print("所有测试完成！")
