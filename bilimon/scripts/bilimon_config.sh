#!/bin/sh

source /koolshare/scripts/base.sh
eval $(dbus export bilimon)
LOG_FILE=/tmp/upload/bilimon_log.txt
LOCK_FILE=/var/lock/bilimon.lock
alias echo_date='echo 【$(TZ=UTC-8 date -R +%Y年%m月%d日\ %X)】:'
export PATH=$PATH:/opt/bin/

set_lock() {
	exec 1000>"$LOCK_FILE"
	flock -x 1000
}

unset_lock() {
	flock -u 1000
	rm -rf "$LOCK_FILE"
}

sync_ntp() {
	echo_date "尝试从ntp服务器: ntp1.aliyun.com 同步时间..."
	ntpclient -h ntp1.aliyun.com -i3 -l -s >/tmp/ali_ntp.txt 2>&1
	SYNC_TIME=$(cat /tmp/ali_ntp.txt | grep -E "\[ntpclient\]" | grep -Eo "[0-9]+" | head -n1)
	if [ -n "${SYNC_TIME}" ]; then
		SYNC_TIME=$(date +%Y/%m/%d-%X @${SYNC_TIME})
		echo_date "完成!时间同步为: ${SYNC_TIME}"
	else
		echo_date "时间同步失败, 跳过!"
	fi
}

fun_wan_start() {
	if [ "${bilimon_enable}" == "1" ]; then
		if [ ! -L "/koolshare/init.d/M71bilimon.sh" ]; then
			echo_date "添加开机启动..."
			ln -sf /koolshare/scripts/bilimon_config.sh /koolshare/init.d/M71bilimon.sh
		fi
	else
		if [ -L "/koolshare/init.d/M71bilimon.sh" ]; then
			echo_date "删除开机启动..."
			rm -rf /koolshare/init.d/M71bilimon.sh >/dev/null 2>&1
		fi
	fi
}

# 安装\检查运行环境
install_env() {
	sed -i "s|^src/gz.*|src/gz entware https://mirrors.bfsu.edu.cn/entware/aarch64-k3.10|" /opt/etc/opkg.conf
	opkg update
	opkg install python3-pip
	python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
	pip install -r /koolshare/bilimon/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
}

# 自动修复路由器重启导致的盘符变化
fix_path() {
	for dir in /mnt/*/; do
		if [ -d "$dir" ]; then
			sub=$(echo "$1" | cut -d'/' -f4-)
			if [ ! -z $sub ] [ -d "$dir$sub" ]; then
				echo "$dir$sub"
			fi
		fi
	done
}

start_bilimon() {
	# 检查入参
	if [[ -z $bilimon_period ]]; then
		close_in_five "请输入有效周期!"
	fi
	if [[ -z $bilimon_mail ]]; then
		close_in_five "请输入有效邮箱!"
	fi
	if [[ -z $bilimon_smtp ]]; then
		close_in_five "请输入有效SMTP密钥!"
	fi
	if [[ -z $bilimon_cookie ]]; then
		close_in_five "请输入有效B站cookie!"
	fi
	if [ -z $bilimon_tmp ]; then
		close_in_five "请输入有效缓存路径!"
	fi

	if [ ! -d $bilimon_tmp ]; then
		# 修复重启导致的缓存目录盘符变化
		echo_date "检查缓存路径..."
		fixed_bilimon_tmp=$(fix_path $bilimon_tmp)
		if [ $fixed_bilimon_tmp != $bilimon_tmp ] && [ -d $fixed_bilimon_tmp ]; then
			bilimon_tmp=$fixed_bilimon_tmp
			dbus set bilimon_tmp=$bilimon_tmp
			echo_date "缓存路径已自动修复!"
		else
			close_in_five "请输入有效缓存路径!"
		fi
	fi

	# 插件开启的时候同步一次时间
	if [ "${bilimon_enable}" == "1" -a -n "$(which ntpclient)" ]; then
		sync_ntp
	fi

	# 检查运行环境
	echo_date "检查 Entware 环境..."
	if [ -d "/opt" ]; then
		install_env
		echo_date "Entware 环境可用!"
	else
		close_in_five "Entware 环境不可用, 请修复!"
	fi

	# 加载B站cookie
	if [ ! -f "$bilimon_tmp/cookie.txt" ] || [ $(<"$bilimon_tmp/cookie.txt") != "$bilimon_cookie" ]; then
		echo "$bilimon_cookie" >"$bilimon_tmp/cookie.txt"
	fi

	# 开启周期监控
	nohup python /koolshare/bilimon/bilimon.py \
		--clock 1 \
		--period "$bilimon_period" \
		--email "$bilimon_mail" \
		--smtp "$bilimon_smtp" \
		--tmp "$bilimon_tmp" \
		>>"/tmp/upload/bilimon_run_log.txt" 2>&1 &

	echo_date "BiliMon 插件启动完毕, 本窗口将在 5s 内自动关闭!"
}

trigger_once() {
	# 检查入参
	if [[ -z $bilimon_period ]]; then
		echo_date "请输入有效周期!XU6J03M6"
		return
	fi
	if [[ -z $bilimon_mail ]]; then
		echo_date "请输入有效邮箱!XU6J03M6"
		return
	fi
	if [[ -z $bilimon_smtp ]]; then
		echo_date "请输入有效SMTP密钥!XU6J03M6"
		return
	fi
	if [[ -z $bilimon_cookie ]]; then
		echo_date "请输入有效B站cookie!XU6J03M6"
		return
	fi
	if [ -z $bilimon_tmp ] || [ ! -d $bilimon_tmp ]; then
		echo_date "请输入有效缓存路径!XU6J03M6"
		return
	fi

	# 检查运行环境
	echo_date "检查 Entware 环境..."
	if [ -d "/opt" ]; then
		install_env
		echo_date "Entware 环境可用!"
	else
		echo_date "Entware 环境不可用, 请修复!XU6J03M6"
		return
	fi

	# 加载B站cookie
	# if [ ! -f "$bilimon_tmp/cookie.txt" ] || [ $(<"$bilimon_tmp/cookie.txt") != "$bilimon_cookie" ]; then
	# 	echo "$bilimon_cookie" >"$bilimon_tmp/cookie.txt"
	# fi

	# 开启单次触发
	nohup python /koolshare/bilimon/bilimon.py \
		--clock 0 \
		--period "$bilimon_period" \
		--email "$bilimon_mail" \
		--smtp "$bilimon_smtp" \
		--tmp "$bilimon_tmp" \
		>>$LOG_FILE 2>&1 &
}

close_in_five() {
	dbus set bilimon_enable=0
	echo_date $1
	echo_date "插件将在5秒后自动关闭!!"
	local i=5
	while [ $i -ge 0 ]; do
		sleep 1
		echo_date $i
		let i--
	done
	stop
	echo_date "插件已关闭!!"
	unset_lock
	exit
}

stop() {
	# 关闭监控进程
	pids=$(ps | grep "python" | grep "bilimon.py" | awk '{print $1}')
	if [ ! -z $pids ]; then
		echo_date "关闭监控进程..."
		for pid in $pids; do
			kill "$pid"
		done
	fi
	fun_wan_start
}

case $1 in
start)
	set_lock
	if [ "${bilimon_enable}" == "1" ]; then
		logger "[软件中心]: 启动 BiliMon !"
		start_bilimon
	fi
	unset_lock
	;;
restart)
	set_lock
	if [ "${bilimon_enable}" == "1" ]; then
		stop
		start_bilimon
	fi
	unset_lock
	;;
stop)
	set_lock
	stop
	unset_lock
	;;
esac

case $2 in
web_submit)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	if [ "${bilimon_enable}" == "1" ]; then
		stop | tee -a $LOG_FILE
		start_bilimon | tee -a $LOG_FILE
	else
		stop | tee -a $LOG_FILE
		echo_date "BiliMon 已经停止运行, 本窗口将再 5s 后关闭!" | tee -a $LOG_FILE
	fi
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;
trigger_once)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	trigger_once | tee -a $LOG_FILE
	unset_lock
	;;
watch_dogs)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	if [[ -f "$bilimon_tmp/traitors.txt" ]]; then
		awk '{print "https://space.bilibili.com/" $0}' "$bilimon_tmp/traitors.txt" | tee -a $LOG_FILE
	else
		echo_date "当前狗库为空!" | tee -a $LOG_FILE
	fi
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;
esac

# 重启自启时触发
bilimon_enable=$(dbus get bilimon_enable)
if [ "$bilimon_enable" == "1" ] && [ -z "$(ps w | grep python | grep -v grep)" ]; then
	set_lock
	true >$LOG_FILE
	# 初始化变量
	bilimon_period=$(dbus get bilimon_period)
	bilimon_mail=$(dbus get bilimon_mail)
	bilimon_smtp=$(dbus get bilimon_smtp)
	bilimon_tmp=$(dbus get bilimon_tmp)
	# 开启 BiliMon
	start_bilimon | tee -a $LOG_FILE
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
fi
