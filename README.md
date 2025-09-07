# WeMediaMon 自媒体监控插件
[![license](https://img.shields.io/badge/license-Apache--2.0-99c711)](./LICENSE)
[![hf](https://img.shields.io/badge/huggingface-WeMediaTools-ffd21e.svg)](https://huggingface.co/collections/Genius-Society/wemediatools-6899cafefc947c81ff14ddde)
[![ms](https://img.shields.io/badge/modelscope-bili__dark__tools-624aff.svg)](https://www.modelscope.cn/studios/kakamond/bili_dark_tools)

主要用于监控自媒体粉丝动向: 取关狗死全家! 推荐B站的UP在1K粉以内时就开始使用本插件, 这样能不放过任何一条取关狗

<a href="https://github.com/Genius-Society/wemediamon" target="_blank">
    <img src="./wemediamon/res/icon-wemediamon.png" style="width: 160px;">
</a>

## 代码下载
```bash
git clone git@gitee.com:Genius-Society/wemediamon.git
cd wemediamon
```

## 环境
```bash
conda create -n py311 python=3.11 -y
conda activate py311
pip install -r requirements.txt
```

## 打包
```bash
python build.py
# 将生成的 wemediamon.tar.gz 包上传至软件中心离线安装页面进行安装
```

## 依赖项
| 前置插件 (安装顺序自上而下) | 安装来源                                                                                           | 备注                                     | 必需  |
| :-------------------------- | :------------------------------------------------------------------------------------------------- | :--------------------------------------- | :---: |
| USB2JFFS                    | [KoolCenter 软件中心](http://192.168.50.1/Module_Softcenter.asp)                                   | 安装后需挂载                             |   ❌   |
| 虚拟内存                    | [KoolCenter 软件中心](http://192.168.50.1/Module_Softcenter.asp)                                   | 安装后需挂载                             |   ❌   |
| Entware                     | [KoolCenter 软件中心](http://192.168.50.1/Module_Softcenter.asp)                                   | 安装后需挂载                             |   ✔️   |
| 科学上网                    | [GitHub](https://github.com/hq450/fancyss?tab=readme-ov-file#%E6%8F%92%E4%BB%B6%E4%B8%8B%E8%BD%BD) | 推荐下载 lite 版 tar.gz 包并离线安装开启 |   ✔️   |

## 机型支持
在 asuswrt 为基础的固件上, WeMediaMon 插件目前仅支持 aarch64 架构的路由器, 具体如下:
- 部分及其未列出, 请根据 CPU 型号和支持软件中心与否自行判断
- 使用 WeMediaMon 建议配置 1G 及以上的虚拟内存, 特别是小内存的路由器

| 机型             | 内存  | CPU/SOC | 架构  | 核心  |  频率   | 插件支持 |
| :--------------- | :---- | :-----: | :---: | :---: | :-----: | :------: |
| RT-AC86U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |    ✔️     |
| GT-AC2900        | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |    ✔️     |
| RT-AX92U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |    ✔️     |
| GT-AC5300        | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| RT-AX88U         | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| GT-AX11000       | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| NetGear RAX80    | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| RT-AX68U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |    ✔️     |
| RT-AX86U         | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| GT-AXE11000      | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |    ✔️     |
| ZenWiFi_Pro_XT12 | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |    ✔️     |
| GT-AX6000        | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |    ✔️     |
| GT-AX11000_PRO   | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |    ✔️     |
| RT-AX86U_PRO     | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |    ✔️     |
| RAX50            | 512MB | BCM6750 | armv7 |   3   | 1.5 GHz |    ✔️     |
| RAX70            | 512MB | BCM6755 | armv7 |   4   | 1.5 GHz |    ✔️     |
| RT-AX56U         | 512MB | BCM6755 | armv7 |   4   | 1.5 GHz |    ✔️     |
| RT-AX56U_V2      | 256MB | BCM6755 | armv7 |   4   | 1.5 GHz |    ✔️     |
| RT-AX58U         | 512MB | BCM6750 | armv7 |   3   | 1.5 GHz |    ✔️     |
| RT-AX82U         | 512MB | BCM6750 | armv7 |   3   | 1.5 GHz |    ✔️     |
| TUF-AX3000       | 512MB | BCM6750 | armv7 |   3   | 1.5 GHz |    ✔️     |
| TUF-AX5400       | 512MB | BCM6750 | armv7 |   3   | 1.5 GHz |    ✔️     |
| ZenWiFi_XT8      | 512MB | BCM6755 | armv7 |   4   | 1.5 GHz |    ✔️     |
| ZenWiFi_XD4      | 256MB | BCM6755 | armv7 |   4   | 1.5 GHz |    ✔️     |
| TUF-AX3000_V2    | 512MB | BCM6756 | armv7 |   4   | 1.7GHz  |    ✔️     |
| RT-AX57          | 256MB | BCM6756 | armv7 |   4   | 1.7GHz  |    ✔️     |

## 手动获取cookie脚本
- 以B站为例
1. 用 `VSCode` 打开工程, 选中 `cookie.py`;
2. 在 `cookie.py` 的 `#TODO:` 处打个断点;
3. 按 `F5` 调试 `.py` 文件, 弹出 `BiliBili` 登录页面;
4. 用手机 `APP` 扫码登录后点击继续使其运行完毕 (断点可保留, 首次获取过 cookie 以后可用非 debug 模式重刷)
5. 弹出的 `cookie.txt` 中的内容即为要拷贝的 cookie

注: 多账号切换获取 cookie 时推荐清理 `user_data` 文件夹而非登出, 否则会导致被登出的账号 cookie 失效

## 致谢
- <https://github.com/koolshare/rogsoft>
- <https://nemo2011.github.io/bilibili-api>
- <https://github.com/Nemo2011/bilibili-api>