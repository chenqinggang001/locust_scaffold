from locust import task, between, SequentialTaskSet, FastHttpUser

from common.prometheus_exporter import *
from common.redis_store import redis_store

logger = get_logger('chenqg', file=True)


class StuLoadExam(SequentialTaskSet):

    # 初始化用户信息
    def __init__(self, parent):
        super().__init__(parent)
        self.user_info = None
        self.token = None
        self.ocid = None
        self.orgid = None
        self.classid = None
        self.userid = None

    @task
    def exams_student(self):
        # 在用户信息队列中，获取用户名
        self.user_info = usernames_queue.get()

        username = self.user_info.get("username")
        # 通过用户名，从redis中获取用户信息
        self.token = redis_store.get(f"{username}_token")
        self.ocid = redis_store.get(f"{username}_ocid")
        self.orgid = redis_store.get(f"{username}_orgid")
        self.classid = redis_store.get(f"{username}_classid")
        self.userid = redis_store.get(f"{username}_userid")
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        param = {"ocId": self.ocid, "keyword": "", "pn": "1", "ps": "20", "lang": "zh"}
        with self.client.get("https://api2.xxx.cn/exams/student", headers=headers,
                             params=param, name='获取考试列表: /exams/student') as res:
            self.user_info["examId"] = res.json()["examList"][0]["examId"]
            assert res.status_code == 200

    @task
    def exams_start(self):
        headers = {"Authorization": self.token, "Content-Type": "application/json"}

        param = {"examId": self.user_info.get('examId'), "traceId": self.userid}
        with self.client.get("/exams/getInfo", headers=headers, params=param,
                             name='获取考试基础信息: /exams/getInfo') as res:
            self.user_info["startTime"] = res.json()["result"]["minStartTime"]
            self.user_info["endTime"] = res.json()["result"]["maxEndTime"]
            assert res.status_code == 200

        param = {"examId": self.user_info.get('examId'), "fromWhere": "org", "traceId": self.userid}
        with self.client.get("/exams/user/study/openPaperFromOrg", headers=headers,
                             params=param, name='进入考试须知页面: /exams/user/study/openPaperFromOrg') as res:
            # 单个用户结束了，将用户名放回队列
            usernames_queue.put(self.user_info.get("username"))
            assert res.status_code == 200


class StuLoadExamUser(FastHttpUser):
    host = 'https://api1.xxx.cn'
    wait_time = between(0.1, 0.3)

    tasks = [StuLoadExam]
