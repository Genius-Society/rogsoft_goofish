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
from huggingface_hub import HfApi
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import ResponseCodeException, Credential, user, sync

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="WeMediaMon configuration script.")

START_MONITOR = 0
TEST_SMTP = 1
UPD_BILI_FANS = 2
UPD_BILI_BLACKS = 3
UPD_HF_FANS = 4

# 添加参数
parser.add_argument("--cmd", type=int)
parser.add_argument("--period", type=int)
parser.add_argument("--email", type=str)
parser.add_argument("--smtp", type=str)
parser.add_argument("--tmp", type=str)
parser.add_argument("--bilick", type=str)
parser.add_argument("--hftag", type=str)
parser.add_argument("--gitag", type=str)
parser.add_argument("--cnblokie", type=str)
parser.add_argument("--itck", type=str)

# 解析命令行参数
args = parser.parse_args()


def upd_log(txt, mode=args.cmd):
    if mode == START_MONITOR:
        with open("/tmp/upload/wemediamon_run_log.txt", "a", encoding="utf-8") as file:
            file.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + f" {txt}\n")
    else:
        print(txt)


def send_email(
    content,
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

        upd_log("邮件发送成功!")

    except smtplib.SMTPException as e:
        if e.smtp_code == -1:
            upd_log("邮件发送成功!")
        else:
            upd_log(f"邮件发送失败: {e}")


class BiliMon:
    def __init__(self):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.tmpdir = args.tmp if args.tmp[-1] != "/" else args.tmp[:-1]
        self.dbfile = f"{self.tmpdir}/bili_followers.json"
        self.blacks = f"{self.tmpdir}/bili_blacklist.txt"
        self._parse_cookie(args.ck)

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

    def _get_fans(self, page):
        try:
            response = requests.get(
                f"https://api.bilibili.com/x/relation/followers?vmid={self.uid}&pn={page}",
                headers={"User-Agent": self.ua, "Cookie": self.ck},
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
                raise PermissionError(
                    f"可能 {self.uid} 需要重新手动扫码登陆, 错误代码: {json_data['code']}"
                )

        except requests.exceptions.RequestException as e:
            upd_log(f"错误: {e}, 重试中...")
            return self._get_fans(page)

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

        upd_log(f"{self.dbfile} 已更新!")

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
        if os.path.exists(self.dbfile):
            with open(self.dbfile, "r", encoding="utf-8") as file:
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
                upd_log(f"暂未发现取关 {self.uid} 者")

            self._upd_json(new_fans, out1000)

        else:
            upd_log(f"暂未发现取关 {self.uid} 者")

    def clean_all_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        for traitor in tqdm(traitors, desc="清理已注销的取关狗"):
            if self._is_deleted(traitor):
                upd_log(f"取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors:
            self._save_traitors(cleaned_traitors)


class HFMon:
    def __init__(self):
        self.hf_api = HfApi()
        self.target: str = args.hftag
        self.hf_domain = "https://huggingface.co"
        self.cache = f"{args.tmp}/hf_followers.json"
        self.tag_users, self.tag_orgs = self._parse_tags()
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
        }

    def _parse_tags(self):
        username = self.target.split("/")[0]
        following_users = [username]
        followings = self.hf_api.list_user_following(username)
        for following in followings:
            following_users.append(following.username)

        following_orgs = []
        response = requests.get(f"{self.hf_domain}/api/users/{username}/following/orgs")
        response.raise_for_status()
        if response.status_code == 200:
            orgs = response.json()
            for org in orgs:
                following_orgs.append(org["name"])
        else:
            raise ConnectionError(response.status_code)

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

    def _get_spaces(self, username: str):
        sleepings, errors = [], []
        spaces = self.hf_api.list_spaces(author=username)
        for space in spaces:
            status = self.hf_api.get_space_runtime(space.id).stage
            if status == "SLEEPING":
                sleepings.append(space.id)
            elif "ERROR" in status:
                errors.append(f"{self.hf_domain}/spaces/{space.id}")

        return sleepings, errors

    def _activate_space(self, space_id: str):
        static = self.hf_api.space_info(space_id).sdk == "static"
        response = requests.get(
            f"https://{space_id.replace('/', '-').replace('_', '-').lower()}.{'static.' if static else ''}hf.space",
            headers=self.header,
        )
        response.raise_for_status()

    def upd_fans(self):
        prev_data, data = {}, {}
        if os.path.exists(self.cache):
            with open(self.cache, "r") as json_file:
                prev_data = json.load(json_file)

        for user in tqdm(self.tag_users, desc="Loading user followers"):
            data[user] = self._get_followers("user", user)

        for org in tqdm(self.tag_orgs, desc="Loading organization followers"):
            data[org] = self._get_followers("organization", org)

        if data == prev_data:
            logs += "\n No data changed. \n"
        else:
            logs += self._compare_data(prev_data, data)
            with open(self.cache, "w") as json_file:
                json.dump(data, json_file, indent=4)

            logs += "\n Data has been updated! \n"

        upd_log(logs)


def update():
    if args.bilick:
        BiliMon().upd_fans()

    if args.hftag:
        HFMon().upd_fans()

    # TODO:


def start_monitor(period=args.period):
    update()
    upd_log(f"监控开启中...每 {period} 小时触发一次")
    schedule.every(period).hours.do(update)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        if args.cmd == START_MONITOR:
            start_monitor()

        elif args.cmd == TEST_SMTP:
            send_email()

        elif args.cmd == UPD_BILI_FANS:
            BiliMon().upd_fans()

        elif args.cmd == UPD_BILI_BLACKS:
            BiliMon().clean_all_traitors()

        elif args.cmd == UPD_HF_FANS:
            HFMon().upd_fans()

    except Exception as e:
        send_email(f"{e}", "[WeMediaMon 插件] 运行错误", "请手动排查")

    upd_log("XU6J03M6")
