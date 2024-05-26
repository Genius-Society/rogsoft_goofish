import os
import shutil
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils import download_file, unzip_file
from smtp import send_email
import gradio as gr

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


DRIVER = init_chrome()


def list2str(cookies):
    cookie_list = []
    for cookie in tqdm(cookies, desc="parsing cookies..."):
        cookie_list.append(cookie["name"] + "=" + cookie["value"])

    return "; ".join(cookie_list)


def upd_cookie():
    global DRIVER
    try:
        DRIVER.get("https://space.bilibili.com")
        cookies = list2str(DRIVER.get_cookies())
        with open("cookie.txt", "w", encoding="utf-8") as file:
            file.write(cookies)

        DRIVER.quit()
        return cookies

    except Exception as e:
        if os.path.exists(USER_DATA):
            shutil.rmtree(USER_DATA)

        send_email(
            "可能是登录状态失效或 chromedriver 版本不匹配造成的",
            subject="更新cookie失败",
            title=f"错误信息：{e}",
        )
        exit()


def save_base64_image(base64_string: str, file_path=f"{USER_DATA}/qrcode.jpg"):
    if os.path.exists(file_path):
        os.remove(file_path)

    import base64

    base64_data = base64_string.split(",")[1]

    # 解码 base64 字符串
    image_data = base64.b64decode(base64_data)

    # 将解码后的数据写入 JPG 文件
    with open(file_path, "wb") as f:
        f.write(image_data)

    return file_path


def browse(url):
    global DRIVER

    DRIVER.get(url)
    img = DRIVER.find_element(By.CSS_SELECTOR, 'img[alt="Scan me!"]')
    base64_img = img.get_attribute("src")
    return save_base64_image(base64_img)


def inference():
    return upd_cookie(scanned=(DRIVER != None))


if __name__ == "__main__":
    with gr.Blocks() as demo:
        with gr.Row():
            gr.Interface(
                fn=browse,
                inputs=gr.Textbox(
                    label="输入网址",
                    value="https://space.bilibili.com",
                ),
                outputs=gr.Image(label="扫码登陆", type="filepath"),
                allow_flagging=False,
            )

        with gr.Row():
            gr.Interface(
                fn=inference,
                inputs=None,
                outputs=gr.TextArea(),
                allow_flagging=False,
            )

    demo.launch(server_name="0.0.0.0")
