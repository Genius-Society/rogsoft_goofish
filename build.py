import os
import hashlib
import requests
import subprocess


def rm_cr():
    print("CRLF 转 LF")
    subprocess.run(
        [
            "bash",
            "-c",
            r"find './' -type f -name '*.sh' -exec sed -i 's/\r$//' {} \;",
        ],
        check=True,
    )


def download_file(
    url="https://github.com/Mxucc/xianyu-super-butler/archive/refs/heads/main.zip",
    save_path="./goofish/bin/main.zip",
):
    r = requests.get(url, stream=True)
    total = int(r.headers.get("content-length", 0))
    done = 0
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r{done/total*100:.1f}%", end="")

    return save_path


def calculate_md5(file_path: str):
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)

    return md5.hexdigest()


def pack(module_name: str):
    print("打包中...")
    output = f"{module_name}.tar.gz"
    intermediate = f"{module_name}.tar"
    subprocess.run(["7z", "a", "-ttar", intermediate, module_name], check=True)
    subprocess.run(["7z", "a", "-tgzip", output, intermediate], check=True)
    if os.path.exists(intermediate):
        os.remove(intermediate)
    else:
        raise FileNotFoundError(f"生成中间产物 {intermediate} 出错!")

    print(f"打包完成, 输出 {output}")
    return f"./{output}"


if __name__ == "__main__":
    try:
        rm_cr()
        zipath = download_file()
        md5 = calculate_md5(zipath)
        with open("./goofish/version", "w") as f:
            f.write(md5)

        pack("goofish")

    except Exception as e:
        print(f"打包出错: {e}")
