import sys
import json
import time
import threading
import copy

from utils.login import login
import config


def fetch_lecture(hd_wid: str, ss):
    url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/yySave.do"
    data_json = {'HD_WID': hd_wid}
    form = {"paramJson": json.dumps(data_json)}
    r = ss.post(url, data=form)
    result = r.json()
    if result['success'] is not False:
        print(result)
        sys.exit(0)
    return result['code'], result['msg'], result['success']


def multi_threads(ss, threads_id, hd_wid: str):
    i = 1
    while True:
        code, msg, success = fetch_lecture(hd_wid, ss)
        print('线程{},第{}次请求,code：{},msg：{},success:{}'.format(
            threads_id, i, code, msg, success))
        if success is True or msg == '当前活动预约人数已满，请重新选择！' or msg == '已经预约过该活动，无需重新预约！':
            sys.exit(0)
        i += 1
        time.sleep(config.interval)


def get_lecture_list(ss):
    url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do#/hdyy"
    ss.get(url)
    url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/modules/hdyy/hdxxxs.do"
    form = {"pageSize": 12, "pageNumber": 1}
    r = ss.post(url, data=form)
    response = r.json()
    rows = response['datas']['hdxxxs']['rows']
    return rows


def get_lecture_info(w_id, ss):
    url = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/modules/hdyy/hdxxxq_cx.do"
    data_json = {'WID': w_id}
    r = ss.post(url, data=data_json)
    try:
        result = r.json()['datas']['hdxxxq_cx']['rows'][0]
        return result
    except Exception:
        print("讲座信息获取失败")
        return False


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print("请输入一卡通号:")
    card_num = config.card_num
    print(card_num)
    print("请输入密码:")
    password = config.password
    print('*'*len(password))
    print("开始登陆")
    s = login(card_num, password)
    lecture_list = get_lecture_list(s)
    for lecture in lecture_list:
        print("讲座wid：", end=" ")
        print(lecture['WID'], end="  |")
        print("讲座名称：", end=" ")
        print(lecture['JZMC'], end="  |")
        print("预约开始时间：", end=" ")
        print(lecture['YYKSSJ'], end="  |")
        print("预约结束时间：", end=" ")
        print(lecture['YYJSSJ'], end="  |")
        print("活动时间：")
        print(lecture['JZSJ'])
    print("----------------讲座列表end----------------")
    lecture_info = False
    while not lecture_info:
        print("请输入讲座wid")
        wid = input()
        lecture_info = get_lecture_info(wid, s)

    print("请输入提前几秒开始抢（请保证本地时间准确）：")
    advance_time = int(input())
    current_time = int(time.time())
    begin_time = int(time.mktime(time.strptime(
        lecture_info['YYKSSJ'], "%Y-%m-%d %H:%M:%S")))
    end_time = int(time.mktime(time.strptime(
        lecture_info['YYJSSJ'], "%Y-%m-%d %H:%M:%S")))
    if current_time > end_time:
        print("抢课时间已结束，大侠请重新来过")
        sys.exit(0)
    while current_time < begin_time - advance_time:
        current_time = int(time.time())
        print('等待{}秒'.format(begin_time - advance_time - current_time))
        time.sleep(1)
    print('开始抢课')
    thread_list = list()
    for _ in range(config.thread_num):
        thread_list.append(threading.Thread(target=multi_threads,
                                            args=(copy.deepcopy(s), 't1', wid)))
    start_interval = config.interval / config.thread_num
    for thread in thread_list:
        thread.start()
        time.sleep(start_interval)
