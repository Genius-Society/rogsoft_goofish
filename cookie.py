import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    for cookie in cookies:
        cookie_list.append(cookie["name"] + "=" + cookie["value"])

    return "; ".join(cookie_list)


def upd_cookie(manual=False):
    driver = init_chrome(vision=manual)
    driver.get("https://space.bilibili.com")
    cookies = list2str(driver.get_cookies())
    with open("cookie.txt", "w", encoding="utf-8") as file:
        file.write(cookies)


if __name__ == "__main__":
    upd_cookie(manual=True)
