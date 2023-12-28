from utils import *


def get_blacks(page):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': read_txt()
    }

    try:
        # 使用 requests 库下载 JSON 数据
        response = requests.get(
            f"https://api.bilibili.com/x/relation/blacks?&pn={page}",
            headers=header
        )
        response.raise_for_status()  # 检查是否成功获取数据

        # 使用 json 库解析 JSON 数据
        json_data = response.json()
        if json_data['code'] == 0:
            blacks = {}
            fan_list = json_data['data']['list']
            for fan in fan_list:
                blacks[str(fan['mid'])] = fan['uname']

            return (blacks, math.ceil(json_data['data']['total'] / 50))

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return (None, 0)


def get_badlist(max_try=3):
    trytime = 0
    bads, pages = get_blacks(page=1)
    while not bads:
        trytime += 1
        if trytime > max_try:
            return None

        time.sleep(random.uniform(0.5, 1))
        bads, pages = get_blacks(page=1)

    for i in tqdm(range(2, pages + 1), desc="Scanning badlist..."):
        time.sleep(random.uniform(0.5, 1))
        blacks, _ = get_blacks(page=i)
        trytime = 0
        while not blacks:
            trytime += 1
            if trytime > max_try:
                return None

            time.sleep(random.uniform(1, 2))
            blacks, _ = get_blacks(page=i)

        count = len(blacks)
        if count == 0:
            break

        bads.update(blacks)

    return bads


def filter_deleted(bads: dict):
    deleted_blacks = []
    for key in bads.keys():
        if bads[key] == '账号已注销':
            deleted_blacks.append(key)

    print(f'Filtered blacklist: [ {len(deleted_blacks)} / {len(bads)} ]')
    return deleted_blacks


template = '''
function batch_unblack(uid) {
    $.ajax({
        url: "//api.bilibili.com/x/relation/modify",
        type: "post",
        xhrFields: {
            withCredentials: true
        },
        data: {
            "fid": uid,
            "act": 6, //1是关注, 2是取关, 5是拉黑, 6是取消拉黑
            "re_src": 11,
            "jsonp": "jsonp",
            "csrf": document.cookie.match(/(?<=bili_jct=).+?(?=;)/)[0]
        }
    })
    console.log("解除拉黑的用户id为:" + uid);
}
'''

cmd = f'''
badlist = {filter_deleted(get_badlist())};
for (var value of badlist)
    batch_unblack(value);
'''

with open('blacks.js', "w", encoding='utf-8') as js_file:
    js_file.write(template + cmd)
