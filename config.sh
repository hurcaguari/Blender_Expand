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

[addons.auto_highlight_in_outliner]
path_type = "url"
path = "http://blender4.com/add-ons/auto-highlight-in-outliner/3.8.2/download/add-on-auto-highlight-in-outliner-v3.8.2.zip"

[addons.Drop_it]
path_type = "url"
path = "http://blender4.com/add-ons/drop-it/1.0.3/download/add-on-drop-it-v1.0.3.zip"

[addons.io_scene_max]
path_type = "url"
path = "https://raw.githubusercontent.com/hurcaguari/Blender_Expand/main/__release__/io_scene_max.zip"

[addons.mesh_looptools]
path_type = "url"
path = "https://raw.githubusercontent.com/hurcaguari/Blender_Expand/main/__release__/looptools.zip"

[addons.per_camera_resolution]
path_type = "git"
path = "https://github.com/kevancress/per_camera_resolution"

[addons.Quad_Remesher]
path_type = "url"
path = "https://raw.githubusercontent.com/hurcaguari/Blender_Expand/main/__release__/Quad_Remesher.zip"
EOL