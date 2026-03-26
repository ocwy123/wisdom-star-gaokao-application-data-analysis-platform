#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('gkzy-backend')

from app import create_app
from app.services.overview import OverviewService
import traceback

app = create_app()

with app.app_context():
    try:
        print("调用 get_score_segment_options...")
        result = OverviewService.get_score_segment_options()
        print(f"结果：{result}")
    except Exception as e:
        print(f"错误：{e}")
        traceback.print_exc()
