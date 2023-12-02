import time
import schedule
from fans import upd_fans


def monitor(trigger_time="12:50"):
    print(f'监控开启中...每日触发时间：{trigger_time}')
    schedule.every().day.at(trigger_time).do(upd_fans)
    while True:
        schedule.run_pending()
        time.sleep(1)


def cyc_monitor(period=1):
    print(f'监控开启中...每{period}小时触发一次')
    schedule.every(period).hours.do(upd_fans)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    cyc_monitor()
