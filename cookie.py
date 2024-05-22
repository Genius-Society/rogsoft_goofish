import os
import shutil
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import download_file, unzip_file
from smtp import send_email

USER_DATA = "user_data"
CHROME = "chrome-win64"
CHROME_URL = f"https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.76/win64/{CHROME}.zip"


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
        cookies = list2str(driver.get_cookies())
        with open("cookie.txt", "w", encoding="utf-8") as file:
            file.write(cookies)

    except Exception as e:
        if os.path.exists(USER_DATA):
            shutil.rmtree(USER_DATA)

        send_email(
            "可能是登录状态失效或 chromedriver 版本不匹配造成的",
            subject="更新cookie失败",
            title=f"错误信息：{e}",
        )
        exit()


if __name__ == "__main__":
    upd_cookie(manual=True)
