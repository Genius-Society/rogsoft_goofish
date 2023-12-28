import json
import requests
from utils import *


def add2blacklist(uid, url="https://api.bilibili.com/x/relation/modify"):
    # 要发送的数据
    data_to_send = {
        'fid': uid,
        'act': 5,
        're_src': 11,
        'jsonp': 'jsonp',
        'csrf': 'c336de768746a875e0383a989bff9e39'
    }

    # 将数据转换为JSON格式
    json_data = json.dumps(data_to_send)

    # 设置请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        'Cookie': read_txt()
    }

    # 发送Ajax POST请求
    response = requests.post(url, data=json_data, headers=headers)

    # 检查响应
    if response.status_code == 200:
        # 请求成功
        print("Ajax POST请求成功")
        print("响应内容:", response.text)
    else:
        # 请求失败
        print("Ajax POST请求失败")
        print("错误码:", response.status_code)
        print("错误内容:", response.text)


if __name__ == "__main__":
    add2blacklist('3493094752258163')
