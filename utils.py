import time
import math
import json
import random
import requests
from tqdm import tqdm
from smtp import send_email


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


userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
global_cookie = read_txt(file_path="../ONMP/bmonitor/cookie.txt")
if not global_cookie:
    print("Use default cookie path")
    global_cookie = read_txt()


def save_traitors(traitors: list, file_path="traitors.txt"):
    with open(file_path, "a") as file:
        for url in traitors:
            file.write(url + "\n")
