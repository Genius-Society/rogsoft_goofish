import os
from blackfollows import parse_cookie, clean_blackfollows
from utils import *


def refresh_cookie():
    header = {"User-Agent": userAgent, "Cookie": global_cookie}
    uid, _, _ = parse_cookie(global_cookie)
    try:
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={uid}",
            headers=header,
        )
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}...")


def get_fans(page):
    header = {"User-Agent": userAgent, "Cookie": global_cookie}
    uid, _, _ = parse_cookie(global_cookie)

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
                msg, subject="更新粉丝列表失败", title=f"错误代码：{json_data['code']}"
            )
            exit()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}, retrying...")
        return get_fans(page, uid)


def get_folowers():
    fans, pages = get_fans(page=1)
    for i in tqdm(range(2, pages + 1), desc="Scanning followers..."):
        time.sleep(random.uniform(0.5, 1))
        followers, _ = get_fans(page=i)
        if followers:
            fans.update(followers)

    return fans


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


if __name__ == "__main__":
    upd_fans()
    clean_blackfollows()
