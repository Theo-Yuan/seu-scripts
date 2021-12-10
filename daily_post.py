from typing import Tuple
import time
from argparse import ArgumentParser

from apscheduler.schedulers.blocking import BlockingScheduler

from health_post import do_report
from utils.login import login
from utils.email import send_email
import config


def login_report(user_config: Tuple):
    ss = login(user_config[0], user_config[1])
    if ss:
        return do_report(ss)


def do_job(try_num: int):
    print(
        f'start...Local Time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}'
        .center(50, '-'))
    for user_config in config.user_list:
        print(user_config)
        count = 0
        while count < try_num and not login_report(user_config):
            count += 1

        if count < try_num:
            send_email(**config.sender_cfg,
                       receivers=[user_config[2]],
                       messageText='Daily post Succeed!')
        else:
            send_email(**config.sender_cfg,
                       receivers=[user_config[2]],
                       messageText='Daily post Failed...qwq')

    print('end')


def daily_do_jobs(try_num: int):
    scheduler = BlockingScheduler()
    scheduler.add_job(do_job, 'cron', hour=config.daily_time[0], minute=config.daily_time[1], args=[try_num])
    scheduler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--once', '-o', action='store_true')
    parser.add_argument('--try_num', '-t', default=3, type=int)

    args = parser.parse_args()
    print('Only do once' if args.once else 'Do it every day')
    if args.once:
        do_job(args.try_num)
    else:
        daily_do_jobs(args.try_num)
