# -*- coding: utf-8 -*-
"""
爬取掌上高考高校详细信息（列表接口 + 详情JSON接口）
输出：data/school_data.jl，每行一个JSON对象，字段对应edu_school表
"""

import json
import time
import random
import requests
from pathlib import Path

# 配置
SCHOOL_LIST_URL = "https://static-data.gaokao.cn/www/2.0/school/list_v2.json?a=www.gaokao.cn"
DETAIL_API_URL = "https://static-data.gaokao.cn/www/2.0/school/{}/info.json?a=www.gaokao.cn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.gaokao.cn/",
    "Accept": "application/json, text/plain, */*",
}
RETRY_TIMES = 3
REQUEST_DELAY = 1.0
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "school_data.jl"


def safe_request(url, headers=None, retry=RETRY_TIMES, **kwargs):
    """安全请求，自动重试"""
    headers = headers or HEADERS
    for i in range(retry):
        try:
            resp = requests.get(url, headers=headers, timeout=10, **kwargs)
            if resp.status_code == 200:
                return resp
            else:
                print(f"请求失败 {url} 状态码 {resp.status_code}, 重试 {i+1}/{retry}")
                time.sleep(REQUEST_DELAY * (i+1))
        except Exception as e:
            print(f"请求异常 {url}: {e}, 重试 {i+1}/{retry}")
            time.sleep(REQUEST_DELAY * (i+1))
    return None


def get_school_list():
    """获取高校列表，返回 {school_id: basic_info} 字典"""
    resp = safe_request(SCHOOL_LIST_URL)
    if not resp:
        print("获取高校列表失败")
        return {}
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析列表JSON失败: {e}")
        return {}
    if data.get("code") != "0000":
        print(f"列表接口返回错误: {data.get('message')}")
        return {}
    return data.get("data", {})


def get_school_detail(school_id):
    """获取学校详情JSON数据"""
    url = DETAIL_API_URL.format(school_id)
    resp = safe_request(url)
    if not resp:
        return None
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析详情JSON失败: {e}")
        return None
    if data.get("code") != "0000":
        return None
    return data.get("data", {})


def parse_school_detail(detail_data):
    """从详情JSON中提取所需字段"""
    if not detail_data:
        return {}

    school_id = detail_data.get("school_id")
    logo = f"https://static-data.gaokao.cn/upload/logo/{school_id}.jpg"
    if detail_data.get("is_logo") == "2":
        logo = ""

    return {
        "code": detail_data.get("zs_code", ""),           # ✅ 使用招生代码作为院校代码
        "city": detail_data.get("city_name", ""),
        "type": detail_data.get("type_name", ""),
        "founded_year": int(detail_data["create_date"]) if detail_data.get("create_date") else None,
        "description": detail_data.get("content", ""),
        "website": detail_data.get("site", ""),
        "phd_count": int(detail_data["num_doctor"]) if detail_data.get("num_doctor") else None,
        "master_count": int(detail_data["num_master"]) if detail_data.get("num_master") else None,
        "logo": logo,
    }


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("正在获取高校列表...")
    school_list = get_school_list()
    if not school_list:
        print("未获取到任何学校，程序退出")
        return
    total = len(school_list)
    print(f"共获取到 {total} 所高校，开始爬取详情...")

    success_count = 0
    fail_count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for idx, (school_id, basic_info) in enumerate(school_list.items(), 1):
            print(f"进度: {idx}/{total} - 正在处理 {basic_info.get('name')} (ID: {school_id})")

            # 列表页基础字段
            name = basic_info.get("name", "")
            province = basic_info.get("p", "")
            city_list = basic_info.get("c", "")
            is_985 = basic_info.get("f985") == "1"
            is_211 = basic_info.get("f211") == "1"
            is_double_first = basic_info.get("dual_class") == "1"

            # 获取详情
            detail_data = get_school_detail(school_id)
            if not detail_data:
                print(f"  -> 获取详情失败，仅使用列表页数据")
                school_data = {
                    "name": name,
                    "code": "", 
                    "province": province,
                    "city": city_list,
                    "type": basic_info.get("nature", ""),
                    "is_985": is_985,
                    "is_211": is_211,
                    "is_double_first": is_double_first,
                    "founded_year": None,
                    "description": "",
                    "website": "",
                    "phd_count": None,
                    "master_count": None,
                    "logo": "",
                }
                f.write(json.dumps(school_data, ensure_ascii=False) + "\n")
                success_count += 1
                continue

            # 解析详情数据
            detail_fields = parse_school_detail(detail_data)

            # 合并数据：优先使用详情字段，后备使用列表页字段
            school_data = {
                "name": name,
                "code": detail_fields.get("code", ""),
                "province": province,
                "city": detail_fields.get("city") or city_list,
                "type": detail_fields.get("type") or basic_info.get("nature", ""),
                "is_985": is_985,
                "is_211": is_211,
                "is_double_first": is_double_first,
                "founded_year": detail_fields.get("founded_year"),
                "description": detail_fields.get("description", ""),
                "website": detail_fields.get("website", ""),
                "phd_count": detail_fields.get("phd_count"),
                "master_count": detail_fields.get("master_count"),
                "logo": detail_fields.get("logo", ""),
            }

            f.write(json.dumps(school_data, ensure_ascii=False) + "\n")
            success_count += 1
            print(f"  -> 成功")

            time.sleep(random.uniform(0.5, 1.5))

    print(f"\n爬取完成！成功: {success_count}, 失败: {fail_count}")
    print(f"数据已保存至: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()