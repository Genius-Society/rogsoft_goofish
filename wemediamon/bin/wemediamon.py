import os
import sys
import json
import math
import time
import random
import smtplib
import argparse
import requests
import schedule
from tqdm import tqdm as _tqdm
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import ResponseCodeException, Credential, user, sync


class Tee:
    def __init__(self, log_path: str):
        self.log_file = open(log_path, "a", encoding="utf-8")
        self.console = sys.__stdout__

    def write(self, txt: str):
        msg = txt.replace("\n", " ").strip()
        if msg:
            msg = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + f" {msg}\n"
            self.console.write(msg)
            self.console.flush()
            if not "XU6J03M6" in msg:
                self.log_file.write(msg)
                self.log_file.flush()

    def flush(self):
        self.console.flush()
        self.log_file.flush()

    def isatty(self):
        return True

    def close(self):
        self.log_file.close()


tee = Tee("/tmp/upload/wemediamon_log.txt")
sys.stdout = tee
sys.stderr = tee

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="WeMediaMon config script")
# 添加参数
parser.add_argument("--cmd", type=str, required=True)
parser.add_argument("--period", type=int, default=2, required=True)
parser.add_argument("--email", type=str, required=True)
parser.add_argument("--smtp", type=str, required=True)
parser.add_argument("--cache", type=str, required=True)
parser.add_argument("--bilick", type=str, default="")
parser.add_argument("--hftag", type=str, default="")
parser.add_argument("--gitags", type=str, default="")
parser.add_argument("--cnblokie", type=str, default="")
parser.add_argument("--itck", type=str, default="")

# 解析命令行参数
args = parser.parse_args()
# print(args)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
CACHE_PATH = args.cache if args.cache[-1] != "/" else args.cache[:-1]


def tqdm(*args, **kwargs):  # 强制使用 Unicode 样式
    kwargs.setdefault("ascii", False)
    return _tqdm(*args, **kwargs)


def send_email(
    content="邮件发送成功!",
    subject="[WeMediaMon 插件] 测试邮件",
    title="SMTP有效性检测",
    smtp_server="smtp.qq.com",
    smtp_port=587,
    email=args.email,
    smtp=args.smtp,
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
    msg["From"] = email
    msg["To"] = email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email, smtp)
            server.sendmail(email, [msg["To"]], msg.as_string())

        print("邮件发送成功!")

    except smtplib.SMTPException as e:
        if e.smtp_code == -1:
            print("邮件发送成功!")
        else:
            print(f"邮件发送失败: {e}")


class BiliMon:
    def __init__(self):
        self.dbfile = f"{CACHE_PATH}/bili_followers.json"
        self.blacks = f"{CACHE_PATH}/bili_blacklist.txt"
        self._parse_cookie(args.bilick)

    def _parse_cookie(self, ck: str):
        self.uid = ck.split("DedeUserID=")[1].split(";")[0]
        self.sessdata = ck.split("SESSDATA=")[1].split(";")[0]
        self.bili_jct = ck.split("bili_jct=")[1].split(";")[0]
        self.buvid3 = ck.split("buvid3=")[1].split(";")[0]
        self.ck = ck
        self.credential = Credential(
            sessdata=self.sessdata,
            bili_jct=self.bili_jct,
            buvid3=self.buvid3,
        )

    def _txt2lst(self):
        if not os.path.exists(self.blacks):
            return []

        with open(self.blacks, "r", encoding="utf-8") as file:
            lines = file.readlines()
        # 去掉每行末尾的换行符
        lines = [line.strip() for line in lines]
        return list(set(lines))

    def _save_traitors(self, traitors: list):
        with open(self.blacks, "w", encoding="utf-8") as file:
            for url in traitors:
                file.write(f"{url}\n")

    def _add_traitors(self, traitors: list):
        old_traitors = self._txt2lst()
        merged_traitors = list(set(old_traitors + traitors))
        self._save_traitors(merged_traitors)

    def _get_fans(self, page, trytime=3):
        try:
            response = requests.get(
                f"https://api.bilibili.com/x/relation/followers?vmid={self.uid}&pn={page}",
                headers={
                    "User-Agent": USER_AGENT,
                    "Cookie": self.ck,
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
                print(json_data["message"])
                raise PermissionError(
                    f"可能 {self.uid} 需要重新手动扫码登陆, 错误代码: {json_data['code']}"
                )

        except requests.exceptions.RequestException as e:
            print(f"错误: {e}, 重试中...")
            time.sleep(random.uniform(4.5, 5))
            trytime -= 1
            if trytime > 0:
                return self._get_fans(page, trytime)

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
            user_ins = user.User(uid=int(user_id), credential=self.credential)
            try:
                await user_ins.get_user_info()
                return False

            except ResponseCodeException as e:
                return e.code == -404

        return sync(is_deleted_async(uid))

    def _is_fans(self, uid):
        async def is_fans_async(relation_id):
            user_ins = user.User(uid=self.uid, credential=self.credential)
            relation = await user_ins.get_relation(relation_id)
            followed_status = relation["be_relation"]["attribute"]
            return followed_status == 2 or followed_status == 6  # 2=已关注, 6=互粉

        return sync(is_fans_async(uid))

    def _upd_json(self, new_fans: dict, out1000: dict):
        if os.path.exists(self.dbfile):
            with open(self.dbfile, "r", encoding="utf-8") as file:
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
            self._add_traitors(traitors_out1000)

        with open(self.dbfile, "w", encoding="utf-8") as file:
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

        print(f"{self.dbfile} 已更新!")

    def _filter_unfollows(self, unfollows):
        real_unfollows, out1000 = [], {}
        for unfollower in tqdm(unfollows, desc=f"过滤 {self.uid} 取关列表"):
            if self._is_fans(unfollower["uid"]):
                out1000.update({unfollower["uid"]: unfollower["uname"]})
            else:
                real_unfollows.append(unfollower)

        return real_unfollows, out1000

    def check_login(self):
        response = requests.get(
            "https://api.bilibili.com/x/web-interface/nav",
            headers={
                "cookie": self.ck,
                "user-agent": USER_AGENT,
            },
        )
        response.raise_for_status()
        if response.status_code == 200:
            isLogin = response.json()["data"]["isLogin"]
            print(("已" if isLogin else "未") + "登录B站")

        else:
            raise ConnectionError(response.status_code)

    def upd_fans(self):
        old_fans = []
        if os.path.exists(self.dbfile):
            with open(self.dbfile, "r", encoding="utf-8") as file:
                old_fans = json.load(file)["fans1000"]

        new_fans: dict = self._get_followers()
        while not new_fans:
            print(f"获取 {self.uid} 粉丝列表失败, 重试中...")
            new_fans = self._get_followers()

        if new_fans != old_fans:
            unfollows = []
            for fan in old_fans:
                if fan not in new_fans:
                    unfollows.append({"uid": fan, "uname": old_fans[fan]})

            unfollows, out1000 = self._filter_unfollows(unfollows)
            if unfollows:
                content = f"以下狗取关了 {self.uid}:"
                traitors = []
                for user in unfollows:
                    url = f'https://space.bilibili.com/{user["uid"]}'
                    content += f'<br><a href="{url}">{user["uname"]}</a><br>'
                    traitors.append(user["uid"])

                if content:
                    self._add_traitors(traitors)
                    send_email(content)

            else:
                print(f"暂未发现取关 {self.uid} 者")

            self._upd_json(new_fans, out1000)

        else:
            print(f"暂未发现取关 {self.uid} 者")

    def clean_all_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            print("当前狗库为空!")
            return

        for traitor in tqdm(traitors, desc="清理已注销的取关狗"):
            if self._is_deleted(traitor):
                print(f"取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors:
            self._save_traitors(cleaned_traitors)


class HFMon:
    def __init__(self):
        self.hf_domain = "https://huggingface.co"
        self.header = {"User-Agent": USER_AGENT}
        self.target: str = args.hftag
        self.cache = f"{CACHE_PATH}/hf_followers.json"
        self.tag_users, self.tag_orgs = self._parse_tags()

    def _list_user_following(self, username):
        response = requests.get(
            f"{self.hf_domain}/api/users/{username}/following",
            headers=self.header,
        )
        response.raise_for_status()
        if response.status_code == 200:
            follows = response.json()
            followings = {}
            for follow in follows:
                followings[str(follow["_id"])] = str(follow["user"])

            return followings

        else:
            raise ConnectionError(response.status_code)

    def _list_user_following_orgs(self, username):
        response = requests.get(
            f"{self.hf_domain}/api/users/{username}/following/orgs",
            headers=self.header,
        )
        response.raise_for_status()
        if response.status_code == 200:
            follows = response.json()
            followings = {}
            for follow in follows:
                followings[str(follow["_id"])] = str(follow["name"])

            return followings

        else:
            raise ConnectionError(response.status_code)

    def _parse_tags(self):
        username = self.target
        following_users = [username]
        followings = self._list_user_following(username)
        for _id in followings:
            following_users.append(followings[_id])

        following_orgs = []
        followings = self._list_user_following_orgs(username)
        for _id in followings:
            following_orgs.append(followings[_id])

        return following_users, following_orgs

    def _get_followers(self, tag_type: str, tag: str):
        response = requests.get(f"{self.hf_domain}/api/{tag_type}s/{tag}/followers")
        response.raise_for_status()
        if response.status_code == 200:
            fans = response.json()
            followers = {}
            for follower in fans:
                followers[str(follower["_id"])] = str(follower["user"])

            return followers

        else:
            raise ConnectionError(response.status_code)

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        for tag in prev_data:
            if tag in data:
                diff = set(prev_data[tag].keys()) - set(data[tag].keys())
                if diff:
                    for id in diff:
                        dog = prev_data[tag][id]
                        me = tag.split("/")[-1]
                        logs += f"\n Dog <a href='{self.hf_domain}/{dog}'>{dog}</a> unfollowed <a href='{self.hf_domain}/{me}'>{me}</a> ! \n"

        if logs:
            send_email(logs)

        return logs

    def upd_fans(self):
        prev_data, data = {}, {}
        if os.path.exists(self.cache):
            with open(self.cache, "r") as json_file:
                prev_data = json.load(json_file)

        for user in tqdm(self.tag_users, desc="Loading user followers"):
            data[user] = self._get_followers("user", user)

        for org in tqdm(self.tag_orgs, desc="Loading organization followers"):
            data[org] = self._get_followers("organization", org)

        logs = ""
        if data == prev_data:
            logs += "\n No data changed. \n"
        else:
            logs += self._compare_data(prev_data, data)
            with open(self.cache, "w") as json_file:
                json.dump(data, json_file, indent=4)

            logs += "\n Data has been updated! \n"

        print(logs)


class GitHubMon:
    def __init__(self):
        self.tags = args.gitags.split(";")
        self.cache = f"{CACHE_PATH}/github_followers.json"

    def _get_followers(self, user: str):
        response = requests.get(f"https://api.github.com/users/{user}/followers")
        response.raise_for_status()
        if response.status_code == 200:
            fans = response.json()
            followers = {}
            for follower in fans:
                followers[str(follower["id"])] = str(follower["login"])

            return followers

        else:
            raise ConnectionError(response.status_code)

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        for tag in prev_data:
            if tag in data:
                diff = set(prev_data[tag].keys()) - set(data[tag].keys())
                if diff:
                    for id in diff:
                        dog = prev_data[tag][id]
                        me = tag.split("/")[-1]
                        logs += f"\n Dog <a href='https://github.com/{dog}'>{dog}</a> unfollowed <a href='https://github.com/{me}'>{me}</a> ! \n"

        if logs:
            send_email(logs)

        return logs

    def upd_fans(self):
        prev_data, data = {}, {}
        if os.path.exists(self.cache):
            with open(self.cache, "r") as json_file:
                prev_data = json.load(json_file)

        for tag in tqdm(self.tags, desc="Getting current followers"):
            data[tag] = self._get_followers(tag)

        if data == prev_data:
            logs += "\n No data changed. \n"
        else:
            logs += self._compare_data(prev_data, data)
            with open(self.cache, "w") as json_file:
                json.dump(data, json_file, indent=4)

            logs += "\n Data has been updated! \n"

        print(logs)


class CnblogsMon:
    def __init__(self):  # TODO:
        return

    def check_login(self):
        print("Check cnblogs login...")

    def upd_fans(self):
        print("Update cnblogs followers...")


class ItchMon:
    def __init__(self):  # TODO:
        return

    def check_login(self):
        print("Check itch.io login...")

    def upd_fans(self):
        print("Update itch.io followers...")


def update():
    if args.bilick:
        BiliMon().upd_fans()

    if args.hftag:
        HFMon().upd_fans()

    if args.gitags:
        GitHubMon().upd_fans()

    if args.cnblokie:
        CnblogsMon().upd_fans()

    if args.itck:
        ItchMon().upd_fans()


def start_monitor(period=args.period):
    update()
    print(f"监控开启中...每 {period} 小时触发一次")
    schedule.every(period).hours.do(update)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        match args.cmd:
            case "START_MONITOR":
                start_monitor()

            case "TEST_SMTP":
                send_email()

            case "TEST_BILI_CK":
                BiliMon().check_login()

            case "UPD_BILI_FANS":
                BiliMon().upd_fans()

            case "UPD_BILI_BLACKS":
                BiliMon().clean_all_traitors()

            case "UPD_HF_FANS":
                HFMon().upd_fans()

            case "UPD_GIT_FANS":
                GitHubMon().upd_fans()

            case "TEST_CNBLOGS_CK":
                CnblogsMon().check_login()

            case "UPD_CNBLOGS_FANS":
                CnblogsMon().upd_fans()

            case "TEST_ITCH_CK":
                ItchMon().check_login()

            case "UPD_ITCH_FANS":
                ItchMon().upd_fans()

            case _:
                print(f"未知指令: {args.cmd}")

    except Exception as e:
        send_email(f"{e}", "[WeMediaMon 插件] 运行错误", "请手动排查")
