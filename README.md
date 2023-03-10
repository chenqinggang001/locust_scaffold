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



#### 配置grafana监控

#### 1、访问grafana

> 初始账号：admin  密码：admin

```
# 上面.env中配置的ip地址+端口号访问
http://192.168.10.181:3000/
```

#### 2、配置prometheus数据源

点击添加数据源

![image-20230210175242636](./testdata/imgs/image-20230210174054504.png)

选择Prometheus，设置Prometheus地址，并保存

![image-20230210175310510](./testdata/imgs/image-20230210174230165.png)

![image-20230210175315168](./testdata/imgs/image-20230210174301373.png)

导入模板，输入模板ID，点击导入，设置Prometheus数据源，导入模板

![image-20230210175321252](./testdata/imgs/image-20230210174339243.png)

![image-20230210175326107](./testdata/imgs/image-20230210174438754.png)

![image-20230210175331609](./testdata/imgs/image-20230210174635240.png)

#### 3、运行locust查看监控

访问locust

```
http://192.168.10.181:8089/
```

启动测试

![image-20230210175337890](./testdata/imgs/image-20230210174902793.png)

![](./testdata/imgs/image-20230210174914705.png)

查看监控

![image-20230210175348978](./testdata/imgs/image-20230210175059193.png)
