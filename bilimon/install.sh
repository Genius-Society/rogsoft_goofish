#!/bin/sh
source /koolshare/scripts/base.sh
alias echo_date='echo 【$(TZ=UTC-8 date -R +%Y年%m月%d日\ %X)】:'
DIR=$(
	cd $(dirname $0)
	pwd
)
module=bilimon
ROG_86U=0
BUILDNO=$(nvram get buildno)
EXT_NU=$(nvram get extendno)
EXT_NU=$(echo ${EXT_NU%_*} | grep -Eo "^[0-9]{1,10}$")
[ -z "${EXT_NU}" ] && EXT_NU="0"
odmpid=$(nvram get odmpid)
productid=$(nvram get productid)
[ -n "${odmpid}" ] && MODEL="${odmpid}" || MODEL="${productid}"
LINUX_VER=$(uname -r | awk -F"." '{print $1$2}')

# 获取固件类型
_get_type() {
	local FWTYPE=$(nvram get extendno | grep koolshare)
	if [ -d "/koolshare" ]; then
		if [ -n "${FWTYPE}" ]; then
			echo "koolshare 官改固件"
		else
			echo "koolshare 梅林改版固件"
		fi
	else
		if [ "$(uname -o | grep Merlin)" ]; then
			echo "梅林原版固件"
		else
			echo "华硕官方固件"
		fi
	fi
}

exit_install() {
	local state=$1
	case $state in
	1)
		echo_date "本插件适用于【koolshare 梅林改/官改 hnd/axhnd】固件平台!"
		echo_date "你的固件平台不能安装!!!"
		echo_date "本插件支持机型/平台: https://github.com/koolshare/rogsoft#rogsoft"
		echo_date "退出安装!"
		rm -rf /tmp/${module}* >/dev/null 2>&1
		exit 1
		;;
	0 | *)
		rm -rf /tmp/${module}* >/dev/null 2>&1
		exit 0
		;;
	esac
}

# 判断路由架构和平台: koolshare固件, 并且linux版本大于等于4.1
if [ -d "/koolshare" -a -f "/usr/bin/skipd" -a "${LINUX_VER}" -ge "41" ]; then
	echo_date 机型: ${MODEL} $(_get_type) 符合安装要求, 开始安装插件!
else
	exit_install 1
fi

# 判断固件UI类型
if [ -n "$(nvram get extendno | grep koolshare)" -a "$(nvram get productid)" == "RT-AC86U" -a "${EXT_NU}" -lt "81918" -a "${BUILDNO}" != "386" ]; then
	ROG_86U=1
fi

if [ "${MODEL}" == "GT-AC5300" -o "${MODEL}" == "GT-AX11000" -o "${MODEL}" == "GT-AX11000_BO4" -o "$ROG_86U" == "1" ]; then
	# 官改固件, 骚红皮肤
	ROG=1
fi

if [ "${MODEL}" == "TUF-AX3000" ]; then
	# 官改固件, 橙色皮肤
	TUF=1
fi

# 关闭进程
pids=$(ps | grep "python" | grep "bilimon.py" | awk '{print $1}')
if [ ! -z $pids ]; then
	echo_date "关闭当前进程..."
	for pid in $pids; do
		kill "$pid"
	done
fi

# 安装插件
mkdir -p /koolshare/bilimon/
cp -rf /tmp/bilimon/bin/* /koolshare/bilimon/
cp -rf /tmp/bilimon/scripts/* /koolshare/scripts/
cp -rf /tmp/bilimon/webs/* /koolshare/webs/
cp -rf /tmp/bilimon/res/* /koolshare/res/
cp -rf /tmp/bilimon/uninstall.sh /koolshare/scripts/uninstall_bilimon.sh

if [ "$ROG" == "1" ]; then
	echo_date "安装 ROG 皮肤!"
	continue
else
	if [ "$TUF" == "1" ]; then
		echo_date "安装 TUF 皮肤!"
		sed -i 's/3e030d/3e2902/g;s/91071f/92650F/g;s/680516/D0982C/g;s/cf0a2c/c58813/g;s/700618/74500b/g;s/530412/92650F/g' /koolshare/webs/Module_${module}.asp >/dev/null 2>&1
	else
		echo_date "安装 ASUSWRT 皮肤!"
		sed -i '/rogcss/d' /koolshare/webs/Module_${module}.asp >/dev/null 2>&1
	fi
fi

chmod +x /koolshare/scripts/bilimon*
chmod +x /koolshare/scripts/uninstall_bilimon.sh

# 离线安装用
dbus set bilimon_version="$(cat $DIR/version)"
dbus set softcenter_module_bilimon_version="$(cat $DIR/version)"
dbus set softcenter_module_bilimon_description="B站最近1K粉丝监控工具"
dbus set softcenter_module_bilimon_install="1"
dbus set softcenter_module_bilimon_name="bilimon"
dbus set softcenter_module_bilimon_title="BiliMon"

# 判断 Entware 是否已安装
if [ -d "/opt" ]; then
	echo_date 已检测到 Entware 环境, 开始安装依赖包!
	export PATH=$PATH:/opt/bin/
	sed -i "s|^src/gz.*|src/gz entware https://mirrors.bfsu.edu.cn/entware/aarch64-k3.10|" /opt/etc/opkg.conf
	opkg update
	opkg install python3-pip
	python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
	pip install -r /koolshare/bilimon/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
	echo_date "BiliMon 插件安装完毕!"
	sh /koolshare/scripts/bilimon_config.sh
else
	echo_date "BiliMon 插件安装完毕, 但未检测到 Entware 环境, 请补充安装部署 Entware 插件!"
fi

# 完成
exit_install
