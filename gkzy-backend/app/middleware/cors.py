from flask import Flask, request, jsonify

def add_cors_headers(response):
    """添加CORS头"""
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

def init_cors(app):
    """初始化CORS"""
    @app.after_request
    def after_request(response):
        return add_cors_headers(response)
    
    @app.route('/options', methods=['OPTIONS'])
    def handle_options():
        return '', 200