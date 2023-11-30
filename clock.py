import time
import schedule
from fans import upd_fans

schedule.every().day.at("21:50").do(upd_fans)

while True:
    schedule.run_pending()
    time.sleep(1)
