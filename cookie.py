import os
import shutil
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from smtp import send_email

userData = "user_data"


def init_chrome(vision=False, keep_alive=False):
    user_dir_name = f"{os.path.dirname(os.path.abspath(__file__))}/{userData}"
    if not os.path.exists(user_dir_name):
        os.makedirs(user_dir_name)

    chrome_options = Options()
    if not vision:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument(rf"user-data-dir={user_dir_name}")
    chrome_options.add_argument("--mute-audio")
    if keep_alive:
        chrome_options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=chrome_options)
    return driver


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
        if os.path.exists(userData):
            shutil.rmtree(userData)

        send_email(
            "可能是登录状态失效造成的", subject="更新cookie失败", title=f"错误信息：{e}"
        )
        exit()


if __name__ == "__main__":
    upd_cookie(manual=True)
