import os
import time
import json
import random
import requests
from tqdm import tqdm
from smtp import send_email


def get_fans(page, uid='30620472'):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': "buvid3=324500E7-4F52-5EA3-F628-1994160741D036790infoc; b_nut=1700736136; CURRENT_FNVAL=4048; _uuid=E72310C8B-3DBD-A361-FDAA-45E105E1518A1036335infoc; buvid4=E7B6EE73-CD40-FAAC-1C53-1357D6E72F0238098-023112310-; buvid_fp=b4fa4c3909839e6a0222f3bd9eee8039; rpdid=|(k|))~uu)Jl0J'u~||~JYuJ); DedeUserID=3546574294616302; DedeUserID__ckMd5=7b698ed75104cc36; enable_web_push=DISABLE; header_theme_version=CLOSE; fingerprint=b4fa4c3909839e6a0222f3bd9eee8039; LIVE_BUVID=AUTO1917009940004703; SESSDATA=e0f7c9fd%2C1716875228%2C49e9d%2Ab1CjBRctTyjev616Kmpb8b_uzbh9IsYHfTCA9VsIke1hhEXVnGh2YL2wwrQ4OfM2kSswYSVjl2SjBsMHk4QWctVW5YV1NOakM5aGpDbHVwcFFXMUlmMkw4WHJ6bHBVMnl3RldYaGk1YmpaSTQwNFByS0k3ckRxdjEwLTVkeW92a1pKRkY0MGJkakdBIIEC; bili_jct=5665cb41eb521465973fae773f57dc27; home_feed_column=4; b_lsid=10AFD1F7F_18C1F2FA52C; sid=6zw8zu6c; bp_video_offset_3546574294616302=869695976567209991; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDE1OTEzNDMsImlhdCI6MTcwMTMzMjA4MywicGx0IjotMX0.x5mUJhaBtCDnq3suz3wZkMq7zXagsyDR7NTy-L1G_Qg; bili_ticket_expires=1701591283; innersign=0; PVID=4; browser_resolution=890-331; bsource=search_bing"
    }

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"https://api.bilibili.com/x/relation/followers?vmid={uid}&pn={page}",
            headers=header,
            proxies={
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890'
            }
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


def get_folowers():
    fans, pages = get_fans(page=1)
    while not fans:
        time.sleep(random.uniform(0.5, 1))
        fans, pages = get_fans(page=1)

    for i in tqdm(range(2, pages + 1), desc="Updating fans..."):
        time.sleep(random.uniform(0.5, 1))
        followers, _ = get_fans(page=i)
        while not followers:
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
    # with open('test.json', 'r', encoding='utf-8') as file:
    #     new_fans = json.load(file)

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
            nickname = user['uname']
            url = "https://space.bilibili.com/" + user['uid']
            # whisper = "https://message.bilibili.com/#/whisper/mid" + user['uid']
            content += f'<br><a href="{url}" target="_blank">{nickname}</a><br>'

        if content:
            send_email(content)

    else:
        print('No unfollower found.')
