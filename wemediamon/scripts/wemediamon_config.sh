#!/bin/sh

source /koolshare/scripts/base.sh
eval $(dbus export wemediamon)
MON_LOG=/tmp/upload/wemediamon_log.txt
RUN_LOG=/tmp/upload/wemediamon_run_log.txt
LOCK_FILE=/var/lock/wemediamon.lock
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
	if [ "${wemediamon_enable}" == "1" -a -n "$(which ntpclient)" ]; then
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

# 安装/检查运行环境
fix_env() {
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

# 失败自动关闭(仅供运行日志使用)
close_with_echo() {
	dbus set wemediamon_enable=0
	echo_date $1
	stop
	echo_date "插件已关闭!!"
	unset_lock
	exit
}

load_params() {
	# 加载dbus变量
	wemediamon_enable=$(dbus get wemediamon_enable)
	wemediamon_period=$(dbus get wemediamon_period)
	wemediamon_email=$(dbus get wemediamon_email)
	wemediamon_smtp=$(dbus get wemediamon_smtp)
	wemediamon_cache=$(dbus get wemediamon_cache)
	wemediamon_bilimon=$(dbus get wemediamon_bilimon)
	wemediamon_bilick=$(dbus get wemediamon_bilick)
	wemediamon_btskon=$(dbus get wemediamon_btskon)
	wemediamon_hfmon=$(dbus get wemediamon_hfmon)
	wemediamon_hftks=$(dbus get wemediamon_hftks)
	wemediamon_papers=$(dbus get wemediamon_papers)
	wemediamon_gitmon=$(dbus get wemediamon_gitmon)
	wemediamon_gitags=$(dbus get wemediamon_gitags)
	wemediamon_cnblon=$(dbus get wemediamon_cnblon)
	wemediamon_cnblokie=$(dbus get wemediamon_cnblokie)
	wemediamon_itchion=$(dbus get wemediamon_itchion)
	wemediamon_itck=$(dbus get wemediamon_itck)
	wemediamon_fmon=$(dbus get wemediamon_fmon)
	wemediamon_fmtag=$(dbus get wemediamon_fmtag)
}

# 检查入参
check_params() {
	# 检查必填入参
	if [[ -z "${wemediamon_period}" ]]; then
		close_with_echo "请输入有效周期!"
	fi
	if [[ -z "${wemediamon_email}" ]]; then
		close_with_echo "请输入有效邮箱!"
	fi
	if [[ -z "${wemediamon_smtp}" ]]; then
		close_with_echo "请输入有效SMTP密钥!"
	fi
	if [ -z "${wemediamon_cache}" ]; then
		close_with_echo "请输入有效缓存路径!"
	fi
	if [ "${wemediamon_bilimon}" != '1' ] &&
		[ "${wemediamon_hfmon}" != '1' ] &&
		[ "${wemediamon_gitmon}" != '1' ] &&
		[ "${wemediamon_cnblon}" != '1' ] &&
		[ "${wemediamon_itchion}" != '1' ] &&
		[ "${wemediamon_fmon}" != '1' ]; then
		close_with_echo "请至少开启一个监控器!"
	fi
	# 检查选填入参
	if [ "${wemediamon_bilimon}" == "1" ]; then
		if [[ -z "${wemediamon_bilick}" ]]; then
			close_with_echo "请输入有效B站cookie!"
		fi
	else
		wemediamon_bilick=''
		wemediamon_btskon='0'
	fi
	if [ "${wemediamon_hfmon}" == "1" ]; then
		if [[ -z "${wemediamon_hftks}" ]]; then
			close_with_echo "请输入有效抱脸Token!"
		fi
	else
		wemediamon_hftks=''
		wemediamon_papers=''
	fi
	if [ "${wemediamon_gitmon}" == "1" ]; then
		if [[ -z "${wemediamon_gitags}" ]]; then
			close_with_echo "请输入有效GitHub目标列表!"
		fi
	else
		wemediamon_gitags=''
	fi
	if [ "${wemediamon_cnblon}" == "1" ]; then
		if [[ -z "${wemediamon_cnblokie}" ]]; then
			close_with_echo "请输入有效博客园cookie!"
		fi
	else
		wemediamon_cnblokie=''
	fi
	if [ "${wemediamon_itchion}" == "1" ]; then
		if [[ -z "${wemediamon_itck}" ]]; then
			close_with_echo "请输入有效itch.io cookie!"
		fi
	else
		wemediamon_itck=''
	fi
	if [ "${wemediamon_fmon}" == "1" ]; then
		if [[ -z "${wemediamon_fmtag}" ]]; then
			close_with_echo "请输入有效猫耳uid!"
		fi
	else
		wemediamon_fmtag=''
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
start_wemediamon() {
	check_params
	sync_ntp
	check_env

	# 开启周期监控
	nohup python -u /koolshare/wemediamon/wemediamon.py \
		--cmd "START_MONITOR" \
		--period "${wemediamon_period}" \
		--email "${wemediamon_email}" \
		--smtp "${wemediamon_smtp}" \
		--cache "${wemediamon_cache}" \
		--bilick "${wemediamon_bilick}" \
		--btskon "${wemediamon_btskon}" \
		--hftks "${wemediamon_hftks}" \
		--papers "${wemediamon_papers}" \
		--gitags "${wemediamon_gitags}" \
		--cnblokie "${wemediamon_cnblokie}" \
		--itck "${wemediamon_itck}" \
		--fmtag "${wemediamon_fmtag}" \
		>>/dev/null 2>&1 &
}

# 单次触发指令
trigger_once() {
	load_params
	check_env

	# 开启单次触发扫描
	python -u /koolshare/wemediamon/wemediamon.py \
		--cmd $1 \
		--period "${wemediamon_period}" \
		--email "${wemediamon_email}" \
		--smtp "${wemediamon_smtp}" \
		--cache "${wemediamon_cache}" \
		--bilick "${wemediamon_bilick}" \
		--btskon "${wemediamon_btskon}" \
		--hftks "${wemediamon_hftks}" \
		--papers "${wemediamon_papers}" \
		--gitags "${wemediamon_gitags}" \
		--cnblokie "${wemediamon_cnblokie}" \
		--itck "${wemediamon_itck}" \
		--fmtag "${wemediamon_fmtag}"
}

# 查看取关狗
watch_dog() {
	case $1 in
	SEE_BILI_BLACKS)
		if [[ -s "${wemediamon_cache}/bili_blacklist.txt" ]]; then
			awk '{print "https://space.bilibili.com/" $0}' "${wemediamon_cache}/bili_blacklist.txt"
		else
			echo_date "当前B站狗库为空!"
		fi
		;;

	SEE_HF_BLACKS)
		if [[ -s "${wemediamon_cache}/hf_blacklist.txt" ]]; then
			awk '{print "https://huggingface.co/api/users/"$0"/overview"}' "${wemediamon_cache}/hf_blacklist.txt"
		else
			echo_date "当前抱脸狗库为空!"
		fi
		;;

	SEE_GIT_BLACKS)
		if [[ -s "${wemediamon_cache}/github_blacklist.txt" ]]; then
			awk '{print "https://api.github.com/user/" $0}' "${wemediamon_cache}/github_blacklist.txt"
		else
			echo_date "当前GitHub狗库为空!"
		fi
		;;

	SEE_CNBLOGS_BLACKS)
		if [[ -s "${wemediamon_cache}/cnblogs_blacklist.txt" ]]; then
			awk '{print "https://home.cnblogs.com/u/" $0}' "${wemediamon_cache}/cnblogs_blacklist.txt"
		else
			echo_date "当前博客园狗库为空!"
		fi
		;;

	SEE_ITCH_BLACKS)
		if [[ -s "${wemediamon_cache}/itch_blacklist.txt" ]]; then
			awk '{print "https://itch.io/profile/" $0}' "${wemediamon_cache}/itch_blacklist.txt"
		else
			echo_date "当前itch.io狗库为空!"
		fi
		;;

	SEE_FM_BLACKS)
		if [[ -s "${wemediamon_cache}/missevan_blacklist.txt" ]]; then
			awk '{print "https://www.missevan.com/" $0}' "${wemediamon_cache}/missevan_blacklist.txt"
		else
			echo_date "当前猫耳FM狗库为空!"
		fi
		;;

	*)
		echo_date "未知指令: $1"
		;;

	esac
}

# 关闭监控进程
stop() {
	load_params
	pids=$(ps | grep "python" | grep "wemediamon.py" | awk '{print $1}')
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
	if [ "${wemediamon_enable}" == "1" ]; then
		start_wemediamon
		echo_date "WeMediaMon 插件启动完毕, 本窗口将在 5s 内自动关闭!"
	else
		echo_date "WeMediaMon 已经停止运行, 本窗口将再 5s 后关闭!"
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
	echo_date "正在检查更新..."
	local local_md5=$(dbus get wemediamon_md5)
	local gitoken="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"
	local git_api="https://api.github.com/repos/Genius-Society/WeMediaMon/releases/tags/1.1"
	local latest_md5=$(curl -s -H "Authorization: token ${gitoken}" "${git_api}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('body', ''))")
	if [ "${local_md5}" == "${latest_md5}" ]; then
		echo_date "WeMediaMon 已是最新版本, 无需更新!"
	else
		echo_date "发现新版本, 更新中..."
		local status=$(curl -x http://127.0.0.1:23456 -s -o /dev/null -w "%{http_code}" https://github.com)
		local asset_url=$(curl -s -H "Authorization: token ${gitoken}" "${git_api}" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(a['url']) for a in data['assets'] if a['name']=='wemediamon.tar.gz']")
		if [ "${status}" == "200" ]; then
			wget --no-hsts -c -t 0 -T 30 -e use_proxy=yes -e https_proxy=http://127.0.0.1:23456 --header="Authorization: token ${gitoken}" --header="Accept: application/octet-stream" -O /tmp/upload/wemediamon.tar.gz "${asset_url}" 2>&1
		else
			wget --no-hsts -c -t 0 -T 30 --header="Authorization: token ${gitoken}" --header="Accept: application/octet-stream" -O /tmp/upload/wemediamon.tar.gz "${asset_url}" 2>&1
		fi
		dbus set soft_name=wemediamon.tar.gz
		unset_lock
		sh /koolshare/scripts/ks_tar_install.sh >/dev/null 2>&1
		echo_date "WeMediaMon 插件已更新!"
	fi
}

# 自启/重启时触发开启 WeMediaMon
if [[ $# -eq 0 || $# -eq 1 ]]; then
	set_lock
	stop
	if [[ "${wemediamon_enable}" == "1" ]]; then
		check_proxy
		start_wemediamon
	fi
	unset_lock
# 网页传参命令触发
elif [ $# -eq 2 ]; then
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

	SEE_*_BLACKS)
		watch_dog "$2" | tee -a $RUN_LOG
		;;

	*)
		trigger_once "$2" | tee -a $RUN_LOG
		;;

	esac

	unset_lock
	echo XU6J03M6 | tee -a $RUN_LOG
fi
