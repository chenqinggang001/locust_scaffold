

# docker-compose快速启动locust集群

### 快速开始

> 前置条件：已安装docker、docker-compose

#### 1、git clone

```
git clone https://github.com/chenqinggang001/locust_scaffold.git
```

```
cd locust_scaffold
```

> 注意：可能会遇到没有权限的问题，需要给目录授权

```
chmod 777 -R $PWD
```

#### 2、build镜像

```shell
# locust镜像
docker build -t mylocust . 
# flask镜像
docker build -f ./flask -t myflask .
```

> 注：如果需要更依赖执行 ``pipenv requirements > requirements.txt``，然后重新build镜像

或者也可以直接pull镜像

> 注意：pull镜像的方式，需要自己去docker-compose.yml中修改对应镜像名称

```
docker pull chenqinggang/locust
docker pull chenqinggang/flask
```

#### 3、编辑.env配置文件

```yaml
# locust脚本文件路径
# 注意!!!: 这是在docker容器中的路径,容器中所在工作路径是/mnt/locust,即当前目录映射在/mnt/locust
LOCUST_FILE_PATH=/mnt/locust/locustfiles/stu/stu_login.py
# 主机的IP地址,用于从机绑定主机,分布式情况下需要用主机的局域网或者公网IP
LOCUST_HOST=110.42.182.87
# 主机暴露的地址,0.0.0.0表示公网/局域网地址都可以访问
LOCUST_MASTER_HOST=0.0.0.0
# 不建议改端口,改了还得去docker-compose.yml改启动命令
WEB_PROT=8089
MASTER_PROT=5557
CONTAINER_NAME=mylocust
FLASK_APP=myflask
FLASK_APP_HOST=110.42.182.87


# redis配置,可以单独部署一个redis服务器,单独部署后修改redis_store.py文件中的配置即可
REDIS_VERSION=7.0.7
# your redis host
REDIS_HOST=110.42.182.87
REDIS_DIR=/data/redis
REAL_REDIS_PORT=6379
# your redis password
REDIS_PASSWORD=yourredispwd
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
