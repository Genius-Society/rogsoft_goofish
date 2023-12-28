import os
import json
from smtp import send_email
from utils import *


def upd_cookie():
    print('Cookie needs upd.')


def get_fans(page, uid='30620472'):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': read_txt()
    }

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={uid}&pn={page}",
            headers=header
        )
        response.raise_for_status()  # 检查是否成功获取数据

        # 使用 json 库解析 JSON 数据
        json_data = response.json()
        if json_data['code'] == 0:
            fans = {}
            fan_list = json_data['data']['list']
            for fan in fan_list:
                fans[str(fan['mid'])] = fan['uname']

            return (fans, int(json_data['data']['total'] / 50))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return (None, 0)


def get_folowers(max_try=3):
    trytime = 0
    fans, pages = get_fans(page=1)
    while not fans:
        trytime += 1
        if trytime > max_try:
            upd_cookie()
            return None

        time.sleep(random.uniform(0.5, 1))
        fans, pages = get_fans(page=1)

    for i in tqdm(range(2, pages + 1), desc="Scanning followers..."):
        time.sleep(random.uniform(0.5, 1))
        followers, _ = get_fans(page=i)
        trytime = 0
        while not followers:
            trytime += 1
            if trytime > max_try:
                upd_cookie()
                return None

            time.sleep(random.uniform(1, 2))
            followers, _ = get_fans(page=i)

        count = len(followers)
        if count == 0:
            break

        fans.update(followers)

    return fans


def upd_fans(fans_json='fans.json'):
    old_fans = {}
    if os.path.exists(fans_json):
        with open(fans_json, 'r', encoding='utf-8') as file:
            old_fans = json.load(file)

    unfollows = []
    new_fans = get_folowers()
    if not new_fans:
        print('Failed to upd fans.')
        return

    for fan in old_fans.keys():
        if fan not in new_fans:
            unfollows.append({
                'uid': fan,
                'uname': old_fans[fan]
            })

    if new_fans != old_fans:
        with open(fans_json, 'w', encoding='utf-8') as file:
            json.dump(new_fans, file, ensure_ascii=False, indent=4)

    if unfollows:
        content = ''
        for user in unfollows:
            url = f'https://space.bilibili.com/{user["uid"]}'
            content += f'<br><a href="{url}" target="_blank">{user["uname"]}</a><br>'

        if content:
            send_email(content)

    else:
        print('No unfollower found.')


if __name__ == "__main__":
    upd_fans()
