@echo off
echo docker ��¼
docker login
echo ���� requirements.txt
pip freeze > requirements.txt
echo ɾ���ɾ���
docker rmi expand:arm64
echo �����¾���
docker buildx build --platform linux/arm64 -t expand:arm64 .
echo ���澵��
docker save -o expand_arm64.tar expand:arm64 
echo ���ǩ
docker tag expand:arm64 docker.io/hurcaguari/expand:arm64
echo ���;���
docker push docker.io/hurcaguari/expand:arm64