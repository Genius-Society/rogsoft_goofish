import time
import schedule
from fans import upd_fans
from blackfollows import clean_blackfollows


def upd():
    clean_blackfollows()
    upd_fans()


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


def hour_monitor(min="30"):
    print(f"监控开启中...每整点{min}分触发一次")
    schedule.every().hour.at(f":{min}").do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    monitor()
