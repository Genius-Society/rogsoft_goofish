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
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from bilibili_api import ResponseCodeException, Credential, favorite_list, user, sync

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description="WeMediaMon 配置脚本")
# 添加参数
parser.add_argument("--cmd", type=str, required=True)
parser.add_argument("--period", type=int, default=2, required=True)
parser.add_argument("--email", type=str, required=True)
parser.add_argument("--smtp", type=str, required=True)
parser.add_argument("--cache", type=str, required=True)
parser.add_argument("--bilick", type=str, default="")
parser.add_argument("--hftk", type=str, default="")
parser.add_argument("--papers", type=str, default="")
parser.add_argument("--gitags", type=str, default="")
parser.add_argument("--cnblokie", type=str, default="")
parser.add_argument("--itck", type=str, default="")

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


def send_email(
    content="邮件发送成功!",
    subject="[WeMediaMon 插件] 测试邮件",
    title="SMTP有效性检测",
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
            print(f"邮件发送失败: {e}")

    except Exception as ex:
        print(ex)


class Monitor:
    def __init__(self, name: str):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
        self.proxy = {
            "http": "http://127.0.0.1:23456",
            "https": "http://127.0.0.1:23456",
        }
        self.cache = args.cache if args.cache[-1] != "/" else args.cache[:-1]
        self.fans = f"{self.cache}/{name}_followers.json"
        self.blacks = f"{self.cache}/{name}_blacklist.txt"

    def _tqdm(self, *args, **kwargs):  # 强制使用 Unicode 样式
        kwargs.setdefault("ascii", False)
        return tqdm(*args, **kwargs)

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


class BiliMon(Monitor):
    def __init__(self):
        super().__init__("bili")
        self.endpoint = "bilibili.com"
        self._parse_cookie(args.bilick)
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
        )

    def _get_fans(self, pn, trytime=3):
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
                    f"{json_data['message']}, 错误代码: {json_data['code']}"
                )

        except requests.exceptions.RequestException as e:
            if trytime > 0:
                print(f"获取B站粉丝失败: {e}, 重试中...")
                time.sleep(random.uniform(4.5, 5))
                trytime -= 1
                return self._get_fans(pn, trytime)

            else:
                raise ConnectionError("获取B站粉丝失败过多次!")

    def _get_followers(self):
        fans, pages = self._get_fans(pn=1)
        for i in self._tqdm(range(2, pages + 1), desc=f"扫描 {self.uid} B站粉丝中"):
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
                raise ResponseCodeException(f"{e}")

    def _is_fans(self, uid):
        relation = sync(
            user.User(uid=self.uid, credential=self.credential).get_relation(uid)
        )
        followed_status = relation["be_relation"]["attribute"]
        return followed_status == 2 or followed_status == 6  # 2=已关注, 6=互粉

    def _upd_json(self, new_fans: dict, out1000: dict):
        if os.path.exists(self.fans):
            with open(self.fans, "r", encoding="utf-8") as file:
                out1000.update(json.load(file)["out1000"])

        traitors_out1000 = []
        out1000_keys = list(out1000.keys())
        for item in self._tqdm(out1000_keys, desc=f"过滤 {self.uid} B站1K以外粉丝列表"):
            if item in new_fans:
                del out1000[item]

            elif not self._is_fans(item):
                traitors_out1000.append(item)
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
                raise ResponseCodeException(f"{e}")

    def _recurse_following(self, pn: int):
        print(f"递归用户 {self.uid} 关注列表第 {pn} 页...")
        time.sleep(random.uniform(0.5, 1))
        return sync(
            user.User(uid=self.uid, credential=self.credential).get_followings(pn=pn)
        )["list"]

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
        print(f"递归用户 {uid} 追的合集/收藏夹列表第 {pn} 页...")
        time.sleep(random.uniform(0.5, 1))
        response = requests.get(
            f"https://api.{self.endpoint}/x/v3/fav/folder/collected/list",
            params={"pn": pn, "ps": step, "up_mid": uid, "platform": "web"},
            headers=self.header,
        ).json()
        if response["code"] != 0:
            raise ConnectionError(response["message"])

        return response["data"]["list"]

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

        return favlists

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
            print(f"获取 {self.uid} B站粉丝列表失败, 重试中...")
            new_fans = self._get_followers()

        if new_fans != old_fans:
            unfollows = []
            for fan in old_fans:
                if fan not in new_fans:
                    unfollows.append({"uid": fan, "uname": old_fans[fan]})

            unfollows, out1000 = self._filter_unfollows(unfollows)
            if unfollows:
                content = f"B站以下狗取关了 {self.uid}:"
                traitors = []
                for user in unfollows:
                    url = f'https://space.{self.endpoint}/{user["uid"]}'
                    content += f'<br><a href="{url}">{user["uname"]}</a><br>'
                    traitors.append(user["uid"])

                if content:
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

    def clean_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            raise LookupError("当前B站狗库为空!")

        for traitor in self._tqdm(traitors, desc="清理已注销的B站取关狗"):
            if self._is_deleted(traitor):
                print(f"B站取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)

    def clean_followings(self):
        followings = self._get_followings()
        for following in self._tqdm(
            followings, desc=f"筛选用户 {self.uid} 所有已注销关注"
        ):
            uid = int(following["mid"])
            if following["uname"] == "账号已注销":
                url = f"https://space.{self.endpoint}/{uid}"
                if self._unfollow(uid):
                    print(f"清理已注销关注 {url} 成功!")
                else:
                    print(f"清理已注销关注 {url} 失败...")

    def clean_subscriptions(self):
        favlists = self._get_favlists()
        for favlist in self._tqdm(favlists, desc=f"筛选用户 {self.uid} 的已失效订阅"):
            if favlist["title"] == "该合集已失效":
                fid = favlist["id"]
                url = f"https://space.{self.endpoint}/{favlist['upper']['mid']}/lists/{fid}"
                if self._unsubscribe(fid):
                    print(f"清理失效订阅 {url} 成功!")
                else:
                    print(f"清理失效订阅 {url} 失败...")

    def clean_folders(self):
        folders = self._get_folders()
        for folder in self._tqdm(
            folders, desc=f"清理用户 {self.uid} 所有收藏夹中失效视频"
        ):
            time.sleep(random.uniform(0.5, 1))
            fid = folder["id"]
            retcode = sync(
                favorite_list.clean_video_favorite_list_content(fid, self.credential)
            )
            url = f"https://space.{self.endpoint}/{self.uid}/favlist?fid={fid}"
            if retcode != 0:
                print(f"清理收藏夹 {url} 已失效视频出错: {retcode}")

    def trigger(self, trytime=3):
        try:
            self.upd_fans()
            self.clean_folders()
            self.clean_followings()
            self.clean_subscriptions()

        except Exception as e:
            print(f"B站监控器触发出错: {e}, 重试中...")
            if trytime > 0:
                trytime -= 1
                self.trigger(trytime)

            else:
                send_email(
                    f"{e}",
                    "[WeMediaMon 插件] B站监控器触发出错",
                    "已重试过多次",
                )


class HFMon(Monitor):
    class HfApi:
        def __init__(self, token: str = None, user_agent: str = None, proxy=None):
            self.endpoint = "https://huggingface.co/api"
            self.ua = user_agent
            self.proxy = proxy
            self.header = {"user-agent": self.ua}
            if token:
                self.header["Authorization"] = f"Bearer {token}"

        def list_user_following(self, username: str):
            return self._get(f"{self.endpoint}/users/{username}/following")

        def list_user_follower(self, user_type: str, username: str):
            return self._get(f"{self.endpoint}/{user_type}s/{username}/followers")

        def list_user_org(self, username: str):
            return self._get(f"{self.endpoint}/users/{username}/following/orgs")

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

        def _get(self, url, headers=None, params=None, trytime=3):
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
                if trytime > 0:
                    print(f"调用 HfApi 失败: {e}, 重试中...")
                    time.sleep(random.uniform(14.5, 15))
                    trytime -= 1
                    return self._get(url, headers, params, trytime)

                else:
                    raise ConnectionError("调用 HfApi 失败过多次!")

    def __init__(self):
        super().__init__("hf")
        self.endpoint = "https://huggingface.co"
        self.papers = args.papers.replace(" ", "").split(";")
        self.token = args.hftk.strip()
        self.header = {"User-Agent": self.ua, "Authorization": f"Bearer {self.token}"}
        self.api = self.HfApi(user_agent=self.ua, proxy=self.proxy)
        self.me = self.api.whoami(token=self.token)["name"]
        self.tag_users, self.tag_orgs = self._parse_tags()

    def _parse_tags(self):
        following_users = [self.me]
        followings = self.api.list_user_following(self.me)
        for following in followings:
            following_users.append(following["user"])

        following_orgs = []
        orgs = self.api.list_user_org(self.me)
        for org in orgs:
            following_orgs.append(org["name"])

        return following_users, following_orgs

    def _activate_space(self, space_id: str):
        static = self.api.space_info(space_id, self.token)["sdk"] == "static"
        response = requests.get(
            f"https://{space_id.replace('/', '-').replace('_', '-').lower()}.{'static.' if static else ''}hf.space",
            headers=self.header,
        )
        response.raise_for_status()

    def _get_followers(self, tag_type: str, tag: str):
        fans = self.api.list_user_follower(tag_type, tag)
        followers = {}
        for follower in fans:
            followers[str(follower["_id"])] = str(follower["user"])

        return followers

    def _list_repos(self, username):
        repos = []
        models = self.api.list_models(author=username)
        for model in models:
            if not model["private"]:
                repos.append({"repo_id": model["id"], "repo_type": "model"})

        datasets = self.api.list_datasets(author=username)
        for dataset in datasets:
            if not dataset["private"]:
                repos.append({"repo_id": dataset["id"], "repo_type": "dataset"})

        spaces = self.api.list_spaces(author=username)
        for space in spaces:
            if not space["private"]:
                repos.append({"repo_id": space["id"], "repo_type": "space"})

        collects = self.api.list_collections(owner=username)
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
        traitors = []
        for tag in prev_data:
            if tag in data:
                diff = set(prev_data[tag].keys()) - set(data[tag].keys())
                for id in diff:
                    dog = prev_data[tag][id]
                    traitors.append(id)
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
        for user in self.tag_users:
            data[user] = self._get_followers("user", user)
            repos = self._list_repos(user)
            for repo in self._tqdm(repos, desc=f"分析 {user} 用户仓库中"):
                data[self._mapo(repo)] = self._list_repo_stargazers(repo)

        for org in self.tag_orgs:
            data[org] = self._get_followers("organization", org)
            repos = self._list_repos(org)
            for repo in self._tqdm(repos, desc=f"分析 {org} 组织仓库中"):
                data[self._mapo(repo)] = self._list_repo_stargazers(repo)

        for paper in self.papers:
            data[f"papers/{paper}"] = self._list_upvoters("paper", paper)

        return data

    def _list_spaces(self, username: str):
        sleepings, errors = [], []
        spaces = self.api.list_spaces(username, self.token)
        for space in spaces:
            status = self.api.get_space_runtime(space["id"], self.token)["stage"]
            if status == "SLEEPING":
                sleepings.append(space["id"])
            elif "ERROR" in status:
                errors.append(f"{self.endpoint}/spaces/{space['id']}")

        return sleepings, errors

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

    def activate(self):
        spaces, failures = [], []
        targets = self.tag_users + self.tag_orgs
        for tag in self._tqdm(targets, desc="搜集抱脸空间中"):
            sleeps, errors = self._list_spaces(tag)
            spaces += sleeps
            failures += errors

        logs = ""
        for space in self._tqdm(spaces, desc="激活抱脸空间中"):
            self._activate_space(space)
            logs += f"{space} "

        if logs:
            print(f"抱脸空间 {logs}激活完成!")

        content = ""
        for failure in failures:
            errepo: str = failure
            errepo = errepo.replace(self.endpoint, "")
            content += f"<br><a href='{failure}'>{errepo[1:]}</a><br>"

        if content:
            send_email(
                f"激活以下抱脸空间失败: {content}",
                "[WeMediaMon 插件] 运行错误",
                "空间激活出现问题",
            )

    def upd_fans(self):
        prev_data, data = {}, {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._get_latest_data()
        if data == prev_data:
            print("抱脸数据无变动")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("抱脸数据已更新!")

    def upd_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            raise LookupError("当前抱脸狗库为空!")

        for traitor in self._tqdm(traitors, desc="清理已注销的抱脸取关狗"):
            if self._is_deleted(traitor):
                print(f"抱脸取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)

    def trigger(self, trytime=3):
        try:
            self.activate()
            self.upd_fans()

        except Exception as e:
            print(f"抱脸监控器触发失败: {e}, 重试中...")
            if trytime > 0:
                trytime -= 1
                self.trigger(trytime)

            else:
                send_email(
                    f"{e}",
                    "[WeMediaMon 插件] 抱脸监控器触发失败",
                    "已重试过多次",
                )


class GitHubMon(Monitor):
    def __init__(self):
        super().__init__("github")
        self.endpoint = "github.com"
        self.tags = args.gitags.split(";")
        self.header = {"user-agent": self.ua}

    def _recurse_followers(self, username, pn, step=100, trytime=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/users/{username}/followers?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if trytime > 0:
                print(f"获取 {username} 用户第 {pn} 页粉丝出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                trytime -= 1
                return self._recurse_followers(username, pn, step, trytime)

            else:
                raise ConnectionError(f"重试获取 {username} 用户的粉丝列表过多次!")

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

    def _recurse_user_repos(self, username, pn, step=100, trytime=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/users/{username}/repos?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if trytime > 0:
                print(f"获取 {username} 用户第 {pn} 页仓库出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                trytime -= 1
                return self._recurse_user_repos(username, pn, step, trytime)

            else:
                raise ConnectionError(f"重试获取 {username} 用户的仓库列表过多次!")

    # 获取用户所有仓库
    def _list_user_repos(self, username):
        pn = 1
        repos = []
        while True:
            data = self._recurse_user_repos(username, pn)
            if not data:
                break

            repos += [repo["full_name"] for repo in data]
            pn += 1

        return repos

    def _recurse_repo_stargazers(self, repo, pn, step=100, trytime=3):
        try:
            time.sleep(random.uniform(0.5, 1))
            response = requests.get(
                f"https://api.{self.endpoint}/repos/{repo}/stargazers?per_page={step}&page={pn}",
                headers=self.header,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if trytime > 0:
                print(f"获取 {repo} 仓库第 {pn} 页收藏者出错: {e}, 重试中...")
                time.sleep(random.uniform(3.5, 4.5))
                trytime -= 1
                return self._recurse_repo_stargazers(repo, pn, step, trytime)

            else:
                raise ConnectionError(f"重试获取 {repo} 仓库收藏者列表过多次!")

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

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = []
        for tag in prev_data:
            if tag in data:
                diff = set(prev_data[tag].keys()) - set(data[tag].keys())
                for id in diff:
                    dog = prev_data[tag][id]
                    traitors.append(id)
                    logs += f"<br><a href='https://{self.endpoint}/{dog}'>{dog}</a>取关了<a href='https://{self.endpoint}/{tag}'>{tag}</a>!<br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下GitHub狗:{logs}",
                "[WeMediaMon 插件] 按罪人名单降下终末",
                "监测到取关狗",
            )

        print(logs)

    def _get_latest_data(self, tags: list, trytime=3):
        data = {}
        try:
            for tag in tags:
                data[tag] = self._list_followers(tag)
                repos = self._list_user_repos(tag)
                for repo in self._tqdm(repos, desc=f"解析 {tag} 仓库中"):
                    data[repo] = self._list_repo_stargazers(repo)

        except Exception as e:
            if trytime > 0:
                print(f"获取最新 GitHub 数据失败: {e}, 重试中...")
                time.sleep(random.uniform(4.5, 5))
                trytime -= 1
                return self._get_latest_data(self.tags, trytime)

            else:
                raise ConnectionError("重试获取最新 GitHub 数据过多次!")

        return data

    def _is_deleted(self, uid):
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

    def upd_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            raise LookupError("当前GitHub狗库为空!")

        for traitor in self._tqdm(traitors, desc="清理已注销的GitHub取关狗"):
            if self._is_deleted(traitor):
                print(f"GitHub取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._get_latest_data(self.tags)
        if data == prev_data:
            print("GitHub 数据无变化")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("GitHub 数据已更新")

    def trigger(self, trytime=3):
        try:
            self.upd_fans()

        except Exception as e:
            print(f"GitHub监控器触发出错: {e}, 重试中...")
            if trytime > 0:
                trytime -= 1
                self.trigger(trytime)

            else:
                send_email(
                    f"{e}",
                    "[WeMediaMon 插件] GitHub监控器触发出错",
                    "已重试过多次",
                )


class CnblogsMon(Monitor):
    def __init__(self):
        super().__init__("cnblogs")
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
        if self.check_login():
            response = requests.get(
                f"https://home.{self.endpoint}/u/{self.username}/followers",
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
        traitors = []
        diff = set(prev_data.keys()) - set(data.keys())
        for id in diff:
            dog = prev_data[id]
            traitors.append(id)
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
                raise LookupError(f"{err_div}")

        return False

    def upd_traitors(self):
        if not self.check_login():
            return

        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            raise LookupError("当前博客园狗库为空!")

        for traitor in self._tqdm(traitors, desc="清理已注销的博客园取关狗"):
            if self._is_deleted(traitor):
                print(f"博客园取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)

    def check_login(self):
        response = requests.get(
            f"https://account.{self.endpoint}/user/userinfo",
            headers=self.header,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        blog_lnk = soup.find("a", id="user_nav_blog_link")
        if blog_lnk:
            self.username = blog_lnk["href"].split(f"{self.endpoint}/")[-1][:-1]
            if self.username:
                print("已登录博客园")
                return True

        print("未登录博客园")
        return False

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._list_followers()
        if data == prev_data:
            print("博客园数据无变化")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("博客园数据已更新")

    def trigger(self, trytime=3):
        try:
            self.upd_fans()

        except Exception as e:
            print(f"博客园监控器触发出错: {e}, 重试中...")
            if trytime > 0:
                trytime -= 1
                self.trigger(trytime)

            else:
                send_email(
                    f"{e}",
                    "[WeMediaMon 插件] 博客园监控器触发出错",
                    "已重试过多次",
                )


class ItchMon(Monitor):
    def __init__(self):
        super().__init__("itch")
        self.endpoint = "itch.io"
        self.header = {
            "accept-language": "zh-CN,zh;q=0.9",
            "connection": "keep-alive",
            "cookie": args.itck,
            "host": "itch.io",
            "referer": f"https://{self.endpoint}/dashboard",
            "user-agent": self.ua,
        }

    def _list_followers(self):
        fans = {}
        isLogin, response_txt = self.check_login()
        if isLogin:
            soup = BeautifulSoup(response_txt, "html.parser")
            fan_lnks = soup.find("div", class_="followers_list").find_all(
                "a", attrs={"data-user_id": True}
            )
            for a in fan_lnks:
                username = a["data-follow_url"].split("/g/")[-1].split("/-/")[0]
                uid = a["data-user_id"]
                fans[uid] = username

        else:
            raise PermissionError("itch.io登录状态失效, 请更新cookie!")

        return fans

    def _compare_data(self, prev_data: dict, data: dict):
        logs = ""
        traitors = []
        diff = set(prev_data.keys()) - set(data.keys())
        for id in diff:
            dog = prev_data[id]
            traitors.append(id)
            logs += f"<br><a href='https://{self.endpoint}/profile/{dog}'>{dog}</a><br>"

        if traitors:
            self._add_traitors(traitors)
            send_email(
                f"以下itch.io狗取关了我:{logs}",
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

    def upd_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        if not traitors:
            raise LookupError("当前itch.io狗库为空!")

        for traitor in self._tqdm(traitors, desc="清理已注销的itch.io取关狗"):
            if self._is_deleted(traitor):
                print(f"itch.io取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors != traitors:
            self._save_traitors(cleaned_traitors)

    def check_login(self):
        response = requests.get(
            f"https://{self.endpoint}/my-followers",
            headers=self.header,
            proxies=self.proxy,
        )
        response.raise_for_status()
        if response.history:
            print("未登录itch.io")
            return False, ""

        else:
            print("已登录itch.io")
            return True, response.text

    def upd_fans(self):
        prev_data = {}
        if os.path.exists(self.fans):
            with open(self.fans, "r") as json_file:
                prev_data = json.load(json_file)

        data = self._list_followers()
        if data == prev_data:
            print("itch.io数据无变化")
        else:
            self._compare_data(prev_data, data)
            with open(self.fans, "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("itch.io数据已更新")

    def trigger(self, trytime=3):
        try:
            self.upd_fans()

        except Exception as e:
            print(f"itch.io监控器触发出错: {e}, 重试中...")
            if trytime > 0:
                trytime -= 1
                self.trigger(trytime)

            else:
                send_email(
                    f"{e}",
                    "[WeMediaMon 插件] itch.io监控器触发出错",
                    "已重试过多次",
                )


def update():
    time.sleep(random.uniform(0.5, 5))
    if args.bilick:
        BiliMon().trigger()

    if args.hftk:
        HFMon().trigger()

    if args.gitags:
        GitHubMon().trigger()

    if args.cnblokie:
        CnblogsMon().trigger()

    if args.itck:
        ItchMon().trigger()


def start_monitor(period=args.period):
    try:
        update()
        print(f"监控开启中...每 {period} 小时触发一次")
        schedule.every(period).hours.do(update)
        while True:
            schedule.run_pending()
            time.sleep(1)

    except Exception as e:
        send_email(f"{e}", "[WeMediaMon 插件] 运行错误", "请手动排查")


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
                BiliMon().clean_traitors()

            case "UPD_HF_FANS":
                HFMon().upd_fans()

            case "ACTIVATE_HF_REPOS":
                HFMon().activate()

            case "UPD_HF_BLACKS":
                HFMon().upd_traitors()

            case "UPD_GIT_FANS":
                GitHubMon().upd_fans()

            case "UPD_GIT_BLACKS":
                GitHubMon().upd_traitors()

            case "TEST_CNBLOGS_CK":
                CnblogsMon().check_login()

            case "UPD_CNBLOGS_FANS":
                CnblogsMon().upd_fans()

            case "UPD_CNBLOGS_BLACKS":
                CnblogsMon().upd_traitors()

            case "TEST_ITCH_CK":
                ItchMon().check_login()

            case "UPD_ITCH_FANS":
                ItchMon().upd_fans()

            case "UPD_ITCH_BLACKS":
                ItchMon().upd_traitors()

            case _:
                print(f"未知指令: {args.cmd}")

    except Exception as e:
        print(f"{e}")
