import os
import math
import shutil
import zipfile
import requests
import subprocess
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

MAX_CK_LEN = 1024
TMP_DIR = "__pycache__"
CHROME = "chrome-win64"
CHROME_URL = f"https://genius-society.asuscomm.com:81/d/archive/mirrors/{CHROME}.zip"


def download_file(url: str, folder_path=f"./{TMP_DIR}"):
    # 确保文件夹存在, 如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_name = url.split("/")[-1]  # 解析文件名
    file_path = os.path.join(folder_path, file_name)  # 文件的完整路径
    response = requests.get(url, stream=True)  # 下载文件
    total_size = int(response.headers.get("content-length", 0))

    # 添加进度条
    with open(file_path, "wb") as f, tqdm(
        total=total_size,
        desc=file_name,
        unit_scale=True,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)
            pbar.update(len(data))

    print(f"文件已下载到: {file_path}")


def unzip_file(zip_file: str, extract_folder=f"./{TMP_DIR}"):
    # 确保解压缩目录存在, 如果不存在则创建
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    # 打开压缩包
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_folder)  # 解压缩到指定目录

    print(f"文件已解压缩到: {extract_folder}")


def init_chrome(vision=False, keep_alive=False):
    user_dir = f"{os.path.dirname(os.path.abspath(__file__))}/{TMP_DIR}/user_data"
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    chrome_dir = f"./{TMP_DIR}/{CHROME}"
    if not os.path.exists(f"{chrome_dir}.zip") and not os.path.exists(chrome_dir):
        download_file(CHROME_URL)
        unzip_file(f"{chrome_dir}.zip")

    elif not os.path.exists(chrome_dir):
        unzip_file(f"{chrome_dir}.zip")

    chrome_options = Options()
    chrome_options.binary_location = f"./{TMP_DIR}/{CHROME}/chrome.exe"
    if not vision:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument(rf"user-data-dir={user_dir}")
    chrome_options.add_argument("--mute-audio")
    if keep_alive:
        chrome_options.add_experimental_option("detach", True)

    return webdriver.Chrome(options=chrome_options)


def list2str(cookies):
    cookie_list = []
    for cookie in tqdm(cookies, desc="parsing cookies..."):
        cookie_list.append(cookie["name"] + "=" + cookie["value"])

    return "; ".join(cookie_list)


def upd_cookie(manual=False, step=MAX_CK_LEN, page="https://space.bilibili.com"):
    try:
        driver = init_chrome(vision=manual)
        driver.get(page)
        cookies = list2str(driver.get_cookies())  # TODO: 在这打断点手动登录
        size = len(cookies)
        count = math.ceil(size / step)
        for i in range(count):
            cookie_txt = f"./{TMP_DIR}/cookie{i + 1 if i else ''}.txt"
            with open(cookie_txt, "w", encoding="utf-8") as file:
                file.write(cookies[i * step : min((i + 1) * step, size)])

            if i:
                subprocess.Popen(["notepad", cookie_txt])

        driver.close()
        os.system(f"notepad ./{TMP_DIR}/cookie.txt")

    except Exception as e:
        if os.path.exists(f"./{TMP_DIR}/user_data"):
            shutil.rmtree(f"./{TMP_DIR}/user_data")

        print(f"更新cookie失败, 错误信息: {e}")
        exit()


if __name__ == "__main__":
    upd_cookie(manual=True)
