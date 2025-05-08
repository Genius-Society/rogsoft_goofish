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
parser.add_argument("--ck", type=str, help="Specify the cookie for BiliMon.")
parser.add_argument("--ck2", type=str, help="Specify the second cookie for BiliMon.")

# 解析命令行参数
args = parser.parse_args()


class BiliMon:
    def __init__(self, ck: str = args.ck, db="fans.json"):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.tmpdir = args.tmp if args.tmp[-1] != "/" else args.tmp[:-1]
        self.blacks = f"{self.tmpdir}/traitors.txt"
        self.email = args.email
        self.smtp = args.smtp
        self._set_cfg(ck, db)

    def _set_cfg(self, ck: str, db: str):
        self.dbfile = f"{self.tmpdir}/{db}"
        self._parse_cookie(ck)

    def _parse_cookie(self, ck: str):
        try:
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

        except Exception as e:
            self._send_email(
                f"请确保 {self.uid} cookie 存在且内容有效: {e}",
                subject="cookie 内容缺失或内容无效",
                title="cookie 解析异常",
            )
            self._upd_log("XU6J03M6")
            exit()

    def _send_email(
        self,
        content,
        subject="[BiliMon 插件] 按罪人名单降下终末",
        title="监测到取关狗",
        smtp_server="smtp.qq.com",
        smtp_port=587,
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
        msg["From"] = self.email
        msg["To"] = self.email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(self.email, self.smtp)
                server.sendmail(self.email, [msg["To"]], msg.as_string())

            self._upd_log("邮件发送成功!")

        except smtplib.SMTPException as e:
            if e.smtp_code == -1:
                self._upd_log("邮件发送成功!")
            else:
                self._upd_log(f"邮件发送失败: {e}")

    def _txt2lst(self):
        try:
            with open(self.blacks, "r", encoding="utf-8") as file:
                lines = file.readlines()
            # 去掉每行末尾的换行符
            lines = [line.strip() for line in lines]
            return list(set(lines))

        except Exception as e:
            self._send_email(
                f"读取文件时出错: {e}",
                subject=f"{self.blacks} 内容缺失或内容无效",
                title="txt 解析异常",
            )
            self._upd_log("XU6J03M6")
            exit()

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
                self._upd_log(msg)
                self._send_email(
                    msg,
                    subject=f"可能 {self.uid} 需要重新手动扫码登陆",
                    title=f"错误代码: {json_data['code']}",
                )
                self._upd_log("XU6J03M6")
                exit()

        except requests.exceptions.RequestException as e:
            self._upd_log(f"错误: {e}, 重试中...")
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

        self._upd_log(f"{self.dbfile} 已更新!")

    def _filter_unfollows(self, unfollows):
        real_unfollows, out1000 = [], {}
        for unfollower in tqdm(unfollows, desc=f"过滤 {self.uid} 取关列表"):
            if self._is_fans(unfollower["uid"]):
                out1000.update({unfollower["uid"]: unfollower["uname"]})
            else:
                real_unfollows.append(unfollower)

        return real_unfollows, out1000

    def _upd_fans(self):
        old_fans = []
        if os.path.exists(self.dbfile):
            with open(self.dbfile, "r", encoding="utf-8") as file:
                old_fans = json.load(file)["fans1000"]

        new_fans: dict = self._get_followers()
        while not new_fans:
            self._upd_log(f"获取 {self.uid} 粉丝列表失败, 重试中...")
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
                    self._send_email(content)

            else:
                self._upd_log(f"暂未发现取关 {self.uid} 者")

            self._upd_json(new_fans, out1000)

        else:
            self._upd_log(f"暂未发现取关 {self.uid} 者")

    def _upd(self):
        now_hour = datetime.now().hour
        if now_hour > 7 and now_hour < 23:
            self._upd_all_fans()
        else:
            self._clean_all_traitors()
            self._upd_log("当前处于免打扰时间段, 仅清理取关狗")

    def _upd_log(self, txt):
        if int(args.clock) == 1:
            with open("/tmp/upload/bilimon_run_log.txt", "a", encoding="utf-8") as file:
                file.write(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + f" {txt}\n")
        else:
            print(txt)

    def _hour_monitor(self, period=2):
        self._upd()
        self._upd_log(f"监控开启中...每 {period} 小时触发一次")
        schedule.every(period).hours.do(self._upd)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def _upd_all_fans(self):
        self._set_cfg(str(args.ck).strip(), "fans.json")
        self._upd_fans()
        ck2 = str(args.ck2).strip()
        if ck2:
            self._set_cfg(ck2, "fans2.json")
            self._upd_fans()

    def _clean_all_traitors(self):
        cleaned_traitors = []
        traitors = self._txt2lst()
        for traitor in tqdm(traitors, desc="清理已注销的取关狗"):
            if self._is_deleted(traitor):
                print(f"取关狗 {traitor} 已被清理!")
            else:
                cleaned_traitors.append(traitor)

            time.sleep(random.uniform(0.5, 1))

        if cleaned_traitors:
            self._save_traitors(cleaned_traitors)

    def start(self):
        try:
            if int(args.clock) == 1:
                self._hour_monitor(period=args.period)
            elif int(args.clock) == 0:
                self._upd_all_fans()
            elif int(args.clock) == 2:
                self._clean_all_traitors()
            elif int(args.clock) == 3:
                self._send_email(
                    "邮件发送成功!",
                    subject="[BiliMon 插件] 邮件发送测试",
                    title="测试 SMTP 模块",
                )

            self._upd_log("XU6J03M6")

        except Exception as e:
            self._upd_log(f"运行错误: {e}, 重试中...")
            time.sleep(1)
            self.start()


if __name__ == "__main__":
    BiliMon().start()
