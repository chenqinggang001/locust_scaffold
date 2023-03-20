# docker-compose快速启动locust集群

### 简介

这是一个locust脚手架项目，有以下这些内容：

1、通过docker一键部署locust集群

2、prometheus、influxdb、grafana性能测试结果监控

3、可供练习的测试接口

4、locust监控配置、跨节点通信、自定义参数、redis存储测试数据等示例代码参考

### 快速开始

> 前置条件：已安装docker、docker-compose

#### 1、git clone

```
git clone https://github.com/chenqinggang001/locust_scaffold.git
```

```
cd locust_scaffold
```

> 注意：可能会遇到没有权限的问题，需要给目录授权 `chmod -R 777 /your/path/locust_scaffold`

#### 2、build镜像

```shell
# locust镜像
docker build -t mylocust . 
# flask镜像
docker build -f .\flask -t myflask .
```

或者也可以直接pull镜像

> 注意：pull镜像的方式，需要自己去docker-compose.yml中修改对应镜像名称

```
docker pull chenqinggang/locust
docker pull chenqinggang/flask
```

#### 3、编辑.env配置文件

```yaml
# git update-index --assume-unchanged .env
# locust脚本文件路径
LOCUST_FILE_PATH=/mnt/locust/locustfiles/stu/stu_login.py
# 主机的IP地址,用于从机绑定主机,分布式情况下需要用主机的局域网或者公网IP
LOCUST_HOST=192.168.10.181
# 主机暴露的地址,0.0.0.0表示所有地址都可以访问
LOCUST_MASTER_HOST=0.0.0.0
# locust的web页面端口
WEB_PROT=8089
# locust master监听端口
MASTER_PROT=5557
# locust容器名称，默认为mylocust:latest，即构建镜像时的镜像名称
CONTAINER_NAME=mylocust:latest
# flask应用容器名称
FLASK_APP=myflask:latest


# redis配置,可以单独部署一个redis服务器,单独部署后修改redis_store.py文件中的配置即可
# redis版本号
REDIS_VERSION=7.0.7
# redis主机地址
REDIS_HOST=192.168.10.181
# redis端口号
REAL_REDIS_PORT=6379
# redis密码
REDIS_PASSWORD=rdspwd123456!
```

#### 4、启动集群

启动loucst-master、loucst-worker、prometheus、influxdb、grafana、flask、redis

```
docker-compose up -d
```

分布式模式下，施压机器单独启动worker，cpu有多少个核心就启动多少个worker

```
docker-compose up -d --scale worker=3 worker
```

#### 配置grafana监控参考：[prometheus + influxdb + grafana 配置locust监控](https://blog.csdn.net/qq_41522024/article/details/128997655)
