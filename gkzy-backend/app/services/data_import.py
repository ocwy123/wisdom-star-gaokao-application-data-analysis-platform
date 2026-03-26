# -*- coding: utf-8 -*-
"""
数据导入服务模块
提供文件上传、数据解析、清洗和导入功能
"""

import os
import pandas as pd
import json
import tempfile
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.services.admin_auth import admin_required

# 导入数据模型
from app.models import School, Major, SchoolMajor, AdmRecord, SchoolHeat, MajorEmployment, ScoreSegment

# 创建蓝图
data_import_bp = Blueprint('data_import', __name__, url_prefix='/api/admin')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'csv': ['csv'],
    'excel': ['xlsx', 'xls'],
    'jl': ['jl', 'json']
}

# 上传目录配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename, file_type):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])

def get_file_extension(file_type):
    """获取文件类型的扩展名"""
    extensions = {
        'csv': '.csv',
        'excel': '.xlsx',
        'jl': '.jl'
    }
    return extensions.get(file_type, '.csv')

@data_import_bp.route('/upload', methods=['POST'])
@admin_required
def upload_file(current_admin):
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        # 获取文件类型参数
        file_type = request.form.get('fileType', 'csv')
        
        if file and allowed_file(file.filename, file_type):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加时间戳避免重名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # 保存文件
            file.save(file_path)
            
            return jsonify({
                'success': True,
                'message': '文件上传成功',
                'data': {
                    'fileName': filename,
                    'filePath': file_path
                }
            })
        else:
            return jsonify({
                'success': False, 
                'message': f'不支持的文件格式，请选择{get_file_extension(file_type)}格式文件'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"文件上传错误: {e}")
        return jsonify({'success': False, 'message': '文件上传失败'}), 500

@data_import_bp.route('/data-import', methods=['POST'])
@admin_required
def data_import(current_admin):
    """数据导入接口"""
    try:
        data = request.get_json()
        
        # 验证参数
        required_fields = ['fileType', 'targetTable', 'filePath']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'缺少参数: {field}'}), 400
        
        file_type = data['fileType']
        target_table = data['targetTable']
        file_path = data['filePath']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '文件不存在'}), 400
        
        # 根据目标表选择导入函数
        import_functions = {
            'edu_school': import_school_data,
            'edu_major': import_major_data,
            'edu_school_major': import_school_major_data,
            'edu_adm_record': import_adm_record_data,
            'ana_school_heat': import_school_heat_data,
            'ana_major_employment': import_major_employment_data,
            'ana_score_segment': import_score_segment_data
        }
        
        if target_table not in import_functions:
            return jsonify({'success': False, 'message': '不支持的数据表'}), 400
        
        # 执行导入（包含详细的日志信息）
        result = import_functions[target_table](file_path, file_type)
        
        return jsonify({
            'success': True,
            'message': '数据导入完成',
            'data': result,
            'logs': result.get('logs', [])  # 返回详细的日志信息
        })
        
    except Exception as e:
        current_app.logger.error(f"数据导入错误: {e}")
        return jsonify({'success': False, 'message': f'数据导入失败: {str(e)}'}), 500

def import_school_data(file_path, file_type):
    """导入高校数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取高校数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_school_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        # 数据验证
        logs.append({'type': 'info', 'message': '进行数据验证...'})
        validation_result = validate_school_data(df_cleaned)
        logs.extend(validation_result.get('logs', []))
        
        logs.append({'type': 'success', 'message': '高校数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_major_data(file_path, file_type):
    """导入专业数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取专业数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_major_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '专业数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_school_major_data(file_path, file_type):
    """导入高校专业关系数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取高校专业关系数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_school_major_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '高校专业关系数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_adm_record_data(file_path, file_type):
    """导入招生录取数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取招生录取数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_adm_record_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '招生录取数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_school_heat_data(file_path, file_type):
    """导入高校热度数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取高校热度数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_school_heat_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '高校热度数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_major_employment_data(file_path, file_type):
    """导入专业就业数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取专业就业数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_major_employment_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '专业就业数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def import_score_segment_data(file_path, file_type):
    """导入一分一段数据"""
    logs = []
    
    try:
        logs.append({'type': 'info', 'message': '开始读取一分一段数据文件...'})
        df = read_data_file(file_path, file_type)
        logs.append({'type': 'success', 'message': f'文件读取成功，共{len(df)}条记录'})
        
        logs.append({'type': 'info', 'message': '开始数据清洗...'})
        df_cleaned = clean_score_segment_data(df)
        logs.append({'type': 'success', 'message': f'数据清洗完成，有效记录{len(df_cleaned)}条'})
        
        logs.append({'type': 'success', 'message': '一分一段数据导入准备完成'})
        
        return {
            'total_records': len(df),
            'cleaned_records': len(df_cleaned),
            'sample_data': df_cleaned.head(3).to_dict('records') if len(df_cleaned) > 0 else [],
            'logs': logs
        }
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'导入过程中发生错误: {str(e)}'})
        return {
            'total_records': 0,
            'cleaned_records': 0,
            'sample_data': [],
            'logs': logs
        }

def read_data_file(file_path, file_type):
    """读取数据文件"""
    try:
        if file_type == 'csv':
            return pd.read_csv(file_path, encoding='utf-8')
        elif file_type == 'excel':
            return pd.read_excel(file_path)
        elif file_type == 'jl':
            # JL格式通常是JSON Lines格式
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line.strip()))
            return pd.DataFrame(data)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
    except Exception as e:
        raise Exception(f"文件读取失败: {str(e)}")

def clean_school_data(df):
    """清洗高校数据"""
    # 这里实现具体的数据清洗逻辑
    # 示例：去除空值、标准化字段等
    df_cleaned = df.copy()
    
    # 去除完全为空的行
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 标准化学校名称（如果有的话）
    if 'name' in df.columns:
        df_cleaned['name'] = df_cleaned['name'].str.strip()
    
    return df_cleaned

def clean_major_data(df):
    """清洗专业数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    if 'name' in df.columns:
        df_cleaned['name'] = df_cleaned['name'].str.strip()
    
    return df_cleaned

def clean_school_major_data(df):
    """清洗高校专业关系数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 确保必要的字段存在
    required_cols = ['school_id', 'major_id']
    for col in required_cols:
        if col in df.columns:
            df_cleaned = df_cleaned.dropna(subset=[col])
    
    return df_cleaned

def clean_adm_record_data(df):
    """清洗招生录取数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 数值字段处理
    numeric_cols = ['plan_count', 'min_score']
    for col in numeric_cols:
        if col in df.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
    
    return df_cleaned

def clean_school_heat_data(df):
    """清洗高校热度数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 数值字段处理
    if 'view_count' in df.columns:
        df_cleaned['view_count'] = pd.to_numeric(df_cleaned['view_count'], errors='coerce')
    if 'favorite_count' in df.columns:
        df_cleaned['favorite_count'] = pd.to_numeric(df_cleaned['favorite_count'], errors='coerce')
    
    return df_cleaned

def clean_major_employment_data(df):
    """清洗专业就业数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 就业率字段处理
    if 'employment_rate' in df.columns:
        df_cleaned['employment_rate'] = pd.to_numeric(df_cleaned['employment_rate'], errors='coerce')
    
    return df_cleaned

def clean_score_segment_data(df):
    """清洗一分一段数据"""
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.dropna(how='all')
    
    # 数值字段处理
    numeric_cols = ['score', 'count', 'cumulative_count']
    for col in numeric_cols:
        if col in df.columns:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
    
    return df_cleaned

def validate_school_data(df):
    """验证高校数据"""
    logs = []
    
    # 检查必要字段
    required_fields = ['name', 'province', 'type']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        logs.append({'type': 'warning', 'message': f'缺少字段: {missing_fields}'})
    else:
        logs.append({'type': 'success', 'message': '必要字段检查通过'})
    
    # 检查空值
    for field in df.columns:
        null_count = df[field].isnull().sum()
        if null_count > 0:
            logs.append({'type': 'warning', 'message': f'字段 {field} 有 {null_count} 个空值'})
    
    # 检查重复值
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        logs.append({'type': 'warning', 'message': f'发现 {duplicate_count} 条重复记录'})
    
    return {'logs': logs}

def validate_major_data(df):
    """验证专业数据"""
    logs = []
    
    # 检查必要字段
    required_fields = ['name', 'category']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        logs.append({'type': 'warning', 'message': f'缺少字段: {missing_fields}'})
    else:
        logs.append({'type': 'success', 'message': '必要字段检查通过'})
    
    return {'logs': logs}

def validate_school_major_data(df):
    """验证高校专业关系数据"""
    logs = []
    
    required_fields = ['school_id', 'major_id']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        logs.append({'type': 'warning', 'message': f'缺少字段: {missing_fields}'})
    else:
        logs.append({'type': 'success', 'message': '必要字段检查通过'})
    
    return {'logs': logs}

def validate_adm_record_data(df):
    """验证招生录取数据"""
    logs = []
    
    required_fields = ['school_id', 'major_name', 'year', 'province']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        logs.append({'type': 'warning', 'message': f'缺少字段: {missing_fields}'})
    else:
        logs.append({'type': 'success', 'message': '必要字段检查通过'})
    
    return {'logs': logs}