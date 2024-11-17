import os
import math
import time
import json
import random
import smtplib
import requests
import schedule
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

GLOBAL_COOKIE = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def send_email(
    content,
    subject="按罪人名单降下终末",
    title="白嫖完再取关？什么人啊？拉黑了",
):
    # 邮件内容
    body = f"""
    <html>
        <body>
            <h1>{title}</h1><br>
            {content}
        </body>
    </html>
    """

    # 构建邮件
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = "MuGeminorum@foxmail.com"
    msg["To"] = "MuGeminorum@foxmail.com"

    # 发送邮件
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    sender_email = "MuGeminorum@foxmail.com"
    password = "hstpwvmtntitbeee"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, [msg["To"]], msg.as_string())

        print("邮件发送成功")

    except smtplib.SMTPException as e:
        print("邮件发送失败:", str(e))


def parse_cookie(cookie_str: str):
    try:
        myuid = cookie_str.split("DedeUserID=")[1].split(";")[0]
        csrf = cookie_str.split("bili_jct=")[1].split(";")[0]
        cookies = {
            cookie.split("=")[0]: cookie.split("=")[1]
            for cookie in cookie_str.split("; ")
        }
        return myuid, csrf, cookies

    except Exception:
        send_email(
            "请确保cookie.txt存在且内容有效",
            subject="cookie文件缺失或内容无效",
            title=f"cookie解析异常",
        )
        exit()


def refresh_cookie():
    header = {"User-Agent": USER_AGENT, "Cookie": GLOBAL_COOKIE}
    uid, _, _ = parse_cookie(GLOBAL_COOKIE)
    try:
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={uid}",
            headers=header,
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}...")


def get_fans(page):
    header = {"User-Agent": USER_AGENT, "Cookie": GLOBAL_COOKIE}
    uid, _, _ = parse_cookie(GLOBAL_COOKIE)

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={uid}&pn={page}",
            headers=header,
        )
        response.raise_for_status()  # 检查是否成功获取数据

        # 使用 json 库解析 JSON 数据
        json_data = response.json()
        if json_data["code"] == 0:
            fans = {}
            fan_list = json_data["data"]["list"]
            for fan in fan_list:
                fans[str(fan["mid"])] = fan["uname"]

            return (fans, math.ceil(json_data["data"]["total"] / 50))

        else:
            msg = json_data["message"]
            print(msg)
            send_email(
                msg,
                subject="可能需要重新手动扫码登陆",
                title=f"错误代码：{json_data['code']}",
            )
            exit()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}, retrying...")
        return get_fans(page, uid)


def get_folowers():
    fans, pages = get_fans(page=1)
    for i in range(2, pages + 1):
        time.sleep(random.uniform(0.5, 1))
        followers, _ = get_fans(page=i)
        if followers:
            fans.update(followers)

    return fans


def save_traitors(traitors: list, file_path="traitors.txt"):
    with open(file_path, "a", encoding="utf-8") as file:
        for url in traitors:
            file.write(f"{url}\n")


def upd_fans(fans_json="fans.json"):
    old_fans = {}
    if os.path.exists(fans_json):
        with open(fans_json, "r", encoding="utf-8") as file:
            old_fans = json.load(file)

    unfollows = []
    new_fans = get_folowers()
    if not new_fans:
        print("Failed to upd fans.")
        send_email(
            "请手动更新cookies",
            subject="更新粉丝列表失败",
            title="可能是由于cookies失效或无粉丝导致的",
        )
        exit()

    for fan in old_fans.keys():
        if fan not in new_fans:
            unfollows.append({"uid": fan, "uname": old_fans[fan]})

    if new_fans != old_fans:
        with open(fans_json, "w", encoding="utf-8") as file:
            json.dump(new_fans, file, ensure_ascii=False, indent=4)

    if unfollows:
        content = ""
        traitors = []
        for user in unfollows:
            url = f'https://space.bilibili.com/{user["uid"]}'
            content += f'<br><a href="{url}" target="_blank">{user["uname"]}</a><br>'
            traitors.append(user["uid"])

        if content:
            save_traitors(traitors)
            send_email(content)

    else:
        print("No unfollower found.")


def upd():
    now_hour = datetime.now().hour
    if now_hour > 7 and now_hour < 23:
        upd_fans()
    else:
        refresh_cookie()
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


def hour_monitor(period=2):
    print(f"监控开启中...每{period}小时触发一次")
    schedule.every(period).hours.do(upd)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    hour_monitor()
