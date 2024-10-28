from flask import Flask, jsonify, send_file, make_response
from werkzeug.routing import BaseConverter
from os.path import exists, join
from os import environ
from json import load as json_load
import argparse

from Construct import CONFIG
from Construct import TimeStamp
from Construct import ConstructApi
import threading
import time
import sys

# 禁用输出缓冲
sys.stdout.flush()
sys.stderr.flush()

app = Flask(__name__)

# 创建自定义转换器
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]

# 注册自定义转换器
app.url_map.converters['regex'] = RegexConverter

@app.route('/', methods=['GET', 'POST'])
def hello():
    response = make_response('''
    <html>
        <body>
            <p>/upexpand - 更新插件列表<br></p>
            <p>/plugin - 获取插件列表<br></p>
            <p>/data/&lt;filename&gt; - 获取文件<br></p>
        </body>
    </html>
    ''')
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/upexpand', methods=['GET', 'POST'])
def upexpand():
    response = make_response(ConstructApi(join(CONFIG.api_json, 'expand.json')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/data/<regex(".*"):filename>', methods=['GET'])
def get_file(filename):
    # 假设文件存储在 'files' 目录中
    file_path = join(CONFIG.expand_zip, filename)
    
    # 检查文件是否存在
    if not exists(file_path):
        return jsonify({"error": "文件不存在"}), 404
    
    # 返回文件
    response = make_response(send_file(file_path, as_attachment=True))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/plugin', methods=['GET', 'POST'])
def plugin():
    # 假设 JSON 文件路径为 'expand.json'
    json_file_path = join(CONFIG.api_json, 'expand.json')
    
    # 检查文件是否存在
    if not exists(json_file_path):
        return ConstructApi(join(CONFIG.api_json, 'expand.json'))
    
    # 读取 JSON 文件内容并返回
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json_load(json_file)
    
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def scheduled_task():
    time.sleep(0.1)  # 等待 3 秒，确保 Flask 应用已经启动
    while True:
        print(f"{TimeStamp()} [INFO] 更新插件列表") if not exists(join(CONFIG.api_json, 'expand.json')) else None
        ConstructApi(join(CONFIG.api_json, 'expand.json')) if not exists(join(CONFIG.api_json, 'expand.json')) else None
        time.sleep(CONFIG.updates)  # 每 <CONFIG.updates> 秒执行一次

if __name__ == '__main__':
    # 从环境变量获取端口号，默认为 8165
    port = environ.get('PORT', '8165')
    # 创建解析器
    parser = argparse.ArgumentParser(description='启动 Flask 应用')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址')
    parser.add_argument('--port', default=port, type=int, help='端口号')
    args = parser.parse_args()
    
    # 启动定时任务线程
    threading.Thread(target=scheduled_task, daemon=True).start()
    
    # 启动 Flask 应用
    app.run(host=args.host, port=args.port)