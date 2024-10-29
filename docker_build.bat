@echo off
echo docker 登录
docker login
echo 生成 requirements.txt
pip freeze > requirements.txt
echo 删除旧镜像
docker rmi expand:arm64
echo 构建新镜像
docker buildx build --platform linux/arm64 -t expand:arm64 .
echo 保存镜像
docker save -o expand_arm64.tar expand:arm64 
echo 打标签
docker tag expand:arm64 docker.io/hurcaguari/expand:arm64
echo 推送镜像
docker push docker.io/hurcaguari/expand:arm64