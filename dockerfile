# 使用 Python 3.13 的 Alpine 版本作为基础镜像
FROM python:3.13.0-alpine

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

# 创建非 root 用户和组
RUN addgroup -S expand && adduser -S expand -G expand

# 设置工作目录
WORKDIR ${APP_PATH}

# 复制 requirements.txt 文件到工作目录
COPY ./requirements.txt ${APP_PATH}/requirements.txt

# 复制 api.py 文件到工作目录
COPY ./api.py ${APP_PATH}/api.py

# 复制 Dockerfile 到工作目录
COPY ./dockerfile ${APP_PATH}/dockerfile

# 复制 config.sh 脚本到工作目录
COPY ./config.sh ${APP_PATH}/config.sh

# 拷贝 Construct 文件夹到工作目录
COPY ./Construct ${APP_PATH}/Construct

# 创建必要的文件夹
RUN mkdir -p ${EXPAND_DATA} ${EXPAND_ZIP} ${APP_PATH}/api_json

# 赋予 config.sh 可执行权限并运行脚本
RUN chmod +x ${APP_PATH}/config.sh && ${APP_PATH}/config.sh

# 更新包索引并安装 git
RUN apk update && apk add --no-cache git

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 更改工作目录的所有权
RUN chown -R expand:expand ${APP_PATH}

# 切换到非 root 用户
USER expand

# 暴露端口
EXPOSE ${PORT}

# 运行 Flask 应用
CMD ["python", "api.py"]