# bilibili-relation-monitor
[![Python application](https://github.com/MuGeminorum/bilibili-relation-monitor/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/MuGeminorum/bilibili-relation-monitor/actions/workflows/python-app.yml)

白嫖取关4🐎

## 手动获取 cookie 方法
浏览器登陆B站待监控账号，在登陆状态下访问：

<https://api.bilibili.com/x/relation/followers?vmid=1>

右键审查元素 - 网络 - 名称中选择 `followers?vmid=1` - 标头 - Cookie:

将 Cookie 中的内容整体粘贴到 cookie.txt 中

## 使用
在安装了 chrome 浏览器的 windows 10 x64 系统下运行：
```bash
pip install -r requirements.txt
```

之后下载项目工程：
```bash
git clone git@gitee.com:MuGeminorum/bilibili-relation-monitor.git
cd bilibili-relation-monitor
```

获取登录状态后，创建一个 start.bat 的快捷方式移至启动文件夹并双击打开

## 获取登录状态的方法
1. 用 `VSCode` 打开工程，选中 `./bmonitor/cookie.py`;
2. 在 `cookie.py` 的 `line 40` 处打个断点;
3. 按 `F5` 运行 `.py` 文件，弹出 `BiliBili` 登录页面;
4. 用手机 `APP` 扫码登录后按 `F5` 使其运行完毕，再释放断点;