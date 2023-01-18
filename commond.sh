# 启动命令示例
# 启动
docker-compose up -d --scale worker=2
# 停止
docker-compose down
# 分布式情况下从机上单独启动worker,cpu有多少个核心就启动多少个worker
docker-compose up -d --scale worker=3 worker