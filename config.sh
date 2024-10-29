#!/bin/sh

# 使用环境变量创建 config.toml 文件
mkdir -p ${APP_PATH}/config

cat <<EOL > ${APP_PATH}/config/config.toml

urlpath = "http://${HOST}:${PORT}"
api_json = "${APP_PATH}/api_json/expand.json"
updates = ${UPDATES}
expand_path = "${EXPAND_DATA}"
expand_zip = "${EXPAND_ZIP}"
expand_tmp = "${EXPAND_TMP}"

[retry]
retry_ints = ${RETRY_INTS}
retry_interval = ${RETRY_INTERVAL}

[addons.utilities_gadget]
path_type = "git"
path = ""
EOL