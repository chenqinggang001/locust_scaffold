# 从dockerhub拉取一个python镜像
FROM locustio/locust
# 在python镜像中执行安装依赖，更改时区
ADD requirements.txt requirements.txt
ENV TZ=Asia/Shanghai
ENV PYTHONPATH "${PYTHONPATH}:/mnt/locust"
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/