import json

from locust import task, between, SequentialTaskSet, FastHttpUser

from common.redis_store import redis_store
from common.prometheus_exporter import *


logger = get_logger('chenqg')


class StuLogin(SequentialTaskSet):

    @task
    def login(self):
        # 在用户信息队列中，获取用户名
        username = usernames_queue.get()["username"]
        headers = {"Content-Type": "application/json"}
        data = json.dumps({'username': username, 'password': '123456'})
        with self.client.post("/users/login/", data=data, headers=headers) as login_res:
            logger.info(login_res.text)
            assert login_res.status_code == 200
            redis_store.set(f"{username}_token", login_res.json()['token'])
            redis_store.set(f"{username}_userid", str(login_res.json()['id']))

        token = redis_store.get(f"{username}_token")
        headers = {"Content-Type": "application/json", "Authorization": token}
        with self.client.get("/course/list/", headers=headers) as course_res:
            assert course_res.status_code == 200
            for i in course_res.json()["courseList"]:
                if i["name"] == "性能测试使用的课程":
                    redis_store.set(f"{username}_ocid", i["id"])
                    break
        logger.info(f"token: {redis_store.get(f'{username}_token')} \n"
                    f"userid: {redis_store.get(f'{username}_userid')} \n"
                    f"ocid: {redis_store.get(f'{username}_ocid')}")
        # 单个用户结束了，将用户名放回队列
        usernames_queue.put({"username": username})


class StuLoginUser(FastHttpUser):
    wait_time = between(1, 2)
    flas_app_host = os.environ.get('FLASK_APP_HOST')
    host = f"http://{flas_app_host}:8000"
    tasks = [StuLogin]
