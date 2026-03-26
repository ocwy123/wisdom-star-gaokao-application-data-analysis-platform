#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('gkzy-backend')

from app import create_app

app = create_app()

with app.test_client() as client:
    print("发送 GET 请求到 /api/overview/score-segment/options")
    response = client.get('/api/overview/score-segment/options')
    print(f"响应状态码：{response.status_code}")
    print(f"响应数据：{response.get_json()}")
