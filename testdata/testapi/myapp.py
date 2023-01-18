from flask import Flask
from flask import request
from testdata.testapi import res_json

app = Flask(__name__)
username_list = ["teststu1", "teststu2", "teststu3", "teststu4",
                 "teststu5", "teststu6", "teststu7", "teststu8"]


@app.route('/users/login/', methods=['POST'])
def login():
    user = request.get_json()["username"]
    pwd = request.get_json()["password"]
    if user in username_list and pwd == '123456':
        return {"token": "user_token_md5", "id": int(user[-1:])}
    else:
        return {"err_msg": "用户名或密码错误"}


@app.route('/course/list/', methods=['GET'])
def course_list():
    token = request.headers.get("Authorization")
    return res_json.courselist if token == 'user_token_md5' else {"err_msg": "error"}


@app.route('/exams/list/', methods=['GET'])
def exam_list():
    token = request.headers.get("Authorization")
    return res_json.exam_list if token == 'user_token_md5' and request.args.get("ocId") == "117091" else {
        "err_msg": "error"}


@app.route('/exams/info/', methods=['GET'])
def exam_info():
    token = request.headers.get("Authorization")
    return res_json.exam_info if token == 'user_token_md5' and request.args.get("examId") == "89362" else {
        "err_msg": "error"}


if __name__ == '__main__':
    app.run('127.0.0.1', port=8000, debug=True)
