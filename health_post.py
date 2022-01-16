# encoding=utf-8
import argparse
import datetime
import random
import json
import pytz

from bs4 import BeautifulSoup
from utils.login import login
import config


def load_params(ss):
    '''合并填报参数'''
    json_form = get_report_data(ss)  # 获取昨日填报信息

    params = {
        'DZ_JSDTCJTW': f'{36+random.random():.1f}',
        'DZ_DBRQ': '%Y-%m-%d',
        'CZRQ': '%Y-%m-%d %H:%M:%S',
        'CREATED_AT': '%Y-%m-%d %H:%M:%S',
        'NEED_CHECKIN_DATE': '%Y-%m-%d'
    }

    print('【使用昨日信息进行填报】')

    # get time
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    today_list = ['CZRQ', 'CREATED_AT', 'NEED_CHECKIN_DATE']
    yesterday_list = ['DZ_DBRQ']
    for key in params.keys():
        # 填充日期
        if key in yesterday_list:
            params[key] = yesterday.strftime(params[key])
        elif key in today_list:
            params[key] = today.strftime(params[key])
        json_form[key] = params[key]
    # print(params)
    return json_form


def do_report(session):
    '''
    session: 已登录的 requests.session 对象
    mode:  填报配置 home, school 等，(留空使用昨天的填报信息)，可自行修改 config.json 文件
    '''
    # 进入填报页面（获取sessionid）
    session.get('http://ehall.seu.edu.cn/appShow?appId=5821102911870447')

    url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/mobile/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'

    json_form = load_params(session)

    res = session.post(url, data=json_form)
    try:
        if json.loads(res.text)['datas']['T_REPORT_EPIDEMIC_CHECKIN_SAVE'] == 1:
            print('填报成功！')
            return True
        else:
            print('填报失败！')
            return False
    except Exception:
        soup = BeautifulSoup(res.text, 'html.parser')
        tag = soup.select('.underscore.bh-mt-16')
        if len(tag) > 1:
            print(tag[0].text.replace('\n', ''))
        else:
            print(res.text)
        print('填报失败！')
        return False


# 获取昨日填报信息
def get_report_data(ss):
    # 进入填报页面（获取sessionid）
    ss.get('http://ehall.seu.edu.cn/appShow?appId=5821102911870447')
    latest_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/getLatestDailyReportData.do'
    wid_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/mobile/dailyReport/getMyTodayReportWid.do'
    # userinfo_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/api/base/getUserDetailDB.do'
    last_res = ss.get(latest_url)
    wid_res = ss.get(wid_url)
    # userinfo_res = ss.post(userinfo_url)
    try:
        tempFormData = {}
        # userInfo = json.loads(userinfo_res.text)['data']
        # 载入当天填报模板
        try:
            wid_data = json.loads(
                wid_res.text)['datas']['getMyTodayReportWid']['rows'][0]
            tempFormData.update(wid_data)
        except Exception:
            print('【getMyTodayReportWid FAILED】')
            # raise       # 经测试：wid为空无影响

        # 载入昨日填报信息
        try:
            last_report = json.loads(
                last_res.text)['datas']['getLatestDailyReportData']['rows'][0]
            tempFormData.update(last_report)
        except Exception:
            print('getLatestDailyReportData FAILED】')
            raise

        # 载入用户信息
        # tempFormData['USER_ID'] = config.card_num
        # tempFormData['PHONE_NUMBER'] = userInfo['PHONE_NUMBER']
        # tempFormData['IDCARD_NO'] = userInfo['IDENTITY_CREDENTIALS_NO']
        # tempFormData['GENDER_CODE'] = userInfo['GENDER_CODE']

        # tempFormData['CLASS_CODE'] = userInfo['CLASS_CODE']
        # tempFormData['CLASS'] = userInfo['CLASS']
        # tempFormData['RYSFLB'] = userInfo['RYSFLB']
        # tempFormData['USER_NAME'] = userInfo['USER_NAME']
        # tempFormData['DEPT_CODE'] = userInfo['DEPT_CODE']  # 学院编号
        # tempFormData['DEPT_NAME'] = userInfo['DEPT_NAME']
    except Exception as e:
        print(e)
        print('【获取填报信息失败，请手动填报】')
        exit()
    return tempFormData


def parse_args():
    parser = argparse.ArgumentParser(description='Test for argparse')
    parser.add_argument(
        '--force', '-f', help='15:00 后是否仍然填报', action='store_true')
    # parser.add_argument(
    #     '--debug', '-d', help='显示调试信息', action='store_true')

    args = parser.parse_args()
    args.card_num = config.card_num
    args.password = config.password
    return args


def main():
    args = parse_args()

    today = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    print(today)
    if today.hour >= 15:  # 超过填报时间
        if args.force:
            print('【超过填报时间，但继续填报】')
        else:
            print('【超过填报时间！放弃填报】')
            exit()
    ss = login(args.card_num, args.password)
    if ss:
        do_report(ss)


if __name__ == '__main__':
    main()
