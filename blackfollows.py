import json
import time
import math
import random
import requests
from smtp import send_email
from utils import read_txt
from tqdm import tqdm


def get_list(page, cookie, api_url='https://api.bilibili.com/x/relation/blacks?'):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': cookie
    }

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"{api_url}&pn={page}",
            headers=header
        )
        response.raise_for_status()  # 检查是否成功获取数据

        # 使用 json 库解析 JSON 数据
        json_data = response.json()
        if json_data['code'] == 0:
            users = {}
            user_list = json_data['data']['list']
            for user in user_list:
                users[str(user['mid'])] = user['uname']

            return (users, math.ceil(json_data['data']['total'] / 50))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return (None, 0)


def get_whist(page, cookie, api_url='https://api.bilibili.com/x/relation/whispers?'):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': cookie
    }

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"{api_url}&pn={page}",
            headers=header
        )
        response.raise_for_status()  # 检查是否成功获取数据

        # 使用 json 库解析 JSON 数据
        json_data = response.json()
        if json_data['code'] == 0:
            whispers = {}
            whist = json_data['data']['list']
            for whisper in whist:
                whispers[str(whisper['mid'])] = whisper['uname']

            return whispers

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return {}


def get_badlist(cookies, max_try=3):
    trytime = 0
    bads, pages = get_list(page=1, cookie=cookies)
    while not bads:
        trytime += 1
        if trytime > max_try:
            return None

        time.sleep(random.uniform(0.5, 1))
        bads, pages = get_list(page=1, cookie=cookies)

    for i in tqdm(range(2, pages + 1), desc="Scanning badlist..."):
        time.sleep(random.uniform(0.5, 1))
        blacks, _ = get_list(page=i, cookie=cookies)
        trytime = 0
        while not blacks:
            trytime += 1
            if trytime > max_try:
                return None

            time.sleep(random.uniform(1, 2))
            blacks, _ = get_list(page=i, cookie=cookies)

        count = len(blacks)
        if count == 0:
            break

        bads.update(blacks)

    return bads


def get_follist(cookies, max_try=3):
    # get followings
    trytime = 0
    myuid, _, _ = parse_cookie(cookies)
    followings_api = f'https://api.bilibili.com/x/relation/followings?vmid={myuid}'
    followings, pages = get_list(
        page=1,
        cookie=cookies,
        api_url=followings_api
    )
    while not followings:
        trytime += 1
        if trytime > max_try:
            return None

        time.sleep(random.uniform(0.5, 1))
        followings, pages = get_list(
            page=1,
            cookie=cookies,
            api_url=followings_api
        )

    for i in tqdm(range(2, pages + 1), desc="Scanning followings..."):
        time.sleep(random.uniform(0.5, 1))
        followee, _ = get_list(page=i, cookie=cookies, api_url=followings_api)
        trytime = 0
        while not followee:
            trytime += 1
            if trytime > max_try:
                return None

            time.sleep(random.uniform(1, 2))
            followee, _ = get_list(
                page=i,
                cookie=cookies,
                api_url=followings_api
            )

        count = len(followee)
        if count == 0:
            break

        followings.update(followee)

    # get whispers
    print("Scanning whispers...")
    p = 1
    whispers = get_whist(page=p, cookie=cookies)
    while whispers:
        followings.update(whispers)
        p += 1
        time.sleep(random.uniform(0.5, 1))
        whispers = get_whist(page=p, cookie=cookies)

    return followings


def filter_deleted(userlist: dict):
    deleted_users = []
    if userlist:
        for key in userlist:
            if userlist[key] == '账号已注销':
                deleted_users.append(key)

        print(f'Filtered list: [ {len(deleted_users)} / {len(userlist)} ]')

    return deleted_users


def batch_modify(uid: str, cookie_str: str, action=6):
    url = "https://api.bilibili.com/x/relation/modify"
    _, csrf, cookies_str = parse_cookie(cookie_str)
    data = {
        "fid": uid,
        "act": action,  # 1是关注, 2是取关, 5是拉黑, 6是取消拉黑
        "re_src": 11,
        "jsonp": "jsonp",
        "csrf": csrf
    }

    headers = {
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Origin": "https://www.bilibili.com/"
    }

    response = requests.post(
        url,
        data=data,
        headers=headers,
        cookies=cookies_str
    )

    return json.loads(response.content)['code']


def parse_cookie(cookie_str: str):
    myuid = cookie_str.split("DedeUserID=")[1].split(";")[0]
    csrf = cookie_str.split("bili_jct=")[1].split(";")[0]
    cookies = {
        cookie.split("=")[0]: cookie.split("=")[1] for cookie in cookie_str.split("; ")
    }
    return myuid, csrf, cookies


def clean_blackfollows():
    cookie = read_txt()
    if not cookie:
        print('请输入cookie')
        send_email(
            '请输入cookie',
            subject='更新关系列表失败',
            title='可能是由于cookies缺失导致的'
        )
        exit()

    blacklist = filter_deleted(get_badlist(cookie))
    bad_outputs = []
    for uid in tqdm(blacklist, desc='清理黑名单...'):
        trytime = 0
        retcode = batch_modify(uid, cookie)
        while retcode != 0 and trytime < 3:
            time.sleep(random.uniform(1, 2))
            retcode = batch_modify(uid, cookie)

        if trytime > 2:
            bad_outputs.append({'uid': f'清理 {uid} 失败！'})
        else:
            bad_outputs.append({'uid': uid})

    follist = filter_deleted(get_follist(cookie))
    follow_outputs = []
    for uid in tqdm(follist, desc='清理关注列表...'):
        trytime = 0
        retcode = batch_modify(uid, cookie, action=2)
        while retcode != 0 and trytime < 3:
            time.sleep(random.uniform(1, 2))
            retcode = batch_modify(uid, cookie, action=2)

        if trytime > 2:
            follow_outputs.append({'uid': f'清理 {uid} 失败！'})
        else:
            follow_outputs.append({'uid': uid})

    print(f'Cleaned blacklist: {bad_outputs}')
    print(f'Cleaned follow list: {follow_outputs}')


if __name__ == "__main__":
    clean_blackfollows()
