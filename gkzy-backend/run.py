from app import create_app

app = create_app()

"""运行 Flask 应用程序"""
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)