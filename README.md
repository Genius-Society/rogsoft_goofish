# bilibili-relation-monitor
[![license](https://img.shields.io/badge/license-Apache_2.0-99c711)](https://github.com/MuGemSt/bilimon/blob/master/LICENSE)

取关狗死全家！

## Environment
```bash
conda create -n py310 python=3.10 -y
conda activate py310
pip install -r requirements.txt
```

## Build
```bash
python build.py
```
将生成的 `bilimon.tar.gz` 包上传至软件中心离线安装页面进行安装

## 手动获取 cookie 方法
1. 用 `VSCode` 打开工程，选中 `cookie.py`;
2. 在 `cookie.py` 的 `#TODO:` 处打个断点;
3. 按 `F5` 运行 `.py` 文件，弹出 `BiliBili` 登录页面;
4. 用手机 `APP` 扫码登录后按 `F5` 使其运行完毕，断点可保留，之后用命令行以非 debug 模式运行。