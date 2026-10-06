#!/bin/sh

source /koolshare/scripts/base.sh
eval $(dbus export goofish)
MON_LOG=/tmp/upload/goofish_log.txt
RUN_LOG=/tmp/upload/goofish_run_log.txt
LOCK_FILE=/var/lock/goofish.lock
alias echo_date='echo 【$(TZ=UTC-8 date -R +%Y年%m月%d日\ %X)】:'
export PATH=$PATH:/opt/bin/

# 文件保护锁
set_lock() {
	exec 1000>"${LOCK_FILE}"
	flock -x 1000
}

unset_lock() {
	flock -u 1000
	rm -rf "${LOCK_FILE}"
}

# 插件开启的时候同步一次时间
sync_ntp() {
	if [ "${goofish_enable}" == "1" -a -n "$(which ntpclient)" ]; then
		echo_date "尝试从ntp服务器: ntp1.aliyun.com 同步时间..."
		ntpclient -h ntp1.aliyun.com -i3 -l -s >/tmp/ali_ntp.txt 2>&1
		SYNC_TIME=$(cat /tmp/ali_ntp.txt | grep -E "\[ntpclient\]" | grep -Eo "[0-9]+" | head -n1)
		if [ -n "${SYNC_TIME}" ]; then
			SYNC_TIME=$(date +%Y/%m/%d-%X @${SYNC_TIME})
			echo_date "完成!时间同步为: ${SYNC_TIME}"
		else
			echo_date "时间同步失败, 跳过!"
		fi
	fi
}

# 添加/删除开机启动
fun_wan_start() {
	if [ "${goofish_enable}" == "1" ]; then
		if [ ! -L "/koolshare/init.d/M71goofish.sh" ]; then
			echo_date "添加开机启动..."
			ln -sf /koolshare/scripts/goofish_config.sh /koolshare/init.d/M71goofish.sh
		fi
	else
		if [ -L "/koolshare/init.d/M71goofish.sh" ]; then
			echo_date "删除开机启动..."
			rm -rf /koolshare/init.d/M71goofish.sh >/dev/null 2>&1
		fi
	fi
}

# 安装/检查运行环境
fix_env() {
	echo "修复 Python 运行环境..."
	sed -i "s|^src/gz.*|src/gz entware https://mirrors.bfsu.edu.cn/entware/aarch64-k3.10|" /opt/etc/opkg.conf
	opkg update
	opkg install python3-pip node node-npm
	npm install -g pnpm
	python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
	pip install --cache-dir /koolshare/goofish/.cache -r /koolshare/goofish/xianyu-super-butler-main/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
	echo "修复完毕! 当前 pypi 列表如下:"
	pip list
	rm -rf /koolshare/goofish/.cache
}

# 失败自动关闭(仅供运行日志使用)
close_with_echo() {
	dbus set goofish_enable=0
	echo_date $1
	stop
	echo_date "插件已关闭!!"
	unset_lock
	exit
}

load_params() {
	# 加载dbus变量
	goofish_enable=$(dbus get goofish_enable)
	goofish_pass=$(dbus get goofish_pass)
}

# 检查入参
check_params() {
	# 检查必填入参
	if [[ -z "${goofish_pass}" ]]; then
		close_with_echo "请输入有效密码!"
	else
		cd /koolshare/goofish/xianyu-super-butler-main
		python3 init_admin.py --pass "${goofish_pass}"
	fi
}

# 检查运行环境
check_env() {
	echo_date "检查 Entware 环境..."
	if [ ! -d "/opt" ]; then
		close_with_echo "Entware 环境不可用, 请先安装 Entware 插件!"
	else
		echo_date "Entware 环境可用, 执行脚本中..."
	fi
}

# 开启监控
start_goofish() {
	check_params
	sync_ntp
	check_env
	cd /koolshare/goofish/xianyu-super-butler-main
	# 开启周期监控
	nohup python -u Start.py >>"$MON_LOG" 2>&1 &
}

# 关闭监控进程
stop() {
	load_params
	pids=$(ps | grep "python" | grep "Start.py" | awk '{print $1}')
	if [[ -n "$pids" ]]; then
		echo_date "关闭监控进程..."
		for pid in $pids; do
			kill "$pid"
		done
	fi
	fun_wan_start
}

apply() {
	stop
	if [ "${goofish_enable}" == "1" ]; then
		start_goofish
		echo_date "goofish 插件启动完毕, 本窗口将在 5s 内自动关闭!"
	else
		echo_date "goofish 已经停止运行, 本窗口将再 5s 后关闭!"
	fi
}

check_proxy() {
	local count=0
	echo_date "等待代理网络连通..."
	until ping -c 1 huggingface.co >/dev/null 2>&1; do
		sleep 1
		count=$((count + 1))
		if [ "$count" -ge 30 ]; then
			echo_date "代理网络仍不可达, 请检查【科学上网】插件, 脚本关闭!"
			exit 1
		fi
	done
	echo_date "已 ping 通, 继续执行后续命令"
}

update() {
	local wget_proxy=""
	local curl_proxy=""
	local status=$(curl -x http://127.0.0.1:23456 -s -o /dev/null -w "%{http_code}" https://github.com)
	if [ "${status}" == "200" ]; then
		wget_proxy="-e use_proxy=yes -e https_proxy=http://127.0.0.1:23456"
		curl_proxy="-x http://127.0.0.1:23456"
	fi
	local latest_md5=$(curl ${curl_proxy} -s https://api.github.com/repos/Genius-Society/rogsoft_goofish/releases/latest | python3 -c "import sys,json;print(json.load(sys.stdin).get('body',''))")
	if [ $(dbus get goofish_md5) == "${latest_md5}" ]; then
		echo_date "goofish 已是最新版本, 无需更新!"
	else
		local latest_ver=$(curl ${curl_proxy} -s https://api.github.com/repos/Genius-Society/rogsoft_goofish/releases/latest | python3 -c "import sys,json;print(json.load(sys.stdin).get('tag_name',''))")
		if wget --no-hsts -c -t 0 -T 30 ${wget_proxy} \
			-O /tmp/upload/goofish.tar.gz \
			"https://github.com/Genius-Society/rogsoft_goofish/releases/download/${latest_ver}/goofish.tar.gz" 2>&1; then
			if [ -s /tmp/upload/goofish.tar.gz ]; then
				dbus set soft_name=goofish.tar.gz
				unset_lock
				echo_date "插件下载成功, 新插件安装中..."
				sh /koolshare/scripts/ks_tar_install.sh >/dev/null 2>&1
				echo_date "goofish 插件已更新!"
			else
				echo_date "下载文件为空, 更新失败!"
			fi
		else
			echo_date "插件下载失败!"
		fi
	fi
}

reset_pass() {
	echo_date "正在重置 admin 密码..."
	if [[ -z "${goofish_pass}" ]]; then
		echo_date "请输入有效密码!"
	else
		cd /koolshare/goofish/xianyu-super-butler-main
		python3 init_admin.py --pass "${goofish_pass}"
	fi
}

# 自启/重启时触发开启 goofish
if [[ $# -eq 0 || $# -eq 1 ]]; then
	set_lock
	stop
	if [[ "${goofish_enable}" == "1" ]]; then
		check_proxy
		start_goofish
	fi
	unset_lock

# 网页传参命令触发
elif [ $# -eq 2 ]; then
	if [ "$2" = "FORCE_STOP" ]; then
		http_response "$1"
		stop >/dev/null 2>&1
		echo XU6J03M6
		exit 0
	fi

	set_lock
	true >$RUN_LOG
	http_response "$1"

	case $2 in
	WEB_SUBMIT)
		apply | tee -a $RUN_LOG
		;;

	FIX_ENV)
		fix_env | tee -a $RUN_LOG
		;;

	CHK_UPD)
		update | tee -a $RUN_LOG
		;;

	RESET_PASS)
		reset_pass | tee -a $RUN_LOG
		;;

	esac

	unset_lock
	echo XU6J03M6 | tee -a $RUN_LOG
fi
