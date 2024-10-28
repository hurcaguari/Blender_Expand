docker login -u 
pip freeze > requirements.txt
docker rmi expand:arm64
docker buildx build --platform linux/arm64 -t expand:arm64 .
docker save -o expand_arm64.tar expand:arm64 
docker tag expand:arm64 docker.io/hurcaguari/expand:arm64
docker push docker.io/hurcaguari/expand:arm64