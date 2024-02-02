# bilibili-relation-monitor
[![Python application](https://github.com/MuGeminorum/bilibili-relation-monitor/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/MuGeminorum/bilibili-relation-monitor/actions/workflows/python-app.yml)

白嫖取关4🐎

## 获取 cookie 方法
浏览器登陆B站待监控账号，在登陆状态下访问：

<https://api.bilibili.com/x/relation/followers?vmid=1>

右键审查元素 - 网络 - 名称中选择 `followers?vmid=1` - 标头 - Cookie:

将 Cookie 中的内容整体粘贴到 cookie.txt 中

## 使用
```bash
git clone git@gitee.com:MuGeminorum/bilibili-relation-monitor.git
cd bilibili-relation-monitor
```

创建一个 start.bat 的快捷方式移至启动文件夹并双击打开
