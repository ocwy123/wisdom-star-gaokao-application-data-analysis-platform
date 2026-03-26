#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据导入功能的简单脚本
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 创建一个简化的Flask应用来测试数据导入功能
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# 添加CORS支持
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'], supports_credentials=True)

# MySQL数据库配置
DB_CONFIG = {
    'host': '192.168.54.241',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'gkzy_mysql',
    'charset': 'utf8mb4'
}

def connect_db():
    """创建数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

# 上传目录配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'csv': ['csv'],
    'excel': ['xlsx', 'xls'],
    'jl': ['jl', 'json']
}

def allowed_file(filename, file_type):
    """检查文件扩展名是否允许"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])

@app.route('/api/admin/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    """文件上传接口"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("收到文件上传请求")
        print("请求文件:", request.files)
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        # 获取文件类型参数
        file_type = request.form.get('fileType', 'csv')
        print(f"文件类型: {file_type}, 文件名: {file.filename}")
        
        if file and allowed_file(file.filename, file_type):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加时间戳避免重名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # 保存文件
            file.save(file_path)
            
            print(f"文件保存成功: {file_path}")
            
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
                'message': f'不支持的文件格式，请选择正确的文件格式'
            }), 400
            
    except Exception as e:
        print(f"文件上传错误: {e}")
        return jsonify({'success': False, 'message': '文件上传失败'}), 500

# 添加管理员认证相关的接口
@app.route('/api/admin/users', methods=['GET', 'OPTIONS'])
def get_users():
    """获取用户列表（从数据库获取）"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 连接到数据库
        conn = connect_db()
        if not conn:
            return jsonify({'success': False, 'message': '数据库连接失败'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # 查询用户表数据（根据您提供的表结构）
        query = """
            SELECT 
                id, 
                username, 
                nickname as real_name,
                phone, 
                email, 
                role, 
                register_time as created_at,
                status,
                updated_at
            FROM usr_user 
            ORDER BY id
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        # 格式化日期字段
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if user['updated_at']:
                user['updated_at'] = user['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"从数据库获取到 {len(users)} 个用户")
        
        return jsonify({
            'success': True,
            'data': users,
            'total': len(users),
            'page': 1,
            'pageSize': 10
        })
        
    except Error as e:
        print(f"数据库查询错误: {e}")
        return jsonify({'success': False, 'message': f'数据库查询失败: {str(e)}'}), 500

@app.route('/api/admin/profile', methods=['GET', 'OPTIONS'])
def get_profile():
    """获取管理员信息（模拟接口）"""
    if request.method == 'OPTIONS':
        return '', 200
    
    # 模拟返回管理员信息
    return jsonify({
        'success': True,
        'data': {
            'id': 1,
            'username': 'admin',
            'email': 'admin@example.com',
            'real_name': '管理员',
            'role': 'admin'
        }
    })

@app.route('/api/admin/data-import', methods=['POST', 'OPTIONS'])
def data_import():
    """数据导入接口"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        print("收到数据导入请求:", data)
        
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
        
        # 模拟导入过程
        logs = [
            {'type': 'info', 'message': '开始数据导入...'},
            {'type': 'success', 'message': f'目标数据表: {target_table}'},
            {'type': 'info', 'message': '读取文件数据...'},
            {'type': 'success', 'message': '文件读取成功'},
            {'type': 'info', 'message': '进行数据清洗...'},
            {'type': 'success', 'message': '数据清洗完成'},
            {'type': 'info', 'message': '数据验证...'},
            {'type': 'success', 'message': '数据验证通过'},
            {'type': 'success', 'message': '数据导入准备完成'}
        ]
        
        return jsonify({
            'success': True,
            'message': '数据导入完成',
            'data': {
                'total_records': 100,
                'cleaned_records': 95,
                'sample_data': []
            },
            'logs': logs
        })
        
    except Exception as e:
        print(f"数据导入错误: {e}")
        return jsonify({'success': False, 'message': f'数据导入失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动测试服务器...")
    print(f"上传目录: {UPLOAD_FOLDER}")
    app.run(debug=True, host='0.0.0.0', port=5001)