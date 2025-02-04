import os
import shutil
import zipfile
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


USER_DATA = "user_data"
CHROME = "chrome-win64"
CHROME_URL = f"https://genius-society.asuscomm.com:81/d/archive/mirrors/{CHROME}.zip"


def download_file(url: str, folder_path="./"):
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
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=file_name,
        ascii=True,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            f.write(data)
            pbar.update(len(data))

    print(f"文件已下载到: {file_path}")


def unzip_file(zip_file: str, extract_folder="./", rm_pkg=True):
    # 确保解压缩目录存在, 如果不存在则创建
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    # 打开压缩包
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_folder)  # 解压缩到指定目录

    print(f"文件已解压缩到: {extract_folder}")
    if rm_pkg:
        os.remove(zip_file)


def init_chrome(vision=False, keep_alive=False):
    user_dir_name = f"{os.path.dirname(os.path.abspath(__file__))}/{USER_DATA}"
    if not os.path.exists(user_dir_name):
        os.makedirs(user_dir_name)

    if not os.path.exists(f"./{CHROME}.zip") and not os.path.exists(f"./{CHROME}"):
        download_file(CHROME_URL)
        unzip_file(f"./{CHROME}.zip")

    chrome_options = Options()
    chrome_options.binary_location = f"./{CHROME}/chrome.exe"
    if not vision:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument(rf"user-data-dir={user_dir_name}")
    chrome_options.add_argument("--mute-audio")
    if keep_alive:
        chrome_options.add_experimental_option("detach", True)

    return webdriver.Chrome(options=chrome_options)


def list2str(cookies):
    cookie_list = []
    for cookie in tqdm(cookies, desc="parsing cookies..."):
        cookie_list.append(cookie["name"] + "=" + cookie["value"])

    return "; ".join(cookie_list)


def upd_cookie(manual=False):
    try:
        driver = init_chrome(vision=manual)
        driver.get("https://space.bilibili.com")
        cookies = list2str(driver.get_cookies())  # TODO: 在这打断点手动登录
        with open("cookie.txt", "w", encoding="utf-8") as file:
            file.write(cookies)

    except Exception as e:
        if os.path.exists(USER_DATA):
            shutil.rmtree(USER_DATA)

        print(
            f"更新cookie失败: 可能是登录状态失效或 chromedriver 版本不匹配造成的, 错误信息: {e}"
        )
        exit()


if __name__ == "__main__":
    upd_cookie(manual=True)
