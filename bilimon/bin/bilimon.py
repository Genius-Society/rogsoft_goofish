import os
import math
import time
import json
import random
import smtplib
import argparse
import requests
import schedule
from tqdm import tqdm
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import ResponseCodeException, Credential, user, sync

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="BiliMon configuration script.")

# 添加参数
parser.add_argument("--clock", type=int, help="1=monitor on, 0=trigger once")
parser.add_argument("--period", type=int, help="Specify the period for BiliMon.")
parser.add_argument("--email", type=str, help="Specify the email address for BiliMon.")
parser.add_argument("--smtp", type=str, help="Specify the SMTP server for BiliMon.")
parser.add_argument("--tmp", type=str, help="Specify the temporary folder for BiliMon.")
parser.add_argument("--cookie", type=str, help="Specify the cookie for BiliMon.")
parser.add_argument("--ck2", type=str, help="Specify the second cookie for BiliMon.")

# 解析命令行参数
args = parser.parse_args()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TMP_DIR = args.tmp if args.tmp[-1] != "/" else args.tmp[:-1]
SCRIPT_DIR = "/koolshare/bilimon"


def upd_log(txt):
    if int(args.clock) == 1:
        with open("/tmp/upload/bilimon_run_log.txt", "a", encoding="utf-8") as file:
            file.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + f" {txt}\n")
    else:
        print(txt)


def send_email(
    content,
    subject="按罪人名单降下终末",
    title="监测到取关狗",
    smtp_server="smtp.qq.com",
    smtp_port=587,
    sender_email=args.email,
    password=args.smtp,
):
    # 邮件内容
    body = f"""
    <html>
        <body>
            <h1>{title}</h1><br>
            [BiliMon 插件] {content}
        </body>
    </html>
    """

    # 构建邮件
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = args.email
    msg["To"] = args.email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, [msg["To"]], msg.as_string())

        upd_log("邮件发送成功!")

    except smtplib.SMTPException as e:
        if e.smtp_code == -1:
            upd_log("邮件发送成功!")
        else:
            upd_log(f"邮件发送失败: {e}")


def parse_cookie(cookies: str):
    uid = sessdata = bili_jct = buvid3 = ""
    try:
        uid = cookies.split("DedeUserID=")[1].split(";")[0]
        sessdata = cookies.split("SESSDATA=")[1].split(";")[0]
        bili_jct = cookies.split("bili_jct=")[1].split(";")[0]
        buvid3 = cookies.split("buvid3=")[1].split(";")[0]
        return uid, sessdata, bili_jct, buvid3

    except Exception as e:
        return uid, f"{e}", bili_jct, buvid3


def txt2lst(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        # 去掉每行末尾的换行符
        lines = [line.strip() for line in lines]
        return list(set(lines))

    except Exception as e:
        send_email(
            f"读取文件时出错: {e}",
            subject=f"{file_path} 内容缺失或内容无效",
            title="txt 解析异常",
        )
        upd_log("XU6J03M6")
        exit()


def save_traitors(traitors: list, file_folder=TMP_DIR):
    with open(f"{file_folder}/traitors.txt", "w", encoding="utf-8") as file:
        for url in traitors:
            file.write(f"{url}\n")


def add_traitors(traitors: list, file_folder=TMP_DIR):
    old_traitors = txt2lst(f"{file_folder}/traitors.txt")
    merged_traitors = list(set(old_traitors + traitors))
    save_traitors(merged_traitors, file_folder)


class BiliUser:
    def __init__(self, cookie: str, dbfile=f"{SCRIPT_DIR}/fans.json"):
        self.cookie = cookie
        self.dbfile = dbfile
        self.uid, self.sessdata, self.bili_jct, self.buvid3 = parse_cookie(self.cookie)
        if not (self.uid and self.sessdata and self.bili_jct and self.buvid3):
            send_email(
                f"请确保 {self.uid} cookie 存在且内容有效: {self.sessdata}",
                subject="cookie 内容缺失或内容无效",
                title="cookie 解析异常",
            )
            upd_log("XU6J03M6")
            exit()

    def _get_fans(self, page):
        try:
            response = requests.get(
                f"https://api.bilibili.com/x/relation/followers?vmid={self.uid}&pn={page}",
                headers={"User-Agent": USER_AGENT, "Cookie": self.cookie},
            )  # 使用 requests 库下载 JSON 数据
            response.raise_for_status()  # 检查是否成功获取数据
            json_data = response.json()  # 使用 json 库解析 JSON 数据
            if json_data["code"] == 0:
                fans = {}
                fan_list = json_data["data"]["list"]
                for fan in fan_list:
                    fans[str(fan["mid"])] = fan["uname"]

                return (fans, math.ceil(json_data["data"]["total"] / 50))

            else:
                msg = json_data["message"]
                upd_log(msg)
                send_email(
                    msg,
                    subject=f"可能 {self.uid} 需要重新手动扫码登陆",
                    title=f"错误代码: {json_data['code']}",
                )
                upd_log("XU6J03M6")
                exit()

        except requests.exceptions.RequestException as e:
            upd_log(f"错误: {e}, 重试中...")
            return self._get_fans(page, self.uid)

    def _get_followers(self):
        fans, pages = self._get_fans(page=1)
        for i in tqdm(range(2, pages + 1), desc=f"扫描 {self.uid} 粉丝中"):
            time.sleep(random.uniform(0.5, 1))
            followers, _ = self._get_fans(page=i)
            if followers:
                fans.update(followers)

        return fans

    def _is_deleted(self, uid):
        async def is_deleted_async(user_id):
            c = Credential(
                sessdata=self.sessdata,
                bili_jct=self.bili_jct,
                buvid3=self.buvid3,
            )
            user_ins = user.User(uid=int(user_id), credential=c)
            try:
                await user_ins.get_user_info()
                return False

            except ResponseCodeException as e:
                return e.code == -404

        return sync(is_deleted_async(uid))

    def _is_fans(self, uid):
        async def is_fans_async(relation_id):
            c = Credential(
                sessdata=self.sessdata,
                bili_jct=self.bili_jct,
                buvid3=self.buvid3,
            )
            user_ins = user.User(uid=self.uid, credential=c)
            relation = await user_ins.get_relation(relation_id)
            followed_status = relation["be_relation"]["attribute"]
            return followed_status == 2 or followed_status == 6  # 2=已关注, 6=互粉

        return sync(is_fans_async(uid))

    def clean_traitors(self, file_folder=TMP_DIR):
        cleaned_traitors = []
        traitors = txt2lst(f"{file_folder}/traitors.txt")
        for traitor in tqdm(traitors, desc="清理已注销的取关狗"):
            if self._is_deleted(traitor):
                print(f"取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors:
            save_traitors(cleaned_traitors, file_folder)

    def _upd_json(self, new_fans: dict, out1000: dict):
        fans_json = self.dbfile
        if os.path.exists(fans_json):
            with open(fans_json, "r", encoding="utf-8") as file:
                out1000.update(json.load(file)["out1000"])

        traitors_out1000 = []
        out1000_keys = list(out1000.keys())
        for item in tqdm(out1000_keys, desc=f"过滤 {self.uid} 的1K以外列表"):
            if item in new_fans:
                del out1000[item]

            elif not self._is_fans(item):
                traitors_out1000.append(item)
                del out1000[item]

        if traitors_out1000:
            add_traitors(traitors_out1000)

        with open(fans_json, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "total": len(new_fans) + len(out1000),
                    "fans1000": new_fans,
                    "out1000": out1000,
                },
                file,
                ensure_ascii=False,
                indent=4,
            )

        upd_log(f"{fans_json} 已更新!")

    def _filter_unfollows(self, unfollows):
        real_unfollows, out1000 = [], {}
        for unfollower in tqdm(unfollows, desc=f"过滤 {self.uid} 取关列表"):
            if self._is_fans(unfollower["uid"]):
                out1000.update({unfollower["uid"]: unfollower["uname"]})
            else:
                real_unfollows.append(unfollower)

        return real_unfollows, out1000

    def upd_fans(self):
        old_fans = []
        fans_json = self.dbfile
        if os.path.exists(fans_json):
            with open(fans_json, "r", encoding="utf-8") as file:
                old_fans = json.load(file)["fans1000"]

        new_fans: dict = self._get_followers()
        while not new_fans:
            upd_log(f"获取 {self.uid} 粉丝列表失败, 重试中...")
            new_fans = self._get_followers()

        if new_fans != old_fans:
            unfollows = []
            for fan in old_fans:
                if fan not in new_fans:
                    unfollows.append({"uid": fan, "uname": old_fans[fan]})

            unfollows, out1000 = self._filter_unfollows(unfollows)
            if unfollows:
                content = ""
                traitors = []
                for user in unfollows:
                    url = f'https://space.bilibili.com/{user["uid"]}'
                    content += f'<br><a href="{url}">{user["uname"]}</a><br>'
                    traitors.append(user["uid"])

                if content:
                    add_traitors(traitors)
                    send_email(content)

            else:
                upd_log(f"暂未发现取关 {self.uid} 者")

            self._upd_json(new_fans, out1000)

        else:
            upd_log(f"暂未发现取关 {self.uid} 者")


def upd_all_fans():
    BiliUser(cookie=args.cookie).upd_fans()
    cookie2 = str(args.ck2).strip()
    if cookie2:
        BiliUser(cookie=cookie2, dbfile=f"{SCRIPT_DIR}/fans2.json").upd_fans()


def clean_all_traitors():
    BiliUser(cookie=args.cookie).clean_traitors()


def upd():
    now_hour = datetime.now().hour
    if now_hour > 7 and now_hour < 23:
        upd_all_fans()
    else:
        clean_all_traitors()
        upd_log("当前处于免打扰时间段")


def hour_monitor(period=2):
    upd()
    upd_log(f"监控开启中...每 {period} 小时触发一次")
    schedule.every(period).hours.do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


def main(retry=True):
    try:
        if int(args.clock) == 1:
            hour_monitor(period=args.period)
        elif int(args.clock) == 0:
            upd_all_fans()
        elif int(args.clock) == 2:
            clean_all_traitors()

        upd_log("XU6J03M6")

    except Exception as e:
        if retry:
            main(False)
        else:
            send_email(
                f"运行错误: {e}",
                subject="BiliMon 插件运行错误",
                title="请手动重启插件",
            )


if __name__ == "__main__":
    main()
