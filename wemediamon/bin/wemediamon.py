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
import subprocess
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import (
    ResponseCodeException,
    Credential,
    favorite_list,
    video,
    user,
    sync,
)

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="WeMediaMon 配置脚本")
# 添加参数
parser.add_argument("--cmd", type=str, required=True)
parser.add_argument("--period", type=int, default=2, required=True)
parser.add_argument("--email", type=str, required=True)
parser.add_argument("--smtp", type=str, required=True)
parser.add_argument("--cache", type=str, required=True)
parser.add_argument("--bilick", type=str, default="")
parser.add_argument("--btskon", type=str, default="0")
parser.add_argument("--hftags", type=str, default="")
parser.add_argument("--gitk", type=str, default="")
parser.add_argument("--gitags", type=str, default="")
parser.add_argument("--cnblokie", type=str, default="")
parser.add_argument("--itck", type=str, default="")
parser.add_argument("--fmtag", type=str, default="")

# 解析命令行参数
args = parser.parse_args()


class Tee:
    def __init__(self, log_path: str):
        self.log_file = open(log_path, "a", encoding="utf-8")
        self.console = sys.__stdout__

    def write(self, txt: str):
        msg = txt.replace("\n", " ").strip()
        if msg:
            msg = datetime.now().strftime("【%Y年%m月%d日 %H:%M:%S】:") + f" {msg}\n"
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

L = lambda: f"(line {sys._getframe(1).f_lineno}) "


def send_email(
    content="邮件发送成功!",
    subject="[WeMediaMon 插件] 测试邮件",
    title="SMTP 有效性检测",
    smtp_server="smtp.qq.com",
    smtp_port=465,
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
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email, smtp)
            server.sendmail(email, [msg["To"]], msg.as_string())

        print("邮件发送成功!")

    except smtplib.SMTPResponseException as e:
        if e.smtp_code == -1:
            print("邮件发送成功!")
        else:
            print(f"{L()}邮件发送失败: {e}")

    except Exception as e:
        print(f"{L()}邮件系统故障: {e}")


class Monitor:
    def __init__(self):
        self.proxy = {
            "http": "http://127.0.0.1:23456",
            "https": "http://127.0.0.1:23456",
        }
        self.cache = args.cache if args.cache[-1] != "/" else args.cache[:-1]
        self.name = self.__class__.__name__.lower().replace("mon", "")
        self.fans = f"{self.cache}/{self.name}_followers.json"
        self.blacks = f"{self.cache}/{self.name}_blacklist.txt"
        self.ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self._latest_chrome_ver()} Safari/537.36"

    def _latest_chrome_ver(self, stable=True):
        ver: str = requests.get("https://pypi.org/pypi/chromedriver-py/json").json()[
            "info"
        ]["version"]
        if stable:
            ver = ver.split(".")[0] + ".0.0.0"

        return ver

    def _tqdm(self, *args, **kwargs):  # 强制使用 Unicode 样式
        kwargs.setdefault("ascii", False)
        return tqdm(*args, **kwargs)

    def _txt2lst(self):
        if not os.path.exists(self.blacks):
            return set()

        with open(self.blacks, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return set([line.strip() for line in lines])

    def _save_traitors(self, traitors: set):
        with open(self.blacks, "w", encoding="utf-8") as file:
            for url in traitors:
                file.write(f"{url}\n")

    def _add_traitors(self, traitors: set):
        self._save_traitors(self._txt2lst() | traitors)

    def _is_deleted(self, _):
        return  # @override

    def clean_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            print(f"当前 {self.name} 狗库为空!")
            return

        for traitor in self._tqdm(traitors, desc=f"清理已失效的 {self.name} 取关狗"):
            if self._is_deleted(traitor):
                print(f"{self.name} 取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)


class BiliMon(Monitor):
    def __init__(self):
        super().__init__()
        self.endpoint = "bilibili.com"
        self._parse_cookie(args.bilick)
        self._upd_ck(self.credential)
        self.header = {"User-Agent": self.ua, "Cookie": self.ck}

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
            dedeuserid=self.uid,
        )
        self.me = user.User(uid=self.uid, credential=self.credential)

    def _upd_ck(self, credential: Credential, exclude="ac_time_value"):
        ck_dict = credential.get_cookies()
        del ck_dict[exclude]
        ck_set = set()
        for key in ck_dict:
            if ck_dict[key]:
                ck_set.add(f"{key}={ck_dict[key]}")

        pure_ck = ";".join(ck_set)
        if self.ck != pure_ck:
            self.ck = pure_ck
            subprocess.run(["dbus", "set", f"wemediamon_bilick={self.ck}"], check=True)

    def _get_fans(self, pn, retry=3):
        try:
            response = requests.get(
                f"https://api.{self.endpoint}/x/relation/followers?vmid={self.uid}&pn={pn}",
                headers=self.header,
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
                raise PermissionError(
                    f"{L() + json_data['message']}, 错误代码: {json_data['code']}"
                )

        except requests.exceptions.RequestException as e:
            if retry > 0:
                print(f"获取B站粉丝失败: {e}, 重试中...")
                time.sleep(random.uniform(4.5, 5))
                return self._get_fans(pn, retry - 1)

            else:
                raise ConnectionError(f"{L()}获取B站粉丝失败过多次!")

    def _get_followers(self):
        fans, pages = self._get_fans(pn=1)
        for i in self._tqdm(range(2, pages + 1), desc=f"扫描 {self.uid} 的B站粉丝中"):
            time.sleep(random.uniform(0.5, 1))
            followers, _ = self._get_fans(pn=i)
            if followers:
                fans.update(followers)

        return fans

    def _is_deleted(self, uid):
        try:
            time.sleep(random.uniform(0.5, 1))
            sync(user.User(uid=int(uid), credential=self.credential).get_user_info())
            return False

        except ResponseCodeException as e:
            if e.code == -404:
                return True
            else:
                raise ResponseCodeException(f"{L()}{e}")

    def _is_fans(self, uid):
        relation = sync(self.me.get_relation(uid))
        followed_status = relation["be_relation"]["attribute"]
        return followed_status == 2 or followed_status == 6  # 2=已关注, 6=互粉

    def _upd_json(self, new_fans: dict, out1000: dict):
        if os.path.exists(self.fans):
            with open(self.fans, "r", encoding="utf-8") as file:
                out1000.update(json.load(file)["out1000"])

        traitors_out1000 = set()
        out1000_keys = list(out1000.keys())
        for item in self._tqdm(out1000_keys, desc=f"过滤 {self.uid} B站1K以外粉丝列表"):
            if item in new_fans:
                del out1000[item]

            elif not self._is_fans(item):
                traitors_out1000.add(item)
                del out1000[item]

        if traitors_out1000:
            self._add_traitors(traitors_out1000)

        with open(self.fans, "w", encoding="utf-8") as file:
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

        print(f"{self.fans} 已更新!")

    def _filter_unfollows(self, unfollows):
        real_unfollows, out1000 = [], {}
        for unfollower in self._tqdm(unfollows, desc=f"过滤 {self.uid} B站取关列表"):
            if self._is_fans(unfollower["uid"]):
                out1000.update({unfollower["uid"]: unfollower["uname"]})
            else:
                real_unfollows.append(unfollower)

        return real_unfollows, out1000

    def _unfollow(self, uid: int):
        try:
            time.sleep(random.uniform(0.5, 1))
            sync(
                user.User(uid=uid, credential=self.credential).modify_relation(
                    user.RelationType.UNSUBSCRIBE
                )
            )  # return None
            return True

        except ResponseCodeException as e:
            if e.code == 22001:
                return True
            else:
                raise ResponseCodeException(f"{L()}{e}")

    def _recurse_following(self, pn: int):
        print(f"递归至 {self.name} 用户 {self.uid} 第 {pn} 页关注列表...")
        time.sleep(random.uniform(0.5, 1))
        return sync(self.me.get_followings(pn=pn))["list"]

    def _get_followings(self):
        pn = 1
        followings = []
        following = self._recurse_following(pn)
        while following:
            followings += following
            pn += 1
            following = self._recurse_following(pn)

        return followings

    def _get_folders(self, uid: int = None):
        if not uid:
            uid = self.uid

        response = requests.get(
            f"https://api.{self.endpoint}/x/v3/fav/folder/created/list-all?up_mid={uid}",
            headers=self.header,
        )
        response.raise_for_status()
        return response.json()["data"]["list"]

    def _recurse_favlist(self, pn: int, uid: int, step=50):  # 递归追的合集/收藏夹
        print(f"递归至 {self.name} 用户 {uid} 追的第 {pn} 页合集/收藏夹列表...")
        time.sleep(random.uniform(0.5, 1))
        response = requests.get(
            f"https://api.{self.endpoint}/x/v3/fav/folder/collected/list",
            params={"pn": pn, "ps": step, "up_mid": uid, "platform": "web"},
            headers=self.header,
        ).json()
        if response["code"] != 0:
            raise ConnectionError(L() + response["message"])

        return response["data"]["list"]

    def _split_lists(self, favlists: list):
        seasons, folders = {}, {}
        for favlist in favlists:
            if favlist["fid"] == 0:
                seasons[favlist["id"]] = favlist
            else:
                folders[favlist["id"]] = favlist

        return list(seasons.values()), list(folders.values())

    def _get_favlists(self, uid=None):  # 获取追的合集/收藏夹
        if not uid:
            uid = self.uid

        pn = 1
        favlists = []
        favlist = self._recurse_favlist(pn, uid)
        while favlist:
            favlists += favlist
            pn += 1
            favlist = self._recurse_favlist(pn, uid)

        return self._split_lists(favlists)

    def _unsubscribe(self, season_id: int):  # seasons <- subscriptions
        time.sleep(random.uniform(0.5, 1))
        return (
            requests.post(
                f"https://api.{self.endpoint}/x/v3/fav/season/unfav",
                data={
                    "season_id": season_id,
                    "platform": "web",
                    "csrf": self.bili_jct,
                },
                headers=self.header,
            ).json()["code"]
            == 0
        )

    def _uncollect(self, media_id: int):  # folders <- collections
        time.sleep(random.uniform(0.5, 1))
        response = requests.post(
            f"https://api.{self.endpoint}/x/v3/fav/folder/unfav",
            data={"media_id": media_id, "csrf": self.bili_jct},
            headers=self.header,
        )
        response.raise_for_status()
        return response.json()["code"] == 0

    def _rand_video(self, region=1010):
        response = requests.get(
            f"https://api.{self.endpoint}/x/web-interface/region/feed/rcmd",
            params={
                "request_cnt": 1,
                "from_region": region,  # 知识区
            },
            headers=self.header,
        )
        response.raise_for_status()
        return response.json()["data"]["archives"][0]["bvid"]

    def _daily_sign(self, manual: bool, randelay=50):
        if not manual:
            time.sleep(random.randint(0, randelay))

        response = requests.get(
            f"https://api.{self.endpoint}/x/member/web/exp/reward",
            headers=self.header,
        )
        response.raise_for_status()
        data = response.json()["data"]
        coins = sync(self.me.get_user_info())["coins"]
        to_add = min(int(coins), 5 - data["coins"] // 10)
        return data["watch"], data["share"], to_add

    def _daily_watch(self, watched: bool):
        if watched:
            print(f"每日观看 {self.name} 视频已完成!")
            return

        time.sleep(random.uniform(3, 3.5))
        response = requests.post(
            f"https://api.{self.endpoint}/x/click-interface/web/heartbeat",
            headers=self.header,
            data={
                "bvid": self._rand_video(),
                "played_time": random.randint(10, 90),
                "realtime": random.randint(10, 90),
                "start_ts": int(time.time()) - 90,
                "type": 3,
            },
        )
        print(f"观看 {self.name} 视频结果: {response.text}")

    def _daily_share(self, shared: bool):
        if shared:
            print(f"每日分享 {self.name} 视频已完成!")
            return

        try:
            time.sleep(random.uniform(3, 3.5))
            sync(
                video.Video(
                    bvid=self._rand_video(),
                    credential=self.credential,
                ).share()
            )
            print(f"✅ 分享 {self.name} 视频成功: +5 经验已到账!")

        except Exception as e:
            print(f"❌️ 分享 {self.name} 视频出错: {e}")

    def _daily_coin(self, to_add: int, max_coins=5, delay=61, manual=False):
        if to_add < max_coins or 0 <= datetime.now().hour < 6:
            print(f"{self.name} 暂不投币!")
            return

        print(f"💰 {self.name} 将投 {to_add} 硬币...")
        try:
            time.sleep(random.uniform(3, 3.5))
            i = 0
            while i < to_add:
                bvid = self._rand_video()
                v = video.Video(bvid=bvid, credential=self.credential)
                if sync(v.get_pay_coins()) < 1:
                    status = sync(v.pay_coin())
                    i += 1
                    print(f"✅ {self.name} 投币 {i}/{to_add}: {status}")
                    time.sleep(2 if manual else delay)

            print(f"✅ {self.name} 投币任务完成, +{to_add * 10} 经验到手!")

        except Exception as e:
            print(f"❌️ {self.name} 投币任务出错: {e}")

    def daily_tasks(self, retry=3, manual=False):
        try:
            watched, shared, coins_to_add = self._daily_sign(manual)
            self._daily_watch(watched)
            self._daily_share(shared)
            self._daily_coin(coins_to_add, manual=manual)

        except Exception as e:
            if retry > 0:
                print(f"完成 {self.name} 每日任务出错: {e}, 剩 {retry} 次重试...")
                time.sleep(random.uniform(3, 3.5))
                self.daily_tasks(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] 自动完成B站每日任务出错",
                    "已重试过多次",
                )

    def check_login(self):
        response = requests.get(
            f"https://api.{self.endpoint}/x/web-interface/nav",
            headers=self.header,
        )
        response.raise_for_status()
        isLogin = response.json()["data"]["isLogin"]
        print(("已" if isLogin else "未") + "登录B站")

    def upd_fans(self):
        old_fans = []
        if os.path.exists(self.fans):
            with open(self.fans, "r", encoding="utf-8") as file:
                old_fans = json.load(file)["fans1000"]

        new_fans: dict = self._get_followers()
        while not new_fans:
            print(f"获取 {self.uid} 的B站粉丝列表失败, 重试中...")
            new_fans = self._get_followers()

        if new_fans != old_fans:
            unfollows = []
            for fan in old_fans:
                if fan not in new_fans:
                    unfollows.append({"uid": fan, "uname": old_fans[fan]})

            unfollows, out1000 = self._filter_unfollows(unfollows)
            if unfollows:
                content = f"B站以下狗取关了 {self.uid}:"
                traitors = set()
                for user in unfollows:
                    url = f'https://space.{self.endpoint}/{user["uid"]}'
                    content += f'<br><a href="{url}">{user["uname"]}</a><br>'
                    traitors.add(user["uid"])

                if traitors:
                    self._add_traitors(traitors)
                    send_email(
                        content,
                        "[WeMediaMon 插件] 按罪人名单降下终末",
                        "监测到取关狗",
                    )

            else:
                print(f"暂未发现B站取关 {self.uid} 者")

            self._upd_json(new_fans, out1000)

        else:
            print(f"暂未发现B站取关 {self.uid} 者")

    def clean_followings(self):
        followings = self._get_followings()
        for following in self._tqdm(
            followings,
            desc=f"筛选 {self.name} 用户 {self.uid} 已注销关注",
        ):
            uid = int(following["mid"])
            if following["uname"] == "账号已注销":
                url = f"https://space.{self.endpoint}/{uid}"
                if self._unfollow(uid):
                    print(f"清理已注销 {self.name} 关注 {url} 成功!")
                else:
                    print(f"清理已注销 {self.name} 关注 {url} 失败...")

    def clean_favlists(self):
        subs, favs = self._get_favlists()
        for sub in self._tqdm(
            subs,
            desc=f"筛选 {self.name} 用户 {self.uid} 的已失效订阅合集",
        ):
            if sub["title"] == "该合集已失效" or sub["media_count"] == 0:
                fid, mid = sub["id"], sub["mid"]
                url = f"https://space.{self.endpoint}/{mid}/lists/{fid}" if mid else fid
                if self._unsubscribe(fid):
                    print(f"清理失效 {self.name} 订阅合集 {url} 成功!")
                else:
                    print(f"清理失效 {self.name} 订阅合集 {url} 失败...")

        for fav in self._tqdm(
            favs,
            desc=f"筛选 {self.name} 用户 {self.uid} 的已失效订阅收藏",
        ):
            if fav["title"] == "收藏夹失效" or fav["media_count"] == 0:
                fid, mid = fav["id"], fav["mid"]
                url = (
                    f"https://space.{self.endpoint}/{mid}/favlist?fid={fid}"
                    if mid
                    else fid
                )
                if self._uncollect(fid):
                    print(f"清理失效 {self.name} 订阅收藏 {url} 成功!")
                else:
                    print(f"清理失效 {self.name} 订阅收藏 {url} 失败...")

    def clean_folders(self):
        folders = self._get_folders()
        for folder in self._tqdm(
            folders,
            desc=f"清理 {self.name} 用户 {self.uid} 收藏夹失效视频",
        ):
            time.sleep(random.uniform(0.5, 1))
            fid = folder["id"]
            retcode = sync(
                favorite_list.clean_video_favorite_list_content(fid, self.credential)
            )
            url = f"https://space.{self.endpoint}/{self.uid}/favlist?fid={fid}"
            if retcode != 0:
                print(f"{L()}清理 {self.name} 收藏夹 {url} 已失效视频出错: {retcode}")

    def trigger(self, retry=3):
        try:
            self.upd_fans()
            self.clean_folders()
            self.clean_followings()
            self.clean_favlists()
            if args.btskon == "1":
                BiliMon().daily_tasks()

        except Exception as e:
            if retry > 0:
                print(f"B站监控器触发出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] B站监控器触发出错",
                    "已重试过多次",
                )


class HFMon(Monitor):
    class HfApi:
        def __init__(self, user_agent: str = None, proxy=None, token: str = None):
            self.endpoint = "https://huggingface.co/api"
            self.ua = user_agent
            self.proxy = proxy
            self.header = {"user-agent": self.ua}
            if token:
                self.header["Authorization"] = f"Bearer {token}"

        def list_user_followings(self, username: str):
            return self._get(f"{self.endpoint}/users/{username}/following")

        def list_followers(self, user_type: str, username: str):
            return self._get(f"{self.endpoint}/{user_type}s/{username}/followers")

        def list_user_following_orgs(self, username: str):
            return self._get(f"{self.endpoint}/users/{username}/following/orgs")

        def list_user_orgs(self, username: str):
            return self.get_user_overview(username)["orgs"]

        def list_models(self, author: str = None):
            return self._get(f"{self.endpoint}/models", params={"author": author})

        def list_datasets(self, author: str = None):
            return self._get(f"{self.endpoint}/datasets", params={"author": author})

        def list_spaces(self, author: str = None, token: str = None):
            header = {"user-agent": self.ua}
            if token:
                header["Authorization"] = f"Bearer {token}"

            return self._get(
                f"{self.endpoint}/spaces",
                headers=header,
                params={"author": author},
            )

        def get_space_runtime(self, space_id: str, token: str = None):
            header = {"user-agent": self.ua}
            if token:
                header["Authorization"] = f"Bearer {token}"

            return self._get(
                f"{self.endpoint}/spaces/{space_id}/runtime",
                headers=header,
            )

        def list_collections(self, owner: str = None):
            return self._get(f"{self.endpoint}/collections", params={"owner": owner})

        def list_repo_likers(self, repo_type: str, repo_id: str):
            return self._get(f"{self.endpoint}/{repo_type}s/{repo_id}/likers")

        def list_upvoters(self, item_type: str, item_id: str):
            return self._get(f"{self.endpoint}/{item_type}s/{item_id}/upvoters")

        def get_user_overview(self, username: str):
            return self._get(f"{self.endpoint}/users/{username}/overview")

        def whatami(self, target: str, retry=3):
            if "." in target:
                return "paper"

            try:
                response = requests.get(
                    f"{self.endpoint}/organizations/{target}/overview",
                    headers=self.header,
                    proxies=self.proxy,
                )
                retcode = response.status_code
                if retcode == 200:
                    return "organization"
                elif retcode == 404:
                    return "user"

                response.raise_for_status()

            except Exception as e:
                if retry > 0:
                    print(f"调用 HfApi.whatami 失败: {e}, 重试中...")
                    time.sleep(random.uniform(14.5, 15))
                    return self.whatami(target, retry - 1)

                else:
                    raise ConnectionError(f"{L()}调用 HfApi.whatami 失败过多次: {e}")

        def whoami(self, token: str = None):
            header = {"user-agent": self.ua}
            if token:
                header["Authorization"] = f"Bearer {token}"

            return self._get(f"{self.endpoint}/whoami-v2", headers=header)

        def space_info(self, space_id: str, token: str = None):
            header = {"user-agent": self.ua}
            if token:
                header["Authorization"] = f"Bearer {token}"

            return self._get(f"{self.endpoint}/spaces/{space_id}", headers=header)

        def _get(self, url, headers=None, params=None, retry=3):
            try:
                time.sleep(random.uniform(0.5, 1))
                if not headers:
                    headers = self.header

                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    proxies=self.proxy,
                )
                response.raise_for_status()
                return response.json()

            except Exception as e:
                if retry > 0:
                    print(f"调用 HfApi 失败: {e}, 重试中...")
                    time.sleep(random.uniform(14.5, 15))
                    return self._get(url, headers, params, retry - 1)

                else:
                    raise ConnectionError(f"{L()}调用 HfApi 失败过多次: {e}")

    def __init__(self):
        super().__init__()
        self.endpoint = "https://huggingface.co"
        self.header = {"User-Agent": self.ua}
        self.api = self.HfApi(user_agent=self.ua, proxy=self.proxy)
        self._parse_tags(args.hftags)

    def _parse_tags(self, hftags: str):
        tags = hftags.replace(" ", "").split(";")
        self.papers, self.users, self.orgs = [], [], []
        for tag in tags:
            tag_type = self.api.whatami(tag)
            if tag_type == "paper":
                self.papers.append(tag)
            elif tag_type == "organization":
                self.orgs.append(tag)
            else:
                self.users.append(tag)
                orgs = self.api.list_user_orgs(tag)
                for org in orgs:
                    self.orgs.append(org["name"])

    def _get_followers(self, tag_type: str, tag: str):
        fans = self.api.list_followers(tag_type, tag)
        followers = {}
        for follower in fans:
            followers[str(follower["_id"])] = str(follower["user"])

        return followers

    def _list_repos(self, name):  # user or org name
        repos = []
        models = self.api.list_models(author=name)
        for model in models:
            if not model["private"]:
                repos.append({"repo_id": model["id"], "repo_type": "model"})

        datasets = self.api.list_datasets(author=name)
        for dataset in datasets:
            if not dataset["private"]:
                repos.append({"repo_id": dataset["id"], "repo_type": "dataset"})

        spaces = self.api.list_spaces(author=name)
        for space in spaces:
            if not space["private"]:
                repos.append({"repo_id": space["id"], "repo_type": "space"})

        collects = self.api.list_collections(owner=name)
        for collect in collects:
            if not collect["private"]:
                repos.append({"repo_id": collect["slug"], "repo_type": "collection"})

        return repos

    def _list_upvoters(self, repo_type: str, repo_id: str):
        fans = self.api.list_upvoters(repo_type, repo_id)
        upvoters = {}
        for upvoter in fans:
            upvoters[str(upvoter["_id"])] = str(upvoter["user"])

        return upvoters

    def _list_repo_stargazers(self, repo: dict):
        fans = {}
        repo_id = repo["repo_id"]
        repo_type = repo["repo_type"]
        if repo_type == "collection" or repo_type == "paper":
            fans = self._list_upvoters(repo_type, repo_id)
        else:
            likers = self.api.list_repo_likers(repo_type, repo_id)
            for liker in likers:
                uid = self.api.get_user_overview(liker["user"])["_id"]
                fans[uid] = liker["user"]

        return fans

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = set()
        for tag in prev_data:
            if tag in data:
                diff = set(dict(prev_data[tag]).keys()) - set(dict(data[tag]).keys())
                for id in diff:
                    if not id in f"{data}":
                        dog = prev_data[tag][id]
                        traitors.add(id)
                        logs += f"<br><a href='{self.endpoint}/{dog}'>{dog}</a>取关了<a href='{self.endpoint}/{tag}'>{tag}</a>!<br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下抱脸狗:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _mapo(self, repo: dict):
        if repo["repo_type"] == "model":
            return repo["repo_id"]

        return repo["repo_type"] + "s/" + repo["repo_id"]

    def _get_latest_data(self):
        data = {}
        for user in self.users:
            data[user] = self._get_followers("user", user)
            repos = self._list_repos(user)
            for repo in self._tqdm(repos, desc=f"分析 {self.name} 用户 {user} 仓库中"):
                data[self._mapo(repo)] = self._list_repo_stargazers(repo)

        for org in self.orgs:
            data[org] = self._get_followers("organization", org)
            repos = self._list_repos(org)
            for repo in self._tqdm(repos, desc=f"分析 {self.name} 组织 {org} 仓库中"):
                data[self._mapo(repo)] = self._list_repo_stargazers(repo)

        for paper in self.papers:
            data[f"papers/{paper}"] = self._list_upvoters("paper", paper)

        return data

    def _is_deleted(self, uid):
        response = requests.get(
            f"{self.endpoint}/api/users/{uid}/overview",
            headers=self.header,
            proxies=self.proxy,
        )
        retcode = response.status_code
        if retcode == 200:
            return False
        elif retcode == 404:
            return True

        response.raise_for_status()

    def upd_fans(self):
        prev_data, data = {}, {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._get_latest_data()
        if data == prev_data:
            print("抱脸数据无变动...")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("抱脸数据已更新!")

    def trigger(self, retry=3):
        try:
            self.upd_fans()

        except Exception as e:
            if retry > 0:
                print(f"抱脸监控器触发失败: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] 抱脸监控器触发失败",
                    "已重试过多次",
                )


class GitHubMon(Monitor):
    def __init__(self):
        super().__init__()
        self.endpoint = "github.com"
        self.tags = str(args.gitags).split(";")
        self.header = {"user-agent": self.ua, "Authorization": f"token {args.gitk}"}
        self.whites = self._get_whitelist(f"{self.cache}/{self.name}_whitelist.txt")

    def _get_tag_type(self, name: str):
        try:
            if ("/" in name) and len(name.split("/")) == 2:
                return "Repo"  # 未来要考虑仓库存在性

            response = requests.get(
                f"https://api.{self.endpoint}/users/{name}",
                headers=self.header,
            )
            response.raise_for_status()
            data: dict = response.json()
            return data.get("type")

        except Exception as e:
            print(f"{L()}获取 {self.name} 目标类型出错: {e}")

        return None

    def _recurse_followers(self, name, pn, step=100, retry=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/users/{name}/followers?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if retry > 0:
                print(f"获取 {name} 第 {pn} 页 {self.name} 粉丝出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                return self._recurse_followers(name, pn, step, retry - 1)

            else:
                raise ConnectionError(f"{L()}重试获取 {name} 的粉丝列表过多次!")

    def _list_followers(self, username: str):
        pn = 1
        followers = {}
        while True:
            fans = self._recurse_followers(username, pn)
            if not fans:
                break

            for follower in fans:
                followers[str(follower["id"])] = str(follower["login"])

            pn += 1

        return followers

    def _recurse_repos(self, name, pn, step=100, retry=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/users/{name}/repos?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if retry > 0:
                print(f"获取 {name} 第 {pn} 页 {self.name} 仓库出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                return self._recurse_repos(name, pn, step, retry - 1)

            else:
                raise ConnectionError(f"{L()}重试获取 {name} 仓库列表过多次!")

    # 获取用户/组织所有仓库
    def _list_repos(self, username):
        pn = 1
        repos = []
        while True:
            data = self._recurse_repos(username, pn)
            if not data:
                break

            repos += [repo["full_name"] for repo in data]
            pn += 1

        return repos

    def _recurse_repo_stargazers(self, repo, pn, step=100, retry=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/repos/{repo}/stargazers?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if retry > 0:
                print(f"获取 {repo} 第 {pn} 页 {self.name} 收藏者出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                return self._recurse_repo_stargazers(repo, pn, step, retry - 1)

            else:
                raise ConnectionError(f"{L()}重试获取 {repo} 收藏者列表过多次!")

    # 获取仓库收藏者
    def _list_repo_stargazers(self, repo):
        pn = 1
        stargazers = {}
        while True:
            data = self._recurse_repo_stargazers(repo, pn)
            if not data:
                break

            for user in data:
                stargazers[str(user["id"])] = user["login"]

            pn += 1

        return stargazers

    def _list_org_members(self, name: str):
        ids = []
        try:
            response = requests.get(
                f"https://api.{self.endpoint}/orgs/{name}/members",
                headers=self.header,  # 未来成员多也需递归
            )
            response.raise_for_status()
            members: list = response.json()
            for member in members:
                ids.append(member["id"])

        except Exception as e:
            print(f"{L()}获取 {name} 的 {self.name} 组织成员列表出错: {e}")

        return ids

    def _parse_whitelist(self, whitelst: str):
        whitelist = []
        for tag in self.tags:
            if self._get_tag_type(tag) == "Organization":
                whitelist += self._list_org_members(tag)

        if whitelist:
            os.makedirs(os.path.dirname(whitelst), exist_ok=True)
            with open(whitelst, "a", encoding="utf-8") as f:
                for item in whitelist:
                    f.write(f"{item}\n")

        return whitelist

    def _get_whitelist(self, whitelst: str):
        whitelist = []
        if os.path.exists(whitelst):
            with open(whitelst, "r", encoding="utf-8") as file:
                lines = file.readlines()

            whitelist = [line.strip() for line in lines]

        else:
            whitelist = self._parse_whitelist(whitelst)

        return set(whitelist)

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = set()
        for tag in prev_data:
            if tag in data:
                diff = set(dict(prev_data[tag]).keys()) - set(dict(data[tag]).keys())
                for id in diff:
                    if not ((id in f"{data}") or (id in self.whites)):
                        dog = prev_data[tag][id]
                        traitors.add(id)
                        logs += f"<br><a href='https://{self.endpoint}/{dog}'>{dog}</a>取关了<a href='https://{self.endpoint}/{tag}'>{tag}</a>!<br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下GitHub狗:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _get_latest_data(self, tags: list, retry=3):
        data = {}
        try:
            for tag in tags:
                if self._get_tag_type(tag) == "Repo":
                    print(f"解析 {self.name} 仓库 {tag} 收藏者中...")
                    data[tag] = self._list_repo_stargazers(tag)

                else:
                    data[tag] = self._list_followers(tag)
                    repos = self._list_repos(tag)
                    for repo in self._tqdm(
                        repos,
                        desc=f"解析 {tag} 的 {self.name} 仓库中",
                    ):
                        data[repo] = self._list_repo_stargazers(repo)

        except Exception as e:
            if retry > 0:
                print(f"获取最新 GitHub 数据失败: {e}, 重试中...")
                time.sleep(random.uniform(4.5, 5))
                return self._get_latest_data(self.tags, retry - 1)

            else:
                raise ConnectionError(f"{L()}重试获取最新 GitHub 数据过多次!")

        return data

    def _is_deleted(self, uid):
        if uid in self.whites:
            print(f"{uid} 在 {self.name} 白名单, 已被排除")
            return True

        response = requests.get(
            f"https://api.{self.endpoint}/user/{uid}",
            headers=self.header,
        )
        retcode = response.status_code
        if retcode == 200:
            return False
        elif retcode == 404:
            return True

        response.raise_for_status()

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._get_latest_data(self.tags)
        if data == prev_data:
            print("GitHub 数据无变化...")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("GitHub 数据已更新!")

    def trigger(self, retry=3):
        try:
            self.upd_fans()

        except Exception as e:
            if retry > 0:
                print(f"GitHub 监控器触发出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] GitHub 监控器触发出错",
                    "已重试过多次",
                )


class CnblogsMon(Monitor):
    def __init__(self):
        super().__init__()
        self.endpoint = "cnblogs.com"
        self.header = {"user-agent": self.ua, "cookie": args.cnblokie}

    def _parse_fans(self, url):
        response = requests.get(url, headers=self.header)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        target_span: str = soup.find("span", title="账户ID").find_next("span").text
        return target_span.strip()

    def _list_followers(self):
        fans = {}
        if self.check_login(False):
            response = requests.get(
                f"https://home.{self.endpoint}/followers",
                headers=self.header,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            fan_lnks = soup.find("div", class_="avatar_list").find_all(
                "a", attrs={"title": True}
            )
            for a in fan_lnks:
                href: str = f"https://home.{self.endpoint}" + a["href"]
                username = href.split("/u/")[-1]
                uid = self._parse_fans(href)
                fans[uid] = username

            return fans

        else:
            raise PermissionError("博客园登录状态失效!")

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = set()
        diff = set(prev_data.keys()) - set(data.keys())
        for id in diff:
            dog = prev_data[id]
            traitors.add(id)
            logs += f"<br><a href='https://home.{self.endpoint}/u/{id}'>{dog}</a><br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下博客园狗取关了我:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _is_deleted(self, uid):
        response = requests.get(
            f"https://home.{self.endpoint}/u/{uid}",
            headers=self.header,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        err_div = soup.find("div", class_="error")
        if err_div:
            if " 用户不存在, 单击" in err_div:
                return True
            else:
                raise LookupError(f"{L()}{err_div}")

        return False

    def check_login(self, log=True):
        response = requests.get(
            f"https://account.{self.endpoint}/user/userinfo",
            headers=self.header,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        blog_lnk = soup.find("a", id="user_nav_blog_link")
        if blog_lnk:
            self.username = str(blog_lnk["href"]).split(f"{self.endpoint}/")[-1]
            if self.username:
                if log:
                    print("已登录博客园!")

                return True

        print("未登录博客园...")
        return False

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._list_followers()
        if data == prev_data:
            print("博客园数据无变化...")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("博客园数据已更新!")

    def trigger(self, retry=3):
        try:
            self.upd_fans()

        except Exception as e:
            if retry > 0:
                print(f"博客园监控器触发出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] 博客园监控器触发出错",
                    "已重试过多次",
                )


class ItchMon(Monitor):
    def __init__(self):
        super().__init__()
        self.endpoint = "itch.io"
        self.header = {
            "accept-language": "zh-CN,zh;q=0.9",
            "connection": "keep-alive",
            "cookie": args.itck,
            "host": self.endpoint,
            "referer": f"https://{self.endpoint}/dashboard",
            "user-agent": self.ua,
        }

    def _list_followers(self):
        fans = {}
        isLogin, response_txt = self.check_login(False)
        if isLogin:
            soup = BeautifulSoup(response_txt, "html.parser")
            fan_lnks = soup.find("div", class_="followers_list").find_all(
                "a", attrs={"data-user_id": True}
            )
            for a in fan_lnks:
                username = str(a["data-follow_url"]).split("/g/")[-1].split("/-/")[0]
                uid = a["data-user_id"]
                fans[uid] = username

        else:
            raise PermissionError(f"{self.endpoint}登录状态失效, 请更新cookie!")

        return fans

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = set()
        diff = set(prev_data.keys()) - set(data.keys())
        for id in diff:
            dog = prev_data[id]
            traitors.add(id)
            logs += f"<br><a href='https://{self.endpoint}/profile/{dog}'>{dog}</a><br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下 {self.endpoint} 狗取关了我:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _is_deleted(self, uid):
        response = requests.get(
            f"https://api.{self.endpoint}/users/{uid}",
            headers={"cookie": self.header["cookie"], "user-agent": self.ua},
            proxies=self.proxy,
        )
        retcode = response.status_code
        if retcode == 200:
            return False
        elif retcode == 400 and response.json()["errors"] == ["invalid user"]:
            return True

        response.raise_for_status()

    def check_login(self, log=True):
        response = requests.get(
            f"https://{self.endpoint}/my-followers",
            headers=self.header,
            proxies=self.proxy,
        )
        response.raise_for_status()
        if response.history:
            print(f"未登录 {self.endpoint}")
            return False, ""

        if log:
            print(f"已登录 {self.endpoint}")

        return True, response.text

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._list_followers()
        if data == prev_data:
            print(f"{self.endpoint} 数据无变化...")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print(f"{self.endpoint} 数据已更新!")

    def trigger(self, retry=15):
        try:
            self.upd_fans()

        except Exception as e:
            if retry > 0:
                print(f"{self.endpoint} 监控器触发出错: {e}, 重试中...")
                time.sleep(random.randint(5, 10))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    f"[WeMediaMon 插件] {self.endpoint} 监控器触发出错",
                    "已重试过多次",
                )


class MissevanMon(Monitor):
    def __init__(self):
        super().__init__()
        self.endpoint = "https://www.missevan.com"
        self.header = {"user-agent": self.ua}

    def _list_followers(self, uid=args.fmtag, pn=1, ps=20):
        response = requests.get(
            f"{self.endpoint}/person/getuserattention",
            params={"type": 1, "user_id": uid, "p": pn, "page_size": ps},
            headers=self.header,
        )
        response.raise_for_status()
        fans = response.json()["info"]["Datas"]
        followers = {}
        for fan in fans:
            followers[str(fan["id"])] = fan["username"]

        return followers

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = set()
        diff = set(prev_data.keys()) - set(data.keys())
        for uid in diff:
            dog = prev_data[uid]
            traitors.add(uid)
            logs += f"<br><a href='{self.endpoint}/{uid}'>{dog}</a><br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下猫耳FM狗取关了我:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _is_deleted(self, uid):
        response = requests.get(f"{self.endpoint}/{uid}", headers=self.header)
        retcode = response.status_code
        if retcode == 200:
            return False
        elif retcode == 404:
            return True

        response.raise_for_status()

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._list_followers()
        if data == prev_data:
            print("猫耳FM数据无变化...")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)

            print("猫耳FM数据已更新!")

    def trigger(self, retry=3):
        try:
            self.upd_fans()

        except Exception as e:
            if retry > 0:
                print(f"猫耳FM监控器触发出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                self.trigger(retry - 1)

            else:
                send_email(
                    f"{L()}{e}",
                    "[WeMediaMon 插件] 猫耳FM监控器触发出错",
                    "已重试过多次",
                )


def check_ss_ver(
    url="https://raw.githubusercontent.com/hq450/fancyss/3.0/packages/version.json.js",
    proxy=None,
):
    try:
        loc_ver = subprocess.run(
            ["dbus", "get", "ss_basic_version_local"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        response = requests.get(url, proxies=proxy)
        response.raise_for_status()
        txt = response.text.strip()
        data: dict = json.loads(txt)
        web_ver = data.get("version")

        if loc_ver != web_ver:
            send_email(
                f"当前版本: {loc_ver}, 更新版本: {web_ver}",
                "[WeMediaMon 插件] 发现ss版本更新",
                "请手动升级",
            )
        else:
            print("ss 无需更新!")

    except Exception as e:
        print(f"检查ss版本出错: {e}, 使用代理重试...")
        check_ss_ver(url, Monitor().proxy)


def drop_caches(value=1, cache="/proc/sys/vm/drop_caches"):
    try:
        with open(cache, "w") as f:
            f.write(str(value))

        print("缓存已清空!")

    except Exception as e:
        send_email(f"{L()}{e}", "[WeMediaMon 插件] 清理缓存出错", "请手动排查")


def update():
    check_ss_ver()
    if args.bilick:
        BiliMon().trigger()

    if args.fmtag:
        MissevanMon().trigger()

    if args.cnblokie:
        CnblogsMon().trigger()

    if args.itck:
        ItchMon().trigger()

    if args.gitags:
        GitHubMon().trigger()

    if args.hftags:
        HFMon().trigger()

    drop_caches()


def start_monitor(period=args.period):
    try:
        print(f"监控开启中...每 {period} 小时触发一次")
        schedule.every(period).hours.do(update)
        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        send_email(f"{L()}{e}", "[WeMediaMon 插件] 运行错误", "请手动排查并重启!!!")


if __name__ == "__main__":
    try:
        match args.cmd:
            case "START_MONITOR":
                start_monitor()

            case "TEST_SMTP":
                send_email()

            case "TEST_MONITOR":
                update()

            case "TEST_BILI_CK":
                BiliMon().check_login()

            case "UPD_BILI_FANS":
                BiliMon().upd_fans()

            case "UPD_BILI_BLACKS":
                BiliMon().clean_traitors()

            case "TEST_BILI_TASKS":
                BiliMon().daily_tasks(manual=True)

            case "UPD_HF_FANS":
                HFMon().upd_fans()

            case "UPD_HF_BLACKS":
                HFMon().clean_traitors()

            case "UPD_GIT_FANS":
                GitHubMon().upd_fans()

            case "UPD_GIT_BLACKS":
                GitHubMon().clean_traitors()

            case "TEST_CNBLOGS_CK":
                CnblogsMon().check_login()

            case "UPD_CNBLOGS_FANS":
                CnblogsMon().upd_fans()

            case "UPD_CNBLOGS_BLACKS":
                CnblogsMon().clean_traitors()

            case "TEST_ITCH_CK":
                ItchMon().check_login()

            case "UPD_ITCH_FANS":
                ItchMon().upd_fans()

            case "UPD_ITCH_BLACKS":
                ItchMon().clean_traitors()

            case "UPD_FM_FANS":
                MissevanMon().upd_fans()

            case "UPD_FM_BLACKS":
                MissevanMon().clean_traitors()

            case _:
                print(f"未知指令: {args.cmd}")

    except Exception as e:
        print(f"{L()}插件故障: {e}")
