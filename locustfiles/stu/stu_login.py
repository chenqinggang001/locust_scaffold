import json

from locust import task, between, SequentialTaskSet, FastHttpUser

from common.redis_store import redis_store
from common.logger_handler import get_logger
from common.prometheus_exporter import *


logger = get_logger('chenqg', file=True)


class StuLogin(SequentialTaskSet):

    @task
    def login(self):
        # 在用户信息队列中，获取用户名
        username = usernames_queue.get()["username"]
        headers = {"Content-Type": "application/json"}
        data = json.dumps({'loginName': username, 'password': 'password'})
        with self.client.post("/users/login", data=data, headers=headers) as login_res:
            logger.info(login_res.text)
            assert login_res.status_code == 200
            redis_store.set(f"{username}_orgid", str(login_res.json()['orgId']))
            redis_store.set(f"{username}_token", login_res.json()['authorization'])
            redis_store.set(f"{username}_userid", str(login_res.json()['userId']))

        token = redis_store.get(f"{username}_token")
        headers = {"Content-Type": "application/json", "Authorization": token}
        param = {"keyword": "", "publishStatus": "1", "type": "1",
                 "pn": "1", "ps": "15", "lang": "zh"}
        with self.client.get("/courses/students", headers=headers, params=param) as course_res:
            assert course_res.status_code == 200
            redis_store.set(f"{username}_ocid", course_res.json()["courseList"][0]["id"])
            redis_store.set(f"{username}_classid", course_res.json()["courseList"][0]["classId"])
        # logger.info(f"orgid: {self.parent.redis_store.get(f'{username}_orgid')} \n"
        #             f"token: {self.parent.redis_store.get(f'{username}_token')} \n"
        #             f"userid: {self.parent.redis_store.get(f'{username}_userid')} \n"
        #             f"ocid: {self.parent.redis_store.get(f'{username}_ocid')}")
        # 单个用户结束了，将用户名放回队列
        usernames_queue.put({"username": username})


class LoginUser(FastHttpUser):
    wait_time = between(1, 2)
    host = "https://apoi1.xxx.cn"

    tasks = [StuLogin]
