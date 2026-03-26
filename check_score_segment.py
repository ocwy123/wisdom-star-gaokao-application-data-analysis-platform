#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('gkzy-backend')

from app import create_app
from app.models.score_segment import ScoreSegment
from app.extensions import db

app = create_app()

with app.app_context():
    # 查询记录总数
    count = ScoreSegment.query.count()
    print(f'ana_score_segment 表中的记录数：{count}')
    
    if count > 0:
        # 查询示例数据
        samples = ScoreSegment.query.limit(5).all()
        print('\n示例数据:')
        for s in samples:
            print(f'  - {s.province}, {s.year}, {s.subject}, {s.score}')
        
        # 查询所有不同的省份、年份、选科
        provinces = db.session.query(ScoreSegment.province).distinct().all()
        years = db.session.query(ScoreSegment.year).distinct().all()
        subjects = db.session.query(ScoreSegment.subject).distinct().all()
        
        print(f'\n省份列表：{[p.province for p in provinces]}')
        print(f'年份列表：{[y.year for y in years]}')
        print(f'选科列表：{[s.subject for s in subjects]}')
    else:
        print('\n表中没有数据！')
