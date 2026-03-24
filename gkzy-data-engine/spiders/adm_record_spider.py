import requests
import json
import time
import re
import os

def fix_unicode_string(s):
    """修复Unicode转义字符串"""
    if isinstance(s, str):
        try:
            return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
        except:
            return s
    return s

def decode_all(data):
    """递归解码所有字符串"""
    if isinstance(data, dict):
        return {k: decode_all(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decode_all(item) for item in data]
    elif isinstance(data, str):
        return fix_unicode_string(data)
    else:
        return data

def get_school_name_mapping():
    """获取学校ID到名称的映射"""
    url = "https://static-data.gaokao.cn/www/2.0/school/school_code.json?a=www.gaokao.cn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.gaokao.cn/',
        'Accept': 'application/json, text/plain, */*'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            decoded_data = decode_all(data)
            
            # 构建 school_id -> name 的映射
            mapping = {}
            for code, info in decoded_data.get("data", {}).items():
                school_id = info.get("school_id")
                name = info.get("name")
                if school_id and name:
                    mapping[school_id] = name
            return mapping
        else:
            print(f"获取学校映射失败: {response.status_code}")
            return {}
    except Exception as e:
        print(f"获取学校映射异常: {e}")
        return {}

def fetch_special_benchmark(special_id, school_mapping):
    """通过API获取专业分数线"""
    # 专业分数线接口（推测）
    url = f"https://static-data.gaokao.cn/www/2.0/special/{special_id}/benchmarkScore.json?a=www.gaokao.cn"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.gaokao.cn/',
        'Accept': 'application/json, text/plain, */*'
    }
    
    try:
        print(f"正在爬取专业 ID: {special_id}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            raw_text = response.text
            data = json.loads(raw_text)
            decoded_data = decode_all(data)
            
            # 如果是分数线数据，可以添加学校名称（如果需要）
            if decoded_data.get("code") == "0000" and "data" in decoded_data:
                # 分数线数据的键名如 "2025_11_3" 等，不直接包含学校ID
                # 所以这里添加专业ID即可
                decoded_data["专业ID"] = special_id
            
            return decoded_data
            
        elif response.status_code == 404:
            print(f"  专业不存在")
            return {
                "专业ID": special_id,
                "code": "404",
                "message": "专业不存在"
            }
        else:
            print(f"  返回错误: {response.status_code}")
            return {
                "专业ID": special_id,
                "错误": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        print(f"  请求失败: {e}")
        return {"专业ID": special_id, "错误": str(e)}

def fetch_school_benchmark(school_id, school_mapping):
    """通过API获取学校分数线（原功能保留）"""
    url = f"https://static-data.gaokao.cn/www/2.0/school/{school_id}/benchmarkScore.json?a=www.gaokao.cn"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.gaokao.cn/',
        'Accept': 'application/json, text/plain, */*'
    }
    
    try:
        print(f"正在爬取学校 ID: {school_id}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            raw_text = response.text
            data = json.loads(raw_text)
            decoded_data = decode_all(data)
            
            # 添加学校名称
            school_name = school_mapping.get(str(school_id), "未知学校")
            decoded_data["学校ID"] = school_id
            decoded_data["学校名称"] = school_name
            
            return decoded_data
            
        elif response.status_code == 404:
            print(f"  学校不存在")
            return {
                "学校ID": school_id,
                "学校名称": school_mapping.get(str(school_id), "未知"),
                "code": "404",
                "message": "学校不存在"
            }
        else:
            print(f"  返回错误: {response.status_code}")
            return {
                "学校ID": school_id,
                "学校名称": school_mapping.get(str(school_id), "未知"),
                "错误": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        print(f"  请求失败: {e}")
        return {"学校ID": school_id, "错误": str(e)}

def crawl_all_schools(school_ids, filename="../data/adm_record_all.json"):
    """爬取所有学校的分数线"""
    print("="*60)
    print(f"开始爬取 {len(school_ids)} 所学校")
    print("="*60)
    
    # 先获取学校名称映射
    print("正在获取学校名称映射...")
    school_mapping = get_school_name_mapping()
    print(f"已获取 {len(school_mapping)} 所学校信息\n")
    
    all_data = []
    success_count = 0
    fail_count = 0
    
    for idx, school_id in enumerate(school_ids, 1):
        print(f"\n[{idx}/{len(school_ids)}] ", end="")
        
        detail = fetch_school_benchmark(school_id, school_mapping)
        all_data.append(detail)
        
        if "错误" in detail or detail.get("code") == "404":
            fail_count += 1
        else:
            success_count += 1
        
        # 实时保存
        final_data = {
            "爬取时间": time.strftime('%Y-%m-%d %H:%M:%S'),
            "学校总数": len(school_ids),
            "已爬取数量": len(all_data),
            "成功数量": success_count,
            "失败数量": fail_count,
            "学校列表": all_data
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        if idx % 10 == 0:
            print(f"  💾 已保存进度")
        
        time.sleep(0.3)
    
    print("\n" + "="*60)
    print(f"爬取完成！")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")
    print(f"  数据已保存到: {filename}")
    
    return final_data

def get_all_school_ids_from_code():
    """从 school_code.json 获取所有学校ID"""
    url = "https://static-data.gaokao.cn/www/2.0/school/school_code.json?a=www.gaokao.cn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            decoded_data = decode_all(data)
            
            school_ids = []
            for code, info in decoded_data.get("data", {}).items():
                school_id = info.get("school_id")
                if school_id:
                    school_ids.append(int(school_id))
            
            return sorted(set(school_ids))
        else:
            print(f"获取学校列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取学校列表异常: {e}")
        return []

def test_single_school(school_id=140):
    """测试单个学校"""
    print(f"测试学校 ID: {school_id}")
    
    school_mapping = get_school_name_mapping()
    data = fetch_school_benchmark(school_id, school_mapping)
    
    if "错误" not in data and data.get("code") != "404":
        print(f"  ✓ 学校名称: {data.get('学校名称', 'N/A')}")
        if 'data' in data:
            d = data['data']
            print(f"  ✓ 包含 {len(d)} 条分数线数据")
            # 显示部分分数线示例
            sample = list(d.items())[:5]
            for key, value in sample:
                print(f"    {key}: {value}")
    else:
        print(f"  ✗ 错误: {data.get('错误', data.get('message', '未知错误'))}")
    
    return data

# def test_single_special(special_id=1):
#     """测试单个专业（尝试专业接口）"""
#     print(f"测试专业 ID: {special_id}")
    
#     school_mapping = get_school_name_mapping()
#     data = fetch_special_benchmark(special_id, school_mapping)
    
#     if "错误" not in data and data.get("code") != "404":
#         print(f"  ✓ 成功获取数据")
#         if 'data' in data:
#             d = data['data']
#             print(f"  ✓ 包含 {len(d)} 条分数线数据")
#             sample = list(d.items())[:5]
#             for key, value in sample:
#                 print(f"    {key}: {value}")
#     else:
#         print(f"  ✗ 错误: {data.get('错误', data.get('message', '未知错误'))}")
    
#     return data

if __name__ == '__main__':
    print("="*60)
    print("高考数据爬虫 - 学校分数线接口")
    print("="*60)
    
    # 先测试一个已知学校
    print("\n测试清华大学 (ID: 140)...")
    test_single_school(140)
    
    print("\n" + "="*60)
    print("获取所有学校ID...")
    school_ids = get_all_school_ids_from_code()
    print(f"共找到 {len(school_ids)} 所学校")
    print(f"学校ID范围: {min(school_ids)} - {max(school_ids)}")
    print(f"前10个ID: {school_ids[:10]}")
    
    print("\n" + "="*60)
    print("是否开始爬取所有学校分数线？")
    print("输入 y 开始爬取，输入 n 取消")
    user_input = input().strip().lower()
    
    if user_input == 'y':
        crawl_all_schools(school_ids)
    else:
        print("已取消")