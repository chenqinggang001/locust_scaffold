#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8
import os
import queue

import requests
import six
from datetime import datetime
from itertools import chain

from flask import request, Response
from locust import stats as locust_stats, runners as locust_runners
from locust import events
from locust.argument_parser import LocustArgumentParser
from locust.runners import MasterRunner, WorkerRunner
from prometheus_client import Metric, REGISTRY, exposition

from common.file_tools import read_text_line
from common.logger_handler import get_logger
from common.mypath import reports_path

usernames = []
usernames_queue = queue.Queue()

logger = get_logger('chenqg', file=True)


class LocustCollector(object):
    registry = REGISTRY

    def __init__(self, environment, runner):
        self.environment = environment
        self.runner = runner

    def collect(self):
        # collect metrics only when locust runner is spawning or running.
        runner = self.runner

        if runner and runner.state in (locust_runners.STATE_SPAWNING, locust_runners.STATE_RUNNING):
            stats = []
            for s in chain(locust_stats.sort_stats(runner.stats.entries), [runner.stats.total]):
                stats.append({
                    "method": s.method,
                    "name": s.name,
                    "num_requests": s.num_requests,
                    "num_failures": s.num_failures,
                    "avg_response_time": s.avg_response_time,
                    "min_response_time": s.min_response_time or 0,
                    "max_response_time": s.max_response_time,
                    "current_rps": s.current_rps,
                    "median_response_time": s.median_response_time,
                    "ninetieth_response_time": s.get_response_time_percentile(0.9),
                    # only total stats can use current_response_time, so sad.
                    # "current_response_time_percentile_95": s.get_current_response_time_percentile(0.95),
                    "avg_content_length": s.avg_content_length,
                    "current_fail_per_sec": s.current_fail_per_sec
                })

            # perhaps StatsError.parse_error in e.to_dict only works in python slave, take notices!
            errors = [e.to_dict() for e in six.itervalues(runner.stats.errors)]

            metric = Metric('locust_user_count', 'Swarmed users', 'gauge')
            metric.add_sample('locust_user_count', value=runner.user_count, labels={})
            yield metric

            metric = Metric('locust_errors', 'Locust requests errors', 'gauge')
            for err in errors:
                metric.add_sample('locust_errors', value=err['occurrences'],
                                  labels={'path': err['name'], 'method': err['method'],
                                          'error': err['error']})
            yield metric

            is_distributed = isinstance(runner, locust_runners.MasterRunner)
            if is_distributed:
                metric = Metric('locust_slave_count', 'Locust number of slaves', 'gauge')
                metric.add_sample('locust_slave_count', value=len(runner.clients.values()), labels={})
                yield metric

            metric = Metric('locust_fail_ratio', 'Locust failure ratio', 'gauge')
            metric.add_sample('locust_fail_ratio', value=runner.stats.total.fail_ratio, labels={})
            yield metric

            metric = Metric('locust_state', 'State of the locust swarm', 'gauge')
            metric.add_sample('locust_state', value=1, labels={'state': runner.state})
            yield metric

            stats_metrics = ['avg_content_length', 'avg_response_time', 'current_rps', 'current_fail_per_sec',
                             'max_response_time', 'ninetieth_response_time', 'median_response_time',
                             'min_response_time',
                             'num_failures', 'num_requests']

            for mtr in stats_metrics:
                mtype = 'gauge'
                if mtr in ['num_requests', 'num_failures']:
                    mtype = 'counter'
                metric = Metric('locust_stats_' + mtr, 'Locust stats ' + mtr, mtype)
                for stat in stats:
                    # Aggregated stat's method label is None, so name it as Aggregated
                    # locust has changed name Total to Aggregated since 0.12.1
                    if 'Aggregated' != stat['name']:
                        metric.add_sample('locust_stats_' + mtr, value=stat[mtr],
                                          labels={'path': stat['name'], 'method': stat['method']})
                    else:
                        metric.add_sample('locust_stats_' + mtr, value=stat[mtr],
                                          labels={'path': stat['name'], 'method': 'Aggregated'})
                yield metric


# prometheus????????????
@events.init.add_listener
def locust_init(environment, runner, **kwargs):
    print("locust init event received")
    if environment.web_ui and runner:
        @environment.web_ui.app.route("/export/prometheus")
        def prometheus_exporter():
            registry = REGISTRY
            encoder, content_type = exposition.choose_encoder(request.headers.get('Accept'))
            if 'name[]' in request.args:
                registry = REGISTRY.restricted_registry(request.args.get('name[]'))
            body = encoder(registry)
            return Response(body, content_type=content_type)

        REGISTRY.register(LocustCollector(environment, runner))


# ????????????????????????
@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        download_url = 'http://localhost:8089/stats/report?download=1'

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        res = requests.get(url=download_url, headers=headers, stream=False)
        now_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        filename = f"time_{now_time}_usercount_{environment.runner.target_user_count}.html"
        file_path = os.path.join(reports_path, filename)
        with open(file_path, 'wb') as f:
            f.write(res.content)


# ????????????
# @events.init_command_line_parser.add_listener
# def _(parser):
#     parser.add_argument("--duration-time", include_in_web_ui=True, type=int, env_var="LOCUST_DURATION_TIME",
#                         default=300, help="????????????")
#
#
# # ????????????
# @events.init_command_line_parser.add_listener
# def _(parser):
#     parser.add_argument("--users-count", include_in_web_ui=True, type=int, env_var="LOCUST_USERS_COUNT", default=100,
#                         help="????????????")
#
#
# # ???????????????
# @events.init_command_line_parser.add_listener
# def _(parser):
#     parser.add_argument("--spawn-rate-count", include_in_web_ui=True, type=int, env_var="LOCUST_SPAWN_RATE_COUNT",
#                         default=1, help="?????????????????????")


# ??????????????????
@events.init_command_line_parser.add_listener
def _(parser: LocustArgumentParser):
    parser.add_argument("--study-time", include_in_web_ui=True, type=int, env_var="LOCUST_STUDY_TIME", default=600,
                        help="????????????")


@events.init_command_line_parser.add_listener
def _(parser: LocustArgumentParser):
    parser.add_argument("--switch-page-ratio", include_in_web_ui=True, type=int, env_var="LOCUST_SWITCH_PAGE_RATIO",
                        default=10,
                        help="????????????????????????")


# ??????????????????
@events.test_start.add_listener
def _(environment, **kw):
    if not isinstance(environment.runner, WorkerRunner):
        print(
            # f"????????????: {environment.parsed_options.duration_time} | "
            # f"????????????: {environment.parsed_options.users_count} | "
            # f"????????????: {environment.parsed_options.spawn_rate_count} | "
            f"????????????: {environment.parsed_options.study_time}")


# ????????????
@events.test_start.add_listener
def on_locust_init_queue(environment, **kwargs):
    if not isinstance(environment.runner, WorkerRunner):
        worker_user = int(environment.runner.target_user_count / environment.runner.worker_count)
        print(
            f'users_count: {environment.runner.target_user_count}, '
            f'concurrence_user: {worker_user}, '
            f'worker_count: {environment.runner.worker_count}')
        environment.out_queue = queue.Queue(worker_user)
        environment.my_queue = queue.Queue(worker_user)
        for i in range(worker_user):
            environment.my_queue.put(i)

    # ????????????????????????????????????????????????????????????
    # class CustomShape(LoadTestShape):
    #
    #     def stages_details(self):
    #         stages = [
    #             {"duration": self.runner.environment.parsed_options.duration_time,
    #              "users": self.runner.environment.parsed_options.users_count,
    #              "spawn_rate": self.runner.environment.parsed_options.spawn_rate_count},
    #         ]
    #         return stages

    # def tick(self):
    #     # sourcery skip: inline-immediately-returned-variable, use-next
    #     run_time = self.get_run_time()
    #
    #     for stage in self.stages_details():
    #         if run_time < stage["duration"]:
    #             tick_data = (stage["users"], stage["spawn_rate"])
    #             return tick_data
    #
    #     return None


def setup_test_users(environment, msg, **kwargs):
    """ WorkerRunner ?????????????????????, ??? on_locust_init ????????? """
    # ???????????????????????????, ??????????????????
    usernames.extend(map(lambda u: u["name"], msg.data))
    for i in usernames:
        usernames_queue.put({"username": i})


def setup_worker_info(environment, msg, **kwargs):
    # ??????worker??????
    environment.runner.send_message("acknowledge_users", f"worker info: {msg.data}")


def on_acknowledge(environment, msg, **kwargs):
    """ MasterRunner ?????????????????????, ??? on_locust_init ????????? """
    # ??????worker??????
    print(msg.data)


@events.init.add_listener
def on_locust_init_testdata(environment, **_kwargs):
    if not isinstance(environment.runner, MasterRunner):
        # ?????????locust?????????test_users????????????????????????test_users????????????????????????????????????setup_test_users??????
        environment.runner.register_message("test_users", setup_test_users)
        environment.runner.register_message("worker_info", setup_worker_info)
    if not isinstance(environment.runner, WorkerRunner):
        environment.runner.register_message("acknowledge_users", on_acknowledge)


@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    if isinstance(environment.runner, WorkerRunner):
        return
    # ????????????????????????????????????
    res = read_text_line("appuser", "app_users")
    users = [{"name": res[i]} for i in range(len(res))]
    worker_count = environment.runner.worker_count
    # ??????worker??????????????????worker?????????????????????
    chunk_size = int(len(users) / worker_count)

    # environment.runner.clients ???????????????????????????????????????worker???ID
    for i, worker in enumerate(environment.runner.clients):
        # ????????????????????????????????????
        start_index = i * chunk_size

        end_index = start_index + chunk_size if i + 1 < worker_count else len(users)
        # ??????????????????????????????????????????????????????
        data = users[start_index:end_index]
        # ???????????????test_users???????????????worker
        index_info = {"worker": worker, "????????????": len(data), "start": start_index, "end": end_index}
        environment.runner.send_message("test_users", data, worker)
        environment.runner.send_message("worker_info", index_info, worker)
