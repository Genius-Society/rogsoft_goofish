# 🐟 Goofish for asuswrt

**闲鱼管理系统 - Koolcenter 软件中心插件版本**

[![Auto Release](https://github.com/Genius-Society/rogsoft_goofish/actions/workflows/auto-release.yml/badge.svg?branch=main)](https://github.com/Genius-Society/rogsoft_goofish/actions/workflows/auto-release.yml)
[![sf](https://img.shields.io/badge/archive-SourceForge-ff6600.svg)](https://sourceforge.net/projects/rogsoft-goofish/files)
[![GitHub](https://img.shields.io/badge/GitHub-GuDong2003/xianyu--auto--reply--fix-blue?logo=github)](https://github.com/GuDong2003/xianyu-auto-reply-fix)
[![license](https://img.shields.io/github/license/Genius-Society/rogsoft_goofish.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)

基于 [GuDong2003/xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix) 二次开发 · 路由部署 · 持续更新

---

## 📸 插件图标 ICO

![](./goofish/res/icon-goofish.png)

## 📖 简介

闲鱼超级管家 - Koolcenter 软件中心插件版本是在 [xianyu-auto-reply](https://github.com/GuDong2003/xianyu-auto-reply-fix) 基础上的二次开发版本，部署到华硕路由器 Koolcenter 版 Merlin 固件，让闲鱼店铺管理更加高效便捷。

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

## ✨ 核心特性

- **多用户系统**：支持注册登录、邮箱验证、图形验证码、权限控制和用户数据隔离。
- **多账号管理**：每个用户可管理多个闲鱼账号，支持独立启停、状态查看和 Cookie 维护。
- **智能回复**：支持关键词回复、默认回复、指定商品回复、图片关键词和 AI 自动回复。
- **自动发货**：支持文本、批量数据、API、图片等发货方式，并提供防重复处理能力。
- **商品管理**：自动收集商品信息，支持商品详情、规格配置和数据去重。
- **运营协同**：提供订单管理、通知渠道、消息通知、在线客服等后台运营能力。
- **监控维护**：支持实时日志、健康检查、安全统计、系统统计和日志文件轮转。
- **容器化部署**：支持本地运行、Docker Compose 和多架构构建。

---

### 首次使用

1. **登录账号** - 访问 http://router.asus.com:8090 登录管理员账号
2. **添加闲鱼账号** - 支持扫码登录、密码登录、手动输入Cookie
3. **配置关键词** - 为每个账号配置自动回复关键词和AI智能议价
4. **开始使用** - 系统会自动监听闲鱼消息并自动回复、自动发货

---

## 🏗️ 技术栈

- **插件**：HTML · CSS · JavaScript · jQuery · Shell · Python 3.11
- **后端框架**：FastAPI + Uvicorn + Python 3.11+ 异步编程
- **数据库**：SQLite 3 + 多用户数据隔离 + 自动迁移
- **前端**：Bootstrap 5 + Vanilla JavaScript + Chart.js
- **通信协议**：REST API + WebSocket + SSE
- **自动化能力**：Playwright + DrissionPage
- **部署方式**：Docker + Docker Compose + Nginx（可选）
- **日志系统**：Loguru + 文件轮转 + 实时收集

```text
┌─────────────────────────────────────────┐
│       Web 界面 (FastAPI + Static)        │
│          用户管理 + 功能界面               │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│             CookieManager               │
│           多账号任务与状态管理             │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│          XianyuLive (多实例)             │
│        WebSocket 连接 + 消息处理          │
└──────────────┬──────────────┬───────────┘
               │              │
┌──────────────▼───────┐ ┌────▼──────────────┐
│    AIReplyEngine     │ │ FileLogCollector  │
│     AI 回复与上下文    │ │   实时日志与统计    │
└──────────────┬───────┘ └────┬──────────────┘
               │              │
┌──────────────▼──────────────▼───────────┐
│              SQLite 数据库               │
│      用户数据 + 商品信息 + 配置数据         │
└─────────────────────────────────────────┘
```

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