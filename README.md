# Bilibili relation monitor
[![license](https://img.shields.io/badge/license-Apache--2.0-99c711)](./LICENSE)
[![hf](https://img.shields.io/badge/huggingface-keep__spaces__alive-ffd21e.svg)](https://huggingface.co/spaces/kakamond/keep_spaces_alive)
[![ms](https://img.shields.io/badge/modelscope-bili__dark__tools-624aff.svg)](https://www.modelscope.cn/studios/kakamond/bili_dark_tools)

监控B站粉丝动向: 取关狗死全家! 推荐 UP 在 1K 粉以内时就开始使用本插件, 这样能不放过任何一条取关狗

![](./bilimon/res/icon-bilimon.png)

## Code download
```bash
git clone git@gitee.com:Genius-Society/bilimon.git
cd bilimon
```

## Environment
```bash
conda create -n py310 python=3.10 -y
conda activate py310
pip install -r ./bilimon/bin/requirements.txt
```

## Build
```bash
python build.py
# 将生成的 bilimon.tar.gz 包上传至软件中心离线安装页面进行安装
```

## Requirement
软件中心安装 Entware 插件并部署完成

## 手动获取 cookie 方法
1. 用 `VSCode` 打开工程, 选中 `cookie.py`;
2. 在 `cookie.py` 的 `#TODO:` 处打个断点;
3. 按 `F5` 调试 `.py` 文件, 弹出 `BiliBili` 登录页面;
4. 用手机 `APP` 扫码登录后点击继续使其运行完毕 (断点可保留, 首次获取过 cookie 以后可用非 debug 模式重刷)

注: 多账号切换获取 cookie 时推荐清理 `user_data` 文件夹而非登出, 否则会导致被登出的账号 cookie 失效

## 批量私信
- <https://www.modelscope.cn/studios/kakamond/bili_dark_tools>

## Thanks
- <https://github.com/koolshare/rogsoft>
- <https://nemo2011.github.io/bilibili-api>
- <https://github.com/Nemo2011/bilibili-api>