#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import socket

# 测试连接
print("测试 1: 检查端口是否可连接")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('localhost', 5000))
if result == 0:
    print("  ✓ 端口 5000 可连接")
else:
    print(f"  ✗ 端口 5000 不可连接，错误码：{result}")
sock.close()

print("\n测试 2: 发送 HTTP 请求")
url = 'http://localhost:5000/api/overview/score-segment/options'
print(f"  请求 URL: {url}")

try:
    response = requests.get(url, timeout=5)
    print(f"  响应状态码：{response.status_code}")
    print(f"  响应内容：{response.text[:200]}")
    print(f"  响应头：{dict(response.headers)}")
except Exception as e:
    print(f"  错误：{e}")
