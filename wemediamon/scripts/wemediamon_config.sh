#!/bin/sh

source /koolshare/scripts/base.sh
eval $(dbus export wemediamon)
LOG_FILE=/tmp/upload/wemediamon_log.txt
RUN_LOG=/tmp/upload/wemediamon_run_log.txt
LOCK_FILE=/var/lock/wemediamon.lock
alias echo_date='echo 【$(TZ=UTC-8 date -R +%Y年%m月%d日\ %X)】:'
export PATH=$PATH:/opt/bin/

set_lock() {
	exec 1000>"${LOCK_FILE}"
	flock -x 1000
}

unset_lock() {
	flock -u 1000
	rm -rf "${LOCK_FILE}"
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
	if [ "${wemediamon_enable}" == "1" ]; then
		if [ ! -L "/koolshare/init.d/M71wemediamon.sh" ]; then
			echo_date "添加开机启动..."
			ln -sf /koolshare/scripts/wemediamon_config.sh /koolshare/init.d/M71wemediamon.sh
		fi
	else
		if [ -L "/koolshare/init.d/M71wemediamon.sh" ]; then
			echo_date "删除开机启动..."
			rm -rf /koolshare/init.d/M71wemediamon.sh >/dev/null 2>&1
		fi
	fi
}

# 安装\检查运行环境
install_env() {
	echo "修复 Python 运行环境..."
	sed -i "s|^src/gz.*|src/gz entware https://mirrors.bfsu.edu.cn/entware/aarch64-k3.10|" /opt/etc/opkg.conf
	opkg update
	opkg install python3-pip
	python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
	pip install --cache-dir /koolshare/wemediamon/.cache -r /koolshare/wemediamon/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
	echo "修复完毕! 当前 pypi 列表如下:"
	pip list
	rm -rf /koolshare/wemediamon/.cache
}

check_params() {
	# 检查入参
	if [[ -z "${wemediamon_period}" ]]; then
		close_in_five "请输入有效周期!"
	fi
	if [[ -z "${wemediamon_email}" ]]; then
		close_in_five "请输入有效邮箱!"
	fi
	if [[ -z "${wemediamon_smtp}" ]]; then
		close_in_five "请输入有效SMTP密钥!"
	fi
	if [ -z "${wemediamon_cache}" ]; then
		close_in_five "请输入有效缓存路径!"
	fi

	if [ "${wemediamon_bilimon}" == "1" ]; then
		if [[ -z "${wemediamon_bilick}" ]]; then
			close_in_five "请输入有效B站cookie!"
		fi
	else
		wemediamon_bilick=""
	fi

	if [ "${wemediamon_hfmon}" == "1" ]; then
		if [[ -z "${wemediamon_hftag}" ]]; then
			close_in_five "请输入有效抱脸用户名!"
		fi
	else
		wemediamon_hftag=""
	fi

	if [ "${wemediamon_gitmon}" == "1" ]; then
		if [[ -z "${wemediamon_gitags}" ]]; then
			close_in_five "请输入有效GitHub目标列表!"
		fi
	else
		wemediamon_gitags=""
	fi
}

start_wemediamon() {
	check_params

	# 插件开启的时候同步一次时间
	if [ "${wemediamon_enable}" == "1" -a -n "$(which ntpclient)" ]; then
		sync_ntp
	fi

	# 检查运行环境
	echo_date "检查 Entware 环境..."
	if [ ! -d "/opt" ]; then
		close_in_five "Entware 环境不可用, 请先安装 Entware 插件!"
	fi

	# 开启周期监控
	rm -rf $RUN_LOG
	nohup python /koolshare/wemediamon/wemediamon.py \
		--cmd "START_MONITOR" \
		--period "${wemediamon_period}" \
		--email "${wemediamon_email}" \
		--smtp "${wemediamon_smtp}" \
		--cache "${wemediamon_cache}" \
		--bilick "${wemediamon_bilick}" \
		--hftag "${wemediamon_hftag}" \
		--gitags "${wemediamon_gitags}" \
		>>$RUN_LOG 2>&1 &

	echo_date "WeMediaMon 插件启动完毕, 本窗口将在 5s 内自动关闭!"
}

trigger() {
	check_params

	# 检查运行环境
	echo_date "检查 Entware 环境..."
	if [ ! -d "/opt" ]; then
		echo_date "Entware 环境不可用, 请先安装 Entware 插件!XU6J03M6"
		return
	fi

	# 开启单次触发扫描
	nohup python /koolshare/wemediamon/wemediamon.py \
		--cmd $1 \
		--period "${wemediamon_period}" \
		--email "${wemediamon_email}" \
		--smtp "${wemediamon_smtp}" \
		--cache "${wemediamon_cache}" \
		--bilick "${wemediamon_bilick}" \
		--hftag "${wemediamon_hftag}" \
		--gitags "${wemediamon_gitags}" \
		>>$LOG_FILE 2>&1 &
}

close_in_five() {
	dbus set wemediamon_enable=0
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
	pids=$(ps | grep "python" | grep "wemediamon.py" | awk '{print $1}')
	if [ ! -z $pids ]; then
		echo_date "关闭监控进程..."
		for pid in $pids; do
			kill "${pid}"
		done
	fi
	fun_wan_start
}

case $1 in
start)
	set_lock
	if [ "${wemediamon_enable}" == "1" ]; then
		logger "[软件中心]: 启动 WeMediaMon !"
		start_wemediamon
	fi
	unset_lock
	;;

restart)
	set_lock
	if [ "${wemediamon_enable}" == "1" ]; then
		stop
		start_wemediamon
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
WEB_SUBMIT)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	if [ "${wemediamon_enable}" == "1" ]; then
		stop | tee -a $LOG_FILE
		start_wemediamon | tee -a $LOG_FILE
	else
		stop | tee -a $LOG_FILE
		echo_date "WeMediaMon 已经停止运行, 本窗口将再 5s 后关闭!" | tee -a $LOG_FILE
	fi
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;

FIX_ENV)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	install_env | tee -a $LOG_FILE
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;

SEE_BILI_BLACKS)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	if [[ -f "${wemediamon_cache}/bili_blacklist.txt" ]]; then
		awk '{print "https://space.bilibili.com/" $0}' "${wemediamon_cache}/bili_blacklist.txt" | tee -a $LOG_FILE
	else
		echo_date "当前狗库为空!" | tee -a $LOG_FILE
	fi
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
	;;

*)
	set_lock
	true >$LOG_FILE
	http_response "$1"
	trigger "$2" | tee -a $LOG_FILE
	unset_lock
	;;

esac

# 重启自启时触发
wemediamon_enable=$(dbus get wemediamon_enable)
if [ "${wemediamon_enable}" == "1" ] && [ -z "$(ps w | grep python | grep -v grep)" ]; then
	set_lock
	true >$LOG_FILE
	# 初始化变量
	wemediamon_period=$(dbus get wemediamon_period)
	wemediamon_email=$(dbus get wemediamon_email)
	wemediamon_smtp=$(dbus get wemediamon_smtp)
	wemediamon_cache=$(dbus get wemediamon_cache)
	wemediamon_bilimon=$(dbus get wemediamon_bilimon)
	wemediamon_bilick=$(dbus get wemediamon_bilick)
	wemediamon_hfmon=$(dbus get wemediamon_hfmon)
	wemediamon_hftag=$(dbus get wemediamon_hftag)
	wemediamon_gitmon=$(dbus get wemediamon_gitmon)
	wemediamon_gitags=$(dbus get wemediamon_gitags)
	wemediamon_cnblon=$(dbus get wemediamon_cnblon)
	wemediamon_itchion=$(dbus get wemediamon_itchion)

	# 开启 WeMediaMon
	start_wemediamon | tee -a $LOG_FILE
	echo XU6J03M6 | tee -a $LOG_FILE
	unset_lock
fi
