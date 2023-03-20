# 示例命令
# 打包镜像
docker build -t mylocust .
# 启动前先授予/data/locust目录权限
chmod -R 777 /data/locust
# 启动命令示例
# 启动
docker-compose up -d --scale worker=2
# 停止
docker-compose down
# 分布式情况下从机上单独启动worker,cpu有多少个核心就启动多少个worker
docker-compose up -d --scale worker=3 worker
# 本地调试单独启动启动flask应用
docker-compose -f app.yml up -d