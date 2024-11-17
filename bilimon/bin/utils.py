import os
import zipfile
import requests
from tqdm import tqdm

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def read_txt(file_path="cookie.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        return str(content).strip()

    except FileNotFoundError:
        print(f"File not found: {file_path}")

    except Exception as e:
        print(f"Error reading file: {str(e)}")

    return ""


GLOBAL_COOKIE = read_txt()


def save_traitors(traitors: list, file_path="traitors.txt"):
    with open(file_path, "a", encoding="utf-8") as file:
        for url in traitors:
            file.write(f"{url}\n")


def download_file(url: str, folder_path="./"):
    # 确保文件夹存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 解析文件名
    file_name = url.split("/")[-1]

    # 文件的完整路径
    file_path = os.path.join(folder_path, file_name)

    # 下载文件
    response = requests.get(url, stream=True)
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

    print(f"文件已下载到：{file_path}")


def unzip_file(zip_file: str, extract_folder="./", rm_pkg=True):
    # 确保解压缩目录存在，如果不存在则创建
    if not os.path.exists(extract_folder):
        os.makedirs(extract_folder)

    # 打开压缩包
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        # 解压缩到指定目录
        zip_ref.extractall(extract_folder)

    print(f"文件已解压缩到：{extract_folder}")
    if rm_pkg:
        os.remove(zip_file)
