## 从dockerhub拉取一个python镜像
#FROM python:3.11.1
#
## 在python镜像的根目录创建一个mytest文件夹
#RUN mkdir -p /mytest/locust
#
## 指定当前工作目录是mytest
## 相当于cd mytest （这么理解不是非常准确）
#WORKDIR /mytest/locust
#
## 添加主机当前目录下的所有文件到镜像的mytest里面
#ADD . .
#
## 在python镜像中执行安装依赖，更改时区
#RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ \
#    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
#    && echo 'Asia/Shanghai' >/etc/timezone

# 从dockerhub拉取一个python镜像
FROM locustio/locust
# 在python镜像中执行安装依赖，更改时区
ADD requirements.txt requirements.txt
ENV TZ=Asia/Shanghai
ENV PYTHONPATH "${PYTHONPATH}:/mnt/locust"
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/