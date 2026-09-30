# 🐟 Goofish for asuswrt

<div align="center">

**闲鱼超级管家 - Koolcenter 软件中心插件版本**

[![Auto Release](https://github.com/Genius-Society/rogsoft_goofish/actions/workflows/auto-release.yml/badge.svg?branch=main)](https://github.com/Genius-Society/rogsoft_goofish/actions/workflows/auto-release.yml)
[![sf](https://img.shields.io/badge/archive-SourceForge-ff6600.svg)](https://sourceforge.net/projects/rogsoft-goofish/files)
[![GitHub](https://img.shields.io/badge/GitHub-Mxucc%2Fxianyu--super--butler-blue?logo=github)](https://github.com/Mxucc/xianyu-super-butler)
[![license](https://img.shields.io/github/license/Genius-Society/rogsoft_goofish.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)

基于 [Mxucc/xianyu-super-butler](https://github.com/Mxucc/xianyu-super-butler) 二次开发 · 路由部署 · 持续更新

</div>

---

## 📸 界面预览

### 插件图标 ICO

![](./goofish/res/icon-goofish.png)

### 工作台 Dashboard

![Dashboard 界面](https://github.com/Mxucc/xianyu-super-butler/raw/main/static/uploads/images/1.png)

### 订单管理 Orders

![订单管理](https://github.com/Mxucc/xianyu-super-butler/raw/main/static/uploads/images/2.png)

### 补发功能 - 立即发货

![补发功能-发货方式选择](https://github.com/Mxucc/xianyu-super-butler/raw/main/static/uploads/images/3.png) ![补发功能-发货中](https://github.com/Mxucc/xianyu-super-butler/raw/main/static/uploads/images/4.png)

---

## 📖 简介

闲鱼超级管家 - Koolcenter 软件中心插件版本是在 [xianyu-auto-reply](https://github.com/Mxucc/xianyu-super-butler) 基础上的二次开发版本，部署到华硕路由器 Koolcenter 版 Merlin 固件，让闲鱼店铺管理更加高效便捷。

---

### 前置插件
在 KoolCenter 软件中心即可安装并挂载, 安装顺序自上而下:
- USB2JFFS
- 虚拟内存
- 科学上网 lite

### 机型支持
在 asuswrt 为基础的固件上, goofish 插件目前仅支持 aarch64 架构的路由器, 具体如下:
- 部分及其未列出, 请根据 CPU 型号和支持软件中心与否自行判断
- 使用 goofish 建议配置 1G 及以上的虚拟内存, 特别是小内存的路由器

| 机型             | 内存  | CPU/SOC | 架构  | 核心  |  频率   |
| :--------------- | :---- | :-----: | :---: | :---: | :-----: |
| RT-AC86U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |
| GT-AC2900        | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |
| RT-AX92U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |
| GT-AC5300        | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| RT-AX88U         | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| GT-AX11000       | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| NetGear RAX80    | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| RT-AX68U         | 512MB | BCM4906 | armv8 |   2   | 1.8 GHz |
| RT-AX86U         | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| GT-AXE11000      | 1GB   | BCM4908 | armv8 |   4   | 1.8 GHz |
| ZenWiFi_Pro_XT12 | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |
| GT-AX6000        | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |
| GT-AX11000_PRO   | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |
| RT-AX86U_PRO     | 1GB   | BCM4912 | armv8 |   4   | 2.0GHz  |

## ⭐ 核心功能

### 智能回复
- 🤖 关键词匹配回复
- 🧠 AI 智能议价（支持自定义折扣规则）
- 📝 默认回复配置
- 🛍️ 商品专属回复

### 自动发货
- 🚚 支持多规格商品
- ⏰ 延时发货设置
- 🎫 卡券管理
- 📋 发货规则配置

### 订单管理
- 📦 订单列表查看
- 🔄 批量刷新（并发处理）
- 🔍 订单详情查看
- 📮 收货人信息管理
- ✅ 订单状态更新

### 账号管理
- 📱 多账号支持
- 🔐 扫码/密码登录
- 🍪 Cookie 手动输入
- ⚡ 账号启用/禁用
- 🤖 AI 议价配置

### 其他功能
- 📊 数据统计与趋势分析
- 📄 Excel 批量导入导出
- 🔍 商品搜索
- 👥 多用户权限管理
- ✨ 基本解决滑块验证失败问题，成功率 99%

---

### 首次使用

1. **登录账号** - 访问 http://router.asus.com:8080 登录管理员账号
2. **添加闲鱼账号** - 支持扫码登录、密码登录、手动输入Cookie
3. **配置关键词** - 为每个账号配置自动回复关键词和AI智能议价
4. **开始使用** - 系统会自动监听闲鱼消息并自动回复、自动发货

---

## 🏗️ 技术栈
**插件：** HTML · CSS · JavaScript · jQuery · Shell · Python 3.11

**后端：** FastAPI · Python 3.11+ · SQLite · Playwright · WebSocket · Asyncio

**前端：** React 18 · TypeScript · Vite · Tailwind CSS · Framer Motion · Zustand

**性能优化：** 浏览器实例池 · 并发处理 · 智能缓存

---

## 💻 开发维护
### 代码下载
```bash
git clone git@github.com:Genius-Society/rogsoft_goofish.git
cd rogsoft_goofish
```

### 环境
```bash
conda create -n py311 python=3.11 -y
conda activate py311
```

### Windows 上打包
```bash
# 要先将 git bash 和 7z 的环境变量配置好重启
python build.py
```

---

## 📄 开源协议

[MIT License](https://opensource.org/licenses/MIT)

> ⚠️ **免责声明**
>
> 本项目仅供学习研究使用，严禁用于商业用途！
>
> 使用本项目时请遵守相关法律法规，因使用本项目而产生的一切后果由使用者自行承担。

---