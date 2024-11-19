#!/bin/sh

source /koolshare/scripts/base.sh
eval $(dbus export bilimon)
LOG_FILE=/tmp/upload/bilimon_log.txt
LOCK_FILE=/var/lock/bilimon.lock
alias echo_date='echo 【$(TZ=UTC-8 date -R +%Y年%m月%d日\ %X)】:'

set_lock() {
	exec 1000>"$LOCK_FILE"
	flock -x 1000
}

unset_lock() {
	flock -u 1000
	rm -rf "$LOCK_FILE"
}

sync_ntp() {
	# START_TIME=$(date +%Y/%m/%d-%X)
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

start_bilimon() {
	export PATH=$PATH:/opt/bin/
	mkdir -p "$bilimon_tmp"
	echo "$bilimon_cookie" >"$bilimon_tmp/cookie.txt"

	if [ "${bilimon_enable}" == "1" ]; then
		nohup python /koolshare/bilimon/bilimon.py \
			--clock 1 \
			--period "$bilimon_period" \
			--email "$bilimon_mail" \
			--smtp "$bilimon_smtp" \
			--tmp "$bilimon_tmp" \
			>/dev/null 2>&1 &

		echo_date "BiliMon插件启动完毕, 本窗口将在5s内自动关闭!"

	else
		stop
	fi
}

trigger_once() {
	export PATH=$PATH:/opt/bin/
	mkdir -p "$bilimon_tmp"
	echo "$bilimon_cookie" >"$bilimon_tmp/cookie.txt"
	nohup python /koolshare/bilimon/bilimon.py \
		--clock 0 \
		--period "$bilimon_period" \
		--email "$bilimon_mail" \
		--smtp "$bilimon_smtp" \
		--tmp "$bilimon_tmp" \
		>$LOG_FILE 2>&1 &
}

close_in_five() {
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
	# 关闭bilimon进程
	killall python
}

case $1 in
start)
	set_lock
	if [ "${bilimon_enable}" == "1" ]; then
		logger "[软件中心]: 启动BiliMon!"
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
		echo_date "BiliMon已经停止运行, 本窗口将再5s后关闭!" | tee -a $LOG_FILE
	fi
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;
trigger_once)
	set_lock
	trigger_once
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;
esac
