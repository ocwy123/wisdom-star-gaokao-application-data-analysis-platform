from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import traceback

app = Flask(__name__)
CORS(app)

# 配置
DATA_DIR = 'data'
SCHOOLS_FILE = os.path.join(DATA_DIR, '全国高校数据.xlsx')

# 分数段划分
SCORE_SEGMENTS = [
    {'name': '顶尖高校(680分+)', 'min': 680, 'max': 750},
    {'name': '优秀高校(650-679分)', 'min': 650, 'max': 679},
    {'name': '一本高校(600-649分)', 'min': 600, 'max': 649},
    {'name': '一本中段(550-599分)', 'min': 550, 'max': 599},
    {'name': '一本边缘(500-549分)', 'min': 500, 'max': 549},
    {'name': '二本高校(450-499分)', 'min': 450, 'max': 499},
    {'name': '二本中段(400-449分)', 'min': 400, 'max': 449},
    {'name': '二本边缘(350-399分)', 'min': 350, 'max': 399},
    {'name': '专科高校(300-349分)', 'min': 300, 'max': 349},
    {'name': '专科以下(<300分)', 'min': 0, 'max': 299}
]

def load_schools_data():
    """加载高校数据"""
    if not os.path.exists(SCHOOLS_FILE):
        print(f"❌ 文件不存在: {SCHOOLS_FILE}")
        return None
    
    try:
        df = pd.read_excel(SCHOOLS_FILE)
        print(f"✅ 成功加载高校数据: {len(df)} 条记录")
        
        # 确保必要的列存在
        if '是否985' in df.columns:
            df['是否985'] = pd.to_numeric(df['是否985'], errors='coerce').fillna(0).astype(int)
        if '是否211' in df.columns:
            df['是否211'] = pd.to_numeric(df['是否211'], errors='coerce').fillna(0).astype(int)
        if '是否双一流' in df.columns:
            df['是否双一流'] = pd.to_numeric(df['是否双一流'], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        print(f"❌ 加载高校数据出错: {e}")
        traceback.print_exc()
        return None

def load_scores_data():
    """加载分数线数据"""
    if not os.path.exists(DATA_DIR):
        return None
    
    score_files = [f for f in os.listdir(DATA_DIR) 
                   if f.startswith('专业录取分数') and f.endswith('.csv')]
    if not score_files:
        print("⚠️ 未找到分数线文件")
        return None
    
    latest_file = sorted(score_files)[-1]
    file_path = os.path.join(DATA_DIR, latest_file)
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"✅ 成功加载分数线数据: {len(df)} 条记录")
        
        # 转换数值类型
        for col in ['最低分', '最高分', '平均分', '录取人数']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"❌ 加载分数线数据出错: {e}")
        return None

@app.route('/')
def index():
    """返回HTML页面"""
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高考志愿数据分析系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
            color: white;
            padding: 25px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
        }
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .nav-tab {
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }
        .nav-tab:hover {
            background: #e6f7ff;
            color: #1890ff;
        }
        .nav-tab.active {
            background: #1890ff;
            color: white;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .card-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
            color: #1890ff;
        }
        .filter-bar {
            background: #fafafa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .filter-item {
            flex: 1;
            min-width: 200px;
        }
        .filter-item label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #666;
        }
        .filter-item input, .filter-item select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            font-size: 14px;
        }
        .filter-item button {
            width: 100%;
            padding: 8px 12px;
            background: #1890ff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .filter-item button:hover {
            background: #40a9ff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #fafafa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #f0f0f0;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-size: 12px;
            margin-right: 5px;
        }
        .badge-985 { background: #f5222d; }
        .badge-211 { background: #fa8c16; }
        .badge-dual { background: #52c41a; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .error {
            color: #f5222d;
            padding: 20px;
            text-align: center;
            background: #fff1f0;
            border-radius: 4px;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
        }
        .pagination button {
            padding: 6px 12px;
            border: 1px solid #d9d9d9;
            background: white;
            border-radius: 4px;
            cursor: pointer;
        }
        .pagination button:hover {
            border-color: #1890ff;
            color: #1890ff;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 高考志愿数据分析系统</h1>
            <p>数据来源：掌上高考 | 实时更新 | 分分数段分析</p>
        </div>

        <div class="nav-tabs">
            <div class="nav-tab active" onclick="switchTab('dashboard')">📊 仪表盘</div>
            <div class="nav-tab" onclick="switchTab('schools')">🏫 高校查询</div>
            <div class="nav-tab" onclick="switchTab('majors')">📚 专业分析</div>
        </div>

        <div id="content">
            <!-- 内容将通过JavaScript动态加载 -->
            <div class="loading">正在加载数据...</div>
        </div>
    </div>

    <script>
        let currentTab = 'dashboard';
        let currentPage = 1;

        // 切换标签页
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.nav-tab').forEach(el => {
                el.classList.remove('active');
            });
            event.target.classList.add('active');
            loadContent();
        }

        // 加载内容
        async function loadContent() {
            const content = document.getElementById('content');
            
            if (currentTab === 'dashboard') {
                await loadDashboard();
            } else if (currentTab === 'schools') {
                await loadSchools();
            } else if (currentTab === 'majors') {
                await loadMajors();
            }
        }

        // 加载仪表盘
        async function loadDashboard() {
            const content = document.getElementById('content');
            
            try {
                // 获取高校数据
                const schoolsRes = await fetch('/api/schools?page=1&page_size=100');
                const schoolsData = await schoolsRes.json();
                
                if (schoolsData.error) {
                    content.innerHTML = `<div class="error">❌ ${schoolsData.error}</div>`;
                    return;
                }

                // 计算统计
                const totalSchools = schoolsData.total;
                const schools = schoolsData.data || [];
                
                let html = `
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${totalSchools}</div>
                            <div class="stat-label">高校总数</div>
                        </div>
                        <div class="stat-item" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                            <div class="stat-value">${schools.filter(s => s['是否985'] == 1).length}</div>
                            <div class="stat-label">985高校</div>
                        </div>
                        <div class="stat-item" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                            <div class="stat-value">${schools.filter(s => s['是否211'] == 1).length}</div>
                            <div class="stat-label">211高校</div>
                        </div>
                        <div class="stat-item" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                            <div class="stat-value">${new Set(schools.map(s => s['省份'])).size}</div>
                            <div class="stat-label">覆盖省份</div>
                        </div>
                    </div>
                `;

                // 高校列表
                html += `
                    <div class="card">
                        <div class="card-title">🏫 高校列表（前20所）</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>学校名称</th>
                                    <th>省份</th>
                                    <th>办学层次</th>
                                    <th>院校类型</th>
                                    <th>标签</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                schools.slice(0, 20).forEach(school => {
                    let badges = '';
                    if (school['是否985'] == 1) badges += '<span class="badge badge-985">985</span>';
                    if (school['是否211'] == 1) badges += '<span class="badge badge-211">211</span>';
                    if (school['是否双一流'] == 1) badges += '<span class="badge badge-dual">双一流</span>';
                    
                    html += `
                        <tr>
                            <td><strong>${school['学校名称'] || '-'}</strong></td>
                            <td>${school['省份'] || '-'}</td>
                            <td>${school['办学层次'] || '-'}</td>
                            <td>${school['院校类型'] || '-'}</td>
                            <td>${badges || '-'}</td>
                        </tr>
                    `;
                });

                html += `
                            </tbody>
                        </table>
                    </div>
                `;

                content.innerHTML = html;

            } catch (error) {
                content.innerHTML = `<div class="error">❌ 加载失败: ${error.message}</div>`;
            }
        }

        // 加载高校查询页面
        async function loadSchools() {
            const content = document.getElementById('content');
            
            let html = `
                <div class="card">
                    <div class="card-title">🔍 高校查询</div>
                    <div class="filter-bar">
                        <div class="filter-item">
                            <label>搜索学校</label>
                            <input type="text" id="searchInput" placeholder="输入学校名称">
                        </div>
                        <div class="filter-item">
                            <label>省份</label>
                            <select id="provinceSelect">
                                <option value="">全部省份</option>
                            </select>
                        </div>
                        <div class="filter-item">
                            <label>学校层次</label>
                            <select id="levelSelect">
                                <option value="">全部</option>
                                <option value="985">985高校</option>
                                <option value="211">211高校</option>
                                <option value="双一流">双一流高校</option>
                            </select>
                        </div>
                        <div class="filter-item">
                            <label>&nbsp;</label>
                            <button onclick="searchSchools()">查询</button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">📋 查询结果</div>
                    <div id="schoolResults">
                        <div class="loading">点击查询按钮加载数据</div>
                    </div>
                    <div class="pagination" id="schoolPagination"></div>
                </div>
            `;

            content.innerHTML = html;

            // 加载省份选项
            try {
                const res = await fetch('/api/filters');
                const filters = await res.json();
                
                const select = document.getElementById('provinceSelect');
                if (filters.school_provinces) {
                    filters.school_provinces.filter(p => p !== 'all').forEach(prov => {
                        select.innerHTML += `<option value="${prov}">${prov}</option>`;
                    });
                }
            } catch (error) {
                console.error('加载省份失败:', error);
            }
        }

        // 搜索学校
        async function searchSchools(page = 1) {
            const search = document.getElementById('searchInput').value;
            const province = document.getElementById('provinceSelect').value;
            const level = document.getElementById('levelSelect').value;
            
            const resultsDiv = document.getElementById('schoolResults');
            resultsDiv.innerHTML = '<div class="loading">加载中...</div>';
            
            try {
                const res = await fetch(`/api/schools?page=${page}&page_size=20&search=${search}&province=${province}&level=${level}`);
                const data = await res.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }

                if (data.data.length === 0) {
                    resultsDiv.innerHTML = '<div class="error">暂无数据</div>';
                    return;
                }

                let html = `
                    <table>
                        <thead>
                            <tr>
                                <th>学校名称</th>
                                <th>省份</th>
                                <th>办学层次</th>
                                <th>院校类型</th>
                                <th>标签</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.data.forEach(school => {
                    let badges = '';
                    if (school['是否985'] == 1) badges += '<span class="badge badge-985">985</span>';
                    if (school['是否211'] == 1) badges += '<span class="badge badge-211">211</span>';
                    if (school['是否双一流'] == 1) badges += '<span class="badge badge-dual">双一流</span>';
                    
                    html += `
                        <tr>
                            <td><strong>${school['学校名称'] || '-'}</strong></td>
                            <td>${school['省份'] || '-'}</td>
                            <td>${school['办学层次'] || '-'}</td>
                            <td>${school['院校类型'] || '-'}</td>
                            <td>${badges || '-'}</td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                html += `<p style="margin-top:10px;color:#666;">共 ${data.total} 条记录，第 ${data.page} 页</p>`;
                
                resultsDiv.innerHTML = html;

                // 更新分页
                const totalPages = Math.ceil(data.total / 20);
                if (totalPages > 1) {
                    let paginationHtml = '';
                    for (let i = 1; i <= Math.min(totalPages, 5); i++) {
                        paginationHtml += `<button onclick="searchSchools(${i})" ${i === page ? 'style="background:#1890ff;color:white;"' : ''}>${i}</button>`;
                    }
                    document.getElementById('schoolPagination').innerHTML = paginationHtml;
                }

            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
            }
        }

        // 加载专业分析页面
        async function loadMajors() {
            const content = document.getElementById('content');
            
            let html = `
                <div class="card">
                    <div class="card-title">📚 专业分析</div>
                    <div class="filter-bar">
                        <div class="filter-item">
                            <label>分数段</label>
                            <select id="scoreSegmentSelect">
                                <option value="all">全部</option>
    `;

            // 添加分数段选项
            const segments = [
                '顶尖高校(680分+)', '优秀高校(650-679分)', '一本高校(600-649分)',
                '一本中段(550-599分)', '一本边缘(500-549分)', '二本高校(450-499分)',
                '二本中段(400-449分)', '二本边缘(350-399分)', '专科高校(300-349分)',
                '专科以下(<300分)'
            ];
            
            segments.forEach(s => {
                html += `<option value="${s}">${s}</option>`;
            });

            html += `
                            </select>
                        </div>
                        <div class="filter-item">
                            <label>&nbsp;</label>
                            <button onclick="loadMajorStats()">分析</button>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">📊 分析结果</div>
                    <div id="majorResults">
                        <div class="loading">请选择分数段并点击分析</div>
                    </div>
                </div>
            `;

            content.innerHTML = html;
        }

        // 加载专业统计数据
        async function loadMajorStats() {
            const segment = document.getElementById('scoreSegmentSelect').value;
            const resultsDiv = document.getElementById('majorResults');
            
            resultsDiv.innerHTML = '<div class="loading">加载中...</div>';
            
            try {
                const res = await fetch(`/api/major-analysis?score_segment=${segment}`);
                const data = await res.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }

                if (!data.top_majors || data.top_majors.length === 0) {
                    resultsDiv.innerHTML = '<div class="error">暂无数据</div>';
                    return;
                }

                let html = `
                    <h4 style="margin-bottom:15px;">热门专业TOP20</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>专业名称</th>
                                <th>总录取人数</th>
                                <th>开设学校数</th>
                                <th>平均分</th>
                                <th>热度得分</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                data.top_majors.forEach((major, index) => {
                    html += `
                        <tr>
                            <td>${index + 1}</td>
                            <td><strong>${major['专业名称'] || '-'}</strong></td>
                            <td>${major['总录取人数']?.toFixed(0) || 0}</td>
                            <td>${major['开设学校数'] || 0}</td>
                            <td>${major['平均分']?.toFixed(1) || '-'}</td>
                            <td>${major['热度得分']?.toFixed(3) || 0}</td>
                        </tr>
                    `;
                });

                html += '</tbody></table>';
                resultsDiv.innerHTML = html;

            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
            }
        }

        // 页面加载时初始化
        window.onload = function() {
            loadContent();
        };
    </script>
</body>
</html>
    '''

@app.route('/api/schools', methods=['GET'])
def get_schools():
    """获取高校列表"""
    try:
        schools_df = load_schools_data()
        if schools_df is None:
            return jsonify({'error': '无法加载高校数据'}), 404
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '')
        province = request.args.get('province', '')
        level = request.args.get('level', '')
        
        filtered_df = schools_df.copy()
        
        # 应用过滤
        if search:
            filtered_df = filtered_df[filtered_df['学校名称'].str.contains(search, na=False, case=False)]
        if province and province != 'all' and province != '':
            filtered_df = filtered_df[filtered_df['省份'] == province]
        if level:
            if level == '985':
                filtered_df = filtered_df[filtered_df['是否985'] == 1]
            elif level == '211':
                filtered_df = filtered_df[filtered_df['是否211'] == 1]
            elif level == '双一流':
                filtered_df = filtered_df[filtered_df['是否双一流'] == 1]
        
        # 分页
        total = len(filtered_df)
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        
        # 转换为字典列表
        result = []
        for idx in range(start, end):
            if idx >= total:
                break
            row = filtered_df.iloc[idx]
            result.append({
                '学校名称': str(row.get('学校名称', '')),
                '省份': str(row.get('省份', '')),
                '办学层次': str(row.get('办学层次', '')),
                '院校类型': str(row.get('院校类型', '')),
                '是否985': int(row.get('是否985', 0)),
                '是否211': int(row.get('是否211', 0)),
                '是否双一流': int(row.get('是否双一流', 0))
            })
        
        return jsonify({
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': result
        })
        
    except Exception as e:
        print(f"❌ API错误: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """获取筛选条件"""
    try:
        schools_df = load_schools_data()
        
        filters = {
            'school_provinces': ['all']
        }
        
        if schools_df is not None and '省份' in schools_df.columns:
            provinces = schools_df['省份'].dropna().unique()
            filters['school_provinces'] = ['all'] + sorted([str(p) for p in provinces if p and str(p) != 'nan'])
        
        return jsonify(filters)
        
    except Exception as e:
        print(f"❌ 获取筛选条件错误: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/major-analysis', methods=['GET'])
def get_major_analysis():
    """获取专业分析数据"""
    try:
        scores_df = load_scores_data()
        if scores_df is None:
            # 如果没有分数线数据，返回模拟数据
            mock_majors = []
            for i in range(20):
                mock_majors.append({
                    '专业名称': f'专业{i+1}',
                    '总录取人数': 1000 - i * 30,
                    '开设学校数': 50 - i,
                    '平均分': 600 - i * 5,
                    '热度得分': 0.9 - i * 0.04
                })
            
            return jsonify({
                'total_majors': 100,
                'top_majors': mock_majors,
                'category_stats': {
                    '计算机类': {'录取人数': 5000, '专业数量': 15},
                    '电子信息类': {'录取人数': 4500, '专业数量': 12},
                    '机械类': {'录取人数': 4000, '专业数量': 10},
                    '经济管理类': {'录取人数': 6000, '专业数量': 18},
                    '医学类': {'录取人数': 3500, '专业数量': 8},
                    '其他': {'录取人数': 7000, '专业数量': 37}
                }
            })
        
        # 专业热度
        major_stats = scores_df.groupby('专业名称').agg({
            '录取人数': 'sum',
            '学校ID': 'nunique',
            '平均分': 'mean'
        }).reset_index()
        
        major_stats.columns = ['专业名称', '总录取人数', '开设学校数', '平均分']
        
        # 过滤无效专业
        major_stats = major_stats[
            (major_stats['专业名称'].notna()) & 
            (major_stats['专业名称'].astype(str).str.strip() != '')
        ]
        
        # 计算热度
        if len(major_stats) > 0:
            max_enroll = major_stats['总录取人数'].max()
            min_enroll = major_stats['总录取人数'].min()
            max_school = major_stats['开设学校数'].max()
            min_school = major_stats['开设学校数'].min()
            
            major_stats['热度得分'] = (
                (major_stats['总录取人数'] - min_enroll) / (max_enroll - min_enroll + 1) * 0.5 +
                (major_stats['开设学校数'] - min_school) / (max_school - min_school + 1) * 0.5
            )
        
        # 专业大类分类
        categories = {
            '计算机类': ['计算机', '软件', '人工智能', '数据', '网络', '信息'],
            '电子信息类': ['电子', '通信', '微电子', '光电'],
            '机械类': ['机械', '车辆', '自动化', '机器人'],
            '经济管理类': ['经济', '金融', '会计', '财务', '管理', '工商'],
            '医学类': ['临床', '医学', '药学', '护理', '口腔'],
            '其他': []
        }
        
        category_stats = {}
        for _, row in major_stats.iterrows():
            major = str(row['专业名称'])
            assigned = False
            for cat, keywords in categories.items():
                if any(k in major for k in keywords):
                    if cat not in category_stats:
                        category_stats[cat] = {'录取人数': 0, '专业数量': 0}
                    category_stats[cat]['录取人数'] += row['总录取人数']
                    category_stats[cat]['专业数量'] += 1
                    assigned = True
                    break
            if not assigned:
                if '其他' not in category_stats:
                    category_stats['其他'] = {'录取人数': 0, '专业数量': 0}
                category_stats['其他']['录取人数'] += row['总录取人数']
                category_stats['其他']['专业数量'] += 1
        
        # 热门专业TOP20
        top_majors = major_stats.sort_values('热度得分', ascending=False).head(20).to_dict('records')
        
        return jsonify({
            'total_majors': len(major_stats),
            'top_majors': top_majors,
            'category_stats': category_stats
        })
        
    except Exception as e:
        print(f"❌ 专业分析错误: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 创建数据目录
    os.makedirs('data', exist_ok=True)
    
    print("=" * 50)
    print("高考志愿数据分析系统启动")
    print("=" * 50)
    print(f"当前目录: {os.getcwd()}")
    print(f"数据文件: {SCHOOLS_FILE}")
    print(f"数据文件是否存在: {os.path.exists(SCHOOLS_FILE)}")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)