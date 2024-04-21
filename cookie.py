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


driver = init_chrome(vision=True)
driver.get("https://space.bilibili.com/30620472")
cookies = driver.get_cookies()
# for cookie in cookies:
#     print(cookie["name"] + ": " + cookie["value"])
with open("cookie.txt", "w", encoding="utf-8") as file:
    file.write(cookies)
