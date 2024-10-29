# Blender 插件扩展管理系统

Blender 插件扩展管理系统是一个用于管理和更新 Blender 插件的自动化工具。该系统通过 Flask 提供 API 接口，支持插件的下载、解压、更新和管理。项目旨在简化 Blender 插件的管理流程，提高开发和使用插件的效率。

#### 项目结构
项目的目录结构如下：

```
api_json/
	expand.json
api.py
compose-dev.yaml
config/
	config.toml
config.sh
Construct/
	__init__.py
	fileio.py
	giturl.py
	tool.py
	utils.py
```

#### 主要功能
1. **插件管理**：
    - 支持从 Git 仓库或 URL 下载插件。
    - 自动解压和安装插件。
    - 定期更新插件列表。

2. **API 接口**：
    - 提供 `/upexpand` 路由用于更新插件列表。
    - 提供 `/plugin` 路由用于获取插件列表。
    - 提供 `/data/<filename>` 路由用于获取插件文件。

3. **配置管理**：
    - 使用 

config.toml

 文件进行配置管理。
    - 支持通过环境变量动态生成配置文件。

#### 关键文件和代码
1. **api.py**：
    - 定义了 Flask 应用的路由和处理逻辑。
    - 通过 [`ConstructApi`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FHurca%2FOneDrive%2FGitCode%2Fblender_expand_docker%2Fapi.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A92%2C%22character%22%3A8%7D%7D%5D%2C%2264aa3dc4-5ad8-4d52-8ede-591f38e5bfbd%22%5D "Go to definition") 函数更新插件列表。
    - 提供了获取插件列表和插件文件的 API 接口。

2. **config/config.toml**：
    - 定义了插件的路径、更新频率等配置信息。
    - 支持插件的 Git 仓库路径和下载 URL。

3. **Construct/tool.py**：
    - 包含 [`ConstructApi`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fc%3A%2FUsers%2FHurca%2FOneDrive%2FGitCode%2Fblender_expand_docker%2Fapi.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A92%2C%22character%22%3A8%7D%7D%5D%2C%2264aa3dc4-5ad8-4d52-8ede-591f38e5bfbd%22%5D "Go to definition") 函数，用于构建 API 文件并更新插件列表。
    - 处理插件的下载、解压和信息构建。

4. **dockerfile** 和 **docker_build.bat**：
    - 定义了 Docker 镜像的构建过程。
    - 包含安装依赖、复制文件和运行脚本的步骤。

#### 使用方法
1. **环境配置**：
    - 通过 config.sh 脚本生成 config.toml 配置文件。
    - 配置环境变量以适应不同的运行环境。

2. **启动应用**：
    - 使用 Docker 构建和运行应用。
    - 通过 docker_build.bat 脚本进行 Docker 镜像的构建和保存。

3. **访问 API**：
    - 通过 `/upexpand` 路由更新插件列表。
    - 通过 `/plugin` 路由获取插件列表。
    - 通过 `/data/<filename>` 路由获取插件文件。

#### 详细步骤
1. **配置环境**：
    - 确保已安装 Docker 和 Docker Compose。
    - 运行 config.sh 脚本生成配置文件：
      ```sh
      ./config.sh
      ```

2. **构建 Docker 镜像**：
    - 运行 docker_build.bat 脚本构建 Docker 镜像：
      ```sh
      ./docker_build.bat
      ```

3. **启动应用**：
    - 使用 Docker Compose 启动应用：
      ```sh
      docker-compose -f compose-dev.yaml up
      ```

4. **访问 API**：
    - 在浏览器中访问 `http://localhost:8165` 查看 API 文档。
    - 使用以下路由进行操作：
      - `/upexpand`：更新插件列表。
      - `/plugin`：获取插件列表。
      - `/data/<filename>`：获取插件文件。

#### 示例代码
以下是 api.py 文件的关键部分代码：

```python
from flask import Flask, request, jsonify, send_file, make_response
from werkzeug.routing import BaseConverter
from Construct.tool import ConstructApi
from os.path import exists, join
from os import environ
import argparse
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
    file_path = join(CONFIG.expand_zip, filename)
    if not exists(file_path):
        return jsonify({"error": "文件不存在"}), 404
    response = make_response(send_file(file_path, as_attachment=True))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/plugin', methods=['GET', 'POST'])
def plugin():
    json_file_path = join(CONFIG.api_json, 'expand.json')
    if not exists(json_file_path):
        return ConstructApi(json_file_path)
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json_load(json_file)
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def scheduled_task():
    time.sleep(0.1)
    while True:
        print(f"{TimeStamp()} [INFO] 更新插件列表") if not exists(join(CONFIG.api_json, 'expand.json')) else None
        ConstructApi(join(CONFIG.api_json, 'expand.json')) if not exists(join(CONFIG.api_json, 'expand.json')) else None
        time.sleep(CONFIG.updates)

if __name__ == '__main__':
    port = environ.get('PORT', '8165')
    parser = argparse.ArgumentParser(description='启动 Flask 应用')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址')
    parser.add_argument('--port', default=port, type=int, help='端口号')
    args = parser.parse_args()
    threading.Thread(target=scheduled_task, daemon=True).start()
    app.run(host=args.host, port=args.port)
```

通过上述步骤和代码示例，你可以轻松地配置和使用 Blender 插件扩展管理系统。该系统提供了灵活的配置和强大的插件管理功能，适用于 Blender 插件开发者和用户。