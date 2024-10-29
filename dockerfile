FROM python:3.12-alpine

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV HOST=127.0.0.1
ENV PORT=8165
ENV API_JSON="/opt/app/api_json"
ENV APP_PATH="/opt/app"
ENV EXPAND_ZIP="/opt/app/data"
ENV EXPAND_DATA="/opt/app/expand_data"
ENV EXPAND_TMP="/opt/app/temp"
ENV UPDATES=1800
ENV RETRY_INTS=5
ENV RETRY_INTERVAL=5

# 设置工作目录
WORKDIR ${APP_PATH}

# 复制当前目录的内容到工作目录
COPY ./requirements.txt ${APP_PATH}/requirements.txt
COPY ./api.py ${APP_PATH}/api.py
COPY ./dockerfile ${APP_PATH}/dockerfile
COPY ./config.sh ${APP_PATH}/config.sh

# 拷贝文件夹
COPY ./Construct ${APP_PATH}/Construct

# 创建文件夹
RUN mkdir -p ${EXPAND_DATA} ${EXPAND_ZIP} ${APP_PATH}/api_json

# 赋予 config.sh 可执行权限并运行脚本
RUN chmod +x ${APP_PATH}/config.sh && ${APP_PATH}/config.sh

# 安装依赖
RUN apk update && apk add --no-cache git

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE ${PORT}

# 运行 Flask 应用
CMD ["sh", "-c", "python api.py"]