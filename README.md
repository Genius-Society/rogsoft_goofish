# bilibili-fans-monitor
[![Python application](https://github.com/monet-joe/bilibili-fans-monitor/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/monet-joe/bilibili-fans-monitor/actions/workflows/python-app.yml)

白嫖取关死妈

## 获取 cookie 方法
浏览器登陆B站待监控账号，在登陆状态下访问：

<https://api.bilibili.com/x/relation/followers?vmid=1>

右键审查元素 - 网络 - 名称中选择 `followers?vmid=1` - 标头 - Cookie:

将 SESSDATA=直到分号之前的内容复制(包括SESSDATA=本身) 粘贴到 cookie.txt 中

## 使用
```bash
git clone git@gitee.com:MuGeminorum/bilibili-fans-monitor.git
cd bilibili-fans-monitor
```

创建一个 start.bat 的快捷方式移至启动文件夹并双击打开
