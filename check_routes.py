#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('gkzy-backend')

from app import create_app

app = create_app()

print("\n注册的路由:")
for rule in app.url_map.iter_rules():
    if 'score-segment' in str(rule):
        print(f"  {rule.endpoint}: {rule}")
