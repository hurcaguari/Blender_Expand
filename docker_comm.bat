docker rmi expand
docker buildx build --platform linux/arm64 -t expand .
docker save -o expand_arm64.tar expand 