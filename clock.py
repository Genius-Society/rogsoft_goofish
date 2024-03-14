import time
import schedule
from fans import upd_fans
from blackfollows import clean_blackfollows
from datetime import datetime


def upd():
    now_hour = datetime.now().hour
    if now_hour > 7 and now_hour < 23:
        clean_blackfollows()
        upd_fans()
    else:
        print("当前处于免打扰时间段")


def monitor(trigger_time="12:50"):
    print(f"监控开启中...每日触发时间：{trigger_time}")
    schedule.every().day.at(trigger_time).do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


def min_monitor(period=2):
    print(f"监控开启中...每{period}分钟触发一次")
    schedule.every(period).minutes.do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


def hour_monitor(period=3):
    print(f"监控开启中...每{period}小时触发一次")
    schedule.every(period).hours.do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    hour_monitor()
