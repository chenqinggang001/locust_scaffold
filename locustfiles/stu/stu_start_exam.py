from locust import task, between, SequentialTaskSet, FastHttpUser

from common.prometheus_exporter import *
from common.redis_store import redis_store

logger = get_logger('chenqg')


class StuLoadExam(SequentialTaskSet):

    # 初始化用户信息
    def __init__(self, parent):
        super().__init__(parent)
        self.user_info = None
        self.token = None
        self.ocid = None
        self.userid = None

    @task
    def exams_student(self):
        # 在用户信息队列中，获取用户名
        self.user_info = usernames_queue.get()

        username = self.user_info.get("username")
        # 通过用户名，从redis中获取用户信息
        self.token = redis_store.get(f"{username}_token")
        self.ocid = redis_store.get(f"{username}_ocid")
        self.userid = redis_store.get(f"{username}_userid")
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        param = {"ocId": self.ocid}
        # logger.info(f"param: {param}, headers: {headers}, user_info: {self.user_info}")
        with self.client.get("/exams/list/", headers=headers,
                             params=param, name='获取考试列表: /exams/list/') as res:
            assert res.status_code == 200
            for i in res.json()["examList"]:
                if i["title"] == "性能测试使用的考试":
                    self.user_info["examId"] = i["examId"]
                    break

    @task
    def exams_start(self):
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        param = {"examId": self.user_info.get('examId')}
        with self.client.get("/exams/info/", headers=headers, params=param,
                             name='获取考试基础信息: /exams/info/') as res:
            self.user_info["startTime"] = res.json()["result"]["minStartTime"]
            self.user_info["endTime"] = res.json()["result"]["maxEndTime"]
            # 单个用户结束了，将用户名放回队列
            usernames_queue.put({"username": self.user_info.get("username")})
            assert res.status_code == 200


class StuLoadExamUser(FastHttpUser):
    flas_app_host = os.environ.get('FLASK_APP_HOST')
    host = f"http://{flas_app_host}:8000"
    wait_time = between(0.1, 0.3)
    tasks = [StuLoadExam]
