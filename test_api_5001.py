#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests

url = 'http://localhost:5000/api/overview/score-segment/options'
print(f"请求 URL: {url}")
response = requests.get(url)
print(f"响应状态码：{response.status_code}")
print(f"响应内容：{response.text[:500]}")
