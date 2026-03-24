# -*- coding: utf-8 -*-
"""
爬取掌上高考专业信息（列表API + 详情API）
输出：data/major_data.jl，每行一个JSON对象，字段对应edu_major表
"""

import json
import re
import time
import random
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ==================== 配置 ====================
# 学科门类 level2 值映射
LEVEL2_MAP = {
    "3": "哲学",
    "4": "经济学",
    "5": "法学",
    "6": "教育学",
    "7": "文学",
    "8": "历史学",
    "9": "理学",
    "10": "工学",
    "11": "农学",
    "12": "医学",
    "13": "管理学",
    "14": "艺术学",
}

# 列表 API
LIST_API_URL = "https://api.zjzw.cn/web/api/?keyword=&level1=1&level2={}&level3=&page={}&size=20&sort=&uri=apidata/api/gkv3/special/lists&signsafe=f565e1b90464fcf7555f6d6c86b1c239"
# 详情 API
DETAIL_API_URL = "https://static-data.gaokao.cn/www/2.0/special/{}/pc_special_detail.json?a=www.gaokao.cn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.gaokao.cn/",
    "Accept": "application/json, text/plain, */*",
}
RETRY_TIMES = 3
LIST_DELAY = 0.5          # 列表页请求间隔
DETAIL_DELAY = 0.8        # 详情页请求间隔
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "major_data.jl"
# ============================================


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
                time.sleep(LIST_DELAY * (i+1))
        except Exception as e:
            print(f"请求异常 {url}: {e}, 重试 {i+1}/{retry}")
            time.sleep(LIST_DELAY * (i+1))
    return None


def get_major_list_by_level2(level2, page=1, size=20):
    """获取指定学科门类的专业列表（分页）"""
    url = LIST_API_URL.format(level2, page)
    resp = safe_request(url)
    if not resp:
        return [], 0
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析列表JSON失败: {e}")
        return [], 0
    if data.get("code") != "0000":
        print(f"列表API返回错误: {data.get('message')}")
        return [], 0
    items = data.get("data", {}).get("item", [])
    total = data.get("data", {}).get("numFound", 0)
    return items, total


def get_major_detail(special_id):
    """获取专业详情"""
    url = DETAIL_API_URL.format(special_id)
    resp = safe_request(url)
    if not resp:
        return {}
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析详情JSON失败: {e}")
        return {}
    if data.get("code") != "0000":
        return {}
    return data.get("data", {})


def chinese_to_int(chinese_num):
    """将汉字数字转换为整数，支持一到十及复合数字如十一"""
    map = {
        "一": 1, "二": 2, "三": 3, "四": 4,
        "五": 5, "六": 6, "七": 7, "八": 8,
        "九": 9, "十": 10
    }
    num_str = chinese_num.replace("年", "").strip()
    if len(num_str) == 2 and num_str[0] == "十":
        return 10 + map.get(num_str[1], 0)
    return map.get(num_str)


def extract_description(detail):
    """
    从详情数据中提取专业介绍（纯文本，无HTML标签）
    优先使用 is_what 字段，否则从 content 中提取第一个段落并清理标签
    """
    # 优先使用 is_what
    desc = detail.get("is_what", "")
    if desc:
        # 移除末尾可能带有的“关键词：”部分
        desc = re.sub(r"关键词：.*$", "", desc).strip()
        return desc

    # 否则从 content 中提取第一个段落
    content = detail.get("content", "")
    if not content:
        return ""

    soup = BeautifulSoup(content, "html.parser")
    # 找到第一个 <p> 标签
    first_p = soup.find("p")
    if first_p:
        return first_p.get_text(strip=True)
    return ""


def parse_major(item, detail):
    """
    解析专业数据，合并列表和详情
    """
    # 学制：limit_year 可能为"四年"、"五年"等，提取数字
    limit_year = item.get("limit_year", "")
    duration = None
    if limit_year:
        # 提取汉字数字
        match = re.search(r"([零一二三四五六七八九十]+)", limit_year)
        if match:
            duration = chinese_to_int(match.group(1))

    # 从详情中提取选科建议和专业介绍
    subjects = detail.get("sel_adv", "")
    description = extract_description(detail)

    return {
        "name": item.get("name", ""),
        "code": item.get("spcode", ""),
        "duration": duration,
        "degree": item.get("degree", ""),
        "subjects": subjects,
        "description": description,
    }


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 按学科门类爬取
    level2_list = sorted(LEVEL2_MAP.keys(), key=lambda x: int(x))
    print(f"准备爬取 {len(level2_list)} 个学科门类: {[LEVEL2_MAP[l] for l in level2_list]}\n")

    all_majors = []
    total_items = 0

    for level2 in level2_list:
        discipline = LEVEL2_MAP[level2]
        print(f"正在爬取 {discipline} 类...")
        page = 1
        discipline_count = 0
        while True:
            items, total = get_major_list_by_level2(level2, page)
            if not items:
                break

            for item in items:
                special_id = item.get("special_id")
                if not special_id:
                    continue
                detail = get_major_detail(special_id)
                major_data = parse_major(item, detail)
                all_majors.append(major_data)
                discipline_count += 1
                if discipline_count % 10 == 0:
                    print(f"    已处理 {discipline_count} 条")
                time.sleep(random.uniform(0.5, DETAIL_DELAY))

            print(f"  第 {page} 页: 获取 {len(items)} 条，本学科累计 {discipline_count} 条")
            if discipline_count >= total:
                break
            page += 1
            time.sleep(random.uniform(0.3, 0.8))

        total_items += discipline_count
        print(f"  {discipline} 类完成，共 {discipline_count} 条\n")
        time.sleep(1)

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for major in all_majors:
            f.write(json.dumps(major, ensure_ascii=False) + "\n")

    print(f"爬取完成！共获取 {len(all_majors)} 个专业")
    print(f"数据已保存至: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()