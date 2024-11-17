#! /bin/sh

source $KSROOT/scripts/base.sh
bilimon_pid=$(ps w | grep python | awk '{print $1}')
LOGTIME=$(TZ=UTC-8 date -R "+%Y-%m-%d %H:%M:%S")
if [ -n "${bilimon_pid}" ]; then
	http_response "【$LOGTIME】bilimon进程运行正常!(Python: ${bilimon_pid})"
else
	http_response "【$LOGTIME】bilimon进程未运行!"
fi
